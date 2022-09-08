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
    out_v: out std_logic;                                           --out_v             :This signal aknowledges the output is valid
    update_out: out std_logic;                                      --update_out        :This update the output of the neuron, since it is necessary to  
    addr_in_gen_rst: out std_logic;                                 --addr_in_gen_rst   :This bit 
    --ADDED PORTS
    --INPUTS
    out_v_set: in integer range 0 to 3;                             --out_v_set                 :Used to reset the validity bit of the layer. 1:It means that the output of the next layer has been computed, and this layer has to reset it out_v to '0' 2: Hold the out_v bit value(This is when the layer still has to be used, has already been used, it's being used by the next layer) 3:Set out_v to '1'. This is when the output has been recovered from the nv_reg, so this aknowledges that the layer is still being used.
    n_power_rst: in std_logic;                                      --n_power_rst               :Active-on-low power reset pin
    data_rec_busy: in std_logic;                                    --data_rec_busy             :data_rec_busy pin 
    data_save_busy: in std_logic;                                   --data_save_busy            :data_save_busy pin
    fsm_nv_reg_state: in fsm_nv_reg_state_t;                        --fsm_nv_reg_state          :State of fsm of the nv_reg state. Contains the imperative command from the fsm_nv_rev.
    data_rec_recovered_offset: in integer range 0 to num_outputs+1; --data_rec_recovered_offset :This contains the offset reached (counting from the start address). It's used to access the volatile registers of the layer.
    data_rec_type: in data_backup_type_t;                           --data_rec_type             :It contains the type of recovery to perform. 'nothing', 'internal' or 'outputs'. This value must be held during the whole recovery/save process
    fsm_state_en_rec: in std_logic;                                 --fsm_state_en_rec          :pin to enable sampling of the fsm state
    fsm_state_rec: in std_logic_vector(nv_reg_width-1 downto 0);    --fsm_state_rec             :It contains the enconding of the state of layer fsm. It is used to resume the state of the layer after recovering data. 
    --OUTPUT
    output_en_rec_vect: out std_logic_vector (0 to num_outputs+1);  --output_en_rec_vect        :Collection of pins to enable recovery by layer's neurons of their output. 
    internal_en_rec_vect: out std_logic_vector (0 to num_outputs+1);--internal_en_rec_vect      :Collection of pins to enable recover by layer's neurons of their internal registers.
    save_state_selector: out integer range 0 to 3;                  --save_state_selector       :Selector to correctly route the data to be saved when saving the internal registers of the layer.'0' The
    addra: out integer range 0 to num_outputs+2;                    --addra                     :This address is used to fetch data from the volatile registers of the layer (which are supposed to be saved into the nv_reg)
    fsm_state_save: out std_logic_vector(nv_reg_width-1 downto 0);  --fsm_state_save            :The encoded state of the fsm of the layer, it is also used to determine the type of save to perform
    fsm_pr_state: out fsm_layer_state_t;                            --fsm_pr_state              :It contains the present state of the fsm. it is used by the power_approzimation units 
    reg_en: out std_logic                                           --reg_en                    :This is used to enable/disable the register, ,including this fsm machine
    );
end I_FSM_layer;

architecture Behavioral of I_FSM_layer is
--Declarative Part
signal nx_state, state_backup_rec, state_backup_save: fsm_layer_state_t := power_off;
signal pr_state: fsm_layer_state_t:=power_off;
signal out_val: std_logic := '0';
signal fsm_state_save_internal:  std_logic_vector(nv_reg_width-1 downto 0);
constant number: integer range 0 to 5:=1;

begin
    
fsm_pr_state <= pr_state;
fsm_state_save <= fsm_state_save_internal;

state_backup_eval: process(all) is
begin
    if n_power_rst = '0' then
        state_backup_rec <= idle;
        state_backup_save <= idle;
        fsm_state_save_internal <= std_logic_vector(to_unsigned(0,fsm_state_save'length));
    else
        --Logic for saving.
        --When saving the state, the state to be saved is the one that the layer is supposed to evolve to if there was no hazard.
        --if rising_edge(clk) then
            if pr_state = idle then
                fsm_state_save_internal <= std_logic_vector(to_unsigned(0,fsm_state_save'length));
                state_backup_save <= idle;
            elsif pr_state = w_sum then
                if addr_TC = '1' then
                    state_backup_save <= b_sum;
                    fsm_state_save_internal <= std_logic_vector(to_unsigned(2,fsm_state_save'length));
                else
                    fsm_state_save_internal <= std_logic_vector(to_unsigned(1,fsm_state_save'length));
                    state_backup_save <= w_sum;
                end if;     
            elsif pr_state = b_sum then
                fsm_state_save_internal <= std_logic_vector(to_unsigned(3,fsm_state_save'length));
                state_backup_save <= act_log;
            elsif pr_state = act_log then
                --In this case we can sckip the finished state, since after the act_log, data is already available outside
                fsm_state_save_internal <= std_logic_vector(to_unsigned(4,fsm_state_save'length));
                state_backup_save <= finished;
            elsif pr_state = finished then
                fsm_state_save_internal <= std_logic_vector(to_unsigned(0,fsm_state_save'length));
                state_backup_save <= idle;
            else
                --1)When we start the data save process,
                --state_backup_save will be containing
                --the last state of the layer before
                --starting saving.
                --2)In this way after we finish the save process
                --the fsm remembers what to write inside the nv_reg.
                fsm_state_save_internal <= fsm_state_save_internal;
                state_backup_save <= state_backup_save;
       --     end if;
            --Logic for recovery
            --fsm_state_rec
            if data_rec_busy = '1' then
                if fsm_state_en_rec = '1' then
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
                    end if;
                end if;
            end if;
        end if;
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
    --output_en_rec_vect <= (others => '0'); 
    addra <= 0;
    mul_sel <= '0';
    --The default value of out_val depends on out_v_set
    if out_v_set = 1 then
        out_val <= '0';
    elsif out_v_set = 2 then
        out_val <= out_val and n_power_rst;
    elsif out_v_set = 3 then 
        out_val <= '1' and n_power_rst;
    else
        out_val <= out_val and n_power_rst;
    end if;
    --out_val <= out_val;-- and n_power_rst;
    sum_reg_rst <= '0';
    update_out<='0';
    addr_in_gen_rst <='0';
    reg_en <= '0';
	--###############################
    case pr_state is
        when power_off =>
        --default values
            sum_reg_rst <= '1';
            --addr_in_gen_rst <= '1';
        when init =>
            mul_sel <= '0';
            sum_reg_rst <= '1';
            update_out <= '0';
            addr_in_gen_rst <= '1';
            reg_en <= '0';
        when recovery =>
            mul_sel <= '0';
            sum_reg_rst <= '0';
            update_out <= '0';
            --addr_in_gen_rst <= '1';
            reg_en <= '0';
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
                        output_en_rec_vect <= (others => '0');
                        internal_en_rec_vect <= (others => '0');
                    when internal =>
                        output_en_rec_vect <= (others => '0');
                        internal_en_rec_vect(addra) <= '1';
--                        if fsm_state_save_internal = std_logic_vector(to_unsigned(3,fsm_state_save_internal'length)) then--act_log
--                            mul_state <= '1';
--                        else
--                            mul_state <= '0';
--                        end if;
                        --if fsm_state_rec = 
                    when outputs =>
                        output_en_rec_vect(addra) <= '1';--addr 0 to num_outputs+1
                        internal_en_rec_vect <= (others => '0');
                    end case;
                    --LAYER OUTPUT RECOVERY)
                    --If we are recovering the output the input address range from 0 to num_outputs-1
                    -- enable and write to V_REG
                    --ena <= '1';                    
                    -- If we're recovering the
                else
                    output_en_rec_vect <= (others => '0');
                    internal_en_rec_vect <= (others => '0');                   
                end if;
            end if;
        when idle =>
            mul_sel <= '0';
            sum_reg_rst <= '1';
            update_out <= '0';
            addr_in_gen_rst <= '1';
            reg_en <= '1';         
        when w_sum =>
            mul_sel <= '0';
            sum_reg_rst <= '0';
            update_out <= '0';
            addr_in_gen_rst <= '0';
            reg_en <= '1';
        when b_sum =>
            mul_sel <= '1';
            sum_reg_rst <= '0';
            update_out <= '0';      
            addr_in_gen_rst <= '1';
            reg_en <= '1';  
        when act_log =>
            mul_sel <= '0';
            sum_reg_rst <= '0';
            update_out <= '0';
            addr_in_gen_rst <= '1';
            reg_en <= '1';
        when finished =>
            mul_sel <= '0';
            out_val <= '1';
            sum_reg_rst <= '0';
            update_out <= '1';
            addr_in_gen_rst <= '1';
            reg_en <= '1';
        when data_save_init =>
            --default values
            reg_en <= '0';
            sum_reg_rst <= '0';
            addr_in_gen_rst <= '0';
        when data_save_init_cmpl =>
            --default values
            reg_en <= '0';
            sum_reg_rst <= '0';
            addr_in_gen_rst <= '0';
        when data_save =>
            reg_en <= '0';
            sum_reg_rst <= '0';
            addr_in_gen_rst <= '0';
            if fsm_state_save_internal = std_logic_vector(to_unsigned(3,fsm_state_save_internal'length)) or fsm_state_save_internal = std_logic_vector(to_unsigned(3,fsm_state_save_internal'length)) then--act_log
                save_state_selector <= 1; --We route the ReLU_out register into the nv_reg cells
            else
                save_state_selector <= 0; --We route the sum_reg register into the nv_reg cells
            end if;
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
