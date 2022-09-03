library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library ieee;
use ieee.std_logic_1164.all;
use ieee.math_real.all;


package I_DNN_package is
    -- Package Declarative Part
    --(It contains variables, types, procedures and function declaration)
    --TestBench for neuron entities and its subentities
    constant neuron_rom_depth : natural := 30;--Number of weights for the neuron to be tested (which corresponds to the the number of input connected to the neuron)
    constant neuron_rom_width : natural := 32;--Bits for fixed-point representation.
	constant neuron_rom_file : string := "../../../../../../scripts/weights_and_bias/w_b/w_2_10.mif";
	constant neuron_bias_file : string := "../../../../../../../scripts/weights_and_bias/w_b/b_2_10.mif";
	--Fixed Point Representation
	constant input_depth: natural := neuron_rom_depth;--Input sequence widths
	constant input_width: natural := 32;
	constant input_int_width: natural := 16;
	constant input_frac_width: natural := input_width-input_int_width;
	constant dataset_path: string := "../../../../../../scripts/datasets/testData/input_neuron2.mif";
	--Weights widths
	constant neuron_width_sfixed: natural := neuron_rom_width; --Bit number for fixed point representation.
	constant neuron_int_width: natural := 16;--number of Bits to represent the integer part (including the sign)
	constant neuron_frac_width: natural := neuron_rom_width - neuron_int_width; --Number of bits to reprent the fractional part.
	--Bias widhts
	constant neuron_width_sfixed_b: natural := neuron_rom_width; --Bit number for fixed point representation.
	constant neuron_int_width_b: natural := 1;--number of Bits to represent the integer part (including the sign)
	constant neuron_frac_width_b: natural := neuron_width_sfixed_b - neuron_int_width_b; --Number of bits to reprent the fractional part.
	--constant neuron_value_b: sfixed(neuron_int_width_b-1 downto -neuron_frac_width_b):=(15=>'1',14=>'1',13=>'1',12=>'0',11=>'1',10=>'1',9=>'1',8=>'1',7=>'0',6=>'0',5=>'0',4=>'1',3=>'1',2=>'1',1=>'1',0=>'1');
    -- Layers variables
    -- Input Layer
    constant num_layers: natural := 3;
    --DNN parameters
    type layer_neurons_type is array(1 to num_layers) of natural;
    constant layer_inputs: layer_neurons_type := (784,30,20);
    constant layer_outputs: layer_neurons_type := (30,20,10);
    constant log2_layer_inputs: layer_neurons_type := (natural(ceil(log2(real(784)))), natural(ceil(log2(real(30)))), natural(ceil(log2(real(10)))));
    constant log2_layer_outputs: layer_neurons_type := (natural(ceil(log2(real(30)))), natural(ceil(log2(real(20)))), natural(ceil(log2(real(10)))));
    constant data_int_width: natural := 16;
    constant data_frac_width: natural := 16;
    constant validation_dataset_path: string := "../../../../../../scripts/datasets/testData/test_data.txt";
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
