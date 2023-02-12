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

def genSigContent(outputdataWidth, outputdataIntWidth, inputSize,inputIntWidth):
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
    f = open("sigContent.mif","w")
    inputFracWidth = inputSize-(inputIntWidth) 
    outputdataFracWidth = outputdataWidth-outputdataIntWidth
    if inputFracWidth < 0: #Sigmoid size is smaller the integer part of the MAC operation
        inputFracWidth = 0
    x = -2**(inputIntWidth-1)#Smallest input going to the Sigmoid LUT from the neuron
    for i in range(0,2**inputSize):
        y = sigmoid(x)
        z =float_to_fp_10(y,outputdataWidth,outputdataFracWidth)
        z_pad = z.__format__('0'+str(outputdataWidth)+'b')
        f.write(z_pad+'\n')
        x=x+(2**-inputFracWidth)
    f.close()
    g = open("dataFormat.log","w")
    g.write("DATA FORMAT \n\n")
    g.write("INPUT DATA FORMAT \n\n")
    g.write("Sigmoid input size: "+ str(inputSize) +"\n")
    g.write("Sigmoid input fractional part size: " + str(inputIntWidth)+"\n")
    g.write("Sigmoid input integer part size: "+str(inputSize-inputIntWidth)+"\n\n")
    g.write("OUTPUT DATA FORMAT \n\n")
    g.write("Sigmoid output size: "+str(outputdataWidth)+"\n")
    g.write("Sigmoid output fractional part size: " +str(outputdataWidth-outputdataIntWidth)+"\n")
    g.write("Sigmoid output integer part size: "+str(outputdataIntWidth)+"\n")
    g.close()


def float_to_fp_10(num,dataWidth,fracBits):
    """
    Funtion for converting a fractional number into base 10 fixed-point representation

    Parameters
    ----------
    num : float
        Fractional number to convert
    dataWidth : integer
        Number of bits to represent the number
    fracBits : integer
        Number of bits for representing the fractional part

    Returns
    -------
    fp_int : integer
        Base 10 fixed-point representation of num

    """
    if num >= 0:
        num = num * (2**fracBits)
        num = int(num)
        fp_int = num
    else:
        num = -num
        num = num * (2**fracBits)#number of fractional bits
        num = int(num)
        if num == 0:
            fp_int = 0
        else:
            fp_int = 2**dataWidth - num
    return fp_int
    
    
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
        
        
if __name__ == "__main__":
    genSigContent(outputdataWidth=32,outputdataIntWidth=16,inputSize=5,inputIntWidth=2)