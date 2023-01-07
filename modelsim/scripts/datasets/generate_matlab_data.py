# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 15:17:46 2022

@author: Win10Admin
"""

try:
    import cPickle as pickle
except:
    import pickle
import gzip
#import numpy as np


f = gzip.open('mnist.pkl.gz', 'rb')         #change this location to the resiprositry where MNIST dataset sits
try:
    training_data, validation_data, test_data = pickle.load(f,encoding='latin1')
except:
    training_data, validation_data, test_data = pickle.load(f)
f.close()

f = open("training_data.txt",'w');
for i in range(50000):
    for j in range(784):
        f.write(str(training_data[0][i][j])+" ")
for i in range(50000):
        f.write(str(training_data[1][i])+" ")
f.close()

f = open("test_data_matlab.txt",'w');
for i in range(1000):
    for j in range(784):
        f.write(str(test_data[0][i][j])+" ")
for i in range(1000):
        f.write(str(test_data[1][i])+" ")
f.close()
    


