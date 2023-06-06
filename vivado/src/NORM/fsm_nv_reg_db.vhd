----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Simone Ruffini
-- 
-- Create Date: 06/25/2020 01:06:12 PM
-- Design Name: 
-- Module Name: fsm_nv_reg_db - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: The finite state machine of the non-volatile register is the enity which supervises the operation of the volatile
-- architecture(VARC). It sends imperative commands to the VARC which mainly are:
-- 1) do_operation
-- 2) save state to the nv_reg
-- 3) recover state from the nv_reg
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Revision 0.02 - Michele Pio Fragasso - Added Description and Pin description
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

use IEEE.NUMERIC_STD.ALL;


use work.COMMON_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;

entity fsm_nv_reg_db is
    port ( 
        clk                     : in STD_LOGIC;             --clk           : clock signal
        resetN                  : in STD_LOGIC;             --resetN        : Active-on-low reset signal
        thresh_stats            : in threshold_t;           --thresh_stats  : vector containing the hazard and the power-off threshold
        task_status             : in STD_LOGIC;             --task_status   : VARC Task status for recovery and save operation. '0': REC/SAVE operation completed '1': REC/SAVE opration 
        fsm_state               : out fsm_nv_reg_state_t;   --fsm_state     : this the state of the finite state machine. It is used to send the imperative commands to the VARC
        fsm_state_sig           : out fsm_nv_reg_state_t    --fsm_state_sig : used with care (it is the future state of the machine, and it is combinatory so it is prone to glitces)
    );
end fsm_nv_reg_db;

architecture Behavioral of fsm_nv_reg_db is
    
signal present_state, future_state : fsm_nv_reg_state_t;
constant max_slack: INTEGER := 0;--The operation slack disable the hazard as long as the volatile architecture didn't carry a certain amount of operations(which is the max_slack value)
begin
    
FSM_NV_REG_DB_SEQ: process (clk,resetN) is 
variable do_operation_s_slack: INTEGER RANGE 0 to max_slack;
begin
    if resetN = '0' then
        present_state <= shutdown_s;
        do_operation_s_slack := 0;
    elsif rising_edge(clk) then
        present_state <= future_state;
        if(present_state = do_operation_s AND do_operation_s_slack < max_slack ) then
            present_state <= do_operation_s;
            do_operation_s_slack := do_operation_s_slack + 1;
        else
            do_operation_s_slack := 0;
        end if;
    end if;  
end process;


FSM_NV_REG_DB_FUTURE: process(present_state,thresh_stats,task_status) is 
begin
    future_state <= present_state; -- default do nothing
    case present_state is
        when shutdown_s =>
            future_state <= init_s;
        when init_s =>
            if thresh_stats = hazard then
                future_state <= init_s;
            else
                future_state <= start_data_recovery_s;
            end if;
        when start_data_recovery_s =>
            if (task_status = '1') then
                future_state <= recovery_s;
            end if;
        when recovery_s =>
            if (task_status = '0') then
                future_state <= data_recovered_s;
--                if thresh_stats = hazard then
--                    future_state <= sleep_s;
--                else
--                    future_state <= data_recovered_s;
--                end if;
            end if;
        when data_recovered_s =>
            --edited Michele Fragasso. To avoid nv_reg corrusption
            --future_state <= do_operation_s;
            if thresh_stats = hazard then
                future_state <= sleep_s;
            else
                future_state <= do_operation_s;
            end if;
        when sleep_s =>
            if (thresh_stats = hazard) then
                future_state <= sleep_s;
            else
                future_state <= do_operation_s;
            end if;
        when do_operation_s =>
            if(thresh_stats = hazard) then
                future_state <= start_data_save_s;
            end if;
        when start_data_save_s =>
            if(task_status = '1') then
                future_state <= data_save_s;    
            end if;
        when data_save_s =>
            if ( task_status = '0' ) then
                future_state <=  data_saved_s;
            end if;
        when data_saved_s =>
            --edited by Fragasso. To avoid data corruption
            if (thresh_stats = hazard) then
                future_state <= sleep_s;
            else
                future_state <= do_operation_s;
            end if;
        when others =>
    end case;
end process FSM_NV_REG_DB_FUTURE;

fsm_state <= present_state;
fsm_state_sig <= future_state;
    
end Behavioral;
-------------------------------------------------------------------------------------------------------------------------------------

