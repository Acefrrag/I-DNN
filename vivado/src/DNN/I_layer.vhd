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

--Observations:
--1) The amount of time to save data in the nv_reg is higher than what it takes to compute the layer output. In general it is not convenient to save the output of the layer whenver there is a hazard, but to enable only a certain amount of layer to save their state?
library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

library work;
use work.I_DNN_package.all;
--Added Packages
use work.COMMON_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;

entity I_layer is
-------GENERIC:-------
generic(                                                                                
    constant num_inputs: natural := 30;
    constant num_outputs: natural := 30;
	constant neuron_inout_IntWidth: natural;
	constant neuron_inout_FracWidth: natural;
	constant neuron_weight_IntWidth: natural;
	constant neuron_weight_FracWidth: natural;
    constant layer_no: natural := 1;                                                    --layer_no          :     Layer number (identifier)
    constant act_fun_type: string := "ReLU";                                                --act_type          :     Choose between "ReLU","Sig"
    constant sigmoid_inputdataWidth: natural;
	constant sigmoid_inputdataIntWidth: natural;
	constant lyr_prms_path: string
    --constant en_backup: std_logic := '1'                                              --en_backup         :     '1': This layer is enabled to save its output '0': This layer is disabled from saving its output                                               
);
--------PORTS----------
port(                                                                                   
    -----ORIGINARY PINS--
    --------INPUTS-------
    clk: in std_logic;                                                                  --clk               :
    data_in: in sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);                     --data_in           :
    data_out_sel: in std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1);   --data_out_sel      :
    start: in std_logic;                                                                --start             :       Signal to trigger the layer and start computation
    -------OUTPUTS-------
    data_out: out sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);                 --data_out          :       I-th neuron output
    data_in_sel: inout std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);  --data_in_sel       :       To select the i-th neuron output
    data_v: out std_logic;                                                              --data_v            :       Aknowledges the layer output validity. Used to save the output of the layer when a hazard occurs. Triggers the next layer                                                                                                                                                                                                                                               
    ------ADDED PINS-----                                                                                        
    --------INPUTS-------
    n_power_reset: in std_logic;                                                        --n_power_reset     :       Emulates power failure. 1 Power on 0: Power Off
    fsm_nv_reg_state: in fsm_nv_reg_state_t;                                            --fsm_nv_reg_state  :       This contains the imperative commands to the varc.
    nv_reg_busy: in std_logic;                                                          --nv_reg_busy       :       Together with nv_reg_bbusy_sig aknowledges the availability fro r/w operation into/from the nv_reg
    nv_reg_busy_sig: in  STD_LOGIC;                                                     --nv_reg_busy_sig   :       It anticipate nv_reg_busy by one clock cycle    
    nv_reg_dout: in STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);                          --nv_reg_dout       :       Contains the nv_reg output (used when recovering data)
    out_v_set: in integer range 0 to 3;                                                 --out_v_set         :      1: layer's output is invalidated. 2: as long we are computing the output of the next layer, or the layer is idle. 3:After a power-off and we recover data.                                                                                        
    -------OUTPUTS-------
    task_status: out std_logic;                                                         --task_status       :       0: The recovery/save operation has finished. 1: It is still being carried on.
    nv_reg_en: out std_logic;                                                           --nv_reg_en         :       1: Reading/Wrinting operation request. 0: nv_reg is disabled
    nv_reg_we: out std_logic;                                                           --nv_reg_we         :       1: Write Operation Request. 0: No operation
    nv_reg_addr: out std_logic_vector(nv_reg_addr_width_bit-1 downto 0);                --nv_reg_addr       :       Contains the address of the nv_reg to access         
    nv_reg_din: out STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);                          --nv_reg_din        :       It contains data to write into the nv_rega
    pr_state: out fsm_layer_state_t                                                     --pr_state          :       It contains the present state of the layer 
    );                                                     
end I_layer;

architecture Behavioral of I_layer is
--------------------------------------TYPES DECLARATION-----------------------------------
type data_out_type is array(0 to num_outputs-1) of sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);            --data_out_type             :This array groups the output of layer's neurons.
type data_backup_output_type is array(0 to num_outputs+2) of std_logic_vector(nv_reg_width-1 downto 0);             --data_backup_output_type   :This array groups the signals to save the layer output. The number of elements used are 1(TAG at first cell) + num_outputs(one output register per neuron).
type data_backup_internal_type is array(0 to num_outputs+2) of std_logic_vector(nv_reg_width-1 downto 0);           --data_backup_internal_type :This array groups the signals of the layer neuron's internal register(cumulative sum register, ReLU register). The number of elements used are num_outputs(an internal register per neuron)+2(layer state and LAYER_CNTR value)+1(TAG at first cell)
-------------------------------------------------------------------------------------------
--------------------------------------SIGNAL DECLARATION-----------------------------------
------------------------------------------LAYER_CNTR---------------------------------------
signal addr: std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1) :=(others => '0');                      --addr          : LAYER_CNTR output. Used to fetch previous layer data as well neuron's weights
signal addr_TC: std_logic := '0';                                                                                   --addr_TC       : Counter Terminal for LAYER_CNTR.
signal addr_compl: std_logic_vector(0 to nv_reg_width-natural(ceil(log2(real(num_inputs))))-1):= (others => '0');   --addr_compl    : Completion of number of bit to save address into the nv_reg cell.
-------------------------------------------------------------------------------------------
------------------------------------------I_FSM_layer--------------------------------------
--Output                                                                                               
signal sum_reg_rst: std_logic;      --Wire                                                              
signal mul_sel: std_logic;          --Wire
signal out_v: std_logic:='0';       --Wire
signal update_out: std_logic;       --Wire
signal addr_in_gen_rst: std_logic;  --Wire
---------------------------------------------------------------------------------------------
---------------------------------------------LAYER-------------------------------------------
signal data_out_vect: data_out_type;        --data_out_vect : Neurons' outputs
---------------------------------------------------------------------------------------------
-------------------------------VOLATILE REGISTERS SIGNALS------------------------------------
---------------------------------LAYER RECOVERY SIGNALS--------------------------------------
-----------------------------LAYER RECOVERY CONTROL SIGNALS----------------------------------
signal output_en_rec_vect: std_logic_vector(0 to num_outputs+1);                        --Recovery enable bits. :Wire
signal internal_en_rec_vect: std_logic_vector(0 to num_outputs+1);                      --internal_en_rec_vect  :Wire
signal fsm_state_rec: std_logic_vector(0 to nv_reg_width-1);                            --fsm_state_rec         :Wire 
signal fsm_state_en_rec: std_logic;                                                     --fsm_state_en_rec      :Wire
---------------------------------------------------------------------------------------------
----------------------------------OTHER RECOVERY SIGNALS-------------------------------------
signal data_backup_vect_output_rec: data_backup_output_type := (others => (others => '0'));         --data_backup_vect_output_rec   : Collection of wires to output recovery pins
signal data_backup_vect_internal_rec: data_backup_internal_type := (others => (others => '0'));     --data_backup_vect_internal_rec : Collection of wires to internal register pins
signal addra: integer range 0 to num_outputs+2;                                                     --addra                         : Address to fetch the volatile registers when recovering data 
--------------------------------------LAYER SAVE SIGNALS------------------------------------------
signal fsm_state_save: std_logic_vector(0 to nv_reg_width-1);                                                           --fsm_state_save                :It contains the encoded state of the layer to save into the nv_reg
signal en: std_logic;                                                                                                  --en                            :Bit to disable VARC registers when saving/recovering data. This is done to prevent the architecture to change its state when saving data.
signal addrb: integer range 0 to num_outputs+2;                                                                         --addrb                         :for saving the output and one for saving the                                          --addrb                 :address to read from the volatile registers when saving data
signal doutb: std_logic_vector(nv_reg_width-1 downto 0);                                                                --doutb                         :It contains               
signal data_backup_vect_output_save: data_backup_output_type;                                                           --data_backup_vect_output_save  :Collection of layer's neuron output.
signal data_backup_vect_internal_save, data_backup_vect_ReLU_save, data_backup_vect_wsum_save: data_backup_internal_type;  --data_backup_vect_internal_save   :Collection of layer's and neurons' internal registers.
signal data_save_type_marker  : integer range 1 to 4:= 1;                                                               --data_save_type_marker         :This encodes the type of data saved inside the nv_reg. The code is written inside the first element of the nv_reg which and instructs the volatile architecture how many cells are supposed to be recovered.
signal data_save_type: data_backup_type_t := nothing;                                                                   --data_save_type                :It contains the type of save to be performed
signal fsm_pr_state         : fsm_layer_state_t;                                                                        --fsm_pr_state                  :It contains the present of the layer. It used both to enable the power_approximation unit and to set the data_rec_busy bit.
--------------------------------------------------------------------------------------
-------------------------------COMMON_SIGNALS-----------------------------------------
signal task_status_internal: STD_LOGIC;         --task_status_internal  : wire
signal rst: std_logic:='1';                     --rst                   :
signal reg_en: std_logic;                       --reg_en                : register enable to enable/disable the internal registers of the volatile architecture when saving and recovering data.
signal out_v_set_mul: integer range 0 to 3 :=1; --out_v_set_mul         : this set the output validity bit of the layer.
                                                                           --Normally this is driven by the output validity bit of the next layer, but when the VARC recovers an output type data, this value is forced to 3 by the fsm of the layer(3 instruct the fsm_layer to set the validity bit to '1').
signal data_in_sel_internal: std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);
--------------------------------------------------------------------------------------
-------------------------------DATA_REC_SIGNALS---------------------------------------
signal data_rec_busy: STD_LOGIC := '0';                                                     --data_rec_busy         : '1': when data recovery is initialized                               
signal data_rec_nv_reg_en: STD_LOGIC:='1';                                                  --data_rec_nv_reg_en    :This enables the nv_reg when recovering data.
constant data_rec_nv_reg_we: STD_LOGIC:='0';                                                --data_rec_nv_reg_we    :'0':This disables the nv_reg_we bit when recovering data  
constant data_rec_nv_reg_din: STD_LOGIC_VECTOR( nv_reg_width-1 DOWNTO 0):=(others => '0');  --data_rec_nv_reg_din   :the nv_reg_din is latched to this when we are recovering data 
signal data_rec_nv_reg_addr : STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);           --data_rec_nv_reg_addr  :addr to rec data from nv_reg 
signal data_rec_var_cntr_init :STD_LOGIC;                                                   --data_rec_var_cntr_init:VAR_CNTR init value when recovering data
signal data_rec_var_cntr_ce: STD_LOGIC;                                                     --data_rec_var_cntr_ce  :
signal data_rec_var_cntr_end_value : INTEGER;                                               --data_rec_cntr_end_vlue:
constant data_rec_nv_reg_start_addr: STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0):=(others => '0');  --data_rec_nv_reg_start_addr    :address from which start recovering data in nv_reg
constant data_rec_v_reg_start_addr: STD_LOGIC_VECTOR(v_reg_addr_width_bit-1 DOWNTO 0):=(others => '0');    --data_rec_v_reg_start_addr     :address from which the recovered data (#ofdata=data_rec_offset) will be collected

--------------------------------------------------------------------------------------
------------------------------DATA_REC process----------------------------------------
signal data_rec_offset: INTEGER RANGE 0 TO num_outputs+2+2:=1;					        --data_rec_offset               :the number of elements to save/recover from the nv_reg
                                                                                                                            -- ex: recover data from a total number of cells equal to 3 consecutive then data_rec_offset = 2
                                                                                                                            -- Initialized to 0 because we recover 1 element(type of recovery)
signal data_rec_type: data_backup_type_t := nothing;                                    --data_rec_type                 :it contains the type of recovery to be carried out
                                                                                                                            --outputs   :  neurons' output
                                                                                                                            --nothing   :  no data to be recovered
                                                                                                                            --internal  :  registers of the volatile architecture(ReLU, cumulative_sum, LAYER_CNTR, fsm_state)                                                                                                                                                      
signal data_rec_recovered_data : STD_LOGIC_VECTOR(nv_reg_width-1 DOWNTO 0);             --data_rec_recovered_data       :the data read from nv_reg at every recovery cycle
signal data_rec_recovered_offset: INTEGER RANGE 0 TO NV_REG_WIDTH -1;                   --data_rec_recovered_offset     :the offset to the cell being accessed.
-------------------------------DATA_SAVE_SIGNALS--------------------------------------
signal data_save_busy: std_logic;                                                       --data_save_busy                : '1': data is being saved into the nv_reg
signal data_save_nv_reg_en: STD_LOGIC;                                                  --data_save_nv_reg_en           : '1': nv_reg has to be enabled to save data
signal data_save_nv_reg_we: STD_LOGIC;                                                  --data_save_nv_reg_we           : '1': nv_reg is being requested to do write operation to save data
signal data_save_nv_reg_din: STD_LOGIC_VECTOR( nv_reg_width-1 DOWNTO 0);                --data_save_nv_reg_din          : contains the data to be saved to nv_reg
signal data_save_nv_reg_addr : STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);      --data_save_nv_reg_addr         : addr to save data into the nv_reg
signal data_save_var_cntr_init :STD_LOGIC;                                              --data_save_var_cntr_init       : to initialize the counter for save op           
signal data_save_var_cntr_ce: STD_LOGIC;                                                --data_save_var_cntr_ce         : to enable the counter for save op
signal data_save_var_cntr_end_value : INTEGER;                                          --data_save_var_cntr_end_value  : end value of the counter for save op
constant data_save_nv_reg_start_addr: STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0):=(others => '0');  --data_save_nv_reg_start_addr   :start address (in nv_reg) from which the data save process will save volatile values
constant data_save_v_reg_start_addr: STD_LOGIC_VECTOR(v_reg_addr_width_bit-1 DOWNTO 0):=(others => '0');    --data_save_v_reg_start_addr    :start address (in bram aka volatile register) from which the data save process will fetch data
--------------------------------------------------------------------------------------
--------------------------------------------------DATA_SAVE process-------------------
signal data_save_v_reg_offset : INTEGER RANGE 0 TO V_REG_WIDTH -1;                      --data_save_v_reg_offset        :the offset used to calculate the last address of v_reg (aka volatile register) for data save process

-------------------------------VAR_COUNTER_SIGNALS------------------------------------
--These signals are latched to the corresponding var_cntr_save/rec_[..] signals depending on what it is been commanded by the fsm_nv_reg
signal var_cntr_clk,var_cntr_init,var_cntr_ce,var_cntr_tc: std_logic;                               --clk, init, ce and tc signals for the counter
signal var_cntr_value, var_cntr_value_last,var_cntr_end_value: integer range 0 to NV_REG_WIDTH+2;   --value, value_last and end value for the counter
--------------------------------------------------------------------------------------

--COMPONENT DECLARATION
------ I_FSM_layer --------
component I_FSM_layer is
    generic (
        num_outputs: natural;
        rom_depth: natural);--the number of summations in the weighted sum will be 16-1=15
    port(
        clk: in std_logic; 
        addr_TC: in std_logic; 
        start: in std_logic; 
        sum_reg_rst: out std_logic; 
        mul_sel: out std_logic; 
        out_v: out std_logic;
        update_out: out std_logic;
        addr_in_gen_rst: out std_logic;
        --Added Pins
        --Input pins
        out_v_set: in integer range 0 to 3;
        n_power_rst: in std_logic;
        data_rec_busy: in std_logic;
        data_rec_type: in data_backup_type_t;
        fsm_nv_reg_state: in fsm_nv_reg_state_t;
        data_rec_recovered_offset: in integer range 0 to num_outputs+1;
        fsm_state_en_rec: in std_logic;
        fsm_state_rec: in std_logic_vector(0 to nv_reg_width-1);
        --Output Pins
        output_en_rec_vect: out std_logic_vector(0 to num_outputs+1); --activation pins for recovery of the outputs (last 2 are unused)
        internal_en_rec_vect: out std_logic_vector(0 to num_outputs+1);
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
---------------------------------OUT_VAL_SET MULTIPLEXER-----------------------------------------
--Description: The output valid set bit, which controls the output valid bit, is normally latched to the out_val_set bit driven by the next layer.
--However after we recover the data this is driven by the internal value as it is necessary to set the output bit to '1'.
-------------------------------------------------------------------------------------------------
out_v_set_mul <= 3 when data_rec_type = outputs and fsm_nv_reg_state = data_recovered_s else
                out_v_set;
-------------------------------------------------------------------------------------------------
----------------------------COMPONENTS INSTANTIATION--------------------------------------------
-------------------------------VAR_CNTR---------------------------------------------------------
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
-----------------------------------FSM_LAYER-----------------------------------------------------
--------------------------FSM_STATE_REC MULTIPLEXER--------------------------------------------
--The state of the layer to be recovered is normally latched to the regular value (data_backup-vect_internal(num_outputs+2) but if we are recovering the state "finished" (which is when we are recovering an output_type set of data but with an offset of num_outputs+2) it takes the corresponding element from the output collection.
fsm_state_rec <= data_backup_vect_output_rec(num_outputs+2) when data_rec_type = outputs and data_rec_offset = num_outputs+2 else
                 data_backup_vect_internal_rec(num_outputs+2);
--It's the same concept for what happens for fsm_state_rec
fsm_state_en_rec <= output_en_rec_vect(num_outputs+1) when data_rec_type = outputs and data_rec_offset = num_outputs+2 else
                internal_en_rec_vect(num_outputs+1);                       

I_fsm_layer_comp: I_FSM_layer
generic map(
    num_outputs => num_outputs,
    rom_depth => num_inputs
)
port map(
    clk => clk,
    addr_TC => addr_TC,                 
    start => start,                    
    sum_reg_rst => sum_reg_rst,         
    mul_sel => mul_sel,                 
    out_v => out_v,                     
    update_out => update_out,           
    addr_in_gen_rst => addr_in_gen_rst, 
    --Added Pins
    --Input pins
    out_v_set => out_v_set_mul,                             
    data_rec_type => data_rec_type,
    n_power_rst => n_power_reset,
    data_rec_busy => data_rec_busy,
    fsm_nv_reg_state => fsm_nv_reg_state,
    data_rec_recovered_offset => data_rec_recovered_offset, --data_rec_recovered_offset :
    fsm_state_en_rec => fsm_state_en_rec,
    fsm_state_rec => fsm_state_rec,
    --Output pins
    output_en_rec_vect => output_en_rec_vect,
    internal_en_rec_vect => internal_en_rec_vect,
    addra => addra,
    fsm_state_save => fsm_state_save,
    fsm_pr_state => fsm_pr_state,
    reg_en => reg_en
    ); 
---------------------------------------------------------------------------------------------------
-------------------------------NEURONS---------------------------------------
I_neurons: for i in 0 to num_outputs-1 generate
    component I_neuron is
        generic(
            rom_width: natural;
            rom_depth: natural;
			neuron_inout_IntWidth: natural;
			neuron_inout_FracWidth: natural;
			neuron_weight_IntWidth: natural;
			neuron_weight_FracWidth: natural;
            weight_file: string;
            bias_file: string;
			act_fun_type: string := "ReLU";
			sigmoid_inputdataWidth: natural := 5;
			sigmoid_inputdataIntWidth: natural := 2;
			Sigfilename: string := "../scripts/sigmoid/SigContent.mif"
			);
        port(
            clk: in std_logic;
            data_in: in sfixed (neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);
            addr: in std_logic_vector (0 to natural(ceil(log2(real(rom_depth))))-1);
            mul_sel: in std_logic;
            sum_reg_rst: in std_logic;
            update_out: in std_logic;
            data_out: out sfixed (neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);
            --ADDED PINS
            --INPUT
            n_power_reset: in std_logic;
            en: in std_logic;
            output_en_rec: in std_logic;
            internal_en_rec: in std_logic;
            data_v: in std_logic;
            data_out_rec: in sfixed (neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);
            state_rec: in std_logic_vector(neuron_inout_IntWidth+neuron_inout_FracWidth-1 downto 0);
            --OUTPUT
            wsum_save: out std_logic_vector(neuron_inout_IntWidth+neuron_inout_FracWidth-1 downto 0);        
            act_log_save: out std_logic_vector(neuron_inout_IntWidth+neuron_inout_FracWidth-1 downto 0)           
            );
    end component;
    begin
        I_neuron_i: I_neuron
        generic map(
        rom_width => neuron_inout_IntWidth+neuron_inout_FracWidth,
        rom_depth => num_inputs,
		neuron_inout_IntWidth => neuron_inout_IntWidth,
		neuron_inout_FracWidth => neuron_inout_FracWidth,
		neuron_weight_IntWidth => neuron_weight_IntWidth,
		neuron_weight_FracWidth => neuron_weight_FracWidth,
        weight_file => "../../../../../../"&lyr_prms_path&"weights/w_" & integer'image(layer_no)&"_"&integer'image(i)&".mif",
        bias_file => "../../../../../../"&lyr_prms_path&"biases/b_" & integer'image(layer_no)&"_"&integer'image(i)&".mif",
        act_fun_type => act_fun_type,
		sigmoid_inputdataWidth => sigmoid_inputdataWidth,
		sigmoid_inputdataIntWidth => sigmoid_inputdataIntWidth,
		Sigfilename => lyr_prms_path&"sigmoid/SigContent.mif")
        port map(
        clk => clk,
        data_in =>data_in,
        addr =>data_in_sel_internal,        
        mul_sel => mul_sel,
        sum_reg_rst => sum_reg_rst,
        update_out => update_out,
        data_out => data_out_vect(i),
        --ADDED PINS
        --INPUT
        n_power_reset => n_power_reset,
        en => reg_en,
        output_en_rec => output_en_rec_vect(i),
        internal_en_rec => internal_en_rec_vect(i),-----Modifying this
        data_v => out_v,
        --w_rec =>w_rec_vect(i),
        data_out_rec => to_sfixed(data_backup_vect_output_rec(i+1)(neuron_inout_IntWidth+neuron_inout_FracWidth-1 downto 0) ,neuron_inout_IntWidth-1, -neuron_inout_FracWidth), --use data convertion
        state_rec => data_backup_vect_internal_rec(i+1)(neuron_inout_IntWidth+neuron_inout_FracWidth-1 downto 0),
        --OUTPUT
        wsum_save => data_backup_vect_wsum_save(i+1),
        act_log_save => data_backup_vect_ReLU_save(i+1)    
        );
end generate;
--------------------------COMBINATORIAL OUTPUT LOGIC---------------------------                                                                                 
---------------------------------OUTPUT LOGIC----------------------------------
data_v <= out_v;
data_out<=data_out_vect(to_integer(unsigned(data_out_sel)));
-------------------------------------------------------------------------------
-------------------------------NV_REG PORTS ACCESS MULTIPLEXER-----------------
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
---------------------------------------------------------------------------------
--------------------------------TASK STATUS LOGIC--------------------------------
task_status_internal <= data_rec_busy OR data_save_busy;    --combined signal: tells if some process is ongoing
                                                                --> (used to regulate v_reg access to avoid collisions)
task_status <= task_status_internal; 
---------------------------------------------------------------------------------
-----------------------------------LAYER_PRESENT_STATE---------------------------
pr_state <= fsm_pr_state;
---------------------------------------------------------------------------------
-------------DATA_IN_SEL------------------
data_in_sel <= data_in_sel_internal;
-----------------------------
-----------------------------------------------------------------------------------------------------------
--------------------------------ROUTING VOLATILE REGISTER CONTENTS LOGIC-----------------------------------
-------------------------------------------ROUTING FOR SAVE PROCESS----------------------------------------
---------------------------------ROUTING NEURONS' OUTPUT REGISTERS-----------------------------------------
--Description: After the layer has computed the output and it is being used by the next layer it is necessary to save the neurons' output
-----------------------------------------------------------------------------------------------------------
ROUTE_SAVE_OUTPUT_SIG: process(all) is--data_out_vect, data_save_type_marker) is
begin
if n_power_reset = '1' then
    for i in 1 to num_outputs loop
        data_backup_vect_output_save(i) <= to_slv(data_out_vect(i-1));
    end loop;
    data_backup_vect_output_save(0) <= std_logic_vector(to_unsigned(data_save_type_marker, 32));
    data_backup_vect_output_save(num_outputs+1) <= addr_compl & addr;
    data_backup_vect_output_save(num_outputs+2) <= fsm_state_save;
else
    data_backup_vect_output_save <= (others => (others => '0'));
end if;
end process ROUTE_SAVE_OUTPUT_SIG;
-----------------------------------------------------------------------------------------------------------
------------------------------ROUTING NEURONS INTERNAL REGISTERS CONTENT-----------------------------------
--Description: When the layer is computing the output it is necessary to save its internal registers.
--This section routes the correct set of register to be saved into the nv_reg.
-----------------------------------------------------------------------------------------------------------
ROUTE_SAVE_STATE_SIG: process(all) is
begin
if n_power_reset = '1' then
    for i in 1 to num_outputs loop
        data_backup_vect_internal_save(i) <= data_backup_vect_wsum_save(i);
    end loop;
    data_backup_vect_internal_save(num_outputs+2) <= fsm_state_save;
    data_backup_vect_internal_save(num_outputs+1) <= addr_compl & addr;
    data_backup_vect_internal_save(0) <= std_logic_vector(to_unsigned(data_save_type_marker,32));
else--simulating power failure
    data_backup_vect_internal_save <= (others => (others => '0'));
end if;
end process ROUTE_SAVE_STATE_SIG;
------------------------------ROUTING FOR REC PROCESS-----------------------------------------------
--Description: When recovery data it is necessary to correctly route he data_rec_recovered_data recovered from the nv_reg into the correct layer's register
--Infact:
--1) When recovering the output it is necessary to put the recovered value inside neuron's output register (data_backup_vect_output_rec)
--2) When recovering the internal register it is necessary to put the recovered value inside neuron's internal register(data_backup_internal_register)
----------------------------------------------------------------------------------------------------
ROUTE_REC_SIG: process(clk) is
begin
if n_power_reset = '1' then
    if rising_edge(clk) then
        if data_rec_type = outputs then
            data_backup_vect_output_rec(addra) <= data_rec_recovered_data;
        else --state or nothing
            data_backup_vect_internal_rec(addra) <= data_rec_recovered_data;    
        end if;
    end if;
else--simulating power failure
    data_backup_vect_output_rec <= (others => (others => '0'));
    data_backup_vect_internal_rec <= (others => (others => '0'));
end if;
end process;

---------------------------------------LAYER_CNTR--------------------------------
--Description:
--This counter is used to access sequentially the layer's input as well as the corresponding layer neuron's weights when computing the weighted sum
----------------------------------------------------------------------------------------------------------------------------------------------------
rst <= addr_in_gen_rst or not(n_power_reset);
data_in_sel_internal <= addr;
addr_TC <= '0' when rst = '1' else
     --data_backup_vect_internal_rec(num_outputs+1)(natural(nv_reg_width-1)) when internal_en_rec_vect(num_outputs) = '1' and data_rec_busy = '1' else
     '1' when unsigned(addr) = num_inputs-1;
LAYER_CNTR: process(clk,rst) is 
begin
   -- if rst = '1' then
    --    addr <= '0';
   -- else
        if rst = '1' then
            addr <= (others => '0');
            --addr_TC <= '0'; --If before shutting down and addr = num_inputs-2, it is necessary to reset addr_TC as well, because it is not reset during the idle state because the rst bit to the addr generator has prioritt over the reg_en
        else
           if rising_edge(clk) then
                if internal_en_rec_vect(num_outputs) = '1' and data_rec_busy = '1' then
                    addr <= data_backup_vect_internal_rec(num_outputs+1)(natural(ceil(log2(real(num_inputs))))-1 downto 0);
                    --addr_TC <= data_backup_vect_internal_rec(num_outputs+1)(natural(nv_reg_width-1));
                elsif reg_en = '1' then
                    addr <= std_logic_vector(unsigned(addr) + 1);
--                    if unsigned(addr) = num_inputs-2 then
--                        addr_TC <= '1';
--                    else
--                        addr_TC <= '0';
--                    end if;
                    if unsigned(addr) = num_inputs-1 then
                        addr <= (others=>'0');
                    end if;
                end if;
            
            end if;
        end if;
end process LAYER_CNTR;
-------------------------------------------------------------------LAYER_TYPE_ONREC------------------------------------------------------------------------------------
--Description:
--This process determines the type of recovery the layer has to perform to recover its state wheather to recover no data, neurons' output or neurons' internal register
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
LAYER_TYPE_ONREC: process(all) is
begin
    --if rising_edge(clk) then
        if data_rec_busy = '1' then
            if nv_reg_we = '0' then
                if addra = 0 then --We are recovering the first cell, which contains the data_rec_type.
                    --1: nothing 2: outputs 3: internal 4:outputs(finished state)
                    if to_integer(unsigned(nv_reg_dout)) = 2 then
                        data_rec_offset <= num_outputs;
                        data_rec_type <= outputs;
                    elsif to_integer(unsigned(nv_reg_dout)) = 3 then
                        data_rec_offset <= num_outputs+2;
                        data_rec_type <= internal;
                    elsif to_integer(unsigned(nv_reg_dout)) = 1 then
                        data_rec_offset <= 1;
                        data_rec_type <= nothing;
                    elsif to_integer(unsigned(nv_reg_dout)) = 4 then--In this case it is necessary to recover the state of layer which is finished
                        data_rec_offset <= num_outputs+2;
                        data_rec_type <= outputs;
                    else
                        data_rec_offset <= data_rec_offset;
                        data_rec_type <= data_rec_type;
                    end if;
                end if;
            end if;
        else
             data_rec_type <= data_rec_type;
        end if;
    --end if;
end process LAYER_TYPE_ONREC;
-------------------------------------------------------------------LAYER_TYPE_ONSAVE------------------------------------------------------------------------------------
--Description:
--This process determines the type of save the layer has to perform to save its state. Wheather to recover no data, neurons' output or neurons' internal register
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
LAYER_TYPE_ONSAVE: process(all) is
--This process determine weather the layer is:
--1) Currently active
--2) Previous of the currently active layer
--3) Idle layer
--Depending on the type of the layer, we save a different collection of data
begin
    if unsigned(fsm_state_save) = 1 or  unsigned(fsm_state_save)= 2 or  unsigned(fsm_state_save) = 3  then
        --The state of the layer is being computed
        data_save_type <= internal;
        data_save_type_marker <= 3;
    elsif unsigned(fsm_state_save) = 4 then
        data_save_type <= outputs; --because we have to save the content of the output register
        data_save_type_marker <= 4;
    elsif out_v = '1' then
        --The output of the layer has been computed, it has been recovered by the layer 
        --other states and the output is necessary to the next layer
        data_save_type <= outputs;
        data_save_type_marker <= 2;
    else--out_v = '0'
        data_save_type <= nothing;
        data_save_type_marker <= 1;
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
----------------------------------------------DATA_REC COMB LOGIC------------------------------------------------------------------
    data_rec_var_cntr_ce <= data_rec_busy;
    data_rec_var_cntr_init <= not data_rec_busy;
    data_rec_nv_reg_en <= not var_cntr_tc; --the value is still gated by the mux, so if we are not in data_rec the nv_reg is not enabled
-------------------------------------------------------------------------------------------------
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
--Additional comments:
--When a hazard occurs, the architecture first samples the hazard, then at next clock cycle it initializes the data_save process.
--------------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------DATA_SAVE COMBINATIONAL LOGIC-----------------------------------------------
data_save_var_cntr_ce <= data_save_busy;
data_save_var_cntr_init <= not data_save_busy;
data_save_nv_reg_en <= not var_cntr_tc; --the value is still gated by the mux, so if we are not in data_save the nv_reg is not enabled
data_save_nv_reg_we <= '1' when data_save_busy ='1' and var_cntr_tc = '0' else '0';
---------------------------------------------------------------------------------------------------------------------------------------
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

doutb <= data_backup_vect_output_save(addrb) when (data_save_type_marker = 2 or data_save_type_marker = 4) else
            data_backup_vect_internal_save(addrb) when data_save_type_marker = 3 else
                    std_logic_vector(to_unsigned(data_save_type_marker,nv_reg_width));

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

DATA_SAVE_OFFSET: process(data_save_type, data_save_type_marker) is
begin
case data_save_type is
    when internal =>--we never end in this case for save output
        data_save_v_reg_offset <= num_outputs+2;  
    when outputs =>
        if data_save_type_marker = 4 then
            data_save_v_reg_offset <= num_outputs+2;
        else
            data_save_v_reg_offset <= num_outputs;
        end if;
    when nothing =>
    data_save_v_reg_offset <= 0;
end case;
end process DATA_SAVE_OFFSET;



--------------------------------------------------VAR_CNTR process--------------------------------------------------------------------
--------------------------VAR_CNTR PORT ACCESS MULITPLEXER---------------------------------------
    var_cntr_init       <=  data_rec_var_cntr_init          when data_rec_busy = '1'    else
                            data_save_var_cntr_init         when data_save_busy = '1'   else
                            '1'; --default initialize counter
    var_cntr_ce         <=  data_rec_var_cntr_ce            when data_rec_busy = '1'    else
                            data_save_var_cntr_ce           when data_save_busy = '1'   else
                            '0'; --default do not count
    var_cntr_end_value  <=  data_rec_var_cntr_end_value     when data_rec_busy = '1'    else
                            data_save_var_cntr_end_value    when data_save_busy = '1'   else
                            1; --default end value is 1
-------------------------------------------------------------------------------------------------    
----------------------VAR_CNTR process COMBINATORIAL LOGIC----------------------------------
data_rec_var_cntr_end_value <= data_rec_offset + 2;         --the plus two is because a cycle is used to get the first data and then 
                                                                --> the other one just to notify as terminal count cycle
data_save_var_cntr_end_value <= data_save_v_reg_offset + 2; --should be + 1 just for the terminal count clk cycle but +2 because on how the var_cntr_clk ticks
                                                                --> beacuase of this an extra clk cycle will be wasted
------------------------------------------------------------------------------------------------------------------------------------------
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