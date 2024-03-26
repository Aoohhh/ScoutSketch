# import os
# import numpy as np

real = []
data_array =[]
right = 0
PR = 0
RR = 0
F1 = 0

for i in data_array:
    if i in real:
        right += 1
pr = right / len(data_array)
rr = right / len(real)
f1 = 2*pr*rr/(pr+rr)

print("PR : ",pr, "RR : ",rr, "F1 : ",f1)