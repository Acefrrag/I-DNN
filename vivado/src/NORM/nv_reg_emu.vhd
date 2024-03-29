----------------------------------------------------------------------------------
-- Engineer: Simone Ruffini [simone.ruffini@tutanota.com]
-- 
-- Create Date: 06/14/2020 10:36:25 AM
-- Design Name: 
-- Module Name: nv_reg_emu - Behavioral
-- Project Name: NON_VOLATILEPRCEMUL-FPGA
-- Target Devices: xilinx zynq series
-- Tool Versions: 
-- Description: this entity handles the emulation of the nv_reg by modifing the way a normal bram is used by
--              the user. The entity does not depend on the particular nv_reg used because it just modifies the speed of 
--              the bram or the way to access it by introducing a wait signal.
--
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Revision 0.02 - Michele Pio Fragasso - Added Additional Comments and Pin Description
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

use work.COMMON_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;

entity nv_reg_emu is
    Generic(
        MAX_DELAY_NS: INTEGER       --MAX_DELAY_NS: this is the maximum delay that the nv_reg uses to process data. It must be a multiple of the clock cycle duration
    );
    Port ( 
        clk     : IN STD_LOGIC;     --clk           : clock signal
        resetN  : IN STD_LOGIC;     --resetN        : active-on-low reset bit. '0':It reset the emulator registers(counter)
        load_en : IN STD_LOGIC;     --load_en       : signal to request access to the nv_reg. Outside it is latched to bram_en bit
        busy_sig: OUT STD_LOGIC;    --busy_sig      : it anticipates the busy signal by one clock cycle.
        busy    : OUT STD_LOGIC     --busy          : busy signal. It's used to communicate the busyness or the availability of the nv_reg.
                                        --When saving, we look at this value before fetching the next data from the volatile registers and putting 
                                        --When recovering, we look at this value before sampling the output of the non-volatile register nv_reg_dout.
    );
end nv_reg_emu;

architecture Behavioral of nv_reg_emu is
    ----------------------------------------------------
    --      INTERNAL SIGNALS FOR THE SAMPLING DELAY
    ----------------------------------------------------
    constant counter_end_value : INTEGER := get_busy_counter_end_value(MASTER_CLK_PERIOD_NS, MAX_DELAY_NS);
    
    signal counter : INTEGER RANGE 0 TO counter_end_value;
    
begin
    
    
    busy <= '0' when counter = counter_end_value else '1';
    busy_sig <= '0' when counter_end_value <2 else
                '0' when counter >= counter_end_value -1 else '1';
                
    COUNT:process(clk,resetN) is
        variable count: std_logic;
    begin
        if resetn = '0' then
            counter <= counter_end_value;
            count := '0';
        elsif rising_edge(clk) then
            
            if load_en = '1' then
                count :='1';
            end if;
            if(count = '1') then
                counter <= counter + 1;
            end if;
            if( counter = counter_end_value) then
                if(load_en /= '1') then 
                    counter <= counter_end_value;
                    count := '0';
                else
                    counter <= 0;
                end if;
            end if;
        end if;
    end process;
end Behavioral;