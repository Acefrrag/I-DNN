"""
Created on Sat Apr 30 12:31:34 2022

@author: Michele Fragasso

Description: This script is used to validate the DNN testbench. It is meant to 
            be used concurrently with the testbench DNN_tb in the
            following way:
                -Set up test_data_sample in this script to choose the MNIST test
                    sample to be compared.
                -Generate the VHDL compatible MNIST test sample, by using the
                    python script generate_VHDL_test_data.py script
                -Change the testbench configuration filepath inside by changing:
                    the line of code inside DNN_tb.vhd
                        constant test_dataset_path: string := "../tb_files/DNN/tb4/dataset/test_data.txt";
                    and the line  code inside DNN_package.vhd:
                        constant DNN_prms_path: string := "../tb_files/DNN/tb4/";
                -Run this program and the testbench. Compare the data_out_vect
                    signal of the last layer with the variable out from this script.
                    Remember: If the last hidden layer are not logged in the waveform
                    make sure you do it, or you will not be able to compare them.
            #Inputs:
                wb_path: Weight and Bias Path relative path. It must be the file
                    containing the same set of weights and bias of the VHDL DNN
                    architecture. Check the date in the training folder name,
                    they should coincide.
                test_data_sample: the sample index within the MNIST database
                act_fun: "ReLU" or "Sig". It must coincide with the activation
                logic implemented in VHDL generated DNN
            #Output:
                test_data[test_data_sample][1]: target value of MNIST sample
                out: output of the last hidden layer (size 10) of the DNN
                digit_out: Classified digit. Computed as argmax(out)
                
                
                
"""

import sys
sys.path.insert(0,"../functions/")

import mnist_loader
import network2
import numpy as np


#Loading the data and dividind the dataset between training and validation data.
training_data, validation_data, test_data = mnist_loader.load_data_wrapper()
#Loading weights and biases
net = network2.load("../files/weights_n_biases/training_02-14-23_11-20-18/WeightsAndBiases.txt")
validation_data = list(validation_data)
training_data = list(training_data)
test_data = list(test_data)
test_data_sample=6452
i = test_data_sample
out_0 = net.feedforward(test_data[i][0])#The target for this input is 8.
print("The resulting number for the input with target "+ str(test_data[i][1]) +" is " + str(np.argmax(out_0)) + "\n")
w_sum_first_layer = np.dot(net.weights[0],test_data[i][0])+net.biases[0]
out_first_layer = network2.relu(np.dot(net.weights[0],test_data[i][0])+net.biases[0])
#print("The output of the first layer is \n" + str(out_first_layer) + "\n")
out_second_layer = network2.relu(np.dot(net.weights[1],out_first_layer)+net.biases[1])
out_third_layer = network2.relu(np.dot(net.weights[2],out_second_layer)+net.biases[2])
#print("The output of the second layer is \n" + str(out_second_layer) + "\n")
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
    