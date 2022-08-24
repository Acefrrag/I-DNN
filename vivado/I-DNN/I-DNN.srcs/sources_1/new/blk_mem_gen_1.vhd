----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 07/13/2022 01:31:35 PM
-- Design Name: 
-- Module Name: blk_mem_gen_1 - Behavioral
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


--Following libraries have to be used
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library std;
use std.textio.all;

library work;
use work.NVME_FRAMEWORK_PACKAGE.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity blk_mem_gen_1 is
generic(
    constant depth: natural:=1;
    constant width: natural:=1;
    constant ram_performance: string:="LOW_LATENCY";
    constant init_file:string :="init_ram_file.txt"  
);
port(
    clka:   in std_logic;                                               -- Clock
    ena:    in std_logic;                                               -- RAM Enable, for additional power savings, disable port when not in use        
    wea:    in std_logic;                                               -- Write enable
    addra:  in std_logic_vector(bram_addr_width_bit-1 DOWNTO 0);        -- Address bus, width determined from RAM_DEPTH
    dina:   in STD_LOGIC_VECTOR(31 DOWNTO 0);                           -- RAM input data
    rsta:   in std_logic;                                               -- Output reset (does not affect memory contents)                     
    regcea: in std_logic;                                               -- Output register enable      
    douta:  out STD_LOGIC_VECTOR(31 DOWNTO 0)                          -- RAM output data
);
end blk_mem_gen_1;

architecture Behavioral of blk_mem_gen_1 is

--Insert the following in the architecture before the begin keyword
--  The following function calculates the address width based on specified RAM depth
function clogb2( depth : natural) return integer is
variable temp    : integer := depth;
variable ret_val : integer := 0;
begin
    while temp > 1 loop
        ret_val := ret_val + 1;
        temp    := temp / 2;
    end loop;

    return ret_val;
end function;

-- Note :
-- If the chosen width and depth values are low, Synthesis will infer Distributed RAM.
-- C_RAM_DEPTH should be a power of 2

constant C_RAM_WIDTH : integer := width;                                                   -- Specify RAM data width
constant C_RAM_DEPTH : integer := depth;                                                   -- Specify RAM depth (number of entries)
constant C_RAM_PERFORMANCE : string := ram_performance;                  -- Select "HIGH_PERFORMANCE" or "LOW_LATENCY" 
constant C_INIT_FILE : string := "insert_the_correct_init_file.txt";
signal douta_reg : std_logic_vector(C_RAM_WIDTH-1 downto 0) := (others => '0');           -- RAM output data when RAM_PERFORMANCE = HIGH_PERFORMANCE
                                         -- Specify name/location of RAM initialization file if using one (leave blank if not)

type ram_type is array (C_RAM_DEPTH-1 downto 0) of std_logic_vector (C_RAM_WIDTH-1 downto 0);      -- 2D Array Declaration for RAM signal
signal ram_data : std_logic_vector(C_RAM_WIDTH-1 downto 0) ;--this contains one element of the ram

-- The folowing code either initializes the memory values to a specified file or to all zeros to match hardware

function initramfromfile (ramfilename : in string) return ram_type is
file ramfile	: text is in ramfilename;
variable ramfileline : line;
variable ram_name	: ram_type;
variable bitvec : bit_vector(C_RAM_WIDTH-1 downto 0);
begin
    for i in ram_type'range loop
        readline (ramfile, ramfileline);
        read (ramfileline, bitvec);
        ram_name(i) := to_stdlogicvector(bitvec);
    end loop;
    return ram_name;
end function;

function init_from_file_or_zeroes(ramfile : string) return ram_type is
begin
    if ramfile = "<Init File Name>" then
        return InitRamFromFile("<Init File Name>") ;
    else
        return (others => (others => '0'));
    end if;
end;

-- Define RAM
signal ram_name : ram_type := init_from_file_or_zeroes(C_INIT_FILE);


begin


--Insert the following in the architecture after the begin keyword
process(clka)
begin
    if(clka'event and clka = '1') then
        if(ena = '1') then
            if(wea = '1') then
                ram_name(to_integer(unsigned(addra))) <= dina;--If wea='0' ram must be unresponsive.
            end if;
            ram_data <= ram_name(to_integer(unsigned(addra)));
        else
            ram_data <= (others => '0');--ram is disabled. Ram must be unresponsive.
        end if;
    end if;
end process;

--  Following code generates LOW_LATENCY (no output register)
--  Following is a 1 clock cycle read latency at the cost of a longer clock-to-out timing

no_output_register : if C_RAM_PERFORMANCE = "LOW_LATENCY" generate
    douta <= ram_data;
end generate;

--  Following code generates HIGH_PERFORMANCE (use output register)
--  Following is a 2 clock cycle read latency with improved clock-to-out timing

output_register : if C_RAM_PERFORMANCE = "HIGH_PERFORMANCE"  generate
process(clka)
begin
        if(clka'event and clka = '1') then
            if(rsta = '1') then
                douta_reg <= (others => '0');
            elsif(regcea = '1') then
                douta_reg <= ram_data;
            end if;
        end if;
end process;
douta <= douta_reg;
end generate;


end Behavioral;


--  Xilinx Single Port Read First RAM
--  This code implements a parameterizable single-port read-first memory where when data
--  is written to the memory, the output reflects the prior contents of the memory location.
--  If the output data is not needed during writes or the last read value is desired to be
--  retained, it is suggested to use Single Port.No Change Mode Template as it is more power
--  efficient.
--  If a reset or enable is not necessary, it may be tied off or removed from the code.
--  Modify the parameters for the desired RAM characteristics.






