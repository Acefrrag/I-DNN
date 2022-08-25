----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 08/23/2022 04:58:18 PM
-- Design Name: 
-- Module Name: SOFT_MAX - Behavioral
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
use work.COMMON_PACKAGE.all;
use work.I_DNN_package.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;

entity SOFT_MAX is
generic(
num_inputs: natural := 10
);
port(
--INPUTS
clk: in std_logic;
start: in std_logic;
data_in: in sfixed(neuron_int_width-1 downto -neuron_frac_width);
data_sampled: in std_logic;
n_power_reset: in std_logic;
--OUTPUTS
data_in_sel: out std_logic_vector(natural(ceil(log2(real(num_inputs))))-1 downto 0);
out_v: out std_logic;
data_out: out sfixed(neuron_int_width-1 downto -neuron_frac_width);
digit_out: out integer range 0 to 9;
softmax_state: out softmax_state_t
);
end SOFT_MAX;

architecture Behavioral of SOFT_MAX is

--Comparator signals
signal temp_max: sfixed(neuron_int_width-1 downto -neuron_frac_width):=(others => '0');
signal temp_max_addr: integer range 0 to 9;
signal comparator_out: sfixed(neuron_int_width-1 downto -neuron_frac_width):=(others => '0');
signal comparator_out_addr: integer range 0 to 9;
signal data_v: std_logic := '0';
--others
signal rst: std_logic := '0';
signal addr: std_logic_vector(natural(ceil(log2(real(num_inputs))))-1 downto 0):=(others=>'0');
signal addr_TC: std_logic := '0';
--FSM
signal pr_state, nx_state: softmax_state_t := idle;
signal digit_out_internal: integer range 0 to 9:=0;
signal data_out_internal: sfixed(neuron_int_width-1 downto -neuron_frac_width):=(others => '0');
signal reg_en: std_logic:='0';
begin

softmax_state <= pr_state;
out_v <= data_v;
rst <= not(n_power_reset);
digit_out <= digit_out_internal;
data_out<= data_out_internal;
--Comparator
comparator_out <= (others => '0') when data_v = '0' and pr_state = idle else
data_in when data_in > temp_max else
temp_max;
comparator_out_addr <= 0 when data_v = '0' and pr_state = idle else
to_integer(unsigned(data_in_sel)) when data_in > temp_max else
temp_max_addr;
data_out_internal <= comparator_out when data_v = '0' else
data_out_internal;
digit_out_internal <= comparator_out_addr when data_v = '0' else
digit_out_internal;

--Temporary Maximum Value Register
max_register: process(clk) is
    begin
        if rising_edge(clk) then
            temp_max <= comparator_out;
            temp_max_addr <= comparator_out_addr;
        end if;
end process;

addr_TC <= '0' when rst = '1' else
     --data_backup_vect_state_rec(num_outputs+1)(natural(nv_reg_width-1)) when s_rec_vect(num_outputs) = '1' and data_rec_busy = '1' else
     '1' when unsigned(addr) = num_inputs-1;
data_in_sel <= addr;
gen_addr: process(clk,rst,data_sampled) is --This process generate the address to access the neuron weight and get the input from the previous layer
begin
    if rst = '1' then
        addr <= (others => '0');
    else
       if rising_edge(clk) then
            if reg_en = '1' then
                addr <= std_logic_vector(unsigned(addr) + 1);
                if unsigned(addr) = num_inputs-1 then
                    addr <= (others=>'0');
                end if;
            end if;
        end if;
    end if;
end process gen_addr;

fsm_softmax_output: process(all) is
begin
    --Default values
    reg_en <= '0';
    if data_sampled = '1' then
        data_v <= '0';
    else
        data_v <= data_v;
    end if;
    case pr_state is
        when power_off =>
            data_v <= '0';
            reg_en <= '0';
        when idle =>
            --data_v <= data_v;
            reg_en <= '0';
        when active =>
            data_v <= '0';
            reg_en <= '1';
        when finished =>
            data_v <= '1';
            reg_en <= '0';
    end case;
end process;

fsm_softmax_state: process(clk, n_power_reset) is
begin
    if n_power_reset = '0' then
        pr_state <= power_off;
    else
        if rising_edge(clk) then
            pr_state <= nx_state;
        end if;
    end if;
end process;

fsm_softmax_nx_state: process(all) is
begin
nx_state <= idle;
case pr_state is
    when power_off =>
        --the fsm is doing nothing
    when idle =>
        if start = '1' then
            nx_state <= active;
        else
            nx_state <= idle;
        end if;
    when active =>
        if addr_TC = '1' then
            nx_state <= finished;
        else
            nx_state <= active;
        end if;
    when finished => 
        nx_state <= idle;
end case;
        
end process;

end Behavioral;
