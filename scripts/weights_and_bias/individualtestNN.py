# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 12:31:34 2022

@author: MicheleFragasso
"""

import mnist_loader
import network2
import json
import numpy as np


#Loading the data and dividind the dataset between training and validation data.
training_data, validation_data, test_data = mnist_loader.load_data_wrapper()
#Loading weights and biases
net = network2.load("WeightsAndBiases.txt")
validation_data = list(validation_data)
training_data = list(training_data)
test_data = list(test_data)
i=179
out_0 = net.feedforward(test_data[i][0])#The target for this input is 8.
print("The resulting number for the input with target "+ str(test_data[i][1]) +" is " + str(np.argmax(out_0)) + "\n")
out_first_layer = network2.relu(np.dot(net.weights[0],test_data[i][0])+net.biases[0])
print("The output of the first layer is \n" + str(out_first_layer) + "\n")
out_second_layer = network2.relu(np.dot(net.weights[1],out_first_layer)+net.biases[1])
print("The output of the second layer is \n" + str(out_second_layer) + "\n")
#TESTING SUM_REG_OUT @ every step NEURON 5 Layer 1
sum_reg_out = np.zeros((785))
k = 0
w_prod = (net.weights[0][5][k]*test_data[i][0][k])[0]
sum_reg_out[k] = w_prod
for k in range(1,783):
    w_prod = (net.weights[0][5][k]*test_data[i][0][k])[0]
    sum_reg_out[k] = w_prod+sum_reg_out[k-1]
    #print(neuron_5_out)
sum_reg_out[k] = sum_reg_out[k]+net.biases[0][4]
    