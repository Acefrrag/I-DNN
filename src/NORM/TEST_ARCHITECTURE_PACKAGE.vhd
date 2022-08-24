----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 07/02/2020 10:37:15 PM
-- Design Name: 
-- Module Name: TEST_ARCHITECTURE_PACKAGE - Behavioral
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

library work;
use work.I_DNN_package.all;
--Augumented Packages
--use work.COMMON_PACKAGE.all;
--use work.NVME_FRAMEWORK_PACKAGE.all;

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;
use IEEE.MATH_REAL.ALL;


-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

package TEST_ARCHITECTURE_PACKAGE is
    
    
    -- States of a general finate state machine for fsm_nv_reg
    type fsm_nv_reg_state_t is(
        shutdown_s,
        init_s,
        start_data_recovery_s,
        recovery_s,
        data_recovered_s,
        do_operation_s,
        start_data_save_s,
        data_save_s,
        data_saved_s
    );
    
    type fsm_layer_state_t is
    (power_off,
    init,
    recovery,
    idle,
    w_sum,
    b_sum,
    act_log,
    finished,
    data_save_init,
    data_save_init_cmpl,
    data_save);

    type data_backup_type_t is(
    nothing,
    state,
    outputt);
    -- Possible thresholds of the voltage trace
    -- Add more thresholds in case of fsmn_nv_reg_db
    type threshold_t is(
        hazard,
        waring,
        nothing
    );

    constant V_REG_WIDTH: INTEGER := 65536;     -- Numver of words of the volatile register for the volatile architecture
    constant RST_EMU_THRESH: INTEGER := 135;   -- Voltage threshold at which the intemittency emulator will trigger reset_emulator
                                                --> This value must be in the range of ones contained in trace_ROM

end package;
package body TEST_ARCHITECTURE_PACKAGE is 
end package body TEST_ARCHITECTURE_PACKAGE;
