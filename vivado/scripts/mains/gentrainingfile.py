# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 11:53:41 2023

Engineer: Michele Pio Fragasso


Description:
    --File description
"""

import sys

def gensizes(num_hidden_layers):
    sizes = []
    input_size = 784
    step = int(input_size/num_hidden_layers)
    neurons = input_size-step
    for layer in range(num_hidden_layers):
        neurons = neurons-step
        sizes.append(neurons)
    
    strsizes = "("
    for size in sizes:
        strsizes += str(size)+";"
    strsizes = strsizes[:-1]
    strsizes += ")"
    
    return(strsizes)

training_filefullpath = "../files/input_file/training_file.txt"

f = open("training_file.txt","w")

num_hidden_layers = 100
act_fun_type = "ReLU"
epochs = 5
eta = 0.4
batch_size = 100
lmbda = 5
sigmoid_inputSize = 5
sigmoid_inputIntSize = 2
sizes = gensizes(num_hidden_layers)


sys.stdout = f
try:
    print(
"""num_hidden_layers,"""+str(num_hidden_layers)+"""
act_fun_type,"""+act_fun_type+"""
epochs,"""+str(epochs)+"""
eta,"""+str(eta)+"""
batch_size,"""+str(batch_size)+"""
lmbda,"""+str(lmbda)+"""
sigmoid_inputSize,"""+str(sigmoid_inputSize)+"""
sigmoid_inputIntSize,"""+str(sigmoid_inputIntSize)+"""
sizes,"""+sizes
    )          
    
finally:
    sys.stdout = sys.__stdout__
    f.close()
    
    
