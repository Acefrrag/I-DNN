set_param general.MaxThreads 4
open_project ../../vivado/I-DNN/I-DNN.xpr
# Update top_level tesbench
set_property top I_DNN_multiple_images_tb [get_filesets sim_1]
set_property top_lib xil_defaultlib [get_filesets sim_1]
update_compile_order -fileset sim_1
set_property -name {xsim.simulate.runtime} -value {0us} -objects [get_filesets sim_1]
set fp [open ./results/DB_results_fixedtime_NVREG_DELAY_FACTOR3_voltage_trace1_4_2450_2850.txt w]
puts "Launching simulation..."
flush stdout
launch_simulation
puts "Simulation launced. Performing tests."
flush stdout
# Fixed time simulation start
puts $fp "voltage_trace: voltage_traces/voltage_trace1.txt"
puts $fp "Fixed time simulation start ######################################"
puts $fp "hazard_threshold_val;time;shtdwn_counter;clk_counter;trace_rom_addr;executed_batches;I_layer1_pwr_apprx_values_idle_state;I_layer1_pwr_apprx_compute_state;I_layer1_pwr_apprx_values_save_state;I_layer1_pwr_apprx_values_rec_state;nv_reg1_pwr_apprx_values_poweron_state;nv_reg1_pwr_apprx_values_rec_state;nv_reg1_pwr_apprx_values_save_state;I_layer2_pwr_apprx_values_idle_state;I_layer2_pwr_apprx_compute_state;I_layer2_pwr_apprx_values_save_state;I_layer2_pwr_apprx_values_rec_state;nv_reg2_pwr_apprx_values_poweron_state;nv_reg2_pwr_apprx_values_rec_state;nv_reg2_pwr_apprx_values_save_state;I_layer3_pwr_apprx_values_idle_state;I_layer3_pwr_apprx_compute_state;I_layer3_pwr_apprx_values_save_state;I_layer3_pwr_apprx_values_rec_state;nv_reg3_pwr_apprx_values_poweron_state;nv_reg3_pwr_apprx_values_rec_state;nv_reg3_pwr_apprx_values_save_state;I_layer4_pwr_apprx_values_idle_state;I_layer4_pwr_apprx_compute_state;I_layer4_pwr_apprx_values_save_state;I_layer4_pwr_apprx_values_rec_state;nv_reg4_pwr_apprx_values_poweron_state;nv_reg4_pwr_apprx_values_rec_state;nv_reg4_pwr_apprx_values_save_state;"
set number 1
set_value -radix unsigned /I_DNN_multiple_images_tb/hazard_threshold 2450
run 3000 us
puts $fp "[get_value -radix unsigned /I_DNN_multiple_images_tb/hazard_threshold];[current_time];[get_value -radix unsigned /I_DNN_multiple_images_tb/shtdwn_counter];[get_value -radix unsigned /I_DNN_multiple_images_tb/clk_counter];[get_value -radix unsigned /I_DNN_multiple_images_tb/intermittency_emulator_cmp/ROM_addr];[get_value -radix unsigned /I_DNN_multiple_images_tb/executed_batches];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer1/power_counter_val(0)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer1/power_counter_val(1)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer1/power_counter_val(2)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer1/power_counter_val(3)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg1/power_counter_val(0)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg1/power_counter_val(1)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg1/power_counter_val(2)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer2/power_counter_val(0)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer2/power_counter_val(1)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer2/power_counter_val(2)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer2/power_counter_val(3)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg2/power_counter_val(0)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg2/power_counter_val(1)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg2/power_counter_val(2)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer3/power_counter_val(0)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer3/power_counter_val(1)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer3/power_counter_val(2)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer3/power_counter_val(3)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg3/power_counter_val(0)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg3/power_counter_val(1)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg3/power_counter_val(2)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer4/power_counter_val(0)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer4/power_counter_val(1)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer4/power_counter_val(2)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer4/power_counter_val(3)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg4/power_counter_val(0)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg4/power_counter_val(1)];[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg4/power_counter_val(2)];"
puts "Simulation number $number ended"
flush stdout
set number [expr $number + 1]
restart
# Fixed time simulation end
puts $fp "Fixed time simulation end ########################################
"
