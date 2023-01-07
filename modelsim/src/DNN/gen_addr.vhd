----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/14/2022 07:19:38 PM
-- Design Name: 
-- Module Name: gen_addr - Behavioral
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


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity gen_addr is

end gen_addr;

architecture Behavioral of gen_addr is

begin

gen_addr: process(clk,rst,addr_r) is --This process generate the address to access the neuron weight and get the input from the previous layer
begin
   -- if rst = '1' then
    --    addr <= '0';
   -- else
        if rst = '1' then
            addr <= (others => '0');
        else
            if addr_r = '1' then--writing into the addr_gen register to resume computation
                addr <= data_backup_vect_state_rec(2*num_outputs)(natural(ceil(log2(real(num_inputs))))-1 downto 0);
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
        end if;    
    --end if;
end process gen_addr;



end Behavioral;
