import numpy as np

class simpleNN:
    def __init__(self, input, hidden, output):
        self.W1 = np.random.randn(input, hidden)
        self.W2 = np.random.randn(hidden, output)

    def forward(self, x):
        z1 = np.dot(x, self.W1)
        a1 = np.tanh(z1)
        z2 = np.dot(a1, self.W2)
        return z2

    def train_step(self, state, action, reward, lr=0.01):

        z1 = np.dot(state, self.W1)
        a1 = np.tanh(z1)
        z2 = np.dot(a1, self.W2)

        exp = np.exp(z2 - np.max(z2))
        probs = exp / np.sum(exp)

        if action >= len(probs):
            return

        dZ2 = probs.copy()
        dZ2[action] -= 1
        dZ2 *= reward

        dW2 = np.outer(a1, dZ2)

        dA1 = np.dot(self.W2, dZ2)
        dZ1 = dA1 * (1 - np.tanh(z1)**2)
        dW1 = np.outer(state, dZ1)

        self.W2 -= lr * dW2
        self.W1 -= lr * dW1