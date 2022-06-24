----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso 
-- 
-- Create Date: 03/20/2022 04:04:40 PM
-- Design Name: 
-- Module Name: FSM_neuron - Behavioral
-- Project Name: DNN
-- Target Devices: 
-- Tool Versions: 
-- Description: FSM to control the pipelined neuron.
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

library work;
use work.TEST_ARCHITECTURE_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.COMMON_PACKAGE.all;


entity I_FSM_layer is
generic (
num_outputs: natural := 30;
rom_depth: natural := 3);--the number of summations in the weighted sum will be 16-1=15
port(
    --ORIGINARY PORTS
    --INPUTS
    clk: in std_logic;
    addr_TC: in std_logic;                                          --addr_TC           :This bit indicates if we are feeding the neuron with the last input
    start: in std_logic;                                            --start             :This signal initiate the neuron computation
    --OUTPUTS
    sum_reg_rst: out std_logic;                                     --sum_reg_rst       :This bit resets the weighted sum register
    mul_sel: out std_logic;                                         --mul_sel           :This signal decides weather to add up the product w_i*x_i or the bias b
    out_v: out std_logic;                                           --out_v             :This signal aknowledge the output is valid
    update_out: out std_logic;                                      --update_out        :This update the output of the neuron, since it is necessary to  
    addr_in_gen_rst: out std_logic;                                 --addr_in_gen_rst   :
    --ADDED PORTS
    --INPUTS
    n_power_rst: in std_logic;                                      --n_power_rst
    data_rec_busy: in std_logic;                                    --data_rec_busy
    fsm_nv_reg_state: in fsm_nv_reg_state_t;                        --fsm_nv_reg_state
    fsm_state_rec: in std_logic_vector(0 to nv_reg_width-1);        --fsm_state_rec             :To recover the state of the fsm
    data_rec_recovered_offset: in integer range 0 to num_outputs+1; --data_rec_recovered_offset :This contains the address 
    data_rec_type: in data_backup_type_t;                           --data_rec_type             :This value must be held from the outer module during the whole recovery/save process
    data_save_type: in data_backup_type_t;                          --data_save_type            :
    --Output pins
    s_r: out std_logic_vector (0 to 2*num_outputs+1);               --s_r               :activation pins for recovery of the state
    o_r: out std_logic_vector (0 to num_outputs+1);                 --o_r               :activation pins for recovery of the outputs (last 2 are unused)
    addra: out integer range 0 to num_outputs+2;                    --addra             :
    fsm_state_save: out std_logic_vector(nv_reg_width-1 downto 0);      --fsm_state_save    :To save the state of the fsm of the layer, it is also used to determine the type of save 
    fsm_pr_state: out fsm_layer_state_t;                            --fsm_pr_state      :It contains the present state of the fsm.
    sum_reg_en: out std_logic                                       --sum_reg_en        :This is used to enable the cumulative sum register
    );
end I_FSM_layer;

architecture Behavioral of I_FSM_layer is
--Declarative Part
signal pr_state, nx_state, state_backup_rec, state_backup_save: fsm_layer_state_t := idle;
signal out_val: std_logic := '0';
constant number: integer range 0 to 5:=1;


begin
    fsm_pr_state <=pr_state;
    
    state_backup_eval: process(fsm_state_rec, pr_state) is
    begin
        --Logic for recovery. State_backup_rec is used to recover the
        --fsm state
        if unsigned(fsm_state_rec) = 0 then
            state_backup_rec <= idle;
        elsif unsigned(fsm_state_rec) = 1 then
            state_backup_rec <= w_sum;
        elsif unsigned(fsm_state_rec) = 2 then
            state_backup_rec <= b_sum;
        elsif unsigned(fsm_state_rec) = 3 then
            state_backup_rec <= act_log;
        elsif unsigned(fsm_state_rec) = 4 then
            state_backup_rec <= finished;
        else
            --When we enter the recovery process the fsm evaluate the
            --state to start the computation.           
            state_backup_rec <= state_backup_rec;
        end if;
        --Logic for saving. state_backup_save is evaluated in order to
        --determine what to write into the nv_reg
        --fsm_state_save <= (others => '0');
        if pr_state = idle then
            fsm_state_save <= std_logic_vector(to_unsigned(0,fsm_state_save'length));
            state_backup_save <= pr_state;
        elsif pr_state = w_sum then
            fsm_state_save <= std_logic_vector(to_unsigned(1,fsm_state_save'length));
            state_backup_save <= pr_state;
        elsif pr_state = b_sum then
            fsm_state_save <= std_logic_vector(to_unsigned(2,fsm_state_save'length));
            state_backup_save <= pr_state;
        elsif pr_state = act_log then
            fsm_state_save <= std_logic_vector(to_unsigned(3,fsm_state_save'length));
            state_backup_save <= pr_state;
        elsif pr_state = finished then
            fsm_state_save <= std_logic_vector(to_unsigned(4,fsm_state_save'length));
            state_backup_save <= pr_state;
        else
            --1)When we start the data save process,
            --state_backup_save will be containing
            --the last state of the layer before
            --starting saving.
            --2)In the same way after we enter the save process
            --The fsm remembers what to write inside the nv_reg.
            fsm_state_save <= fsm_state_save;
            state_backup_save <= state_backup_save;
        end if;
end process;

    out_v <= out_val;
    state_reg: process(clk,n_power_rst)
    begin
        if n_power_rst = '0' then
            pr_state <= power_off;
        elsif rising_edge(clk) then
            pr_state <= nx_state;
        end if;
    end process state_reg;
    
    output: process(all)
    --Outputs of this FSM are:
    --mul_sel: Multiplexer Selector: to select between weighted sum or bias
    --out_v: Output Data Valid: to aknowledge the data coming out the neruon is ready
    --sum_reg_rst: To reset the weighted sum register
    --update_out: To update the neuron output
    --addr_in_gen_en: To enable the address generator.
    begin
    --################ V_REG DEFAULTS
    s_r <= (others => '0');
    o_r <= (others => '0'); 
    addra <= 0;
	--###############################
    case pr_state is
        when power_off =>
        when init =>
            mul_sel <= '0';
            out_val <= '0';
            sum_reg_rst <= '1';
            update_out <= '0';
            addr_in_gen_rst <= '0';
        when recovery =>
            mul_sel <= '0';
            out_val <= '0';
            sum_reg_rst <= '0';
            update_out <= '0';
            addr_in_gen_rst <= '0';
            --Augumented FSM Outputs
            if fsm_nv_reg_state = recovery_s then
                if data_rec_busy = '1' then
                    --if the data recovery has ended then change state  
                    --The data to recover and where to put it depends
                    --on weather we saved the state of the layer or just the output
                    --LAYER STATE RECOVERY
                    --If we are recovevring the state the input address ranges from 0 to num_outputs+1 (fsm_state + addr_gen_addr)
                    addra <= data_rec_recovered_offset;
                    case data_rec_type is
                    when nothing =>
                        o_r <= (others => '0');
                        s_r <= (others => '0');
                    when state =>
                        s_r(addra-1) <= '1';--addra 0 to 2*num_outputs+1. This represents an issue because the state_recovery(s_r) signal is intended to be for num_outputs neurons                 
                    when outputt =>
                        o_r(addra-1) <= '1';--addr 0 to num_outputs+1
                    end case;
                    --LAYER OUTPUT RECOVERY)
                    --If we are recovering the output the input address range from 0 to num_outputs-1
                    -- enable and write to V_REG
                    --ena <= '1';                    
                    -- If we're recovering the 
                end if;
            end if;
        when idle =>
            mul_sel <= '0';
            out_val <= '0';
            sum_reg_rst <= '1';
            update_out <= '0';
            addr_in_gen_rst <= '1';         
        when w_sum =>
            mul_sel <= '0';
            out_val <= '0';
            sum_reg_rst <= '0';
            update_out <= '0';
            addr_in_gen_rst <= '0';
        when b_sum =>
            mul_sel <= '1';
            out_val <= '0';
            sum_reg_rst <= '0';
            update_out <= '0';      
            addr_in_gen_rst <= '1';  
        when act_log =>
            mul_sel <= '0';
            out_val <= '0';
            sum_reg_rst <= '0';
            update_out <= '0';
            addr_in_gen_rst <= '1';
        when finished =>
            mul_sel <= '0';
            out_val <= '1';
            sum_reg_rst <= '0';
            update_out <= '1';
            addr_in_gen_rst <= '1';
        when data_save_init =>
            --default values
        when data_save_init_cmpl =>
            --default values
        when data_save =>
            --default values
    end case;
    end process output;
    
    next_state: process(all)
    begin
    --default state
    nx_state <= pr_state;
    case pr_state is
       when power_off =>
            nx_state <= init;
       when init =>
            if fsm_nv_reg_state = start_data_recovery_s and data_rec_busy = '1' then
               nx_state <= recovery;
            else
               nx_state <= init;         
            end if;
        when recovery =>
            if fsm_nv_reg_state = data_recovered_s then
                nx_state <= state_backup_rec; --The fsm took the state from the nv_reg
            else
                nx_state <= recovery;
            end if;
        when idle =>
            --next
            if fsm_nv_reg_state = do_operation_s then
                if start = '1' then
                    nx_state <= w_sum;
                else
                    nx_state <= idle;
                end if;
            else
                nx_state <= data_save_init;
            end if;
       when w_sum =>
            if fsm_nv_reg_state = do_operation_s then
                if addr_TC = '1' then --we stopped feeding inputs
                      nx_state <= b_sum;
                else
                      nx_state <= w_sum;
                end if;
             else 
                nx_state <= data_save_init;
             end if;
        when b_sum =>
            if fsm_nv_reg_state = do_operation_s then
                nx_state <= act_log;
            else
                nx_state <= data_save_init;
            end if;
        when act_log =>
            if fsm_nv_reg_state = do_operation_s then
                nx_state <= finished;
            else
                nx_state <= data_save_init;
            end if;
        when finished =>
            if fsm_nv_reg_state = do_operation_s then
                nx_state <= idle;
            else 
                nx_state <= data_save_init;
            end if;
        when data_save_init =>
            nx_state <= data_save_init_cmpl;
        when data_save_init_cmpl =>
            nx_state <= data_save;
        when data_save =>
            if fsm_nv_reg_state = do_operation_s then
                nx_state <= state_backup_save;
            end if;
        end case;        
    end process next_state;
end Behavioral;
