# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 18:10:49 2023

Engineer: Michele Pio Fragasso

Description:
    This script generates DB results for a given DNN architecture,
    for different voltage traces at given NV_REG_DELAY_FACTOR.
    
    I noticed that the simulation crashes if too many simulations are performed
    without restarting the Vivado simulator. Therefore the number of simulations
    in betwwen the initial hazard threshold (stored inside <values[i]>) and
    the final hazard threhsold (<overall_final_value>) is split up in smaller
    dimension batches of dimension <num_sim>.
    
    MOTIVATION
    The motivation of this script is:

        1) VOLTAGE TRACE ANALYSIS:
            Evaluate a given DNN for all voltage traces but it has also been used to study different DNN
            for the same voltage trace. 

        VOLTAGE TRACE ANALYSIS:
            
            I identified some patterns:
            1) The power consumption follows more or less the number of oscillation of 
            the voltage trace around the hazard threshold vs hazard threshold.
            How can I characterize this in one value I still have to find. But for sure
            I cannot do any fitting of the curve.
                
            2)The throughput depends on the voltage trace and most likely from the
            DNN architecture. They exhibit an exponential decay wrt hazrd tghreshold
            so that's very interesting to show. I can characterize the voltage trace wrt
            the dacay factor
            
            1)POWER CONSUMPTION
            To express the dependence correlation between power consumption and number
            of oscillations was computed for different vts. Guesses were confirmied
            
            2) TROUGHPUT
            1)I can bar chart the decay factor for different voltage trace and for
            different NV_REG_DELAY_FACTOR. This is what I want to do next!
        
        2) DNN ANALYSIS
    
            By running this script multiple times by setting a different DNN
            architecture (see usage) I can do performance analysis for different 
            DNN (number of layers and sizes per layer)
            
    This justifies this script!

INPUTS
    The inuts are located in the main section of this python script
    
    num_hidden_layers   : Contain the number of the hidden layers of the
                            architecture to be tested. This data is taken from
                            the training_file.txt maximum size
    
    indexes             : List voltage trace indexes, they range
                            between 0 and 9. The script will run simulation
                            for the voltage traces specified in this list.
    
    values              : Vector of 10 values. Every refer to a voltage trace
                            and is the mininum threshold to allow correct
                            backup with data corruption. Values are computed by
                            running the script "preanalysis_single_vt.py"
                            This list must be filled entirely even if some
                            voltage traces are not analysied
    
    overall_final_value : Hazard threshold end value.
   
    NV_REG_FACTOR       : NV_REG_FACTOR to be tested
    
    num_sim             : batch size for number of consecutive simulations.
    
    step                : hazard threshold step.
    
OUTPUTS:
    Set of results file.
    
    For every voltage trace there is a set of result files, each one referring
    to a batch of simulation in between the initial and final threshold value.
    
USAGE:
    
    Before running the script ensure that the DB policy is commented,
    especially after the testbench was run manually.
    
    Also endure 
    
    FAQS:
    1) How can I test the DNN for different DNNs?
    Answer:
    You first set up training_file.txt. At that point you run trainNN.py and
    the new DNN architecture is loaded into the vivado project. Under this 
    scenario you most lkely want to run the architecture for only one voltage
    trace, therefore the "index" variable should contain the voltage trace
    index to be analyzed.
    
    2) How can I load a previously trained DNN and run the simulation with that
    DNN?
    Answer:
    You can find all the DNN models in ../files/weights_n_biases/. All you
    need to do is to copy and paste only the generated architectures inside
    VHDL_output:
        DNN.vhd, DNN_package.vhd and MI_DNN_package.vhd must be put inside
        ../../src/DNN
        NVME_framework.vhd has to be inside ../../src/NORM
        
    
    
IMPORTANT NOTES:
    1)To stop simulating, in Spyder you should restart the kernel. Anyway, if you
    do this,the dynamic backup policy within DNN.vhd file
    is not commented back therefore producing 
    an error when running again this simulating script (the result file will be
    empty). In that case make sure you comment it manually!!!

    2)A big DNN architecture, a high simulation time or a high number of
    consecutive simulations (num_sim), can produce a crash during simulation.
    You should start by setting num_sim to 1 and then gradually increasing
    to check what is the crash limit for that particular DNN architecture.
    Also a crash results in the missed commenting of the backup policy. So make
    sure you comment it.
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
    
    
def uncomment_DB_DNN():
    DNN_path = "../../src/DNN/I_DNN.vhd"
    DB_start_marker = "##DB##Start"
    DB_end_marker = "##DB##End"
    ctl = open(DNN_path, "r+")
    DNN_VHDL_lines = ctl.readlines()
    start_index = [index for index, code_line in enumerate(DNN_VHDL_lines) if DB_start_marker in code_line][0]
    end_index = [index for index, code_line in enumerate(DNN_VHDL_lines) if DB_end_marker in code_line][0]

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
    
def comment_DB_DNN():
    DNN_path = "../../src/DNN/I_DNN.vhd"
    DB_start_marker = "##DB##Start"
    DB_end_marker = "##DB##End"
    ctl = open(DNN_path, "r+")
    DNN_VHDL_lines = ctl.readlines()
    start_index = [index for index, code_line in enumerate(DNN_VHDL_lines) if DB_start_marker in code_line][0]
    end_index = [index for index, code_line in enumerate(DNN_VHDL_lines) if DB_end_marker in code_line][0]

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
    
    uncomment_DB_DNN()

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
    db_results_path = "./results/DB_results/"
    try:
        sys.mkdir(db_results_path)
    except:
        print("Folder ./results/DB_results already exists")
        
        
    
    
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


        db_fix_val_cmds[layer_pwr_appr_idle_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(0)]"
        db_fix_val_cmds[layer_pwr_appr_compute_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(1)]"
        db_fix_val_cmds[layer_pwr_appr_save_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(2)]"
        db_fix_val_cmds[layer_pwr_appr_rec_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_layer"+str(i+1)+"/power_counter_val(3)]"
        db_fix_val_cmds[nv_reg_pwr_appr_poweron_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg"+str(i+1)+"/power_counter_val(0)]"
        db_fix_val_cmds[nv_reg_pwr_appr_rec_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg"+str(i+1)+"/power_counter_val(1)]"
        db_fix_val_cmds[nv_reg_pwr_appr_save_state_key] = "[get_value -radix unsigned /I_DNN_multiple_images_tb/I_DNN_cmp/pwr_appr_comp_nvreg"+str(i+1)+"/power_counter_val(2)]"

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
    ########################## RUN GENERATED BATCH FIlE###############################
    run_line = vivado_path + " -mode batch -source " + tcl_script_path

    print("Executing: " + str(run_line))
    os.system(run_line)
    
    print("Simulation Ended!!")
    
    comment_DB_DNN()
    
if __name__=="__main__":
    #Do not change this
    voltage_trace_names = ["voltage_trace"+str(i) for i in range(1,11)] 
    DNN_architecture = {}
    
    
    #####################################INPUTS###############################
    #VALUES SETUP
    """DNN_max_size = 30"""
    #values for NV_REG_DELAY = 2
    #values = [2450, 2500, 2500, 2400, 2400, 2450, 2500, 2400, 2450, 2400]
    #values for NV_REG_DELAY = 4
    #values = [2450, 2500, 2500, 2400, 2400, 2450, 2500, 2500, 2450, 2400]
    #values for NV_REG_DELAY = 8
    #values = [2450, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #VALUES for NV_REG_FACTOR = 11
    #values= [2800,2650,2650,2850,2900,2800,2950,2450,2700,2450]
    """DNN_max_size = 120"""
    #The DNN layer sizes are:
    #sizes = [120, 100, 60, 60, 50, 40, 30, 10]
    #values for NV_REG_DELAY = 2
    #values = [2500, 2500, 2650, 2500, 2500, 2500, 2550, 2400, 2550, 2400]
    #values for NV_REG_DELAY = 5
    #values = [2550,2550,2650,2550,2600,2600,2400,2400,2600,2400]
    """DNN_max_size = 50"""
    #sizes
    #(50,40,30,25,10)
    #NVREG_FACTOR = 2
    #values = [2450, 2600, 2600, 2500, 2500, 2550, 2550, 2450, 2550, 2450]
    #NVREG_FACTOR = 3
    #values = [2550, 2650, 2650, 2550, 2550, 2650, 2700, 2450, 2650, 2450]
    #OTHER INPUTS
    """DNN_max_size = 40"""
    values = [0,2500,0,0,0,0,0,0,0,0]
    DNN_architecture["num_hidden_layers"] = 4
    NV_REG_FACTOR = 2
    indexes = [1]
    overall_final_value = 2950
    step = 30
    num_sim = 5
    #################################END_INPUTS################################
    

    for k in indexes:
        start_value = values[k]
        voltage_trace_name = voltage_trace_names[k]
        while start_value < overall_final_value:
            end_value = start_value+num_sim*step
            #Generate results for num_sim simulations
            generate_results(NV_REG_FACTOR=NV_REG_FACTOR, DNN_architecture=DNN_architecture, voltage_trace_name=voltage_trace_name, start_value_threshold=start_value, end_value_threshold=end_value,num_sim=num_sim)
            #Upload start_value
            start_value = end_value
            