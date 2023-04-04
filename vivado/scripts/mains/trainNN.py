"""
Author: Vipin Kizhepatt

Revision April 04 21:36:56 2022: Michele Pio Fragasso

Description:
    All the paths are relative paths to this file folder.
    
    This python script trains a DNN and generates a VHDL NORM compatible
    I-DNN architecture. It also generates the necessary VHDL packages to make
    it work.
    The DNN parameters that can be chosen by the users are the number of
    layers, and the neurons per layer. Also the activation function type
    and the sigmoid size can be set up.
    The generated DNN is tested with two different testbenches:
        -I_DNN_single_image_tb.vhd, which tests one single MNIST sample;
        -I_DNN_multiple_images_tb.vhd, which tests more than one MNIST sample,
        this VHDL entity is used to perform simulations
Reminder:
    The number of the layers refers to the number of hidden layers of the 
    architecture. Therefore they do not include the input layer (the MNIST
    sample 784 pixels) and the output layer (the SOFTMAX layer).
Usage:
    INPUT:
    1) MNIST DATA SET, the loading is assigned to the mnist_loader
    2) "training_file.txt", located at the relative path ../files/input_file
    3) Number of MNIST samples to test with the testbench.
    OUTPUT:
    1) VHDL I-DNN architecture and packages:
        The architecture generated is:
            -I-DNN.vhd, it contains the VHDL NORM compatible I-DNN architecture.
        The packages generated at this step are:
            -NVME_FRAMEWORK_PACKAGE.vhd, which is the package to
                configure the NVR.
            -I_DNN_package.vhd, which contains the parameters to be run with
                the testbench I_DNN_tb.vhd
            -I_DNN_MI_package.vhd, which contains the parameters to be run with
                the testbench I_DNN_multiple_images_tb.vhd;
    2) Weights and Biases:
        Weights and Biases of layer L and neuron N are respectively put in the
        files w_L_N.txt and b_L_N.txt. These files are put in the folder:
        ../../tb_files/DNN/multiple_images, for I_DNN_multiple_images_tb.vhd
        ../../tb_files/DNN/single_image, for I_DNN
    3) Architecture Compatible MNIST sample
        Every DNN is characterized by a certain DATA FORMAT. The MNIST samples
        the testbench is tested with must be compatible data format
        -For the testbench I_DNN_tb.vhd, there is only one MNIST sample
        -For the testbench I_DNN_multiple_images_tb.vhd, the number of
        
FAQs:
1)  How do I set up  the training_file.txt?
    The training file of the input DNN parameters has this format
    <field>, <field_value>
    fields:
        num_hidden_layers:      number of hidden layers, it does not include the
                                input and output layer
        act_fun_type:           activation function type: ReLU or Sig
        epochs:                 number of training epochs
        eta:                    learning rate
        batch_size:             mini batch size, that is the batch size the training
                                is performed over.
        lmbda:                  regularitazion parameter
        sigmoid_inputSize:      Size in bit of the input to the sigmoid
        sigmoid_inputIntSize:   Size in bit of the integer part
2)  
"""

import sys
sys.path.insert(0, "../functions/")

import mnist_loader

import os
import datetime
import misc
import VHDL_DNN as VDNN #Library to train and generate the VHDL DNN files

#Directories Path
#Date Format
date = datetime.datetime.now()
date_str = date.strftime("%x")+" "+date.strftime("%X")
date = (date.strftime("%x")+"_"+date.strftime("%X")).replace(" ","_").replace(":","-").replace("/","-")
training_ID = "training_"+date
#DIRECTORIES PATHS
#BACKUP PATHS
#Backup Directory Path: This folder contains the backup to all file generated during training
backup_dir_path = "../files/weights_n_biases/"+training_ID+"/"
#Backup VHDL architectures
VHDL_architectures_path = "../files/weights_n_biases/"+training_ID+"/VHDL_output/"
#Backup Sigmoid Content
backup_sigmoid_path="../files/sigmoid/"

#OUTPUT DIRECTORY PATHS
#src paths
#This paths contains the directory path to the VHDL entities and packages
#ready to be simulated.
vivadosrcDNNpath = "../../src/DNN/"
vivadosrcNORMpath = "../../src/NORM/"
#Output Directory path
MI_DNN_tb_folderpath = "../../tb_files/DNN/multiple_images/tb_"+training_ID+"/"
DNN_tb_folderpath = "../../tb_files/DNN/single_image/tb_"+training_ID+"/"

#INPUT DIRECTORY PATH
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
try:
    os.mkdir(backup_dir_path)
except:
    pass


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
print("\nTraining Done. \n")

#BACKING UP DNN MODEL
print("Backing up DNN MODEL and files in script folder. \n")
wb_filename = "WeightsAndBiases.txt"
path = backup_dir_path+wb_filename
VDNN.savenet(net, path)
#Creating Training Report Log
report_filename = "training_report.txt"
path = backup_dir_path+report_filename
#Creating training report
VDNN.savelogfile(net, e_a, DNN_in_prms, path)
print("\nComputing data Format....")
validation_data = DNN_in_prms["datasets"][0]
net.compute_DataFormat(validation_data)
print("Computing Done!\n")
#Creating sigmoid Content
print("\nCreating Sigmoid Content...")
net.assignSigSize(sigmoid_inputSize=DNN_in_prms["sigmoid_inputSize"], sigmoid_inputIntSize=DNN_in_prms["sigmoid_inputIntSize"])
net.generateSigmoid(path=backup_sigmoid_path)
print("Sigmoid Content Created!\n")
#Generating VHDL Weights and Bias files
print("\nGenerating VHDL compatible weights and biases...")
misc.genWeightsAndBias(dir_path=backup_dir_path, dataWidth=net.neuroninputSize, weightIntWidth=net.neuronweightIntSize, inputIntWidth=net.neuroninputIntSize)
print("Done!\n")
#GENERATING Intermittent DNN VHDL ARCHITECTURE
print("\nGenerating VHDL entities and packages...")
#Generating I_DNN_package.vhd
VDNN.mkpkg(DNN_in_prms, net,VHDL_architectures_path)
#Generatining I_DNN_MI_package.vhd
VDNN.mkMIpkg(DNN_in_prms, net,VHDL_architectures_path)
VDNN.mkentity(DNN_in_prms, net,VHDL_architectures_path)
VDNN.mkNVME_pkg(DNN_in_prms, VHDL_architectures_path)
#Generating VHDL compatible MNIST SAMPLE
print("Done!\n")
print("\n Generating VHDL compatible MNIST samples")
outputpath = "../files/datasets/testData/automated/"
VDNN.mk_MI_datasets(DNN_in_prms, net, outputpath)
print("Done.")
print("Backup Complete.\n")

#################### GENERATING OUTPUT FILES ############################

print("Updating Vivado project by uploading newly generated DNN model and files inside...\n")
print("Uploading VHDL entities and packages into the vivado src folder...")
outputpath = vivadosrcDNNpath
VDNN.mkMIpkg(DNN_in_prms, net, outputpath)
#Uploading DNN package and architecture
VDNN.mkentity(DNN_in_prms, net, outputpath)
VDNN.mkpkg(DNN_in_prms, net, outputpath)
#Uploading NVME_FRAMEWORK_PACKAGE
outputpath = vivadosrcNORMpath
VDNN.mkNVME_pkg(DNN_in_prms, outputpath)
print("Done!\n")

#Loading multiple images DNN testbench parameters into folder 
print("Uploading multiple images files...\n")
outputpath = MI_DNN_tb_folderpath
print("Saving DNN model information...")
VDNN.savenet(net, outputpath+wb_filename)
print("DNN model information generated!\n")
print("Generating Sigmoid Content...")
net.generateSigmoid(path=outputpath)
print("Sigmoid Generated!\n")
print("Generating VHDL compatible weights and biases...")
misc.genWeightsAndBias(dir_path=outputpath,dataWidth=net.neuroninputSize, weightIntWidth=net.neuronweightIntSize, inputIntWidth=net.neuroninputIntSize)
print("VHDL compatible Weights and Biases Generated!\n")
print("Generating MNIST samples...")
VDNN.mk_MI_datasets(DNN_in_prms, net, outputpath)
print("MNIST samples generated!\n")
VDNN.savelogfile(net, e_a, DNN_in_prms, outputpath+report_filename)
print("Multiple images files uploaded!\n")


#Loading single image DNN testbench parameters into folder
print("Uploading single image files...\n")
outputpath = DNN_tb_folderpath
VDNN.savenet(net, outputpath+wb_filename)
print("Generating Sigmoid Content...")
net.generateSigmoid(outputpath)
print("Sigmoid Content Generated\n ")
print("Generating MNIST sample...")
VDNN.mk_SI_datasets(DNN_in_prms, net, outputpath)
print("MNIST samples generated!\n")
VDNN.savelogfile(net, e_a, DNN_in_prms,outputpath+report_filename)
print("Generating VHDL compatible weights and biases...")
misc.genWeightsAndBias(dir_path=outputpath,dataWidth=net.neuroninputSize, weightIntWidth=net.neuronweightIntSize, inputIntWidth=net.neuroninputIntSize)
print("VHDL compatible Weights and Biases Generated!\n")
print("Single image files uploaded!")

################## END OUTPUT FILES GENERATION ######################