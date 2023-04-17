# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 15:40:08 2022

Engineer: Michele Pio Fragasso


Description:
    --Collection of function to test generated DNN VHDL architecture and make
    comparisons with the testbench results.
"""

import numpy as np
import os
import datetime
import re           #Module to extract numbers in string
import misc
import sys

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
    This function computes the layer output and generates the VHDL layer
    testbench.

    Parameters
    ----------
    layer_folder : name of the layer folder inside ../files/testbenching/
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
    
    #Extracting paths to the test data, training_data and sigmoid content
    layer_folder_path = os.getcwd()+"\..\\\\files\\\\testbenching\\\\"+layer_folder
    layer_folder_contents = os.listdir(layer_folder_path)
    for i in range(len(layer_folder_contents)):
        if layer_folder_contents[i].find("test_dataset") == 0:
            test_data_path = layer_folder_path+"\\\\"+layer_folder_contents[i]
        if layer_folder_contents[i].find("training") == 0:
            training_data_path = layer_folder_path+"\\\\"+layer_folder_contents[i]
        if layer_folder_contents[i] == "sigmoid":
            sigmoid_data_path = layer_folder_path+"\\\\"+layer_folder_contents[i]
    #Extracting paths to weights and biases from the traiining data folder
    training_data_contents = os.listdir(training_data_path)
    for i in range(len(training_data_contents)):
        if training_data_contents[i] == "weights":
            weights_path = training_data_path+"\\\\"+training_data_contents[i]
        if training_data_contents[i] == "biases":
            biases_path = training_data_path+"\\\\"+training_data_contents[i]
    
    #Loading input to the layer
    (neuroninputs_sfixed_float, neuron_dataWidth) = file_to_sfixed(test_data_path+"\\\\test_data.txt", neuroninput_IntWidth)
    num_inputs = neuroninputs_sfixed_float.shape[0]
    
    #Loading weights of the layer
    weight_files = os.listdir(weights_path)
    number_neurons = len(weight_files)
    neuronweights_sfixed_float = []
    c = 0
    for filename in weight_files:
        (n_weight_sfixed_float, weight_dataWidth) = file_to_sfixed(weights_path+"\\\\"+filename, neuronweight_IntWidth)
        neuronweights_sfixed_float.append(n_weight_sfixed_float)
        c = c + 1
        #print(c)
    
    #Loading biases of the layer
    neuronbias_sfixed_float = np.zeros(number_neurons)
    bias_files = os.listdir(biases_path)
    c = 0
    for filename in bias_files:
        (neuronbias_sfixed_float[c], bias_dataWidth) = file_to_sfixed(biases_path+"\\\\"+filename, neuronbias_IntWidth)
        c = c + 1
        
    #Computing the layer's output
    #Computing weightes sums
    w_sums = np.zeros(number_neurons)
    layer_outputs = np.zeros(number_neurons)
    (sigmoid_inputSize, sigmoid_inputIntSize) = sigmoid_extract_size(sigmoid_data_path)
    for c in range(w_sums.shape[0]):
        w_sums[c] = np.dot(neuroninputs_sfixed_float, neuronweights_sfixed_float[c]) + neuronbias_sfixed_float[c]
    #Applying activation function
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
    
    #Creating Layer testbench VHDL file
    create_layer_tb(layer_folder, num_inputs, number_neurons, neuron_dataWidth, neuroninput_IntWidth,weight_dataWidth,neuronweight_IntWidth,sigmoid_inputSize, sigmoid_inputIntSize,act_fun)
    
    #Packing layer output
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
    sys.stdout = f
    print("""   
----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso
-- 
-- Create Date: """+date_str+"""
-- Design Name: 
-- Module Name: I_layer_tb - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: This layer testbench is generated with a python script which compares the VHDL with the python output.
--			It tests the capababilities to support different activation functions and different sizes for the Integer and Fractional part of input/output data and weights.
----------------------------------------------------------------------------------

library std;
use std.textio.all;

library ieee;
use ieee.STD_LOGIC_1164.ALL;
use ieee.math_real.all;
use ieee.numeric_std.all;

library work;
use work.I_DNN_package.all;
use work.COMMON_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.INTERMITTENCY_EMULATOR_package.all;

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity I_layer_tb is

end I_layer_tb;


architecture Behavioral of I_layer_tb is

--TESTBENCH CONSTANTS
constant layer_tb_num_inputs: natural := """+str(num_inputs)+""";
constant layer_tb_num_neurons: natural := """+str(num_outputs)+""";
constant layer_tb_sigmoid_inputdata_Width: natural  := """+str(sigmoid_inputSize)+""";
constant layer_tb_sigmoid_inputdata_IntWidth: natural := """+str(sigmoid_inputIntSize)+""";
constant layer_tb_neuron_inout_Width: natural := 32;
constant layer_tb_neuron_inout_IntWidth: natural  := """+str(input_dataIntWidth)+""";
constant layer_tb_neuron_inout_FracWidth: natural := layer_tb_neuron_inout_Width-layer_tb_neuron_inout_IntWidth;
constant layer_tb_neuron_weight_Width : natural := 32;
constant layer_tb_neuron_weight_IntWidth: natural := """+str(weight_dataIntWidth)+""";
constant layer_tb_neuron_weight_FracWidth: natural := layer_tb_neuron_weight_Width-layer_tb_neuron_weight_IntWidth;
--constant layer_tb_voltage_trace_path: string := "../src/NORM/voltage_traces/I_layer_trace_complete.txt";
constant layer_tb_voltage_trace_path: string := "./voltage_traces/voltage_trace2.txt";

type datain_type is array(0 to layer_tb_num_inputs-1) of sfixed(layer_tb_neuron_inout_IntWidth-1 downto -layer_tb_neuron_inout_FracWidth);

impure function datain_makesfixed (bit_in: in bit_vector(layer_tb_neuron_inout_Width-1 downto 0)) return sfixed is
    variable fixedpoint_s: sfixed(layer_tb_neuron_inout_IntWidth-1 downto -layer_tb_neuron_inout_FracWidth);
    --variable a: std_logic := 0;
    begin
    for i in fixedpoint_s'range loop
        fixedpoint_s(i) := To_StdULogic(bit_in(i+layer_tb_neuron_inout_FracWidth));
    end loop;
    return fixedpoint_s;
end function;

impure function gen_datain(dataset_path: in string) return datain_type is
file text_header: text open read_mode is dataset_path;
variable text_line: line;
variable line_i: bit_vector(0 to layer_tb_neuron_inout_Width-1);
variable dataset_content: datain_type;

    begin
    for i in dataset_content'range loop
        readline(text_header, text_line);
        read(text_line, line_i);
        dataset_content(i) := datain_makesfixed(line_i);
    end loop;
    file_close(text_header);
    return dataset_content;
end function;


--Data Input
constant tb_path: string :="./tb_files/layer/tb2/";
constant layer_parameters_path: string := tb_path;
constant layer_dataset_path: string := "../"&tb_path&"inputs/test_data.txt";


signal input_reg: datain_type := gen_datain(layer_dataset_path);


constant hazard_threshold : integer := 2600;
--TestBench Signals
--Volatile Architecture Signals
--Input
signal clk: std_logic:= '0';
signal data_in: sfixed(layer_tb_neuron_inout_IntWidth-1 downto -layer_tb_neuron_inout_FracWidth):= (others => '0');
signal data_out_sel: std_logic_vector(0 to natural(ceil(log2(real(layer_tb_num_neurons))))-1) := (others => '0');
signal start: std_logic:='1';--to increment the counter while the output is begin computed
--Output
signal data_out: sfixed(layer_tb_neuron_inout_IntWidth-1 downto -layer_tb_neuron_inout_FracWidth);--The next layer controls which neuron's output to access
signal data_in_sel: std_logic_vector(0 to natural(ceil(log2(real(layer_tb_num_inputs))))-1);
signal data_v: std_logic;
signal out_v_set: integer range 0 to 3:=0;
--Augumented Pins
--Input
signal n_power_reset: std_logic:='0';--Device is powered up
signal fsm_nv_reg_state, fsm_state_sig: fsm_nv_reg_state_t:=shutdown_s;
signal nv_reg_busy: std_logic:='0';
signal nv_reg_busy_sig:  std_logic:='0';
signal nv_reg_dout: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0):=(others=>'0');
signal previous_layer: std_logic:='0';--To decide wheather to save or not the output
--Output
signal task_status: std_logic;
signal nv_reg_en: std_logic;
signal nv_reg_we: std_logic;
signal nv_reg_addr: std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
signal nv_reg_din: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
signal current_layer: std_logic;
--
signal reset_emulator       : std_logic; 
signal threshold_value      : intermittency_arr_int_type(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0);
signal threshold_compared   : std_logic_vector(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0); 
signal select_threshold     : integer range 0 to INTERMITTENCY_NUM_THRESHOLDS -1; --This is used to select the threshold for power failure
signal thresh_stats         : threshold_t;
--
signal resetN_emulator      : std_logic;


component nv_reg is
    Generic(
        MAX_DELAY_NS: INTEGER;
        NV_REG_WIDTH: INTEGER;
        NV_REG_DEPTH: INTEGER
    );
    Port ( 
        clk             : in STD_LOGIC;
        resetN          : in STD_LOGIC; 
        power_resetN 	: in STD_LOGIC;
        -------------chage from here-------------- 
        busy            : out STD_LOGIC;
        busy_sig        : out STD_LOGIC;
        en              : in STD_LOGIC;
        we              : in STD_LOGIC;
        addr            : in STD_LOGIC_VECTOR(integer(ceil(log2(real(nv_reg_depth))))-1 DOWNTO 0);
        din             : in STD_LOGIC_VECTOR(31 DOWNTO 0);
        dout            : out STD_LOGIC_VECTOR(31 DOWNTO 0)
        -------------chage to here---------------- 
    );
end component;

component I_layer is
generic(                                                                                
    --------GENERIC---------
    constant num_inputs: natural;
    constant num_outputs: natural ;
	constant neuron_inout_IntWidth: natural;
	constant neuron_inout_FracWidth: natural;
	constant neuron_weight_IntWidth: natural;
	constant neuron_weight_FracWidth: natural;
    constant layer_no: natural;                                                    --layer_no          :     Layer number (identifier)
    constant act_fun_type: string;                                                --act_type          :     Choose between "ReLU","Sig"
	constant sigmoid_inputdataWidth: natural;
	constant sigmoid_inputdataIntWidth: natural;
	constant lyr_prms_path: string);
port(                                                                                   --------PORTS-------
    --------INPUTS-------
    clk: in std_logic;                                                                  --clk               :
    data_in: in sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);                     --data_in           :
    data_out_sel: in std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1);   --data_out_sel      :
    start: in std_logic;                                                                --start             :       Signal to trigger the layer and start computation
    -------OUTPUTS-------
    data_out: out sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);                 --data_out          :       I-th neuron output
    data_in_sel: inout std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);  --data_in_sel       :       To select the i-th neuron output
    data_v: out std_logic;                                                              --data_v            :       Aknowledges the layer output validity. Used to save the output of the layer when a hazard occurs. Triggers the next layer                                                                                                                                                                                                                                               
    ------ADDED PINS-----                                                                                        
    --------Inputs-------
    n_power_reset: in std_logic;                                                        --n_power_reset     :       Emulates power failure. 1 Power on 0: Power Off
    fsm_nv_reg_state: in fsm_nv_reg_state_t;                                            --fsm_nv_reg_state  :       This contains the imperative commands to the varc.
    nv_reg_busy: in std_logic;                                                          --nv_reg_busy       :       Together with nv_reg_bbusy_sig aknowledges the availability fro r/w operation into/from the nv_reg
    nv_reg_busy_sig: in  STD_LOGIC;                                                     --nv_reg_busy_sig   :    
    nv_reg_dout: in STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);                          --nv_reg_dout       :       Contains the nv_reg output (used when recovering data)
    out_v_set: in integer range 0 to 3;                                                              --out_v_set            :     This resets the validity bit(Only one layer output can be valid at a time).
                                                                                        
    -------Outputs-------
    task_status: out std_logic;                                                         --task_status       :       0: The recovery/save operation has finished. 1: It is still being carried on.
    nv_reg_en: out std_logic;                                                           --nv_reg_en         :       1: Reading/Wrinting operation request. 0: nv_reg is disabled
    nv_reg_we: out std_logic;                                                           --nv_reg_we         :       1: Write Operation Request. 0: No operation
    nv_reg_addr: out std_logic_vector(nv_reg_addr_width_bit-1 downto 0);                --nv_reg_addr       :       Contains the address of the nv_reg to access         
    nv_reg_din: out STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0)                           --nv_reg_din        :       It contains data to write into the nv_rega
    );        
end component;

component fsm_nv_reg_db is
    port ( 
        clk                     : in STD_LOGIC;
        resetN                  : in STD_LOGIC;
        thresh_stats            : in threshold_t;
        task_status             : in STD_LOGIC;
        fsm_state               : out fsm_nv_reg_state_t;
        fsm_state_sig           : out fsm_nv_reg_state_t --used with care (it is the future state of the machine, and it is combinatory so it is prone to glitces)
    );
end component;

component intermittency_emulator is
    generic(
        constant voltage_trace_path: string
    ); 
    port(
        sys_clk             : in std_logic;
        threshold_value     : in intermittency_arr_int_type(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0); 
        select_threshold    : in integer range 0 to INTERMITTENCY_NUM_THRESHOLDS -1;
        reset_emulator      : out std_logic; 
        threshold_compared  : out std_logic_vector(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0)
    );
end component;



begin

I_layer_comp: I_layer
generic map
(
    num_inputs => layer_tb_num_inputs,
    num_outputs => layer_tb_num_neurons,
	neuron_inout_IntWidth => layer_tb_neuron_inout_IntWidth,
	neuron_inout_FracWidth => layer_tb_neuron_inout_FracWidth,
	neuron_weight_IntWidth => layer_tb_neuron_weight_IntWidth,
	neuron_weight_FracWidth => layer_tb_neuron_weight_FracWidth,
    layer_no => 1,														--Layer number (identifier)
    act_fun_type => "ReLu", 											-- Choose between "ReLU" and "Sig"
    sigmoid_inputdataWidth => layer_tb_sigmoid_inputdata_Width,
	sigmoid_inputdataIntWidth => layer_tb_sigmoid_inputdata_IntWidth,
	lyr_prms_path => layer_parameters_path
)
port map
(   
    --Volatile Pins
    --Inputs
    clk => clk,
    data_in => data_in,
    data_out_sel => data_out_sel,
    start => start,
    --Outputs    
    data_out => data_out,
    data_in_sel => data_in_sel,
    data_v => data_v,
    --Augumented Pins
    --Input
    n_power_reset => resetN_emulator,
    fsm_nv_reg_state => fsm_nv_reg_state,
    nv_reg_busy => nv_reg_busy,
    nv_reg_busy_sig => nv_reg_busy_sig,
    nv_reg_dout => nv_reg_dout,
    --Output
    task_status => task_status,
    nv_reg_en => nv_reg_en,
    nv_reg_we => nv_reg_we,
    nv_reg_addr => nv_reg_addr,
    nv_reg_din => nv_reg_din,
    out_v_set => out_v_set
);

INTERMITTENCY_EMULATOR_1 : intermittency_emulator
    generic map(
        voltage_trace_path => layer_tb_voltage_trace_path
    )
    port map(
        sys_clk             => clk,
        reset_emulator      => reset_emulator,
        threshold_value     => threshold_value,
        threshold_compared  => threshold_compared,
        select_threshold    => select_threshold
    );

fsm_nv_reg_db_comp: fsm_nv_reg_db
    port map(
        clk             => clk,
        resetN          => resetN_emulator,
        thresh_stats    => thresh_stats,
        task_status     => task_status,
        fsm_state       => fsm_nv_reg_state,
        fsm_state_sig   => fsm_state_sig
    );

nv_reg_comp: nv_reg
    Generic map(
        MAX_DELAY_NS => FRAM_MAX_DELAY_NS,
        NV_REG_WIDTH => NV_REG_WIDTH,
        NV_REG_DEPTH => layer_tb_num_neurons+3
    )
    Port map( 
        clk             => clk,
        resetN          => '1',
        power_resetN 	=> resetN_emulator,
        -------------chage from here-------------- 
        busy            => nv_reg_busy,
        busy_sig        => nv_reg_busy_sig,
        en              => nv_reg_en,
        we              => nv_reg_we,
        addr            => nv_reg_addr,
        din             => nv_reg_din,
        dout            => nv_reg_dout
        -------------chage to here---------------- 
        );

clk_gen: process is
begin
    wait for 20 ns;
    clk <= not(clk);
end process;

start_gen: process is
begin
    --Testing with hazard during w_sum(after computing element number 12) start at 780 ns. 
    wait for 880 ns;
    start <= '0';
    --Testing with no power failure start at 10060 ns.
    wait for 9160 ns;
    start <= '1';
    wait for 200 ns;
    start <= '0';
    --Testing with hazard at the end of w_sum(after computing element 28) start at 13220 ns.
    wait for 2980 ns;
    start <= '1';
    wait for 200 ns;
    start <= '0';
    --Testing with hazard at b_sum. Start at 22780 ns.
    wait for 9360 ns;
    start <= '1';
    wait for 200 ns;
    start <= '0';
    --Testing with hazard at act_log. Start 
    wait for 9640 ns;
    start <= '1';
    wait for 200 ns;
    start <= '0';
    wait for 8100 ns;
    start <= '1';
    wait for 200 ns;
    start <= '0';
    wait for 10740 ns;
    start <= '1';
    wait for 200 ns;
    start <= '0';
    wait;
end process;

out_v_set_gen: process is
begin
    --Invalidating output after test 1. 
    wait for 8540 ns;
    out_v_set <= 1;
    wait for 40 ns;
    out_v_set <= 2;
    --Invalidating output after test 2
    wait for 2820 ns;
    out_v_set <= 1;
    wait for 40 ns;
    out_v_set <= 2;
    --Invalidating output after test 3
    wait for 9560 ns;
    out_v_set <= 1;
    wait for 40 ns;
    out_v_set <= 2;
    wait for 9520 ns;
    out_v_set <= 1;
    wait for 40 ns;
    out_v_set <= 2;
    wait for 9780 ns;
    out_v_set <= 1;
    wait for 40 ns;
    out_v_set <= 2;
    wait for 11360 ns;
    out_v_set <= 1;
    wait for 40 ns;
    out_v_set <= 2;
    wait;
end process;

data_in <= input_reg(to_integer(unsigned(data_in_sel)));
resetN_emulator <= not(reset_emulator);
thresh_stats <= hazard when threshold_compared(1) = '1' else nothing;
-- sets reset_emulator threshold
threshold_value(0) <= RST_EMU_THRESH;
-- sets the value for the hazard threshold, used by fsm_nv_reg_db
threshold_value(1) <= hazard_threshold;

end Behavioral;
)""")
    f.close()
    #Set default value for standard output
    sys.stdout = sys.__stdout__