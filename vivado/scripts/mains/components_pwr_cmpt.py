# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 19:27:22 2023

Engineer: Michele Pio Fragasso


Description:
    This is the first script to produce data. It produces the power consumption
    for the single components from (layer_1, nvreg_1) to (layer_n, nvreg_n)

    This script is used to produce the power approximation values
    and instant power calculation for layers and non-volatile registers
    for different NVREG_DELAY_FACTOR
"""


import sys
sys.path.insert(0, "../functions/")

from matplotlib import pyplot as plt
import re
import os
import network2

#---------------------------Helper Functions-----------------------------------
def render_key(key):
    """
    This function renders the key to be displayed on plot, for plotting
    neat title for thesis submission.

    Parameters
    ----------
    key : string
        This is the signal name inside VHDL. It's formatted for code usability,
        but it's not rendered for readibility.
        
        Examples:
            nv_reg4_inst_pwr_save_state
            nv_reg4_pwr_apprx_save_state
            layer4_inst_pwr_save_state
            layer4_pwr_apprx_save_state
    Returns
    -------
    rendered_key : string
        This is the rendered version of key. It is used to present readable
        signal description for thesis submission
        
        Rendering Cases:
            The key "nv_reg4_inst_pwr_save_state" will be rendered to
            "Power Consumption SAVE STATE NVR4"
            
            The key "nv_reg4_pwr_apprx_save_state" will be rendered to
            "PA Value SAVE STATE NVR4"
            
            The key "layer4_pwr_apprx_save_state" will be rendered to
            "PA Valye SAVE STATE layer4"
            
            The key "layer4_inst_pwr_save_state" will be rendered to
            "Power Consumption SAVE STATE layer4"
            
            The key "total_power_consumption" is rendered as
            "Total Power Consumption"
            
            The key "throughput" is rendered as
            Throughput
            
            The key throughput_pwr_csmpt_W is rendered as
            Efficiency
            
            T

    """
    #To implement the rendering the sequence of rendered key parts need to be
    #extracted and concatenated at the end.
    #1) The sequence of strings is determined.
    #2) Next they are concatenated and the rendered key is determined.
       
    #SEQUENCE OF KEY RENDERED PARTS
    #Layer Number    
    layer_no_match = (re.search(r"\d+", key))
    layer_no = layer_no_match.group() if layer_no_match!=None else " "
    #Type of components
    cmpt_part = "NVR" if "nv_reg" in key else \
                "layer" if "layer" in key else \
                "None"
    #Type of power state
    pwr_state_part =    "SAVE STATE" if "save_state" in key else \
                        "REC STATE" if "rec_state" in key else \
                        "COMPUTE STATE" if "compute_state" in key else \
                        "IDLE STATE" if "idle_state" in key else \
                        "POWER ON" if "poweron" in key else \
                        "None"
    #Type of signal (PA value or Power Consumption)
    type_part = "Power Consumption" if "inst_pwr" in key else \
                "PA Value" if "pwr_apprx" in key else \
                "None"
    #Overall performance index
    overall_perf_string =   "Total Power Consumption" if "total_power_consumption"\
                                in key else \
                            "Efficiency" if "throughput_pwr_csmpt_W" in key else \
                            "Throughput" if "throughput" in key else \
                            "None"
    #Hazard Threshold
    hzrd_th_string =    "Hazard Threshold" if "hazard_threshold_val" in key else\
                         "None"   
    #Rendering for components
    rendered_key =  (type_part + " " + pwr_state_part + " " + cmpt_part + layer_no) \
                        if cmpt_part != "None" else \
                    overall_perf_string if overall_perf_string != "None" else \
                    hzrd_th_string if hzrd_th_string != "None" else \
                    key
    return (rendered_key)

enable_plot_save = True
NV_REG_FACTORS = [2,5,8,11]

results_plots_path = "./plots/DB_components_pwr_cmpt/"
DB_result_log_path = "./results/DB_result_log.txt"
voltage_trace_namefile = "voltage_trace2"

try:
    os.mkdir(results_plots_path)
except:
    pass

#Generating list of DB result paths. There is a result per NV_REG_DELAY_FACTOR
#We have to generate results for every NV_REG_FACTOR.
#foldername = "4layer_80"
foldername = "4layer_80_powerpoint"
results_path_list = []
for NV_REG_FACTOR in NV_REG_FACTORS:
    results_path_list.append("./results/DB_results/"+foldername+"/"+voltage_trace_namefile+"/DB_results_fixedtime_NVREG_DELAY_FACTOR"+str(NV_REG_FACTOR)+".txt")
results_name = "DB"
result_figures_list = []
#end_data_fixed_time_simulations is a list where every entry refers to a
#NV_REG_FACTOR
end_data_fixed_time_simulations = []
#Computing the numebr of hidden layers, it is used to determine the number of
#hidden layers.
net = network2.load("../files/weights_n_biases/training_04-20-23_14-50-41/WeightsAndBiases.txt")
number_neurons = net.sizes[1:]
num_hidden_layers = len(number_neurons)

"""GENERATING LIST OF END-OF-SIMULATION SIGNALS"""
#It arrange the end-of-simulation values in two lists
i_factor = 0 #index of NV_REG_FACTORS list
for results_path in results_path_list:
    NV_REG_FACTOR = NV_REG_FACTORS[i_factor]
    results_file = open(results_path, 'r')
    allLines = results_file.readlines()
    data_fix_time_tmp = []
    start_fix_time = 0
    #Generating list of signal names
    for i, line in enumerate(allLines):
        if "voltage_trace" in line:
            vt_line = line
            voltage_trace_name = vt_line.rstrip(vt_line[-1])
        if "Fixed time simulation start" in line:
            start_fix_time = 1
        else:
            if start_fix_time == 1:
                if "Fixed time simulation end" not in line:
                    data_fix_time_tmp.append(str(line.strip()))
                else:
                    start_fix_time = 0
    names_fixed_time = list(filter(None,data_fix_time_tmp.pop(0).split(";")))
    #Generating dictionary of end-of-sim signals, where avery elements contains
    #the end-of-simulation signal value for a given hazard threshold
    #Setting-up dictionary
    end_data_fixed_time = {}
    for key in names_fixed_time:
        end_data_fixed_time[key] = []
    #Filling dictionary entrie
    for i,data in enumerate(data_fix_time_tmp):
        data=list(filter(lambda x: None if '' else str(x),data.split(";")))
        for j,item in enumerate(data):
            divide = 1
            if "ms" in item:
                divide = 10**-3
            elif "ns" in item:
                divide = 10**-3
            elif "ps" in item:
                divide = 10**-9
            else:
                None
            key = names_fixed_time[j]
            #[^0-9] is a pattern to search any character which is not a digit
            #It's part of the regular expression standard.
            item = int(re.sub(r"[^0-9]", "",item))
            end_data_fixed_time[key].append(item*divide)
    results_file.close()
    #It happends the NV_REG_FACTOR simulation result to the list of simulations
    end_data_fixed_time_simulations.append(end_data_fixed_time)
    i_factor += 1

"""PERFORMANCE INDEXES"""
#Instant Power Calculation
#   1) For every I-layer
#   2) For every nv_reg
test_no = 0
for NV_REG_FACTOR in NV_REG_FACTORS:
    """Power Model"""
    #Layer
    PWR_STATE_LAYER_IDLE = 1/1_000_000
    PWR_STATE_LAYER_COMP_DEF = 100/1_000_000
    #Number of neurons for which the layer uses PWR_COMP_DEF during computation
    BASE_NEURONS = 30 
    PWR_STATE_LAYER_COMP =  [neurons*PWR_STATE_LAYER_COMP_DEF/BASE_NEURONS for neurons in number_neurons]
    PWR_STATE_LAYER_SAVE = 20/1_000_000
    PWR_STATE_LAYER_REC = 20/1_000_000
    #Non-volatile reegister
    PWR_NVREG_POWERON = 1/1_000_000
    BASE_DELAY_FACTOR = 2
    PWR_NVREG_RECOVERY_DEF = 10000/1_000_000
    PWR_NVREG_SAVE_DEF = 10000/1_000_000
    PWR_NVREG_RECOVERY = ((BASE_DELAY_FACTOR/NV_REG_FACTOR)**1)*PWR_NVREG_RECOVERY_DEF
    PWR_NVREG_SAVE = ((BASE_DELAY_FACTOR/NV_REG_FACTOR)**1)*PWR_NVREG_SAVE_DEF

    end_data_fixed_time = end_data_fixed_time_simulations[test_no]
    for i in range(num_hidden_layers):
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_idle_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_idle_state"
        inst_pwr = [PWR_STATE_LAYER_IDLE*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_compute_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_compute_state"
        inst_pwr = [PWR_STATE_LAYER_COMP[i]*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_save_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_save_state"
        inst_pwr = [PWR_STATE_LAYER_SAVE*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_rec_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_rec_state"
        inst_pwr = [PWR_STATE_LAYER_REC*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_poweron_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_poweron_state"
        inst_pwr = [PWR_NVREG_POWERON*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_rec_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_rec_state"
        inst_pwr = [PWR_NVREG_RECOVERY*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_save_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_save_state"
        inst_pwr = [PWR_NVREG_SAVE*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
    test_no += 1

"""OVERALL PERFORMANCE INDEXES"""
#1)Total power consumption
#2)Executed Batches
#3)Throughput (Executed batches/sim_time)
#4)Efficiency (Throughput/Total Power Consumption)
test_no = 0
for NV_REG_FACTOR in NV_REG_FACTORS:
    pwr_csmpt = [0 for c in range(len(end_data_fixed_time_simulations[test_no]["hazard_threshold_val"]))]
    for i in range(num_hidden_layers):
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_idle_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_idle_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time_simulations[test_no]["hazard_threshold_val"]))]
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_compute_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_compute_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time_simulations[test_no]["hazard_threshold_val"]))]
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_save_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_save_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time_simulations[test_no]["hazard_threshold_val"]))]
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_rec_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_rec_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time_simulations[test_no]["hazard_threshold_val"]))]
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_poweron_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_poweron_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time_simulations[test_no]["hazard_threshold_val"]))]
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_rec_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_rec_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time_simulations[test_no]["hazard_threshold_val"]))]
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_save_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_save_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time_simulations[test_no]["hazard_threshold_val"]))]
    end_data_fixed_time_simulations[test_no]["total_power_consumption"] = pwr_csmpt
    end_data_fixed_time_simulations[test_no]["throughput"] = [end_data_fixed_time_simulations[test_no]["executed_batches"][k]/end_data_fixed_time_simulations[test_no]["time"][k] for k in range(len(end_data_fixed_time_simulations[test_no]["time"]))]
    end_data_fixed_time_simulations[test_no]["throughput_pwr_csmpt_W"] = [end_data_fixed_time_simulations[test_no]["throughput"][k]/end_data_fixed_time_simulations[test_no]["total_power_consumption"][k]*1000 for k in range(len(end_data_fixed_time_simulations[test_no]["hazard_threshold_val"]))]
    test_no += 1


#Uploading the signal names, they now include the performance indexes
#Uploading the total number of simulation objects as well
test_no = 0
for NV_REG_FACTOR in NV_REG_FACTORS:
    names_fixed_time = list(end_data_fixed_time_simulations[test_no].keys())
    test_no += 1
number_objects = len(end_data_fixed_time_simulations[0])


"""PLOTTING END-OF-SIMULATION SIGNALS"""
#In this section the END-OF-SIMULATION signals are produced.
#They include:
    #1) Power Approximation Values
    #2) Instant Power Consumption Values
    #3) Performance Indexes Values
for i in range(number_objects):
    result_figures_list.append(plt.figure())
test_no = 0
for NV_REG_FACTOR in NV_REG_FACTORS:
    names_fixed_time = list(end_data_fixed_time_simulations[test_no].keys())
    end_data_fixed_time = end_data_fixed_time_simulations[test_no]
    for i in range(number_objects):
        key_xaxis = "hazard_threshold_val"
        key_yaxis = names_fixed_time[i]
        rendered_key_xaxis = "Hazard Threshold [mV]"
        rendered_key_yaxis = render_key(names_fixed_time[i])
        #ax.append(result_figures_list[i].gca())
        ax = result_figures_list[i].gca()
        
        
        xlabel = "Hazard Threshold [mV]"
        ytitle = rendered_key_yaxis
        if "Power" in ytitle:
            unit_string = " [mW]"
            ylabel = "Power Consumption"
        else:
            if "PA" in ytitle:
                unit_string = " [No. Cycles]"
                ylabel = "PA Value"
            else:
                if "Total" in ytitle:
                    unit_string = " [mW]"
                    ylabel = rendered_key_yaxis
                else:
                    if "Throughput" in ytitle and "throughput_pwr" not in ytitle:
                        unit_string = "[Op/s]"
                        ylabel = rendered_key_yaxis
                    else:
                        if "Efficiency"  in ytitle:
                            unit_string += "[Op/s/mW]"
                            ylabel = rendered_key_yaxis
                        else:
                            unit_string = "" 
                            ylabel = rendered_key_yaxis
        ylabel += unit_string
        title = ytitle + " vs. Hazard Threshold"
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.plot(end_data_fixed_time[key_xaxis],end_data_fixed_time[key_yaxis], label="NVREG_FACTOR="+str(NV_REG_FACTOR))
        ax.legend()
        ax.grid(True)
    test_no += 1
plt.show()


# #PLOTTING AND SAVING PLOT FOR FINDING OPTIMAL VALUE
# #THORUGHPUT OF NVREG _FACTOR = 2
NV_REG_FACTOR = 2
index = [index for index,value in list(enumerate(NV_REG_FACTORS)) if NV_REG_FACTORS[index] == NV_REG_FACTOR][0]
end_data_fixed_time = end_data_fixed_time_simulations[index]

# #OPTIMAL VALUE GIVEN NUMBER NEURONS
# #Plotting the optimal value starting from the target hazard threshold
hazard_target = 2480 #Valur found from singl trace analysis
#Searching for the maximum in the right neighbourhood
indexes = [index for index, value in list(enumerate(end_data_fixed_time[names_fixed_time[0]])) if value > hazard_target]
index = min(indexes)
hazard_rounded = end_data_fixed_time[names_fixed_time[0]][index]
throughput_rounded = end_data_fixed_time[names_fixed_time[-1]][index]
section_throughput = end_data_fixed_time[names_fixed_time[-1]][index:]
index_opt = section_throughput.index(max(section_throughput))
opt_throughput = section_throughput[index_opt]
opt_threshold = end_data_fixed_time[names_fixed_time[0]][index_opt+index]
optimal_value_neurons_plot = "opt_value_neurons"
key_xaxis = "hazard_threshold_val"
key_yaxis = names_fixed_time[-1]
#ax.append(result_figures_list[i].gca())
fig = plt.figure()
axis = fig.gca()
title = "Fixed Time Results - Hazard Threshold vs."+names_fixed_time[-1]
xlabel = "Hazard Threshold [mV]"
ylabel = names_fixed_time[-1]
if "inst_pwr" in title:
    ylabel += " [mW]"
if "apprx_values" in title:
    ylabel += " [No. Cycles]"
if "total" in title:
    ylabel += " [mW]"
if "throughput" in title and "throughput_pwr" not in title:
    ylabel += "[Op/s]"
if "throughput_pwr"  in title:
    ylabel += "[Op/s/mW]"
axis.set_title(title)
axis.set_xlabel(xlabel)
axis.set_ylabel(ylabel)
axis.plot(end_data_fixed_time[key_xaxis],end_data_fixed_time[key_yaxis], color="crimson",label="NVREG_FACTOR="+str(NV_REG_FACTOR))
axis.legend()
axis.grid(True)
#Computing Throughput, Normalized
#Starting point
axis.plot(hazard_rounded, throughput_rounded, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
axis.text(hazard_rounded+100, throughput_rounded-2000, "Starting Point: ("+ str(int(hazard_rounded))+" mV ,"+str(int(throughput_rounded))+" OP/s/mW )",bbox = dict(facecolor='blue', alpha=0.5))
#Optimal 
axis.plot(opt_threshold, opt_throughput, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
axis.text(opt_threshold+100, opt_throughput+1000, "Optimal Value: ("+ str(int(opt_threshold))+" mV ,"+str(int(opt_throughput))+" OP/s/mW )",bbox = dict(facecolor='blue', alpha=0.5))
fig.savefig(results_plots_path+optimal_value_neurons_plot,dpi=1260)

# #OPTIMAL VALUE GIVEN THROUGHPUT SPECIFICATION
# #TARGET THROGUHTPUT VALUE
throughput_target_figname = "throughput_target"
throughput_target = 10_000
indexes = [index for index, value in list(enumerate(end_data_fixed_time[names_fixed_time[-2]])) if value <= throughput_target]
index = min(indexes)
throughput_rounded = end_data_fixed_time[names_fixed_time[-2]][index]
throughput_W_rounded = end_data_fixed_time[names_fixed_time[-1]][index]
hazard_target = end_data_fixed_time[names_fixed_time[0]][index]
#Plotting data of throughput figure
key_xaxis = "hazard_threshold_val"
key_yaxis = names_fixed_time[-2]
#ax.append(result_figures_list[i].gca())
fig = plt.figure()
axis = fig.gca()
title = "Fixed Time Results - Hazard Threshold vs."+names_fixed_time[-2]
xlabel = "Hazard Threshold [mV]"
ylabel = names_fixed_time[-2]
if "inst_pwr" in title:
    ylabel += " [mW]"
if "apprx_values" in title:
    ylabel += " [No. Cycles]"
if "total" in title:
    ylabel += " [mW]"
if "throughput" in title and "throughput_pwr" not in title:
    ylabel += "[Op/s]"
if "throughput_pwr"  in title:
    ylabel += "[Op/s/mW]"
axis.set_title(title)
axis.set_xlabel(xlabel)
axis.set_ylabel(ylabel)
axis.plot(end_data_fixed_time[key_xaxis],end_data_fixed_time[key_yaxis], color="crimson",label="NVREG_FACTOR="+str(NV_REG_FACTOR))
axis.legend()
axis.grid(True)
axis.axhline(throughput_target)
#Start ingPoint
axis.plot(hazard_target, throughput_rounded, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
axis.text(hazard_target+100, throughput_rounded+1000, "Starting Point: "+str(int(hazard_target))+" mV , "+str(int(throughput_target))+" Op/s", bbox = dict(facecolor='blue', alpha=0.5))
fig.savefig(results_plots_path+throughput_target_figname+"",dpi=1060)


# #OPTIMAL HAZARD THRESHOLD
# #Finding optimal Hazard threshold
optimal_threshold_throughput_figname = "optimal_threshold_throughput"
section_throughput = end_data_fixed_time[names_fixed_time[-1]][index:]
index_opt = section_throughput.index(max(section_throughput))
opt_throughput = section_throughput[index_opt]
opt_threshold = end_data_fixed_time[names_fixed_time[0]][index_opt+index]
#Plotting
key_xaxis = "hazard_threshold_val"
key_yaxis = names_fixed_time[-1]
#ax.append(result_figures_list[i].gca())
fig = plt.figure()
axis = fig.gca()
title = "Fixed Time Results - Hazard Threshold vs."+names_fixed_time[-1]
xlabel = "Hazard Threshold [mV]"
ylabel = names_fixed_time[-1]
if "inst_pwr" in title:
    ylabel += " [mW]"
if "apprx_values" in title:
    ylabel += " [No. Cycles]"
if "total" in title:
    ylabel += " [mW]"
if "throughput" in title and "throughput_pwr" not in title:
    ylabel += "[Op/s]"
if "throughput_pwr"  in title:
    ylabel += "[Op/s/mW]"
axis.set_title(title)
axis.set_xlabel(xlabel)
axis.set_ylabel(ylabel)
axis.plot(end_data_fixed_time[key_xaxis],end_data_fixed_time[key_yaxis], color="crimson",label="NVREG_FACTOR="+str(NV_REG_FACTOR))
axis.legend()
axis.grid(True)
#Start Point
axis.plot(hazard_target, throughput_W_rounded, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
axis.text(hazard_target+100, throughput_W_rounded-2000, "Starting Point: "+str(int(hazard_target))+" mV , "+str(int(throughput_W_rounded))+" Op/s/mW", bbox = dict(facecolor='blue', alpha=0.5))

#Computing Throughput, Normalized 
axis.plot(opt_threshold, opt_throughput, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
axis.text(opt_threshold+100, opt_throughput+1000, "Optimal Value: ("+ str(int(opt_threshold))+" mV ,"+str(int(opt_throughput))+" OP/s/mW )",bbox = dict(facecolor='blue', alpha=0.5))
fig.savefig(results_plots_path+optimal_threshold_throughput_figname+"",dpi=1260)
        
test_no = 0
wrng_values = end_data_fixed_time_simulations[test_no]["hazard_threshold_val"][0:50]
power_consumption = end_data_fixed_time_simulations[test_no]["total_power_consumption"][0:50]
I_layer1_cycle_save_state = end_data_fixed_time_simulations[test_no]["I_layer1_pwr_apprx_values_save_state"][0:50]
throughput_per_power = end_data_fixed_time_simulations[test_no]["throughput_pwr_csmpt_W"][0:50]
#Loading voltage trace
vt_path = "../../src/NORM/voltage_traces/"+voltage_trace_namefile+".txt"
vt_file = open(vt_path,"r")
allLines = vt_file.readlines()
vt_file.close()
vt_voltages_original = [int(line) for line in allLines]
#vt_voltages = vt_voltages_original
vt_voltages = vt_voltages_original[0:10000]
vt_voltages += vt_voltages_original[0:8750]
#Computing number of oscillations
oscs = []
for wrng_value in wrng_values:
    osc = 0
    for i in range(len(vt_voltages)-1):
        if vt_voltages[i] > wrng_value and vt_voltages[i+1] < wrng_value:
            osc += 1
    oscs.append(osc)

fig = plt.figure()
ax1 = fig.gca()
ax1.plot(wrng_values, oscs, color="blue")
ax1.set_ylabel('Number of oscillations', color='blue')


ax2 = ax1.twinx()
ax2.plot(wrng_values, power_consumption, color="red")
ax2.set_ylabel('Power Consumption', color='red')
ax2.grid(True)
plt.show()


#Comparing power consumption versus number of oscillations as function of hazard threshold


#SAVING PLOT
if enable_plot_save == True:
    print("Saving Plots...")
    for i in range(number_objects):
        fig = result_figures_list[i]
        key_yaxis = names_fixed_time[i]
        fig.savefig(results_plots_path+key_yaxis,dpi=1060)
    print("Finished Saving!")

