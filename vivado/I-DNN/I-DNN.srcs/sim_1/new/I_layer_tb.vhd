----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 05/24/2022 05:08:53 PM
-- Design Name: 
-- Module Name: I_layer_tb - Behavioral
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

library work;
use work.I_DNN_package.all;
use work.COMMON_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity I_layer_tb is

end I_layer_tb;

architecture Behavioral of I_layer_tb is
component I_layer is
generic(
    constant num_inputs: natural;
    constant num_outputs: natural;
    constant layer_no: natural;--Layer number (identifier)
    constant act_type: string; -- Choose between "ReLU","Sig"
    constant act_fun_size: natural -- If the user choose an analytical activation function the number of sample have to be chosen
);
port(
    clk: in std_logic;
    data_in: in sfixed(input_int_width-1 downto -input_frac_width);
    data_out_sel: in std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1);
    start: in std_logic;--to increment the counter while the output of the output is begin computed
    data_out: out sfixed(neuron_int_width-1 downto -neuron_frac_width);--The next layer controls which neuron's output to access
    data_in_sel: out std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);
    data_v: out std_logic;
    --Augumented Pins
    --Input
    n_power_reset: in std_logic;
    fsm_nv_reg_state: in fsm_nv_reg_state_t;
    nv_reg_busy: in std_logic;
    nv_reg_busy_sig: in  STD_LOGIC;
    nv_reg_dout: in STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
    save_output: in std_logic;--To decide wheather to save or not the output
    --Output
    task_status: out std_logic;
    nv_reg_en: out std_logic;
    nv_reg_we: out std_logic;
    nv_reg_addr: out std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
    nv_reg_din: out STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
    save_state: out std_logic);--This is high when the layer is the currently active
end component I_layer;


constant num_inputs: natural := 30;
constant num_outputs: natural := 30;
--TestBench Signals
--Volatile Architecture Signals
signal clk: std_logic;
signal data_in: sfixed(input_int_width-1 downto -input_frac_width);
signal data_out_sel: std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1);
signal start: std_logic;--to increment the counter while the output of the output is begin computed
signal data_out: sfixed(neuron_int_width-1 downto -neuron_frac_width);--The next layer controls which neuron's output to access
signal data_in_sel: std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);
signal data_v: std_logic;
--Augumented Pins
--Input
signal n_power_reset: std_logic;
signal fsm_nv_reg_state: fsm_nv_reg_state_t;
signal nv_reg_busy: std_logic;
signal nv_reg_busy_sig:  STD_LOGIC;
signal nv_reg_dout: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
signal save_output: std_logic;--To decide wheather to save or not the output
--Output
signal task_status: std_logic;
signal nv_reg_en: std_logic;
signal nv_reg_we: std_logic;
signal nv_reg_addr: std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
signal nv_reg_din: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
signal save_state: std_logic;

begin

I_layer_comp: I_layer
generic map
(
    num_inputs => num_inputs,
    num_outputs => num_outputs,
    layer_no => 0,--Layer number (identifier)
    act_type => "ReLu", -- Choose between "ReLU","Sig"
    act_fun_size => 10 -- If the user choose an analytical activation function the number of sample have to be chosen
)
port map
(   
    --Volatile Pins
    --Inputs
    clk => clk,
    data_in => data_in,
    data_out_sel => data_out_sel,
    start => start,
    --Outputs    
    data_out => data_out,
    data_in_sel => data_in_sel,
    data_v => data_v,
    --Augumented Pins
    --Input
    n_power_reset => n_power_reset,
    fsm_nv_reg_state => fsm_nv_reg_state,
    nv_reg_busy => nv_reg_busy,
    nv_reg_busy_sig => nv_reg_busy_sig,
    nv_reg_dout => nv_reg_dout,
    save_output => save_output,--To decide wheather to save or not the output
    --Output
    task_status => task_status,
    nv_reg_en => nv_reg_en,
    nv_reg_we => nv_reg_we,
    nv_reg_addr => nv_reg_addr,
    nv_reg_din => nv_reg_din,
    save_state => save_state
);




end Behavioral;
