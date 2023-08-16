import numpy as np
import pandas as pd

import urllib.request

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00267/data_banknote_authentication.txt"

filename = "Banknote.csv"

urllib.request.urlretrieve(url, filename)

data = np.genfromtxt(filename, delimiter=",")

np.random.seed(0)
np.random.shuffle(data)

# whenever the last column is < 0.5 (ie 0), change it to 0
data[data[:,-1] < 0.5,-1] = -1

train = data[:1000]
test = data[1000:]
np.savetxt("Banknote-Train.csv", train, delimiter=" ", header="x0 x1 x2 x3 y", fmt="%.6f")
np.savetxt("Banknote-Test.csv", test, delimiter=" ", header="x0 x1 x2 x3 y", fmt="%.6f")
