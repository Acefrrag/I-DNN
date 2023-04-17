library ieee;
use ieee.std_logic_1164.all;
use ieee.math_real.all;
use ieee.numeric_std.all;

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library std;
use std.textio.all;

library work;
use work.I_DNN_package.all;

entity Sigmoid is
generic(
	constant inputdataWidth: natural := DNN_sigmoid_inputdata_Width;
	constant inputdataIntWidth: natural := DNN_sigmoid_inputdata_IntWidth;
	constant outputdataWidth: natural := DNN_neuron_inout_Width;
	constant outputdataIntWidth: natural := DNN_neuron_inout_IntWidth;
	constant Sigfilename: string := "SigContent.txt"
);
port(
	data_in		: in sfixed(inputdataIntWidth-1 downto -(inputdataWidth-inputdataIntWidth));
	data_out	: out sfixed(outputdataIntWidth-1 downto -(outputdataWidth-outputdataIntWidth))
);
end Sigmoid;


Architecture Behavioral of Sigmoid is


type rom_type is array (0 to 2**DNN_sigmoid_inputdata_Width-1) of sfixed(outputdataIntWidth-1 downto -(outputdataWidth-outputdataIntWidth));


impure function makesfixed (bit_in: in bit_vector(outputdataWidth-1 downto 0)) return sfixed is
	variable outputdataFracWidth: natural := outputdataWidth-outputdataIntWidth;
    variable fixedpoint_s: sfixed((outputdataIntWidth)-1 downto -(outputdataFracWidth));
    begin
    for i in fixedpoint_s'range loop
        fixedpoint_s(i) := To_StdULogic(bit_in(i+(outputdataFracWidth)));
    end loop;
    return fixedpoint_s;
end function;

impure function genSigROM(filename: string) return rom_type is

file file_header: text open read_mode is filename;
variable text_line: line;
variable bit_line: bit_vector(outputdataWidth-1 downto 0);
variable sigmoid_content: rom_type := (others => (others => '0'));
begin
	for i in sigmoid_content'range loop
		readline(file_header, text_line);
		read(text_line, bit_line);
		sigmoid_content(i) := makesfixed(bit_line);
	end loop;
	return sigmoid_content;
end function;

signal sigmoid_ROM: rom_type := genSigROM(Sigfilename);
--signal data_in_slv: std_logic_vector(data_in'length-1 downto 0);
--signal data_in
signal data_in_integer: integer:=0; --Signed integer(2's complement) representation of the fixed-point representation of the sigmoid input.
signal addr: std_logic_vector(inputdataWidth-1 downto 0) := (others => '0');

begin

--data_in_slv <= to_slv(data_in);
--data_in_signed <= signed(data_in_slv);
--data_in_integer <= to_integer(data_in_signed);		--Used to generate the address to the Sigmoid ROM
data_in_integer <= to_integer(signed(to_slv(data_in)));
data_out <= Sigmoid_ROM(to_integer(unsigned(addr)));

--SIGMOID LUT pointer
--It is generated from data_in_integer:
--1) If the number representation is 0, then then address is the middle, that is 2^(inputdataWidth-1).
--2) If the number representation is the smallest possible that is -2^(inputdataWidth-1), the address is 0, because that corresponds to the smallest abscissa value.
--3) If the number representation is the highest possible, that is 2^(inputdataWidth-1)-1, the address is the maximum, that is 2^(inputdataWidth)-1.
--From these two the formula is inferred. But it is necessary to convert the number into his representation.
addr <=  std_logic_vector(to_unsigned(data_in_integer+2**(inputdataWidth-1), addr'length));



--addr_finder: process(CLK) is
--addr <=  std_logic_vector(to_unsigned(data_in_integer+2**(inputdataWidth-1), addr'length));
--begin
--if rising_edge(CLK) then
--	if data_in_integer >= 0 then
--		--if the number representation is >= 0 it means that we have to select sigmoid values 
--		addr <= std_logic_vector(to_unsigned(data_in_integer+2**(inputdataWidth-1), addr'length));
--	else
--		addr <= std_logic_vector(to_unsigned(data_in_integer+2**(inputdataWidth-1), addr'length));
--	end if;
--end if;
--end process; */




end Behavioral;