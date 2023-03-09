----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 06/14/2020 05:43:53 PM
-- Design Name: 
-- Module Name: NVME_FRAMEWORK_PACKAGE - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision: Michele Pio Fragasso
-- Revision 0.02 - File Created
-- Additional Comments:
-- 1) changed constant value NV_REG_WIDTH from 16 to 32
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.math_real.all;

library work;
use work.I_DNN_package.all;

package NVME_FRAMEWORK_PACKAGE is

    constant NUM_PWR_STATES                     : integer := 3;     -- The sum of all power states entities that are connected to a power approximator have.
    constant PWR_CONSUMPTION_ROM_BITS           : integer := 10;    -- The bit length of a word for the pwr_consumption_val_ROM
    constant PWR_APPROX_COUNTER_NUM_BITS        : integer := 31;    -- The register size (in bits) of all power approximators (if the pa is used a lot bigger values are suggested)
    constant INTERMITTENCY_NUM_THRESHOLDS       : integer := 2;     -- The number of voltage thsholds the intermittency emulator will track (at least one, i.e. the shutdown threshold)
    constant NV_REG_WIDTH                       : INTEGER := DNN_neuron_inout_Width;    -- The word size in bits of all non volatile registers
    constant nv_reg_depth                       : integer := 20;
    constant bram_addr_width_bit : INTEGER := integer(ceil(log2(real(NV_REG_depth))));
                                                                ---> !!!!! This value must be kept in sync with the one used inside the bram ip for all nv_reg !!!!!
   
end package NVME_FRAMEWORK_PACKAGE;
