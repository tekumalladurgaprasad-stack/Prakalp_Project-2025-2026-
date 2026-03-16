import numpy as np

def OR_GATE():
    x = np.array([[0,0],
              [0,1],
              [1,0],
              [1,1]])

    y = np.array([0,1,1,1])

    w = np.zeros(2)
    lr = 0.1
    b = 0
    for epoch in range(20):
        for i in range(len(x)):
            z = np.dot(w,x[i]) + b
            y_pred = 1 if z >= 0 else 0
            error = y[i] - y_pred
            w += lr * error * x[i]
            b += lr * error
    return w,b
