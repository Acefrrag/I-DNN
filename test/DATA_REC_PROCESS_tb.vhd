----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/12/2022 05:19:46 PM
-- Design Name: 
-- Module Name: DATA_REC_PROCESS_tb - Behavioral
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

entity DATA_REC_PROCESS_tb is

end DATA_REC_PROCESS_tb;

architecture Behavioral of DATA_REC_PROCESS_tb is

constant num_outputs: natural := 30;
constant num_inputs: natural := 30;

signal clk: std_logic := '0';
signal n_power_reset: std_logic:= '0';
signal nv_reg_busy: std_logic:= '0';
signal fsm_nv_reg_state: fsm_nv_reg_state_t := shutdown_s;
signal data_rec_offset: INTEGER RANGE 0 TO 2*num_outputs+2+2:=0;
signal var_cntr_tc: std_logic:='0';
signal var_cntr_value: INTEGER range 0 to NV_REG_WIDTH+2:=0;
signal var_cntr_value_last: INTEGER range 0 to NV_REG_WIDTH+2:=0;
signal nv_reg_dout: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0):=(others => '0');
signal addr: std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1) :=(others => '0');


signal data_rec_nv_reg_we: std_logic;
signal data_rec_nv_reg_din: std_logic_vector(nv_reg_width-1 downto 0);
signal data_rec_recovered_offset: INTEGER RANGE 0 TO NV_REG_WIDTH -1;


signal data_rec_recovered_data: STD_LOGIC_VECTOR( 31 DOWNTO 0);
signal data_rec_type: data_backup_type_t;

component DATA_REC_PROCESS is
generic(
num_outputs: natural;
num_inputs: natural
);

port(
clk: in std_logic;
n_power_reset: in std_logic;
nv_reg_busy:in std_logic;
fsm_nv_reg_state: in fsm_nv_reg_state_t;
data_rec_offset: in INTEGER RANGE 0 TO 2*num_outputs+2+2;
var_cntr_tc: in std_logic;
var_cntr_value: in INTEGER range 0 to NV_REG_WIDTH+2;
var_cntr_value_last: in INTEGER range 0 to NV_REG_WIDTH+2;
nv_reg_dout: in STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
addr: in std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1) :=(others => '0');


data_rec_nv_reg_we: out std_logic;
data_rec_nv_reg_din: out std_logic_vector(nv_reg_width-1 downto 0);
data_rec_recovered_offset: out INTEGER RANGE 0 TO NV_REG_WIDTH -1;


data_rec_recovered_data: inout STD_LOGIC_VECTOR( 31 DOWNTO 0);
data_rec_type: inout data_backup_type_t);

end component;

begin

DATA_REC_PROCESS_comp: DATA_REC_PROCESS
generic map(
num_outputs => num_outputs,
num_inputs => num_inputs

)
port map(
clk => clk,
n_power_reset => n_power_reset,
nv_reg_busy => nv_reg_busy,
fsm_nv_reg_state => fsm_nv_reg_state,
data_rec_offset => data_rec_offset,
var_cntr_tc => var_cntr_tc,
var_cntr_value => var_cntr_value,
var_cntr_value_last => var_cntr_value_last,
nv_reg_dout => nv_reg_dout,
addr => addr,

data_rec_nv_reg_we => data_rec_nv_reg_we,
data_rec_nv_reg_din => data_rec_nv_reg_din,
data_rec_recovered_offset => data_rec_recovered_offset,


data_rec_recovered_data => data_rec_recovered_data,
data_rec_type => data_rec_type
);

tb: process is
begin
wait for 20 ns;
clk <= '0';
wait for 20 ns;
clk <= '1';
wait;
end process;



end Behavioral;
