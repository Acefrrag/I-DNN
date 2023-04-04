"""
Created on Mon Dec 26 16:24:43 2022

Engineer: Michele Pio Fragasso


Description:
    --This python script computes a generic layer output with a given set of weights
    biases and an input to the layer
    
    Inputs:
        neuronweight_IntWidth: It contains the integer size of the input of the
            neuron weight
        neuroninput_IntWidth: It contains the integer part of the neuron
            input/output
        layer_filename: Name of the folder containinig parameter to test the layer.
                        To generate the layer parameters you can use the main
                        trainNN.py script and take any set of weights
    Outputs:
        layer output to be compared with the testbench
        VHDL layer_tb.vhd file to test the layer in Vivado
        
    Usage: After setting the size for the neuron inputs, weights and biases,
    the layer output for that specific format is available inside
    layer_out_dict
    
    The testbench to test the layer with is put inside the folder
    ../files/testbenching/layer_folder2
    
    After the weights and biases, and sigmoid with the chosen data Format are
    generated, they have to be put in the testbench folder
    ../../tb_files/layer/tb<number>.
    Remember to create the folders:
        
    -biases, containing the VHDL baises
    -weights, containing the VHDL weights
    -inputs, VHDL input to the layer
    -sigmoid, sigmoid content
    
    And to modify the layer 
    
    """

import sys
sys.path.insert(0, "../functions/")

import DNN_testbench

###Data Width of Weights, Inputs and Biases
neuronweight_Width = 32
neuroninput_Width = 32
neuronbias_Width = neuronweight_Width + neuroninput_Width
###Integer Part Width of Weight, Input and Bias
neuronweight_IntWidth = 2
neuroninput_IntWidth = 16
neuronbias_IntWidth = neuronweight_IntWidth+neuroninput_IntWidth

layer_filename = "layer_folder2"
layer_out_dict = DNN_testbench.testbench_layer(layer_filename, neuronweight_IntWidth, neuronbias_IntWidth, neuroninput_IntWidth, act_fun="Sig")
