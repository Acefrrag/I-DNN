----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Simone Ruffini
-- 
-- Create Date: 06/30/2020 12:55:22 PM
-- Design Name: 
-- Module Name: nv_reg - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: This entity implements the non-volatile register. It includes the memory block and the emulator.
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Revision 0.02 - Michele Pio Fragasso
-- 1)Added Description and Pin Description as well extensive commentary of signals and line of codes 
-- 2)Added parameter NV_REG_DEPTH. The system was impresicely using NV_REG_WIDTH as NV_REG_DEPTH 
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;
use IEEE.math_real.all;

library work;
use work.NVME_FRAMEWORK_PACKAGE.all;




entity nv_reg is
    Generic(
        MAX_DELAY_NS: INTEGER;      --MAX_DELAY_NS  :This is the delay that the nv_reg uses to process data(writing into and reading from).
        NV_REG_WIDTH: INTEGER;      --NV_REG_WIDTH  :This is the number of bits used to represents an element of the non-volatile register.
        NV_REG_DEPTH: INTEGER       --NV_REG_DEPTH  :This is the number of cells of the nv_reg.
    );
    Port ( 
        clk             : in STD_LOGIC;                                                             --clk               : clock signal
        resetN          : in STD_LOGIC;                                                             --resetN            : active-on-low reset signal. This reset every cell of the nv_reg cycle by cycle. It requires the nv_reg is powered.
        power_resetN 	: in STD_LOGIC;                                                               --power_resetN      : active-on-low power_resetN. This powers-off the nv_reg. Disabling write and read operation        
        --------change from here--------------                                                          
        busy            : out STD_LOGIC;                                                            --busy              :busy signal                                                                 
        busy_sig        : out STD_LOGIC;                                                            --busy_sig          :busy_signal 
        en              : in STD_LOGIC;                                                             --en                :enable bit. This enables write and read operations
        we              : in STD_LOGIC;                                                             --we                :write enable bit. This enables write operations
        addr            : in STD_LOGIC_VECTOR(integer(ceil(log2(real(NV_REG_DEPTH))))-1 DOWNTO 0);  --addr              :address. This is used to fetch the cell to write into and read from
        din             : in STD_LOGIC_VECTOR(31 DOWNTO 0);                                         --din               :data input. Non-volatile register to be written into cell located at "addr"
        dout            : out STD_LOGIC_VECTOR(31 DOWNTO 0)                                         --dout              :data output. Non-volatile register cell content at "addr" located at "addr"
        -------------change to here----------------
    );
end nv_reg;

architecture Behavioral of nv_reg is

------------------------------------NV_REG_EMU_SIGNALS------------------------------------------
signal rstn: STD_LOGIC;
signal busy_internal: STD_LOGIC;
------------------------------------------------------------------------------------------------
------------------------------------NV_REG_CNST-------------------------------------------------
constant bram_addr_width_bit : INTEGER := integer(ceil(log2(real(NV_REG_DEPTH))));
constant depth: natural :=NV_REG_DEPTH;
constant width: natural := NV_REG_WIDTH;
constant init_file: string := "init_ram_file.txt";
------------------------------------------------------------------------------------------------
------------------------------------BRAM_SIGNALS------------------------------------------------
--This signals are directly wired to the BRAM (the storage).
signal bram_en  :STD_LOGIC;                                         
signal bram_we  :STD_LOGIC;  
signal bram_addr:STD_LOGIC_VECTOR(bram_addr_width_bit-1 DOWNTO 0); 
signal bram_din :STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0); 
signal bram_dout:STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);                
------------------------------------------------------------------------------------------------   
------------------------------------RESET_SIGNALS-----------------------------------------------
--This signals are used when the nv_reg has to be reset.
signal bram_en_rst         :STD_LOGIC := '0';                                                       --bram_en_rst   :Enable Bit. It is set to '1' when it is necessary to reset the nv_reg reset 
signal bram_we_rst         :STD_LOGIC := '0';                                                       --bram_we_rst   :Write Enable Bit. It is set when resetting the nv_reg
signal bram_addr_rst       :STD_LOGIC_VECTOR(bram_addr_width_bit-1 DOWNTO 0) := (OTHERS => '0');    --bram_addr_rst :This contains the address used to sequentially rfeset the whole nv_reg, cycle by cycle.
signal bram_din_rst        :STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0):= (OTHERS => '0');            --bram_din_rst  :This contain a sequence of zeroes to reset the nv_reg.
------------------------------------------------------------------------------------------------

-------------------------------------------SINGLE PORT READ FIRST RAM---------------------------------------------
COMPONENT rams_sp_rf IS
generic(
    constant ram_depth: natural;                            
    constant ram_width: natural;
    constant init_file:string
);
PORT (
    clk : IN STD_LOGIC;
    en : IN STD_LOGIC;
    we : IN STD_LOGIC;
    addr : IN STD_LOGIC_VECTOR(bram_addr_width_bit-1 DOWNTO 0);
    di : IN STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0); 
    do : OUT STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0)
  );
END COMPONENT rams_sp_rf;
-----------------------------------------------------------------------
--------------------------------------------------NV_REG_EMULATOR-----------------------------------------------
COMPONENT nv_reg_emu is
    Generic(
        MAX_DELAY_NS: INTEGER 
    );
    Port ( 
        clk     : IN STD_LOGIC;
        resetN  : IN STD_LOGIC;
        load_en : IN STD_LOGIC; 
        busy_sig: OUT STD_LOGIC;
        busy    : OUT STD_LOGIC
    );
end COMPONENT;
-------------------------------------------------------------------------------------------------------------------

begin

BRAM: rams_sp_rf
generic map(
    ram_depth => depth,
    ram_width => width,
    init_file => init_file
)
port map(
    clk => clk,
    di => bram_din,
    do => bram_dout,
    addr => bram_addr,
    en => bram_en,
    we => bram_we
);
EMU: nv_reg_emu
Generic map(
    MAX_DELAY_NS => MAX_DELAY_NS
)
Port map( 
    clk     =>clk,
    resetN  =>rstN,
    load_en =>bram_en,
    busy_sig=>busy_sig,
    busy    =>busy_internal
);

busy<=busy_internal;
--------------------------MUX------------------------------
rstN <= '0' when resetN = '0' else
        '0' when power_resetN = '0' else
        resetN;
bram_en <= bram_en_rst when resetN = '0' else
        '0' when power_resetN = '0' else
        (en or busy_internal);                          --ENABLE HOLD: IMPORTANT keeps the bram active even if the signal was deactivated
bram_we <= bram_we_rst when resetN = '0' else
        '0' when power_resetN = '0' else
        we;
bram_addr <= bram_addr_rst when resetN = '0' else
        (OTHERS => '0') when power_resetN = '0' else
        addr;
bram_din <= bram_din_rst when resetN = '0' else
        (OTHERS => '0') when power_resetN = '0' else
        din;
dout <= bram_dout when resetN = '0' else
        (OTHERS => '0') when power_resetN = '0' else
        bram_dout;
-----------------------------------------------------------
--to use a different bram memory as primitive for the nv_reg
--add combinatory logic on the new ports reaching the memory
--primitive like above. The clock must not be changed.
-------------------place new logic here-------------------- 

----------------------END MUX------------------------------


RST_BRAM: process(clk) is --the reset is syncronous(the nv_reg is reset cycle by cycle)
variable counter : INTEGER RANGE 0 TO (NV_REG_DEPTH -1);
begin
    if(rising_edge(clk)) then
        if(resetN = '0') then
            bram_en_rst <= '1';
            bram_we_rst <= '1';
            
            bram_din_rst <= (OTHERS => '0');
            if(counter < NV_REG_WIDTH ) then
                counter := counter +1;
            elsif(counter = NV_REG_WIDTH ) then
                bram_we_rst <= '0';
                bram_en_rst <= '0';
            end if;
            bram_addr_rst <= std_logic_vector(to_unsigned(counter-1,bram_addr_width_bit));
        else
            bram_we_rst <= '0';
            counter := 0;
        end if;
    end if;
end process;

end Behavioral;
