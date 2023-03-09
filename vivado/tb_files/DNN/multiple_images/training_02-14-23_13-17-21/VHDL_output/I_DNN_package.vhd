----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso 
-- 
-- Create Date: 02-14-23_13-17-21
-- Design Name: 
-- Module Name: DNN - Behavioral 
-- Project Name: 
-- Target Devices: 
-- Tool Versions:
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision: 
-- Revision 0.01 - File Created 
-- Additional Comments: 
----------------------------------------------------------------------------------
library ieee_proposed;
use ieee_proposed.fixed_pkg.all;
library ieee;
use ieee.std_logic_1164.all;
use ieee.math_real.all;


   package I_DNN_package is
   -- Package Declarative Part
   --(It contains variables, types, procedures and function declaration)
    -- Package Declarative Part
	--DNN constants
	constant DNN_num_inputs: natural := 784;
	constant DNN_sigmoid_inputdata_Width: natural  := 5;
	constant DNN_sigmoid_inputdata_IntWidth: natural := 2;
	--Neuron input (and output) sizes
	constant DNN_neuron_inout_Width: natural := 32;
	constant DNN_neuron_inout_IntWidth: natural  := 5;
	constant DNN_neuron_inout_FracWidth: natural := DNN_neuron_inout_Width-DNN_neuron_inout_IntWidth;
	--Neuron weight sizes
	constant DNN_neuron_weight_Width: natural := 32;
	constant DNN_neuron_weight_IntWidth: natural := 1;
	constant DNN_neuron_weight_FracWidth: natural := DNN_neuron_weight_Width-DNN_neuron_weight_IntWidth;
   constant DNN_testbench_input_path: string :="./tb_files/DNN/single_image/tb_training_02-14-23_13-17-21/test_dataset_0910/VHDL_dataset_0910.txt";
   constant DNN_prms_path: string := "../tb_files/DNN/single_imagetb_training_02-14-23_13-17-21";
	constant act_fun_type: string  := "ReLU";
   --TestBench for neuron entities and its subentities
   -- Layers variables
   -- Input Layer
   constant num_hidden_layers: natural :=12;
   --DNN parameters
   type layer_neurons_type is array(1 to num_hidden_layers) of natural;
   constant log2_layer_inputs: layer_neurons_type := (natural(ceil(log2(real(784)))),natural(ceil(log2(real(100)))),natural(ceil(log2(real(40)))),natural(ceil(log2(real(40)))),natural(ceil(log2(real(35)))),natural(ceil(log2(real(35)))),natural(ceil(log2(real(30)))),natural(ceil(log2(real(30)))),natural(ceil(log2(real(25)))),natural(ceil(log2(real(20)))),natural(ceil(log2(real(15)))),natural(ceil(log2(real(15)))));
   constant log2_layer_outputs: layer_neurons_type := (natural(ceil(log2(real(100)))),natural(ceil(log2(real(40)))),natural(ceil(log2(real(40)))),natural(ceil(log2(real(35)))),natural(ceil(log2(real(35)))),natural(ceil(log2(real(30)))),natural(ceil(log2(real(30)))),natural(ceil(log2(real(25)))),natural(ceil(log2(real(20)))),natural(ceil(log2(real(15)))),natural(ceil(log2(real(15)))),natural(ceil(log2(real(10)))));
   constant layer_inputs: layer_neurons_type := (784,100,40,40,35,35,30,30,25,20,15,15);
   constant layer_outputs: layer_neurons_type := (100,40,40,35,35,30,30,25,20,15,15,10);
   constant bias_int_width: natural := 1;            



   --Functions Declaration
   function isum(l_n: layer_neurons_type)return natural;
   function low(vect_lengths: layer_neurons_type; index: natural) return natural;
   function high(VectorBits: layer_neurons_type; index: natural) return natural; 
   function get_subvector(vector: std_logic_vector; VectorBits: layer_neurons_type;index: natural) return std_logic_vector;






   end package I_DNN_package;

   package body I_DNN_package is

   --Package Body Section
function isum(l_n: layer_neurons_type) return natural is
        variable result: natural := 0;
            begin
            for i in l_n'range loop
                result := result + l_n(i);
        end loop;
            return result;
end function;             
    function low(vect_lengths : layer_neurons_type; index : NATURAL) return NATURAL is
        variable pos : NATURAL := 0;
            begin
            for i in vect_lengths'low to index - 1 loop
               pos := pos + vect_lengths(i);
          end loop; 
          return pos;
      end function;


function high(VectorBits : layer_neurons_type; index : NATURAL) return NATURAL is
     variable pos : NATURAL := 0;
     begin
        for i in VectorBits'low to index loop
           pos := pos + VectorBits(i);
        end loop;
        return pos - 1;
end function;

               function get_subvector(vector: std_logic_vector; VectorBits: layer_neurons_type; index : natural) return std_logic_vector is
     begin
     return vector(high(VectorBits, index) downto low(VectorBits, index));
end function;

end package body I_DNN_package;   
