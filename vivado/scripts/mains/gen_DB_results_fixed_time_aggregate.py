# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 18:10:49 2023

Engineer: Michele Pio Fragasso


Description:
    --This script should generate DB results for a given DNN architecture,
    -- for different voltage trace at given NV_REG_DELAY_FACTOR.
    
    
    The motivation of this script is first of all try to abtain a larger amount
    of data to aggregate together:
    
    So far I identified some patterns:
    - The power consumption follows more or less the number of oscillation of 
    the voltage trace around the hazard threshold vs hazard threshold.
    How can I characterize this in one value I still have to find. But for sure I cannot
    do any fitting of the curve.
    
    -The throuput depends on the voltage trace and most likely from the
    DNN architecture. They exhibit an exponential decay wrt hazrd tghreshold
    so that's very interesting to show. I can characterize the voltage trace wrt
    the dacay factor
    
    1)I can bar chart the decay factor for different voltage trace and for
    different NV_REG_DELAY_FACTOR. This is what I want to do next!
    
    2)Also I can plot the decay factor for different DNN architectures
    (number of layers and sizes per layer)
    This justifies this script!

    So I need to perform more test with different DNNs
    architectures. Mostly it depends on the number of layer and the size per layer
    
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
        

def generate_results(NV_REG_FACTOR, DNN_architecture, voltage_trace_name, start_value_threshold, end_value_threshold, num_sim=20):
    voltage_trace_path = "voltage_traces/"+voltage_trace_name+".txt"
    voltage_trace_path_folder = "../src/NORM/voltage_traces/"+voltage_trace_name+".txt" 
    length_path = len(voltage_trace_path)
    testbench_path = "../../test/I_DNN_multiple_images_tb.vhd"
    #System clock period in ns
    system_clock_period = 40
    #System clock period in MHz
    system_clock_frequency = int(1/system_clock_period*10**(9))
    #The voltage trace timescale should be always greater than 4 times the system clock period
    voltage_trace_timescale = 160
    intermittency_prescaler = int(voltage_trace_timescale/system_clock_period)
    #Fixed Time defaults
    time_constant_us = 3_000
    #time_constant_us = 1
    #end_value_threshold = 4050
    threshold_step = int((end_value_threshold-start_value_threshold)/num_sim)

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
    db_results_path = "./results/"
    try:
        sys.mkdir(db_results_path)
    except:
        print("Folder ./results/ already exists")
        
    
    
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
        
    tcl_script_path = tcl_script_folder_path+"/DB_fixed_time_NVREG_DELAY_"+str(NV_REG_FACTOR)+"_simulation_batch.tcl"

    threshold_signal_path = "/I_DNN_multiple_images_tb/hazard_threshold"

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
    print("set fp [open " + db_results_path + "DB_results_fixedtime_NVREG_DELAY_FACTOR"+str(NV_REG_FACTOR)+"_"+voltage_trace_name+"_"+str(num_hidden_layers)+"_"+str(start_value_threshold)+"_"+str(end_value_threshold)+".txt w]")

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
    
if __name__=="__main__":
    DNN_architecture = {}
    #•DNN_architecture["num_hidden_layers"] = 12
    DNN_architecture["num_hidden_layers"] = 4
    #indexes contains the index to the voltage traces that you want to be synthesized
    indexes = [i for i in range(5,6)]
    #DNN 4 layer tets
    #indexes = [4,5,6,7,10]
    #indexes = [3]
    #indexes = [i for i in range(1,11)]
    #indexes = [i for i in range(8,11)]
    #DNN 12 layer tests
    
    #indexes = [i for i in range(1,11) if i!=2 ]
    voltage_trace_names = ["voltage_trace"+str(i) for i in range(1,11)]
    

    #VALUES is a vector of 10 elements. It's min_hzrd vs trace
    #Each element refers to a voltage trace and it contains the minimum hazard
    #threshold to ensure correct backup.
    #12 layer test
    #values = [2600,2550,2650,2650,2650,2650,2750,2400,2600,2450]
    #values = [2930 for i in range(1,11)]
    #4 layer test
    #values for NV_REG_DELAY = 11
    values= [2800,2650,2650,2850,2900,3250,2950,2450,2700,2450]#3250 was 2800
    #values for NV_REG_DELAY = 8
    #values = [2450, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #8layer DNN test twice as base
    #sizes = [120, 100, 60, 60, 50, 40, 30, 10]
    #values for NV_REG_DELAY = 2
    #values = [2500, 2500, 2650, 2500, 2500, 2500, 2550, 2400, 2550, 2400]#instead of 3412 there is 2500
    #values = [2520]
    #NV_REG_FACTOR5
    #values = [2550,2550,2650,2550,2600,2600,2400,2400,2600,2400]
    overall_final_value = 4000
    # for k in range(len(values)):
    #     name = voltage_trace_names[k]
    #     start_th[name] = values[k]
    NV_REG_FACTOR = 5
    step = 40
    num_sim = 20
    for k in indexes:
        start_value = values[k]
        voltage_trace_name = voltage_trace_names[k]
        while start_value < overall_final_value:
            end_value = start_value+num_sim*step
            generate_results(NV_REG_FACTOR=NV_REG_FACTOR, DNN_architecture=DNN_architecture, voltage_trace_name=voltage_trace_name, start_value_threshold=start_value, end_value_threshold=end_value,num_sim=num_sim)
            start_value = end_value