----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 08/13/2022 07:07:22 AM
-- Design Name: 
-- Module Name: test_sfixed - Behavioral
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

library ieee;
use ieee.fixed_pkg.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity test_sfixed is
port(
    inputa: in sfixed(31 downto -32)
);
end test_sfixed;

architecture Behavioral of test_sfixed is

signal test1: sfixed(15 downto -16);

begin

test1 <= resize(inputa, 15, -16);



end Behavioral;
