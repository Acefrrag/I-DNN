-- Single-Port Block RAM Read-First Mode
-- rams_sp_rf.vhd

-- Revision 0.01 (Michele Pio Fragasso)
-- Added comments.
-- Description:         This entity should infer a block RAM into FPGA according to the vivado design guide: synthesis v 2020.2.
-- Additional Comments: This entity comes from the "Code Example" collection, available from the "Vivado Design Suite User Guide: Synthesis" guide. VIVADO 2020.2 version
--                      1)Impure function InitRamFromFile has been copied from rams_init_file.vhd from the same guide. Function has also been modified.
--                          The return type is not an array of bit_vector but an array of std_logic_vector in order to make it compatible with the already existent architecture.
--                      2)Parameters depth, width and init_file have been added.                     


library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;
library std;
use std.textio.all;

entity rams_sp_rf is
 generic(
    constant ram_depth: natural:=1;                     --ram_depth     :Number of cells inside the ram
    constant ram_width: natural:=1;                     --ram_width     :Number of bits for every cell
    constant init_file:string :="init_ram_file.txt"     --init_file     :String to init_ram_file. Uncomment/Comment the corresponding line to disable/enable initialization.
 );
 port(
  clk  : in  std_logic;                                                         --clk   :Clock Signal                     
  we   : in  std_logic;                                                         --we    :Write Enable Bit
  en   : in  std_logic;                                                         --en    :Enable Bit
  addr : in  std_logic_vector(natural(ceil(log2(real(ram_depth))))-1 downto 0);   --addr  :Address
  di   : in  std_logic_vector(ram_width-1 downto 0);                            --di    :Data input
  do   : out std_logic_vector(ram_width-1 downto 0)                             --do    :Data output
 );
end rams_sp_rf;

architecture syn of rams_sp_rf is
 type RamType is array (0 to ram_depth) of std_logic_vector(31 downto 0);

 impure function InitRamFromFile(RamFileName : in string) return RamType is
  FILE RamFile : text is in RamFileName;
  variable RamFileLine : line;
  variable RAM_content : bit_vector(ram_width-1 downto 0);
  variable RAM : RamType;
 begin
  for I in RamType'range loop
   readline(RamFile, RamFileLine);
   read(RamFileLine, RAM_content);
   RAM(I) := to_stdlogicvector(RAM_content);
  end loop;
  return RAM;
 end function;

--signal RAM : RamType := InitRamFromFile("rams_init_file.data"); --Uncomment/Comment to enable/disable initialization of ram
signal RAM : RamType:=(others => (others => '0'));
begin
 process(clk)
 begin
  if clk'event and clk = '1' then
   if en = '1' then
    if we = '1' then
     RAM(to_integer(unsigned(addr))) <= di;
    end if;
    do <= RAM(to_integer(unsigned(addr)));
   end if;
  end if;
 end process;

end syn;
