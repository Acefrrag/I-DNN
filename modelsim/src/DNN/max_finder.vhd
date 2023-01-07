----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 04/17/2022 12:00:58 PM
-- Design Name: 
-- Module Name: max_finder - Behavioral
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
library ieee_proposed;
use ieee_proposed.fixed_pkg.all;


library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;



library work;
use work.DNN_package.all;

entity max_finder is
generic(
    constant num_inputs: natural := 30);
port(
    clk: in std_logic;
    data_in: in sfixed(input_int_width-1 downto -input_frac_width);
    start: in std_logic;
    in_sel: out std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);
    data_out: out sfixed(input_int_width-1 downto -input_frac_width);
    addr_out: out std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);
    data_v: out std_logic
    );
end max_finder;

architecture Behavioral of max_finder is

type max_finder_state is(idle, finding, finished);


signal max: sfixed(input_int_width-1 downto -input_frac_width):=(others=>'0');
signal addr: std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1):=(others => '0');
signal rst: std_logic;
signal pr_state,nx_state: max_finder_state;
signal addr_TC: std_logic;

begin
in_sel <= addr;


--Finite State Machine
fsm_out: process(all) is
begin
case pr_state is
when idle =>
    rst <= '1';
    data_v <= '0';
when finding =>
    rst <= '0';
    data_v <= '0';
when finished =>
    rst <= '0';
    data_v <= '1';
end case;
end process fsm_out;

fsm_nx_state: process(all) is
begin
case pr_state is
when idle =>
    if start='1' then
        nx_state <= finding;
    else
        nx_state <= idle;
    end if;
when finding =>
    if addr_TC = '1' then
        nx_state <= finished;
    else    
        nx_state <= idle;
    end if;
when finished =>
    nx_state <= idle;
end case;

end process fsm_nx_state;

fsm_seq: process is
begin

end process fsm_seq;



end Behavioral;
