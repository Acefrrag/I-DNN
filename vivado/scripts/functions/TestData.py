# -*- coding: utf-8 -*-
"""
Author: Vipin Kizhepatt

Revision: Michele Pio Fragasso

Description:
    Collection of functions for generating fixed-point test dataset to be fed
    to the testbench module of the DNN architecture.
    
    This package is used by VHDL_DNN for VHDL NORM compatible DNN reconfiguration.
"""

import sys


headerFilePath = "../datasets/testData/automated/"
mnistPath = "../files/MNIST_package/"

try:
    import cPickle as pickle
except:
    import pickle
import gzip
import numpy as np
import os

dataWidth = 32 #specify the number of bits in test data
IntSize = 16 #Number of bits of integer portion including sign bit

try:
    testDataNum = int(sys.argv[1])
except:
    testDataNum = 3

def float_to_fp_int(num,dataWidth,fracBits):
    """
    Funtion for converting a floating-point number into integer fixed-point
    representation.

    Parameters
    ----------
    num : float
        Floating point number to converts into fixed point notation
    dataWidth : integer
        Size of the fixed-point representation
    fracBits : integer
        Size of the fractional part of the fixed-point representation
    Returns
    -------
    fp_num: integer
        Integer Fixed-point representation of num
    """                        
    if num >= 0:
        num = num * (2**fracBits)
        #ceil the num
        fp_num = int(num)
    else:
        num = -num
        num = num * (2**fracBits)
        num = int(num)
        if num == 0:
            fp_num = 0
        else:
            fp_num = 2**dataWidth - num
    return fp_num


def load_data():
    """
    This function load all the data from the MNIST package.

    Returns
    -------
    training_data : data structure
        It's a list containing 2 elements:
        The first element contains a list of the greyscales images.
        The second element is a list containing the digit to which the
        corresponding image belongs to.
        training_data[0] => [0:999][0:783] of float values.
        training_data[1] => [0:999] of integer values between 0 and 9.
    validation_data : data structure
        same as training_data
    test_data : data_structure
        same as training_data

    """

    mnist_filename="mnist.pkl.gz"
    f = gzip.open(mnistPath+mnist_filename, 'rb')
    try:
        training_data, validation_data, test_data = pickle.load(f,encoding='latin1')
    except:
        training_data, validation_data, test_data = pickle.load(f)
    f.close()
    return (training_data, validation_data, test_data)

def genTestData(dataWidth,IntSize,testDataNum,te_d,outputpath,net_test):
    """
    This function:
        1. Creates a file "test_data.txt"containing the fixed point representation of the pixels of a greyscale handwritten number from the test dataset;
        
        2. Creates a file "testData.txt" containing the floating point number of those pixels;
        
        3. Creates a visual data file visual_data<digit>.txt highliting the pixels of the image filled with greycolor(which makes up the number);
        
        4. Creates a C header file containing variables declaration.These are the two lines of code:
            -int dataValues[] = {<base 10 fixed-point representation pixels of greyscale image>};
            
            -int result=<corresponding digit to the greyscale handwritten number>
        5. Create a log genData.log containing information about the data format
        6. Creates a dataset_<num>_digitout.txt containing the class to which the image corresponds to
        7. Creates a file dataset_<num>_classdigit.txt contaning the digit classfied by using the corresponding neural network.
    Parameters
    ----------
    dataWidth : int
        size of the pixels
    IntSize : int
        size of the integer part of the pixels
    testDataNum : int
        test dataset image index
    Returns
    -------
    None.
    """

    
    #Test Data greyscale are reshaped into (1,784) matrix instead of (784,)
    test_inputs = [np.reshape(x, (1, 784)) for x in te_d[0]]
    x = len(test_inputs[0][0])
    FracSize=dataWidth-IntSize
    count = 0
    if testDataNum < 10:
        ext = "000"+str(testDataNum)
    elif testDataNum < 100:
        ext = "00"+str(testDataNum)
    elif testDataNum < 1000:
        ext = "0"+str(testDataNum)
    else:
        ext = str(testDataNum)
    try:
        foldername="test_dataset_"+ext
        folderpath=outputpath+foldername
        os.mkdir(folderpath)
    except:
        #No directory is created in case of error
        print("Folder already exist. None is created")
    logFile = open(folderpath+"/"+"genData.log","w")
    logFile.write("DataSet no. "+str(testDataNum)+"\n\n")
    logFile.write("Data Format:\n")
    logFile.write("Data Width: "+str(dataWidth)+"\n")
    logFile.write("Integer Part Width: "+str(IntSize)+"\n")
    logFile.write("Fractional Part Widht: "+str(dataWidth-IntSize)+"\n")
    logFile.close()
    #dataHeaderFile = open(folderpath+"/"+"dataValues.h","w")
    #dataHeaderFile.write("int dataValues[]={")
    fileName = "VHDL_dataset_"+ext+".txt"
    f = open(folderpath+"/"+fileName,'w')
    fileName = 'visual_data'+str(te_d[1][testDataNum])+'.txt'
    g = open(folderpath+"/"+fileName,'w')
    fileName = "testData.txt"
    k = open(folderpath+"/"+fileName,'w')
    for i in range(0,x):
        #Filling up testData.txt
        k.write(str(test_inputs[testDataNum][0][i])+',')
        
        #Filling up dataValues.h
        #Converting floating-point pixel into fixed-point integer representation
        fp_pixel_int = float_to_fp_int(test_inputs[testDataNum][0][i],dataWidth,FracSize)
        #dataHeaderFile.write(str(fp_pixel_int)+',')
        
        #Filling up test_data.txt
        #Zero Padding the MSb
        fp_pixel_bin_padded = fp_pixel_int.__format__('0'+str(dataWidth)+'b');
        f.write(fp_pixel_bin_padded+'\n')
        
        #Filling up visual_data<digit>.txt
        if test_inputs[testDataNum][0][i]>0:
            g.write(str(1)+' ')
        else:
            g.write(str(0)+' ')
        count += 1
        if count%28 == 0:
            g.write('\n')
    #Footer dataValues.h
    #dataHeaderFile.write('0};\n')
    #dataHeaderFile.write('int result='+str(te_d[1][testDataNum])+';\n')
    #Closing files
    k.close()
    g.close()
    f.close()
    #dataHeaderFile.close()
    
    filename = "dataset_"+ext+"_digitout.txt"
    a = open(folderpath+"/"+filename,"w")
    a.write(str(te_d[1][testDataNum]))
    a.close()
    
    filename = "dataset_"+ext+"_classdigit.txt"
    out_DNN = net_test.feedforward(te_d[0][testDataNum])#The target for this input is 8.
    out_DNN_digit = str(np.argmax(out_DNN))
    a = open(folderpath+"/"+filename,"w")
    a.write(str(out_DNN_digit))
    a.close()
    
def gensetofTestData(dataWidth,IntSize,number_set,te_d):
    """
    This function creates the fixed-point images from every element of the test data set within the MNIST package.

    Parameters
    ----------
    dataWidth : integer
        Size of the greyscale pixel in bits.
    IntSize : TYPE
        Size of the integer part.
    number_set : integer
        Number of images to randomly pick-up from the test dataset of MNIST
    
    Returns
    -------
    None.
    """
    test_inputs = [np.reshape(x, (1, 784)) for x in te_d[0]]
    size_te_d = (len(test_inputs))
    #x is the length of a single image (784)
    pixel_indexes = np.random.randint(0, size_te_d-1, number_set)
    for i in pixel_indexes:
        genTestData(dataWidth,IntSize,i,te_d)



if __name__ == "__main__":
    #genTestData(dataWidth,IntSize,testDataNum=1)
    tr_d, va_d, te_da = load_data()
    #•genTestData(dataWidth,IntSize,175)
    gensetofTestData(dataWidth, IntSize,10,te_da)
