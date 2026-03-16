import numpy as np

def AND_GATE():
    x = np.array([[0,0],
              [0,1],
              [1,0],
              [1,1]])

    y = np.array([0,0,0,1])

    w = np.zeros(2)
    b = 0
    lr = 0.1
    for epoch in range(20):
        for i in range(len(x)):
            z = np.dot(w,x[i]) + b
            if z >= 0:
                y_pred = 1
            else:
                y_pred = 0

            error = y[i] - y_pred
            w[0] = w[0] + lr * error * x[i][0]
            w[1] = w[1] + lr * error * x[i][1]

            b += lr * error
    return w,b


def predict(x1,x2,w,b):
    z = x1*w[0] + x2 * w[1] + b
    return 1 if z >= 0 else 0