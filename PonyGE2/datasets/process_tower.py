import numpy as np

import pandas as pd

"""

From Vladislavleva et al, Order of Nonlinearity:

"The Tower problem contains real-life data for which the true
input–output relationship is unknown. To assess extrapolative
capabilities of GP solutions for the Tower problem, we decided to
select significant input variables at a preprocessing step, and then
used only those to divide the data into training and test sets. The
driving variables identified at initial screening using the fitness
inheritance approach (see [9]) were x1, x4, x6, x12, and x23. The 5000
data records corresponding to these inputs were scaled into the 5-D
cube [0, 1]^5. All records belonging to the interval [0.02, 0.98]^5
were selected into the training set, and the remaining records formed
a test set for extrapolation."

It sounds like the response variable was not scaled, and the error
values given in the paper (around 30 for train, 40 for test) suggest
this also (the response variable is in the range [50, 535]).

"""


df = pd.read_table("towerData.txt", delimiter="\t")
print(df.head())
idxs = [1, 4, 6, 12, 23]
vars = ["x"+str(idx) for idx in idxs]

df = df[vars + ["towerResponse"]]
print(df.head())

print(df["towerResponse"].min())
print(df["towerResponse"].max())

def scale(x):
    return (x - x.min()) / (x.max() - x.min())

for var in vars:
    df[var] = scale(df[var])

print(df.head())

# this is ugly but I can't get Pandas to select using an iterator over vars
df_train = df[((df["x1"] > 0.02) & (df["x1"] < 0.98) &
               (df["x4"] > 0.02) & (df["x4"] < 0.98) &
               (df["x6"] > 0.02) & (df["x6"] < 0.98) &
               (df["x12"] > 0.02) & (df["x12"] < 0.98) &
               (df["x23"] > 0.02) & (df["x23"] < 0.98))]
df_test = df[~((df["x1"] > 0.02) & (df["x1"] < 0.98) &
                (df["x4"] > 0.02) & (df["x4"] < 0.98) &
                (df["x6"] > 0.02) & (df["x6"] < 0.98) &
                (df["x12"] > 0.02) & (df["x12"] < 0.98) &
                (df["x23"] > 0.02) & (df["x23"] < 0.98))]

print(df_train.head())
print(df_test.head())

colnames = ["#x1", "x4", "x6", "x12", "x23", "y"] # add a comment symbol to header
df_train.to_csv("Tower-Train.txt", sep="\t", index=False, header=colnames)
df_test.to_csv("Tower-Test.txt", sep="\t", index=False, header=colnames)

def normalise(x, minv, maxv):
    return (x - minv) / (maxv - minv)

col = "towerResponse"
minv = df_train[col].min()
maxv = df_train[col].max()

df_train[col] = normalise(df_train[col], minv, maxv)
df_test[col] = normalise(df_test[col], minv, maxv)

df_train.to_csv("TowerNorm-Train.txt", sep="\t", index=False, header=colnames)
df_test.to_csv("TowerNorm-Test.txt", sep="\t", index=False, header=colnames)
