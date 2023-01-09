----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/12/2022 02:16:56 PM
-- Design Name: 
-- Module Name: DATA_REC_PROCESS - Behavioral
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


------------------------------------------------DATA_REC process-------------------------------------------------------------------
-- Doc:
--      this process and its brothers are concernd of data recovery from non volatile register. The recovered data and its amount 
--      can be defined by changing the constants in VOL_ARC CONSTANTS subsection of this code. The recovered data can be obtained 
--      by combining the information carried by: data_rec_recovered_data, data_rec_recovered_offset. This is necessary because
--      from request to offer there are delays expecially from NV_REG.



entity DATA_REC_PROCESS is
generic(
num_outputs: natural := 30;
num_inputs:natural := 30
);

port(
clk: in std_logic;
n_power_reset: in std_logic;
nv_reg_busy:in std_logic;
fsm_nv_reg_state: in fsm_nv_reg_state_t;
data_rec_offset: in INTEGER RANGE 0 TO 2*num_outputs+2+2;
var_cntr_tc: in std_logic;
var_cntr_value: in INTEGER range 0 to NV_REG_WIDTH+2;
var_cntr_value_last: in INTEGER range 0 to NV_REG_WIDTH+2;
nv_reg_dout: in STD_LOGIC_VECTOR(NV_REG_WIDTH-1 DOWNTO 0);
addr: in std_logic_vector(0 to natural(ceil(log2(real(num_inputs))))-1) :=(others => '0');


data_rec_nv_reg_we: out std_logic;
data_rec_nv_reg_din: out std_logic_vector(nv_reg_width-1 downto 0);
data_rec_recovered_offset: out INTEGER RANGE 0 TO NV_REG_WIDTH -1;


data_rec_recovered_data: inout STD_LOGIC_VECTOR( 31 DOWNTO 0);
data_rec_type: inout data_backup_type_t

);

end DATA_REC_PROCESS;

architecture Behavioral of DATA_REC_PROCESS is

signal data_rec_busy: std_logic:= '0';



begin

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


DATA_REC_RECOVERY_SIGNALS_CNTRL: process(data_rec_busy) is
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


end Behavioral;
