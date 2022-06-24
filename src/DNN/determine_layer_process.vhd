----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/14/2022 07:59:35 PM
-- Design Name: 
-- Module Name: determine_layer_process - Behavioral
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

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity determine_layer_process is
--  Port ( );
end determine_layer_process;

architecture Behavioral of determine_layer_process is

begin
determine_layer_type: process(fsm_state_save, current_layer) is
--This process determine weather the layer is:
--1) Currently active
--2) Previous of the currently active layer
--3) Idle layer
begin
    if (unsigned(fsm_state_save) = 1) or (unsigned(fsm_state_save) = 2) or (unsigned(fsm_state_save) = 3) then
        mul_sel_backup <= 1;
        --Also, we need to set the number of elements to retrieve from the nv_reg
        --In case it's nothing we oinly need to write to the first element of the nv_reg
        data_rec_offset <= 2*num_outputs+2+2;
    elsif current_layer = '1' then
        mul_sel_backup <= 2;
        data_rec_offset <= num_outputs+2;
    else
        mul_sel_backup <= 3;
        data_rec_offset <= 2;--In this case we don't retrieve any data.
    end if;

end process;

end Behavioral;
