----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/12/2022 03:30:44 PM
-- Design Name: 
-- Module Name: DATA_SAVE_PROCESS - Behavioral
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

library work;
use work.I_DNN_package.all;
--Augumented Packages
use work.COMMON_PACKAGE.all;
use work.NVME_FRAMEWORK_PACKAGE.all;
use work.TEST_ARCHITECTURE_PACKAGE.all;






library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;
use ieee.fixed_pkg.all;



-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity DATA_SAVE_PROCESS is
generic(
num_outputs: natural := 30;
num_inputs: natural := 30
);
port(
clk: in std_logic;
data_save_busy: in std_logic;
var_cntr_tc: in std_logic;
nv_reg_busy: in std_logic;
var_cntr_value: in integer range 0 to NV_REG_WIDTH+2;
mul_sel_backup: in  integer range 1 to 3:= 1;
nv_reg_busy_sig: in std_logic;
data_save_nv_reg_start_addr: in STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);

data_save_var_cntr_ce: out std_logic;
data_save_var_cntr_init: out std_logic;
data_save_nv_reg_en: out std_logic;
data_save_nv_reg_we: out std_logic;
addrb: out integer range 0 to num_outputs+2;
doutb: out std_logic_vector(nv_reg_width-1 downto 0);
data_save_nv_reg_din: out STD_LOGIC_VECTOR( 31 DOWNTO 0);
data_save_nv_reg_addr : out STD_LOGIC_VECTOR(nv_reg_addr_width_bit-1 DOWNTO 0);


data_save_v_reg_offset: inout INTEGER RANGE 0 TO V_REG_WIDTH -1


);
end DATA_SAVE_PROCESS;

architecture Behavioral of DATA_SAVE_PROCESS is

type rom_type is array (0 to num_inputs-1) of sfixed(neuron_int_width-1 downto -neuron_frac_width);
type data_out_type is array(0 to num_outputs-1) of sfixed(neuron_int_width-1 downto -neuron_frac_width);
type data_backup_state_type is array(0 to 2*num_outputs+2-1) of std_logic_vector(nv_reg_width-1 downto 0); --data grouping for saving state(weighted_sum, fsm_state, addr_gen)
type weighted_sum_backup_type is array(0 to num_outputs-1) of std_logic_vector(2*(neuron_int_width+neuron_frac_width)-1 downto 0); --this contains the weighted sum elements(64 bits) split up into 2 elements of 32 bits BIG ENDIAN NOTATION
type data_backup_output_type is array(0 to num_outputs) of std_logic_vector(nv_reg_width-1 downto 0); --data gropuing for saving output (the last two wire are not connected to anything)
type backup_type_t is (state, output, nothing);

signal data_backup_vect_state_save: data_backup_state_type;
signal data_backup_vect_output_save: data_backup_output_type;

begin


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


end Behavioral;
