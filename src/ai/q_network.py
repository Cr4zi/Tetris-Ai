from tetris import Tetris
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
from collections import deque, namedtuple

Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))

class ReplayMemory(object):
    def __init__(self, capacity):
        self.capactiy = capacity
        self.memory = deque([], maxlen=capacity)

    def clear(self):
        if len(self.memory) == self.capactiy:
            self.memory.clear()
        
    def push(self, *args):
        # This clears memory if needed
        self.clear()

        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

class QNetwork(nn.Module):
    def __init__(self):
        super(QNetwork, self).__init__()
        self.layer1 = nn.Linear(7, 64)
        self.layer2 = nn.Linear(64, 64)
        self.layer3 = nn.Linear(64, 32)
        self.layer4 = nn.Linear(32, 1)

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = F.tanh(self.layer3(x))
        return self.layer4(x)

