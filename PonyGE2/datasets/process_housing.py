import numpy as np
import urllib.request
import subprocess
import os

"""Well-known Boston housing dataset. We just add a 1-line header and do a
deterministic shuffle and split.

"""

if not os.path.isfile("Housing/housing.data"):
    url = "http://www.dcc.fc.up.pt/~ltorgo/Regression/housing.tar.gz"
    filename = "housing.tar.gz"
    urllib.request.urlretrieve(url, filename)

    subprocess.call(["gunzip", filename])
    subprocess.call(["tar", "xf", filename[:11]])

d = np.genfromtxt("Housing/housing.data", delimiter=",")
np.random.seed(0)
np.random.shuffle(d)

idx = int(0.7 * len(d))
d_train = d[:idx]
d_test = d[idx:]

colnames = "#CRIM ZN INDUS CHAS NOX RM AGE DIS RAD TAX PTRATIO B LSTAT CLASS"
np.savetxt("Housing-Train.csv", d_train, delimiter=",", header=colnames)
np.savetxt("Housing-Test.csv", d_test, delimiter=",", header=colnames)

def normalise(x, minv, maxv):
    return (x - minv) / (maxv - minv)

for col in range(d_train.shape[1]):
    minv = d_train[:,col].min()
    maxv = d_train[:,col].max()
    d_train[:,col] = normalise(d_train[:,col], minv, maxv)
    d_test[:,col] = normalise(d_test[:,col], minv, maxv)

np.savetxt("HousingNorm-Train.csv", d_train, delimiter=",", header=colnames)
np.savetxt("HousingNorm-Test.csv", d_test, delimiter=",", header=colnames)
