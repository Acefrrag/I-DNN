"""
Description: This script should be run with different NV_REg_delay_factpr in ode
to produce parametric plots.
"""

import os
import sys


##---------------------------------------------------------------------- Functions
def cleanup ():
    operative_system = sys.platform
    if operative_system == "linux" :
        try:
            os.remove("./vivado.log")
            os.remove("./vivado.jou")
        except FileNotFoundError:
            print("\t-> files to be deleted are not found, proceeding.... \n")
    else:
        try:
            os.remove(".\\vivado.log")
            os.remove(".\\vivado.jou")
        except FileNotFoundError:
            print("\t-> files to be deleted are not found, proceeding.... \n")
##--------------------------------------------------------------------------------
    ##--------------------------------------------helper functions
def printlnres(string):
    print("puts $fp \"" + string + "\"")
def printres(string):
    print("puts -nonewline $fp \"" + string + "\"")
def printnlterminal(string):
    print("puts \"" + string + "\"")
    print("flush stdout")
    ##------------------------------------------------------------
    
NV_REG_DELAY_FACTOR = 2
#Modifying COMMON_PACKAG to update the nv_reg delay factor
CMN_PKG_path = "../../src/NORM/COMMON_PACKAGE.vhd"
f = open(CMN_PKG_path, "r+")
allLines = f.readlines()
for i, line in enumerate(allLines):
    if "FRAM_MAX_DELAY_NS" in line:
        allLines.pop(i)
        allLines.insert(i, "    constant FRAM_MAX_DELAY_NS                  : INTEGER := MASTER_CLK_PERIOD_NS*2;\n")


##----------------------------------------------------------------------- Defaults
#This is the relative voltage trace path taken from the folder where the testbench I_DNN_multiple_image_tb.vhd is located.
voltage_trace_path = "voltage_traces/voltage_trace2.txt"
voltage_trace_path_folder = "../src/NORM/voltage_traces/voltage_trace2.txt" 
length_path = len(voltage_trace_path)
testbench_path = "../../test/I_DNN_multiple_images_tb.vhd"
#Determining max value of voltage trace and number of elements
vt_f = open("../../test/"+voltage_trace_path_folder)
vt_lines = vt_f.readlines()
voltages = [int(voltage) for voltage in vt_lines]
num_elements = len(voltages)
max_voltage = max(voltages)
vt_f.close()


#Modifying voltage trace source
ctf = open(testbench_path, "r+")
testbench_lines = ctf.readlines()

marker_voltage_path_line = "constant voltage_trace_path"
for i,line in enumerate(testbench_lines):
    if marker_voltage_path_line in line:
        testbench_lines.pop(i)
        testbench_lines.insert(i, "constant voltage_trace_path: string(1 to "+str(length_path)+") := \""+ str(voltage_trace_path)+"\";\n")

    ## Reach start of file
ctf.seek(0)

    ## Delete contents
ctf.truncate()

    ## Write the cange to the file by rewriting it entirely
ctf.writelines(testbench_lines) 
ctf.close()

#System clock period in ns
system_clock_period = 40
#System clock period in MHz
system_clock_frequency = int(1/system_clock_period*10**(9))
#The voltage trace timescale should be always greater than 4 times the system clock period
voltage_trace_timescale = 160
intermittency_prescaler = int(voltage_trace_timescale/system_clock_period)

common_package_path = "../../src/NORM/COMMON_PACKAGE.vhd"
marker_master_clock_speed_hz = "MASTER_CLK_SPEED_HZ"
f = open(common_package_path, "r+")
package_lines = f.readlines()
for i, line in enumerate(package_lines):
    if marker_master_clock_speed_hz in line:
        package_lines.pop(i)
        package_lines.insert(i, "constant MASTER_CLK_SPEED_HZ: INTEGER := "+str(system_clock_frequency)+";\n")



intermittency_emulator_path = "../../src/NORM/INTERMITTENCY_EMULATOR_package.vhd"
marker_num_elements_ROM = "INTERMITTENCY_NUM_ELEMNTS_ROM"
marker_max_ROM = "INTERMITTENCY_MAX_VAL_ROM_TRACE"
marker_intermittency_prescaler = "INTERMITTENCY_PRESCALER"
ctl = open(intermittency_emulator_path, "r+")
package_lines = ctl.readlines()

for i, line in enumerate(package_lines):
    if marker_num_elements_ROM in line:
        package_lines.pop(i)
        package_lines.insert(i, "constant INTERMITTENCY_NUM_ELEMNTS_ROM: integer :=  "+str(num_elements)+";\n")
    if marker_max_ROM in line:
        package_lines.pop(i)
        package_lines.insert(i, "constant INTERMITTENCY_MAX_VAL_ROM_TRACE: integer := "+str(max_voltage)+";\n")
    if marker_intermittency_prescaler in line:
        package_lines.pop(i)
        package_lines.insert(i, "constant INTERMITTENCY_PRESCALER: integer := "+str(intermittency_prescaler)+";\n")
    ## Reach start of file
ctl.seek(0)

    ## Delete contents
ctl.truncate()

    ## Write the cange to the file by rewriting it entirely
ctl.writelines(package_lines) 
ctl.close()



num_hidden_layers = 4
if sys.platform == "linux":
    vivado_path =  "/opt/Xilinx/Vivado/2020.2/bin/vivado"
elif sys.platform == "win32":
    vivado_path = "C:\\Xilinx\\Vivado\\2020.2\\bin\\vivado.bat"
else:
    sys.exit("I don't know how to open vivado on your system")

## Default parameters
project_path = "../../vivado/I-DNN/I-DNN.xpr" 
db_results_path = "./results/"
try:
    sys.mkdir(db_results_path)
except:
    print("The destination folder for the tcl script already exists")
    
characterization_testbench_path = "../../test/I_DNN_multiple_images_tb.vhd"

time_constant_us = 1500

executed_batches_target = 4

start_value_threshold = 2500
end_value_threshold = 3000
threshold_step = 80
##--------------------------------------------------------------------------------


##---------------------------------------------------------------Testbench changes
    ## Change testbench of top level to use the correct architecture for this 
    ## specific test. We need architecture Behavioral_db
ctf = open(characterization_testbench_path, "r+")
testbench_lines = ctf.readlines()

search_marker_start = "----##DB!!"
search_marker_end = "----!!DB##"
start = 0
for i,line in enumerate(testbench_lines):
    if search_marker_start in line:
        start = 1
    else:
        if start == 1: 
            if search_marker_end not in line:
                if "--" in line:
                    testbench_lines.pop(i) 
                    testbench_lines.insert(i,line[2:])
            else:
                start = 0
    ## Reach start of file
ctf.seek(0)

    ## Delete contents
ctf.truncate()

    ## Write the cange to the file by rewriting it entirely
ctf.writelines(testbench_lines) 
ctf.close()
##--------------------------------------------------------------------------------


allThreshold = []
for val in range(start_value_threshold,end_value_threshold,threshold_step):
    allThreshold.append(val)

##--------------------------------------------------- Creation of tcl batch script
    ##  Defaults
    ## to get description of this signals use the describe command see
    ## UG835 (v2020.1) June 3, 2020 www.xilinx.com Tcl Command Reference Guide page 479

tcl_script_folder_path = "./tcl"
try:
    os.mkdir(tcl_script_folder_path)
except:
    print("The tcl script folder already exists")
    
tcl_script_path = tcl_script_folder_path+"/DB_simulation_batch.tcl"

threshold_signal_path = "/I_DNN_multiple_images_tb/hazard_threshold"
executed_batches_val_sig_path = "/I_DNN_multiple_images_tb/executed_batches"

executed_batches = "/I_DNN_multiple_images_tb/executed_batches"

db_fix_time_cmds= {
    "hazard_threshold_val"          :"[get_value -radix unsigned /I_DNN_multiple_images_tb/hazard_threshold]",
    "time"                          :"[current_time]",
    "shtdwn_counter"                :"[get_value -radix unsigned /I_DNN_multiple_images_tb/shtdwn_counter]",
    "clk_counter"                   :"[get_value -radix unsigned /I_DNN_multiple_images_tb/clk_counter]",
    "trace_rom_addr"                :"[get_value -radix unsigned /I_DNN_multiple_images_tb/intermittency_emulator_cmp/ROM_addr]",
    "executed_batches"              :"[get_value -radix unsigned /I_DNN_multiple_images_tb/executed_batches]"
}

##Adding power approximator values per layer
for i in range(num_hidden_layers):
    layer_pwr_appr_idle_state_key = "I_layer"+str(i+1)+"_pwr_apprx_values_idle_state"
    layer_pwr_appr_compute_state_key = "I_layer"+str(i+1)+"_pwr_apprx_compute_state"
    layer_pwr_appr_save_state_key = "I_layer"+str(i+1)+"_pwr_apprx_values_save_state"
    layer_pwr_appr_rec_state_key = "I_layer"+str(i+1)+"_pwr_apprx_values_rec_state"
    nv_reg_pwr_appr_poweron_state_key = "nv_reg"+str(i+1)+"_pwr_apprx_values_poweron_state"
    nv_reg_pwr_appr_rec_state_key = "nv_reg"+str(i+1)+"_pwr_apprx_values_rec_state"
    nv_reg_pwr_appr_save_state_key = "nv_reg"+str(i+1)+"_pwr_apprx_values_save_state"
    # layer_inst_pwr_idle_state_key = "I_layer"+str(i+1)+"inst_pwr_idle_state"
    # layer_inst_pwr_compute_state_key = "I_layer"+str(i+1)+"inst_pwr_compute_state"
    # layer_inst_pwr_save_state_key = "I_layer"+str(i+1)+"inst_pwr_save_state"
    # layer_inst_pwr_rec_state_key = "I_layer"+str(i+1)+"inst_pwr_rec_state"
    # nv_reg_inst_pwr_poweron_key = "nv_reg"+str(i+1)+"inst_pwr_poweron_state"
    # nv_reg_inst_pwr_rec_state_key = "nv_reg"+str(i+1)+"inst_pwr_rec_state"
    # nv_reg_inst_pwr_save_state_key = "nv_reg"+str(i+1)+"inst_pwr_save_state"
    db_fix_time_cmds[layer_pwr_appr_idle_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(0)]"
    db_fix_time_cmds[layer_pwr_appr_compute_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(1)]"
    db_fix_time_cmds[layer_pwr_appr_save_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(2)]"
    db_fix_time_cmds[layer_pwr_appr_rec_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(3)]"
    db_fix_time_cmds[nv_reg_pwr_appr_poweron_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg"+str(i+1)+"/power_counter_val(0)]"
    db_fix_time_cmds[nv_reg_pwr_appr_rec_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg"+str(i+1)+"/power_counter_val(1)]"
    db_fix_time_cmds[nv_reg_pwr_appr_save_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg"+str(i+1)+"/power_counter_val(2)]"
    # db_fix_time_cmds[layer_inst_pwr_idle_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_layer"+str(i+1)+"/output_data(0)]"
    # db_fix_time_cmds[layer_inst_pwr_compute_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_layer"+str(i+1)+"/output_data(1)]"
    # db_fix_time_cmds[layer_inst_pwr_save_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_layer"+str(i+1)+"/output_data(2)]"
    # db_fix_time_cmds[layer_inst_pwr_rec_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_layer"+str(i+1)+"/output_data(3)]"
    # db_fix_time_cmds[nv_reg_inst_pwr_poweron_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_nvreg"+str(i+1)+"/output_data(0)]"
    # db_fix_time_cmds[nv_reg_inst_pwr_rec_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_nvreg"+str(i+1)+"/output_data(1)]"
    # db_fix_time_cmds[nv_reg_inst_pwr_save_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_nvreg"+str(i+1)+"/output_data(2)]"

number_objects = len(db_fix_time_cmds)
DB_log_path = "./results/DB_result_log.txt"
f = open(DB_log_path, "w")
f.write("number_simulation_objects: "+str(number_objects))
f.close()


db_fix_val_cmds= {
    "hazard_threshold_val"          :"[get_value -radix unsigned /I_DNN_multiple_images_tb/threshold_value(1)]",
    "time"                          :"[current_time]",
    "shtdwn_counter"                :"[get_value -radix unsigned /I_DNN_multiple_images_tb/shtdwn_counter]",
    "clk_counter"                   :"[get_value -radix unsigned /I_DNN_multiple_images_tb/clk_counter]",
    "trace_rom_addr"                :"[get_value -radix unsigned /I_DNN_multiple_images_tb/intermittency_emulator_cmp/ROM_addr]",
    "executed_batches"                      :"[get_value -radix unsigned /I_DNN_multiple_images_tb/executed_batches]"

}

##Adding power approximator values per layer
for i in range(num_hidden_layers):
    layer_pwr_appr_idle_state_key = "I_layer"+str(i+1)+"_pwr_apprx_values_idle_state"
    layer_pwr_appr_compute_state_key = "I_layer"+str(i+1)+"_pwr_apprx_compute_state"
    layer_pwr_appr_save_state_key = "I_layer"+str(i+1)+"_pwr_apprx_values_save_state"
    layer_pwr_appr_rec_state_key = "I_layer"+str(i+1)+"_pwr_apprx_values_rec_state"
    nv_reg_pwr_appr_poweron_state_key = "nv_reg"+str(i+1)+"_pwr_apprx_values_poweron_state"
    nv_reg_pwr_appr_rec_state_key = "nv_reg"+str(i+1)+"_pwr_apprx_values_rec_state"
    nv_reg_pwr_appr_save_state_key = "nv_reg"+str(i+1)+"_pwr_apprx_values_save_state"
    # layer_inst_pwr_idle_state_key = "I_layer"+str(i+1)+"inst_pwr_idle_state"
    # layer_inst_pwr_compute_state_key = "I_layer"+str(i+1)+"inst_pwr_compute_state"
    # layer_inst_pwr_save_state_key = "I_layer"+str(i+1)+"inst_pwr_save_state"
    # layer_inst_pwr_rec_state_key = "I_layer"+str(i+1)+"inst_pwr_rec_state"
    # nv_reg_inst_pwr_poweron_key = "nv_reg"+str(i+1)+"inst_pwr_poweron_state"
    # nv_reg_inst_pwr_rec_state_key = "nv_reg"+str(i+1)+"inst_pwr_rec_state"
    # nv_reg_inst_pwr_save_state_key = "nv_reg"+str(i+1)+"inst_pwr_save_state"

    db_fix_val_cmds[layer_pwr_appr_idle_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(0)]"
    db_fix_val_cmds[layer_pwr_appr_compute_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(1)]"
    db_fix_val_cmds[layer_pwr_appr_save_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(2)]"
    db_fix_val_cmds[layer_pwr_appr_rec_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(3)]"
    db_fix_val_cmds[nv_reg_pwr_appr_poweron_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg"+str(i+1)+"/power_counter_val(0)]"
    db_fix_val_cmds[nv_reg_pwr_appr_rec_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg"+str(i+1)+"/power_counter_val(1)]"
    db_fix_val_cmds[nv_reg_pwr_appr_save_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg"+str(i+1)+"/power_counter_val(2)]"
    # db_fix_val_cmds[layer_inst_pwr_idle_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_layer"+str(i+1)+"/output_data(0)]"
    # db_fix_val_cmds[layer_inst_pwr_compute_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_layer"+str(i+1)+"/output_data(1)]"
    # db_fix_val_cmds[layer_inst_pwr_save_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_layer"+str(i+1)+"/output_data(2)]"
    # db_fix_val_cmds[layer_inst_pwr_rec_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_layer"+str(i+1)+"/output_data(3)]"
    # db_fix_val_cmds[nv_reg_inst_pwr_poweron_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_nvreg"+str(i+1)+"/output_data(0)]"
    # db_fix_val_cmds[nv_reg_inst_pwr_rec_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_nvreg"+str(i+1)+"/output_data(1)]"
    # db_fix_val_cmds[nv_reg_inst_pwr_save_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/inst_pwr_calc_comp_nvreg"+str(i+1)+"/output_data(2)]"

## Create script tcl script file (later removed)
tcl_script_file = open(tcl_script_path, 'w')

## get Stdout file descriptor
std_out = sys.stdout

## Redirect prints (stdout) to tcl_script_file
sys.stdout=tcl_script_file

## Increase usable threads in vivado
threads = os.cpu_count() 
if threads != None:
    print("set_param general.MaxThreads " + str(threads))

## Open projectt
print("open_project " + project_path )

    ## Update top level testbench
print("# Update top_level tesbench")
print("set_property top I_DNN_multiple_images_tb [get_filesets sim_1]")
print("set_property top_lib xil_defaultlib [get_filesets sim_1]")

print("update_compile_order -fileset sim_1")

    ## Set simulation starting poit at 0
print("set_property -name {xsim.simulate.runtime} -value {0us} -objects [get_filesets sim_1]")

    ## Creates result file
print("set fp [open " + db_results_path + "DB_results_NVREG_DELAY_FACTOR"+str(NV_REG_DELAY_FACTOR)+".txt w]")

    ## Launch simulation
printnlterminal("Launching simulation...")
print("launch_simulation")
printnlterminal("Simulation launced. Performing tests.")


### FIXED TIME###
print("# Fixed time simulation start")

printlnres("voltage_trace: "+ voltage_trace_path)
printlnres("Fixed time simulation start ######################################")
        
## outputs the keys of db_fix_tim_data in this format: key1;key2;key3;...;
printlnres( "".join(
        list(str(a)+";" for a in list(db_fix_time_cmds.keys()))
    )
)

print("set number 1")
for threshold in allThreshold:
    print("set_value -radix unsigned " + threshold_signal_path + " " + str(threshold))
    print("run " + str(time_constant_us) + " us")
        ## print commands of the db_fixe_time_data as command1;command2;....commandN;
        ## this commands will be printed in the results file
    printlnres( "".join( 
            list(str(value)+";" for value in list(db_fix_time_cmds.values()))
        ) 
    )
    
    printnlterminal("Simulation number $number ended")
    print("set number [expr $number + 1]")
    print("restart")

print("# Fixed time simulation end")
printlnres("Fixed time simulation end ########################################\n")

### FIXED VALUE ###

## This tcl command adds a condition that is checked every time the conditioned signal changes, if the condition is true the inner code is executed
## condition remain even after a restart, condtions can be reported by running report_conditions, and be all removed by running remove_condtion -all
print("add_condition -name cond1 -radix unsigned \"" + executed_batches + " == " + str(executed_batches_target) + "\" {" )
print("global fp")
    ## print commands of the db_fix_val_data as command1;command2;....commandN;
    ## this commands will be printed in the results file
printlnres( "".join( 
        list(str(value)+";" for value in list(db_fix_val_cmds.values()))
    )

)
printnlterminal("Simulation number $number ended")
print("stop}")

print("# Fixed value simulation start")
printlnres("Fixed value simulation start #####################################")

## outputs the keys of db_fix_val_data in this format: key1;key2;key3;...;
printlnres( "".join(
        list(str(a)+";" for a in list(db_fix_val_cmds.keys()))
    )
)

for threshold in allThreshold:
    print("set_value -radix unsigned " + threshold_signal_path + " " + str(threshold))
    print("run " + str(time_constant_us) + " us")   ## this value must be setup manually, bigger value will result in long simulations if the condtion in add_condition is not reached
                        ## but smaller value will not the simulation to reach the condition
    print("set value [get_value -radix unsigned "+ executed_batches_val_sig_path +"]")

        ## This part is executed only if add_condition is not met (happens if vol_cntr is not able to reach value_constant)
    print("if { [expr $value < "+ str(executed_batches_target)+"] } {")

        ## print commands of the db_fix_val_data as command1;command2;....commandN;
        ## this commands will be printed in the results file
    printlnres( "".join( 
            list(str(value)+";" for value in list(db_fix_val_cmds.values()))
        )
    )
    print("}")
    print("restart")

print("# Fixed value simulation end")
printlnres("Fixed value simulation end #######################################")

    ## Restore std out descriptor to its original value
sys.stdout=std_out

    ## Close generated script file
tcl_script_file.close()
##-------------------------------------------------------------Remove vivado files
cleanup()
##--------------------------------------------------------------------------------

##################################################################################
########################## RUN GENERATED BATCH FIlE###############################
    ## parameters to pass to vivado
run_line = vivado_path + " -mode batch -source " + tcl_script_path

##run_line = "export LC_ALL=C \n" + run_line    ## <- eventually remove this
print("Executing: " + str(run_line))
sys.stdout.flush()
##subprocess.run([vivado_path, "-mode", "batch", "-source", tcl_script_path])






os.system(run_line)
##################################################################################
##################################################################################

##---------------------------------------------------------------Testbench changes
    ## Change testbench of top level to use the correct architecture for this 
    ## specific test. We need architecture Behavioral_db
# ctf = open(characterization_testbench_path, "r+")
# testbench_lines = ctf.readlines()

# search_marker_start = "----##DB!!"
# search_marker_end = "----!!DB##"
# start = 0
# for i,line in enumerate(testbench_lines):
#     if search_marker_start in line:
#         start = 1
#     else:
#         if start == 1: 
#             if search_marker_end not in line:
#                 if "--" not in line:
#                     testbench_lines.pop(i)
#                     testbench_lines.insert(i,"--" + line)
#             else:
#                 start = 0

#     ## Reach beginning of file
# ctf.seek(0)

#     ## Delete contents
# ctf.truncate()

#     ## Write the cange to the file by rewriting it entirely
# ctf.writelines(testbench_lines) 
# ctf.close()
##--------------------------------------------------------------------------------

##-------------------------------------------------------------Remove vivado files
cleanup()