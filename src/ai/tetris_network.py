from .q_network import QNetworkA, ReplayMemory, Transition
from tetris import Tetris
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
import math
import matplotlib.pyplot as plt

class TetrisNetwork:
    def __init__(self, env: Tetris, load=False, epsilon_start=1.0, epsilon_min=0.001, epsilon_decay=100_000, learning_rate=1e-4):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else
            "mps" if torch.backends.mps.is_available() else
            "cpu"
        )
        print(self.device)
        
        self.env = env
        self.BATCH_SIZE = 512
        self.exp_buffer = ReplayMemory(20_000)
        
        self.steps_done = 0
        self.epsilon_start = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.GAMMA = 0.99

        self.network = QNetworkA().to(self.device)
        if load:
            self.network.load_state_dict(torch.load("max_reward_network", weights_only=True))
            self.network.eval()
            print("Loaded")

        self.optimizer = optim.AdamW(self.network.parameters(), lr=self.learning_rate)

        self.loss_history = []
        self.reward_history = []
        self.steps_per_episode = []

    def select_action(self, candidates):
        self.epsilon = self.epsilon_min + (self.epsilon_start - self.epsilon_min) * math.exp(-1 * self.steps_done / self.epsilon_decay)
        
        self.steps_done += 1

        if random.uniform(0, 1) < self.epsilon:
            return random.randrange(len(candidates))

        with torch.no_grad():
            feature_tensor = torch.tensor(
                [candidate["features"] for candidate in candidates],
                dtype=torch.float32,
                device=self.device
            )
            values = self.network(feature_tensor)
            best = values.argmax().item()

        return best

    def optimize_model(self):
        if len(self.exp_buffer) < self.BATCH_SIZE:
            return

        transitions = self.exp_buffer.sample(self.BATCH_SIZE)
        batch = Transition(*zip(*transitions))

        non_final_mask = torch.tensor(tuple(not d for d in batch.done), dtype=torch.bool, device=self.device)
        non_final_next_states = torch.cat(
            [s for s, d in zip(batch.next_state, batch.done) if not d]
        )

        state_batch = torch.cat(batch.state)
        reward_batch = torch.cat(batch.reward).unsqueeze(1)
        done_batch = torch.cat(batch.done).unsqueeze(1)

        '''
        Since the model only calculate the grade of the state, it doesn't need the action.
        We predict argmax(Q(s_t)) instead of argmax(Q(s_t,a_i)).
        '''
        state_values = self.network(state_batch)

        next_state_values = torch.zeros(self.BATCH_SIZE, 1, device=self.device)
        with torch.no_grad():
            next_state_values[non_final_mask] = self.network(non_final_next_states)
            next_state_values[done_batch] = 0

        expected_values = reward_batch + self.GAMMA * next_state_values
        loss = F.mse_loss(state_values, expected_values)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.loss_history.append(loss.item())
        
    def pick_move(self):
        candidates = self.env.prepare_candidates()

        best_action = self.select_action(candidates)
        action = candidates[best_action]
        return action
        
    def train(self):
        self.network.train()
        max_reward = 0
        if torch.cuda.is_available():
            episodes = 10_000
        else:
            episodes = 10000

        for episode in range(episodes):
            state = self.env.reset()
            state = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)

            rewards = 0
            steps = 0
            
            while not self.env.done:
                steps += 1
                action = self.pick_move()
                
                observation, reward, done = self.env.do_move(action["x"], action["y"], action["rot"])
                rewards += reward

                reward_tensor = torch.tensor(
                    [reward],
                    device=self.device,
                    dtype=torch.float32
                )

                if done:
                    next_state = None
                else:
                    next_state = torch.tensor(observation, dtype=torch.float32, device=self.device).unsqueeze(0)

                done_tensor = torch.tensor([done], dtype=torch.bool, device=self.device)

                self.exp_buffer.push(state, next_state, reward_tensor, done_tensor)

                state = next_state

            if episode % 200 == 0:
                self.save_model()

            if rewards > max_reward:
                max_reward = rewards
                self.save_model("max_reward_network")

            self.optimize_model()
            self.optimize_model()

            print(f"At episode: {episode}, steps_done: {steps}, epsilon: {self.epsilon}, reward: {rewards}")
            self.reward_history.append(rewards)
            self.steps_per_episode.append(steps)

        print(f"Max Rewards: {max_reward}")

    
    def save_model(self, name="network"):
        torch.save(self.network.state_dict(), name)

    def save_graphs(self):
        plt.figure()
        plt.plot(self.loss_history)
        plt.title("Training Loss")
        plt.xlabel("Optimization Step")
        plt.ylabel("Loss")
        plt.savefig("loss.png")
        plt.close()

        # Rewards
        plt.figure()
        plt.plot(self.reward_history)
        plt.title("Episode Reward")
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.savefig("rewards.png")
        plt.close()

        # Steps per episode
        plt.figure()
        plt.plot(self.steps_per_episode)
        plt.title("Steps per Episode")
        plt.xlabel("Episode")
        plt.ylabel("Steps")
        plt.savefig("steps.png")
        plt.close()
