set_property -name {xsim.simulate.runtime} -value {0us} -objects [get_filesets sim_1]
# Define the filename
set filename [file join [file dirname [info script]] "output.txt"]

# Open the file for writing
set fp [open $filename "w"]

# Write a string to the file
puts $fp "This is a test string."


launch_simulation
# Fixed time simulation start
puts $fp "Fixed time simulation start ######################################"
puts $fp "warning_threshold_val;vol_cntr1_val;vol_cntr_pa_val;framework_pa_val;data_save_pa_val;time;shtdwn_counter;clk_counter;trace_rom_addr;"
set_value -radix unsigned /characterization_testbench/warning_threshold 3000
run 100 us
#puts $fp "[get_value -radix unsigned /characterization_testbench/warning_threshold];[get_value -radix unsigned /characterization_testbench/VOL_ARC_1/vol_cntr1_value];[get_value -radix unsigned /characterization_testbench/power_counter_val(0)];[get_value -radix unsigned /characterization_testbench/power_counter_val(1)];[get_value -radix unsigned /characterization_testbench/power_counter_val(2)];[current_time];[get_value -radix unsigned /characterization_testbench/shtdwn_counter];[get_value -radix unsigned /characterization_testbench/clk_counter];[get_value -radix unsigned /characterization_testbench/INTERMITTENCY_EMULATOR_1/ROM_addr];"


# Close the file
close $fp