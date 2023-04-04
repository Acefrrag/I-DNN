----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 08/07/2022 09:33:47 AM
-- Design Name: 
-- Module Name: test_sfixed_tb - Behavioral
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

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity test_sfixed_tb is
--  Port ( );
end test_sfixed_tb;

architecture Behavioral of test_sfixed_tb is
signal inputa: sfixed(31 downto -32);
component test_sfixed is
port(
    inputa: in sfixed (31 downto -32)
);
end component;
begin

test_sfixed_cmp: test_sfixed
port map(
    inputa => inputa
);

pr_comp: process is
begin
inputa <= to_sfixed(0.0178462595213205, inputa);
wait for 20 ns;
wait;
end process;

end Behavioral;


