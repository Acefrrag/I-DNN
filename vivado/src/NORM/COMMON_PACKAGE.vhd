----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 05/15/2020 07:14:26 PM
-- Design Name: 
-- Module Name: COMMON_PACKAGE - Behavioral
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
use IEEE.NUMERIC_STD.ALL;
use IEEE.MATH_REAL.ALL; --for log2 and ceil
-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

use work.TEST_ARCHITECTURE_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;

package COMMON_PACKAGE is
    type POWER_APPROX_COUNTER_TYPE is array (integer range <>) of INTEGER range 0 to 2**PWR_APPROX_COUNTER_NUM_BITS - 1;
   

    constant nv_reg_addr_width_bit              : INTEGER := integer(ceil(log2(real(NV_REG_depth))));   -- This value is autocomputed and is used inside the code for faster writing
    constant v_reg_addr_width_bit               : INTEGER := integer(ceil(log2(real(V_REG_WIDTH))));    -- This value is autocomputed and is used inside the code for faster writing

constant MASTER_CLK_SPEED_HZ: INTEGER := 25000000;
                                                                        -- !!!!!!!!! If the sytem master clk changes, change this value to the same number !!!!!!!!
                                                                         -- This is the period of the var_counter clock. Which is always twice as slow as the master clock.
    constant MASTER_CLK_PERIOD_NS               : INTEGER := (1e9/MASTER_CLK_SPEED_HZ); -- Master clk period, this value is autocomputed.
    
    constant FRAM_MAX_DELAY_NS                  : INTEGER := MASTER_CLK_PERIOD_NS*5;
                                                                                        -- !!!!! By changing this value the behaviour of non volatile registers changes too !!!!!

    pure function get_busy_counter_end_value(
        input_clk_period : INTEGER;  --in nannoseconds
        max_delay_time: INTEGER  --in nannoseconds
    ) return INTEGER;
end package;

library IEEE;
use ieee.math_real.all;
package body COMMON_PACKAGE is 
    -- This function calculates the end value used by the counter used in nv_reg_emu
    pure function get_busy_counter_end_value(
            input_clk_period : INTEGER; -- period in nanoseconds of the input clk that the nv_reg takes
            max_delay_time: INTEGER     -- delay in nanoseconds at wich nv_reg will output its value after a request
        ) return INTEGER is
    begin
        assert (max_delay_time > 0)
            report "nv_reg dealy time = 0" severity Failure;
        if(max_delay_time <= input_clk_period) then--if the fram is as fast as the clk or faster 
            return 0; --then nothing to do 
        else
            return  integer(ceil(real(max_delay_time)/real(input_clk_period))) - 1; --return the upper bound if the delay is greater then the clk period
        end if;
    end function;
end package body COMMON_PACKAGE;