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
	constant MI_DNN_num_inputs: natural := 784;
	constant MI_DNN_sigmoid_inputdata_Width: natural  := 5;
	constant MI_DNN_sigmoid_inputdata_IntWidth: natural := 2;
	--Neuron input (and output) sizes
	constant MI_DNN_neuron_inout_Width: natural := 32;
	constant MI_DNN_neuron_inout_IntWidth: natural  := 13;
	constant MI_DNN_neuron_inout_FracWidth: natural := MI_DNN_neuron_inout_Width-MI_DNN_neuron_inout_IntWidth;
	--Neuron weight sizes
	constant MI_DNN_neuron_weight_Width: natural := 32;
	constant MI_DNN_neuron_weight_IntWidth: natural := 4;
	constant MI_DNN_neuron_weight_FracWidth: natural := MI_DNN_neuron_weight_Width-MI_DNN_neuron_weight_IntWidth;
	constant MI_DNN_prms_path: string := "./tb_files/DNN/multiple_images/";
	constant MI_act_fun_type: string  := "ReLU";
   --TestBench for neuron entities and its subentities
   -- Layers variables
   -- Input Layer
   constant MI_num_hidden_layers: natural :=4;


end package;


package body I_DNN_MI_package is 


end package body I_DNN_MI_package;
