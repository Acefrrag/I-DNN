"""
Author: Vipin Kizhepatt

Revision Dec 26 21:36:56 2022: Michele Pio Fragasso


Description:
    --This python script trains a DNN and generates the DNN top level VHDL
    architecture which implements it. It also generates the necessary VHDL packages to make
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

import os
import datetime
import misc
import VHDL_DNN as VDNN



#Directories Path
date = datetime.datetime.now()
date_str = date.strftime("%x")+" "+date.strftime("%X")
date = (date.strftime("%x")+"_"+date.strftime("%X")).replace(" ","_").replace(":","-").replace("/","-")
training_ID = "training_"+date
#Directories path
dir_path = "../files/weights_n_biases/"+training_ID+"/"
VHDL_architectures_path = "../files/weights_n_biases/"+training_ID+"/VHDL_output/"
MI_DNN_tb_folderpath = "../../tb_files/DNN/multiple_images/tb_"+training_ID+"/"
DNN_tb_folderpath = "../../tb_files/DNN/single_image/tb_"+training_ID+"/"

vivadosrcDNNpath = "../../src/DNN/"
vivadosrcNORMpath = "../../src/NORM/"


DNN_input_training_filepath = "../files/input_file/training_file.txt"
#Creating input parameters
#DNN INPUT TRAINING PARAMETERS
DNN_in_prms = VDNN.extract_input(DNN_input_training_filepath)
DNN_in_prms["date"] = date
DNN_in_prms["architecturepath"] = VHDL_architectures_path
DNN_in_prms["num_images"] = 8
DNN_in_prms["MItbfoldername"] = "tb_"+training_ID
DNN_in_prms["tbfoldername"] = "tb_"+training_ID

#Making directories
try:
    os.mkdir(MI_DNN_tb_folderpath)
except:
    pass
try:
    os.mkdir(DNN_tb_folderpath)
except:
    pass
# MI_tbfoldername, MI_tbfolderpath = VDNN.mktbfolder(MI_DNN_tb_filespath)
# tb_fold
try:
    os.mkdir(dir_path)
except:
    pass
    print(23)

try:
    os.mkdir(VHDL_architectures_path)
except:
    pass


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
#Computing Neuron Sizes
neuron_input_Width = 32
neuron_weight_Width = 32
validation_data = DNN_in_prms["datasets"][0]
print("Training Done.")



#Creating training report
VDNN.savelogfile(net, e_a, path, DNN_in_prms)
print("Computinf data Format")
net.compute_DataFormat(validation_data)
print("End.")
#Creating sigmoid Content
print("Creating sSigmoid Content")
net.assignSigSize(sigmoid_inputSize=DNN_in_prms["sigmoid_inputSize"], sigmoid_inputIntSize=DNN_in_prms["sigmoid_inputIntSize"])
dest_path="../files/sigmoid/"
net.generateSigmoid(path=dest_path)
print("Done")
#Generating VHDL Weights and Bias files
print("Generating VHDL weights and biases")
misc.genWeightsAndBias(dir_path=dir_path, dataWidth=net.neuroninputSize, weightIntWidth=net.neuronweightIntSize, inputIntWidth=net.neuroninputIntSize)
print("Done")
try:
    os.mkdir(dir_path+"VHDL_output")
except:
    pass

#GENERATING Intermittent DNN VHDL ARCHITECTURE
print("Generating entities to be upload in the script folder---")
#Generating I_DNN_package.vhd
VDNN.mkpkg(DNN_in_prms, net,VHDL_architectures_path)
#Generatining I_DNN_MI_package.vhd
path = "../files/weights_n_biases/training_"+date+"/VHDL_output"
VDNN.mkMIpkg(VHDL_architectures_path, DNN_in_prms, net)

# path = "../..src/DNN/"
# VDNN.mkMIpackage(path, DNN_in_prms, net)
#Generating I_DNN.vhd

VDNN.mkentity(DNN_in_prms, net,VHDL_architectures_path)
VDNN.mkNVME_pkg(DNN_in_prms, VHDL_architectures_path)

outputpath = "../files/datasets/testData/automated/"
VDNN.mkdatasets(DNN_in_prms, net, outputpath)
print("Done.")

#Loading MI_DNN parameters into folder 
print("Generating enitities for uploading into the tb_files folder---")
outputpath = MI_DNN_tb_folderpath
VDNN.savenet(net, outputpath+wb_filename)
net.generateSigmoid(path=outputpath)
misc.genWeightsAndBias(dir_path=outputpath,dataWidth=net.neuroninputSize, weightIntWidth=net.neuronweightIntSize, inputIntWidth=net.neuroninputIntSize)
VDNN.mkdatasets(DNN_in_prms, net, outputpath)
VDNN.savelogfile(net, e_a, outputpath+report_filename, DNN_in_prms)
VDNN.mkNVME_pkg(DNN_in_prms, outputpath)

#Loading DNN parameters into folder
outputpath = DNN_tb_folderpath
VDNN.savenet(net, outputpath+wb_filename)
net.generateSigmoid(outputpath)
VDNN.mkdatasets(DNN_in_prms, net, outputpath)
VDNN.savelogfile(net, e_a, outputpath+report_filename, DNN_in_prms)
misc.genWeightsAndBias(dir_path=outputpath,dataWidth=net.neuroninputSize, weightIntWidth=net.neuronweightIntSize, inputIntWidth=net.neuroninputIntSize)


#Uploading Architecture Files
#Uploading MI_DNN package
outputpath = vivadosrcDNNpath
VDNN.mkMIpkg(outputpath, DNN_in_prms, net)
#Uploading DNN package and architecture
outputpath = vivadosrcDNNpath
VDNN.mkentity(DNN_in_prms, net, outputpath)
VDNN.mkpkg(DNN_in_prms, net, outputpath)
outputpath = vivadosrcNORMpath
VDNN.mkNVME_pkg(DNN_in_prms, outputpath)
print("Done.")