import numpy as np
class simpleNN:
    def __init__(self, input, hidden, output):
        self.W1 = np.random.randn(input, hidden)
        self.W2 = np.random.randn(hidden, output)
    def forward(self, x):
        z1 = np.dot(self.W1, x)
        a1 = np.tanh(z1)

        z2 = np.dot(a1, self.W2)
        return z2
    def train(self, states, actions, reward, lr=0.01):
        for state, action in zip(states, actions):

            # forward pass
            z1 = np.dot(state, self.W1)
            a1 = np.tanh(z1)
            z2 = np.dot(a1, self.W2)

            # softmax (convert to probabilities)
            exp = np.exp(z2)
            probs = exp / np.sum(exp)

            # gradient for output
            dZ2 = probs
            dZ2[action] -= 1   # push chosen action
            dZ2 *= reward      # scale by win/loss

            # backprop
            dW2 = np.outer(a1, dZ2)

            dA1 = np.dot(self.W2, dZ2)
            dZ1 = dA1 * (1 - np.tanh(z1)**2)
            dW1 = np.outer(state, dZ1)

            # update weights
            self.W2 -= lr * dW2
            self.W1 -= lr * dW1