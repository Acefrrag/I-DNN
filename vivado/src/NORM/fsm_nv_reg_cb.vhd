----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 08/10/2020 04:16:02 PM
-- Design Name: 
-- Module Name: fsm_nv_reg_cb - Behavioral
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
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;
use work.COMMON_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;

entity fsm_nv_reg_cb is       
    port ( 
        clk                     : in STD_LOGIC;
        resetN                  : in STD_LOGIC;
        task_status             : in STD_LOGIC;
        thresh_stats            : in threshold_t;
        period_backup_clks      : integer range 0 to 2**31 -1; 
        fsm_state               : out fsm_nv_reg_state_t;
        fsm_state_sig           : out fsm_nv_reg_state_t --used with care (it is the future state of the machine, and it is combinatory so it is prone to glitces)
    );
end fsm_nv_reg_cb;

architecture Behavioral of fsm_nv_reg_cb is
    signal present_state, future_state : fsm_nv_reg_state_t;
    constant max_slack: INTEGER := 10;
    
    signal CB_count_init    : std_logic := '0';                 
    signal CB_count_CE      : std_logic := '0';
    signal CB_count_TC      : std_logic;
    signal CB_count_val     : integer; 
    
    component var_counter is
        Generic(
            MAX         : INTEGER;
            INIT_VALUE  : INTEGER;
            INCREASE_BY : INTEGER
        );
        Port ( 
            clk         : in STD_LOGIC;
            resetN      : in STD_LOGIC;
            INIT        : in STD_LOGIC;
            CE          : in STD_LOGIC;
            end_value   : in INTEGER RANGE 0 TO MAX;
            TC          : out STD_LOGIC;
            value       : out INTEGER RANGE 0 TO MAX
        );
        
        
    end component;
    
begin
    
    COUTER : var_counter 
    generic map(
        MAX         => 2**31 -1,
        INIT_VALUE  => 0,
        INCREASE_BY => 1
    )
    port map(
        clk         => clk,
        resetN      => resetN,
        INIT        => CB_count_init,
        CE          => CB_count_CE,
        end_value   => period_backup_clks,
        TC          => CB_count_TC,
        value       => CB_count_val
    );
    
    FSM_MV_REG_SEQ: process (clk,resetN) is 
    begin
        if resetN = '0' then
            present_state <= shutdown_s;
        elsif rising_edge(clk) then
            present_state <= future_state;
        end if;  
    end process;
    
    
    
    FSM_NV_REG_FUTURE: process(thresh_stats,present_state,task_status,CB_count_TC) is 
    begin
        future_state <= present_state; -- default do nothing
        CB_count_CE <= '0';
        CB_count_init <= '1';
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
                    if thresh_stats = hazard then
                        future_state <= sleep_s;
                    else
                        future_state <= data_recovered_s;
                    end if;
                end if;
            when data_recovered_s =>
                future_state <= do_operation_s;
            when do_operation_s =>
                CB_count_CE <= '1';
                CB_count_init <= '0';
                if(CB_count_TC = '1') then --Counter is full
                    if thresh_stats = hazard then
                    --If the system is in hazard it is not possible to save the state
                    --without risking data corruption. So we keep on executing, we will
                    --save data as soon voltage goes back to normal level
                        CB_count_CE <= '0'; -- The counter must be disabled to preserve the count terminal
                        CB_count_init <= '0';
                        future_state <= sleep_s; 
                        --The system will soon power off so put the device to
                        --sleep to save power
                    else
                        future_state <= start_data_save_s;
                    end if;
                end if;
            when sleep_s =>
                if thresh_stats = hazard then
                    CB_count_CE <= '0';
                    CB_count_init <= '0';
                    future_state <= sleep_s;
                else --thresh_stats = nothing
                    if CB_count_TC = '1' then--We wanted to save but we couldn't
                        future_state <= start_data_save_s;
                    else--We were coming from a recovery operation
                        future_state <= do_operation_s;
                    end if;
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
                future_state <= do_operation_s;
            when others =>
        end case;
    end process FSM_NV_REG_FUTURE;
    
    fsm_state <= present_state;
    fsm_state_sig <= future_state;
    


end Behavioral;
