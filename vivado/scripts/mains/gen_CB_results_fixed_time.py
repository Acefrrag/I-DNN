# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 18:10:49 2023

Engineer: Michele Pio Fragasso


Description:
    This script generates CB policy results for a given DNN architecture,
    for different voltage trace at given NV_REG_DELAY_FACTOR.
    
    The constant backup policy backups the DNN state after <backup_period_clks>
    system clock cycles. For every simulation the DNN is tested for a given
    backup period clk. The 
    
#INPUTS

#OUTPUTS


            
    
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

def update_CMNPKG(NV_REG_DELAY_FACTOR, sys_f):
    #COMMON_PACKAGE.vhd update
    CMN_PKG_path = "../../src/NORM/COMMON_PACKAGE.vhd"
    p = open(CMN_PKG_path, "r+")
    allLines = p.readlines()
    marker_master_clock_speed_hz = "constant MASTER_CLK_SPEED_HZ"
    for i, line in enumerate(allLines):
        if "FRAM_MAX_DELAY_NS" in line:
            allLines.pop(i)
            allLines.insert(i, "    constant FRAM_MAX_DELAY_NS                  : INTEGER := MASTER_CLK_PERIOD_NS*"+str(NV_REG_DELAY_FACTOR)+";\n")
        if marker_master_clock_speed_hz in line:
            allLines.pop(i)
            allLines.insert(i, "constant MASTER_CLK_SPEED_HZ: INTEGER := "+str(sys_f)+";\n")    
    p.seek(0)
    p.truncate()
    p.writelines(allLines)
    p.close()
    
def update_TB(tb_path, vt_path, tb_path_len):
    #Modifying voltage trace source file from the testbench file
    ctf = open(tb_path, "r+")
    testbench_lines = ctf.readlines()
    marker_voltage_path_line = "constant voltage_trace_path"
    for i,line in enumerate(testbench_lines):
        if marker_voltage_path_line in line:
            testbench_lines.pop(i)
            testbench_lines.insert(i, "constant voltage_trace_path: string(1 to "+str(tb_path_len)+") := \""+ str(vt_path)+"\";\n")
    ## Reach start of file
    ctf.seek(0)
    ## Delete contents
    ctf.truncate()
    ## Write the cange to the file by rewriting it entirely
    ctf.writelines(testbench_lines) 
    ctf.close()

def max_vt(vt_path_folder):
    #Determining max value of voltage trace and number of elements
    vt_f = open("../../test/"+vt_path_folder)
    vt_lines = vt_f.readlines()
    voltages = [int(voltage) for voltage in vt_lines]
    num_elements = len(voltages)
    max_voltage = max(voltages)
    vt_f.close()
    return max_voltage, num_elements

def update_IEPKG(intermittency_prescaler, max_voltage, num_elements):
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
    
def uncomment_CB_DNN():
    DNN_path = "../../src/DNN/I_DNN.vhd"
    CB_start_marker = "##CB##Start"
    CB_end_marker = "##CB##End"
    ctl = open(DNN_path, "r+")
    DNN_VHDL_lines = ctl.readlines()
    start_index = [index for index, code_line in enumerate(DNN_VHDL_lines) if CB_start_marker in code_line][0]
    end_index = [index for index, code_line in enumerate(DNN_VHDL_lines) if CB_end_marker in code_line][0]

    i = start_index+2
    while i <= end_index-1:
        line = DNN_VHDL_lines.pop(i)
        line = line[2:]
        DNN_VHDL_lines.insert(i, line)
        i += 1
    
    ctl.seek(0)
    ctl.truncate()
    ctl.writelines(DNN_VHDL_lines)
    ctl.close()
    
def comment_CB_DNN():
    DNN_path = "../../src/DNN/I_DNN.vhd"
    CB_start_marker = "##CB##Start"
    CB_end_marker = "##CB##End"
    ctl = open(DNN_path, "r+")
    DNN_VHDL_lines = ctl.readlines()
    start_index = [index for index, code_line in enumerate(DNN_VHDL_lines) if CB_start_marker in code_line][0]
    end_index = [index for index, code_line in enumerate(DNN_VHDL_lines) if CB_end_marker in code_line][0]

    i = start_index+2
    while i <= end_index-1:
        line = DNN_VHDL_lines.pop(i)
        line = "--"+line
        DNN_VHDL_lines.insert(i, line)
        i += 1
    
    ctl.seek(0)
    ctl.truncate()
    ctl.writelines(DNN_VHDL_lines)
    ctl.close()
    

def generate_results(sim_prms, NV_REG_FACTOR, DNN_architecture, voltage_trace_name,threshold, backup_period_clks_chunk):
    voltage_trace_path = "voltage_traces/"+voltage_trace_name+".txt"
    voltage_trace_path_folder = "../src/NORM/voltage_traces/"+voltage_trace_name+".txt" 
    length_path = len(voltage_trace_path)
    testbench_path = "../../test/I_DNN_multiple_images_tb.vhd"
    #SETTING UP SIMULATION PARAMETERS
    #System clock period in ns
    system_clock_period = sim_prms["system_clock_period_ns"]
    time_constant_us = sim_prms["sim_time_us"]
    #System clock period in MHz
    system_clock_frequency = int(1/system_clock_period*10**(9))
    #The voltage trace timescale should be always greater than 4 times the system clock period
    voltage_trace_timescale = 160
    intermittency_prescaler = int(voltage_trace_timescale/system_clock_period)
    #Fixed Time defaults
    
    #time_constant_us = 1
    #end_value_threshold = 4050

    uncomment_CB_DNN()

    update_CMNPKG(NV_REG_FACTOR,sys_f=system_clock_frequency)
    
    update_TB(tb_path=testbench_path, vt_path=voltage_trace_path, tb_path_len=length_path)
    
    max_voltage, num_elements = max_vt(voltage_trace_path_folder)
    
    update_IEPKG(intermittency_prescaler=intermittency_prescaler, max_voltage=max_voltage, num_elements=num_elements)
    
    num_hidden_layers = DNN_architecture["num_hidden_layers"]
    if sys.platform == "linux":
        vivado_path =  "/opt/Xilinx/Vivado/2020.2/bin/vivado"
    elif sys.platform == "win32":
        vivado_path = "C:\\Xilinx\\Vivado\\2020.2\\bin\\vivado.bat"
    else:
        sys.exit("I don't know how to open vivado on your system")

    ## Default parameters
    project_path = "../../vivado/I-DNN/I-DNN.xpr" 
    cb_results_path = "./results/CB_results/"
    try:
        sys.mkdir(cb_results_path)
    except:
        print("Folder ./results/CB_results already exists")
        
    
    
        
    ##--------------------------------------------------- Creation of tcl batch script
    ##  Defaults
    ## to get description of this signals use the describe command see
    ## UG835 (v2020.1) June 3, 2020 www.xilinx.com Tcl Command Reference Guide page 479

    tcl_script_folder_path = "./tcl"
    try:
        os.mkdir(tcl_script_folder_path)
    except:
        print("The tcl script folder already exists")
        
    tcl_script_path = tcl_script_folder_path+"/DB_fixed_time_NVREG_DELAY_"+str(NV_REG_FACTOR)+"_simulation_batch.tcl"

    threshold_signal_path = "/I_DNN_multiple_images_tb/hazard_threshold"
    period_backup_clk_signal_path = "/I_DNN_multiple_images_tb/I_DNN_cmp/period_backup_clks"

    db_fix_time_cmds= {
        "hazard_threshold_val"          :"[get_value -radix unsigned /I_DNN_multiple_images_tb/hazard_threshold]",
        "backup_period_clks"            :"[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/period_backup_clks]",
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

        db_fix_time_cmds[layer_pwr_appr_idle_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(0)]"
        db_fix_time_cmds[layer_pwr_appr_compute_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(1)]"
        db_fix_time_cmds[layer_pwr_appr_save_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(2)]"
        db_fix_time_cmds[layer_pwr_appr_rec_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(3)]"
        db_fix_time_cmds[nv_reg_pwr_appr_poweron_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg"+str(i+1)+"/power_counter_val(0)]"
        db_fix_time_cmds[nv_reg_pwr_appr_rec_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg"+str(i+1)+"/power_counter_val(1)]"
        db_fix_time_cmds[nv_reg_pwr_appr_save_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg"+str(i+1)+"/power_counter_val(2)]"

    number_objects = len(db_fix_time_cmds)
    DB_log_path = "./results/DB_result_log.txt"
    f = open(DB_log_path, "w")
    f.write("number_simulation_objects: "+str(number_objects))
    f.close()



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
    print("set fp [open " + cb_results_path + "CB_results_fixedtime_NVREG_DELAY_FACTOR"+str(NV_REG_FACTOR)+"_"+voltage_trace_name+"_"+str(num_hidden_layers)+"_"+str(threshold)+"_"+str(backup_period_clks_chunk[0])+"_"+str(backup_period_clks_chunk[-1])+".txt w]")

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
    for backup_period_clk in backup_period_clks_chunk:
        print("set_value -radix unsigned " + threshold_signal_path + " " + str(threshold))
        print("set_value -radix unsigned " + period_backup_clk_signal_path + " " + str(backup_period_clk))
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

    # ##run_line = "export LC_ALL=C \n" + run_line    ## <- eventually remove this
    print("Executing: " + str(run_line))
    # sys.stdout.flush()
    # ##subprocess.run([vivado_path, "-mode", "batch", "-source", tcl_script_path])

    os.system(run_line)
    
    print("Simulation Ended!!")
    
    comment_CB_DNN()
    
if __name__=="__main__":
    #Do not change these
    voltage_trace_names = ["voltage_trace"+str(i) for i in range(1,11)] 
    DNN_architecture = {}
    sim_prms = {}
    
    #VALUES SETUP
    #12-LAYER test
    #VAUES for NV_REG_FACTOR=2
    #values = [2600,2550,2650,2650,2650,2650,2750,2400,2600,2450]
    #4-LAYER test
    #VALUES for NV_REG_FACTOR = 11
    #values= [2800,2650,2650,2850,2900,2800,2950,2450,2700,2450]
    #values for NV_REG_DELAY = 8
    
    #max DNN size 30
    #values for NV_REG_DELAY = 2
    values = [2450,2500,2500,2400,2400,2450,2350,2350,2450,2350]
    
    
    #8layer DNN scaled_up version. The sizes are
    #sizes = [120, 100, 60, 60, 50, 40, 30, 10]
    #values for NV_REG_DELAY = 2
    #values = [2500, 2500, 2650, 2500, 2500, 2500, 2550, 2400, 2550, 2400]#instead of 3412 there is 2500
    #values for NV_REG_DELAY = 5
    #values = [2550,2550,2650,2550,2600,2600,2400,2400,2600,2400]
    
    sim_prms["sim_time_us"] = 3_000
    sim_prms["system_clock_period_ns"] = 40
    sim_prms["backup_period_clks_end"] = 2048#(sim_prms["sim_time_us"]*1_000/sim_prms["system_clock_period_ns"])/10
    sim_prms["backup_period_clks_start"] = 1024#2**10
    DNN_architecture["num_hidden_layers"] = 5
    indexes = [i for i in range(7,8)]
    #Total number of simulations
    overall_num_sim = 2#35
    # Define the starting and ending values of the interval
    start_val = sim_prms["backup_period_clks_start"]
    end_val = sim_prms["backup_period_clks_end"]
    backup_period_clks = []
    #The backup_clk values increase
    #The backup period of clk increases as a function
    #Since the CB policy shows variations of simulation results in the beginning
    #of the backup_period_clks interval we generate the samples with increasing
    #distance. Most of the backup_period_clks will be focused in the beginning
    #of the interval.
    for i in range(overall_num_sim):
        dist = (end_val - start_val) * ((i+1)/overall_num_sim)**2
        backup_period_clk = int(start_val + dist)
        backup_period_clks.append(backup_period_clk)
        

    
    NV_REG_FACTOR = 2
    num_sims = 2
    
    
    for k in indexes:
        threshold = values[k]
        voltage_trace_name = voltage_trace_names[k]
        done_sims = 0
        p_chunk = 0 
        while done_sims < overall_num_sim:
            remaining = overall_num_sim - done_sims
            if remaining > num_sims:
                done_sims += num_sims  #number of simulation done overall
                num_sim = num_sims     #number of simulation done at this step
                backup_period_clks_chunk = backup_period_clks[p_chunk*num_sim:(p_chunk+1)*num_sim-1] #chunk of the backup_period_clks to test
                generate_results(sim_prms = sim_prms, NV_REG_FACTOR=NV_REG_FACTOR, DNN_architecture=DNN_architecture, voltage_trace_name=voltage_trace_name, threshold=threshold, backup_period_clks_chunk=backup_period_clks_chunk)
            else:
                done_sims += remaining
                num_sim = remaining
                backup_period_clks_chunk = backup_period_clks[p_chunk*num_sim:-1]
                generate_results(sim_prms = sim_prms, NV_REG_FACTOR=NV_REG_FACTOR, DNN_architecture=DNN_architecture, voltage_trace_name=voltage_trace_name, threshold=threshold, backup_period_clks_chunk=backup_period_clks_chunk)
            p_chunk += 1