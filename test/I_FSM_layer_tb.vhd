----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/12/2022 11:18:22 AM
-- Design Name: 
-- Module Name: I_FSM_layer_tb - Behavioral
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

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
use ieee.math_real.all;

library work;
use work.I_DNN_package.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;
use work.COMMON_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity I_FSM_layer_tb is
--  Port ( );
end I_FSM_layer_tb;

architecture Behavioral of I_FSM_layer_tb is

constant num_outputs: natural := 30;
constant num_inputs: natural := 30;


signal clk: std_logic:='0';
signal addr_TC: std_logic:= '0';
signal start: std_logic:='0';
signal sum_reg_rst: std_logic;
signal mul_sel: std_logic;
signal out_v: std_logic; --This signal aknowledge the output is valid
signal update_out: std_logic; --This update the output of the neuron, since it is necessary to  
signal addr_in_gen_rst: std_logic;
--Enhanced ports
--Input pins
signal n_power_reset: std_logic:='1';
signal  data_rec_busy: std_logic:='0';
signal  fsm_nv_reg_state: fsm_nv_reg_state_t:=shutdown_s;
signal  fsm_state_rec: std_logic_vector(0 to nv_reg_width-1):=(others => '0');-- To recover the state of the fsm
signal  data_rec_recovered_offset: integer range 0 to num_outputs+1:=0;--This contains the address 
signal  data_rec_type: data_backup_type_t:=nothing; --This value must be held from the outer module furing the whole recovery/save process
--Output pins
signal  w_rec: std_logic_vector (0 to 2*num_outputs+1); --activation pins for recovery of the state
signal  o_rec: std_logic_vector (0 to num_outputs+1); --activation pins for recovery of the outputs (last 2 are unused)
signal  addra: integer range 0 to num_outputs+2; --This
signal  fsm_state_save: std_logic_vector(0 to nv_reg_width-1); --To save the state of the fsm of the layer



component I_FSM_layer is
generic (
num_outputs: natural;
rom_depth: natural);--the number of summations in the weighted sum will be 16-1=15
port(clk: in std_logic; 
    addr_TC: in std_logic; --This bit indicates if we are feeding the neuron with the last input
    start: in std_logic; --This signal initiate the neuron computation
    sum_reg_rst: out std_logic; --This bit resets the weighted sum register
    mul_sel: out std_logic; --This signal decides weather to add up the product w_i*x_i or the bias b
    out_v: out std_logic; --This signal aknowledges the output is valid
    update_out: out std_logic;
    addr_in_gen_rst: out std_logic;
    --Augumented Pins
    --Input pins
    n_power_rst: in std_logic;
    data_rec_busy: in std_logic;
    data_rec_type: in data_backup_type_t;
    fsm_nv_reg_state: in fsm_nv_reg_state_t;
    fsm_state_rec: in std_logic_vector(0 to nv_reg_width-1);-- To recover the state of the fsm
    data_rec_recovered_offset: in integer range 0 to num_outputs+1; 
    --Output Pins
    s_r: out std_logic_vector(0 to 2*num_outputs+1); --activation pins for recovery of the state
    o_r: out std_logic_vector(0 to num_outputs+1); --activation pins for recovery of the outputs (last 2 are unused)
    addra: out integer range 0 to num_outputs+2;
    fsm_state_save: out std_logic_vector(0 to nv_reg_width-1) --To save the state of the fsm of the layer
    ); --This updates the output of the neuron, since it is necessary to  
end component;






begin


I_fsm_layer_comp: I_FSM_layer
generic map(
num_outputs => num_outputs,
rom_depth => num_inputs
)
port map(
    clk => clk,
    addr_TC => addr_TC, --This bit indicates if we are feeding the neuron with the last input
    start => start,  --This signal initiate the neuron computation
    sum_reg_rst => sum_reg_rst, --This bit resets the weighted sum register
    mul_sel => mul_sel,  --This signal decides weather to add up the product w_i*x_i or the bias b
    out_v => out_v,--This signal aknowledge the output is valid
    update_out => update_out,
    addr_in_gen_rst => addr_in_gen_rst,
    --Augumented Pins
    --Input pins
    data_rec_type => data_rec_type,
    n_power_rst => n_power_reset,
    data_rec_busy => data_rec_busy,
    fsm_nv_reg_state => fsm_nv_reg_state,
    fsm_state_rec => fsm_state_rec,
    data_rec_recovered_offset => data_rec_recovered_offset,
    --Output pins
    o_r => o_rec,
    s_r => w_rec,
    addra => addra,
    fsm_state_save => fsm_state_save

    ); --This update the output of the neuron, since it is necessary to  
 
I_FSM_layer_tb_pr: process is
begin
wait for 20 ns;
clk <= '1';
wait for 20 ns;
clk <= '0';
wait for 20 ns;
wait;
end process;


end Behavioral;
