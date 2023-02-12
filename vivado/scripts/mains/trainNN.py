"""
Author: Vipin Kizhepatt

Revision Dec 26 21:36:56 2022: Michele Pio Fragasso


Description:
    --This python script trains a DNN and generates the DNN top level VHDL
    architecture which implements it as well the necessary VHDL packages to make
    it work.
    --This train a neural network with an arbitrary number of layers, with as
    many neurons per layer as we want.
    --The number of layer of the DNN architecture does not include the input layer,
    infact the input is external to the DNN architecture, and is fed sequentially
    to the architecture. It does not even include the output layer which is a simple SOFTMAX
    --The last hidden layer is always a 10 neuron layer, every neuron is the digit
    and the output is how the DNN is confident about that digit being the digit depicted
    in the input image.
"""

import sys
sys.path.insert(0, "../functions/")

import mnist_loader
import network2

import os
import datetime
import time
import misc
import numpy as np
import Sigmoid
import VHDL_DNN as VDNN



#Directories Path
date = datetime.datetime.now()
date_str = date.strftime("%x")+" "+date.strftime("%X")
date = (date.strftime("%x")+"_"+date.strftime("%X")).replace(" ","_").replace(":","-").replace("/","-")
dir_path = "../files/weights_n_biases/training_"+date+"/"
VHDL_architectures_path = "../files/weights_n_biases/training_"+date+"/VHDL_output"

#Making directories
try:
    os.mkdir(dir_path)
except:
    pass

try:
    os.mkdir(VHDL_architectures_path)
except:
    pass

DNN_input_training_filepath = "../files/input_file/training_file.txt"
#Creating input parameters
#DNN INPUT TRAINING PARAMETERS
DNN_in_prms = VDNN.extract_input(DNN_input_training_filepath)
DNN_in_prms["date"] = date
DNN_in_prms["architecturepath"] = VHDL_architectures_path
DNN_in_prms["num_images"] = 8

#DNN TRAINING  
training_data, validation_data, test_data = mnist_loader.load_data_wrapper()
DNN_in_prms["datasets"] = list(training_data), list(validation_data), list(test_data)  
print("\nCurrently Training... \n")
#Creating the layers of the DNN. The layers' neuron number are enumerated. starting from
#the input layer until the output layer.
net, e_a = VDNN.train(DNN_in_prms)

#Saving DNN parameters
wb_filename = "WeightsAndBiases.txt"
path = dir_path+wb_filename
VDNN.savenet(net, path)
#Creating Training Report Log
report_filename = "training_report.txt"
path = dir_path+report_filename
VDNN.savelogfile(net, e_a, path, DNN_in_prms)
#Computing Neuron Sizes
neuron_input_Width = 32
neuron_weight_Width = 32
validation_data = DNN_in_prms["datasets"][0]
net.compute_DataFormat(validation_data)

#Creating sigmoid Content
net.assignSigSize(sigmoid_inputSize=DNN_in_prms["sigmoid_inputSize"], sigmoid_inputIntSize=DNN_in_prms["sigmoid_inputIntSize"])
dest_path="../files/sigmoid/"
net.generateSigmoid(path=dest_path)
#Generating VHDL Weights and Bias files
misc.genWeightsAndBias(dir_path=dir_path, dataWidth=net.neuroninputSize, weightIntWidth=net.neuronweightIntSize, inputIntWidth=net.neuroninputIntSize)

try:
    os.mkdir(dir_path+"VHDL_output")
except:
    pass

#GENERATING Intermittent DNN VHDL ARCHITECTURE
#Generating I_DNN_package.vhd
VDNN.makepackage(DNN_in_prms, net)
#Generatining I_DNN_MI_package.vhd
path = "../files/weights_n_biases/training_"+date+"/VHDL_output"
VDNN.mkMIpackage(path, DNN_in_prms, net)
# path = "../..src/DNN/"
# VDNN.mkMIpackage(path, DNN_in_prms, net)
#Generating I_DNN.vhd

VDNN.mkentity(DNN_in_prms, net)

outputpath = "../files/datasets/testData/automated/"
VDNN.mkdatasets(DNN_in_prms, net, outputpath)


    

