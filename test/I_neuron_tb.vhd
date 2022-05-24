----------------------------------------------------------------------------------
-- Company: University of Trento
-- Engineer: Michele Pio Fragasso   
-- 
-- Create Date: 05/15/2022 10:25:20 AM
-- Design Name: 
-- Module Name: I_neuron_tb - Behavioral
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


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.math_real.all;
use ieee.numeric_std.all;

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library work;
use work.I_DNN_package.all;



entity I_neuron_tb is
--  Port ( );
end I_neuron_tb;

architecture Behavioral of I_neuron_tb is

signal clk, mul_sel, sum_reg_rst,update_out,w_rec,o_rec, n_power_rst: std_logic;
signal data_in, data_out,data_out_rec: sfixed (input_int_width-1 downto -input_frac_width);
signal addr: std_logic_vector (0 to natural(ceil(log2(real(neuron_rom_depth))))-1);
signal weighted_sum_save, weighted_sum_rec: sfixed (input_int_width+neuron_int_width-1 downto -input_frac_width-neuron_frac_width);
--Register to store neuron weighted sum and output;
signal weighted_sum_backup: sfixed (input_int_width+neuron_int_width-1 downto -input_frac_width-neuron_frac_width);
signal neuron_output_backup: sfixed (input_int_width-1 downto -input_frac_width);


component I_neuron is
    generic(
    constant rom_width: natural;
    constant rom_depth: natural;
    constant weight_file: string;
    constant bias_file: string);
port(
    clk: in std_logic;
    data_in: in sfixed (input_int_width-1 downto -input_frac_width);
    addr: in std_logic_vector (0 to natural(ceil(log2(real(rom_depth))))-1);
    mul_sel: in std_logic;
    sum_reg_rst: in std_logic;
    update_out: in std_logic;
    data_out: out sfixed (input_int_width-1 downto -input_frac_width);
    --Augumented pins
    n_power_reset: in std_logic;
    w_rec: in std_logic;
    o_rec: in std_logic;
    data_out_rec: in sfixed (input_int_width-1 downto -input_frac_width);
    weighted_sum_save: out sfixed (input_int_width+neuron_int_width-1 downto -input_frac_width-neuron_frac_width);
    weighted_sum_rec: in sfixed (input_int_width+neuron_int_width-1 downto -input_frac_width-neuron_frac_width));
end component I_neuron;

begin

I_neuron_comp: I_neuron
generic map(
    rom_width => neuron_rom_width,
    rom_depth => neuron_rom_depth,
    weight_file => neuron_rom_file,
    bias_file => neuron_bias_file
    )
port map(
    clk => clk,
    data_in => data_in,
    addr => addr,
    mul_sel => mul_sel,
    sum_reg_rst => sum_reg_rst,
    update_out => update_out,
    data_out => data_out,
    --Augumented pins
    n_power_reset => n_power_rst,
    w_rec => w_rec,
    o_rec => o_rec,
    data_out_rec => data_out_rec,
    weighted_sum_save => weighted_sum_save,
    weighted_sum_rec => weighted_sum_rec);
    
test_neuron: process is
begin

clk <= '0';--0
mul_sel <= '0';
update_out <= '0';
sum_reg_rst <= '0';
w_rec <= '0';
o_rec <= '0';
n_power_rst <= '1';
data_in <= to_sfixed(0,data_in);
data_out_rec <= (others => '0');
weighted_sum_rec <=(others => '0');
addr <= (others => '0');
wait for 20 ns;
clk <= not(clk);--1
data_in <= to_sfixed(3.7,data_in);
wait for 20 ns;
clk <= not(clk);--0
wait for 20 ns;
addr <= std_logic_vector(unsigned(addr)+1);
data_in <= to_sfixed(10.7,data_in);
clk <= not(clk);--1
wait for 20 ns;
clk <= not(clk);--0
wait for 20 ns;
clk <= not(clk);--1
weighted_sum_backup <= weighted_sum_save;
wait for 20 ns;
n_power_rst <= '0';
wait for 20 ns;
n_power_rst <= '1';
wait for 10 ns;
weighted_sum_rec <= weighted_sum_backup;
wait for 10 ns;
w_rec <= '1';
clk <= not(clk);--0
wait for 20 ns;
clk <= not(clk);--1
addr <= std_logic_vector(unsigned(addr)+1);
data_in <= to_sfixed(10.7,data_in);
wait for 20 ns;
w_rec <= '0';
clk <= not(clk);--0
wait for 20 ns;
clk <= not(clk);--1
wait for 20 ns;
clk <= not(clk);--0
wait for 20 ns;
update_out <= '1';
clk <= not(clk);--1
wait for 20 ns;
update_out <= '0';
clk <= not(clk);--0
wait for 20 ns;
neuron_output_backup <= data_out;
n_power_rst <= '0';
wait for 20 ns;
n_power_rst <= '1';
clk <= not(clk);--1
wait for 20 ns;
clk <= not(clk); --0
data_out_rec <= neuron_output_backup;
o_rec <= '1';
wait for 20 ns;
clk <= not(clk); --1
wait for 20 ns;





end process test_neuron;


end Behavioral;
