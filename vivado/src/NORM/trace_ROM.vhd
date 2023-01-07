----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 05/17/2020 03:56:37 PM
-- Design Name: 
-- Module Name: trace_ROM - Behavioral
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

library std;
use std.textio.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity trace_ROM is
    generic(
        NUM_ELEMNTS_ROM : integer;
        MAX_VAL         : integer
    );
    port(	
	   	clk       : in	std_logic;
		addr      : in	integer range 0 to NUM_ELEMNTS_ROM - 1;
		data_out  : out	integer range 0 to MAX_VAL
    );
end trace_ROM;



architecture Behavioral of trace_ROM is
    type rom_type is array (0 to NUM_ELEMNTS_ROM - 1) of integer range 0 to  MAX_VAL;

    function init_trace_ROM(file_name: in string) return rom_type is
        file text_header : text is in file_name;--Open the file with filename path
        variable voltage_i: integer range 0 to MAX_VAL;
        variable line_i: line;
        variable voltage_trace_content: rom_type;
        begin
            for i in rom_type'range loop
                readline(text_header, line_i);
                read(line_i, voltage_i);
                voltage_trace_content(i) := voltage_i;
            end loop;
        return voltage_trace_content;       
    end function;
    
    
    --signal ROM: rom_type := init_trace_ROM("voltage_traces/I_DNN_trace_complete_4layers.txt");
    signal ROM: rom_type := init_trace_ROM("voltage_traces/I_layer_trace_complete.txt");
    --signal ROM: rom_type := init_trace_ROM("voltage_traces/I_DNN_trace_complete.txt");
    begin
    
    
    get_data:process (clk) is
	begin
		if rising_edge(clk) then
			data_out <= ROM(addr);	--get the address read it as unsigned and convert to integer to get the value from ROM(integer)
		end if;
	end process;

end Behavioral;
