----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso
-- 
-- Create Date: 02-13-23_22-45-30 
-- Design Name: 
-- Module Name: DNN - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 

-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- It would be nice if it is possible to implement a way to evaluate
-- if it is more convenient to save the output or keep on computing the layer output
-- For example if the number of clock cycles required to save the output equals the ones required
-- to compute the output of the DNN. 
----------------------------------------------------------------------------------


library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;

library work;
use work.I_DNN_package.all;
use work.COMMON_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.INTERMITTENCY_EMULATOR_package.all;

entity I_DNN is
generic(
constant neuron_inout_IntWidth: natural;
constant neuron_inout_FracWidth: natural;
constant neuron_weight_IntWidth: natural;
constant neuron_weight_FracWidth: natural;
constant sigmoid_inputdataWidth: natural;
constant sigmoid_inputdataIntWidth: natural;
constant act_fun_type: string;
constant DNN_prms_path: string 
);
port(
--ORIGINARY PINS
data_in: in sfixed (neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);                      --data_in   : serial input to the DNN.
start: in std_logic;                                                                --start     : signal to trigger the DNN
clk: in std_logic;                                                                  --clk       : system clock
data_out: out sfixed (neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);--data_out  : serial output from the DNN
digit_out: out integer range 0 to 9;                   
data_v: out std_logic;                                                              --data_v    : data validity bit. It aknowledges the availability of data from the DNN
addr_in: out std_logic_vector(0 to natural(ceil(log2(real(layer_inputs(1)))))-1);   --addr_in   : To scan through the valdation data set
--AUGUMENTED PINS
n_power_reset: in std_logic;                                                        --n_power_reset     : reset pin which emulates a power failure                       
data_sampled: in std_logic;
thresh_stats: in threshold_t                                                        --threshold_stats   : this contains the hazard signal to trigger the data save process
); --To scan through the valdation data set
end I_DNN;

architecture Behavioral of I_DNN is
--TYPES-------------------------------------------------
type data_vect_type is array(1 to num_hidden_layers) of sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);
type out_v_set_vect_t is array(1 to num_hidden_layers) of integer range 0 to 3;
--LAYER SIGNALS-----------------------------------------
signal out_v_set_vect: out_v_set_vect_t;
signal data_out_vect, data_in_vect: data_vect_type;
signal start_vect: std_logic_vector(1 to num_hidden_layers);
signal data_in_sel_vect: std_logic_vector(0 to natural(ceil(log2(real(isum(layer_inputs)))))-1);
signal data_out_sel_vect: std_logic_vector(0 to natural(ceil(log2(real(isum(layer_outputs)))))-1);
signal data_v_vect: std_logic_vector(1 to num_hidden_layers):=(others=>'0');
signal data_in_sel1: std_logic_vector(0 to  natural(ceil(log2(real(layer_inputs(1)))))-1);

signal data_out_sel1: std_logic_vector(0 to  natural(ceil(log2(real(layer_outputs(1)))))-1);
signal data_in_sel2: std_logic_vector(0 to  natural(ceil(log2(real(layer_inputs(2)))))-1);

signal data_out_sel2: std_logic_vector(0 to  natural(ceil(log2(real(layer_outputs(2)))))-1);
signal data_in_sel3: std_logic_vector(0 to  natural(ceil(log2(real(layer_inputs(3)))))-1);

signal data_out_sel3: std_logic_vector(0 to  natural(ceil(log2(real(layer_outputs(3)))))-1);
signal data_in_sel4: std_logic_vector(0 to  natural(ceil(log2(real(layer_inputs(4)))))-1);

signal data_out_sel4: std_logic_vector(0 to  natural(ceil(log2(real(layer_outputs(4)))))-1);
--SOFTMAX
signal softmax_data_v: std_logic;
signal softmax_state: softmax_state_t:=power_off;
--INTERMITTENCY EMULATOR---------------------------------
signal resetN_emulator: std_logic;
--FSM_NV_REG SIGNALS-------------------------------------
signal threshold_value      : intermittency_arr_int_type(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0);
signal threshold_compared   : std_logic_vector(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0); 
signal select_threshold     : integer range 0 to INTERMITTENCY_NUM_THRESHOLDS -1; --This is used to select the threshold for power failure
signal task_status          : std_logic;
signal fsm_nv_reg_state, fsm_state_sig: fsm_nv_reg_state_t:=shutdown_s;
--NV_REG_SIGNALS
--NV_REG1
signal nv_reg_busy1:std_logic:='0';
signal nv_reg_busy_sig1: std_logic:='0';
signal nv_reg_dout1: std_logic_vector(nv_reg_width-1 DOWNTO 0):=(others=>'0');
signal previous_layer1:std_logic_vector(nv_reg_width-1 downto 0):=(others=>'0');
signal task_status1:std_logic;
signal nv_reg_en1:std_logic;
signal nv_reg_we1:std_logic;
signal nv_reg_addr1:std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
signal nv_reg_din1:std_logic_vector(nv_reg_width-1 downto 0);
--NV_REG1
signal nv_reg_busy2:std_logic:='0';
signal nv_reg_busy_sig2: std_logic:='0';
signal nv_reg_dout2: std_logic_vector(nv_reg_width-1 DOWNTO 0):=(others=>'0');
signal previous_layer2:std_logic_vector(nv_reg_width-1 downto 0):=(others=>'0');
signal task_status2:std_logic;
signal nv_reg_en2:std_logic;
signal nv_reg_we2:std_logic;
signal nv_reg_addr2:std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
signal nv_reg_din2:std_logic_vector(nv_reg_width-1 downto 0);
--NV_REG1
signal nv_reg_busy3:std_logic:='0';
signal nv_reg_busy_sig3: std_logic:='0';
signal nv_reg_dout3: std_logic_vector(nv_reg_width-1 DOWNTO 0):=(others=>'0');
signal previous_layer3:std_logic_vector(nv_reg_width-1 downto 0):=(others=>'0');
signal task_status3:std_logic;
signal nv_reg_en3:std_logic;
signal nv_reg_we3:std_logic;
signal nv_reg_addr3:std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
signal nv_reg_din3:std_logic_vector(nv_reg_width-1 downto 0);
--NV_REG1
signal nv_reg_busy4:std_logic:='0';
signal nv_reg_busy_sig4: std_logic:='0';
signal nv_reg_dout4: std_logic_vector(nv_reg_width-1 DOWNTO 0):=(others=>'0');
signal previous_layer4:std_logic_vector(nv_reg_width-1 downto 0):=(others=>'0');
signal task_status4:std_logic;
signal nv_reg_en4:std_logic;
signal nv_reg_we4:std_logic;
signal nv_reg_addr4:std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
signal nv_reg_din4:std_logic_vector(nv_reg_width-1 downto 0);
---------------POWER APPROXIMATION (PA) UNITS SIGNALS------------------------
constant num_pwr_states_layer: natural:=4;
constant num_pwr_states_nvreg: natural:=3;
constant num_pwr_states_softmax:natural:=2;
--LAYER1 PA
signal pr_state_layer1: fsm_layer_state_t;
signal power_state_en_layer1				: std_logic_vector(num_pwr_states_layer - 1 downto 0);                              -- array of power state that are enable
signal power_counter_val_layer1				: power_approx_counter_type(num_pwr_states_layer - 1 downto 0) := (others => 0);    -- array of state counter values
signal power_counter_full_layer1		: std_logic_vector(num_pwr_states_layer - 1 downto 0) := (others => '0');           -- array of terminal counters
signal power_counter_reset_layer1		: std_logic_vector(num_pwr_states_layer - 1 downto 0):=(others => '0');             -- array to reset counters
--NVREG1 PA
signal power_state_en_nvreg1          : std_logic_vector(num_pwr_states_nvreg - 1 downto 0);                              -- array of power state that are enable
signal power_counter_val_nvreg1       : power_approx_counter_type(num_pwr_states_nvreg - 1 downto 0) := (others => 0);    -- array of state counter values
signal power_counter_full_nvreg1      : std_logic_vector(num_pwr_states_nvreg - 1 downto 0) := (others => '0');           -- array of terminal counters 
signal power_counter_reset_nvreg1     : std_logic_vector(num_pwr_states_nvreg - 1 downto 0):=(others => '0');                              -- array to reset counters
--LAYER2 PA
signal pr_state_layer2: fsm_layer_state_t;
signal power_state_en_layer2				: std_logic_vector(num_pwr_states_layer - 1 downto 0);                              -- array of power state that are enable
signal power_counter_val_layer2				: power_approx_counter_type(num_pwr_states_layer - 1 downto 0) := (others => 0);    -- array of state counter values
signal power_counter_full_layer2		: std_logic_vector(num_pwr_states_layer - 1 downto 0) := (others => '0');           -- array of terminal counters
signal power_counter_reset_layer2		: std_logic_vector(num_pwr_states_layer - 1 downto 0):=(others => '0');             -- array to reset counters
--NVREG2 PA
signal power_state_en_nvreg2          : std_logic_vector(num_pwr_states_nvreg - 1 downto 0);                              -- array of power state that are enable
signal power_counter_val_nvreg2       : power_approx_counter_type(num_pwr_states_nvreg - 1 downto 0) := (others => 0);    -- array of state counter values
signal power_counter_full_nvreg2      : std_logic_vector(num_pwr_states_nvreg - 1 downto 0) := (others => '0');           -- array of terminal counters 
signal power_counter_reset_nvreg2     : std_logic_vector(num_pwr_states_nvreg - 1 downto 0):=(others => '0');                              -- array to reset counters
--LAYER3 PA
signal pr_state_layer3: fsm_layer_state_t;
signal power_state_en_layer3				: std_logic_vector(num_pwr_states_layer - 1 downto 0);                              -- array of power state that are enable
signal power_counter_val_layer3				: power_approx_counter_type(num_pwr_states_layer - 1 downto 0) := (others => 0);    -- array of state counter values
signal power_counter_full_layer3		: std_logic_vector(num_pwr_states_layer - 1 downto 0) := (others => '0');           -- array of terminal counters
signal power_counter_reset_layer3		: std_logic_vector(num_pwr_states_layer - 1 downto 0):=(others => '0');             -- array to reset counters
--NVREG3 PA
signal power_state_en_nvreg3          : std_logic_vector(num_pwr_states_nvreg - 1 downto 0);                              -- array of power state that are enable
signal power_counter_val_nvreg3       : power_approx_counter_type(num_pwr_states_nvreg - 1 downto 0) := (others => 0);    -- array of state counter values
signal power_counter_full_nvreg3      : std_logic_vector(num_pwr_states_nvreg - 1 downto 0) := (others => '0');           -- array of terminal counters 
signal power_counter_reset_nvreg3     : std_logic_vector(num_pwr_states_nvreg - 1 downto 0):=(others => '0');                              -- array to reset counters
--LAYER4 PA
signal pr_state_layer4: fsm_layer_state_t;
signal power_state_en_layer4				: std_logic_vector(num_pwr_states_layer - 1 downto 0);                              -- array of power state that are enable
signal power_counter_val_layer4				: power_approx_counter_type(num_pwr_states_layer - 1 downto 0) := (others => 0);    -- array of state counter values
signal power_counter_full_layer4		: std_logic_vector(num_pwr_states_layer - 1 downto 0) := (others => '0');           -- array of terminal counters
signal power_counter_reset_layer4		: std_logic_vector(num_pwr_states_layer - 1 downto 0):=(others => '0');             -- array to reset counters
--NVREG4 PA
signal power_state_en_nvreg4          : std_logic_vector(num_pwr_states_nvreg - 1 downto 0);                              -- array of power state that are enable
signal power_counter_val_nvreg4       : power_approx_counter_type(num_pwr_states_nvreg - 1 downto 0) := (others => 0);    -- array of state counter values
signal power_counter_full_nvreg4      : std_logic_vector(num_pwr_states_nvreg - 1 downto 0) := (others => '0');           -- array of terminal counters 
signal power_counter_reset_nvreg4     : std_logic_vector(num_pwr_states_nvreg - 1 downto 0):=(others => '0');                              -- array to reset counters
--SOFTMAX PA
signal power_state_en_softmax          : std_logic_vector(num_pwr_states_softmax - 1 downto 0);                              -- array of power state that are enable
signal power_counter_val_softmax       : power_approx_counter_type(num_pwr_states_softmax - 1 downto 0) := (others => 0);    -- array of state counter values
signal power_counter_full_softmax      : std_logic_vector(num_pwr_states_softmax - 1 downto 0) := (others => '0');           -- array of terminal counters
signal power_counter_reset_softmax     : std_logic_vector(num_pwr_states_softmax - 1 downto 0):=(others => '0');                              -- array to reset counters
--INST_PWR_CALC
--LAYER1 INST_PWR_CALC
signal start_evaluation_layer1          : std_logic:='1';
signal evaluation_ready_layer1          : std_logic;
signal num_state_to_evaluate_layer1     : integer range 0 to num_pwr_states_layer-1:=0;
signal input_counter_val_layer1         : power_approx_counter_type(num_pwr_states_layer -1 downto 0);
signal output_data_layer1               : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0);
--NV_REG1INST_PWR_CALC
signal start_evaluation_nvreg1          : std_logic:='1';
signal evaluation_ready_nvreg1          : std_logic;
signal num_state_to_evaluate_nvreg1     : integer range 0 to num_pwr_states_nvreg-1:=0;
signal input_counter_val_nvreg1         : power_approx_counter_type(num_pwr_states_nvreg -1 downto 0);
signal output_data_nvreg1               : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0);
--LAYER2 INST_PWR_CALC
signal start_evaluation_layer2          : std_logic:='1';
signal evaluation_ready_layer2          : std_logic;
signal num_state_to_evaluate_layer2     : integer range 0 to num_pwr_states_layer-1:=0;
signal input_counter_val_layer2         : power_approx_counter_type(num_pwr_states_layer -1 downto 0);
signal output_data_layer2               : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0);
--NV_REG2INST_PWR_CALC
signal start_evaluation_nvreg2          : std_logic:='1';
signal evaluation_ready_nvreg2          : std_logic;
signal num_state_to_evaluate_nvreg2     : integer range 0 to num_pwr_states_nvreg-1:=0;
signal input_counter_val_nvreg2         : power_approx_counter_type(num_pwr_states_nvreg -1 downto 0);
signal output_data_nvreg2               : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0);
--LAYER3 INST_PWR_CALC
signal start_evaluation_layer3          : std_logic:='1';
signal evaluation_ready_layer3          : std_logic;
signal num_state_to_evaluate_layer3     : integer range 0 to num_pwr_states_layer-1:=0;
signal input_counter_val_layer3         : power_approx_counter_type(num_pwr_states_layer -1 downto 0);
signal output_data_layer3               : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0);
--NV_REG3INST_PWR_CALC
signal start_evaluation_nvreg3          : std_logic:='1';
signal evaluation_ready_nvreg3          : std_logic;
signal num_state_to_evaluate_nvreg3     : integer range 0 to num_pwr_states_nvreg-1:=0;
signal input_counter_val_nvreg3         : power_approx_counter_type(num_pwr_states_nvreg -1 downto 0);
signal output_data_nvreg3               : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0);
--LAYER4 INST_PWR_CALC
signal start_evaluation_layer4          : std_logic:='1';
signal evaluation_ready_layer4          : std_logic;
signal num_state_to_evaluate_layer4     : integer range 0 to num_pwr_states_layer-1:=0;
signal input_counter_val_layer4         : power_approx_counter_type(num_pwr_states_layer -1 downto 0);
signal output_data_layer4               : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0);
--NV_REG4INST_PWR_CALC
signal start_evaluation_nvreg4          : std_logic:='1';
signal evaluation_ready_nvreg4          : std_logic;
signal num_state_to_evaluate_nvreg4     : integer range 0 to num_pwr_states_nvreg-1:=0;
signal input_counter_val_nvreg4         : power_approx_counter_type(num_pwr_states_nvreg -1 downto 0);
signal output_data_nvreg4               : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0);
--SOFTMAX
signal start_evaluation_softmax          : std_logic:='1';
signal evaluation_ready_softmax          : std_logic;
signal num_state_to_evaluate_softmax     : integer range 0 to num_pwr_states_softmax-1:=0;
signal input_counter_val_softmax         : power_approx_counter_type(num_pwr_states_softmax -1 downto 0);
signal output_data_softmax               : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0);
--
--COMPONENTS DECLARATION---------------------------------------------------
--LAYER
component I_layer is
    generic(
constant num_inputs: natural;
constant num_outputs: natural;
constant neuron_inout_IntWidth: natural;
constant neuron_inout_FracWidth: natural;
constant neuron_weight_IntWidth: natural;
constant neuron_weight_FracWidth: natural;
constant layer_no: natural;--Layer number (identifier)
constant act_fun_type: string; -- Choose between "ReLU","Sig"
constant sigmoid_inputdataWidth: natural;
constant sigmoid_inputdataIntWidth: natural;
constant lyr_prms_path: string
);
port(
    ---ORIGINARY PINS----
    ------Inputs---------
    clk: in std_logic;
    data_in: in sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);
    data_out_sel: in std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1);
    start: in std_logic;                                                                
    -------Outputs-------
    data_out: out sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);                 
    data_in_sel: inout std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);  
    data_v: out std_logic;                                                              
    --ADDED PINS---------                                                               
    --------Inputs-------
    n_power_reset: in std_logic;                                                        
    fsm_nv_reg_state: in fsm_nv_reg_state_t;                                            
    nv_reg_busy: in std_logic;                                                          
    nv_reg_busy_sig: in  STD_LOGIC;                                                     
    nv_reg_dout: in STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);                          
    out_v_set: in integer range 0 to 3;                                                 
    -------Outputs-------
    task_status: out std_logic;                                                        
    nv_reg_en: out std_logic;                                                       
    nv_reg_we: out std_logic;                                                   
    nv_reg_addr: out std_logic_vector(nv_reg_addr_width_bit-1 downto 0);    
    nv_reg_din: out STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
    pr_state: out fsm_layer_state_t                           
    );                                                     
end component;
--FSM_NV_REG_DB
component fsm_nv_reg_db is
    port ( 
        clk                     : in STD_LOGIC;
        resetN                  : in STD_LOGIC;
        thresh_stats            : in threshold_t;
        task_status             : in STD_LOGIC;
        fsm_state               : out fsm_nv_reg_state_t;
        fsm_state_sig           : out fsm_nv_reg_state_t 
        );
end component;
--NV_REG
component nv_reg is
    Generic(
        MAX_DELAY_NS: INTEGER;
        NV_REG_WIDTH: INTEGER;
        NV_REG_DEPTH: INTEGER
    );
    Port ( 
        clk             : in STD_LOGIC;
        resetN          : in STD_LOGIC;
        power_resetN 	: in STD_LOGIC;
        -------------change from here--------------
        busy            : out STD_LOGIC;
        busy_sig        : out STD_LOGIC;
        en              : in STD_LOGIC;
        we              : in STD_LOGIC;
        addr            : in STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);
        din             : in STD_LOGIC_VECTOR(31 DOWNTO 0);
        dout            : out STD_LOGIC_VECTOR(31 DOWNTO 0)
        -------------change to here---------------- 
    );
end component;
component SOFT_MAX is
generic(
num_inputs: natural := 10
);
port(
--INPUTS
clk: in std_logic;
start: in std_logic;
data_in: in sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);
data_sampled: in std_logic;
n_power_reset: in std_logic;
--OUTPUTS
data_in_sel: out std_logic_vector(natural(ceil(log2(real(num_inputs))))-1 downto 0);
out_v: out std_logic;
data_out: out sfixed(neuron_inout_IntWidth-1 downto -neuron_inout_FracWidth);
digit_out: out integer range 0 to 9;
softmax_state: out softmax_state_t
);
end component;
component power_approximation is
    generic(
        pwr_states_num          :natural
        );
    port(
        sys_clk                 : in std_logic; -- system clock
        power_state_en          : in std_logic_vector(pwr_states_num - 1 downto 0); -- array of power state that are enable
        power_counter_val       : out power_approx_counter_type(pwr_states_num - 1 downto 0) := (others => 0); -- array of state counter values
        power_counter_full      : out std_logic_vector(pwr_states_num - 1 downto 0) := (others => '0'); -- array of terminal counters 
        power_counter_reset     : in std_logic_vector(pwr_states_num - 1 downto 0) -- array to reset counters
    );
end component;
component instant_pwr_calc is
    generic(
        pwr_states_num              :natural;
        type_device                 :string
    );
    port (
        sys_clk                 : in std_logic; -- system clock
        start_evaluation        : in std_logic; -- start evaluation signal 
        evaluation_ready        : out std_logic; -- evaluation ready singal 
        num_state_to_evaluate   : in integer range 0 to pwr_states_num-1; -- number of state to evaluate
        input_counter_val       : in power_approx_counter_type(pwr_states_num -1 downto 0); -- array of each state counter
        output_data             : out std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0) -- output data
    );
end component;

begin

--Data Path
--Data
data_in_vect(1) <= data_in;
data_in_vect(2) <= data_out_vect(1);
data_in_vect(3) <= data_out_vect(2);
data_in_vect(4) <= data_out_vect(3);
--Aknowledges Bits
start_vect(1) <= start;
start_vect(2) <= data_v_vect(1);
start_vect(3) <= data_v_vect(2);
start_vect(4) <= data_v_vect(3);
--Data Selectors
addr_in <= data_in_sel1;
data_out_sel1<= data_in_sel2;
data_out_sel2<= data_in_sel3;
data_out_sel3<= data_in_sel4;
data_v <= softmax_data_v;
--Reset bit
resetN_emulator <= n_power_reset;
--TASK STATUS bit
task_status <= task_status1 or task_status2 or task_status3 or task_status4;
--out_v_set PROCESS
--Description: This process computes the out_v_set bit feeding the layer, in order to invalidate the output of that layer.
out_v_set_val: process(all) is
begin
--Layer1
if data_v_vect(2) = '0' then
    out_v_set_vect(1) <= 2;
elsif data_v_vect(2) = '1' then
    out_v_set_vect(1) <= 1;
end if;
--Layer2
if data_v_vect(3) = '0' then
    out_v_set_vect(2) <= 2;
elsif data_v_vect(3) = '1' then
    out_v_set_vect(2) <= 1;
end if;
--Layer3
if data_v_vect(4) = '0' then
    out_v_set_vect(3) <= 2;
elsif data_v_vect(4) = '1' then
    out_v_set_vect(3) <= 1;
end if;
--Layer3
if softmax_data_v = '0' then
    out_v_set_vect(4) <= 2;
elsif softmax_data_v = '1' then
    out_v_set_vect(4) <= 1;
end if;
--out_v_set_vect(3) <= out_v_set;
end process out_v_set_val;
--COMPONENT INSTANTIATION
--FMS_NV_REG_DB_COMP
fsm_nv_reg_db_comp: fsm_nv_reg_db
    port map(
        clk             => clk,
        resetN          => resetN_emulator,
        thresh_stats    => thresh_stats,
        task_status     => task_status,
        fsm_state       => fsm_nv_reg_state,
        fsm_state_sig   => fsm_state_sig
    );
--LAYER1
--NVREG
nv_reg_comp1: nv_reg
    Generic map(
        MAX_DELAY_NS => FRAM_MAX_DELAY_NS,
        NV_REG_WIDTH => NV_REG_WIDTH,
        NV_REG_DEPTH => NV_REG_DEPTH
    )
    Port map(
        clk             => clk,
        resetN          => '1',
        power_resetN 	=> resetN_emulator,
        -------------chage from here--------------
        busy            => nv_reg_busy1,
        busy_sig        => nv_reg_busy_sig1,
        en              => nv_reg_en1,
        we              => nv_reg_we1,
        addr            => nv_reg_addr1,
        din             => nv_reg_din1,
        dout            => nv_reg_dout1
        -------------chage to here----------------
        );
--LAYER
I_layer1: I_layer
    generic map(
    num_inputs => layer_inputs(1),
    num_outputs => layer_outputs(1),
neuron_inout_IntWidth => neuron_inout_IntWidth,
neuron_inout_FracWidth => neuron_inout_FracWidth,
neuron_weight_IntWidth => neuron_weight_IntWidth,
neuron_weight_FracWidth => neuron_weight_FracWidth,
    layer_no => 1,
    act_fun_type => "ReLU",
sigmoid_inputdataWidth=> 5,
sigmoid_inputdataIntWidth=> 2,
lyr_prms_path => DNN_prms_path
    )
    port map(
    --ORIGINARY PINS
    --Input
    clk => clk,
    data_in => data_in_vect(1),
    data_out_sel => data_out_sel1,
    start => start_vect(1),
    --Output
    data_out => data_out_vect(1),
    data_in_sel => data_in_sel1,
    data_v => data_v_vect(1),
    --ADDED PINS
    --Inputs
    n_power_reset => n_power_reset,
    fsm_nv_reg_state => fsm_nv_reg_state,
    nv_reg_busy => nv_reg_busy1,
    nv_reg_busy_sig => nv_reg_busy_sig1,
    nv_reg_dout => nv_reg_dout1,
    out_v_set => out_v_set_vect(1),
    --Outputs
    task_status => task_status1,
    nv_reg_en => nv_reg_en1,
    nv_reg_we => nv_reg_we1,
    nv_reg_addr => nv_reg_addr1,
    nv_reg_din => nv_reg_din1,
    pr_state => pr_state_layer1

    );
--LAYER2
--NVREG
nv_reg_comp2: nv_reg
    Generic map(
        MAX_DELAY_NS => FRAM_MAX_DELAY_NS,
        NV_REG_WIDTH => NV_REG_WIDTH,
        NV_REG_DEPTH => NV_REG_DEPTH
    )
    Port map(
        clk             => clk,
        resetN          => '1',
        power_resetN 	=> resetN_emulator,
        -------------chage from here--------------
        busy            => nv_reg_busy2,
        busy_sig        => nv_reg_busy_sig2,
        en              => nv_reg_en2,
        we              => nv_reg_we2,
        addr            => nv_reg_addr2,
        din             => nv_reg_din2,
        dout            => nv_reg_dout2
        -------------chage to here----------------
        );
--LAYER
I_layer2: I_layer
    generic map(
    num_inputs => layer_inputs(2),
    num_outputs => layer_outputs(2),
neuron_inout_IntWidth => neuron_inout_IntWidth,
neuron_inout_FracWidth => neuron_inout_FracWidth,
neuron_weight_IntWidth => neuron_weight_IntWidth,
neuron_weight_FracWidth => neuron_weight_FracWidth,
    layer_no => 2,
    act_fun_type => "ReLU",
sigmoid_inputdataWidth=> 5,
sigmoid_inputdataIntWidth=> 2,
lyr_prms_path => DNN_prms_path
    )
    port map(
    --ORIGINARY PINS
    --Input
    clk => clk,
    data_in => data_in_vect(2),
    data_out_sel => data_out_sel2,
    start => start_vect(2),
    --Output
    data_out => data_out_vect(2),
    data_in_sel => data_in_sel2,
    data_v => data_v_vect(2),
    --ADDED PINS
    --Inputs
    n_power_reset => n_power_reset,
    fsm_nv_reg_state => fsm_nv_reg_state,
    nv_reg_busy => nv_reg_busy2,
    nv_reg_busy_sig => nv_reg_busy_sig2,
    nv_reg_dout => nv_reg_dout2,
    out_v_set => out_v_set_vect(2),
    --Outputs
    task_status => task_status2,
    nv_reg_en => nv_reg_en2,
    nv_reg_we => nv_reg_we2,
    nv_reg_addr => nv_reg_addr2,
    nv_reg_din => nv_reg_din2,
    pr_state => pr_state_layer2

    );
--LAYER3
--NVREG
nv_reg_comp3: nv_reg
    Generic map(
        MAX_DELAY_NS => FRAM_MAX_DELAY_NS,
        NV_REG_WIDTH => NV_REG_WIDTH,
        NV_REG_DEPTH => NV_REG_DEPTH
    )
    Port map(
        clk             => clk,
        resetN          => '1',
        power_resetN 	=> resetN_emulator,
        -------------chage from here--------------
        busy            => nv_reg_busy3,
        busy_sig        => nv_reg_busy_sig3,
        en              => nv_reg_en3,
        we              => nv_reg_we3,
        addr            => nv_reg_addr3,
        din             => nv_reg_din3,
        dout            => nv_reg_dout3
        -------------chage to here----------------
        );
--LAYER
I_layer3: I_layer
    generic map(
    num_inputs => layer_inputs(3),
    num_outputs => layer_outputs(3),
neuron_inout_IntWidth => neuron_inout_IntWidth,
neuron_inout_FracWidth => neuron_inout_FracWidth,
neuron_weight_IntWidth => neuron_weight_IntWidth,
neuron_weight_FracWidth => neuron_weight_FracWidth,
    layer_no => 3,
    act_fun_type => "ReLU",
sigmoid_inputdataWidth=> 5,
sigmoid_inputdataIntWidth=> 2,
lyr_prms_path => DNN_prms_path
    )
    port map(
    --ORIGINARY PINS
    --Input
    clk => clk,
    data_in => data_in_vect(3),
    data_out_sel => data_out_sel3,
    start => start_vect(3),
    --Output
    data_out => data_out_vect(3),
    data_in_sel => data_in_sel3,
    data_v => data_v_vect(3),
    --ADDED PINS
    --Inputs
    n_power_reset => n_power_reset,
    fsm_nv_reg_state => fsm_nv_reg_state,
    nv_reg_busy => nv_reg_busy3,
    nv_reg_busy_sig => nv_reg_busy_sig3,
    nv_reg_dout => nv_reg_dout3,
    out_v_set => out_v_set_vect(3),
    --Outputs
    task_status => task_status3,
    nv_reg_en => nv_reg_en3,
    nv_reg_we => nv_reg_we3,
    nv_reg_addr => nv_reg_addr3,
    nv_reg_din => nv_reg_din3,
    pr_state => pr_state_layer3

    );
--LAYER4
--NVREG
nv_reg_comp4: nv_reg
    Generic map(
        MAX_DELAY_NS => FRAM_MAX_DELAY_NS,
        NV_REG_WIDTH => NV_REG_WIDTH,
        NV_REG_DEPTH => NV_REG_DEPTH
    )
    Port map(
        clk             => clk,
        resetN          => '1',
        power_resetN 	=> resetN_emulator,
        -------------chage from here--------------
        busy            => nv_reg_busy4,
        busy_sig        => nv_reg_busy_sig4,
        en              => nv_reg_en4,
        we              => nv_reg_we4,
        addr            => nv_reg_addr4,
        din             => nv_reg_din4,
        dout            => nv_reg_dout4
        -------------chage to here----------------
        );
--LAYER
I_layer4: I_layer
    generic map(
    num_inputs => layer_inputs(4),
    num_outputs => layer_outputs(4),
neuron_inout_IntWidth => neuron_inout_IntWidth,
neuron_inout_FracWidth => neuron_inout_FracWidth,
neuron_weight_IntWidth => neuron_weight_IntWidth,
neuron_weight_FracWidth => neuron_weight_FracWidth,
    layer_no => 4,
    act_fun_type => "ReLU",
sigmoid_inputdataWidth=> 5,
sigmoid_inputdataIntWidth=> 2,
lyr_prms_path => DNN_prms_path
    )
    port map(
    --ORIGINARY PINS
    --Input
    clk => clk,
    data_in => data_in_vect(4),
    data_out_sel => data_out_sel4,
    start => start_vect(4),
    --Output
    data_out => data_out_vect(4),
    data_in_sel => data_in_sel4,
    data_v => data_v_vect(4),
    --ADDED PINS
    --Inputs
    n_power_reset => n_power_reset,
    fsm_nv_reg_state => fsm_nv_reg_state,
    nv_reg_busy => nv_reg_busy4,
    nv_reg_busy_sig => nv_reg_busy_sig4,
    nv_reg_dout => nv_reg_dout4,
    out_v_set => out_v_set_vect(4),
    --Outputs
    task_status => task_status4,
    nv_reg_en => nv_reg_en4,
    nv_reg_we => nv_reg_we4,
    nv_reg_addr => nv_reg_addr4,
    nv_reg_din => nv_reg_din4,
    pr_state => pr_state_layer4

    );
soft_max_comp: SOFT_MAX
generic map(
num_inputs => 10
)
port map(
clk => clk,
start => data_v_vect(4),
data_in => data_out_vect(4),
data_sampled => data_sampled,
n_power_reset => n_power_reset,
data_in_sel => data_out_sel4,
out_v => softmax_data_v,
data_out => data_out,
digit_out => digit_out,
softmax_state => softmax_state
);
pwr_appr_comp_layer1: power_approximation
generic map(
    pwr_states_num => num_pwr_states_layer
)
port map(
        sys_clk                 => clk,
        power_state_en          => power_state_en_layer1,
        power_counter_val       => power_counter_val_layer1,
        power_counter_full      => power_counter_full_layer1,
        power_counter_reset     => power_counter_reset_layer1
);
pwr_appr_comp_nvreg1: power_approximation
generic map(
    pwr_states_num => num_pwr_states_nvreg
)
port map(
        sys_clk                 => clk,
        power_state_en          => power_state_en_nvreg1,
        power_counter_val       => power_counter_val_nvreg1,
        power_counter_full      => power_counter_full_nvreg1,
        power_counter_reset     => power_counter_reset_nvreg1
);
pwr_appr_comp_layer2: power_approximation
generic map(
    pwr_states_num => num_pwr_states_layer
)
port map(
        sys_clk                 => clk,
        power_state_en          => power_state_en_layer2,
        power_counter_val       => power_counter_val_layer2,
        power_counter_full      => power_counter_full_layer2,
        power_counter_reset     => power_counter_reset_layer2
);
pwr_appr_comp_nvreg2: power_approximation
generic map(
    pwr_states_num => num_pwr_states_nvreg
)
port map(
        sys_clk                 => clk,
        power_state_en          => power_state_en_nvreg2,
        power_counter_val       => power_counter_val_nvreg2,
        power_counter_full      => power_counter_full_nvreg2,
        power_counter_reset     => power_counter_reset_nvreg2
);
pwr_appr_comp_layer3: power_approximation
generic map(
    pwr_states_num => num_pwr_states_layer
)
port map(
        sys_clk                 => clk,
        power_state_en          => power_state_en_layer3,
        power_counter_val       => power_counter_val_layer3,
        power_counter_full      => power_counter_full_layer3,
        power_counter_reset     => power_counter_reset_layer3
);
pwr_appr_comp_nvreg3: power_approximation
generic map(
    pwr_states_num => num_pwr_states_nvreg
)
port map(
        sys_clk                 => clk,
        power_state_en          => power_state_en_nvreg3,
        power_counter_val       => power_counter_val_nvreg3,
        power_counter_full      => power_counter_full_nvreg3,
        power_counter_reset     => power_counter_reset_nvreg3
);
pwr_appr_comp_layer4: power_approximation
generic map(
    pwr_states_num => num_pwr_states_layer
)
port map(
        sys_clk                 => clk,
        power_state_en          => power_state_en_layer4,
        power_counter_val       => power_counter_val_layer4,
        power_counter_full      => power_counter_full_layer4,
        power_counter_reset     => power_counter_reset_layer4
);
pwr_appr_comp_nvreg4: power_approximation
generic map(
    pwr_states_num => num_pwr_states_nvreg
)
port map(
        sys_clk                 => clk,
        power_state_en          => power_state_en_nvreg4,
        power_counter_val       => power_counter_val_nvreg4,
        power_counter_full      => power_counter_full_nvreg4,
        power_counter_reset     => power_counter_reset_nvreg4
);
pwr_appr_comp_softmax: power_approximation
generic map(
    pwr_states_num => num_pwr_states_softmax
)
port map(
        sys_clk                 => clk,
        power_state_en          => power_state_en_softmax,
        power_counter_val       => power_counter_val_softmax,
        power_counter_full      => power_counter_full_softmax,
        power_counter_reset     => power_counter_reset_softmax
);
input_counter_val_layer1 <= power_counter_val_layer1;
inst_pwr_calc_comp_layer1: instant_pwr_calc
    generic map(
        pwr_states_num => num_pwr_states_layer,
        type_device => "layer"
    )
    port map(
        sys_clk                 => clk,
        start_evaluation        => start_evaluation_layer1,
        evaluation_ready        => evaluation_ready_layer1,
        num_state_to_evaluate   => num_state_to_evaluate_layer1,
        input_counter_val       => input_counter_val_layer1,
        output_data             => output_data_layer1
    );
input_counter_val_nvreg1 <= power_counter_val_nvreg1;
inst_pwr_calc_comp_nvreg1: instant_pwr_calc
    generic map(
        pwr_states_num => num_pwr_states_nvreg,
        type_device => "nvreg"
    )
    port map(
        sys_clk                 => clk,
        start_evaluation        => start_evaluation_nvreg1,
        evaluation_ready        => evaluation_ready_nvreg1,
        num_state_to_evaluate   => num_state_to_evaluate_nvreg1,
        input_counter_val       => input_counter_val_nvreg1,
        output_data             => output_data_nvreg1
    );input_counter_val_layer2 <= power_counter_val_layer2;
inst_pwr_calc_comp_layer2: instant_pwr_calc
    generic map(
        pwr_states_num => num_pwr_states_layer,
        type_device => "layer"
    )
    port map(
        sys_clk                 => clk,
        start_evaluation        => start_evaluation_layer2,
        evaluation_ready        => evaluation_ready_layer2,
        num_state_to_evaluate   => num_state_to_evaluate_layer2,
        input_counter_val       => input_counter_val_layer2,
        output_data             => output_data_layer2
    );
input_counter_val_nvreg2 <= power_counter_val_nvreg2;
inst_pwr_calc_comp_nvreg2: instant_pwr_calc
    generic map(
        pwr_states_num => num_pwr_states_nvreg,
        type_device => "nvreg"
    )
    port map(
        sys_clk                 => clk,
        start_evaluation        => start_evaluation_nvreg2,
        evaluation_ready        => evaluation_ready_nvreg2,
        num_state_to_evaluate   => num_state_to_evaluate_nvreg2,
        input_counter_val       => input_counter_val_nvreg2,
        output_data             => output_data_nvreg2
    );input_counter_val_layer3 <= power_counter_val_layer3;
inst_pwr_calc_comp_layer3: instant_pwr_calc
    generic map(
        pwr_states_num => num_pwr_states_layer,
        type_device => "layer"
    )
    port map(
        sys_clk                 => clk,
        start_evaluation        => start_evaluation_layer3,
        evaluation_ready        => evaluation_ready_layer3,
        num_state_to_evaluate   => num_state_to_evaluate_layer3,
        input_counter_val       => input_counter_val_layer3,
        output_data             => output_data_layer3
    );
input_counter_val_nvreg3 <= power_counter_val_nvreg3;
inst_pwr_calc_comp_nvreg3: instant_pwr_calc
    generic map(
        pwr_states_num => num_pwr_states_nvreg,
        type_device => "nvreg"
    )
    port map(
        sys_clk                 => clk,
        start_evaluation        => start_evaluation_nvreg3,
        evaluation_ready        => evaluation_ready_nvreg3,
        num_state_to_evaluate   => num_state_to_evaluate_nvreg3,
        input_counter_val       => input_counter_val_nvreg3,
        output_data             => output_data_nvreg3
    );input_counter_val_layer4 <= power_counter_val_layer4;
inst_pwr_calc_comp_layer4: instant_pwr_calc
    generic map(
        pwr_states_num => num_pwr_states_layer,
        type_device => "layer"
    )
    port map(
        sys_clk                 => clk,
        start_evaluation        => start_evaluation_layer4,
        evaluation_ready        => evaluation_ready_layer4,
        num_state_to_evaluate   => num_state_to_evaluate_layer4,
        input_counter_val       => input_counter_val_layer4,
        output_data             => output_data_layer4
    );
input_counter_val_nvreg4 <= power_counter_val_nvreg4;
inst_pwr_calc_comp_nvreg4: instant_pwr_calc
    generic map(
        pwr_states_num => num_pwr_states_nvreg,
        type_device => "nvreg"
    )
    port map(
        sys_clk                 => clk,
        start_evaluation        => start_evaluation_nvreg4,
        evaluation_ready        => evaluation_ready_nvreg4,
        num_state_to_evaluate   => num_state_to_evaluate_nvreg4,
        input_counter_val       => input_counter_val_nvreg4,
        output_data             => output_data_nvreg4
    );input_counter_val_softmax <= power_counter_val_softmax;
inst_pwr_calc_comp_softmax: instant_pwr_calc
    generic map(
        pwr_states_num => num_pwr_states_softmax,
        type_device => "softmax"
    )
    port map(
        sys_clk                 => clk,
        start_evaluation        => start_evaluation_softmax,
        evaluation_ready        => evaluation_ready_softmax,
        num_state_to_evaluate   => num_state_to_evaluate_softmax,
        input_counter_val       => input_counter_val_softmax,
        output_data             => output_data_softmax
    );    


power_states_gen: process(all) is 
begin

----------LAYER1------------
if pr_state_layer1 = power_off then
    power_state_en_layer1 <= (others => '0');
elsif pr_state_layer1 = idle or pr_state_layer1 = init or pr_state_layer1 = data_save_init or pr_state_layer1 = data_save_init_cmpl then
    power_state_en_layer1 <= (others => '0');
    power_state_en_layer1(0) <= '1';
elsif pr_state_layer1 = w_sum or pr_state_layer1 = b_sum or pr_state_layer1 = act_log or pr_state_layer1 = finished then
    power_state_en_layer1 <= (others => '0');
    power_state_en_layer1(1) <= '1';
elsif pr_state_layer1 = data_save then
    power_state_en_layer1 <= (others => '0');
    power_state_en_layer1(2) <= '1';
elsif pr_state_layer1 = recovery then
    power_state_en_layer1 <= (others => '0');
    power_state_en_layer1(3) <= '1';
end if;
--NVREG1
if pr_state_layer1 = power_off then
    power_state_en_nvreg1 <= (others => '0');
elsif nv_reg_en1 = '0' then
    power_state_en_nvreg1(0) <= '1';
    power_state_en_nvreg1(1) <= '0';
    power_state_en_nvreg1(2) <= '0';
else
    power_state_en_nvreg1(0) <= '1';
    power_state_en_nvreg1(1) <= '1';
    if nv_reg_we1 = '1' then
        power_state_en_nvreg1(2) <= '1';
    else
        power_state_en_nvreg1(2) <= '0';
    end if;
end if;
----------LAYER2------------
if pr_state_layer2 = power_off then
    power_state_en_layer2 <= (others => '0');
elsif pr_state_layer2 = idle or pr_state_layer2 = init or pr_state_layer2 = data_save_init or pr_state_layer2 = data_save_init_cmpl then
    power_state_en_layer2 <= (others => '0');
    power_state_en_layer2(0) <= '1';
elsif pr_state_layer2 = w_sum or pr_state_layer2 = b_sum or pr_state_layer2 = act_log or pr_state_layer2 = finished then
    power_state_en_layer2 <= (others => '0');
    power_state_en_layer2(1) <= '1';
elsif pr_state_layer2 = data_save then
    power_state_en_layer2 <= (others => '0');
    power_state_en_layer2(2) <= '1';
elsif pr_state_layer2 = recovery then
    power_state_en_layer2 <= (others => '0');
    power_state_en_layer2(3) <= '1';
end if;
--NVREG2
if pr_state_layer2 = power_off then
    power_state_en_nvreg2 <= (others => '0');
elsif nv_reg_en2 = '0' then
    power_state_en_nvreg2(0) <= '1';
    power_state_en_nvreg2(1) <= '0';
    power_state_en_nvreg2(2) <= '0';
else
    power_state_en_nvreg2(0) <= '1';
    power_state_en_nvreg2(1) <= '1';
    if nv_reg_we2 = '1' then
        power_state_en_nvreg2(2) <= '1';
    else
        power_state_en_nvreg2(2) <= '0';
    end if;
end if;
----------LAYER3------------
if pr_state_layer3 = power_off then
    power_state_en_layer3 <= (others => '0');
elsif pr_state_layer3 = idle or pr_state_layer3 = init or pr_state_layer3 = data_save_init or pr_state_layer3 = data_save_init_cmpl then
    power_state_en_layer3 <= (others => '0');
    power_state_en_layer3(0) <= '1';
elsif pr_state_layer3 = w_sum or pr_state_layer3 = b_sum or pr_state_layer3 = act_log or pr_state_layer3 = finished then
    power_state_en_layer3 <= (others => '0');
    power_state_en_layer3(1) <= '1';
elsif pr_state_layer3 = data_save then
    power_state_en_layer3 <= (others => '0');
    power_state_en_layer3(2) <= '1';
elsif pr_state_layer3 = recovery then
    power_state_en_layer3 <= (others => '0');
    power_state_en_layer3(3) <= '1';
end if;
--NVREG3
if pr_state_layer3 = power_off then
    power_state_en_nvreg3 <= (others => '0');
elsif nv_reg_en3 = '0' then
    power_state_en_nvreg3(0) <= '1';
    power_state_en_nvreg3(1) <= '0';
    power_state_en_nvreg3(2) <= '0';
else
    power_state_en_nvreg3(0) <= '1';
    power_state_en_nvreg3(1) <= '1';
    if nv_reg_we3 = '1' then
        power_state_en_nvreg3(2) <= '1';
    else
        power_state_en_nvreg3(2) <= '0';
    end if;
end if;
----------LAYER4------------
if pr_state_layer4 = power_off then
    power_state_en_layer4 <= (others => '0');
elsif pr_state_layer4 = idle or pr_state_layer4 = init or pr_state_layer4 = data_save_init or pr_state_layer4 = data_save_init_cmpl then
    power_state_en_layer4 <= (others => '0');
    power_state_en_layer4(0) <= '1';
elsif pr_state_layer4 = w_sum or pr_state_layer4 = b_sum or pr_state_layer4 = act_log or pr_state_layer4 = finished then
    power_state_en_layer4 <= (others => '0');
    power_state_en_layer4(1) <= '1';
elsif pr_state_layer4 = data_save then
    power_state_en_layer4 <= (others => '0');
    power_state_en_layer4(2) <= '1';
elsif pr_state_layer4 = recovery then
    power_state_en_layer4 <= (others => '0');
    power_state_en_layer4(3) <= '1';
end if;
--NVREG4
if pr_state_layer4 = power_off then
    power_state_en_nvreg4 <= (others => '0');
elsif nv_reg_en4 = '0' then
    power_state_en_nvreg4(0) <= '1';
    power_state_en_nvreg4(1) <= '0';
    power_state_en_nvreg4(2) <= '0';
else
    power_state_en_nvreg4(0) <= '1';
    power_state_en_nvreg4(1) <= '1';
    if nv_reg_we4 = '1' then
        power_state_en_nvreg4(2) <= '1';
    else
        power_state_en_nvreg4(2) <= '0';
    end if;
end if;
--SOFTMAX
if softmax_state = power_off then
    power_state_en_softmax <= (others => '0');
elsif softmax_state = idle then
    power_state_en_softmax <= (others => '0');
    power_state_en_softmax(0) <= '1';
elsif softmax_state = active or softmax_state = finished then
    power_state_en_softmax <= (others => '0');
    power_state_en_softmax(1) <= '1';
end if;


end process;




evaluation_gen_process: process(evaluation_ready_layer1,start_evaluation_layer1) is

begin
if rising_edge(evaluation_ready_layer1) then
    start_evaluation_layer1 <= '0' after 20 ns;
    num_state_to_evaluate_layer1 <= num_state_to_evaluate_layer1 +1;
    if num_state_to_evaluate_layer1 = num_pwr_states_layer-1 then
        num_state_to_evaluate_layer1 <= 0;
    end if;
end if;
if rising_edge(evaluation_ready_nvreg1)  then
    start_evaluation_nvreg1 <= '0' after 20 ns;
    num_state_to_evaluate_nvreg1 <= num_state_to_evaluate_nvreg1 +1;
    if num_state_to_evaluate_nvreg1 = num_pwr_states_nvreg-1 then
        num_state_to_evaluate_nvreg1 <= 0;
    end if;
end if;
if rising_edge(evaluation_ready_layer2) then
    start_evaluation_layer2 <= '0' after 20 ns;
    num_state_to_evaluate_layer2 <= num_state_to_evaluate_layer2 +1;
    if num_state_to_evaluate_layer2 = num_pwr_states_layer-1 then
        num_state_to_evaluate_layer2 <= 0;
    end if;
end if;
if rising_edge(evaluation_ready_nvreg2)  then
    start_evaluation_nvreg2 <= '0' after 20 ns;
    num_state_to_evaluate_nvreg2 <= num_state_to_evaluate_nvreg2 +1;
    if num_state_to_evaluate_nvreg2 = num_pwr_states_nvreg-1 then
        num_state_to_evaluate_nvreg2 <= 0;
    end if;
end if;
if rising_edge(evaluation_ready_layer3) then
    start_evaluation_layer3 <= '0' after 20 ns;
    num_state_to_evaluate_layer3 <= num_state_to_evaluate_layer3 +1;
    if num_state_to_evaluate_layer3 = num_pwr_states_layer-1 then
        num_state_to_evaluate_layer3 <= 0;
    end if;
end if;
if rising_edge(evaluation_ready_nvreg3)  then
    start_evaluation_nvreg3 <= '0' after 20 ns;
    num_state_to_evaluate_nvreg3 <= num_state_to_evaluate_nvreg3 +1;
    if num_state_to_evaluate_nvreg3 = num_pwr_states_nvreg-1 then
        num_state_to_evaluate_nvreg3 <= 0;
    end if;
end if;
if rising_edge(evaluation_ready_layer4) then
    start_evaluation_layer4 <= '0' after 20 ns;
    num_state_to_evaluate_layer4 <= num_state_to_evaluate_layer4 +1;
    if num_state_to_evaluate_layer4 = num_pwr_states_layer-1 then
        num_state_to_evaluate_layer4 <= 0;
    end if;
end if;
if rising_edge(evaluation_ready_nvreg4)  then
    start_evaluation_nvreg4 <= '0' after 20 ns;
    num_state_to_evaluate_nvreg4 <= num_state_to_evaluate_nvreg4 +1;
    if num_state_to_evaluate_nvreg4 = num_pwr_states_nvreg-1 then
        num_state_to_evaluate_nvreg4 <= 0;
    end if;
end if;
if start_evaluation_layer1 = '0' then
start_evaluation_layer1 <= '1' after 320 ns;
start_evaluation_nvreg1 <= '1' after 320 ns;
start_evaluation_layer2 <= '1' after 320 ns;
start_evaluation_nvreg2 <= '1' after 320 ns;
start_evaluation_layer3 <= '1' after 320 ns;
start_evaluation_nvreg3 <= '1' after 320 ns;
start_evaluation_layer4 <= '1' after 320 ns;
start_evaluation_nvreg4 <= '1' after 320 ns;
start_evaluation_softmax <= '1' after 320 ns;
end if;
if rising_edge(evaluation_ready_softmax) then
    start_evaluation_softmax <= '0' after 20 ns;
    num_state_to_evaluate_softmax <= num_state_to_evaluate_softmax +1;
    if num_state_to_evaluate_softmax = num_pwr_states_softmax-1 then
        num_state_to_evaluate_softmax <= 0;
    end if;
end if;






end process;



end Behavioral;
