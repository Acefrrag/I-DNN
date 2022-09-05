----------------------------------------------------------------------------------
-- Company: University of Trento
-- Engineer: Simone Ruffini
-- 
-- Create Date: 06/26/2020 05:19:23 PM
-- Design Name: 
-- Module Name: var_counter - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: This entity is used to fetch elements to recover from and save into the non-volatile register. It is syncronized with the
-- var_cntr_clk which depends on the intrinsic speed of the non-volatile register.
-- 
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Revision 0.02 Michele Pio Fragasso - Wrote Description
-- Additional Comments: 
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity var_counter is
    Generic(
        MAX         : INTEGER;          --MAX           : unused. It contains the upper limit of the counter
        INIT_VALUE  : INTEGER;          --INIT_VALUE    : This parameter specifies where the counter starts from when the counter is initialized
        INCREASE_BY : INTEGER           --INCREASE_BY   : This paramter specifies the increment at every clk cycle
    );
    Port (
        
        clk         : in STD_LOGIC;                     --clk       :clock signal
        resetn      : in STD_LOGIC;                     --resetn    :active on low reset signal
        INIT        : in STD_LOGIC;                     --INIT      :Init bit to initialize the var_counter_value with INIT_VALUE
        CE          : in STD_LOGIC;                     --CE        :Counter enable bit. '0': Disabled '1': Enabled
        end_value   : in INTEGER RANGE 0 TO MAX;        --end_value :Signal containing the upper counter limit. When counter value passes this value, the counter is reset.
        TC          : out STD_LOGIC;                    --TC        :Counter Terminal Bit. When counter value reaches end value this is set to '1' aknowledging the reach of the last value 
        value       : out INTEGER RANGE 0 TO MAX        --value     .Counter Value. It is increment by INCREASE_BY at every cycle of clk.
    );
end var_counter;

architecture Behavioral of var_counter is
    signal counter : INTEGER RANGE 0 TO MAX;
begin
    -----------------------------------------------------------------------
    --                          Constraints                              --
    -----------------------------------------------------------------------
    value <= counter;
    TC <= '1' when counter = end_value else '0';
    
    COUNT:process(clk,INIT,resetn) is
    begin
        if resetn = '0' then
            counter <= 0;
--            TC <= '0';
        elsif(INIT = '1') then
            counter <= INIT_VALUE;
        elsif rising_edge(clk) then
--            TC <= '0';
            if CE = '1' then
                if(counter >= end_value ) then
                    counter <= 0;
                else
                    counter <= counter + INCREASE_BY;
                end if;
            end if;
--            if( counter = MAX-1 ) then 
--                    TC <= '1';
--            end if;
        end if;
    end process;

end Behavioral;
