----------------------------------------------------------------------------------
-- Company: University of Trento
-- Engineer: Michele Pio Fragasso
-- 
-- Create Date: 03/17/2022 09:04:44 AM
-- Update Date: 06/05/2022 4:05:00 PM
-- Design Name: 
-- Module Name: neuron - Behavioral
-- Project Name: Intermitten Architecture neuron for DNN
-- Target Devices: ICE40
-- Tool Versions: 
-- Description: This entity implement the neuron to be included in the
-- intermittent DNN. When a hazard occur I have decided to save the currently-active layer
-- state which means I save the weighted sum for every neuron. This
-- require the neuron to output also this quantity.
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------

library std;
use std.textio.all;

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use ieee.numeric_std.all;
use ieee.math_real.all;
use ieee.fixed_pkg.all;

library work;
use work.I_DNN_package.all;


entity I_neuron is

generic(
    constant rom_width: natural := 16;
    constant rom_depth: natural := 3;
    constant weight_file: string := "weights.txt";
    constant bias_file: string := "bias.txt");
port(
    --ORIGINARY PINS
    --INPUT
    clk: in std_logic;                                                          --clk:          Clock signalzz
    data_in: in sfixed (input_int_width-1 downto -input_frac_width);            --data_in:      Serial Data Input Port
    addr: in std_logic_vector (0 to natural(ceil(log2(real(rom_depth))))-1);    --addr:         Address to access ROM memory
    mul_sel: in std_logic;                                                      --mul_sel:      Multiplexer Selection Bit to choose between bias and weighted sum element
    sum_reg_rst: in std_logic;                                                  --sum_reg_rst:  Reset Bit to reset the cumulative sum register
    update_out: in std_logic;                                                   --update_out:   Update bit to update the output register of the neuron
    --OUTPUT
    data_out: out sfixed (input_int_width-1 downto -input_frac_width);          --data_out:     Serial Data Output Port
    --ADDED PINS
    --INPUT
    n_power_reset: in std_logic;                                                --n_power_reset:To reset the volatile register of the neuron
    en: in std_logic;                                                           --en:           Pin to enable the register (Active on low) - en=0: Volatile registers hold their data to enable save process.
    output_en_rec: in std_logic;                                                        --output_en_rec:        Pin to enable the output recovery. '1': Content of neuron output is overwritten with the recovered data
    internal_en_rec: in std_logic;                                                        --internal_en_rec:        Pin to enable the state recovery. '1': Content of neuron w_sum and is overwritten with the recovered data
    data_out_rec: in sfixed (neuron_int_width-1 downto -neuron_frac_width);       --data_out_rec: Recovery Port to recover the output of the neuron
    state_rec: in std_logic_vector(neuron_frac_width+neuron_int_width-1 downto 0);  --wsum_rec:     Recovery Port to recover the weighted sum or the ReLU output of the neuron
    data_v: in std_logic;
    --OUTPUT
    wsum_save: out std_logic_vector(neuron_frac_width+neuron_int_width-1 downto 0); --wsum_save:    Save Port to save the currently computed weighted sum
    ReLU_save: out std_logic_vector(neuron_frac_width+neuron_int_width-1 downto 0)  --ReLU_save:    Save Port to save the output of the activation function
    );      
end entity I_neuron;


architecture Behavioral of I_neuron is

signal weight_out: sfixed (neuron_int_width-1 downto -neuron_frac_width):=(others=>'0');
signal clk_sig: std_logic := '0';
signal sum_reg_out: sfixed((neuron_int_width)-1 downto (-neuron_frac_width)) := (others => '0');
signal mul_out: sfixed((neuron_int_width)-1 downto (-neuron_frac_width)) := (others => '0');
signal weight_prod: sfixed((neuron_int_width)-1 downto (-neuron_frac_width)) := (others => '0');
signal bias: sfixed((neuron_int_width)-1 downto (-neuron_frac_width));
signal out_reg_val: sfixed(neuron_int_width-1 downto -neuron_frac_width);
signal out_ReLU: sfixed(input_int_width-1 downto -input_frac_width);
signal out_ReLU_d: sfixed(input_int_width-1 downto -input_frac_width);
signal start_d: std_logic;
--signal data_in_d: sfixed(input_int_width-1 downto -input_frac_width);


component weight_memory is
generic(rom_depth: natural;
        rom_width: natural;
        log_file: string);
port( clk: in std_logic;
    addr: in std_logic_vector(0 to natural(ceil(log2(real(rom_depth))))-1);
    dout: out sfixed (neuron_int_width-1 downto -neuron_frac_width));
end component weight_memory;


component ReLU is
generic(data_width: natural);
port(data_in: in sfixed((neuron_int_width)-1 downto (-neuron_frac_width));
    data_out: out sfixed(neuron_int_width-1 downto -neuron_frac_width));
end component ReLU;

function makesfixed (bit_in: in bit_vector((neuron_rom_width)-1 downto 0)) return sfixed is
    variable fixedpoint_s: sfixed((neuron_int_width)-1 downto (-neuron_frac_width));
    --variable a: std_logic := 0;
    begin
    for i in fixedpoint_s'range loop
        fixedpoint_s(i) := To_StdULogic(bit_in(i+neuron_frac_width));
    end loop;
    return fixedpoint_s;
end function;

impure function init_bias(bias_file: in string) return sfixed is
file text_header: text open read_mode is bias_file; --This produces a header to the file
variable text_line: line; --the type line represents a line in the file
variable bit_line: bit_vector(input_width-1 downto 0);
variable bias_content: sfixed((neuron_int_width)-1 downto (-neuron_frac_width));
variable j: std_logic;
begin
j:='0';
readline(text_header, text_line);
read(text_line, bit_line);
bias_content := makesfixed(bit_line);
return bias_content;

end function; 


begin

weight_prod <= resize(weight_out*data_in, neuron_int_width-1, -neuron_frac_width);
bias <= init_bias(bias_file);

clk_sig <= clk;

--Neuron Output

data_out <= out_reg_val;

weight_memory_comp: weight_memory
generic map(
rom_depth => rom_depth,
rom_width => neuron_rom_width,
log_file => weight_file)
port map(clk => clk_sig,
addr => addr,
dout => weight_out);
    
ReLU_comp: ReLU
generic map(data_width => rom_width)
port map(
    data_in => sum_reg_out,
    data_out => out_ReLU
);


sum_reg: process (clk,n_power_reset)
begin
    if n_power_reset = '0' then
        sum_reg_out <= (others => '0');
    else
            if sum_reg_rst = '1' then
                sum_reg_out <= (others => '0');
            else
                if rising_edge(clk) then
                        if internal_en_rec = '1' then
                            sum_reg_out <= to_sfixed(state_rec, neuron_int_width-1, -neuron_frac_width);
                        end if;
                        if en = '1' then
                             sum_reg_out <= mul_out;
                        end if;
                 else
                        sum_reg_out <= sum_reg_out;--do nothing. Data is not updated. Data is hold.
                 end if;
             end if;
     end if;
end process sum_reg;
wsum_save <= to_slv(sum_reg_out);


mul_temp: process(all)
begin
    case mul_sel is  
    when '0' => --the product w_i*x_i is chosen
        mul_out <= resize(weight_prod + sum_reg_out, neuron_int_width-1, -neuron_frac_width);
    when '1' => -- the bias is added
        mul_out <= resize(bias + sum_reg_out,neuron_int_width-1, -neuron_frac_width);
    when others =>
        mul_out <= resize(weight_prod + sum_reg_out,neuron_int_width-1, -neuron_frac_width);
    end case;
end process mul_temp;

out_ReLU_reg: process(clk) is
begin
    if rising_edge(clk) then
        if internal_en_rec = '1' then
            out_ReLU_d <= to_sfixed(state_rec,neuron_int_width-1, -neuron_frac_width);
        end if;
    end if;
    if falling_edge(clk) then
    --It is necessary to sample the activation function output after its transition. Otherwise it samples the old output of the activation function.
        if en = '1' then
            out_ReLU_d <= out_ReLU;
        end if;
    end if;
end process out_ReLU_reg;
ReLU_save <= to_slv(out_ReLU_d);

out_reg: process(update_out,n_power_reset,clk) is
begin
    if n_power_reset = '0' then
        out_reg_val <= (others => '0');
    else
        if rising_edge(clk) then
            if output_en_rec = '1' then
                out_reg_val <= data_out_rec;
            end if;
        end if;
        if rising_edge(clk) then
            if data_v = '0' and en = '1' then
                out_reg_val <= out_ReLU_d;
            end if;
        end if;
    end if;
end process out_reg;






end Behavioral;
