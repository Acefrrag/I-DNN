----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso
-- 
-- Create Date: 04/18/2022 09:21:01 PM
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
-- 
----------------------------------------------------------------------------------


library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library work;
use work.DNN_package.all;


entity DNN is
port(
data_in: in sfixed (data_int_width-1 downto -data_frac_width);
start: in std_logic;
clk: in std_logic;
data_out: out sfixed (data_int_width-1 downto -data_frac_width);
addr_in: out std_logic_vector(0 to natural(ceil(log2(real(layer_inputs(1)))))-1); --To scan through the valdation data set
addr_out: out std_logic_vector(0 to natural(ceil(log2(real(layer_outputs(3)))))-1)); --To scan through the valdation data set

end DNN;

architecture Behavioral of DNN is
type data_vect_type is array(1 to num_layers) of sfixed(data_int_width-1 downto -data_frac_width);

signal data_out_vect, data_in_vect: data_vect_type;
signal start_vect: std_logic_vector(0 to num_layers);
signal data_in_sel_vect: std_logic_vector(0 to natural(ceil(log2(real(isum(layer_inputs)))))-1);
signal data_out_sel_vect: std_logic_vector(0 to natural(ceil(log2(real(isum(layer_outputs)))))-1);
signal data_v_vect: std_logic_vector(1 to num_layers);
signal data_in_sel1: std_logic_vector(0 to  natural(ceil(log2(real(layer_inputs(1)))))-1);
signal data_out_sel1: std_logic_vector(0 to  natural(ceil(log2(real(layer_outputs(1)))))-1);
signal data_in_sel2: std_logic_vector(0 to  natural(ceil(log2(real(layer_inputs(2)))))-1);
signal data_out_sel2: std_logic_vector(0 to  natural(ceil(log2(real(layer_outputs(2)))))-1);
signal data_in_sel3: std_logic_vector(0 to  natural(ceil(log2(real(layer_inputs(3)))))-1);
signal data_out_sel3: std_logic_vector(0 to  natural(ceil(log2(real(layer_outputs(3)))))-1);



component layer is
    generic(
    constant num_inputs: natural;
    constant num_outputs: natural;
    constant layer_no: natural;--Layer number (identifier)
    constant act_type: string; -- Choose between "ReLU","Sig"
    constant act_fun_size: natural -- If the user choose an analytical activation function the number of sample have to be chosen
    );
port(
    clk: in std_logic;
    data_in: in sfixed(input_int_width-1 downto -input_frac_width);
    data_out_sel: in std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1);
    start: in std_logic;--to increment the counter while the output of the output is begin computed
    data_out: out sfixed(neuron_int_width-1 downto -neuron_frac_width);--The next layer controls which neuron's output to access
    data_in_sel: out std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);
    data_v: out std_logic);
end component;

begin

--Data Path
--Data
data_in_vect(1) <= data_in;
data_in_vect(2) <= data_out_vect(1);
data_in_vect(3) <= data_out_vect(2);
data_out <= data_out_vect(3);
--Aknowledges
start_vect(1) <= start;
start_vect(2) <= data_v_vect(1);
start_vect(3) <= data_v_vect(2);
--Data Selectors
addr_in <= data_in_sel1;
addr_in <= data_in_sel1;
data_out_sel1 <= data_in_sel2;
data_out_sel2 <= data_in_sel3;
data_out_sel3 <= addr_out;


layer1: layer
    generic map(
    num_inputs => layer_inputs(1),
    num_outputs => layer_outputs(1),
    layer_no => 1,
    act_type => "ReLU",
    act_fun_size => 0
    )
    port map(
    clk => clk,
    data_in => data_in_vect(1),
    data_out_sel => data_out_sel1,
    start => start_vect(1),
    data_out => data_out_vect(1),
    data_in_sel => data_in_sel1,
    data_v => data_v_vect(1)
    );
    
 layer2: layer
    generic map(
    num_inputs => layer_inputs(2),
    num_outputs => layer_outputs(2),
    layer_no => 2,
    act_type => "ReLU",
    act_fun_size => 0
    )
    port map(
    clk => clk,
    data_in => data_in_vect(2),
    data_out_sel => data_out_sel2,
    start => start_vect(2),
    data_out => data_out_vect(2),
    data_in_sel => data_in_sel2,
    data_v => data_v_vect(2)
    );
    
layer3: layer
    generic map(
    num_inputs => layer_inputs(3),
    num_outputs => layer_outputs(3),
    layer_no => 3,
    act_type => "ReLU",
    act_fun_size => 0
    )
    port map(
    clk => clk,
    data_in => data_in_vect(3),
    data_out_sel => data_out_sel3,
    start => start_vect(3),
    data_out => data_out_vect(3),
    data_in_sel => data_in_sel3,
    data_v => data_v_vect(3)
    );



--layers: for i in 1 to num_layers generate
--    component layer is
--    generic(
--    constant num_inputs: natural;
--    constant num_outputs: natural;
--    constant layer_no: natural;--Layer number (identifier)
--    constant act_type: string; -- Choose between "ReLU","Sig"
--    constant act_fun_size: natural -- If the user choose an analytical activation function the number of sample have to be chosen
--    );
--port(
--    clk: in std_logic;
--    data_in: in sfixed(input_int_width-1 downto -input_frac_width);
--    data_out_sel: in std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1);
--    start: in std_logic;--to increment the counter while the output of the output is begin computed
--    data_out: out sfixed(neuron_int_width-1 downto -neuron_frac_width);--The next layer controls which neuron's output to access
--    data_in_sel: out std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1);
--    data_v: out std_logic);
            
--    end component;
--begin

--    layer_i: layer
--    generic map(
--    num_inputs => layer_inputs(i),
--    num_outputs => layer_outputs(i+1),
--    layer_no => i,
--    act_type => "ReLU",
--    act_fun_size => 0
--    )
--    port map(
--    clk => clk,
--    data_in => data_in_vect(i),
--    data_out_sel => get_subvector(data_out_sel_vect, log2_layer_outputs, i),
--    start => start_vect(i),
--    data_out => data_out_vect(i),
--    data_in_sel => get_subvector(data_in_sel_vect, log2_layer_inputs, i),
--    data_v => data_v_vect(i)
--    );
--end generate;


end Behavioral;
