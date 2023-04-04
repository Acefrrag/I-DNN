----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 01/26/2023 01:06:06 PM
-- Design Name: 
-- Module Name: mult_tb - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: Multiplier (used in the instant power approximation unit)
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

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity mult_tb is

end mult_tb;

architecture Behavioral of mult_tb is

signal A: std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS - 1 DOWNTO 0);
signal B: STD_LOGIC_VECTOR(PWR_CONSUMPTION_ROM_BITS - 1 DOWNTO 0);
signal P: STD_LOGIC_VECTOR(PWR_APPROX_COUNTER_NUM_BITS+PWR_CONSUMPTION_ROM_BITS-1 DOWNTO 0);



component mult is
port(
            A         : IN STD_LOGIC_VECTOR(PWR_APPROX_COUNTER_NUM_BITS - 1 DOWNTO 0);
            B           : IN STD_LOGIC_VECTOR(PWR_CONSUMPTION_ROM_BITS - 1 DOWNTO 0);
            P           : OUT STD_LOGIC_VECTOR(PWR_APPROX_COUNTER_NUM_BITS+PWR_CONSUMPTION_ROM_BITS-1 DOWNTO 0)

);
end component;

begin

mult_cmp: mult
port map(
    A => A,
    B => B,
    P => P
);


A <= std_logic_vector(to_unsigned(60000,PWR_APPROX_COUNTER_NUM_BITS));
B <= std_logic_vector(to_unsigned(50,PWR_CONSUMPTION_ROM_BITS));


end Behavioral;
