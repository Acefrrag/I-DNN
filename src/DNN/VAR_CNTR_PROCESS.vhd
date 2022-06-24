----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/12/2022 06:06:35 PM
-- Design Name: 
-- Module Name: VAR_CNTR - Behavioral
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


library ieee_proposed;
use ieee_proposed.fixed_pkg.all;


library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;


library work;
use work.I_DNN_package.all;
--Augumented Packages
use work.COMMON_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity VAR_CNTR_PROCESS is
    generic(
    num_outputs: natural := 30;
    num_inputs: natural := 30
    );
    port(
    clk: in std_logic;
    task_status: in std_logic;
    task_status_internal: in std_logic;
    nv_reg_busy_sig: in std_logic;
    var_cntr_init: in std_logic;
    n_power_reset: in std_logic;
    var_cntr_ce: in std_logic;
    var_cntr_end_value: in INTEGER range 0 to NV_REG_WIDTH+2;
    var_cntr_value: out INTEGER range 0 to NV_REG_WIDTH+2;
    var_cntr_value_last: out INTEGER range 0 to NV_REG_WIDTH+2;
    var_cntr_tc: out std_logic;
    var_cntr_clk: out std_logic;
    data_rec_var_cntr_end_value : out INTEGER; 
    data_rec_offset: IN INTEGER RANGE 0 TO 2*num_outputs+2+2;
    data_save_var_cntr_end_value: out INTEGER;
    data_save_v_reg_offset:  in INTEGER RANGE 0 TO V_REG_WIDTH -1
    );
    
end VAR_CNTR_PROCESS;

architecture Behavioral of VAR_CNTR_PROCESS is


component var_counter is
    Generic(
        MAX         : INTEGER;
        INIT_VALUE  : INTEGER;
        INCREASE_BY : INTEGER
    );
    Port (
        
        clk         : in STD_LOGIC;
        resetn      : in STD_LOGIC;
        INIT        : in STD_LOGIC;
        CE          : in STD_LOGIC;
        end_value   : in INTEGER RANGE 0 TO MAX;
        TC          : out STD_LOGIC;
        value       : out INTEGER RANGE 0 TO MAX
    );
end component var_counter;

begin

--------------------------------------------------VAR_CNTR process--------------------------------------------------------------------    

data_rec_var_cntr_end_value <= data_rec_offset + 2;         --the plus two is because a cycle is used to get the first data and then 
                                                                --> the other one just to notify as terminal count cycle
data_save_var_cntr_end_value <= data_save_v_reg_offset + 2; --should be + 1 just for the terminal count clk cycle but +2 because on how the var_cntr_clk ticks
                                                                --> beacuase of this an extra clk cycle will be wasted

    
VAR_CNTR_CLK_GEN: process(clk,task_status) is
begin
if(task_status_internal = '0') then
   var_cntr_clk <= '1';
elsif(rising_edge(clk)) then
     var_cntr_clk <= '0';
        if(nv_reg_busy_sig = '0' and var_cntr_clk /='1' ) then
            var_cntr_clk <= '1';
        end if;
    end if;
end process VAR_CNTR_CLK_GEN;
    
VAR_CNTR: var_counter
Generic map(
    MAX         => num_outputs+2,
    INIT_VALUE  => 0,
    INCREASE_BY => 1
)              
Port map(          
    clk         => var_cntr_clk,
    resetn      => n_power_reset,
    INIT        => var_cntr_init,
    CE          => var_cntr_ce,
    end_value   => var_cntr_end_value, 
    TC          => var_cntr_tc,
    value       => var_cntr_value
);

VAR_CNTR_LAST_VAL: process(task_status_internal,var_cntr_value) is
    variable var_cntr_value_last_var: INTEGER range 0 to NV_REG_WIDTH+2;
begin
   if(task_status_internal = '0') then
        var_cntr_value_last<= 0;
        var_cntr_value_last_var := var_cntr_value;
    else --changes on val_cntr_value events
        var_cntr_value_last <= var_cntr_value_last_var;
        var_cntr_value_last_var := var_cntr_value;
    end if;
end process VAR_CNTR_LAST_VAL;  

end Behavioral;
