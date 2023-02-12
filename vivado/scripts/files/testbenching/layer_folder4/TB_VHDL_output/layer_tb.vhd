----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso
-- 
-- Create Date: 01/09/23 23:01:52
-- Design Name: 
-- Module Name: layer_tb - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- This file has been generated with a python script. Rather than modifying it directly, you shall make changes from the python generating script.
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library ieee;
use ieee.STD_LOGIC_1164.ALL;
use ieee.math_real.all;
use ieee.numeric_std.all;
use ieee.fixed_pkg.all;

library std;
use std.textio.all;



library work;
use work.DNN_package.all;

entity layer_tb is
end layer_tb;

architecture Behavioral of layer_tb is

--TESTBENCH CONSTANTS
constant layer_tb_num_inputs: natural := 30;
constant layer_tb_num_neurons: natural := 20;
constant layer_tb_sigmoid_inputdata_Width: natural  := 5;
constant layer_tb_sigmoid_inputdata_IntWidth: natural := 3;
constant layer_tb_neuron_input_Width: natural := 32;
constant layer_tb_neuron_input_IntWidth: natural  := 16;
constant layer_tb_neuron_input_FracWidth: natural := layer_tb_neuron_input_Width-layer_tb_neuron_input_IntWidth;
constant layer_tb_neuron_weight_Width : natural := 32;
constant layer_tb_neuron_weight_IntWidth: natural := 2;
constant layer_tb_neuron_weight_FracWidth: natural := layer_tb_neuron_weight_Width-layer_tb_neuron_weight_IntWidth;

--Code to read input
type datain_type is array(0 to layer_tb_num_inputs-1) of sfixed(layer_tb_neuron_input_IntWidth-1 downto -layer_tb_neuron_input_FracWidth);

impure function makesfixed (bit_in: in bit_vector(neuron_rom_width-1 downto 0)) return sfixed is
    variable fixedpoint_s: sfixed(layer_tb_neuron_input_IntWidth-1 downto -layer_tb_neuron_input_FracWidth);
    --variable a: std_logic := 0;
    begin
    for i in fixedpoint_s'range loop
        fixedpoint_s(i) := To_StdULogic(bit_in(i+layer_tb_neuron_input_FracWidth));
    end loop;
    return fixedpoint_s;
end function;

impure function gen_datain(dataset_path: in string) return datain_type is

file text_header: text open read_mode is dataset_path;
variable text_line: line;
variable line_i: bit_vector(0 to neuron_rom_width-1);
variable dataset_content: datain_type;

    begin
    for i in dataset_content'range loop
        readline(text_header, text_line);
        read(text_line, line_i);
        dataset_content(i) := makesfixed(line_i);
    end loop;
    file_close(text_header);
    return dataset_content;
end function;


--Data Input
constant tb_path: string :="../tb_files/layer/tb2/";
constant layer_parameters_path: string := tb_path;
constant dataset_path: string := tb_path&"inputs/test_data.txt";


signal input_reg: datain_type := gen_datain(dataset_path);

signal clk: std_logic := '0';
signal data_in: sfixed (layer_tb_neuron_input_IntWidth-1 downto -layer_tb_neuron_input_FracWidth) := input_reg(0);
signal start: std_logic:='1';
signal data_out: sfixed (layer_tb_neuron_input_IntWidth-1 downto -layer_tb_neuron_input_FracWidth);
signal data_out_sel: std_logic_vector(0 to natural(ceil(log2(real(layer_tb_num_neurons))))-1) := (others => '0');--num_outputs=30
--signal data_in_sel: std_logic_vector(0 to natural(ceil(log2(real(30))))-1);--num_outputs=30
signal data_v: std_logic := '0';
signal in_sel: std_logic_vector(0 to natural(ceil(log2(real(layer_tb_num_inputs))))-1):=(others=>'0');--num_inputs=30
signal start_scan: std_logic := '0';


component layer is
generic(
    num_inputs: natural;
    num_outputs: natural;
	neuron_input_IntWidth: natural;
	neuron_input_FracWidth: natural;
	neuron_weight_IntWidth: natural;
	neuron_weight_FracWidth: natural;
    layer_no: natural;
    act_fun_type: string;
	sigmoid_inputdataWidth: natural;
	sigmoid_inputdataIntWidth: natural;
	lyr_prms_path: string); -- If the user choose an analytical activation function the number of sample have to be chosen
port (
    clk: in std_logic;
    data_in: in sfixed (neuron_input_IntWidth-1 downto -neuron_input_FracWidth);
    data_out_sel: in std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1):=(others => '0');--num_outputs=30
    start: in std_logic;
    data_out: out sfixed (neuron_input_IntWidth-1 downto -neuron_input_FracWidth);
    data_in_sel: out std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);--num_outputs=30
    data_v: out std_logic);
end component layer;
begin

layer_comp: layer
generic map(
num_inputs => layer_tb_num_inputs,
num_outputs => layer_tb_num_neurons,
neuron_input_IntWidth => layer_tb_neuron_input_IntWidth,
neuron_input_FracWidth => layer_tb_neuron_input_FracWidth,
neuron_weight_IntWidth => layer_tb_neuron_weight_IntWidth,
neuron_weight_FracWidth => layer_tb_neuron_weight_FracWidth,
layer_no => 1,
act_fun_type => "ReLU",
sigmoid_inputdataWidth => 5,
sigmoid_inputdataIntWidth => 2,
lyr_prms_path => layer_parameters_path
)
port map(
clk => clk,
data_in => data_in,
data_out_sel => data_out_sel,
start => start,
data_out => data_out,
data_in_sel => in_sel,
data_v => data_v);


clk_gen: process is
begin
wait for 20 ns;
clk <= not(clk);
end process clk_gen;


--data_gen: process is
--the assignment <= is a non-blocking assignment
--begin
--if rising_edge(clk) then
    --in_sel <= std_logic_vector(unsigned(in_sel) + 1);
    --if unsigned(in_sel) >= neuron_rom_depth then --After all the data is fed to the layer start is permanently set to 0. Leaving the layer in the idle state.
        --addr_TC <= '1';
        --start <= '0';
        --in_sel <= (others => '0');
    --else
        --input_valid <= '1';
        data_in <= input_reg(to_integer(unsigned(in_sel)));
    --end if;    
--end if;
--end process data_gen;

out_access: process(data_v) is

begin
if data_v='1' then
    data_out_sel <= std_logic_vector(to_unsigned(integer'(7),5));
end if;
end process out_access;

start_pr: process is
begin
wait for 60 ns;
start <= '0';
end process start_pr;





end Behavioral;
