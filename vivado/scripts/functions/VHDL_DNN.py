# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 23:01:26 2023

Engineer: Michele Pio Fragasso


Description:
    --File description
"""

import network2
import sys
import TestData as genData


def create_file(DNN_in_prms):
    return()

def extract_input(training_file):
    num_inputs_DNN = 784
    
    f = open(training_file, "r")
    allLines = f.readlines()
    
    DNN_in_prms = {}
    
    for line in allLines:
        key, value = line.strip().split(",")
        DNN_in_prms[key] = value
        if key != "act_fun_type" and key != "sizes":
            if "." in value:
                DNN_in_prms[key] = float(value)
            else:
                DNN_in_prms[key] = int(value)
    value = DNN_in_prms["sizes"]
    data_list = value.strip()[1:-1].split(";")
    data_list = [int(item) for item in data_list]
    DNN_in_prms["sizes"] = data_list
    DNN_in_prms["sizes"].insert(0,num_inputs_DNN)
    return(DNN_in_prms)

def train(DNN_in_prms):
    
    training_data, validation_data, test_data = DNN_in_prms["datasets"]
    
    #Creating network
    net = network2.Network(DNN_in_prms["sizes"], DNN_in_prms["act_fun_type"])#change the number of layers or number of neurons in each layer here
    
    epochs = DNN_in_prms["epochs"]
    batch_size = DNN_in_prms["batch_size"]
    eta = DNN_in_prms["eta"]
    lmbda = DNN_in_prms["lmbda"]
    (e_c, e_a, t_c, t_a) = net.SGD(training_data, epochs=epochs, mini_batch_size=batch_size, eta=eta, lmbda=lmbda,evaluation_data=validation_data, monitor_evaluation_accuracy=True)

    
    return(net, e_a)

def savenet(net, path):
    net.save(path)

def savelogfile(net, e_a, path,DNN_in_prms):
    #SAVING TRAINING REPORT
   
    f = open(path, 'w')
    
    training_data,validation_data, test_data = DNN_in_prms["datasets"]
    epochs = DNN_in_prms["epochs"]
    batch_size = DNN_in_prms["batch_size"]
    eta = DNN_in_prms["eta"]
    lmbda = DNN_in_prms["lmbda"]
    date = DNN_in_prms["date"]
    
    f.write("TRAINING REPORT - "+ date + "\n \n")
    f.write("Number of layers: "+str(net.num_layers)+"\n")
    f.write("Neurons per layer: "+str(net.sizes)+"\n")
    f.write("Activation function: "+str(net.act_fun_type))
    f.write("Training data size: "+str(len(training_data))+"\n")
    f.write("Training epochs: "+ str(epochs)+"\n")
    f.write("Training batch size:"+ str(batch_size)+"\n")
    f.write("Training learning rate: eta ="+ str(eta)+"\n")
    f.write("Training regularitation value: lambda ="+ str(lmbda)+"\n")
    f.write("Evaluation data size: "+str(len(validation_data))+"\n")
    f.write("Evaluation Accuracies per epoch: \n")
    for i in range(epochs):
        f.write("Epoch:"+str(i)+" Accuracy: "+str(e_a[i])+"/"+str(len(validation_data))+"\n")
    f.close()    

def makepackage(DNN_in_prms, net):
    
    
    VHDL_architectures_path = DNN_in_prms["architecturepath"]
    date = DNN_in_prms["date"]
    sigmoid_inputSize = net.sigmoidinputSize
    sigmoid_inputIntSize = net.sigmoidinputIntSize
    neuron_input_Width = net.neuroninputSize
    neuron_input_IntWidth = net.neuroninputIntSize
    neuron_weight_IntWidth = net.neuronweightIntSize
    neuron_weight_Width = net.neuronweightSize
    act_fun_type = net.act_fun_type
    num_hidden_layers = net.num_hidden_layers
    num_inputs = net.sizes[:-1]
    num_outputs = net.sizes[1:]
    try:
        f = open(VHDL_architectures_path+"/I_DNN_package.vhd", "w")
        f.write(
    "----------------------------------------------------------------------------------\n"
    "-- Company: \n"
    "-- Engineer: Michele Pio Fragasso \n"
    "-- \n"
    "-- Create Date: "+str(date)+"\n"
    "-- Design Name: \n"
    "-- Module Name: DNN - Behavioral \n"
    "-- Project Name: \n"
    "-- Target Devices: \n"
    "-- Tool Versions:\n"
    "-- Description: \n"
    "-- \n"
    "-- Dependencies: \n"
    "-- \n"
    "-- Revision: \n"
    "-- Revision 0.01 - File Created \n"
    "-- Additional Comments: \n"
    "----------------------------------------------------------------------------------\n"
    "library ieee_proposed;\n"
    "use ieee_proposed.fixed_pkg.all;"
    "\n"
    "library ieee;\n"
    "use ieee.std_logic_1164.all;\n"
    "use ieee.math_real.all;\n"
    "\n"
    "\n"
    "   package I_DNN_package is\n"
    "   -- Package Declarative Part\n"
    "   --(It contains variables, types, procedures and function declaration)\n"
    "    -- Package Declarative Part\n"
    "	--DNN constants\n"
    "	constant DNN_num_inputs: natural := 784;\n"
    "	constant DNN_sigmoid_inputdata_Width: natural  := "+str(sigmoid_inputSize)+";\n"
    "	constant DNN_sigmoid_inputdata_IntWidth: natural := "+str(sigmoid_inputIntSize)+";\n"
    "	--Neuron input (and output) sizes\n"
    "	constant DNN_neuron_inout_Width: natural := "+str(neuron_input_Width)+";\n"			
    "	constant DNN_neuron_inout_IntWidth: natural  := "+str(neuron_input_IntWidth)+";\n"
    "	constant DNN_neuron_inout_FracWidth: natural := DNN_neuron_inout_Width-DNN_neuron_inout_IntWidth;\n"
    "	--Neuron weight sizes\n"
    "	constant DNN_neuron_weight_Width: natural := "+str(neuron_weight_Width)+";\n"
    "	constant DNN_neuron_weight_IntWidth: natural := "+str(neuron_weight_IntWidth)+";\n"
    "	constant DNN_neuron_weight_FracWidth: natural := DNN_neuron_weight_Width-DNN_neuron_weight_IntWidth;\n"
    "	constant DNN_multiple_images_prms_path: string := \"./tb_files/DNN/multiple_images/\";\n"
    "   constant DNN_prms_path: string := \"../tb_files/DNN/tb4/\";\n"
    "	constant act_fun_type: string  := \""+str(act_fun_type)+"\";\n"
    "   --TestBench for neuron entities and its subentities\n"
    "   -- Layers variables\n"
    "   -- Input Layer\n"
    "   constant num_hidden_layers: natural :="+str(num_hidden_layers)+";\n"
    "   --DNN parameters\n"
    "   type layer_neurons_type is array(1 to num_hidden_layers) of natural;\n"
                    )
        string1=(
    "   constant log2_layer_inputs: layer_neurons_type := (")
        string2=(
    "   constant log2_layer_outputs: layer_neurons_type := (")
        for i in range (1,num_hidden_layers):
            string1 = string1 + "natural(ceil(log2(real("+str(num_inputs[i-1])+")))),"
            string2 = string2 + "natural(ceil(log2(real("+str(num_outputs[i-1])+")))),"
        string1 = string1 + "natural(ceil(log2(real("+str(num_inputs[num_hidden_layers-1])+")))));\n"
        string2 = string2 + "natural(ceil(log2(real("+str(num_outputs[num_hidden_layers-1])+")))));\n"
        f.write(string1+string2)
        string1 =(
    "   constant layer_inputs: layer_neurons_type := (")
        string2 =(
    "   constant layer_outputs: layer_neurons_type := (")
        for i in range (1,num_hidden_layers):
            string1 = string1 + str(num_inputs[i-1]) + ","
            string2 = string2 + str(num_outputs[i-1]) + ","
        string1 = string1 + str(num_inputs[num_hidden_layers-1])+");\n"
        string2 = string2 + str(num_outputs[num_hidden_layers-1])+");\n"
        f.write(string1 + string2) 
        f.write(
    "   constant validation_dataset_path: string := \"../../../../../../scripts/datasets/testData/test_data.txt\";\n"
    "   constant bias_int_width: natural := 1;            \n"
    "\n"
    "\n"
    "\n"
    "   --Functions Declaration\n"
    "   function isum(l_n: layer_neurons_type)return natural;\n"
    "   function low(vect_lengths: layer_neurons_type; index: natural) return natural;\n"
    "   function high(VectorBits: layer_neurons_type; index: natural) return natural; \n"   
    "   function get_subvector(vector: std_logic_vector; VectorBits: layer_neurons_type;index: natural) return std_logic_vector;\n"
    "\n"
    "\n"
    "\n" 
    "\n"
    "\n"
    "\n"
    "   end package I_DNN_package;\n"
    "\n"
    "   package body I_DNN_package is\n"
    "\n"    
    "   --Package Body Section\n"
    "function isum(l_n: layer_neurons_type) return natural is\n"
    "        variable result: natural := 0;\n"
    "            begin\n"
    "            for i in l_n'range loop\n"
    "                result := result + l_n(i);\n"
    "        end loop;\n"
    "            return result;\n"
    "end function;             \n"
    "    function low(vect_lengths : layer_neurons_type; index : NATURAL) return NATURAL is\n"
    "        variable pos : NATURAL := 0;\n"
    "            begin\n"
    "            for i in vect_lengths'low to index - 1 loop\n"
    "               pos := pos + vect_lengths(i);\n"
    "          end loop; \n"
    "          return pos;\n"
    "      end function;\n"
    "\n"
    "\n"                
    "function high(VectorBits : layer_neurons_type; index : NATURAL) return NATURAL is\n"
    "     variable pos : NATURAL := 0;\n"
    "     begin\n"
    "        for i in VectorBits'low to index loop\n"
    "           pos := pos + VectorBits(i);\n"
    "        end loop;\n"
    "        return pos - 1;\n"
    "end function;\n"
    "\n"                
    "               function get_subvector(vector: std_logic_vector; VectorBits: layer_neurons_type; index : natural) return std_logic_vector is\n"
    "     begin\n"
    "     return vector(high(VectorBits, index) downto low(VectorBits, index));\n"
    "end function;\n"
    "\n"
    "end package body I_DNN_package;   \n"
    )
    finally:
        f.close()
    
def mkMIpackage(path, DNN_in_prms, net):

    sizes = net.sizes
    sigmoid_inputSize = net.sigmoidinputSize
    sigmoid_inputIntSize = net.sigmoidinputIntSize
    neuroninputSize = net.neuroninputSize
    neuroninputIntSize = net.neuroninputIntSize
    neuronweightSize = net.neuronweightSize
    neuronweightIntSize = net.neuronweightIntSize
    act_fun_type = net.act_fun_type
    num_hidden_layers = net.num_hidden_layers
    
    try:
        f = open(path+"/I_DNN_MI_package.vhd","w")
        sys.stdout = f
        print("""
----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 01/28/2023 07:02:29 PM
-- Design Name: 
-- Module Name: I_DNN_multiple_images_package - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: This file contains variable used by the DNN testbench for multiple images
-- That testbench uses different parameters and datasets.
-- The prefix MI specificy to what testbench the system applies, which is the mulitple images
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------
library IEEE;
use ieee.math_real.all;


package I_DNN_MI_package is
-- Package Declarative Part
   --(It contains variables, types, procedures and function declaration)
    -- Package Declarative Part
	--DNN constants
	constant MI_DNN_num_inputs: natural := """+str(sizes[0])+""";
	constant MI_DNN_sigmoid_inputdata_Width: natural  := """+str(sigmoid_inputSize)+""";
	constant MI_DNN_sigmoid_inputdata_IntWidth: natural := """+str(sigmoid_inputIntSize)+""";
	--Neuron input (and output) sizes
	constant MI_DNN_neuron_inout_Width: natural := """+str(neuroninputSize)+""";
	constant MI_DNN_neuron_inout_IntWidth: natural  := """+str(neuroninputIntSize)+""";
	constant MI_DNN_neuron_inout_FracWidth: natural := MI_DNN_neuron_inout_Width-MI_DNN_neuron_inout_IntWidth;
	--Neuron weight sizes
	constant MI_DNN_neuron_weight_Width: natural := """+str(neuronweightSize)+""";
	constant MI_DNN_neuron_weight_IntWidth: natural := """+str(neuronweightIntSize)+""";
	constant MI_DNN_neuron_weight_FracWidth: natural := MI_DNN_neuron_weight_Width-MI_DNN_neuron_weight_IntWidth;
	constant MI_DNN_prms_path: string := "./tb_files/DNN/multiple_images/";
	constant MI_act_fun_type: string  := """+act_fun_type+""";
   --TestBench for neuron entities and its subentities
   -- Layers variables
   -- Input Layer
   constant MI_num_hidden_layers: natural :="""+str(num_hidden_layers)+""";


end package;


package body I_DNN_MI_package is 


end package body I_DNN_MI_package;
        """)
        
    finally:
        sys.stdout = sys.__stdout__
        f.close()
    

def mkentity(DNN_in_prms, net):
    
    VHDL_architectures_path = DNN_in_prms["architecturepath"]
    date = DNN_in_prms["date"]
    num_hidden_layers = DNN_in_prms["num_hidden_layers"]
    
    try:
        f = open(VHDL_architectures_path+"/I_DNN.vhd",'w')
        #VHDL File Descriptor
        f.write(
        "----------------------------------------------------------------------------------\n"
        "-- Company: \n"
        "-- Engineer: Michele Pio Fragasso\n"
        "-- \n"
        "-- Create Date: "+str(date)+" \n"
        "-- Design Name: \n"
        "-- Module Name: DNN - Behavioral\n"
        "-- Project Name: \n"
        "-- Target Devices: \n"
        "-- Tool Versions: \n"
        "-- Description: \n"
        "-- \n"
        "\n"
        "-- \n"
        "-- Dependencies: \n"
        "-- \n"
        "-- Revision:\n"
        "-- Revision 0.01 - File Created\n"
        "-- Additional Comments:\n"
        "-- It would be nice if it is possible to implement a way to evaluate\n"
        "-- if it is more convenient to save the output or keep on computing the layer output\n"
        "-- For example if the number of clock cycles required to save the output equals the ones required\n"
        "-- to compute the output of the DNN. \n"
        "----------------------------------------------------------------------------------\n"
        "\n"
        "\n"
        #Libraries
        "library ieee;\n"
        "use ieee.std_logic_1164.all;\n"
        "use ieee.numeric_std.all;\n"
        "use ieee.math_real.all;\n"
        "\n"
        "library ieee_proposed;\n"
        "use ieee_proposed.fixed_pkg.all;\n"
        "\n"
        "library work;\n"
        "use work.I_DNN_package.all;\n"
        "use work.COMMON_PACKAGE.all;\n"
        "use work.TEST_ARCHITECTURE_PACKAGE.all;\n"
        "use work.NVME_FRAMEWORK_PACKAGE.all;\n"
        "use work.INTERMITTENCY_EMULATOR_package.all;\n"
        "\n"
        #Entity declaration
        "entity I_DNN is\n"
        "generic(\n"
        "constant neuron_inout_IntWidth: natural;\n"
        "constant neuron_inout_FracWidth: natural;\n"
        "constant neuron_weight_IntWidth: natural;\n"
        "constant neuron_weight_FracWidth: natural;\n"
        "constant sigmoid_inputdataWidth: natural;\n"
        "constant sigmoid_inputdataIntWidth: natural;\n"
        "constant act_fun_type: string;\n"
        "constant DNN_prms_path: string \n"
        ");\n"
        "port(\n"
        "--ORIGINARY PINS\n"
        "data_in: in sfixed (neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);                      --data_in   : serial input to the DNN.\n"
        "start: in std_logic;                                                                --start     : signal to trigger the DNN\n"
        "clk: in std_logic;                                                                  --clk       : system clock\n"
        "data_out: out sfixed (neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);--data_out  : serial output from the DNN\n"
        "digit_out: out integer range 0 to 9;                   \n"
        "data_v: out std_logic;                                                              --data_v    : data validity bit. It aknowledges the availability of data from the DNN\n"  
        "addr_in: out std_logic_vector(0 to natural(ceil(log2(real(layer_inputs(1)))))-1);   --addr_in   : To scan through the valdation data set\n"
        "--AUGUMENTED PINS\n"
        "n_power_reset: in std_logic;                                                        --n_power_reset     : reset pin which emulates a power failure                       \n"                  
        "data_sampled: in std_logic;\n"
        "thresh_stats: in threshold_t                                                        --threshold_stats   : this contains the hazard signal to trigger the data save process\n"
        "); --To scan through the valdation data set\n"
        "end I_DNN;\n"
        #Begin Archictecture
        "\n"
        "architecture Behavioral of I_DNN is\n"
        #Declarative Part
        #Types
        "--TYPES-------------------------------------------------\n"
        "type data_vect_type is array(1 to num_hidden_layers) of sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);\n"
        "type out_v_set_vect_t is array(1 to num_hidden_layers) of integer range 0 to 3;\n"
        #Layer Signals
        "--LAYER SIGNALS-----------------------------------------\n"
        "signal out_v_set_vect: out_v_set_vect_t;\n"
        "signal data_out_vect, data_in_vect: data_vect_type;\n"
        "signal start_vect: std_logic_vector(1 to num_hidden_layers);\n"
        "signal data_in_sel_vect: std_logic_vector(0 to natural(ceil(log2(real(isum(layer_inputs)))))-1);\n"
        "signal data_out_sel_vect: std_logic_vector(0 to natural(ceil(log2(real(isum(layer_outputs)))))-1);\n"
        "signal data_v_vect: std_logic_vector(1 to num_hidden_layers):=(others=>'0');\n")
        for i in range(num_hidden_layers):
            index = str(i+1)
            block = []
            block.append("signal data_in_sel"+str(i+1)+": std_logic_vector(0 to  natural(ceil(log2(real(layer_inputs("+str(i+1)+")))))-1);\n")
            block.append("signal data_out_sel"+str(i+1)+": std_logic_vector(0 to  natural(ceil(log2(real(layer_outputs("+str(i+1)+")))))-1);\n")
            f.write("\n".join(block))
        f.write(
        #Softmax Signals
        "--SOFTMAX\n"
        "signal softmax_data_v: std_logic;\n"
        "signal softmax_state: softmax_state_t:=power_off;\n"
        #Intermittency Emulator Signals
        "--INTERMITTENCY EMULATOR---------------------------------\n"
        "signal resetN_emulator: std_logic;\n"
        #FSM Non-Volatile Register Signals
        "--FSM_NV_REG SIGNALS-------------------------------------\n"
        "signal threshold_value      : intermittency_arr_int_type(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0);\n"
        "signal threshold_compared   : std_logic_vector(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0); \n"
        "signal select_threshold     : integer range 0 to INTERMITTENCY_NUM_THRESHOLDS -1; --This is used to select the threshold for power failure\n"
        "signal task_status          : std_logic;\n"
        "signal fsm_nv_reg_state, fsm_state_sig: fsm_nv_reg_state_t:=shutdown_s;\n"
        #Non-Volatile Registers Signals
        "--NV_REG_SIGNALS\n")
        for i in range(num_hidden_layers):
            index = str(i+1)
            block = []
            block.append("--NV_REG1")
            block.append("signal nv_reg_busy"+index+":std_logic:='0';")
            block.append("signal nv_reg_busy_sig"+index+": std_logic:='0';")
            block.append("signal nv_reg_dout"+index+": std_logic_vector(nv_reg_width-1 DOWNTO 0):=(others=>'0');")
            block.append("signal previous_layer"+index+":std_logic_vector(nv_reg_width-1 downto 0):=(others=>'0');")
            block.append("signal task_status"+index+":std_logic;")
            block.append("signal nv_reg_en"+index+":std_logic;")
            block.append("signal nv_reg_we"+index+":std_logic;")
            block.append("signal nv_reg_addr"+index+":std_logic_vector(nv_reg_addr_width_bit-1 downto 0);")
            block.append("signal nv_reg_din"+index+":std_logic_vector(nv_reg_width-1 downto 0);\n")
            f.write("\n".join(block))#Concatenating string adding new line in between
        #Power Approximation Signals
        f.write(
        "---------------POWER APPROXIMATION (PA) UNITS SIGNALS------------------------\n"
        "constant num_pwr_states_layer: natural:=4;\n"
        "constant num_pwr_states_nvreg: natural:=3;\n"
        "constant num_pwr_states_softmax:natural:=2;\n")
        for i in range(num_hidden_layers):
            index = str(i+1)
            block = []
            block.append("--LAYER"+index+" PA")
            block.append("signal pr_state_layer"+index+": fsm_layer_state_t;")
            block.append("signal power_state_en_layer"+index+"\t\t\t\t: std_logic_vector(num_pwr_states_layer - 1 downto 0);                              -- array of power state that are enable")
            block.append("signal power_counter_val_layer"+index+"\t\t\t\t: power_approx_counter_type(num_pwr_states_layer - 1 downto 0) := (others => 0);    -- array of state counter values")
            block.append("signal power_counter_full_layer"+index+"\t\t: std_logic_vector(num_pwr_states_layer - 1 downto 0) := (others => '0');           -- array of terminal counters")
            block.append("signal power_counter_reset_layer"+index+"\t\t: std_logic_vector(num_pwr_states_layer - 1 downto 0):=(others => '0');             -- array to reset counters")
            block.append("--NVREG"+index+" PA")
            block.append("signal power_state_en_nvreg"+index+"          : std_logic_vector(num_pwr_states_nvreg - 1 downto 0);                              -- array of power state that are enable")
            block.append("signal power_counter_val_nvreg"+index+"       : power_approx_counter_type(num_pwr_states_nvreg - 1 downto 0) := (others => 0);    -- array of state counter values")
            block.append("signal power_counter_full_nvreg"+index+"      : std_logic_vector(num_pwr_states_nvreg - 1 downto 0) := (others => '0');           -- array of terminal counters ")
            block.append("signal power_counter_reset_nvreg"+index+"     : std_logic_vector(num_pwr_states_nvreg - 1 downto 0):=(others => '0');                              -- array to reset counters\n")
            f.write("\n".join(block))
        f.write("--SOFTMAX PA\n"
        "signal power_state_en_softmax          : std_logic_vector(num_pwr_states_softmax - 1 downto 0);                              -- array of power state that are enable\n"
        "signal power_counter_val_softmax       : power_approx_counter_type(num_pwr_states_softmax - 1 downto 0) := (others => 0);    -- array of state counter values\n"
        "signal power_counter_full_softmax      : std_logic_vector(num_pwr_states_softmax - 1 downto 0) := (others => '0');           -- array of terminal counters\n"
        "signal power_counter_reset_softmax     : std_logic_vector(num_pwr_states_softmax - 1 downto 0):=(others => '0');                              -- array to reset counters\n"
        #Instant Power Calculator Signals
        "--INST_PWR_CALC\n")
        for i in range(num_hidden_layers):
            block = []
            index = str(i+1)
            block.append("--LAYER"+index+" INST_PWR_CALC")
            block.append("signal start_evaluation_layer"+index+"          : std_logic:='1';")
            block.append("signal evaluation_ready_layer"+index+"          : std_logic;")
            block.append("signal num_state_to_evaluate_layer"+index+"     : integer range 0 to num_pwr_states_layer-1:=0;")
            block.append("signal input_counter_val_layer"+index+"         : power_approx_counter_type(num_pwr_states_layer -1 downto 0);")
            block.append("signal output_data_layer"+index+"               : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0);")
            block.append("--NV_REG"+index+"INST_PWR_CALC")
            block.append("signal start_evaluation_nvreg"+index+"          : std_logic:='1';")
            block.append("signal evaluation_ready_nvreg"+index+"          : std_logic;")
            block.append("signal num_state_to_evaluate_nvreg"+index+"     : integer range 0 to num_pwr_states_nvreg-1:=0;")
            block.append("signal input_counter_val_nvreg"+index+"         : power_approx_counter_type(num_pwr_states_nvreg -1 downto 0);")
            block.append("signal output_data_nvreg"+index+"               : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0);\n")
            f.write("\n".join(block))
        f.write(
        "--SOFTMAX\n"
        "signal start_evaluation_softmax          : std_logic:='1';\n"
        "signal evaluation_ready_softmax          : std_logic;\n"
        "signal num_state_to_evaluate_softmax     : integer range 0 to num_pwr_states_softmax-1:=0;\n"
        "signal input_counter_val_softmax         : power_approx_counter_type(num_pwr_states_softmax -1 downto 0);\n"
        "signal output_data_softmax               : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0);\n"
        "--\n"
        "--COMPONENTS DECLARATION---------------------------------------------------\n"
        "--LAYER\n"
        "component I_layer is\n"
        "    generic(\n"
        "constant num_inputs: natural;\n"
        "constant num_outputs: natural;\n"
        "constant neuron_inout_IntWidth: natural;\n"
    	"constant neuron_inout_FracWidth: natural;\n"
    	"constant neuron_weight_IntWidth: natural;\n"
    	"constant neuron_weight_FracWidth: natural;\n"
        "constant layer_no: natural;--Layer number (identifier)\n"
        "constant act_fun_type: string; -- Choose between \"ReLU\",\"Sig\"\n"
        "constant sigmoid_inputdataWidth: natural;\n"
    	"constant sigmoid_inputdataIntWidth: natural;\n"
    	"constant lyr_prms_path: string\n"
        ");\n"
        "port(\n"
        "    ---ORIGINARY PINS----\n"
        "    ------Inputs---------\n"
        "    clk: in std_logic;\n"                                                                  
        "    data_in: in sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);\n"                     
        "    data_out_sel: in std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1);\n"
        "    start: in std_logic;                                                                \n"
        "    -------Outputs-------\n"
        "    data_out: out sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);                 \n"
        "    data_in_sel: inout std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);  \n"
        "    data_v: out std_logic;                                                              \n"
        "    --ADDED PINS---------                                                               \n"                                                                                                         
        "    --------Inputs-------\n"
        "    n_power_reset: in std_logic;                                                        \n"
        "    fsm_nv_reg_state: in fsm_nv_reg_state_t;                                            \n"
        "    nv_reg_busy: in std_logic;                                                          \n"
        "    nv_reg_busy_sig: in  STD_LOGIC;                                                     \n"
        "    nv_reg_dout: in STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);                          \n"
        "    out_v_set: in integer range 0 to 3;                                                 \n"                                                                                         
        "    -------Outputs-------\n"
        "    task_status: out std_logic;                                                        \n"
        "    nv_reg_en: out std_logic;                                                       \n"
        "    nv_reg_we: out std_logic;                                                   \n"
        "    nv_reg_addr: out std_logic_vector(nv_reg_addr_width_bit-1 downto 0);    \n"
        "    nv_reg_din: out STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);\n"
        "    pr_state: out fsm_layer_state_t                           \n"
        "    );                                                     \n"
        "end component;\n"
        "--FSM_NV_REG_DB\n"
        "component fsm_nv_reg_db is\n"
        "    port ( \n"
        "        clk                     : in STD_LOGIC;\n"
        "        resetN                  : in STD_LOGIC;\n"
        "        thresh_stats            : in threshold_t;\n"
        "        task_status             : in STD_LOGIC;\n"
        "        fsm_state               : out fsm_nv_reg_state_t;\n"
        "        fsm_state_sig           : out fsm_nv_reg_state_t \n"
        "        );\n"
        "end component;\n"
        "--NV_REG\n"
        "component nv_reg is\n"
        "    Generic(\n"
        "        MAX_DELAY_NS: INTEGER;\n"
        "        NV_REG_WIDTH: INTEGER;\n"
        "        NV_REG_DEPTH: INTEGER\n"
        "    );\n"
        "    Port ( \n"
        "        clk             : in STD_LOGIC;\n"
        "        resetN          : in STD_LOGIC;\n" 
        "        power_resetN 	: in STD_LOGIC;\n"
        "        -------------change from here--------------\n" 
        "        busy            : out STD_LOGIC;\n"
        "        busy_sig        : out STD_LOGIC;\n"
        "        en              : in STD_LOGIC;\n"
        "        we              : in STD_LOGIC;\n"
        "        addr            : in STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);\n"
        "        din             : in STD_LOGIC_VECTOR(31 DOWNTO 0);\n"
        "        dout            : out STD_LOGIC_VECTOR(31 DOWNTO 0)\n"
        "        -------------change to here---------------- \n"
        "    );\n"
        "end component;\n"
        "component SOFT_MAX is\n"
        "generic(\n"
        "num_inputs: natural := 10\n"
        ");\n"
        "port(\n"
        "--INPUTS\n"
        "clk: in std_logic;\n"
        "start: in std_logic;\n"
        "data_in: in sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);\n"
        "data_sampled: in std_logic;\n"
        "n_power_reset: in std_logic;\n"
        "--OUTPUTS\n"
        "data_in_sel: out std_logic_vector(natural(ceil(log2(real(num_inputs))))-1 downto 0);\n"
        "out_v: out std_logic;\n"
        "data_out: out sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);\n"
        "digit_out: out integer range 0 to 9;\n"
        "softmax_state: out softmax_state_t\n"
        ");\n"
        "end component;\n"
        "component power_approximation is\n"
        "    generic(\n"
        "        pwr_states_num          :natural\n"
        "        );\n"
        "    port(\n"
        "        sys_clk                 : in std_logic; -- system clock\n"
        "        power_state_en          : in std_logic_vector(pwr_states_num - 1 downto 0); -- array of power state that are enable\n"
        "        power_counter_val       : out power_approx_counter_type(pwr_states_num - 1 downto 0) := (others => 0); -- array of state counter values\n"
        "        power_counter_full      : out std_logic_vector(pwr_states_num - 1 downto 0) := (others => '0'); -- array of terminal counters \n"
        "        power_counter_reset     : in std_logic_vector(pwr_states_num - 1 downto 0) -- array to reset counters\n"
        "    );\n"
        "end component;\n"
        "component instant_pwr_calc is\n"
        "    generic(\n"
        "        pwr_states_num              :natural;\n"
        "        type_device                 :string\n"
        "    );\n"
        "    port (\n"
        "        sys_clk                 : in std_logic; -- system clock\n"
        "        start_evaluation        : in std_logic; -- start evaluation signal \n"
        "        evaluation_ready        : out std_logic; -- evaluation ready singal \n"
        "        num_state_to_evaluate   : in integer range 0 to pwr_states_num-1; -- number of state to evaluate\n"
        "        input_counter_val       : in power_approx_counter_type(pwr_states_num -1 downto 0); -- array of each state counter\n"
        "        output_data             : out std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0) -- output data\n"
        "    );\n"
        "end component;\n"
        "\n"
        "begin\n"
        "\n"
        "--Data Path\n"
        "--Data\n"
        "data_in_vect(1) <= data_in;\n");
        block = []
        for i in range(1, num_hidden_layers):
            index = str(i+1)
            pr_index = str(i)
            block.append("data_in_vect("+index+") <= data_out_vect("+pr_index+");")
        f.write("\n".join(block)+"\n")
        f.write("--Aknowledges Bits\n"
        "start_vect(1) <= start;\n")
        block = []
        for i in range(1, num_hidden_layers):
            index = str(i+1)
            pr_index = str(i)
            block.append("start_vect("+str(i+1)+") <= data_v_vect("+str(i)+");")
        f.write("\n".join(block)+"\n")
        f.write(
        "--Data Selectors\n"
        "addr_in <= data_in_sel1;\n")
        block = []
        for i in range(1,num_hidden_layers):
            index = str(i+1)
            pr_index = str(i)
            block.append("data_out_sel"+pr_index+"<= data_in_sel"+index+";")
        f.write("\n".join(block)+"\n")
        f.write(
        "data_v <= softmax_data_v;\n"
        "--Reset bit\n"
        "resetN_emulator <= n_power_reset;\n"
        "--TASK STATUS bit\n")
        line = []
        line.append("task_status <= task_status1")
        for i in range(1,num_hidden_layers):
            index = str(i+1)
            line.append(" or task_status"+index)
        f.write("".join(line)+";\n")
        f.write(
        "--out_v_set PROCESS\n"
        "--Description: This process computes the out_v_set bit feeding the layer, in order to invalidate the output of that layer.\n"
        "out_v_set_val: process(all) is\n"
        "begin\n")
        for i in range(num_hidden_layers-1):
            index = str(i+1)
            nx_index = str(i+2)
            block = []
            block.append("--Layer"+index)
            block.append("if data_v_vect("+nx_index+") = '0' then")
            block.append("    out_v_set_vect("+index+") <= 2;")
            block.append("elsif data_v_vect("+nx_index+") = '1' then")
            block.append("    out_v_set_vect("+index+") <= 1;")
            block.append("end if;")
            f.write("\n".join(block)+"\n")
        index = str(i+1)
        nx_index = str(i+2)
        block = []
        block.append("--Layer"+index)
        block.append("if softmax_data_v = '0' then")
        block.append("    out_v_set_vect("+nx_index+") <= 2;")
        block.append("elsif softmax_data_v = '1' then")
        block.append("    out_v_set_vect("+nx_index+") <= 1;")
        block.append("end if;")
        f.write("\n".join(block)+"\n")
        f.write(
        "--out_v_set_vect(3) <= out_v_set;\n"
        "end process out_v_set_val;\n"
        "--COMPONENT INSTANTIATION\n"
        "--FMS_NV_REG_DB_COMP\n"
        "fsm_nv_reg_db_comp: fsm_nv_reg_db\n"
        "    port map(\n"
        "        clk             => clk,\n"
        "        resetN          => resetN_emulator,\n"
        "        thresh_stats    => thresh_stats,\n"
        "        task_status     => task_status,\n"
        "        fsm_state       => fsm_nv_reg_state,\n"
        "        fsm_state_sig   => fsm_state_sig\n"
        "    );\n")
        #NV_REG_COMP
        for i in range(num_hidden_layers):
            block = []
            index = str(i+1)
            block.append("--LAYER"+index)
            block.append("--NVREG")
            block.append("nv_reg_comp"+index+": nv_reg")
            block.append("    Generic map(")
            block.append("        MAX_DELAY_NS => FRAM_MAX_DELAY_NS,")
            block.append("        NV_REG_WIDTH => NV_REG_WIDTH,")
            block.append("        NV_REG_DEPTH => NV_REG_DEPTH")             
            block.append("    )")
            block.append("    Port map(") 
            block.append("        clk             => clk,")
            block.append("        resetN          => '1',")
            block.append("        power_resetN 	=> resetN_emulator,")
            block.append("        -------------chage from here--------------") 
            block.append("        busy            => nv_reg_busy"+index+",")
            block.append("        busy_sig        => nv_reg_busy_sig"+index+",")
            block.append("        en              => nv_reg_en"+index+",")
            block.append("        we              => nv_reg_we"+index+",")
            block.append("        addr            => nv_reg_addr"+index+",")
            block.append("        din             => nv_reg_din"+index+",")
            block.append("        dout            => nv_reg_dout"+index)
            block.append("        -------------chage to here----------------")
            block.append("        );")
            block.append("--LAYER")
            block.append("I_layer"+index+": I_layer")
            block.append("    generic map(")
            block.append("    num_inputs => layer_inputs("+index+"),")
            block.append("    num_outputs => layer_outputs("+index+"),")
            block.append("neuron_inout_IntWidth => neuron_inout_IntWidth,")
            block.append("neuron_inout_FracWidth => neuron_inout_FracWidth,")
            block.append("neuron_weight_IntWidth => neuron_weight_IntWidth,")
            block.append("neuron_weight_FracWidth => neuron_weight_FracWidth,")
            block.append("    layer_no => "+index+",")
            block.append("    act_fun_type => \"ReLU\"," )
            block.append("sigmoid_inputdataWidth=> 5,")
            block.append("sigmoid_inputdataIntWidth=> 2,")
            block.append("lyr_prms_path => DNN_prms_path")
            block.append("    )")
            block.append("    port map(")
            block.append("    --ORIGINARY PINS")
            block.append("    --Input")
            block.append("    clk => clk,")                           
            block.append("    data_in => data_in_vect("+index+"),")                  
            block.append("    data_out_sel => data_out_sel"+index+",")  
            block.append("    start => start_vect("+index+"),")                               
            block.append("    --Output")                                              
            block.append("    data_out => data_out_vect("+index+"),")                 
            block.append("    data_in_sel => data_in_sel"+index+",")  
            block.append("    data_v => data_v_vect("+index+"),")                                                                                                                                                                                                                                                                                                               
            block.append("    --ADDED PINS")
            block.append("    --Inputs")                                                              
            block.append("    n_power_reset => n_power_reset,")
            block.append("    fsm_nv_reg_state => fsm_nv_reg_state,")
            block.append("    nv_reg_busy => nv_reg_busy"+index+",")
            block.append("    nv_reg_busy_sig => nv_reg_busy_sig"+index+",")
            block.append("    nv_reg_dout => nv_reg_dout"+index+",")
            block.append("    out_v_set => out_v_set_vect("+index+"),")
            block.append("    --Outputs")
            block.append("    task_status => task_status"+index+",")
            block.append("    nv_reg_en => nv_reg_en"+index+",")
            block.append("    nv_reg_we => nv_reg_we"+index+",")
            block.append("    nv_reg_addr => nv_reg_addr"+index+",")
            block.append("    nv_reg_din => nv_reg_din"+index+",")
            block.append("    pr_state => pr_state_layer"+index)
            block.append("")
            block.append("    );\n")
            f.write("\n".join(block))
        
        f.write(             
        "soft_max_comp: SOFT_MAX\n"
        "generic map(\n"
        "num_inputs => 10\n"
        ")\n"
        "port map(\n"
        "clk => clk,\n"
        "start => data_v_vect("+index+"),\n"
        "data_in => data_out_vect("+index+"),\n"
        "data_sampled => data_sampled,\n"
        "n_power_reset => n_power_reset,\n"
        "data_in_sel => data_out_sel"+index+",\n"
        "out_v => softmax_data_v,\n"
        "data_out => data_out,\n"
        "digit_out => digit_out,\n"
        "softmax_state => softmax_state\n"
        ");\n")
        #POWER_APPROXIMATION UNITS
        for i in range(num_hidden_layers):
            block = []
            index = str(i+1)
            block.append("pwr_appr_comp_layer"+index+": power_approximation")
            block.append("generic map(")
            block.append("    pwr_states_num => num_pwr_states_layer")
            block.append(")")
            block.append("port map(")
            block.append("        sys_clk                 => clk,")
            block.append("        power_state_en          => power_state_en_layer"+index+",")
            block.append("        power_counter_val       => power_counter_val_layer"+index+",")
            block.append("        power_counter_full      => power_counter_full_layer"+index+",")
            block.append("        power_counter_reset     => power_counter_reset_layer"+index)
            block.append(");")
            block.append("pwr_appr_comp_nvreg"+index+": power_approximation")
            block.append("generic map(")
            block.append("    pwr_states_num => num_pwr_states_nvreg")
            block.append(")")
            block.append("port map(")
            block.append("        sys_clk                 => clk,")
            block.append("        power_state_en          => power_state_en_nvreg"+index+",")
            block.append("        power_counter_val       => power_counter_val_nvreg"+index+",")
            block.append("        power_counter_full      => power_counter_full_nvreg"+index+",")
            block.append("        power_counter_reset     => power_counter_reset_nvreg"+index)
            block.append(");\n")
            f.write("\n".join(block))
        f.write(    
        "pwr_appr_comp_softmax: power_approximation\n"
        "generic map(\n"
        "    pwr_states_num => num_pwr_states_softmax\n"
        ")\n"
        "port map(\n"
        "        sys_clk                 => clk,\n"
        "        power_state_en          => power_state_en_softmax,\n"
        "        power_counter_val       => power_counter_val_softmax,\n"
        "        power_counter_full      => power_counter_full_softmax,\n"
        "        power_counter_reset     => power_counter_reset_softmax\n"
        ");\n")
        #Instant Power Calculations
        for i in range(num_hidden_layers):
            block = []
            index = str(i+1)
            block.append("input_counter_val_layer"+index+" <= power_counter_val_layer"+index+";")
            block.append("inst_pwr_calc_comp_layer"+index+": instant_pwr_calc")
            block.append("    generic map(")
            block.append("        pwr_states_num => num_pwr_states_layer,")
            block.append("        type_device => \"layer\"")
            block.append("    )")
            block.append("    port map(")
            block.append("        sys_clk                 => clk,")
            block.append("        start_evaluation        => start_evaluation_layer"+index+",")
            block.append("        evaluation_ready        => evaluation_ready_layer"+index+",")
            block.append("        num_state_to_evaluate   => num_state_to_evaluate_layer"+index+",")
            block.append("        input_counter_val       => input_counter_val_layer"+index+",")
            block.append("        output_data             => output_data_layer"+index)
            block.append("    );")
            block.append("input_counter_val_nvreg"+index+" <= power_counter_val_nvreg"+index+";")
            block.append("inst_pwr_calc_comp_nvreg"+index+": instant_pwr_calc")
            block.append("    generic map(")
            block.append("        pwr_states_num => num_pwr_states_nvreg,")
            block.append("        type_device => \"nvreg\"")
            block.append("    )")
            block.append("    port map(")
            block.append("        sys_clk                 => clk,")
            block.append("        start_evaluation        => start_evaluation_nvreg"+index+",")
            block.append("        evaluation_ready        => evaluation_ready_nvreg"+index+",")
            block.append("        num_state_to_evaluate   => num_state_to_evaluate_nvreg"+index+",")
            block.append("        input_counter_val       => input_counter_val_nvreg"+index+",")
            block.append("        output_data             => output_data_nvreg"+index)
            block.append("    );")
            f.write("\n".join(block))
        f.write(
        "input_counter_val_softmax <= power_counter_val_softmax;\n"
        "inst_pwr_calc_comp_softmax: instant_pwr_calc\n"
        "    generic map(\n"
        "        pwr_states_num => num_pwr_states_softmax,\n"
        "        type_device => \"softmax\"\n"
        "    )\n"
        "    port map(\n"
        "        sys_clk                 => clk,\n"
        "        start_evaluation        => start_evaluation_softmax,\n"
        "        evaluation_ready        => evaluation_ready_softmax,\n"
        "        num_state_to_evaluate   => num_state_to_evaluate_softmax,\n"
        "        input_counter_val       => input_counter_val_softmax,\n"
        "        output_data             => output_data_softmax\n"
        "    );    \n"
        "\n"
        "\n"
        "power_states_gen: process(all) is \n"
        "begin\n"
        "\n")
        for i in range(num_hidden_layers):
            index = str(i+1)
            block = []
            block.append("----------LAYER"+index+"------------")
            block.append("if pr_state_layer"+index+" = power_off then")
            block.append("    power_state_en_layer"+index+" <= (others => '0');")
            block.append("elsif pr_state_layer"+index+" = idle or pr_state_layer"+index+" = init or pr_state_layer"+index+" = data_save_init or pr_state_layer"+index+" = data_save_init_cmpl then")
            block.append("    power_state_en_layer"+index+" <= (others => '0');")
            block.append("    power_state_en_layer"+index+"(0) <= '1';")
            block.append("elsif pr_state_layer"+index+" = w_sum or pr_state_layer"+index+" = b_sum or pr_state_layer"+index+" = act_log or pr_state_layer"+index+" = finished then")
            block.append("    power_state_en_layer"+index+" <= (others => '0');")
            block.append("    power_state_en_layer"+index+"(1) <= '1';")
            block.append("elsif pr_state_layer"+index+" = data_save then")
            block.append("    power_state_en_layer"+index+" <= (others => '0');")
            block.append("    power_state_en_layer"+index+"(2) <= '1';")
            block.append("elsif pr_state_layer"+index+" = recovery then")
            block.append("    power_state_en_layer"+index+" <= (others => '0');")
            block.append("    power_state_en_layer"+index+"(3) <= '1';")
            block.append("end if;")
            block.append("--NVREG"+index)
            block.append("if pr_state_layer"+index+" = power_off then")
            block.append("    power_state_en_nvreg"+index+" <= (others => '0');")
            block.append("elsif nv_reg_en"+index+" = '0' then")
            block.append("    power_state_en_nvreg"+index+"(0) <= '1';")
            block.append("    power_state_en_nvreg"+index+"(1) <= '0';")
            block.append("    power_state_en_nvreg"+index+"(2) <= '0';")
            block.append("else")
            block.append("    power_state_en_nvreg"+index+"(0) <= '1';")
            block.append("    power_state_en_nvreg"+index+"(1) <= '1';")
            block.append("    if nv_reg_we"+index+" = '1' then")
            block.append("        power_state_en_nvreg"+index+"(2) <= '1';")
            block.append("    else")
            block.append("        power_state_en_nvreg"+index+"(2) <= '0';")
            block.append("    end if;")
            block.append("end if;\n")
            f.write("\n".join(block))
        f.write(
        "--SOFTMAX\n"
        "if softmax_state = power_off then\n"
        "    power_state_en_softmax <= (others => '0');\n"
        "elsif softmax_state = idle then\n"
        "    power_state_en_softmax <= (others => '0');\n"
        "    power_state_en_softmax(0) <= '1';\n"
        "elsif softmax_state = active or softmax_state = finished then\n"
        "    power_state_en_softmax <= (others => '0');\n"
        "    power_state_en_softmax(1) <= '1';\n"
        "end if;\n"
        "\n"
        "\n"
        "end process;\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "evaluation_gen_process: process(evaluation_ready_layer1,start_evaluation_layer1) is\n"
        "\n"
        "begin\n")
        for i in range(num_hidden_layers):
            block = []
            index = str(i+1)
            block.append("if rising_edge(evaluation_ready_layer"+index+") then")
            block.append("    start_evaluation_layer"+index+" <= '0' after 20 ns;")
            block.append("    num_state_to_evaluate_layer"+index+" <= num_state_to_evaluate_layer"+index+" +1;")
            block.append("    if num_state_to_evaluate_layer"+index+" = num_pwr_states_layer-1 then")
            block.append("        num_state_to_evaluate_layer"+index+" <= 0;")
            block.append("    end if;")
            block.append("end if;")
            block.append("if rising_edge(evaluation_ready_nvreg"+index+")  then")
            block.append("    start_evaluation_nvreg"+index+" <= '0' after 20 ns;")
            block.append("    num_state_to_evaluate_nvreg"+index+" <= num_state_to_evaluate_nvreg"+index+" +1;")
            block.append("    if num_state_to_evaluate_nvreg"+index+" = num_pwr_states_nvreg-1 then")
            block.append("        num_state_to_evaluate_nvreg"+index+" <= 0;")
            block.append("    end if;")
            block.append("end if;")
            f.write("\n".join(block)+"\n")
        block = []
        block.append("if start_evaluation_layer1 = '0' then")
        for i in range(num_hidden_layers):
            index = str(i+1)
            block.append("start_evaluation_layer"+index+" <= '1' after 320 ns;")
            block.append("start_evaluation_nvreg"+index+" <= '1' after 320 ns;")
        block.append("start_evaluation_softmax <= '1' after 320 ns;")
        block.append("end if;")
        f.write("\n".join(block)+"\n")
        
        f.write(
        "if rising_edge(evaluation_ready_softmax) then\n"
        "    start_evaluation_softmax <= '0' after 20 ns;\n"
        "    num_state_to_evaluate_softmax <= num_state_to_evaluate_softmax +1;\n"
        "    if num_state_to_evaluate_softmax = num_pwr_states_softmax-1 then\n"
        "        num_state_to_evaluate_softmax <= 0;\n"
        "    end if;\n"
        "end if;\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "end process;\n"
        "\n"
        "\n"
        "\n"
        "end Behavioral;\n")
    finally:
        f.close()

def mkdatasets(DNN_in_prms, net,outputpath):
    
    image_indexes = [6542, 910, 1000, 1160, 1549, 6542, 1570, 1290]
    test_data = DNN_in_prms["datasets"][2]
    te_data = [[],[]]
    [(te_data[0].append(image),te_data[1].append(digit)) for (image,digit) in test_data]
    
    
    
    [genData.genTestData(dataWidth=net.neuroninputSize, IntSize=net.neuroninputIntSize, testDataNum=dataset_index, te_d = te_data,outputpath=outputpath) for dataset_index in image_indexes] 

    
    
    
    
    return
    
    