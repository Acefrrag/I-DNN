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
library std;
use std.textio.all;

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.math_real.all;
use ieee.numeric_std.all;

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

type datain_type is array(0 to neuron_rom_depth-1) of sfixed(neuron_int_width-1 downto -neuron_frac_width);

function makesfixed (bit_in: in bit_vector(neuron_rom_width-1 downto 0)) return sfixed is
    variable fixedpoint_s: sfixed(neuron_int_width-1 downto -neuron_frac_width);
    --variable a: std_logic := 0;
    begin
    for i in fixedpoint_s'range loop
        fixedpoint_s(i) := To_StdULogic(bit_in(i+neuron_frac_width));
    end loop;
    return fixedpoint_s;
end function;

impure function gen_datain(dataset_path: in string) return datain_type is

file text_header: text is in dataset_path;
variable text_line: line;
variable line_i: bit_vector(0 to neuron_rom_width-1);
variable dataset_content: datain_type;

    begin
    for i in dataset_content'range loop
        readline(text_header, text_line);
        read(text_line, line_i);
        dataset_content(i) := makesfixed(line_i);
    end loop;
    file_close(text_header);
    return dataset_content;
end function;

--Data Input
signal input_reg: datain_type := gen_datain(dataset_path);


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
    fsm_nv_reg_state: in fsm_nv_reg_state_t; --shutdown_s, init_s, recovery_s, data_recovered_s, do_operation_s, start_data_save_s, data_save_s, data_saved_s
    nv_reg_busy: in std_logic;
    nv_reg_busy_sig: in  STD_LOGIC;
    nv_reg_dout: in STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
    previous_layer: in std_logic;--To decide wheather to save or not the output
    --Output
    task_status: out std_logic;
    nv_reg_en: out std_logic;
    nv_reg_we: out std_logic;
    nv_reg_addr: out std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
    nv_reg_din: out STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
    current_layer: out std_logic);--This is high when the layer is the currently active
end component I_layer;


constant num_inputs: natural := 30;
constant num_outputs: natural := 30;
--TestBench Signals
--Volatile Architecture Signals
--Input
signal clk: std_logic:= '0';
signal data_in: sfixed(input_int_width-1 downto -input_frac_width):= (others => '0');
signal data_out_sel: std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1) := (others => '0');
signal start: std_logic:='0';--to increment the counter while the output is begin computed
--Output
signal data_out: sfixed(neuron_int_width-1 downto -neuron_frac_width);--The next layer controls which neuron's output to access
signal data_in_sel: std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);
signal data_v: std_logic;
--Augumented Pins
--Input
signal n_power_reset: std_logic:='0';--Device is powered up
signal fsm_nv_reg_state: fsm_nv_reg_state_t:=shutdown_s;
signal nv_reg_busy: std_logic:='0';
signal nv_reg_busy_sig:  STD_LOGIC:='0';
signal nv_reg_dout: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0):=(others=>'0');
signal previous_layer: std_logic:='0';--To decide wheather to save or not the output
--Output
signal task_status: std_logic;
signal nv_reg_en: std_logic;
signal nv_reg_we: std_logic;
signal nv_reg_addr: std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
signal nv_reg_din: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
signal current_layer: std_logic;

begin

I_layer_comp: I_layer
generic map
(
    num_inputs => num_inputs,
    num_outputs => num_outputs,
    layer_no => 1,--Layer number (identifier)
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
    previous_layer => previous_layer,--To decide wheather to save or not the output
    --Output
    task_status => task_status,
    nv_reg_en => nv_reg_en,
    nv_reg_we => nv_reg_we,
    nv_reg_addr => nv_reg_addr,
    nv_reg_din => nv_reg_din,
    current_layer => current_layer
);

testbench: process is
    begin
        start <= '1';
        wait for 20 ns;
        clk <= '1';
        wait for 20 ns;
        clk <= '0';
        wait for 20 ns;
        clk <= '1';
        wait for 20 ns;
        clk <= '0';
        n_power_reset <= '1';--Power On
        wait for 20 ns;  --shutdown_s, init_s, recovery_s, data_recovered_s, do_operation_s, start_data_save_s, data_save_s, data_saved_s
        -- type fsm_nv_reg_state_t is(
        --            shutdown_s,
        --            init_s,
        --            start_data_recovery_s,
        --            recovery_s,
        --            data_recovered_s,
        --            do_operation_s,
        --            start_data_save_s,
        --            data_save_s,
        --            data_saved_s
        --        );
        clk <= '1'; --Computation of the layer starts here. Data is being recovered here 
        fsm_nv_reg_state <= init_s;
        wait for 20 ns;
        clk <= '0';
        wait for 20 ns;
        fsm_nv_reg_state <= start_data_recovery_s;
        clk <= '1';
        wait for 20 ns;
        clk <= '0';
        wait for 20 ns;
        fsm_nv_reg_state <= recovery_s;
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
        --Data is completely fetched at this time (task status is 0)
        clk <= '1';
        wait for 20 ns;
        clk <= '0';
        wait for 20 ns;
        fsm_nv_reg_state <= data_recovered_s;
        clk <= '1';
        wait for 20 ns;
        clk <= '0';
        wait for 20 ns;
        fsm_nv_reg_state <= do_operation_s;
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
        fsm_nv_reg_state <= start_data_save_s;
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
        fsm_nv_reg_state <= data_save_s;
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
        wait;
end process testbench;


data_in <= input_reg(to_integer(unsigned(data_in_sel)));



end Behavioral;
