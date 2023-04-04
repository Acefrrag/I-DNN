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

signal clk, mul_sel, sum_reg_rst,update_out,w_rec,o_rec, n_power_rst: std_logic:= '0';
signal data_in, data_out,data_out_rec: sfixed (input_int_width-1 downto -input_frac_width);
signal addr: std_logic_vector (0 to natural(ceil(log2(real(neuron_rom_depth))))-1);
signal weighted_sum_save, weighted_sum_rec: sfixed (input_int_width+neuron_int_width-1 downto -input_frac_width-neuron_frac_width);
--Register to store neuron weighted sum and output;
signal weighted_sum_backup: sfixed (input_int_width+neuron_int_width-1 downto -input_frac_width-neuron_frac_width);
signal neuron_output_backup: sfixed (input_int_width-1 downto -input_frac_width);
signal state_rec: std_logic_vector(input_int_width+neuron_int_width-1 downto 0);
signal en: std_logic;
signal wsum_save: std_logic_vector(input_int_width+neuron_int_width downto 0);
signal ReLU_save: std_logic_vector(input_int_width+input_frac_width downto 0);


component I_neuron is
    generic(
    constant rom_width: natural;
    constant rom_depth: natural;
    constant weight_file: string;
    constant bias_file: string);
port(
    --ORIGINARY PINS
    --INPUT
    clk: in std_logic;
    data_in: in sfixed (input_int_width-1 downto -input_frac_width);
    addr: in std_logic_vector (0 to natural(ceil(log2(real(rom_depth))))-1);
    mul_sel: in std_logic;
    sum_reg_rst: in std_logic;
    update_out: in std_logic;
    --OUTPUT
    data_out: out sfixed (input_int_width-1 downto -input_frac_width);
    --ADDED PINS
    --INPUT
    n_power_reset: in std_logic;
    en: in std_logic;
    s_rec: in std_logic;
    o_rec: in std_logic;
    data_out_rec: in sfixed (input_int_width-1 downto -input_frac_width);
    state_rec: in std_logic_vector(input_int_width+neuron_int_width-1 downto 0);
    --OUTPUT
    wsum_save: out std_logic_vector(input_int_width+neuron_int_width-1 downto 0);
    ReLU_save: out std_logic_vector(input_int_width+input_frac_width-1 downto 0)
    );
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
    --ORIGINARY PINS
    --INPUT
    clk => clk,
    data_in => data_in,
    addr => addr,
    mul_sel => mul_sel,
    sum_reg_rst => sum_reg_rst,
    update_out => update_out,
    --OUTPUT
    data_out => data_out,
    --ADDED PINS
    --INPUT
    n_power_reset => n_power_rst,
    en => en,
    s_rec => w_rec,
    o_rec => o_rec,
    data_out_rec => data_out_rec,
    state_rec => state_rec,
    --OUTPUT
    wsum_save => wsum_save,
    ReLU_save => ReLU_save);
    
clk_gen: process is
begin
clk <= not(clk);
wait for 20ns;
end process clk_gen;





end Behavioral;
