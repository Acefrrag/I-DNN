# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 15:40:08 2022

Engineer: Michele Pio Fragasso


Description:
    --Collection of function to test my DNN VHDL architecture and make
    comparisons with the testbench results
"""

import numpy as np
import os
import datetime
import re           #Module to extract numbers in string
import misc

##GLOBAL VARIABLES
dt_string = np.dtype(str)
dt_float = np.dtype(float)
dt_int = np.dtype(int)
dtint64 = np.dtype(np.int64)

pathfiles = "./files/"

def twoscomplement(number, N):
    """
    This functions computes the 2s complement of an integer number with respect to N bits

    Parameters
    ----------
    bitstring : integer
        Number to be complemented w.r.t. 2^N
    Returns
    -------
    twocompl : integer
    2s complement of number w.r.t. N

    """
    twocompl = 2**N - number
    return(twocompl)

def bitstring_to_decimal(bitstring):
    """
    This function converts a string of bits into the decimal representation

    Parameters
    ----------
    bitstring : string
        String of bits, they must contain '0' or '1'

    Returns
    -------
    number: integer
        Base 10 representation of the number

    """
    number = 0
    N = len(bitstring)
    for i in range(N):
        weight = (N-1)-i
        bit = int(bitstring[i])
        digit = bit*2**weight
        number = number + digit
    return(number)

    


def file_to_sfixed(cllct_filename, data_IntWidth):
    
    """
    This function loads the binary files containg DNN parameters
    (Input, weights, bias etc...) expressed in fixed-point notation and converts
    them in the corresponding fractional number(type float).

    Parameters
    ----------
    cllct_filename : string
        path to the file with the data to be converted
    data_IntWidth : TYPE
        Size of Integer Part of data
    Returns
    -------
    data_sfixed_float: : array of floats
        Data converted with the specified precision
    data_width: integer
        Width of the data saved in the files (number of bits)
    """
    
    data_str = np.loadtxt(fname=cllct_filename, dtype=dt_string, ndmin=1)
    data_Width = len(data_str[0])
    data_FracWidth = data_Width-data_IntWidth
    number_data = data_str.shape[0]
    if data_Width <= 32:
        data_integer_sfixed = np.zeros(number_data, dt_int)   #integer representation of the sfixed numbers
    else:
        data_integer_sfixed = np.zeros(number_data, dtint64)         #floating point representation of the weights (to easily perform operations)
    data_sfixed_float = np.zeros(number_data, dt_float)
    for j in range(number_data):
        #Determining sign of the number
        if data_str[j][0] == '1':
            sign = -1
        else:
            sign = 1;
        #Obtaining the signed representation of the fixed number. To be given to the rig function
        if sign == 1:
            data_integer_sfixed[j] = bitstring_to_decimal(data_str[j])
        else:
            data_integer_sfixed[j] = sign*twoscomplement(bitstring_to_decimal(data_str[j]), data_Width)
        data_sfixed_float[j] = data_integer_sfixed[j]/(2**data_FracWidth)

    return (data_sfixed_float,data_Width)


#def neuron_output(weight_filename, file, bias_filename,neuronweight_Width, neuronweight_IntWidth, neuroninput_Width, neuroninput_IntWidth, neuronbias_Width, neuronbias_IntWidth):
    
    #inputs_sfixed_float = file_to_sfixed(cllct_filename=pathfiles+input_filename, data_Width=neuroninput_Width, data_IntWidth=neuroninput_IntWidth)
    #w#eights_sfixed_float = file_to_sfixed(cllct_filename=pathfiles+weight_filename, data_Width=neuronweight_Width, data_IntWidth=neuronweight_IntWidth)
    #bias_sfixed_float = file_to_sfixed(cllct_filename=pathfiles+bias_filename, data_Width=neuronbias_Width, data_IntWidth=neuronbias_IntWidth)

    #n_output_float = np.dot(inputs_sfixed_float, weights_sfixed_float)+bias_sfixed_float
    
    #return(n_output_float)
    
    
def testbench_layer(layer_folder, neuronweight_IntWidth, neuronbias_IntWidth, neuroninput_IntWidth,act_fun):
    """
    This function computes the layer output and generates the VHDL layer testbench 

    Parameters
    ----------
    layer_folder : TYPE
        DESCRIPTION.
    neuronweight_IntWidth : TYPE
        DESCRIPTION.
    neuronbias_IntWidth : TYPE
        DESCRIPTION.
    neuroninput_IntWidth : TYPE
        DESCRIPTION.
    act_fun: string
        Activation function selected "ReLU" or "Sig"
    Returns
    -------
    layer_outputs : numpy ndarray of floats

    """
    
    #extracting the only element from the directory list of files
    layer_folder_path = os.getcwd()+"\..\\\\files\\\\testbenching\\\\"+layer_folder
    layer_folder_contents = os.listdir(layer_folder_path)
    for i in range(len(layer_folder_contents)):
        if layer_folder_contents[i].find("test_dataset") == 0:
            test_data_path = layer_folder_path+"\\\\"+layer_folder_contents[i]
        if layer_folder_contents[i].find("training") == 0:
            training_data_path = layer_folder_path+"\\\\"+layer_folder_contents[i]
        if layer_folder_contents[i] == "sigmoid":
            sigmoid_data_path = layer_folder_path+"\\\\"+layer_folder_contents[i]
    training_data_contents = os.listdir(training_data_path)
    for i in range(len(training_data_contents)):
        if training_data_contents[i] == "weights":
            weights_path = training_data_path+"\\\\"+training_data_contents[i]
        if training_data_contents[i] == "biases":
            biases_path = training_data_path+"\\\\"+training_data_contents[i]
    
    (neuroninputs_sfixed_float, neuron_dataWidth) = file_to_sfixed(test_data_path+"\\\\test_data.txt", neuroninput_IntWidth)
    num_inputs = neuroninputs_sfixed_float.shape[0]
    weight_files = os.listdir(weights_path)
    number_neurons = len(weight_files)
    neuronweights_sfixed_float = []
    c = 0
    for filename in weight_files:
        (n_weight_sfixed_float, weight_dataWidth) = file_to_sfixed(weights_path+"\\\\"+filename, neuronweight_IntWidth)
        neuronweights_sfixed_float.append(n_weight_sfixed_float)
        c = c + 1
        #print(c)
    
    neuronbias_sfixed_float = np.zeros(number_neurons)
    bias_files = os.listdir(biases_path)
    c = 0
    for filename in bias_files:
        (neuronbias_sfixed_float[c], bias_dataWidth) = file_to_sfixed(biases_path+"\\\\"+filename, neuronbias_IntWidth)
        c = c + 1
    #Computing the layer output
    w_sums = np.zeros(number_neurons)
    layer_outputs = np.zeros(number_neurons)
    (sigmoid_inputSize, sigmoid_inputIntSize) = sigmoid_extract_size(sigmoid_data_path)
    for c in range(w_sums.shape[0]):
        w_sums[c] = np.dot(neuroninputs_sfixed_float, neuronweights_sfixed_float[c]) + neuronbias_sfixed_float[c]
    if act_fun == "ReLU":
        for c in range(w_sums.shape[0]):
            if w_sums[c] > 0:
                layer_outputs[c] = w_sums[c]
            else:
                layer_outputs[c] = 0
    else: #act_fun = "Sig"
        # for c in range(number_neurons):
        #     layer_outputs[c] = genSigmoid.sigmoid(w_sums[c])
        LUT = file_to_sfixed(sigmoid_data_path+"\\\\sigContent.mif",neuroninput_IntWidth)
    
        
        for c in range(number_neurons):
            if w_sums[c] > 2**(sigmoid_inputIntSize-1)-2**-((sigmoid_inputSize-sigmoid_inputIntSize)):
                w_sums[c] = 2**(sigmoid_inputIntSize-1)-2**(-(sigmoid_inputSize-sigmoid_inputIntSize))
            else:
                if w_sums[c] < -2**(sigmoid_inputIntSize-1):
                    w_sums[c] = -2**(sigmoid_inputIntSize-1)
                    
            if w_sums[c] >= 0:
                LUT_index=-1+2**(sigmoid_inputSize-1)+misc.float_to_fp_10(w_sums[c], sigmoid_inputSize, sigmoid_inputSize-sigmoid_inputIntSize)+1#+2 is to get the cardinal position inside the LUT. -1 is because Python indexes starts from 0.
            else:
                LUT_index=-2**(sigmoid_inputSize-1)+misc.float_to_fp_10(w_sums[c], sigmoid_inputSize, sigmoid_inputSize-sigmoid_inputIntSize)
            layer_outputs[c] = LUT[0][LUT_index]
        
    create_layer_tb(layer_folder, num_inputs, number_neurons, neuron_dataWidth, neuroninput_IntWidth,weight_dataWidth,neuronweight_IntWidth,sigmoid_inputSize, sigmoid_inputIntSize,act_fun)
    layer_outputs_dict = {}
    for i in range(len(weight_files)):
        layer_outputs_dict[weight_files[i].replace("w","neuron")] = layer_outputs[i]
    return(layer_outputs_dict)

def neuron_weighted_sum(neuron_folder, neuronweight_IntWidth, neuronbias_IntWidth, neuroninput_IntWidth):
    pathfile = os.getcwd()+"\..\\\\files\\\\"+neuron_folder+"\\\\"
    files = os.listdir(pathfile)
    #Neuron weights generation
    weight_index = 0
    bias_index = 0
    input_index = 0
    for i in range(3):
        if files[i].find("weight_file")==0:
            weight_index = i
        if files[i].find("bias_file")==0:
            bias_index = i
        if files[i].find("input_data_file")==0:
            input_index = i
    #Generating weights
    weight_filename = files[weight_index]
    weights_sfixed_float = file_to_sfixed(pathfile+weight_filename, neuronweight_IntWidth)
    input_filename = files[input_index]
    inputs_sfixed_float = file_to_sfixed(pathfile+input_filename, neuroninput_IntWidth)
    bias_filename = files[bias_index]
    bias_sfixed_float = file_to_sfixed(pathfile+bias_filename, neuronbias_IntWidth)
    neuron_ws = np.dot(inputs_sfixed_float, weights_sfixed_float)+bias_sfixed_float
    return(neuron_ws)


def sigmoid_extract_size(sigmoid_data_path):
    logfilename = "\dataFormat.log"
    f = open(sigmoid_data_path+logfilename)
    lines = f.readlines()
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
    

def create_layer_tb(layer_folder,num_inputs, num_outputs, input_dataWidth, input_dataIntWidth, weight_dataWidth, weight_dataIntWidth, sigmoid_inputSize, sigmoid_inputIntSize,act_fun):
       
    date = datetime.datetime.now()
    date_str = date.strftime("%x")+" "+date.strftime("%X")
    tb_path = "..\\\\files\\\\testbenching\\\\"+layer_folder+"\\\\TB_VHDL_output"
    f = open(tb_path+"\\\\layer_tb.vhd","w")
    f.write("----------------------------------------------------------------------------------\n")
    f.write("-- Company: \n")
    f.write("-- Engineer: Michele Pio Fragasso\n")
    f.write("-- \n")
    f.write("-- Create Date: "+date_str+"\n")
    f.write("-- Design Name: \n")
    f.write("-- Module Name: layer_tb - Behavioral\n")
    f.write("-- Project Name: \n")
    f.write("-- Target Devices: \n")
    f.write("-- Tool Versions: \n")
    f.write("-- Description: \n")
    f.write("-- This file has been generated with a python script. Rather than modifying it directly, you shall make changes from the python generating script.\n")
    f.write("-- Dependencies: \n")
    f.write("-- \n")
    f.write("-- Revision:\n")
    f.write("-- Revision 0.01 - File Created\n")
    f.write("-- Additional Comments:\n")
    f.write("-- \n")
    f.write("----------------------------------------------------------------------------------\n")
    f.write("\n")
    f.write("\n")
    f.write("library ieee;\n")
    f.write("use ieee.STD_LOGIC_1164.ALL;\n")
    f.write("use ieee.math_real.all;\n")
    f.write("use ieee.numeric_std.all;\n")
    f.write("use ieee.fixed_pkg.all;\n")
    f.write("\n")
    f.write("library std;\n")
    f.write("use std.textio.all;\n")
    f.write("\n")
    f.write("\n")
    f.write("\n")
    f.write("library work;\n")
    f.write("use work.DNN_package.all;\n")
    f.write("\n")
    f.write("entity layer_tb is\n")
    f.write("end layer_tb;\n")
    f.write("\n")
    f.write("architecture Behavioral of layer_tb is\n")
    f.write("\n")
    f.write("--TESTBENCH CONSTANTS\n")
    f.write("constant layer_tb_num_inputs: natural := "+str(num_inputs)+";\n")
    f.write("constant layer_tb_num_neurons: natural := "+str(num_outputs)+";\n")
    f.write("constant layer_tb_sigmoid_inputdata_Width: natural  := "+str(sigmoid_inputSize)+";\n")
    f.write("constant layer_tb_sigmoid_inputdata_IntWidth: natural := "+str(sigmoid_inputIntSize)+";\n")
    f.write("constant layer_tb_neuron_input_Width: natural := "+str(input_dataWidth)+";\n")
    f.write("constant layer_tb_neuron_input_IntWidth: natural  := "+str(input_dataIntWidth)+";\n")
    f.write("constant layer_tb_neuron_input_FracWidth: natural := layer_tb_neuron_input_Width-layer_tb_neuron_input_IntWidth;\n")
    f.write("constant layer_tb_neuron_weight_Width : natural := "+str(weight_dataWidth)+";\n")
    f.write("constant layer_tb_neuron_weight_IntWidth: natural := "+str(weight_dataIntWidth)+";\n")
    f.write("constant layer_tb_neuron_weight_FracWidth: natural := layer_tb_neuron_weight_Width-layer_tb_neuron_weight_IntWidth;\n")
    f.write("\n")
    f.write("--Code to read input\n")
    f.write("type datain_type is array(0 to layer_tb_num_inputs-1) of sfixed(layer_tb_neuron_input_IntWidth-1 downto -layer_tb_neuron_input_FracWidth);\n")
    f.write("\n")
    f.write("impure function makesfixed (bit_in: in bit_vector(neuron_rom_width-1 downto 0)) return sfixed is\n")
    f.write("    variable fixedpoint_s: sfixed(layer_tb_neuron_input_IntWidth-1 downto -layer_tb_neuron_input_FracWidth);\n")
    f.write("    --variable a: std_logic := 0;\n")
    f.write("    begin\n")
    f.write("    for i in fixedpoint_s'range loop\n")
    f.write("        fixedpoint_s(i) := To_StdULogic(bit_in(i+layer_tb_neuron_input_FracWidth));\n")
    f.write("    end loop;\n")
    f.write("    return fixedpoint_s;\n")
    f.write("end function;\n")
    f.write("\n")
    f.write("impure function gen_datain(dataset_path: in string) return datain_type is\n")
    f.write("\n")
    f.write("file text_header: text open read_mode is dataset_path;\n")
    f.write("variable text_line: line;\n")
    f.write("variable line_i: bit_vector(0 to neuron_rom_width-1);\n")
    f.write("variable dataset_content: datain_type;\n")
    f.write("\n")
    f.write("    begin\n")
    f.write("    for i in dataset_content'range loop\n")
    f.write("        readline(text_header, text_line);\n")
    f.write("        read(text_line, line_i);\n")
    f.write("        dataset_content(i) := makesfixed(line_i);\n")
    f.write("    end loop;\n")
    f.write("    file_close(text_header);\n")
    f.write("    return dataset_content;\n")
    f.write("end function;\n")
    f.write("\n")
    f.write("\n")
    f.write("--Data Input\n")
    f.write("constant tb_path: string :=\"../tb_files/layer/tb2/\";\n")
    f.write("constant layer_parameters_path: string := tb_path;\n")
    f.write("constant dataset_path: string := tb_path&\"inputs/test_data.txt\";\n")
    f.write("\n")
    f.write("\n")
    f.write("signal input_reg: datain_type := gen_datain(dataset_path);\n")
    f.write("\n")
    f.write("signal clk: std_logic := '0';\n")
    f.write("signal data_in: sfixed (layer_tb_neuron_input_IntWidth-1 downto -layer_tb_neuron_input_FracWidth) := input_reg(0);\n")
    f.write("signal start: std_logic:='1';\n")
    f.write("signal data_out: sfixed (layer_tb_neuron_input_IntWidth-1 downto -layer_tb_neuron_input_FracWidth);\n")
    f.write("signal data_out_sel: std_logic_vector(0 to natural(ceil(log2(real(layer_tb_num_neurons))))-1) := (others => '0');--num_outputs=30\n")
    f.write("--signal data_in_sel: std_logic_vector(0 to natural(ceil(log2(real(30))))-1);--num_outputs=30\n")
    f.write("signal data_v: std_logic := '0';\n")
    f.write("signal in_sel: std_logic_vector(0 to natural(ceil(log2(real(layer_tb_num_inputs))))-1):=(others=>'0');--num_inputs=30\n")
    f.write("signal start_scan: std_logic := '0';\n")
    f.write("\n")
    f.write("\n")
    f.write("component layer is\n")
    f.write("generic(\n")
    f.write("    num_inputs: natural;\n")
    f.write("    num_outputs: natural;\n")
    f.write("	neuron_input_IntWidth: natural;\n")
    f.write("	neuron_input_FracWidth: natural;\n")
    f.write("	neuron_weight_IntWidth: natural;\n")
    f.write("	neuron_weight_FracWidth: natural;\n")
    f.write("    layer_no: natural;\n")
    f.write("    act_fun_type: string;\n")
    f.write("	sigmoid_inputdataWidth: natural;\n")
    f.write("	sigmoid_inputdataIntWidth: natural;\n")
    f.write("	lyr_prms_path: string); -- If the user choose an analytical activation function the number of sample have to be chosen\n")
    f.write("port (\n")
    f.write("    clk: in std_logic;\n")
    f.write("    data_in: in sfixed (neuron_input_IntWidth-1 downto -neuron_input_FracWidth);\n")
    f.write("    data_out_sel: in std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1):=(others => '0');--num_outputs=30\n")
    f.write("    start: in std_logic;\n")
    f.write("    data_out: out sfixed (neuron_input_IntWidth-1 downto -neuron_input_FracWidth);\n")
    f.write("    data_in_sel: out std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);--num_outputs=30\n")
    f.write("    data_v: out std_logic);\n")
    f.write("end component layer;\n")
    f.write("begin\n")
    f.write("\n")
    f.write("layer_comp: layer\n")
    f.write("generic map(\n")
    f.write("num_inputs => layer_tb_num_inputs,\n")
    f.write("num_outputs => layer_tb_num_neurons,\n")
    f.write("neuron_input_IntWidth => layer_tb_neuron_input_IntWidth,\n")
    f.write("neuron_input_FracWidth => layer_tb_neuron_input_FracWidth,\n")
    f.write("neuron_weight_IntWidth => layer_tb_neuron_weight_IntWidth,\n")
    f.write("neuron_weight_FracWidth => layer_tb_neuron_weight_FracWidth,\n")
    f.write("layer_no => 1,\n")
    f.write("act_fun_type => \""+act_fun+"\",\n")
    f.write("sigmoid_inputdataWidth => 5,\n")
    f.write("sigmoid_inputdataIntWidth => 2,\n")
    f.write("lyr_prms_path => layer_parameters_path\n")
    f.write(")\n")
    f.write("port map(\n")
    f.write("clk => clk,\n")
    f.write("data_in => data_in,\n")
    f.write("data_out_sel => data_out_sel,\n")
    f.write("start => start,\n")
    f.write("data_out => data_out,\n")
    f.write("data_in_sel => in_sel,\n")
    f.write("data_v => data_v);\n")
    f.write("\n")
    f.write("\n")
    f.write("clk_gen: process is\n")
    f.write("begin\n")
    f.write("wait for 20 ns;\n")
    f.write("clk <= not(clk);\n")
    f.write("end process clk_gen;\n")
    f.write("\n")
    f.write("\n")
    f.write("--data_gen: process is\n")
    f.write("--the assignment <= is a non-blocking assignment\n")
    f.write("--begin\n")
    f.write("--if rising_edge(clk) then\n")
    f.write("    --in_sel <= std_logic_vector(unsigned(in_sel) + 1);\n")
    f.write("    --if unsigned(in_sel) >= neuron_rom_depth then --After all the data is fed to the layer start is permanently set to 0. Leaving the layer in the idle state.\n")
    f.write("        --addr_TC <= '1';\n")
    f.write("        --start <= '0';\n")
    f.write("        --in_sel <= (others => '0');\n")
    f.write("    --else\n")
    f.write("        --input_valid <= '1';\n")
    f.write("        data_in <= input_reg(to_integer(unsigned(in_sel)));\n")
    f.write("    --end if;    \n")
    f.write("--end if;\n")
    f.write("--end process data_gen;\n")
    f.write("\n")
    f.write("out_access: process(data_v) is\n")
    f.write("\n")
    f.write("begin\n")
    f.write("if data_v='1' then\n")
    f.write("    data_out_sel <= std_logic_vector(to_unsigned(integer'(7),5));\n")
    f.write("end if;\n")
    f.write("end process out_access;\n")
    f.write("\n")
    f.write("start_pr: process is\n")
    f.write("begin\n")
    f.write("wait for 60 ns;\n")
    f.write("start <= '0';\n")
    f.write("end process start_pr;\n")
    f.write("\n")
    f.write("\n")
    f.write("\n")
    f.write("\n")
    f.write("\n")
    f.write("end Behavioral;\n")
    f.close()