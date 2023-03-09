# -*- coding: utf-8 -*-
"""
Created on Wed Dec 28 12:55:36 2022

Engineer: Michele Pio Fragasso


Description:
    --File description
"""

import numpy as np
import re
import os
import json


dt_string = np.dtype(str)



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
        num = round(num)
        fp_int = num
    else:
        num = -num
        num = num * (2**fracBits)#number of fractional bits
        num = round(num)
        if num == 0:
            fp_int = 0
        else:
            fp_int = 2**dataWidth - num
    return fp_int
    
    
def read_integer():
    """
    Procedure to read an integer 

    Returns
    -------
    val : integer
        number read from terminal
    """
    check = 0
    while check == 0:
        val = input()
        try:
            float(val)
            check = 1
        except ValueError:
            print("Input is not a number. Insert it again")
            check = 0
    return(val)
   

def sigmoid_extract_size(sigmoid_data_path):
    logfilename = "dataFormat.log"
    with open(sigmoid_data_path+"\\\\"+logfilename) as file:
        lines = file.readlines()
    c = 0
    for line in lines:
        if line.find("Sigmoid input size:")==0:
            sigmoid_input_size_str = re.findall(r'\d',lines[c])[0]
        if line.find("Sigmoid input integer part size:")==0:
            sigmoid_input_Intsize_str = re.findall(r'\d',lines[c])[0]
        c = c + 1
    sigmoid_inputSize = int(sigmoid_input_size_str)
    sigmoid_inputIntSize = int(sigmoid_input_Intsize_str)
    return(sigmoid_inputSize, sigmoid_inputIntSize)
    
def genWeightsAndBias(dir_path, dataWidth, weightIntWidth, inputIntWidth):
    """
        

    Parameters
    ----------
    dir_path : TYPE
        DESCRIPTION.
    dataWidth : TYPE
        DESCRIPTION.
    weightIntWidth : TYPE
        DESCRIPTION.
    inputIntWidth : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    #The bias is added to the cumulative sum. In principle, the cumulative sum
    #size is the sum of the sizes of the weight and input. But since we are sure
    #that the chosen precision will allow us to efficiently represent the neuron's
    #weighted sums, we can cut everything to the input size. This is to save
    #the data within the NV_REG cells (32 bit width).
    #therefore the bias will have the same size as the neuron's input.
    #In the volatile DNN, the bias as well the cumulative sum hadn't been reduced
    #in size since there was no need to save the data.
    
    weightWidth = dataWidth
    weightFracWidth = dataWidth-weightIntWidth
    biasWidth = dataWidth
    biasIntWidth = inputIntWidth
    biasFracWidth = biasWidth-biasIntWidth
    biases_path = dir_path+"/biases/"
    weights_path = dir_path+"/weights/"
    try:
        os.mkdir(biases_path)
        os.mkdir(weights_path)
    except:
        print("Folder already exists. No folder created.")
    myDataFile = open(dir_path+"WeightsAndBiases.txt","r")
    weightHeaderFile = open(dir_path+"weightValues.h","w")
    myData = myDataFile.read()
    myDict = json.loads(myData)
    myWeights = myDict['weights']
    myBiases = myDict['biases']
    #Generating weights
    weightHeaderFile.write("int weightValues[]={")
    for layer in range(0,len(myWeights)):
        for neuron in range(0,len(myWeights[layer])):
            weight_filename = 'w_'+str(layer+1)+'_'+str(neuron)+'.mif'
            f = open(weights_path+weight_filename,'w')
            for weight in range(0,len(myWeights[layer][neuron])):
                weight_fp_int = float_to_fp_10(myWeights[layer][neuron][weight],dataWidth,weightFracWidth)#conversion in corresponding integer.
                weight_fp_bin = weight_fp_int.__format__('0'+str(weightWidth)+'b')#Used for zero padding to reach DataWidth bits
                f.write(weight_fp_bin+'\n')
                weightHeaderFile.write(str(weight_fp_int)+',')
        f.close()
            
    weightHeaderFile.write("0};\n")
    weightHeaderFile.close()

    biasHeaderFile = open(dir_path+"biasValues.h","w")
    biasHeaderFile.write("int biasValues[]={")
    for layer in range(0,len(myBiases)):
        for neuron in range(0,len(myBiases[layer])):
             bias_filename = 'b_'+str(layer+1)+'_'+str(neuron)+'.mif'
             f = open(biases_path+bias_filename,'w')
             p = myBiases[layer][neuron][0]
             bias_fp_int = float_to_fp_10(p,biasWidth,biasFracWidth)
             bias_fp_bin = bias_fp_int.__format__('0'+str(biasWidth)+'b')
             f.write(bias_fp_bin+"\n")
             biasHeaderFile.write(str(bias_fp_int)+',')
             f.close()
             
    biasHeaderFile.write('0};\n')
    biasHeaderFile.close()

    dataFormatFile = open(dir_path+"dataFormatFile.txt","w")
    dataFormatFile.write("DATA FORMAT BIASES AND WEIGHTS\n\n")
    dataFormatFile.write("WEIGHTS FORMAT:\n\n")
    dataFormatFile.write("Data Size: "+str(dataWidth)+"\n")
    dataFormatFile.write("Integer Data Size: "+str(weightIntWidth)+"\n")
    dataFormatFile.write("Fractional Data Size: "+str(weightFracWidth)+"\n\n")
    dataFormatFile.write("BIASES FORMAT:\n\n")
    dataFormatFile.write("Data Size: "+str(biasWidth)+"\n")
    dataFormatFile.write("Integer Data Size: "+str(biasIntWidth)+"\n")
    dataFormatFile.write("Fractional Data Size: "+str(biasFracWidth)+"\n\n")
    dataFormatFile.close()
    
def genVoltageTraceFile(trace, vt_ts=160, SC_p = 40):

    output_voltage_trace_path = "../../src/NORM/voltage_traces/"
    IE_pkg_path = "../../src/NORM/"

    x_trace = trace["samples"]
    y_trace = trace["voltages"]
    
    prescaler_value = int(vt_ts/SC_p)
    w_len = len(y_trace)

    
    #CREATE VHDL compatible voltage trace
    output = open(output_voltage_trace_path+"voltage_trace"+trace["trace_ID"]+".txt", "w")
    for data_trace in y_trace:
    #Code for saving data
         output.write(str(int(data_trace)) + "\n")
    output.close()
    
    
    max_value =int(max(y_trace))
    
    #UPDATING IE_FRAMEWORK_pakcga.vhd     
    IE_pkg_file = open(IE_pkg_path+"INTERMITTENCY_EMULATOR_package.vhd", "r+")
    allLines = IE_pkg_file.readlines()
    for i, line in list(enumerate(allLines)):
        if "INTERMITTENCY_PRESCALER" in line:
            allLines.pop(i)
            allLines.insert(i, "constant INTERMITTENCY_PRESCALER: integer := "+str(prescaler_value)+";\n")
        if "INTERMITTENCY_MAX_VAL" in line:
            allLines.pop(i)
            allLines.insert(i, "constant INTERMITTENCY_MAX_VAL_ROM_TRACE: integer := "+str(max_value)+";\n")
        if "NUM_ELEMNTS_ROM" in line:
            allLines.pop(i)
            allLines.insert(i, "constant INTERMITTENCY_NUM_ELEMNTS_ROM: integer := "+str(w_len)+";\n")
    IE_pkg_file.seek(0)
    IE_pkg_file.truncate()
    IE_pkg_file.writelines(allLines)
    IE_pkg_file.close()
            
  
    
    
def compute_max_neuron_number(trace,system_clock_cycle_period=40, voltage_trace_timescale=80, wrng_value=2500, shtdw_value=2300, NV_REG_DELAY_FACTOR=2,window_length=10000):
    """
    This function computes the maximum number of neurons the DNN can have per layer.


    By default is assumed that the voltage trace timescale is twice the 
    system clock. 
    Parameters
    ----------
    trace : dictionary including trace info
    trace must have two entries:
            "samples": list of integer identifying the number of sample
            "voltage": list of floats containing the trace voltage value
    system_clock_cycle_period : integer, optional
        DNN clock cycle period in nanoseconds. The default is 40.
    voltage_trace_timescale : integer, optional
        Shutdown threshold in millivolts. The default is 2200.
    NV_REG_DELAY_FACTOR: integer
        Factor which defines the delay of the nv_reg w.r.t. the
        master system clock (1,2,3,4...)

    Returns
        Voltage trace timescale in nanoseconds. The default is 80.
    wrng_value : TYPE, optional
        Hazard threshold in millivots. The default is 2500.
    shtdw_value : TYPE, optional
    -------
    max_number_neurond: integer
        Number of neuron the DNN can have at maximum to ensure correct save of data.
        
        After analyzying the NV_REG behavior we noticed that the amount of clock
        cycles necessary to save N cells into the nv_reg is given by:
            
            *
        
        Therefore is P is the number of the neurons, the formula is given by:
            
            CLK_CYCLES = (P+2)*nv_reg_delay_factor+6 = P*nv_reg_delay_factor+2*nv_reg_delay_factor+6
            
        Therefore P is given by
        
            P = (CLK_CYCLES - 2*nv_reg_delay_factor - 6)/nv_reg_delay_factor

    """
    

    x_trace = trace["samples"]
    y_trace = trace["voltages"]

    #Trace neglecting the initial power off
    start_sample_value = shtdw_value+300
    indexes = [index for index, value in list(enumerate(y_trace)) if y_trace[index] < start_sample_value]
    start_index = min([i-1 for i, index in list(enumerate(indexes)) if indexes[i]-indexes[i-1]>1])-5
    y_trace = y_trace[start_index:-1]
    x_trace = [int(x[0]) for x in list(enumerate(y_trace))]
    #Trace with the first window_length samples
    y_trace = y_trace[0:window_length]
    x_trace = [int(x[0]) for x in list(enumerate(y_trace))]
    #Computing the minimum sample distance in the trace between the hazard and
    #the shutdown threshold.
    min_sample_distance = 2000
    c = min_sample_distance
    for (sample) in (x_trace):
        data = y_trace[sample]
        if data > wrng_value:
            c = 0
        elif data <= wrng_value and data > shtdw_value:
            c += 1
        elif data <= shtdw_value:
            distance = c
            if distance < min_sample_distance:
                min_sample_distance = distance
        
    
    #Time the device has to correctly save the data
    minimum_backup_time = min_sample_distance*voltage_trace_timescale
    max_backup_clock_cycles = minimum_backup_time/system_clock_cycle_period
    max_number_neurons = int((max_backup_clock_cycles - 6)/NV_REG_DELAY_FACTOR -2)
    return(max_number_neurons)



# def compute_hazard(trace,system_clock_cycle_period=40, voltage_trace_timescale=80, neuron_value=10, shtdw_value=2300, NV_REG_DELAY_FACTOR=2,window_length=10000):

#     max_backup_clock_cycle = (neuron_value+2)*NV_REG_DELAY_FACTOR+6
#     min_sample_distance = 2000
#     c = min_sample_distance
#     for (sample) in (x_trace):
#         data = y_trace[sample]
#         if data > wrng_value:
#             c = 0
#         elif data <= wrng_value and data > shtdw_value:
#             c += 1
#         elif data <= shtdw_value:
#             distance = c
#             if distance < min_sample_distance:
#                 min_sample_distance = distance
#     min_hazard_threshold =     
#     𝐶𝐿𝐾_𝐶𝑌𝐶𝐿𝐸𝑆=(𝑃+2)∗DELAY_FACTOR+6=
# P∗DELAY_FACTOR+2∗DELAY_FACTOR+6
    

    return(0)