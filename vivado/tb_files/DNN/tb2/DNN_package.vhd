----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso
-- 
-- Create Date: 01/04/23 11:51:46
-- Design Name: 
-- Module Name: DNN_tb - Behavioral
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
-- 
----------------------------------------------------------------------------------)


library ieee;
use ieee.std_logic_1164.all;
use ieee.math_real.all;
use ieee.fixed_pkg.all;
package DNN_package is
--DNN constants
constant DNN_num_inputs: natural := 784;
constant DNN_sigmoid_inputdata_Width: natural  := 5;
constant DNN_sigmoid_inputdata_IntWidth: natural := 2;
constant DNN_neuron_input_Width: natural := 32;
constant DNN_neuron_input_IntWidth: natural  := 16;
constant DNN_neuron_input_FracWidth: natural := DNN_neuron_input_Width-DNN_neuron_input_IntWidth;constant DNN_neuron_weight_Width : natural := 32;
constant DNN_neuron_weight_IntWidth: natural := 3;
constant DNN_neuron_weight_FracWidth: natural := DNN_neuron_weight_Width-DNN_neuron_weight_IntWidth;
constant DNN_prms_path: string := "../tb_files/DNN/tb2/";
constant act_fun_type: string  := "ReLU";
-- Layers variables
-- Input Layer
constant num_hidden_layers: natural := 3;
--DNN parameters
type layer_neurons_type is array(1 to num_hidden_layers) of natural;

constant log2_layer_inputs: layer_neurons_type := (natural(ceil(log2(real(784)))),natural(ceil(log2(real(30)))),natural(ceil(log2(real(20)))));
constant log2_layer_outputs: layer_neurons_type := (natural(ceil(log2(real(30)))),natural(ceil(log2(real(20)))),natural(ceil(log2(real(10)))));
constant layer_inputs: layer_neurons_type := (784,30,20);
constant layer_outputs: layer_neurons_type := (30,20,10);


--Functions Declaration
function isum(l_n: layer_neurons_type)return natural;
function low(vect_lengths: layer_neurons_type; index: natural) return natural;
function high(VectorBits: layer_neurons_type; index: natural) return natural; 
function get_subvector(vector: std_logic_vector; VectorBits: layer_neurons_type;index: natural) return std_logic_vector;



end package DNN_package;

package body DNN_package is
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
end package body DNN_package;
