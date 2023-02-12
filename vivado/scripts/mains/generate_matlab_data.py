# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 11:01:55 2022

Engineer: Michele Pio Fragasso


Description:
    --Supposedly this program create two files training_data.txt and test_data_matlab.txt
    compatible with matlab scripts.
    
"""

try:
    import cPickle as pickle
except:
    import pickle
    
import gzip

import numpy as np

destination_path = "../to_matlab/"
MNIST_path = "../MNIST_package/mnist.pkl.gz"

f = gzip.open(MNIST_path, 'rb')         #change this location to the resiprositry where MNIST dataset sits
try:
    training_data, validation_data, test_data = pickle.load(f,encoding='latin1')
except:
    training_data, validation_data, test_data = pickle.load(f)
f.close()
#Training data is a tuple composed of two elements
#The first element is an array of matrixes containg the greyscale handwritten numbers,
#the second element is the digit (0 to 9) to which the image corresponds to.
trainingdata_filename = "training_data.txt"
training_data_images = training_data[0]
training_data_digits = np.reshape(training_data[1],(training_data[1].shape[0],1))
training_dataset = np.concatenate((training_data_images, training_data_digits), axis=1)
np.savetxt(destination_path+trainingdata_filename, X = training_dataset, newline = "\n",fmt="%.10f")
#TestData
testdata_filename = "test_data.txt"
test_data_images = test_data[0]
test_data_digits = np.reshape(test_data[1],(test_data[1].shape[0],1))
test_dataset = np.concatenate((test_data_images, test_data_digits), axis=1)
np.savetxt(destination_path+testdata_filename, X = test_dataset, newline = "\n",fmt="%.10f")

#This replaces this file
# f = open(trainingdata_filename,'w');
# for i in range(50000):
#     for j in range(784):
#         f.write(str(training_data[0][i][j])+" ")
# for i in range(50000):
#         f.write(str(training_data[1][i])+" ")
# f.close()

# f = open("test_data_matlab.txt",'w');
# for i in range(1000):
#     for j in range(784):
#         f.write(str(test_data[0][i][j])+" ")
# for i in range(1000):
#         f.write(str(test_data[1][i])+" ")
# f.close()
    


