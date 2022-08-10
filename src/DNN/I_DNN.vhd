----------------------------------------------------------------------------------
-- Company: 
-- Engineer: Michele Pio Fragasso
-- 
-- Create Date: 04/18/2022 09:21:01 PM
-- Design Name: 
-- Module Name: DNN - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: This vhdl file instantiate the intermittent architecture of the DNN. This vhdl is generated with a python script, therefore if you need to modify this file, you have
-- to change the python script.
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

entity I_DNN is
port(
--ORIGINARY PINS
data_in: in sfixed (data_int_width-1 downto -data_frac_width);                      --data_in   : serial input to the DNN.
start: in std_logic;                                                                --start     : signal to trigger the DNN
clk: in std_logic;                                                                  --clk       : system clock
data_out: out sfixed (data_int_width-1 downto -data_frac_width);                    --data_out  : serial output from the DNN
data_v: out std_logic;                                                              --data_v    : data validity bit. It aknowledges the availability of data from the DNN  
addr_in: out std_logic_vector(0 to natural(ceil(log2(real(layer_inputs(1)))))-1);   --addr_in   : To scan through the valdation data set
addr_out: out std_logic_vector(0 to natural(ceil(log2(real(layer_outputs(3)))))-1); --addr_out  : To scan through the output of the DNN
--AUGUMENTED PINS
n_power_reset: in std_logic;                                                        --n_power_reset     : reset pin which emulates a power failure                                         
out_inv: in integer range 0 to 3;                                                   --out_inv           : output invalidity bit. This is used to invalidate the output of the                                                                                                   --     last layer, to prevent the DNN to save useless data. 
thresh_stats: in threshold_t                                                        --threshold_stats   : this contains the hazard signal to trigger the data save process
); --To scan through the valdation data set
end I_DNN;

architecture Behavioral of I_DNN is
--TYPES-------------------------------------------------
type data_vect_type is array(1 to num_layers) of sfixed(data_int_width-1 downto -data_frac_width);
type out_inv_vect_t is array(1 to num_layers) of integer range 0 to 3;
--LAYER SIGNALS-----------------------------------------
signal out_inv_vect: out_inv_vect_t;
signal data_out_vect, data_in_vect: data_vect_type;
signal start_vect: std_logic_vector(1 to num_layers);
signal data_in_sel_vect: std_logic_vector(0 to natural(ceil(log2(real(isum(layer_inputs)))))-1);
signal data_out_sel_vect: std_logic_vector(0 to natural(ceil(log2(real(isum(layer_outputs)))))-1);
signal data_v_vect: std_logic_vector(1 to num_layers):=(others=>'0');
signal data_in_sel1: std_logic_vector(0 to  natural(ceil(log2(real(layer_inputs(1)))))-1);
signal data_out_sel1: std_logic_vector(0 to  natural(ceil(log2(real(layer_outputs(1)))))-1);
signal data_in_sel2: std_logic_vector(0 to  natural(ceil(log2(real(layer_inputs(2)))))-1);
signal data_out_sel2: std_logic_vector(0 to  natural(ceil(log2(real(layer_outputs(2)))))-1);
signal data_in_sel3: std_logic_vector(0 to  natural(ceil(log2(real(layer_inputs(3)))))-1);
signal data_out_sel3: std_logic_vector(0 to  natural(ceil(log2(real(layer_outputs(3)))))-1);
--INTERMITTENCY EMULATOR---------------------------------
signal resetN_emulator: std_logic;
--FSM_NV_REG SIGNALS-------------------------------------
signal threshold_value      : intermittency_arr_int_type(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0);
signal threshold_compared   : std_logic_vector(INTERMITTENCY_NUM_THRESHOLDS - 1 downto 0); 
signal select_threshold     : integer range 0 to INTERMITTENCY_NUM_THRESHOLDS -1; --This is used to select the threshold for power failure
signal task_status          :std_logic;
signal fsm_nv_reg_state, fsm_state_sig: fsm_nv_reg_state_t:=shutdown_s;
--NV_REG_SIGNALS
--Layer1
signal nv_reg_busy1: std_logic:='0';
signal nv_reg_busy_sig1:  std_logic:='0';
signal nv_reg_dout1: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0):=(others=>'0');
signal previous_layer1: std_logic:='0';--To decide wheather to save or not the output
signal task_status1:std_logic;
signal nv_reg_en1: std_logic;
signal nv_reg_we1: std_logic;
signal nv_reg_addr1: std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
signal nv_reg_din1: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
--Layer2
signal nv_reg_busy2: std_logic:='0';
signal nv_reg_busy_sig2:  std_logic:='0';
signal nv_reg_dout2: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0):=(others=>'0');
signal previous_layer2: std_logic:='0';--To decide wheather to save or not the output
signal task_status2:std_logic;
signal nv_reg_en2: std_logic;
signal nv_reg_we2: std_logic;
signal nv_reg_addr2: std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
signal nv_reg_din2: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
--Layer3
signal nv_reg_busy3: std_logic:='0';
signal nv_reg_busy_sig3:  std_logic:='0';
signal nv_reg_dout3: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0):=(others=>'0');
signal previous_layer3: std_logic:='0';--To decide wheather to save or not the output
signal task_status3:std_logic;
signal nv_reg_en3: std_logic;
signal nv_reg_we3: std_logic;
signal nv_reg_addr3: std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
signal nv_reg_din3: STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
--COMPONENTS DECLARATION---------------------------------------------------
--LAYER
component I_layer is
    generic(
    constant num_inputs: natural;
    constant num_outputs: natural;
    constant layer_no: natural;--Layer number (identifier)
    constant act_type: string; -- Choose between "ReLU","Sig"
    constant act_fun_size: natural -- If the user choose an analytical activation function the number of sample have to be chosen
    );
port(
    ---ORIGINARY PINS----
    ------Inputs---------
    clk: in std_logic;                                                                  
    data_in: in sfixed(input_int_width-1 downto -input_frac_width);                     
    data_out_sel: in std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1);   
    start: in std_logic;                                                                
    -------Outputs-------
    data_out: out sfixed(neuron_int_width-1 downto -neuron_frac_width);                 
    data_in_sel: inout std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);  
    data_v: out std_logic;                                                              
    --ADDED PINS---------                                                                                                                                                                        
    --------Inputs-------
    n_power_reset: in std_logic;                                                        
    fsm_nv_reg_state: in fsm_nv_reg_state_t;                                            
    nv_reg_busy: in std_logic;                                                          
    nv_reg_busy_sig: in  STD_LOGIC;                                                     
    nv_reg_dout: in STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);                          
    out_inv: in integer range 0 to 3;                                                                                                                                          
    -------Outputs-------
    task_status: out std_logic;                                                        
    nv_reg_en: out std_logic;                                                       
    nv_reg_we: out std_logic;                                                   
    nv_reg_addr: out std_logic_vector(nv_reg_addr_width_bit-1 downto 0);    
    nv_reg_din: out STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0)                           
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
        NV_REG_WIDTH: INTEGER
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
        addr            : in STD_LOGIC_VECTOR(integer(ceil(log2(real(NV_REG_WIDTH))))-1 DOWNTO 0);
        din             : in STD_LOGIC_VECTOR(31 DOWNTO 0);
        dout            : out STD_LOGIC_VECTOR(31 DOWNTO 0)
        -------------change to here---------------- 
    );
end component;

begin

--Data Path
--Data
data_in_vect(1) <= data_in;
data_in_vect(2) <= data_out_vect(1);
data_in_vect(3) <= data_out_vect(2);
data_out <= data_out_vect(3);
--Aknowledges Bits
start_vect(1) <= start;
start_vect(2) <= data_v_vect(1);
start_vect(3) <= data_v_vect(2);
--Data Selectors
addr_in <= data_in_sel1;
data_out_sel1 <= data_in_sel2;
data_out_sel2 <= data_in_sel3;
data_out_sel3 <= addr_out;
data_v <= data_v_vect(3);
--Reset bit
resetN_emulator <= n_power_reset;
--TASK STATUS bit
task_status <= task_status1 or task_status2 or task_status3;
--OUT_INV PROCESS
--Description: This process computes the out_inv bit feeding the layer, in order to invalidate the output of that layer.
out_inv_val: process(data_v_vect) is
begin
--Layer1
if data_v_vect(2) = '0' then
    out_inv_vect(1) <= 2;
elsif data_v_vect(2) = '1' then
    out_inv_vect(1) <= 1;
end if;
--Layer2
if data_v_vect(3) = '0' then
    out_inv_vect(2) <= 2;
elsif data_v_vect(3) = '1' then
    out_inv_vect(2) <= 1;
end if;
--Layer3
out_inv_vect(3) <= out_inv;
end process out_inv_val;
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
        NV_REG_WIDTH => NV_REG_WIDTH
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
    layer_no => 1,
    act_type => "ReLU", 
    act_fun_size => 0
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
    out_inv => out_inv_vect(1),
    --Outputs
    task_status => task_status1,
    nv_reg_en => nv_reg_en1,
    nv_reg_we => nv_reg_we1,
    nv_reg_addr => nv_reg_addr1,
    nv_reg_din => nv_reg_din1
    );                                                     
--LAYER2
--NVREG
nv_reg_comp2: nv_reg
    Generic map(
        MAX_DELAY_NS => FRAM_MAX_DELAY_NS,
        NV_REG_WIDTH => NV_REG_WIDTH
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
        ------------------ to here---------------- 
        );
--LAYER
I_layer2: I_layer
    generic map(
    num_inputs => layer_inputs(2),
    num_outputs => layer_outputs(2),
    layer_no => 2,
    act_type => "ReLU", 
    act_fun_size => 0
    )
    port map(
    clk => clk,                                                               
    data_in => data_in_vect(2),                  
    data_out_sel => data_out_sel2,  
    start => start_vect(2),                               
                                                  
    data_out => data_out_vect(2),                 
    data_in_sel => data_in_sel2,  
    data_v => data_v_vect(2),                                                                                                                                                 
                                                                                                                                                                             
    --Augumented Pins
    --Inputs                                                                                       
    n_power_reset => n_power_reset,
    fsm_nv_reg_state => fsm_nv_reg_state,
    nv_reg_busy => nv_reg_busy2,
    nv_reg_busy_sig => nv_reg_busy_sig2,
    nv_reg_dout => nv_reg_dout2,
    out_inv => out_inv_vect(2),
    --Outputs
    task_status => task_status2,
    nv_reg_en => nv_reg_en2,
    nv_reg_we => nv_reg_we2,
    nv_reg_addr => nv_reg_addr2,
    nv_reg_din => nv_reg_din2
    ); 
--LAYER3
--NVREG
nv_reg_comp3: nv_reg
    Generic map(
        MAX_DELAY_NS => FRAM_MAX_DELAY_NS,
        NV_REG_WIDTH => NV_REG_WIDTH
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
    layer_no => 3,
    act_type => "ReLU", 
    act_fun_size => 0
    )
    port map(
    clk => clk,                                                               
    data_in => data_in_vect(3),                  
    data_out_sel => data_out_sel3,  
    start => start_vect(3),                               
                                                  
    data_out => data_out_vect(3),                 
    data_in_sel => data_in_sel3,  
    data_v => data_v_vect(3),                                                                                                                                                 
                                                                                                                                                                             
    --Augumented Pins
    --Inputs                                                                                       
    n_power_reset => n_power_reset,
    fsm_nv_reg_state => fsm_nv_reg_state,
    nv_reg_busy => nv_reg_busy3,
    nv_reg_busy_sig => nv_reg_busy_sig3,
    nv_reg_dout => nv_reg_dout3,
    out_inv => out_inv_vect(3),
    --Outputs
    task_status => task_status3,
    nv_reg_en => nv_reg_en3,
    nv_reg_we => nv_reg_we3,
    nv_reg_addr => nv_reg_addr3,
    nv_reg_din => nv_reg_din3
    ); 

end Behavioral;
