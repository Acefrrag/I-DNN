----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso 
-- 
-- Create Date: 03/20/2022 04:04:40 PM
-- Design Name: 
-- Module Name: FSM_neuron - Behavioral
-- Project Name: DNN
-- Target Devices: 
-- Tool Versions: 
-- Description: FSM to control the pipelined neuron.
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;


entity I_FSM_layer is
generic (
rom_depth: natural := 3);--the number of summations in the weighted sum will be 16-1=15

port(clk: in std_logic;
    addr_TC: in std_logic; --This bit indicates if we are feeding the neuron with the last input
    start: in std_logic; --This signal initiate the neuron computation
    sum_reg_rst: out std_logic; --This bit resets the weighted sum register
    mul_sel: out std_logic; --This signal decides weather to add up the product w_i*x_i or the bias b
    out_v: out std_logic; --This signal aknowledge the output is valid
    update_out: out std_logic;
    addr_in_gen_rst: out std_logic); --This update the output of the neuron, since it is necessary to  
end I_FSM_layer;

architecture Behavioral of I_FSM_layer is
--Declarative Part
type neuron_state is (idle, init, w_sum, b_sum, act_log, finished);
signal pr_state, nx_state: neuron_state := idle;
signal out_val: std_logic := '0';

begin
    out_v <= out_val;
    state_reg: process(clk)
    begin
        if rising_edge(clk) then
            pr_state <= nx_state;
        end if;
    end process state_reg;
    
    output: process(all)
    --Outputs of this FSM are:
    --mul_sel: Multiplexer Selector: to select between weighted sum or bias
    --out_v: Output Data Valid: to aknowledge the data coming out the neruon is ready
    --sum_reg_rst: To reset the weighted sum register
    --update_out: To update the neuron output
    --addr_in_gen_en: To enable the address generator.
    begin
    case pr_state is
        when idle =>
            mul_sel <= '0';
            out_val <= '0';
            sum_reg_rst <= '1';
            update_out <= '0';
            addr_in_gen_rst <= '1';         
        when init =>
            mul_sel <= '0';
            out_val <= '0';
            sum_reg_rst <= '1';
            update_out <= '0';
            addr_in_gen_rst <= '0';    
        when w_sum =>
            mul_sel <= '0';
            out_val <= '0';
            sum_reg_rst <= '0';
            update_out <= '0';
            addr_in_gen_rst <= '0';
        when b_sum =>
            mul_sel <= '1';
            out_val <= '0';
            sum_reg_rst <= '0';
            update_out <= '0';      
            addr_in_gen_rst <= '1';  
        when act_log =>
            mul_sel <= '0';
            out_val <= '0';
            sum_reg_rst <= '0';
            update_out <= '0';
            addr_in_gen_rst <= '1';
        when finished =>
            mul_sel <= '0';
            out_val <= '1';
            sum_reg_rst <= '0';
            update_out <= '1';
            addr_in_gen_rst <= '1';
    end case;
    end process output;
    
    next_state: process(all)
    begin
    --default state
    nx_state <= idle;
    case pr_state is
        when idle =>
            --next
            if start = '1' then
                nx_state <= init;
            else
                nx_state <= idle;
            end if;
        when init =>
            nx_state <= w_sum;
        when w_sum =>
            if addr_TC = '1' then --we stopped feeding inputs
                  nx_state <= b_sum;
            else
                  nx_state <= w_sum;
            end if;
        when b_sum =>
            nx_state <= act_log;
        when act_log =>
            nx_state <= finished;
        when finished =>
            nx_state <= idle;
    end case;        
    end process next_state;
end Behavioral;
