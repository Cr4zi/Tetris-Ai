import sys
from tetris import Tetris
from window import Window
from ai import tetris_network 

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python main.py <opt>")
        exit(0)

    if sys.argv[1] == "play":
        window = Window(False)
        window.start()
    elif sys.argv[1] == "train":
        env = Tetris()
        net = tetris_network.TetrisNetwork(env, True)
        net.train()
        net.save_model()
