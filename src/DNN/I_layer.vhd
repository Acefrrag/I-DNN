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
--1)Circuit to discern weather it's necessary to RECOVER the state, output or nothing. And route the correct signals FROM the nv_reg

library ieee_proposed;
use ieee_proposed.fixed_pkg.all;


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
use ieee.math_real.all;


library work;
use work.I_DNN_package.all;
--Augumented Packages
use work.COMMON_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;


entity I_layer is
generic(
    constant num_inputs: natural := 30;
    constant num_outputs: natural := 30;
    constant layer_no: natural := 0;--Layer number (identifier)
    constant act_type: string := "ReLU"; -- Choose between "ReLU","Sig"
    constant act_fun_size: natural := 10 -- If the user choose an analytical activation function the number of sample have to be chosen
);
port(
    clk: in std_logic;
    data_in: in sfixed(input_int_width-1 downto -input_frac_width);
    data_out_sel: in std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1);
    start: in std_logic;--to increment the counter while the output of the output is begin computed
    data_out: out sfixed(neuron_int_width-1 downto -neuron_frac_width);--The next layer controls which neuron's output to access
    data_in_sel: out std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1);
    data_v: out std_logic;
    --Augumented Pins
    --Input
    n_power_reset: in std_logic;
    fsm_nv_reg_state: in fsm_nv_reg_state_t;
    nv_reg_busy: in std_logic;
    nv_reg_busy_sig: in  STD_LOGIC;
    nv_reg_dout: in STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
    save_output: in std_logic;--To decide wheather to save or not the output
    --Output
    task_status: out std_logic;
    nv_reg_en: out std_logic;
    nv_reg_we: out std_logic;
    nv_reg_addr: out std_logic_vector(nv_reg_addr_width_bit-1 downto 0);
    nv_reg_din: out STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
    save_state: out std_logic);--This is high when the layer is the currently active
end I_layer;


architecture Behavioral of I_layer is
type rom_type is array (0 to num_inputs-1) of sfixed(neuron_int_width-1 downto -neuron_frac_width);
type data_out_type is array(0 to num_outputs-1) of sfixed(neuron_int_width-1 downto -neuron_frac_width);
type data_backup_state_type is array(0 to num_outputs+2) of std_logic_vector(nv_reg_width-1 downto 0); --data grouping for saving state(weighted_sum, fsm_state, addr_gen)
type data_backup_output_type is array(0 to num_outputs+2) of std_logic_vector(nv_reg_width-1 downto 0); --data gropuing for saving output (the last two wire are not connected to anything)
type backup_type_t is (state, output, nothing);

--signal data_out_sel: std_logic_vector(0 to natural(ceil(log2(real(num_outputs))))-1):=(others=>'0');
signal addr: std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1) :=(others => '0');
signal rst: std_logic := '1';
signal data_out_vect: data_out_type;
signal out_v_vect: std_logic_vector(0 to num_outputs-1):=(others => '0');
signal addr_TC: std_logic := '0';
signal sum_reg_rst: std_logic;
signal mul_sel: std_logic; 
signal out_v: std_logic; 
signal update_out: std_logic;
signal addr_in_gen_rst: std_logic;
signal data_in_d: sfixed(input_int_width-1 downto -input_frac_width);
signal weighted_sum: sfixed(input_int_width+neuron_int_width downto -input_frac_width-neuron_frac_width);
------------------CONSTANTS--------------------------
constant bits_addrb: natural := natural(ceil(log2(real(num_outputs+2))));--to access data_backup_vect_state_save and data_backup_vect_output_save

-------------------------------VAR SIGNALS--------------------------------------------
signal fsm_state_rec: std_logic_vector(0 to nv_reg_width-1);
signal s_r: integer range 0 to num_outputs+1; --activation pins for recovery of the state
signal o_r: integer range 0 to num_outputs+1; --activation pins for recovery of the outputs (last 2 are unused)
signal addra: integer range 0 to num_outputs+2; --address to access the data grouping when recovering data
signal fsm_state_save: std_logic_vector(0 to nv_reg_width-1); --To save the state of the fsm of the layer
signal addrb: integer range 0 to num_outputs+2; --address to access the data grouping when saving data
-------------------------------GROUPING LAYER SIGNALS--------------------------------------------
--Data Path for saving layer state/output
signal data_backup_vect_state_save, data_backup_vect_state_rec: data_backup_state_type; --These are connected to the save and rec inputs for backing up layer state
signal data_backup_vect_output_save, data_backup_vect_output_rec: data_backup_output_type; --These are connected to the save and rec inputs for backing up layer output
signal o_rec_vect, w_rec_vect: std_logic_vector(0 to num_outputs-1); --Recovery enable bits. The i-th element enables overwriting the w_sum or the out_reg of the corresponding neuron. It is used during the recovery of data. 
signal backup_type: backup_type_t;--State, Output, Nothing
signal doutb: std_logic_vector(nv_reg_width-1 downto 0);
--------------------------------------------------------------------------------------
-------------------------------COMMON_SIGNALS-----------------------------------------
signal dina     : std_logic_vector(31 DOWNTO 0);
signal task_status_internal: STD_LOGIC;
--------------------------------------------------------------------------------------
-------------------------------DATA_REC_SIGNALS---------------------------------------  
signal data_rec_busy: STD_LOGIC;
signal data_rec_nv_reg_en: STD_LOGIC;  
signal data_rec_nv_reg_we: STD_LOGIC;  
signal data_rec_nv_reg_din: STD_LOGIC_VECTOR( 31 DOWNTO 0);
signal data_rec_nv_reg_addr : STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);
signal data_rec_var_cntr_init :STD_LOGIC;
signal data_rec_var_cntr_ce: STD_LOGIC;
signal data_rec_var_cntr_end_value : INTEGER;   
--------------------------------------------------------------------------------------
-------------------------------DATA_SAVE_SIGNALS------------------------------------------- 
signal data_save_busy: STD_LOGIC;
signal data_save_nv_reg_en: STD_LOGIC;
signal data_save_nv_reg_we: STD_LOGIC;
signal data_save_nv_reg_din: STD_LOGIC_VECTOR( 31 DOWNTO 0);
signal data_save_nv_reg_addr : STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);
signal data_save_var_cntr_init :STD_LOGIC;
signal data_save_var_cntr_ce: STD_LOGIC;
signal data_save_var_cntr_end_value : INTEGER;    
--------------------------------------------------------------------------------------
-------------------------------VAR_COUNTER_SIGNALS------------------------------------
signal var_cntr_clk,var_cntr_init,var_cntr_ce,var_cntr_tc: STD_LOGIC;
signal var_cntr_value, var_cntr_value_last,var_cntr_end_value: INTEGER range 0 to NV_REG_WIDTH+2;
--------------------------------------------------------------------------------------   
--------------------------------------------------DATA_REC process-------------------------------------------------------------------
signal data_rec_nv_reg_start_addr: STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);	--address from which start recovering data in nv_reg
signal data_rec_v_reg_start_addr: STD_LOGIC_VECTOR(v_reg_addr_width_bit-1 DOWNTO 0);    --addres in v_reg from which the recovered data (#ofdata=data_rec_offset) will be stored
signal data_rec_offset: INTEGER RANGE 0 TO NV_REG_WIDTH-1;					            --the offset used to calculate the last address recovered from nv_reg in data recovery process
signal data_rec_type: data_rec_type_t := nothing;                                                                                       --> ex: if we have 3 consecutive WORDS saved in nv_reg that we want to recover then data_rec_offset = 2
signal data_rec_recovered_data : STD_LOGIC_VECTOR( 31 DOWNTO 0);                        --the data recovered from nv_reg after recovery starts
signal data_rec_recovered_offset: INTEGER RANGE 0 TO NV_REG_WIDTH -1;                   --the offset associated to data_rec_recovered_data when in recovery, used to know which WORD from nv_reg data_rec_recovered_data is.
--signal data_rec_recovered_offset_last : INTEGER RANGE 0 TO NV_REG_WIDTH-1;              --shift register used to sinchronize the offset of the recovered data with the recovered data data
--------------------------------------------------DATA_SAVE process-------------------------------------------------------------------
signal data_save_nv_reg_start_addr: STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);	--start address (in nv_reg) from which the data save process will save volatile values
signal data_save_v_reg_start_addr: STD_LOGIC_VECTOR(v_reg_addr_width_bit-1 DOWNTO 0);   --start address (in bram aka volatile register) from which the data save process will fetch data
                                                                                        --> this address is where the first WORD of volatile data (that will be lost after power failure) is stored
signal data_save_v_reg_offset : INTEGER RANGE 0 TO V_REG_WIDTH -1;				        --the offset used to calculate the last address of v_reg (aka volatile register) for data save process
                                                                                        --> ex: if we have 2 consecutive WORDS saved in v_reg that we want to store in nv_reg then data_save_v_reg_offset=1
-- this upper signal can change during the vol_cntr process. 
-- For example after a power failure we could want to retrive the old data and then save the values in a different place in nv_reg (thus changing data_save_nv_reg_start_addr).
-- Or we could only want to recover a subset of the data stored in nv_reg (thus changing data_rec_nv_reg_start_addr and data_rec_offset).
-- This could be implemented in hw by using an eeprom to store this values or the nv_reg itself by keeping this data in a std and first access location for the executing process.
--------------------------------------------------V_REG_RESET process------------------------------------------------------------------
signal v_reg_reset_ena      : std_logic;
signal v_reg_reset_wea      : std_logic_vector(0 DOWNTO 0);
signal v_reg_reset_addra    : std_logic_vector(v_reg_addr_width_bit-1 DOWNTO 0);
signal v_reg_reset_dina     : std_logic_vector(31 DOWNTO 0);
-----------------------------------------------------------------------------------------------------------------------------------
signal mul_sel_backup       : integer range 1 to 3:= 1;

component I_FSM_layer is
generic (
num_outputs: natural;
rom_depth: natural);--the number of summations in the weighted sum will be 16-1=15
port(clk: in std_logic; 
    addr_TC: in std_logic; --This bit indicates if we are feeding the neuron with the last input
    start: in std_logic; --This signal initiate the neuron computation
    sum_reg_rst: out std_logic; --This bit resets the weighted sum register
    mul_sel: out std_logic; --This signal decides weather to add up the product w_i*x_i or the bias b
    out_v: out std_logic; --This signal aknowledge the output is valid
    update_out: out std_logic;
    addr_in_gen_rst: out std_logic;
    --Augumented Pins
    --Input pins
    n_power_rst: in std_logic;
    data_rec_busy: in std_logic;
    fsm_nv_reg_state: in fsm_nv_reg_state_t;
    fsm_state_rec: in std_logic_vector(0 to nv_reg_width-1);-- To recover the state of the fsm
    data_rec_recovered_offset: in integer range 0 to num_outputs+1; 
    --Output Pins
    s_r: out std_logic_vector(0 to num_outputs+1); --activation pins for recovery of the state
    o_r: out std_logic_vector(0 to num_outputs+1); --activation pins for recovery of the outputs (last 2 are unused)
    addra: out integer range 0 to num_outputs+2;
    fsm_state_save: out std_logic_vector(0 to nv_reg_width-1) --To save the state of the fsm of the layer
    ); --This updates the output of the neuron, since it is necessary to  
end component;

component var_counter is --This is used to count the elements being accessed inside the nv_reg.
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
end component;




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

determine_layer_type: process is
--This process determine weather the layer is:
--1) Currently active 2) Previous of the currently active layer 3) Idle layer
begin
    if (unsigned(fsm_state_save) = 1) or (unsigned(fsm_state_save) = 2) or (unsigned(fsm_state_save) = 3) then
        mul_sel_backup <= 1;
        --Also, we need to set the number of elements to retrieve from the nv_reg
        --In case it's nothing we oinly need to write to the first element of the nv_reg
        data_rec_offset <= num_outputs+2+2;
    elsif save_output = '1' then
        mul_sel_backup <= 2;
        data_rec_offset <= num_outputs+2;
    else
        mul_sel_backup <= 3;
        data_rec_offset <= 2;
    end if;

end process;

I_fsm_layer_comp: I_FSM_layer
generic map(
num_outputs => num_outputs,
rom_depth => num_inputs
)
port map(
    clk => clk,
    addr_TC => addr_TC, --This bit indicates if we are feeding the neuron with the last input
    start => start,  --This signal initiate the neuron computation
    sum_reg_rst => sum_reg_rst, --This bit resets the weighted sum register
    mul_sel => mul_sel,  --This signal decides weather to add up the product w_i*x_i or the bias b
    out_v => out_v,--This signal aknowledge the output is valid
    update_out => update_out,
    addr_in_gen_rst => addr_in_gen_rst,
    --Augumented Pins
    --Input pins
    n_power_rst => n_power_reset,
    data_rec_busy => data_rec_busy,
    fsm_nv_reg_state => fsm_nv_reg_state,
    fsm_state_rec => fsm_state_rec,
    data_rec_recovered_offset => data_rec_recovered_offset,
    --Output pins
    o_r => o_rec_vect,
    s_r => w_rec_vect,
    addra => addra,
    fsm_state_save => fsm_state_save

    ); --This update the output of the neuron, since it is necessary to  
 

task_status <= data_rec_busy OR data_save_busy;
--addra = 0, data_rec_type is begin fetched
--addra = 1..num_outputs neurons' registers are being fetched
--addra = end-1..end addr_gen and fsm_state are begin fetched
data_backup_vect_state_rec(addra) <= data_rec_recovered_data; --Data to be written to one of the volatile registers
data_backup_vect_output_rec(addra) <= data_rec_recovered_data;

   
data_v <= out_v;

rst <= addr_in_gen_rst;
data_in_sel <= addr;
--rst <= 
gen_addr: process(clk,rst) is --This process generate the address to access the neuron weight and get the input from the previous layer
begin
   -- if rst = '1' then
    --    addr <= '0';
   -- else
        if rst = '1' then
            addr <= (others => '0');
        else
            if rising_edge(clk) then
                addr <= std_logic_vector(unsigned(addr) + 1);
                if unsigned(addr) = num_inputs-1 then
                    addr <= (others=>'0');
                    addr_TC <= '1';
                else
                    addr_TC <= '0';
                end if;
            end if;
        end if;    
    --end if;
end process gen_addr;


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
            weighted_sum: out sfixed(input_int_width+neuron_int_width downto -neuron_frac_width-input_frac_width);
            data_out: out sfixed (input_int_width-1 downto -input_frac_width);
            --Augumented Pins
            n_power_reset: in std_logic;
            w_rec: in std_logic;
            o_rec: in std_logic;
            data_out_rec: in sfixed (input_int_width-1 downto -input_frac_width);
            weighted_sum_save: out std_logic_vector(input_int_width+neuron_int_width+input_frac_width+neuron_frac_width-1 downto 0);
            weighted_sum_rec: in sfixed (input_int_width+neuron_int_width-1 downto -input_frac_width-neuron_frac_width)
            );
    end component;
    begin
        I_neuron_i: I_neuron
        generic map(
        rom_width => neuron_rom_width,
        rom_depth => num_inputs,
        weight_file => "../scripts/weights_and_bias/w_b/w_" & integer'image(layer_no)&"_"&integer'image(i)&".mif",
        bias_file => "../../../../../../scripts/weights_and_bias/w_b/b_" & integer'image(layer_no)&"_"&integer'image(i)&".mif")
        port map(
        clk => clk,
        data_in =>data_in,
        addr =>data_in_sel,        
        mul_sel => mul_sel,
        sum_reg_rst => sum_reg_rst,
        update_out => update_out,
        weighted_sum => weighted_sum,
        data_out => data_out_vect(i),
        --Augumunted Pins
        n_power_reset => n_power_reset,
        o_rec => o_rec_vect(i),
        w_rec => w_rec_vect(i),
        data_out_rec => to_sfixed(data_backup_vect_output_rec(i+1)(input_int_width+input_frac_width-1 downto 0) ,input_int_width, input_frac_width), --use data convertion
        weighted_sum_save => data_backup_vect_state_save(i+1),
        weighted_sum_rec => to_sfixed(data_backup_vect_state_rec(i+1), input_int_width+neuron_int_width, input_frac_width+neuron_frac_width)
    
        );
end generate;




--num_outputs = 30 => data_out_sel = 5 2^5=32
--Output logic
data_out<=data_out_vect(to_integer(unsigned(data_out_sel)));
--data_out_sel_pr: process(clk,out_v_vect) is
--begin
--    if out_v_vect(0) ='0' then
--        data_out_sel <= (others => '0');
--    else
--        if rising_edge(clk) then
--            if out_v_vect(0) = '1' then
--            data_out_sel <= std_logic_vector(unsigned(data_out_sel) + 1);
--                if unsigned(data_out_sel)=num_outputs-1 then
--                    data_out_sel <= (others => '0');
--                end if;
--            end if;
--        end if;
--    end if;
--end process data_out_sel_pr;

input_reg: process(clk) is
begin
    if rising_edge(clk) then
        data_in_d <= data_in;
        --start_d <= start;
    end if;
end process input_reg;


--------------------------------------------------DATA_SAVE process-------------------------------------------------------------------
--%%%%%%%%%%%%%%%%%%% DATA_SAVE COMB LOGIC %%%%%%%%%%%%%%%%%%%%%%
data_save_var_cntr_ce <= data_save_busy;
data_save_var_cntr_init <= not data_save_busy;
data_save_nv_reg_en <= not var_cntr_tc; --the value is still gated by the mux, so if we are not in data_save the nv_reg is not enabled
--data_save_nv_reg_we <= (OTHERS => '1') when data_save_busy ='1' and var_cntr_tc = '0' and var_cntr_value > 0 else (OTHERS => '0');
data_save_nv_reg_we <= '1' when data_save_busy ='1' and var_cntr_tc = '0' else '0';
--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
DATA_SAVE_V_REG_SIG_CNTRL: process (clk,data_save_busy) is
begin
    if data_save_busy ='0' then
        addrb <= 0;
    elsif rising_edge(clk) then
       if nv_reg_busy = '0' then    -- when nv_reg turns busy the content of addrb must be available, given this premise, 
                                    --> change the value when it is captured as no more busy 
            if (var_cntr_value <= data_save_v_reg_offset ) then
                addrb <= var_cntr_value;
            end if;
        end if;
    end if;
end process DATA_SAVE_V_REG_SIG_CNTRL;

--doutb must be replaced by the i-th element of the data group
--data_backup_vect_state_save
--data_backup_vect_output_save
--doutb will be connected to either of this signal depending of what we are saving
doutb <= data_backup_vect_state_save(addrb) when mul_sel_backup = 1 else
         data_backup_vect_output_save(addrb) when mul_sel_backup = 2 else
                    std_logic_vector(to_unsigned(mul_sel_backup,nv_reg_width));
        
DATA_SAVE_NV_REG_SIG: process (clk,data_save_busy) is
begin
    if data_save_busy ='0' then
        data_save_nv_reg_din <= doutb;
        data_save_nv_reg_addr <= (others => '0'); --data_save_nv_reg_start_addr;
    elsif rising_edge(clk) then
       if nv_reg_busy_sig = '0' and nv_reg_busy = '1' then --capture the nv_reg signals at the start cycle and keep them constant
            if (var_cntr_value <= data_save_v_reg_offset) then
                data_save_nv_reg_din <= doutb;
                data_save_nv_reg_addr <= std_logic_vector(   unsigned(data_save_nv_reg_start_addr) + 
                                                            to_unsigned(var_cntr_value,nv_reg_addr_width_bit)  
                                                        );
            end if;
        end if;
    end if;
    
end process DATA_SAVE_NV_REG_SIG;

------------------------------------------------DATA_REC process-------------------------------------------------------------------
-- Doc:
--      this process and its brothers are concernd of data recovery from non volatile register. The recovered data and its amount 
--      can be defined by changing the constants in VOL_ARC CONSTANTS subsection of this code. The recovered data can be obtained 
--      by combining the information carried by: data_rec_recovered_data, data_rec_recovered_offset. This is necessary because
--      from request to offer there are delays expecially from NV_REG.

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
            end if; 
        end if;
    end process DATA_REC;

DATA_REC_V_REG_SIG_CNTRL: process(clk,data_rec_busy) is
begin
   if (data_rec_busy = '0') then 
       data_rec_recovered_offset <= 0;
       data_rec_recovered_data <= (OTHERS => '0');
   elsif (rising_edge(clk)) then
       if(nv_reg_busy ='0') then
           if(var_cntr_value > 0 AND var_cntr_value <= data_rec_offset + 1 ) then -- the plus one is used because the data is moved into a shift register for siyncronization purposes
               data_rec_recovered_data <= nv_reg_dout;
               data_rec_recovered_offset <= var_cntr_value_last;
           end if;
       end if;
   end if;
end process DATA_REC_V_REG_SIG_CNTRL;


DATA_REC_RECOVERY_SIGNALS_CNTRL: process is
--This process determines weather to recover output, state or nothing
begin
if data_rec_busy = '1' then
    if unsigned(addr) = 0 then
        if unsigned(data_rec_recovered_data) = 0 then
            data_rec_type <= nothing;
        elsif unsigned(data_rec_recovered_data) = 1 then
            data_rec_type <= state;
        elsif unsigned(data_rec_recovered_data) = 2 then
            data_rec_type <= outputt;
        end if;
    else
        data_rec_type <= data_rec_type;
    end if;
else --When we're not recovering data data_rec_type is nothing
    data_rec_type <= nothing;
end if;
    
        
end process DATA_REC_RECOVERY_SIGNALS_CNTRL;

--------------------------------------------------VAR_CNTR process--------------------------------------------------------------------
-- Doc:
--
--    

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