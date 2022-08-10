----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso
-- 
-- Create Date: 04/05/2022 10:28:34 AM
-- Design Name: 
-- Module Name: layer - Behavioral
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
--Things to develop:
--X)Circuit to discern weather it's necessary to RECOVER the state, output or nothing. And route the correct signals FROM the nv_reg
--X)Save the neurons' weighted sum in 2 clock cycles. Done by adding num_outputs pins and leaving NC half of te total pins
--X)Augument gen_addr pins. Add pins to write the desired value into the register to resume computation

--Observations:
--1) The amount of time to save data in the nv_reg is higher than what it takes to compute the layer output. In general it is not convenient to save the output of the layer whenver there is a hazard, but to enable only a certain amount of layer to save their state.

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

entity I_layer is
--GENERIC:
generic(                                                                                
    constant num_inputs: natural := 30;
    constant num_outputs: natural := 30;
    constant layer_no: natural := 1;                                                    --layer_no          :     Layer number (identifier)
    constant act_type: string := "ReLU";                                                --act_type          :     Choose between "ReLU","Sig"
    constant act_fun_size: natural := 10;                                               --act_fun_size      :     If the user chooses an analytical activation function the number of sample have to be chosen
    constant en_backup: std_logic := '1'                                                --en_backup         :     '1': This layer is enabled to save its output '0': This layer is disabled from saving its output                                               
);
--------PORTS-------
port(                                                                                   
    -----ORIGINARY PINS--
    --------INPUTS-------
    clk: in std_logic;                                                                  --clk               :
    data_in: in sfixed(input_int_width-1 downto -input_frac_width);                     --data_in           :
    data_out_sel: in std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1);   --data_out_sel      :
    start: in std_logic;                                                                --start             :       Signal to trigger the layer and start computation
    -------OUTPUTS-------
    data_out: out sfixed(neuron_int_width-1 downto -neuron_frac_width);                 --data_out          :       I-th neuron output
    data_in_sel: inout std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);  --data_in_sel       :       To select the i-th neuron output
    data_v: out std_logic;                                                              --data_v            :       Aknowledges the layer output validity. Used to save the output of the layer when a hazard occurs. Triggers the next layer                                                                                                                                                                                                                                               
    ------ADDED PINS-----                                                                                        
    --------INPUTS-------
    n_power_reset: in std_logic;                                                        --n_power_reset     :       Emulates power failure. 1 Power on 0: Power Off
    fsm_nv_reg_state: in fsm_nv_reg_state_t;                                            --fsm_nv_reg_state  :       This contains the imperative commands to the varc.
    nv_reg_busy: in std_logic;                                                          --nv_reg_busy       :       Together with nv_reg_bbusy_sig aknowledges the availability fro r/w operation into/from the nv_reg
    nv_reg_busy_sig: in  STD_LOGIC;                                                     --nv_reg_busy_sig   :    
    nv_reg_dout: in STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);                          --nv_reg_dout       :       Contains the nv_reg output (used when recovering data)
    out_inv: in integer range 0 to 3;                                                   --out_inv          :        1: output is invalidated. 2: as long we are computing the output of the next layer. 3:After a power-off and we recover data.                                                                                        
    -------OUTPUTS-------
    state_layer: out std_logic_vector(3 downto 0);
    task_status: out std_logic;                                                         --task_status       :       0: The recovery/save operation has finished. 1: It is still being carried on.
    nv_reg_en: out std_logic;                                                           --nv_reg_en         :       1: Reading/Wrinting operation request. 0: nv_reg is disabled
    nv_reg_we: out std_logic;                                                           --nv_reg_we         :       1: Write Operation Request. 0: No operation
    nv_reg_addr: out std_logic_vector(nv_reg_addr_width_bit-1 downto 0);                --nv_reg_addr       :       Contains the address of the nv_reg to access         
    nv_reg_din: out STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0)                           --nv_reg_din        :       It contains data to write into the nv_rega
    );                                                     
end I_layer;




--Make a change
architecture Behavioral of I_layer is
----------TYPE DECLARATION-----------
type data_out_type is array(0 to num_outputs-1) of sfixed(neuron_int_width-1 downto -neuron_frac_width);                            --data_out_type             :
type data_backup_output_type is array(0 to num_outputs+2) of std_logic_vector(nv_reg_width-1 downto 0);                               --data_backup_output_type   :This array groups the signals of the layer output. It's just the neurons' output(num_output signals). No of signals: num_outputs (the last 2 are unused)
type data_backup_state_type is array(0 to num_outputs+2) of std_logic_vector(nv_reg_width-1 downto 0);
------------SIGNAL DECLARATION--------
--gen_addr
signal addr: std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1) :=(others => '0');      --addr          : gen_addr output. Used to fetch previous layer data
signal addr_compl: std_logic_vector(0 to nv_reg_width-natural(ceil(log2(real(num_inputs))))-1):= (others => '0');
signal addr_TC: std_logic := '0';                                                                   --addr_TC       : gen_addr output. Used to acknowledge the end of data fetching
--I_FSM_layer
--Output                                                                                               
signal sum_reg_rst: std_logic;                                                                                                    
signal mul_sel: std_logic; 
signal out_v: std_logic:='0'; 
signal update_out: std_logic;
signal addr_in_gen_rst: std_logic;
--LAYER
--INPUT
--OUTPUT
signal data_out_vect: data_out_type;                                                                 --data_out_vect : Neurons' output collection

-----------VOLATILE REGISTERS SIGNALS------------
--This signals are used to group the input and output to the volatile elements of the architecture. FSM_layer state, addr_gen content, neurons' output and weighted sum.
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%RECOVERY SIGNALS
                                                                                                       --addra = end-1..end addr_gen and fsm_state are begin fetched
--signal s_r: integer range 0 to num_outputs+1;                                         --activation pins to recover the state(FSM state, addr_gen content and w_sum). It is used to trigger the overwriting 
--signal o_r: integer range 0 to num_outputs+1;                                         --activation pins to recover the outputs (neurons' outputs. Last 2 are unused). It is used to trigger the overwriting
--CONTROL SIGNALS
signal o_rec_vect: std_logic_vector(0 to num_outputs+1);                                --Recovery enable bits. The i-th element enables overwriting the w_sum or the out_reg of the corresponding neuron. It is used during the recovery of data. 
signal s_rec_vect: std_logic_vector(0 to num_outputs+1);                                --s_rec_vect            :Bit to write into the addr_gen register and weighted_sum_reegisters. To resume computation of the layer from the state.
signal fsm_state_rec: std_logic_vector(0 to nv_reg_width-1);                            --fsm_state_rec         :FSM State. To recover the FSM state

--REC SIGNALS
signal data_backup_vect_output_rec: data_backup_output_type := (others => (others => '0'));                            --data_backup_vect_output_rec:
signal data_backup_vect_state_rec: data_backup_state_type := (others => (others => '0'));
--ADDR SIGNALS
signal addra: integer range 0 to num_outputs+2;                                         --addra                 :address to write into the volatile register when recovering data 

--SAVE SIGNALS
signal fsm_state_save: std_logic_vector(0 to nv_reg_width-1);                           --fsm_state_save        :To save the FSM state
signal en: std_logic;                                                                 --en                  :Bit to disable neuron register( weighted sum mainly) when
signal addrb: integer range 0 to num_outputs+2;--num_outputs elements for saving the output and one for saving the                                          --addrb                 :address to read from the volatile registers when saving data
signal data_backup_vect_output_save: data_backup_output_type;                           --data_backup_vect_output_save:
signal data_backup_vect_state_save, data_backup_vect_ReLU_save, data_backup_vect_wsum_save: data_backup_state_type;
constant bits_addrb: natural := natural(ceil(log2(real(num_outputs+2))));               --Address width to access data_backup_vect_state_save and data_backup_vect_output_save

signal doutb: std_logic_vector(nv_reg_width-1 downto 0);                    --Look at code. Must be replaced
signal dina     : std_logic_vector(31 DOWNTO 0);                            --Look at code Must be replaced.

--------------------------------------------------------------------------------------
-------------------------------COMMON_SIGNALS-----------------------------------------
signal task_status_internal: STD_LOGIC;
signal rst: std_logic:='1';
signal reg_en: std_logic;
signal out_inv_mul: integer range 0 to 3 :=1;
--------------------------------------------------------------------------------------
-------------------------------DATA_REC_SIGNALS---------------------------------------  
signal data_rec_busy: STD_LOGIC := '0';                                     
signal data_rec_nv_reg_en: STD_LOGIC;  
signal data_rec_nv_reg_we: STD_LOGIC;  
signal data_rec_nv_reg_din: STD_LOGIC_VECTOR( 31 DOWNTO 0);
signal data_rec_nv_reg_addr : STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);
signal data_rec_var_cntr_init :STD_LOGIC;
signal data_rec_var_cntr_ce: STD_LOGIC;
signal data_rec_var_cntr_end_value : INTEGER;   
--------------------------------------------------------------------------------------
-------------------------------DATA_SAVE_SIGNALS-------------------------------------- 
signal data_save_busy: std_logic;                                                       --data_save_busy                : '1': data is being saved into the nv_reg
signal data_save_nv_reg_en: STD_LOGIC;                                                  --data_save_nv_reg_en           : '1': nv_reg has to be enabled to save data
signal data_save_nv_reg_we: STD_LOGIC;                                                  --data_save_nv_reg_we           : '1': nv_reg is being requested to do write operation to save data
signal data_save_nv_reg_din: STD_LOGIC_VECTOR( nv_reg_width-1 DOWNTO 0);                --data_save_nv_reg_din          : contains the data to be saved to nv_reg
signal data_save_nv_reg_addr : STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);      --data_save_nv_reg_addr         : addr to save data into the nv_reg
signal data_save_var_cntr_init :STD_LOGIC;                                              --data_save_var_cntr_init       : to initialize the counter for save op           
signal data_save_var_cntr_ce: STD_LOGIC;                                                --data_save_var_cntr_ce         : to enable the counter for save op
signal data_save_var_cntr_end_value : INTEGER;                                          --data_save_var_cntr_end_value  : end value of the counter for save op
signal save_state_selector: integer range 0 to 3;
--------------------------------------------------------------------------------------
-------------------------------VAR_COUNTER_SIGNALS------------------------------------
signal var_cntr_clk,var_cntr_init,var_cntr_ce,var_cntr_tc: STD_LOGIC;                               --clk, init, ce and tc signals for the counter
signal var_cntr_value, var_cntr_value_last,var_cntr_end_value: INTEGER range 0 to NV_REG_WIDTH+2;   --value, value_last and end value for the counter
--------------------------------------------------------------------------------------   
------------------------------DATA_REC process----------------------------------------
signal data_rec_nv_reg_start_addr: STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);	--data_rec_nv_reg_start_addr     :address from which start recovering data in nv_reg
signal data_rec_v_reg_start_addr: STD_LOGIC_VECTOR(v_reg_addr_width_bit-1 DOWNTO 0);    --data_rec_v_reg_start_addr     :address from which the recovered data (#ofdata=data_rec_offset) will be collected
signal data_rec_offset: INTEGER RANGE 0 TO num_outputs+2+2:=1;					    --data_rec_offset              :the offset used to calculate the last address recovered from nv_reg in data recovery process
                                                                                                                            -- ex: recover data from a total number of cells equal to 3 consecutive then data_rec_offset = 2
                                                                                                                            -- Initialized to 0 because we recover 1 element(type of recovery)
signal data_rec_type: data_backup_type_t := nothing;                                    --data_rec_type                 :it contains the type of recovery to be carried out
                                                                                                                            --outputt   :  neurons' output
                                                                                                                            --nothing   :  no data to be recovered
                                                                                                                            --state     :  weohgted_sum, gen_addr content, and fsm_state to be recovered                                                                                                                                                       
signal data_rec_recovered_data : STD_LOGIC_VECTOR(nv_reg_width-1 DOWNTO 0);             --data_rec_recovered_data       :the data recovered from nv_reg at every recovery cycle
signal data_rec_recovered_offset: INTEGER RANGE 0 TO NV_REG_WIDTH -1;                   --data_rec_recovered_offset     :the offset to the cell being accessed.
--------------------------------------------------DATA_SAVE process-------------------
signal data_save_nv_reg_start_addr: STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);	--data_save_nv_reg_start_addr   :start address (in nv_reg) from which the data save process will save volatile values
signal data_save_v_reg_start_addr: STD_LOGIC_VECTOR(v_reg_addr_width_bit-1 DOWNTO 0);   --data_save_v_reg_start_addr    :start address (in bram aka volatile register) from which the data save process will fetch data

signal data_save_v_reg_offset : INTEGER RANGE 0 TO V_REG_WIDTH -1;				        --data_save_v_reg_offset          : the offset used to calculate the last address of v_reg (aka volatile register) for data save process
signal data_save_type: data_backup_type_t := nothing;                                   --data_save_type                    :it contains the type of save to be performed

signal mul_sel_backup       : integer range 1 to 3:= 1;
signal fsm_pr_state         : fsm_layer_state_t;


--COMPONENT DECLARATION
------ I_FSM_layer --------
component I_FSM_layer is
    generic (
        num_outputs: natural;
        rom_depth: natural);--the number of summations in the weighted sum will be 16-1=15
    port(
        clk: in std_logic; 
        addr_TC: in std_logic; --This bit indicates if we are feeding the neuron with the last input
        start: in std_logic; --This signal initiate the neuron computation
        sum_reg_rst: out std_logic; --This bit resets the weighted sum register
        mul_sel: out std_logic; --This signal decides weather to add up the product w_i*x_i or the bias b
        out_v: out std_logic; --This signal aknowledges the output is valid
        update_out: out std_logic;
        addr_in_gen_rst: out std_logic;
        --Augumented Pins
        --Input pins
        out_inv: in integer range 0 to 3;
        n_power_rst: in std_logic;
        data_rec_busy: in std_logic;
        data_save_busy: in std_logic;
        data_rec_type: in data_backup_type_t;
        data_save_type: in data_backup_type_t;
        fsm_nv_reg_state: in fsm_nv_reg_state_t;
        data_rec_recovered_offset: in integer range 0 to num_outputs+1;
        fsm_state_r: std_logic;
        fsm_state_rec:std_logic_vector(0 to nv_reg_width-1);
        --Output Pins
        o_r: out std_logic_vector(0 to num_outputs+1); --activation pins for recovery of the outputs (last 2 are unused)
        s_r: out std_logic_vector(0 to num_outputs+1);
        save_state_selector: out integer range 0 to 3;
        addra: out integer range 0 to num_outputs+2;
        fsm_state_save: out std_logic_vector(0 to nv_reg_width-1); --To save the state of the fsm of the layer
        fsm_pr_state: out fsm_layer_state_t;
        reg_en: out std_logic
    ); --This updates the output of the neuron, since it is necessary to  
end component;
------ VAR_COUNTER -------
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

--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% NV_REG PORTS ACCESS MULTIPLEXER %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    nv_reg_en   <=  data_rec_nv_reg_en      when data_rec_busy = '1'    else
                    data_save_nv_reg_en     when data_save_busy = '1'   else
                    '0';
    nv_reg_we   <=  data_rec_nv_reg_we      when data_rec_busy = '1'    else
                    data_save_nv_reg_we     when data_save_busy = '1'   else
                    '0';
    nv_reg_addr <=  data_rec_nv_reg_addr    when data_rec_busy = '1'    else
                    data_save_nv_reg_addr   when data_save_busy = '1'   else
                    (OTHERS => '0');
                    
    nv_reg_din  <=  data_rec_nv_reg_din     when data_rec_busy = '1'    else
                    data_save_nv_reg_din    when data_save_busy = '1'   else
                    (OTHERS => '0');
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
--
out_inv_mul <= 3 when data_rec_type = outputt else
                out_inv;
--
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%VOL_ARC CONSTANTS%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    data_rec_nv_reg_start_addr  <= (others => '0');--(0 => '1', OTHERS => '0'); -- 1 
    data_rec_v_reg_start_addr   <= (others => '0');--(3 => '1', OTHERS => '0'); -- 8
    data_save_nv_reg_start_addr <= data_rec_nv_reg_start_addr;
    data_save_v_reg_start_addr  <= data_rec_v_reg_start_addr;
    --data_save_v_reg_offset      <= data_rec_offset;
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% VAR_CNTR PORT ACCESS MULITPLEXER %%%%%%%%%%%%%%%%%%%%%%%%%%%% 
    var_cntr_init       <=  data_rec_var_cntr_init          when data_rec_busy = '1'    else
                            data_save_var_cntr_init         when data_save_busy = '1'   else
                            '1'; --default initialize counter
    var_cntr_ce         <=  data_rec_var_cntr_ce            when data_rec_busy = '1'    else
                            data_save_var_cntr_ce           when data_save_busy = '1'   else
                            '0'; --default do not count
    var_cntr_end_value  <=  data_rec_var_cntr_end_value     when data_rec_busy = '1'    else
                            data_save_var_cntr_end_value    when data_save_busy = '1'   else
                            1; --default end value is 1
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
--%%%%%%%%%%%%%%%%%%% DATA_REC COMB LOGIC %%%%%%%%%%%%%%%%%%%%%%%
    data_rec_var_cntr_ce <= data_rec_busy;
    data_rec_var_cntr_init <= not data_rec_busy;
    data_rec_nv_reg_en <= not var_cntr_tc; --the value is still gated by the mux, so if we are not in data_rec the nv_reg is not enabled
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

--COMPONENTS INSTANTIATION
--%%%%%%%%%%%%%%%%%%%%%%%%%%%FSM_LAYER%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
--fsm_state_save <= data_backup_vect_state_save(num_outputs+1);
I_fsm_layer_comp: I_FSM_layer
generic map(
    num_outputs => num_outputs,
    rom_depth => num_inputs
)
port map(
    clk => clk,
    addr_TC => addr_TC,                 --addr_TC           :addr_TC This bit indicates if we are feeding the neuron with the last input
    start => start,                     --start             :start This signal initiate the neuron computation
    sum_reg_rst => sum_reg_rst,         --sum_reg_rst       :sum_reg_rst This bit resets the weighted sum register
    mul_sel => mul_sel,                 --mul_sel           :mul_sel This signal decides weather to add up the product w_i*x_i or the bias b
    out_v => out_v,                     --out_v             :out_v This signal aknowledge the output is valid
    update_out => update_out,           --update_out        :update_out
    addr_in_gen_rst => addr_in_gen_rst, --addr_in_gen_rst   :addr_in_gen_rst
    --Augumented Pins
    --Input pins
    out_inv => out_inv_mul,
    data_rec_type => data_rec_type,     
    data_save_type => data_save_type,
    n_power_rst => n_power_reset,
    data_rec_busy => data_rec_busy,
    data_save_busy => data_save_busy,
    fsm_nv_reg_state => fsm_nv_reg_state,
    data_rec_recovered_offset => data_rec_recovered_offset, --data_rec_recovered_offset :
    fsm_state_r => s_rec_vect(num_outputs+1),
    fsm_state_rec => data_backup_vect_state_rec(num_outputs+1),
    --Output pins
    o_r => o_rec_vect,
    s_r => s_rec_vect,
    save_state_selector => save_state_selector,
    addra => addra,
    fsm_state_save => fsm_state_save,
    fsm_pr_state => fsm_pr_state,
    reg_en => reg_en
    ); 
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%NEURONS%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
I_neurons: for i in 0 to num_outputs-1 generate
    component I_neuron is
        generic(
            rom_width: natural;
            rom_depth: natural;
            weight_file: string;
            bias_file: string);
        port(
            clk: in std_logic;
            data_in: in sfixed (input_int_width-1 downto -input_frac_width);
            addr: in std_logic_vector (0 to natural(ceil(log2(real(rom_depth))))-1);
            mul_sel: in std_logic;
            sum_reg_rst: in std_logic;
            update_out: in std_logic;
            data_out: out sfixed (input_int_width-1 downto -input_frac_width);
            --ADDED PINS
            --INPUT
            n_power_reset: in std_logic;
            en: in std_logic;
            o_rec: in std_logic;
            s_rec: in std_logic;
            data_out_rec: in sfixed (input_int_width-1 downto -input_frac_width);
            state_rec: in std_logic_vector(input_int_width+neuron_int_width-1 downto 0);
            --OUTPUT
            wsum_save: out std_logic_vector(input_int_width+neuron_int_width-1 downto 0);        
            ReLU_save: out std_logic_vector(input_int_width+neuron_int_width-1 downto 0)           
            );
    end component;
    begin
        I_neuron_i: I_neuron
        generic map(
        rom_width => neuron_rom_width,
        rom_depth => num_inputs,
        weight_file => "../../scripts/weights_and_bias/w_b/w_" & integer'image(layer_no)&"_"&integer'image(i)&".mif",
        bias_file => "../../../../../../scripts/weights_and_bias/w_b/b_" & integer'image(layer_no)&"_"&integer'image(i)&".mif")
        port map(
        clk => clk,
        data_in =>data_in,
        addr =>data_in_sel,        
        mul_sel => mul_sel,
        sum_reg_rst => sum_reg_rst,
        update_out => update_out,
        data_out => data_out_vect(i),
        --ADDED PINS
        --INPUT
        n_power_reset => n_power_reset,
        en => reg_en,
        o_rec => o_rec_vect(i),
        s_rec => s_rec_vect(i),-----Modifying this
        --w_rec =>w_rec_vect(i),
        data_out_rec => to_sfixed(data_backup_vect_output_rec(i+1)(input_int_width+input_frac_width-1 downto 0) ,input_int_width-1, -input_frac_width), --use data convertion
        state_rec => data_backup_vect_state_rec(i+1)(input_int_width+input_frac_width-1 downto 0),
        --OUTPUT
        wsum_save => data_backup_vect_wsum_save(i+1),
        ReLU_save => data_backup_vect_ReLU_save(i+1)    
        );
end generate;
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
ROUTE_OUTPUT_SIG: process(data_out_vect) is
begin
for i in 1 to num_outputs loop
    data_backup_vect_output_save(i) <= to_slv(data_out_vect(i-1));
end loop;
data_backup_vect_output_save(0) <= std_logic_vector(to_unsigned(mul_sel_backup, 32));
end process ROUTE_OUTPUT_SIG;

ROUTE_STATE_SIG: process(data_backup_vect_wsum_save, data_backup_vect_ReLU_save) is
begin
if save_state_selector = 0 then--w_sum, b_sum state then
    for i in 1 to num_outputs loop
        data_backup_vect_state_save(i) <= data_backup_vect_wsum_save(i);
    end loop;
else --mul_state = '1' 'act_log'
    for i in 1 to num_outputs loop
        data_backup_vect_state_save(i) <= data_backup_vect_ReLU_save(i);
    end loop;
end if;
data_backup_vect_state_save(num_outputs+1) <= addr_compl & addr;
data_backup_vect_state_save(num_outputs+2) <= fsm_state_save;
data_backup_vect_state_save(0) <= std_logic_vector(to_unsigned(mul_sel_backup,32));

end process ROUTE_STATE_SIG;

--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%COMBINATORIAL LOGIC%%%%%%%%%%%%%%%%%%%%%%%%%%%
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%TASK STATUS LOGIC%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
task_status <= task_status_internal;                     
task_status_internal <= data_rec_busy OR data_save_busy;    --combined signal: tells if some process is ongoing 
                                                                --> (used to regulate v_reg access to avoid collisions)
state_layer <= fsm_state_save(0 to 3);
                                                              

--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
--%%%%%%%%%%%%%%%%%%%%%DATA BACKUP WIRING%%%%%%%%%%%%%%%%%%%%%
--%%%%REC%%%%%
--%%DATA SIGNALS
data_backup_vect_output_wire: process(clk) is
begin
if rising_edge(clk) then
data_backup_vect_output_rec(addra) <= data_rec_recovered_data;
end if;
end process;

data_backup_vect_state_wire: process(clk) is
begin
if rising_edge(clk) then
data_backup_vect_state_rec(addra) <= data_rec_recovered_data;
end if;
end process;
--%%%SAVE%%
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
--%%%%LAYER DATA_VALID%%%%%%%%%%%
data_v <= out_v;
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
--%%%%%addr_gen rst%%%%%%
rst <= addr_in_gen_rst or not(n_power_reset);
--%%addr to fetch data%%%
data_in_sel <= addr;
--%%%%%%%%


gen_addr: process(clk,rst) is --This process generate the address to access the neuron weight and get the input from the previous layer
begin
   -- if rst = '1' then
    --    addr <= '0';
   -- else
        if rst = '1' then
            addr <= (others => '0');
            addr_TC <= '0'; --If before shutting down and addr = num_inputs-2, it is necessary to reset addr_TC as well, because it is not reset during the idle state because the rst bit to the addr generator has prioritt over the reg_en
        else
           if rising_edge(clk) then
                if reg_en = '1' then
                    addr <= std_logic_vector(unsigned(addr) + 1);
                    if unsigned(addr) = num_inputs-2 then
                        addr_TC <= '1';
                    else
                        addr_TC <= '0';
                    end if;
                    if unsigned(addr) = num_inputs-1 then
                        addr <= (others=>'0');
                    end if;
                end if;
            end if;
        end if;
end process gen_addr;


--To determine the layer type on recovery we need to look at the first element recovered from the nv_reg
LAYER_TYPE_ONREC: process(clk) is
begin
    if data_rec_busy = '1' then
        if nv_reg_we = '0' then
            if addra = 0 then -- we are recovering 
                --fsm_state_save = 0 id
                --2: outputt 3:state 1:nothing
                if to_integer(unsigned(nv_reg_dout)) = 2 then
                    data_rec_offset <= num_outputs;
                    data_rec_type <= outputt;
                elsif to_integer(unsigned(nv_reg_dout)) = 3 then
                    data_rec_offset <= num_outputs+2;
                    data_rec_type <= state;
                elsif to_integer(unsigned(nv_reg_dout)) = 1 then
                    data_rec_offset <= 1;
                    data_rec_type <= nothing;
                else
                    data_rec_offset <= data_rec_offset;
                    data_rec_type <= data_rec_type;
                end if;
            end if;
        end if;
    else
         data_rec_type <= nothing;
    end if;
end process LAYER_TYPE_ONREC;

LAYER_TYPE_ONSAVE: process(fsm_state_save, out_v) is
--This process determine weather the layer is:
--1) Currently active
--2) Previous of the currently active layer
--3) Idle layer
--Depending on the type of the layer, we save a different collection of data
begin
    if unsigned(fsm_state_save) = 1 or  unsigned(fsm_state_save)= 2 or  unsigned(fsm_state_save) = 3 then
        --The state of the layer is being computed
        data_save_type <= state;
        mul_sel_backup <= 3;
    elsif out_v = '1' then
        --The output of the layer has been computed, it has been recovered by the layer 
        --other states and the output is necessary to the next layer
        data_save_type <= outputt;
        mul_sel_backup <= 2;
     else
        --w_sum, b_sum, act_log
        data_save_type <= nothing;
        mul_sel_backup <= 1;
        --Also, we need to set the number of elements to retrieve from the nv_reg
        --In case it's nothing we only need to write to the first element of the nv_reg
   
    end if;
end process;

------------------------------------------------DATA_REC process-------------------------------------------------------------------
-- Doc:
--      this process and its brothers are concernd of data recovery from non volatile register. The recovered data and its amount 
--      can be defined by changing the constants in VOL_ARC CONSTANTS subsection of this code. The recovered data can be obtained 
--      by combining the information carried by: data_rec_recovered_data, data_rec_recovered_offset. This is necessary because
--      from request to offer there are delays expecially from NV_REG.
-----------------------------------------------------------------------------------------------------------------------------------

--%%%%%%%%%%%%%%%%%%% DATA_REC CONSTANTS %%%%%%%%%%%%%%%%%%%%%%%%
data_rec_nv_reg_we <= '0';
data_rec_nv_reg_din <= (OTHERS => '0');
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

--Data Recovery entities
DATA_REC: process(n_power_reset,clk) is
    begin
        if(n_power_reset = '0') then
            data_rec_busy <= '0';
           -- data_rec_nv_reg_en <= '0';
            
        elsif(rising_edge(clk)) then
            if(fsm_nv_reg_state = start_data_recovery_s) then
                data_rec_busy <= '1';
               -- data_rec_nv_reg_en <= '1';  
            elsif(var_cntr_tc = '1') then
                data_rec_busy <= '0';
                --data_rec_nv_reg_en <= '0';
            --else we are doing normal operation and data_rec_busy is 0
            end if; 
        end if;
end process DATA_REC;

DATA_REC_NV_REG_SIG_CNTRL: process (data_rec_busy,var_cntr_value) is            
begin 
    if (data_rec_busy = '0') then 
        data_rec_nv_reg_addr <= data_rec_nv_reg_start_addr; 
    else
        if(var_cntr_value<=data_rec_offset) then
            data_rec_nv_reg_addr <= std_logic_vector(   unsigned(data_rec_nv_reg_start_addr) 
                                                        + to_unsigned(var_cntr_value,nv_reg_addr_width_bit)
                                                     ); 
        end if; -- if the bound is not respected latch the last value, 
                --> i.e. when the process starts it is "data_rec_nv_reg_start_addr", while
                --> when it is over "data_rec_offset" it assumes "data_rec_nv_reg_start_addr + data_rec_offset"
    end if;
end process DATA_REC_NV_REG_SIG_CNTRL;

DATA_REC_V_REG_SIG_CNTRL: process(clk,data_rec_busy) is
begin
   if (data_rec_busy = '0') then 
       data_rec_recovered_offset <= 0;
       data_rec_recovered_data <= (OTHERS => '0');
   elsif (rising_edge(clk)) then
       if(nv_reg_busy='0') then
           if(var_cntr_value > 0 AND var_cntr_value <= data_rec_offset + 1 ) then -- the plus one is used because the data is moved into a shift register for siyncronization purposes
               data_rec_recovered_data <= nv_reg_dout;
               data_rec_recovered_offset <= var_cntr_value_last;
           end if;
       end if;
   end if;
end process DATA_REC_V_REG_SIG_CNTRL;

--------------------------------------------------DATA_SAVE process-------------------------------------------------------------------
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%DATA_SAVE COMBINATIONAL LOGIC%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
data_save_var_cntr_ce <= data_save_busy;
data_save_var_cntr_init <= not data_save_busy;
data_save_nv_reg_en <= not var_cntr_tc; --the value is still gated by the mux, so if we are not in data_save the nv_reg is not enabled
--data_save_nv_reg_we <= (OTHERS => '1') when data_save_busy ='1' and var_cntr_tc = '0' and var_cntr_value > 0 else (OTHERS => '0');
data_save_nv_reg_we <= '1' when data_save_busy ='1' and var_cntr_tc = '0' else '0';
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

DATA_SAVE: process(n_power_reset,clk) is
begin
    if(n_power_reset = '0') then
        data_save_busy <= '0';
        --enb <= '0';
    elsif(rising_edge(clk)) then
        
        if(fsm_nv_reg_state = start_data_save_s) then
            --enb <= '1';
            if(fsm_pr_state=data_save_init_cmpl) then
                data_save_busy <= '1';
            end if;  
        end if;
        if(var_cntr_tc = '1') then
            --enb <= '0';
            data_save_busy <= '0';
        end if; 
    end if;
end process DATA_SAVE;

DATA_SAVE_V_REG_SIG_CNTRL: process (clk,var_cntr_value,data_save_busy) is
begin
    if data_save_busy ='0' then
        addrb <= 0;
    elsif rising_edge(clk) then
       if nv_reg_busy = '0' then    --> when nv_reg turns busy the content of addrb must be available, given this premise, 
                                    --> change the value when it is captured as no more busy 
            if (var_cntr_value <= data_save_v_reg_offset) then
                addrb <= var_cntr_value;
            end if;
       end if;
    end if;
end process DATA_SAVE_V_REG_SIG_CNTRL;

--doutb must be replaced by the i-th element of the data group
--data_backup_vect_state_save
--data_backup_vect_output_save
--doutb will be connected to either of this signal depending of what we are saving
doutb <= data_backup_vect_output_save(addrb) when mul_sel_backup = 2 else
            data_backup_vect_state_save(addrb) when mul_sel_backup = 3 else
                    std_logic_vector(to_unsigned(mul_sel_backup,nv_reg_width));

DATA_SAVE_NV_REG_SIG: process (clk,var_cntr_value,data_save_busy) is
begin
    if data_save_busy ='0' then
        data_save_nv_reg_din <= doutb;
        data_save_nv_reg_addr <= (others => '0'); --data_save_nv_reg_start_addr;
    elsif rising_edge(clk) then
       if nv_reg_busy_sig = '0' and nv_reg_busy = '1' then --capture the nv_reg signals at the start cycle and keep them constant
            if (var_cntr_value <= data_save_v_reg_offset) then
                data_save_nv_reg_din <= doutb;
                data_save_nv_reg_addr <= std_logic_vector(   unsigned(data_save_nv_reg_start_addr) + 
                                                            to_unsigned(var_cntr_value,nv_reg_addr_width_bit));
            end if;
        end if;
    end if;
end process DATA_SAVE_NV_REG_SIG;

DATA_SAVE_OFFSET: process(data_save_type) is
begin
case data_save_type is
    when state =>--we never end in this case for save output
    data_save_v_reg_offset <= num_outputs+2;
    when outputt =>
    data_save_v_reg_offset <= num_outputs;
    when nothing =>
    data_save_v_reg_offset <= 0;
end case;
end process DATA_SAVE_OFFSET;



--------------------------------------------------VAR_CNTR process--------------------------------------------------------------------    
--%%%%%%%%%%%%%%%%%%%%VAR_CNTR process COMBINATORIAL LOGIC%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
data_rec_var_cntr_end_value <= data_rec_offset + 2;         --the plus two is because a cycle is used to get the first data and then 
                                                                --> the other one just to notify as terminal count cycle
data_save_var_cntr_end_value <= data_save_v_reg_offset + 2; --should be + 1 just for the terminal count clk cycle but +2 because on how the var_cntr_clk ticks
                                                                --> beacuase of this an extra clk cycle will be wasted
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
VAR_CNTR_CLK_GEN: process(clk,task_status_internal) is
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

--Output logic
data_out<=data_out_vect(to_integer(unsigned(data_out_sel)));





end Behavioral;