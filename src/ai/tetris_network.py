from .q_network import QNetwork, ReplayMemory, Transition
from tetris import Tetris
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
import math


class TetrisNetwork:
    def __init__(self, env: Tetris, load=False, epsilon=1, epsilon_min=0.05, epsilon_decay=1000_000, learning_rate=3e-4):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else
            "mps" if torch.backends.mps.is_available() else
            "cpu"
        )
        
        self.env = env
        self.BATCH_SIZE = 256
        self.exp_buffer = ReplayMemory(2048)
        
        self.steps_done = 0
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.GAMMA = 0.99
        self.TAU = 0.005

        self.policy_net = QNetwork().to(self.device)
        self.target_net = QNetwork().to(self.device)
        if load:
            self.policy_net.load_state_dict(torch.load("policy_net", weights_only=False))
            self.policy_net.eval()
            
            self.target_net.load_state_dict(torch.load("target_net", weights_only=False))
            self.target_net.eval()

        self.optimizer = optim.AdamW(self.policy_net.parameters(), lr=self.learning_rate, amsgrad=True)

    def select_action(self, candidates):
        self.epsilon = max(self.epsilon_min, math.exp(- self.steps_done / self.epsilon_decay))
        
        self.steps_done += 1

        if random.uniform(0, 1) < self.epsilon:
            return random.randrange(len(candidates))

        with torch.no_grad():
            feature_tensor = torch.tensor(
                [candidate["features"] for candidate in candidates],
                dtype=torch.float32,
                device=self.device
            )
            values = self.policy_net(feature_tensor).squeeze(-1)
            best = values.argmax().item()

        return best

    def optimize_model(self):
        if len(self.exp_buffer) < self.BATCH_SIZE:
            return

        transitions = self.exp_buffer.sample(self.BATCH_SIZE)
        batch = Transition(*zip(*transitions))

        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                            batch.next_state)), device=self.device, dtype=torch.bool)
        non_final_next_states = torch.cat([s for s in batch.next_state
                                                    if s is not None])
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        #state_action_values = self.policy_net(state_batch).gather(1, action_batch)
        state_action_values = self.policy_net(state_batch).squeeze(1)

        next_state_values = torch.zeros(self.BATCH_SIZE, device=self.device)
        with torch.no_grad():
            #next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1).values
            next_state_values[non_final_mask] = self.target_net(non_final_next_states).squeeze(1)
        expected_state_action_values = (next_state_values * self.GAMMA) + reward_batch

        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

        self.optimizer.zero_grad()
        loss.backward()

        torch.nn.utils.clip_grad_value_(self.policy_net.parameters(), 100)
        self.optimizer.step()

    def train(self):
        if torch.cuda.is_available():
            episodes = 100_000
        else:
            episodes = 50

        for episode in range(episodes):
            state = self.env.reset()
            state = torch.tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)
            print(f"At episode: {episode}, steps_done: {self.steps_done}, epsilon: {self.epsilon}")
            while not self.env.done:
                moves_dict = self.env.graded_moves(False)
                candidates = []
                for rot in range(4):
                    for move in moves_dict[rot]:
                        candidates.append({"rot": rot, "x": move[0], "y": move[1], "features" : move[2]})
                
                best_action = self.select_action(candidates)
                action_idx = torch.tensor(
                    [[best_action]],
                    device=self.device,
                    dtype=torch.long
                )
                action = candidates[best_action]
                
                observation, reward, done = self.env.do_move(action["x"], action["y"], action["rot"])

                reward_tensor = torch.tensor(
                    [reward],
                    device=self.device,
                    dtype=torch.float32
                )

                if done:
                    next_state = None
                else:
                    next_state = torch.tensor(observation, dtype=torch.float32, device=self.device).unsqueeze(0)

                self.exp_buffer.push(state, action_idx, next_state, reward_tensor)

                state = next_state

                self.optimize_model()

                target_net_state_dict = self.target_net.state_dict()
                policy_net_state_dict = self.policy_net.state_dict()
                for key in policy_net_state_dict:
                    target_net_state_dict[key] = policy_net_state_dict[key]*self.TAU + target_net_state_dict[key]*(1-self.TAU)
                self.target_net.load_state_dict(target_net_state_dict)

    def save_model(self):
        torch.save(self.policy_net.state_dict(), "policy_net")
        torch.save(self.target_net.state_dict(), "target_net")
