----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 04/21/2022 11:55:17 AM 
-- Design Name: 
-- Module Name: I-DNN_tb - Behavioral 
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: This testbench is used to test the I-DNN with only
-- one input MNIST sample. The image is taken from the MNIST package
-- validation data and it corresponds the sample number 0910 which
-- is the handwritten number 4. 
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
use ieee.math_real.all;

library std;
use std.textio.all;

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library work;
use work.I_DNN_package.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.COMMON_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;
use work.INTERMITTENCY_EMULATOR_package.all;

entity I_DNN_tb is

end I_DNN_tb;

architecture Behavioral of I_DNN_tb is

type datain_type is array(0 to layer_inputs(1)-1) of sfixed(DNN_neuron_inout_IntWidth-1 downto -(DNN_neuron_inout_FracWidth));
function makesfixed (bit_in: in bit_vector(DNN_neuron_inout_Width-1 downto 0)) return sfixed is
    variable fixedpoint_s: sfixed(DNN_neuron_inout_IntWidth-1 downto -DNN_neuron_inout_FracWidth);
    --variable a: std_logic := 0;
    begin
    for i in fixedpoint_s'range loop
        fixedpoint_s(i) := To_StdULogic(bit_in(i+DNN_neuron_inout_FracWidth));
    end loop;
    return fixedpoint_s;
end function;

impure function gen_datain(dataset_path: in string) return datain_type is
file text_header: text is in dataset_path;
variable text_line: line;
variable line_i: bit_vector(0 to DNN_neuron_inout_Width-1);
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

constant hazard_threshold : integer := 2400;


signal input_reg: datain_type := gen_datain("../"&DNN_testbench_input_path);

signal data_in: sfixed (DNN_neuron_inout_IntWidth-1 downto -DNN_neuron_inout_FracWidth):= (others => '0');
signal start: std_logic := '1';
signal clk: std_logic := '0';
signal data_out: sfixed (DNN_neuron_inout_IntWidth-1 downto -DNN_neuron_inout_FracWidth) := (others => '0');
signal addr_in: std_logic_vector(0 to natural(ceil(log2(real(layer_inputs(1)))))-1) := (others => '0');
signal addr_out: std_logic_vector(0 to natural(ceil(log2(real(layer_outputs(3)))))-1) := (others => '0');
signal data_v: std_logic;
signal n_power_reset: std_logic;
--Intermittency emulator
signal reset_emulator       : std_logic; 
signal threshold_value      : intermittency_arr_int_type(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0);
signal threshold_compared   : std_logic_vector(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0); 
signal select_threshold     : integer range 0 to INTERMITTENCY_NUM_THRESHOLDS -1; --This is used to select the threshold for power failure
--
signal thresh_stats         : threshold_t;
signal data_sampled         : std_logic:='0';
--
--constant voltage_trace_path   : string := "voltage_traces/I_layer_trace_complete.txt";
--This voltage trace 
constant voltage_trace_path   : string(1 to 33) := "voltage_traces/voltage_trace6.txt";


component I_DNN is
generic(
constant neuron_inout_IntWidth: natural;
constant neuron_inout_FracWidth: natural;
constant neuron_weight_IntWidth: natural;
constant neuron_weight_FracWidth: natural;
constant sigmoid_inputdataWidth: natural;
constant sigmoid_inputdataIntWidth: natural;
constant act_fun_type: string;
constant DNN_prms_path: string 
);
port(
data_in: in sfixed (DNN_neuron_inout_IntWidth-1 downto -DNN_neuron_inout_FracWidth);
start: in std_logic;
clk: in std_logic;
data_out: out sfixed (DNN_neuron_inout_IntWidth-1 downto -DNN_neuron_inout_FracWidth);
addr_in: out std_logic_vector(0 to natural(ceil(log2(real(layer_inputs(1)))))-1); --To scan through the valdation data set
data_v: out std_logic;
data_sampled: in std_logic;
--Augumented Pins
n_power_reset: in std_logic;
thresh_stats: in threshold_t
);
end component;

component intermittency_emulator is
generic(
    voltage_trace_path: string
);
port(
        sys_clk             : in std_logic; 
        threshold_value     : in intermittency_arr_int_type(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0);
        select_threshold    : in integer range 0 to INTERMITTENCY_NUM_THRESHOLDS -1;
        reset_emulator      : out std_logic; 
        threshold_compared  : out std_logic_vector(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0) 
);
end component;

begin

thresh_stats <= hazard when threshold_compared(1) = '1' else nothing;
intermittency_emulator_cmp: intermittency_emulator
generic map(
    voltage_trace_path => voltage_trace_path
)
port map(
    sys_clk => clk,
    threshold_value => threshold_value,
    select_threshold => select_threshold,
    reset_emulator => reset_emulator,
    threshold_compared => threshold_compared
);

I_DNN_cmp: I_DNN
generic map(
neuron_inout_IntWidth => DNN_neuron_inout_IntWidth,
neuron_inout_FracWidth => DNN_neuron_inout_FracWidth,
neuron_weight_IntWidth => DNN_neuron_weight_IntWidth,
neuron_weight_FracWidth => DNN_neuron_weight_FracWidth,
sigmoid_inputdataWidth => DNN_sigmoid_inputdata_Width,
sigmoid_inputdataIntWidth => DNN_sigmoid_inputdata_IntWidth,
act_fun_type => act_fun_type,
DNN_prms_path => DNN_prms_path
)
port map(
data_in => data_in,
start => start,
clk => clk,
data_out => data_out,
addr_in =>  addr_in, --To scan through the validation data set
data_v => data_v,
data_sampled => data_sampled,
--Augumented Pins
n_power_reset => n_power_reset,
thresh_stats => thresh_stats
);


clk_gen: process is

begin
wait for 20 ns;
clk <= not(clk);
end process clk_gen;

data_in <=  input_reg(to_integer(unsigned(addr_in)));

-- sets reset_emulator threshold
threshold_value(0) <= RST_EMU_THRESH;
-- sets the value for the hazard threshold, used by fsm_nv_reg_db
threshold_value(1) <= hazard_threshold;
n_power_reset <= not(reset_emulator);



start_gen: process(reset_emulator) is
begin
if reset_emulator = '1' then
    start <= '0';
else
    start <= '1';
end if;
end process start_gen;

data_sampled_gen: process(data_v) is

begin
if data_v = '1' then
    data_sampled <= '1';
else    
    data_sampled <= '0';
end if;

end process;



end Behavioral;
