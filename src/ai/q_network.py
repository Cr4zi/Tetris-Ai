from tetris import Tetris
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
from collections import deque, namedtuple

Transition = namedtuple('Transition',
                        ('state', 'next_state', 'reward', 'done'))

class ReplayMemory(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

class QNetworkA(nn.Module):
    def __init__(self):
        super(QNetworkA, self).__init__()
        self.layer1 = nn.Sequential(nn.Linear(7, 64))
        self.layer2 = nn.Sequential(nn.Linear(64, 64))
        self.layer3 = nn.Sequential(nn.Linear(64, 32))
        self.layer4 = nn.Sequential(nn.Linear(32, 1))

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = F.relu(self.layer3(x))
        return self.layer4(x)


class QNetworkB(nn.Module):
    def __init__(self):
        super(QNetworkB, self).__init__()
        self.layer1 = nn.Sequential(nn.Linear(7, 256))
        self.layer2 = nn.Sequential(nn.Linear(256, 128))
        self.layer3 = nn.Sequential(nn.Linear(128, 64))
        self.layer4 = nn.Sequential(nn.Linear(64, 1))

    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = F.relu(self.layer3(x))
        return self.layer4(x)
