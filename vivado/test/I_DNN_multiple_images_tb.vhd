----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso
-- 
-- Create Date: 01/16/2023 11:24:12 AM
-- Design Name: 
-- Module Name: I_DNN_multiple_images_tb - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: This testbench tests the intermittent neural
-- network with multiple images (8 total images).
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
use ieee.math_real.all;

library std;
use std.textio.all;

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library work;
use work.I_DNN_package.all;
use work.I_DNN_MI_package.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.COMMON_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;
use work.INTERMITTENCY_EMULATOR_package.all;

entity I_DNN_multiple_images_tb is

end I_DNN_multiple_images_tb;

architecture Behavioral of I_DNN_multiple_images_tb is


function makesfixed (bit_in: in bit_vector(MI_DNN_neuron_inout_Width-1 downto 0)) return sfixed is
    variable fixedpoint_s: sfixed(MI_DNN_neuron_inout_IntWidth-1 downto -MI_DNN_neuron_inout_FracWidth);
    --variable a: std_logic := 0;
    begin
    for i in fixedpoint_s'range loop
        fixedpoint_s(i) := To_StdULogic(bit_in(i+MI_DNN_neuron_inout_FracWidth));
    end loop;
    return fixedpoint_s;
end function;

impure function gen_datain(dataset_path: in string) return datain_type is
file text_header: text is in dataset_path;
variable text_line: line;
variable line_i: bit_vector(0 to MI_DNN_neuron_inout_Width-1);
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


impure function gen_digit(dataset_path: in string) return integer is
file text_header: text is in dataset_path;
variable text_line: line;
variable digit_content: integer;

    begin
    readline(text_header, text_line);
    read(text_line, digit_content);
    file_close(text_header);
    return digit_content;
end function;



impure function load_images(full_path: in pathname_type) return set_images_type is

variable images_content: set_images_type;

begin
for i in images_content'range loop
    images_content(i) := gen_datain(full_path(i));
end loop;

return(images_content);
end function;

impure function load_digits(full_path: in digit_pathname_type) return set_digits_type is

variable digits_content: set_digits_type;

begin
for i in digits_content'range loop
    digits_content(i) := gen_digit(full_path(i));
end loop;

return(digits_content);

end function;

      
signal hazard_threshold : integer := 3000;
signal input_reg: datain_type := (others => (others => '0'));
signal images: set_images_type := load_images(full_path_images);
signal digits: set_digits_type := load_digits(full_path_digits);
signal data_in: sfixed (MI_DNN_neuron_inout_IntWidth-1 downto -MI_DNN_neuron_inout_FracWidth):= (others => '0');
signal start: std_logic := '1';
signal clk: std_logic := '0';
signal data_out: sfixed (MI_DNN_neuron_inout_IntWidth-1 downto -MI_DNN_neuron_inout_FracWidth) := (others => '0');
signal addr_in: std_logic_vector(0 to natural(ceil(log2(real(layer_inputs(1)))))-1) := (others => '0');
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
--signal voltage_trace_path   : string := "voltage_traces/I_layer_trace_complete.txt";
--signal voltage_trace_path   : string(1 to 47) := "voltage_traces/I_DNN_trace_complete_4layers.txt";
constant voltage_trace_path: string(1 to 33) := "voltage_traces/voltage_trace3.txt";
signal image_no: integer := 0;
signal shtdwn_counter, clk_counter: integer := 0;
signal executed_batches: integer := 0;
signal corruption_backup_counter: integer := 0;
signal correct_backup_counter: integer := 0;
signal digit_out: integer := 0;

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
data_in: in sfixed (MI_DNN_neuron_inout_IntWidth-1 downto -MI_DNN_neuron_inout_FracWidth);
start: in std_logic;
clk: in std_logic;
data_out: out sfixed (MI_DNN_neuron_inout_IntWidth-1 downto -MI_DNN_neuron_inout_FracWidth);
addr_in: out std_logic_vector(0 to natural(ceil(log2(real(layer_inputs(1)))))-1); --To scan through the valdation data set
data_v: out std_logic;
data_sampled: in std_logic;
digit_out: out integer;
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
neuron_inout_IntWidth => MI_DNN_neuron_inout_IntWidth,
neuron_inout_FracWidth => MI_DNN_neuron_inout_FracWidth,
neuron_weight_IntWidth => MI_DNN_neuron_weight_IntWidth,
neuron_weight_FracWidth => MI_DNN_neuron_weight_FracWidth,
sigmoid_inputdataWidth => MI_DNN_sigmoid_inputdata_Width,
sigmoid_inputdataIntWidth => MI_DNN_sigmoid_inputdata_IntWidth,
act_fun_type => MI_act_fun_type,
DNN_prms_path => MI_DNN_prms_path
)
port map(
data_in => data_in,
start => start,
clk => clk,
data_out => data_out,
addr_in =>  addr_in, --To scan through the validation data set
data_v => data_v,
digit_out => digit_out,
data_sampled => data_sampled,
--Augumented Pins
n_power_reset => n_power_reset,
thresh_stats => thresh_stats
);

input_reg <= images(image_no);

image_no_pr: process(data_v) is
variable error: std_logic := '0';
begin
if rising_edge(data_v) then
    if digit_out = digits(image_no) then
        correct_backup_counter <= correct_backup_counter + 1;
    else
        corruption_backup_counter <= corruption_backup_counter +1 ;
        error := '1';
    end if;
    executed_batches <= executed_batches + 1;
    if error = '0' then
        image_no <= image_no + 1;
        if image_no = 7 then
            image_no <= 0;
        end if;
    else
        image_no <= image_no;
    end if;
end if;
end process;

counter_proc: process (clk,n_power_reset) is
begin
        if falling_edge(n_power_reset) then
            shtdwn_counter <= shtdwn_counter +1;
        end if;
        if n_power_reset = '1' AND rising_edge(clk) then
            clk_counter <= clk_counter + 1;
        end if;
end process;




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


data_sampled_pr: process (all) is

begin
if (data_v) = '1' then
    data_sampled <= '1';
else
    data_sampled <= '0';
end if;

end process;


start_gen: process(clk) is
begin
if rising_edge(clk) then
    if data_v = '1' then
        start <= '1';
    elsif start = '1' and to_integer(unsigned(addr_in)) > 0 then
        start <= '0';
    end if;
end if;
end process start_gen;



end Behavioral;