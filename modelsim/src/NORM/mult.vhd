----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 08/26/2022 10:55:40 AM
-- Design Name: 
-- Module Name: mult - Behavioral
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
use ieee.numeric_std.all;

library work;
use work.COMMON_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;
use work.I_DNN_package.all;

entity mult is
port(
            A         : IN STD_LOGIC_VECTOR(PWR_APPROX_COUNTER_NUM_BITS - 1 DOWNTO 0);
            B           : IN STD_LOGIC_VECTOR(PWR_CONSUMPTION_ROM_BITS - 1 DOWNTO 0);
            P           : OUT STD_LOGIC_VECTOR(PWR_APPROX_COUNTER_NUM_BITS+PWR_CONSUMPTION_ROM_BITS-1 DOWNTO 0)

);
end mult;

architecture Behavioral of mult is

begin
P <= std_logic_vector(unsigned(A)*unsigned(B));

end Behavioral;