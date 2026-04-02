import numpy as np

class simpleNN:
    def __init__(self, input, hidden, output):
        self.W1 = np.random.randn(input, hidden)
        self.W2 = np.random.randn(hidden, output)

        self.b1 = np.zeros(hidden)
        self.b2 = np.zeros(output)

    def forward(self, x):
        z1 = np.dot(x, self.W1) + self.b1
        a1 = np.tanh(z1)
        z2 = np.dot(a1, self.W2) + self.b2
        return z2

    def train_step(self, state, action, damage_list, lr=0.01):

        z1 = np.dot(state, self.W1) + self.b1
        a1 = np.tanh(z1)
        z2 = np.dot(a1, self.W2) + self.b2

        temperature = 0.5
        exp = np.exp((z2 - np.max(z2)) / temperature)
        probs = exp / np.sum(exp)

        if action >= len(damage_list):
            return

        best_action = np.argmax(damage_list)
        max_damage = max(damage_list)

        damage = damage_list[action]
        reward = damage / (max_damage + 1e-6)

        if action != best_action:
            reward -= 0.3

        dZ2 = probs.copy()
        dZ2[action] -= 1
        dZ2 *= reward

        dW2 = np.outer(a1, dZ2)
        dB2 = dZ2

        dA1 = np.dot(self.W2, dZ2)
        dZ1 = dA1 * (1 - np.tanh(z1)**2)

        dW1 = np.outer(state, dZ1)
        dB1 = dZ1

        self.W2 -= lr * dW2
        self.b2 -= lr * dB2

        self.W1 -= lr * dW1
        self.b1 -= lr * dB1

