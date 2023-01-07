----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/16/2022 11:20:38 AM
-- Design Name: 
-- Module Name: routing_w_sum_sig_tb - Behavioral
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

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity routing_w_sum_sig_tb is
--  Port ( );
end routing_w_sum_sig_tb;

architecture Behavioral of routing_w_sum_sig_tb is

constant num_outputs: natural := 30;
constant num_inputs: natural := 30;

signal clk: std_logic;

    component routing_w_sum_sig
        generic(
            num_outputs: natural;
            num_inputs: natural 
        );
    end component;
begin

routing_w_sum_comp: routing_w_sum_sig
generic map(
    num_outputs => num_outputs,
    num_inputs => num_inputs
);

tb: process is

begin
wait for 20 ns;
clk <= '1';
wait for 20 ns;
clk <= '0';
wait;

end process;

end Behavioral;
