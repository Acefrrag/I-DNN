----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/14/2022 07:18:26 PM
-- Design Name: 
-- Module Name: routing_w_sum_sig - Behavioral
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

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;
use ieee.fixed_pkg.all;
-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity routing_w_sum_sig is
generic(
     num_outputs: natural := 30;
     num_inputs: natural := 30
);
end routing_w_sum_sig;

architecture Behavioral of routing_w_sum_sig is

type rom_type is array (0 to num_inputs-1) of sfixed(neuron_int_width-1 downto -neuron_frac_width);
type data_out_type is array(0 to num_outputs-1) of sfixed(neuron_int_width-1 downto -neuron_frac_width);
type data_backup_state_type is array(0 to 2*num_outputs+2-1) of std_logic_vector(nv_reg_width-1 downto 0); --data grouping for saving state(weighted_sum, fsm_state, addr_gen)
type weighted_sum_backup_type is array(0 to num_outputs-1) of std_logic_vector(2*(neuron_int_width+neuron_frac_width)-1 downto 0); --this contains the weighted sum elements(64 bits) split up into 2 elements of 32 bits BIG ENDIAN NOTATION
type data_backup_output_type is array(0 to num_outputs) of std_logic_vector(nv_reg_width-1 downto 0); --data gropuing for saving output (the last two wire are not connected to anything)
type backup_type_t is (state, output, nothing);

signal weighted_sum_vect_save,  weighted_sum_vect_rec: weighted_sum_backup_type;
signal data_backup_vect_state_rec, data_backup_vect_state_save: data_backup_state_type;

begin

routing_w_sum_sig: process(weighted_sum_vect_save,data_backup_vect_state_rec) is
begin

--Routing weighted_sum_backup(Output from neuron)
for i in 0 to num_outputs-1 loop
    data_backup_vect_state_save(2*i) <= weighted_sum_vect_save(i)(neuron_frac_width+neuron_int_width-1 downto 0);
    data_backup_vect_state_save((2*i)+1) <= weighted_sum_vect_save(i)(2*(neuron_frac_width+neuron_int_width)-1 downto neuron_frac_width+neuron_int_width);
end loop;
--Routing weighted_sum_recovery(Input to neuron)
for i in 0 to num_outputs-1 loop
    weighted_sum_vect_rec(i)(neuron_frac_width+neuron_int_width-1 downto 0) <= data_backup_vect_state_rec(2*i);
    weighted_sum_vect_rec(i)(2*(neuron_frac_width+neuron_int_width)-1 downto neuron_frac_width+neuron_int_width) <= data_backup_vect_state_rec(2*i+1);
end loop;

end process routing_w_sum_sig;


end Behavioral;
