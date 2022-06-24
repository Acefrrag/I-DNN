----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/13/2022 08:42:04 PM
-- Design Name: 
-- Module Name: DATA_SAVE_PROCESS_tb - Behavioral
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


library work;
use work.I_DNN_package.all;
--Augumented Packages
use work.COMMON_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;


library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity DATA_SAVE_PROCESS_tb is

end DATA_SAVE_PROCESS_tb;

architecture Behavioral of DATA_SAVE_PROCESS_tb is

constant num_outputs: natural := 30;
constant num_inputs: natural := 30;

signal clk: std_logic:='0';
signal data_save_busy: std_logic:='0';
signal var_cntr_tc: std_logic:='0';
signal nv_reg_busy: std_logic:='0';
signal var_cntr_value: integer range 0 to NV_REG_WIDTH+2:=0;
signal mul_sel_backup: integer range 1 to 3:= 1;
signal nv_reg_busy_sig: std_logic:='0';
signal data_save_nv_reg_start_addr: STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0):=(others => '0');

signal data_save_var_cntr_ce: std_logic;
signal data_save_var_cntr_init: std_logic;
signal data_save_nv_reg_en: std_logic;
signal data_save_nv_reg_we: std_logic;
signal addrb: integer range 0 to num_outputs+2;
signal doutb: std_logic_vector(nv_reg_width-1 downto 0);
signal data_save_nv_reg_din: STD_LOGIC_VECTOR( 31 DOWNTO 0);
signal data_save_nv_reg_addr : STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);

signal data_save_v_reg_offset: INTEGER RANGE 0 TO V_REG_WIDTH -1;


component DATA_SAVE_PROCESS is
generic(
num_outputs: natural;
num_inputs: natural
);
port(
clk: in std_logic;
data_save_busy: in std_logic;
var_cntr_tc: in std_logic;
nv_reg_busy: in std_logic;
var_cntr_value: in integer range 0 to NV_REG_WIDTH+2;
mul_sel_backup: in  integer range 1 to 3:= 1;
nv_reg_busy_sig: in std_logic;
data_save_nv_reg_start_addr: in STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);
data_save_var_cntr_ce: out std_logic;
data_save_var_cntr_init: out std_logic;
data_save_nv_reg_en: out std_logic;
data_save_nv_reg_we: out std_logic;
addrb: out integer range 0 to num_outputs+2;
doutb: out std_logic_vector(nv_reg_width-1 downto 0);
data_save_nv_reg_din: out STD_LOGIC_VECTOR( 31 DOWNTO 0);
data_save_nv_reg_addr : out STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);


data_save_v_reg_offset: inout INTEGER RANGE 0 TO V_REG_WIDTH -1);


end component;

begin

DATA_SAVE_PROCESS_comp: DATA_SAVE_PROCESS
generic map(
num_outputs => num_outputs,
num_inputs => num_inputs
)
port map(
clk => clk,
data_save_busy => data_save_busy,
var_cntr_tc => var_cntr_tc, 
nv_reg_busy => nv_reg_busy,
var_cntr_value => var_cntr_value,
mul_sel_backup => mul_sel_backup,
nv_reg_busy_sig => nv_reg_busy_sig,
data_save_nv_reg_start_addr => data_save_nv_reg_start_addr,

data_save_var_cntr_ce => data_save_var_cntr_ce,
data_save_var_cntr_init => data_save_var_cntr_init,
data_save_nv_reg_en => data_save_nv_reg_en,
data_save_nv_reg_we => data_save_nv_reg_we,
addrb => addrb,
doutb => doutb,
data_save_nv_reg_din => data_save_nv_reg_din,
data_save_nv_reg_addr => data_save_nv_reg_addr,
data_save_v_reg_offset => data_save_v_reg_offset
);

tb: process is

begin
wait for 20 ns;
clk <= '1';
wait for 20 ns;
clk <= '0';
wait;

end process;


end Behavioral;
