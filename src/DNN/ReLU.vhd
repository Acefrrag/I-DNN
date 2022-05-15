----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso
-- 
-- Create Date: 03/22/2022 10:07:47 AM
-- Design Name: Activation Function Module
-- Module Name: act_log - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: This entity implements the activation logic block of the neuron
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
use ieee.numeric_std;
use ieee.std_logic_misc.all;-- To use OR_REDUCE

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library work;
use work.DNN_package.all;


entity ReLU is
generic(
    data_width: natural := 16);
port(
    data_in: in sfixed((neuron_int_width+input_int_width)-1 downto (-neuron_frac_width-input_frac_width));
    data_out: out sfixed(input_int_width-1 downto -input_frac_width));
end ReLU;

architecture Behavioral of ReLU is

signal addr_TC: std_logic := '0';
signal or_red_data_in: std_logic;

component unary_or is
generic (N: positive);
port(
        inp: in std_logic_vector(N-1 downto 0);
        outp: out std_logic);
end component unary_or;

--OR(data_in(2*bit_int-1 downto bit_int-1))

begin
    
    unary_or_comp: unary_or
    generic map(
        --
        N => input_int_width+1)--1 for the bit to the right and 1 for extra bit coming from the sum
    port map(
        inp => to_std_logic_vector(data_in(neuron_int_width+input_int_width-1 downto neuron_int_width-1)),
        outp => or_red_data_in
    );
    
    --ifs MUST GO INSIDE A PROCESS!!! If is sequential logic
    activation_logic: process(all)
    --Declarative part
    begin
        --Sequential Statement Part
        if data_in(neuron_int_width+input_int_width-1)='1' then
            data_out <= (others => '0');
        else
            if or_red_data_in='1' then --This number is greater than the maximum number which can be represented in bit_int bit
                data_out <= (data_out'LEFT => '0',
                            others => '1');
            else
                data_out <= data_in(input_int_width-1 downto -input_frac_width);
            end if; --[neuron_int_width, input_int_width, neuron_frac_width, input_frac_width]
        end if;
    end process activation_logic;
end Behavioral;
