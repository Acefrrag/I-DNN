----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/10/2020 10:43:43 PM
-- Design Name: 
-- Module Name: PWR_CONSUMPTION_VAL_ROM - Behavioral
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

entity pwr_consumption_val_ROM is
    generic(
        NUM_ELEMENTS_ROM : integer;
        MAX_VAL         : integer;
		type_device		: string:="layer"
    );
    port(	
	   	clk       : in	std_logic;
		addr      : in	integer range 0 to NUM_ELEMENTS_ROM;
		data_out  : out	integer range 0 to MAX_VAL - 1
    );
end pwr_consumption_val_ROM;

architecture Behavioral of pwr_consumption_val_ROM is
    type rom_type is array (3 downto 0) of integer range 0 to MAX_VAL-1;
    --The INST_PWR_CONS values are expressed in uW
    signal ROM_layer: rom_type := (
        20, --power state 3
        20,
        100,
        2 --power state 0
    );
	signal ROM_nvreg: rom_type := (
        0, --power state 3 unused
        100,
        75,
        2 --power state 0
    );
	signal ROM_softmax: rom_type := (
        0,
        0,
        0,
        0--unused
    );
begin
    get_data:process (clk) is begin
        if rising_edge(clk) then
			if type_device = "layer" then
				data_out <= ROM_layer(addr);
			elsif type_device = "nvreg" then
				data_out <= ROM_nvreg(addr);
			elsif type_device = "softmax" then
				data_out <= ROM_softmax(addr);	--get the address read it as unsigned and convert to integer to get the value from ROM(integer)
			end if;
		end if;
	end process;

end Behavioral;
