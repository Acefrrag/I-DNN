----------------------------------------------------------------------------------
-- Company: University of Trento
-- Engineer: Michele Pio Fragasso
-- 
-- Create Date: 03/25/2022 11:04:08 AM
-- Design Name: 
-- Module Name: unary_or - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: This entity computes the or between the bits of std_logic_logic vector. It is used to verify if there is an overflow
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


entity unary_OR IS
    generic (N: natural := 8); --array size
    port (
        inp: in std_logic_vector(N-1 downto 0);
        outp: out std_logic);
end entity;
-------------------------------------------
architecture unary_OR of unary_OR is
    signal temp: std_logic_vector(N-1 downto 0);
begin
    temp(0) <= inp(0);
    gen: for i in 1 to N-1 generate
        temp(i) <= temp(i-1) or inp(i);
    end generate; 
    outp <= temp(N-1); 
end architecture;
-------------------------------------------
