import numpy as np


def XNOR_GATE():
    X = np.array([[0,0],
              [0,1],
              [1,0],
              [1,1]])

    y = np.array([[1],
              [0],
              [0],
              [1]])

    def sigmoid(x):
        return 1/(1+np.exp(-x))

    def sigmoid_derivative(x):
        return x*(1-x)


    np.random.seed(1)

    w1 = np.random.randn(2,2)
    b1 = np.zeros((1,2))

    w2 = np.random.randn(2,1)
    b2 = np.zeros((1,1))

    lr = 0.5
    for epoch in range(50000):

        z1 = np.dot(X, w1) + b1
        a1 = sigmoid(z1)

        z2 = np.dot(a1, w2) + b2
        a2 = sigmoid(z2)

        error = a2 - y

        da2 = error * sigmoid_derivative(a2)

        dw2 = np.dot(a1.T, da2)
        db2 = np.sum(da2, axis=0, keepdims=True)

        da1 = np.dot(da2, w2.T) * sigmoid_derivative(a1)

        dw1 = np.dot(X.T, da1)
        db1 = np.sum(da1, axis=0, keepdims=True)

        w2 -= lr * dw2
        b2 -= lr * db2

        w1 -= lr * dw1
        b1 -= lr * db1
    return [w1,w2], [b1,b2]