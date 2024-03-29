----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/10/2020 10:36:33 PM
-- Design Name: 
-- Module Name: INSTANT_PWR_CALC - Behavioral
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
--Revision 0.02 - Power Model setup
-- Comments: The power model has been set up in this module but it is
--implemented offline inside the evaluation python scripts.
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

use work.COMMON_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;

entity instant_pwr_calc is
    generic(
        pwr_states_num              :natural:=3;
        type_device                 :string:="layer"
    );
    port (
        sys_clk                 : in std_logic; -- system clock
        start_evaluation        : in std_logic; -- start evaluation signal 
        evaluation_ready        : out std_logic; -- evaluation ready singal 
        num_state_to_evaluate   : in integer range 0 to pwr_states_num-1; -- number of state to evaluate
        input_counter_val       : in power_approx_counter_type(pwr_states_num -1 downto 0); -- array of each state counter
        output_data             : out std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS + PWR_CONSUMPTION_ROM_BITS-1 downto 0) -- output data
    );
end instant_pwr_calc;

architecture Behavioral of instant_pwr_calc is

    --- ROM component declaration ---
    component PWR_CONSUMPTION_VAL_ROM is
        generic(
            NUM_ELEMENTS_ROM    : integer;
            MAX_VAL             : integer;
            type_device         : string:="layer"
        );
        port(	
            clk       : in	std_logic;
            addr      : in	integer range 0 to NUM_ELEMENTS_ROM - 1;
            data_out  : out	integer range 0 to MAX_VAL - 1
        );
    end component;
    
    --- multiplier component declaration ---
    COMPONENT mult
        PORT (
            A           : IN STD_LOGIC_VECTOR(PWR_APPROX_COUNTER_NUM_BITS - 1 DOWNTO 0);
            B           : IN STD_LOGIC_VECTOR(PWR_CONSUMPTION_ROM_BITS - 1 DOWNTO 0);
            P           : OUT STD_LOGIC_VECTOR(PWR_APPROX_COUNTER_NUM_BITS+PWR_CONSUMPTION_ROM_BITS-1 DOWNTO 0)
        );
    END COMPONENT;

    --- MULTIPLIER SIGNALS ---
    signal SCLR : std_logic := '0';
    signal P : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS+PWR_CONSUMPTION_ROM_BITS-1 downto 0);
    signal CE : std_logic := '0';
    
    --- COUNTER SIGNALS ---
    signal input_counter_val_std_logic_vector : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS -1 downto 0) := (others => '0');
    signal input_counter_val_std_logic_vector_FF : std_logic_vector(PWR_APPROX_COUNTER_NUM_BITS -1 downto 0) := (others => '0');
    signal sample_input_counter_val_std_logic_vector : std_logic := '0';
    
    --- ROM ---
    signal ROM_addr_FF : integer range 0 to NUM_PWR_STATES - 1;
    signal sample_ROM_addr : std_logic := '0';
    signal ROM_data_out  : integer range 0 to 2**PWR_CONSUMPTION_ROM_BITS - 1;
    signal ROM_data_out_std_logic_vector : std_logic_vector(PWR_CONSUMPTION_ROM_BITS - 1 downto 0);
    
    --- FSM SIGNALS --- 
    type instant_pwr_calc_state is(
        wait_state,
        wait_ROM_data_state,
        wait_evaluation_state_1,
        wait_evaluation_state_2,
        wait_evaluation_state_3,
        wait_evaluation_state_4,
        data_ready_state
    );
    signal instant_pwr_calc_present_state, instant_pwr_calc_future_state : instant_pwr_calc_state := wait_state; 
    
begin
    
    --- DATA-FLOW ---
    input_counter_val_std_logic_vector <= std_logic_vector(to_unsigned(input_counter_val(num_state_to_evaluate),PWR_APPROX_COUNTER_NUM_BITS));
    ROM_data_out_std_logic_vector <= std_logic_vector(to_unsigned(ROM_data_out, PWR_CONSUMPTION_ROM_BITS));
    output_data <= P;

    --- ROM INSTANCE ---
    PWR_CONSUMPTION_VAL_ROM_comp : PWR_CONSUMPTION_VAL_ROM
        generic map(
            NUM_ELEMENTS_ROM => NUM_PWR_STATES,
            MAX_VAL => 2**PWR_CONSUMPTION_ROM_BITS,
            type_device => type_device
        )
        port map(
            clk => sys_clk,
            addr => ROM_addr_FF,
            data_out => ROM_data_out
        );

    --- MULTIPLIER INSTANCE --- 
    MULTIPLIER_0 : mult
        port map(
            A => input_counter_val_std_logic_vector_FF,
            B => ROM_data_out_std_logic_vector,
            P => P
        );
        
    --- SEQUANTIAL FSM ---
    fsm_seq : process(sys_clk) begin
		if rising_edge(sys_clk) then
            instant_pwr_calc_present_state <= instant_pwr_calc_future_state; -- change state
		end if;
	end process;
	
	--- COMBINATORY FSM --
    fsm_comb : process(instant_pwr_calc_present_state, start_evaluation) begin
        -- default values ---
        instant_pwr_calc_future_state <= instant_pwr_calc_present_state;
        CE <= '0';
        sample_ROM_addr <= '0';
        sample_input_counter_val_std_logic_vector <= '0';
        evaluation_ready <= '0';
        case instant_pwr_calc_present_state is
            when wait_state =>
                if start_evaluation = '1' then
                    -- if start_evaluation = '1' then change state
                    instant_pwr_calc_future_state <= wait_ROM_data_state;
                    
                    --- start sampling ---
                    sample_input_counter_val_std_logic_vector <= '1'; -- sample counter val
                    sample_ROM_addr <= '1'; -- sample ROM address ( = number of state to evaluate)
                    
                end if;
            when wait_ROM_data_state => 
                -- wait one clock cycle for ROM data             
                instant_pwr_calc_future_state <= wait_evaluation_state_1;                
            when wait_evaluation_state_1 =>
                -- wait first clock cycle 
                CE <= '1';
                instant_pwr_calc_future_state <= wait_evaluation_state_2;
            when wait_evaluation_state_2 =>
                -- wait second clock cycle 
                CE <= '1';
                instant_pwr_calc_future_state <= wait_evaluation_state_3;
            when wait_evaluation_state_3 =>
                -- wait third clock cycle 
                CE <= '1';
                instant_pwr_calc_future_state <= wait_evaluation_state_4;
            when wait_evaluation_state_4 =>
                -- wait fourth clock cycle 
                CE <= '1';
                instant_pwr_calc_future_state <= data_ready_state;            
            when data_ready_state =>
                -- data ready
                evaluation_ready <= '1';
                instant_pwr_calc_future_state <= wait_state;
        end case;
    end process;
    
    --- Flip Flop PROCESS ---
    FF_proc : process(sys_clk) begin
        if rising_edge(sys_clk) then
            if sample_ROM_addr = '1' then -- sample num_state_to_evaluate val
                ROM_addr_FF <= num_state_to_evaluate;
            end if;
            if sample_input_counter_val_std_logic_vector = '1' then -- sample input_counter_val_std_logic_vector val
                input_counter_val_std_logic_vector_FF <= input_counter_val_std_logic_vector;
            end if;
		end if;
    end process;

    
end Behavioral;
