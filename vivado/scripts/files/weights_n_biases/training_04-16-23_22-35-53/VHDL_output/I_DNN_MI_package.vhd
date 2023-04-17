
----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 04-16-23_22-35-53
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

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library work;
use work.I_DNN_package.all;


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
	constant MI_DNN_neuron_inout_IntWidth: natural  := 11;
	constant MI_DNN_neuron_inout_FracWidth: natural := MI_DNN_neuron_inout_Width-MI_DNN_neuron_inout_IntWidth;
	--Neuron weight sizes
	constant MI_DNN_neuron_weight_Width: natural := 32;
	constant MI_DNN_neuron_weight_IntWidth: natural := 4;
	constant MI_DNN_neuron_weight_FracWidth: natural := MI_DNN_neuron_weight_Width-MI_DNN_neuron_weight_IntWidth;
	constant MI_DNN_prms_path: string := "./tb_files/DNN/multiple_images/tb_training_04-16-23_22-35-53/";
	constant MI_act_fun_type: string  := "ReLU";
   --TestBench for neuron entities and its subentities
   -- Layers variables
   -- Input Layer
   constant MI_num_hidden_layers: natural :=4;

    type datain_type is array(0 to layer_inputs(1)-1) of sfixed(MI_DNN_neuron_inout_IntWidth-1 downto -(MI_DNN_neuron_inout_FracWidth));
    type set_images_type is array(0 to 7) of datain_type;
    type set_digits_type is array(0 to 7) of integer range 0 to 9;
    type filenames_type is array(0 to 7) of string(1 to 39);
    type digit_filenames_type is array(0 to 7) of string(1 to 45);
    type pathname_type is array(0 to 7) of string (1 to 101);
    type digit_pathname_type is array(0 to 7) of string (1 to 107); 
    
    constant datasets_path: string := "../tb_files/DNN/multiple_images/tb_training_04-16-23_22-35-53/"; --(1 to 27) := "./tb_files/DNN/tb5/dataset/";
    constant image_filenames: filenames_type := ("test_dataset_6542/VHDL_dataset_6542.txt", "test_dataset_0910/VHDL_dataset_0910.txt", "test_dataset_1000/VHDL_dataset_1000.txt","test_dataset_1160/VHDL_dataset_1160.txt","test_dataset_1549/VHDL_dataset_1549.txt","test_dataset_6542/VHDL_dataset_6542.txt","test_dataset_1570/VHDL_dataset_1570.txt","test_dataset_1290/VHDL_dataset_1290.txt");
    constant digit_filenames: digit_filenames_type := ("test_dataset_6542/dataset_6542_classdigit.txt", "test_dataset_0910/dataset_0910_classdigit.txt", "test_dataset_1000/dataset_1000_classdigit.txt","test_dataset_1160/dataset_1160_classdigit.txt","test_dataset_1549/dataset_1549_classdigit.txt","test_dataset_6542/dataset_6542_classdigit.txt","test_dataset_1570/dataset_1570_classdigit.txt","test_dataset_1290/dataset_1290_classdigit.txt");
    constant full_path_images: pathname_type := (datasets_path&image_filenames(0),datasets_path&image_filenames(1),datasets_path&image_filenames(2),datasets_path&image_filenames(3),datasets_path&image_filenames(4),datasets_path&image_filenames(5),datasets_path&image_filenames(6),datasets_path&image_filenames(7));
    constant full_path_digits: digit_pathname_type := (datasets_path&digit_filenames(0),datasets_path&digit_filenames(1),datasets_path&digit_filenames(2),datasets_path&digit_filenames(3),datasets_path&digit_filenames(4),datasets_path&digit_filenames(5),datasets_path&digit_filenames(6),datasets_path&digit_filenames(7));
    


end package;


package body I_DNN_MI_package is 


end package body I_DNN_MI_package;
        
