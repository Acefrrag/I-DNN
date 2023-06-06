# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 22:41:51 2023

Engineer: Michele Pio Fragasso


Description:
    This file collects and plots the CB results for a given DNN for one or more voltage trace.
    Also apply a power consumption model to compute the power consumption.
"""

import re
import os

#POWER MODEL
"""LAYER"""
num_hidden_layers = 4
sizes = [30, 25, 15, 10]
PWR_STATE_LAYER_IDLE = 1/1_000_000
PWR_STATE_LAYER_COMP_DEF = 100/1_000_000
BASE_NEURONS = 30 #Number of neurons for which the layer uses PWR_COMP_DEF during computation
PWR_STATE_LAYER_SAVE = 20/1_000_000
PWR_STATE_LAYER_REC = 20/1_000_000
"""NV_REG"""
PWR_NVREG_POWERON = 1/1_000000
BASE_DELAY_FACTOR = 2
PWR_NVREG_RECOVERY_DEF = 10_000/1_000_000
PWR_NVREG_SAVE_DEF = 10_000/1_000_000

enable_plot_save = True

def data_from_lines(allLines):
    """
    This function returns a dictionary of the end-of-simulation values given the
    lines read from the results files

    Parameters
    ----------
    allLines : list
        list of strings

    Returns
    -------
    end_data_fixed_time: dictionary
        dictionary of end-of-simulation values
    """
    data_fix_time_tmp = []
    start_fix_time = 0
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
    
    end_data_fixed_time = {}
    end_data_fixed_val = {}
    for key in names_fixed_time:
        end_data_fixed_time[key] = []
        end_data_fixed_val[key] = []
        
    
    #[^0-9] is a pattern to search any character which is not a digit
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
            item = int(re.sub(r"[^0-9]", "",item))
            end_data_fixed_time[key].append(item*divide)
            
    return(end_data_fixed_time)
    
def overall_data(end_data_fixed_time, NV_REG_FACTOR):
    """
    This function makes a completion of the end-of-simulation data with the 
    power consumption values, including efficiency.

    Parameters
    ----------
    end_data_fixed_time : TYPE
        DESCRIPTION.
    NV_REG_FACTOR : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """


    #INSTANTANEUOS POWER CONSUMPTION LAYER
    PWR_STATE_LAYER_COMP =  [neurons*PWR_STATE_LAYER_COMP_DEF/BASE_NEURONS for neurons in sizes]
    #INSTANTANEUOS POWER CONSUMPTION NVREG
    PWR_NVREG_RECOVERY = ((BASE_DELAY_FACTOR/NV_REG_FACTOR)**1)*PWR_NVREG_RECOVERY_DEF
    PWR_NVREG_SAVE = ((BASE_DELAY_FACTOR/NV_REG_FACTOR)**1)*PWR_NVREG_SAVE_DEF

    #Computing instant power per unit per power state
    for i in range(num_hidden_layers):
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_idle_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_idle_state"
        inst_pwr = [PWR_STATE_LAYER_IDLE*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time[key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_compute_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_compute_state"
        inst_pwr = [PWR_STATE_LAYER_COMP[i]*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time[key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_save_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_save_state"
        inst_pwr = [PWR_STATE_LAYER_SAVE*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time[key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_rec_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_rec_state"
        inst_pwr = [PWR_STATE_LAYER_REC*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time[key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_poweron_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_poweron_state"
        inst_pwr = [PWR_NVREG_POWERON*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time[key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_rec_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_rec_state"
        inst_pwr = [PWR_NVREG_RECOVERY*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time[key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_save_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_save_state"
        inst_pwr = [PWR_NVREG_SAVE*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time[key_pwr_csmpt] = inst_pwr

    #Computing the total power consumption for the DNN
    pwr_csmpt = [0 for c in range(len(end_data_fixed_time["backup_period_clks"]))]
    for i in range(num_hidden_layers):
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_idle_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_idle_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time[key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_compute_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_compute_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time[key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_save_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_save_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time[key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_rec_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_rec_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time[key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_poweron_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_poweron_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time[key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_rec_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_rec_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time[key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_save_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_save_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time[key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]

    #Computing throughput and throughput per power consumption(efficiency)
    end_data_fixed_time["total_power_consumption"] = pwr_csmpt
    end_data_fixed_time["throughput"] = [end_data_fixed_time["executed_batches"][k]/end_data_fixed_time["time"][k] for k in range(len(end_data_fixed_time["time"]))]
    end_data_fixed_time["throughput_pwr_csmpt"] = [end_data_fixed_time["throughput"][k]/end_data_fixed_time["total_power_consumption"][k]*1000 for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]

def load_data(input_path):
    
    f = open(input_path, "r")
    allLines= f.readlines()
    f.close()
    
    return(allLines)


def print_possible 

if __name__=="__main__":
    output_path = "./plots/CB_analysis_vt_plots/"
    try:
        os.mkdir(output_path)
    except:
        pass

    voltage_trace_names = ["voltage_trace"+str(i) for i in range(11)]
    input_path = "./results/CB_results/4layer80/"
    
    NV_REG_FACTOR = 2
    
    
    
    
    
    