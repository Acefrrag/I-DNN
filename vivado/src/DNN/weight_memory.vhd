----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso
-- 
-- Create Date: 03/17/2022 11:22:23 AM
-- Design Name: 
-- Module Name: weight_memory - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: This entity implements the weight memory that stores
-- the input weights for a neuron of the DNN.
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


library std;
use std.textio.all;



entity weight_memory is
generic(
    rom_depth: natural := 3;
    rom_width: natural :=16;
    rom_int_width: natural := 4;
    rom_frac_width: natural := rom_width-rom_int_width;
    log_file: string := "test.txt");
port(
    clk: in std_logic;
    addr: in std_logic_vector(0 to natural(ceil(log2(real(rom_depth))))-1);
    dout: out sfixed (rom_int_width-1 downto -rom_frac_width));
end weight_memory;

architecture Behavioral of weight_memory is
-- Types must be defined inside the architecture!!
-- Weight memory
type rom_type is array (0 to rom_depth-1) of sfixed(rom_int_width-1 downto -rom_frac_width);

function makesfixed (bit_in: in bit_vector(rom_width-1 downto 0)) return sfixed is
    variable fixedpoint_s: sfixed(rom_int_width-1 downto -rom_frac_width);
    --variable a: std_logic := 0;
    begin
    for i in fixedpoint_s'range loop
        fixedpoint_s(i) := To_StdULogic(bit_in(i+rom_frac_width));
    end loop;
    return fixedpoint_s;
end function;

impure function initweightmemory(text_in: in string) return rom_type is
  file text_header : text is in text_in;
  variable text_line : line;
  variable line_i : bit_vector(rom_width-1 downto 0);
  variable rom_content : rom_type;
begin
  for i in rom_content'range loop
    readline(text_header, text_line);
    read(text_line, line_i);
    rom_content(i) := makesfixed(line_i);
  end loop;
  file_close(text_header);
  return rom_content;
end function;


--SIGNAL DEFINITION MUST GO INSIDE THE DECLARATIVE PART!!!!
signal ROM: rom_type := initweightmemory(log_file);
signal var1: sfixed(1 downto -rom_width+2);
signal var2: sfixed(1 downto -rom_width+2);
signal mult: sfixed(3 downto -2*rom_width+4);
signal out_p: sfixed(1 downto -rom_width+2) := (others => '0');
begin
dout <= out_p;
read_memory: process (clk) --clk is part of the sensitivity list of the process
begin
    var1 <= to_sfixed(0.5,var1);
    var2 <= to_sfixed(1.9375,var2);
    if falling_edge(clk) then
        out_p <= ROM(to_integer(unsigned(addr)));
        --When you compute a fixed-point multiplication you need to use n1+n2 bits. You may crop the 16lsb bit
        mult <= dout*var1;
    end if;
end process read_memory;
end Behavioral;
