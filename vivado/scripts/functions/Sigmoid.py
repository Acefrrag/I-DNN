# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 10:15:25 2022

Engineer: Michele Pio Fragasso


Description:
    
    Contains a set of function to generate the binary Sigmoid values to load into the LUT.
    
    The output file SigmoidContent.mif contains the Sigmoid output value y for different values of
    x. The number of outputs will be 2^(inputSize). 
    
    Notes:
    --"Base" 10 fixed-point representation" is the fixed-point representation but converted from
    binary to base 10.
"""


import math
import misc

def genSigContent(dest_path,outputdataWidth, outputdataIntWidth, inputSize,inputIntWidth):
    """
    Generates a file containing the sigmoid function values.
    
    Parameters
    ----------
    outputdataWidth : integer
        Width of the sigmoid output. Must corresponds to the neuron output width.
    outputdataIntWidth: integer
        Width of the integer part of the sigmoid output.
    inputSize : integer
        Size of the abscissa value.
        The x value will be represented using sigmoidSize bits
        The number of samples will be 2**inputSize.
    inputIntWidth : integer
        Size of the integer part of the obscissa value.
        FracWidth = sigmoidSize-IntWidth.
        The resolution step of the abscissa will be 2**(-inputFracWidth).
    Returns
    -------
    None.
    """
    f = open(dest_path+"sigContent.mif","w")
    inputFracWidth = inputSize-(inputIntWidth) 
    outputdataFracWidth = outputdataWidth-outputdataIntWidth
    if inputFracWidth < 0: #Sigmoid size is smaller the integer part of the MAC operation
        inputFracWidth = 0
    x = -2**(inputIntWidth-1)#Smallest input going to the Sigmoid LUT from the neuron
    for i in range(0,2**inputSize):
        y = sigmoid(x)
        z =misc.float_to_fp_10(y,outputdataWidth,outputdataFracWidth)
        z_pad = z.__format__('0'+str(outputdataWidth)+'b')
        f.write(z_pad+'\n')
        x=x+(2**-inputFracWidth)
    f.close()
    g = open(dest_path+"dataFormat.log","w")
    g.write("DATA FORMAT \n\n")
    g.write("INPUT DATA FORMAT \n\n")
    g.write("Sigmoid input size: "+ str(inputSize) +"\n")
    g.write("Sigmoid input integer part size: " + str(inputIntWidth)+"\n")
    g.write("Sigmoid input fractional part size: "+str(inputSize-inputIntWidth)+"\n\n")
    g.write("OUTPUT DATA FORMAT \n\n")
    g.write("Sigmoid output size: "+str(outputdataWidth)+"\n")
    g.write("Sigmoid output fractional part size: " +str(outputdataWidth-outputdataIntWidth)+"\n")
    g.write("Sigmoid output integer part size: "+str(outputdataIntWidth)+"\n")
    g.write("Smallest sigmoid input: " + str(-2**(inputIntWidth-1))+"\n")
    g.close()

   
    
def sigmoid(x):
    """
    Function implementing the analytical function of the sigmoid
    Parameters
    ----------
    x : float
        Sigmoid Argument
    Returns
    -------
    sigmoid_value: float
        Sigmoid value corresponding to the x value.
    """
    try:
        sigmoid_value = 1 / (1+math.exp(-x))
        return sigmoid_value
    except:
        sigmoid_value = 0
        return sigmoid_value
        
        
