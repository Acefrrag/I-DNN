----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 08/23/2022 10:22:43 PM
-- Design Name: 
-- Module Name: SOFTMAX_tb - Behavioral
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


library ieee;
use ieee.STD_LOGIC_1164.ALL;
use ieee.math_real.all;
use ieee.numeric_std.all;

library std;
use std.textio.all;

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library work;
use work.COMMON_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.I_DNN_package.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity SOFTMAX_tb is
--  Port ( );
end SOFTMAX_tb;

architecture Behavioral of SOFTMAX_tb is
type data_in_vect_t is array (0 to 9) of sfixed(neuron_int_width-1 downto -neuron_frac_width);

function makesfixed (bit_in: in bit_vector(neuron_rom_width-1 downto 0)) return sfixed is
    variable fixedpoint_s: sfixed(neuron_int_width-1 downto -neuron_frac_width);
    --variable a: std_logic := 0;
    begin
    for i in fixedpoint_s'range loop
        fixedpoint_s(i) := To_StdULogic(bit_in(i+neuron_frac_width));
    end loop;
    return fixedpoint_s;
end function;

impure function gen_data_in(datain_path: in string) return data_in_vect_t is
file text_header: text is in datain_path;
variable text_line: line;
variable line_i: bit_vector( 0 to neuron_rom_width-1);
variable data_in_content: data_in_vect_t;
begin
    for i in data_in_content'range loop
        readline(text_header, text_line);    
        read(text_line, line_i);
        data_in_content(i) := makesfixed(line_i);
    end loop;
    return data_in_content;
end function;

constant num_inputs: natural := 10;
signal data_in_vect: data_in_vect_t := gen_data_in("../scripts/datasets/testData/input_SOFTMAX.mif");
signal clk: std_logic:='0';
signal start: std_logic:='0';
signal data_in: sfixed(neuron_int_width-1 downto -neuron_frac_width);
signal data_sampled: std_logic:='0';
signal n_power_reset: std_logic:='1';
signal data_in_sel: std_logic_vector(natural(ceil((log2(real(num_inputs)))))-1 downto 0);
signal out_v: std_logic:='0';
signal data_out: sfixed(neuron_int_width-1 downto -neuron_frac_width);
signal digit_out: integer range 0 to 9:=0;

component SOFT_MAX is
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
digit_out: out integer range 0 to 9
);
end component;
begin

SOFTMAX_comp: SOFT_MAX
generic map(
num_inputs => 10
)
port map(
clk => clk,
start => start,
data_in => data_in,
data_sampled => data_sampled,
n_power_reset => n_power_reset,
--OUTPUTS
data_in_sel => data_in_sel,
out_v => out_v,
data_out => data_out,
digit_out => digit_out
);

clk_gen: process is
begin
wait for 20 ns;
clk <= not(clk);
end process;

start_gen: process is
begin
wait for 100 ns;
start <= '1';
wait for 50 ns;
start <= '0';
wait;
end process;

data_sampled_pr: process(out_v) is
begin
if out_v = '1' then
    data_sampled <= '1' after 50 ns;
end if;
end process;

data_in <= data_in_vect(to_integer(unsigned(data_in_sel)));

data_in_vect_gen: process(out_v) is
begin
if out_v = '1' then
    data_in_vect(0) <= to_sfixed(10.0, data_in_vect(0)) after 60 ns;
end if;
end process;

end Behavioral;
