----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/14/2022 08:00:32 PM
-- Design Name: 
-- Module Name: VAR_CNTR_PROCESS - Behavioral
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
use work.I_DNN_package.all;
--Augumented Packages
use work.COMMON_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity VAR_CNTR_PROCESS_tb is

end VAR_CNTR_PROCESS_tb;

architecture Behavioral of VAR_CNTR_PROCESS_tb is

constant num_outputs: natural := 30;
constant num_inputs: natural := 30;

signal clk: std_logic:='0';
signal task_status: std_logic:= '1';
signal task_status_internal: std_logic:='1';
signal nv_reg_busy_sig: std_logic:='0';
signal var_cntr_init: std_logic:='0';
signal n_power_reset: std_logic:='1';
signal var_cntr_ce: std_logic:='1';
signal var_cntr_end_value: INTEGER range 0 to NV_REG_WIDTH+2:=5;
signal var_cntr_value: INTEGER range 0 to NV_REG_WIDTH+2;
signal var_cntr_value_last: INTEGER range 0 to NV_REG_WIDTH+2;
signal var_cntr_tc: std_logic;
signal var_cntr_clk: std_logic;
signal data_rec_var_cntr_end_value : INTEGER; 
signal data_rec_offset: INTEGER RANGE 0 TO 2*num_outputs+2+2;
signal data_save_var_cntr_end_value: INTEGER;
signal data_save_v_reg_offset:  INTEGER RANGE 0 TO V_REG_WIDTH -1;

component VAR_CNTR_PROCESS is
    generic(
    num_outputs: natural;
    num_inputs: natural
    );
    port(
    clk: in std_logic;
    task_status: in std_logic;
    task_status_internal: in std_logic;
    nv_reg_busy_sig: in std_logic;
    var_cntr_init: in std_logic;
    n_power_reset: in std_logic;
    var_cntr_ce: in std_logic;
    var_cntr_end_value: in INTEGER range 0 to NV_REG_WIDTH+2;
    var_cntr_value: out INTEGER range 0 to NV_REG_WIDTH+2;
    var_cntr_value_last: out INTEGER range 0 to NV_REG_WIDTH+2;
    var_cntr_tc: out std_logic;
    var_cntr_clk: out std_logic;
    data_rec_var_cntr_end_value : out INTEGER; 
    data_rec_offset: IN INTEGER RANGE 0 TO 2*num_outputs+2+2;
    data_save_var_cntr_end_value: out INTEGER;
    data_save_v_reg_offset:  in INTEGER RANGE 0 TO V_REG_WIDTH -1
    );
end component;

begin

VAR_CNTR_PROCESS_comp: VAR_CNTR_PROCESS
generic map(
    num_outputs => num_outputs,
    num_inputs => num_inputs
)
port map(
    clk => clk,
    task_status => task_status,
    task_status_internal => task_status_internal,
    nv_reg_busy_sig => nv_reg_busy_sig,
    var_cntr_init => var_cntr_init,
    n_power_reset => n_power_reset,
    var_cntr_ce => var_cntr_ce,
    var_cntr_end_value =>     var_cntr_end_value,
    var_cntr_value => var_cntr_value,
    var_cntr_value_last => var_cntr_value_last,
    var_cntr_tc => var_cntr_tc,
    var_cntr_clk => var_cntr_clk,
    data_rec_var_cntr_end_value => data_rec_var_cntr_end_value,
    data_rec_offset => data_rec_offset,
    data_save_var_cntr_end_value => data_save_var_cntr_end_value,
    data_save_v_reg_offset => data_save_v_reg_offset
);

tb: process is
begin
    wait for 20 ns;
    clk <= '1';
    wait for 20 ns;
    clk <= '0';
    wait for 20 ns;
    clk <= '1';
    wait for 20 ns;
    clk <= '0';
    wait for 20 ns;
    clk <= '1';
    wait for 20 ns;
    clk <= '0';
    wait for 20 ns;
    clk <= '1';
    wait for 20 ns;
    clk <= '0';
    wait for 20 ns;
    clk <= '1';
    wait for 20 ns;
    clk <= '0';
    wait;
end process;

end Behavioral;
