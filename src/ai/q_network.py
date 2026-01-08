from .. import Tetris
import tensorflow as tf

class QNetwork:
    def __init__(self, env: Tetris, epsilon=1, epsilon_min=0.05, epsilon_decay=0.01):
        self.states = 7
        self.exp_buff = []
        self.env = env
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.model = self._create_model()

    def _create_model(self):
        model = tf.keras.model.Sequential([
            tf.keras.layers.Dense(64, input_dim=self.states, activation='relu'),
            tf.keras.layers.Dense(64, activation='tanh'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='linear')
        ])

        model.compile(
            optimizer='adam',
            loss='mse')

        model.summary()

        tf.keras.utils.plot_model(model, "model.png", show_shapes=True)

        return model

