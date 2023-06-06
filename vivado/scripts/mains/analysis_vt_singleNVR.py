# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 09:08:19 2023

Engineer: Michele Pio Fragasso


Description:
    
    This script computes the relevant indexed performances for all voltage traces
    
    
    This script compares the results for all different voltage traces
    for different DELAY_FACTOR, for a 4 layer DNN. Also, this script contains
    the POWER MODEL used by pwr_cmpt_validation.py in order to validate it.
    This script is intended to be used for a specific DNN archicture so you 
    should not modify it.
    
    The script computes performance indexes for different hazard thresholds.
    
    The performance indexes analyzed are throughput and power consumption.
     
    THROUGHPUT
    For the throughput an exponential decay has been noticed (you can 
    check it by setting plt_show=True for the compute_fit_param).
    Therefore for every voltage trace and for every NVR_FACTOR an exponential
    fit has been performed. The decay factor is of low covariance, while
    the initial throughput amplitude covariance is high.
    
    For some fitting the covariance matrix could not be estimated. Therefore
    the option method was set to trf. In this way the Penros pseudo inverse
    matrix is computed.
    
    POWER CONSUMPTION
    
    The power consumption showed a strong correlation with the voltage trace
    oscillations around the hazard threshold. Therefore the person correlation
    coefficent has been computed for all voltage traces
    
    INPUTS
        enable_sngl_plot_show       : Boolean
            True: It enable to plot show of the power consumption of the single
            I-DNN components  (layers and nv_regs)
            This also disable the characterization plots (THROUGHPUT fit and POWER
                                                          CONSUMPTION)
            False: The opposite. It enables the characterization plots and
            disables the single plots
    
        POWER MODEL                 : Variables
            The power model was set after running pwr_cmpt_validation.py
            Note that pwr_cmpt_validation.py calls this python script to set the power
            model. Modifying the power model has effects on pwr_cmpt_validation.py
            LAYER
            PWR_STATE_LAYER_IDLE        : Power Consumption idle layer in uW
            PWR_STATE_LAYER_COMP_DEF    : Power Consumption compute_state in uW for
                                            base neurons
            BASE_NEURONS                : Base Neuron number. It's the number of
                                            neurons for which the layer consumes
                                            PWR_STATE_LAYER_LAYER_DEF
            PWR_STATE_LAYER_SAVE        : Power Consumption save state in uW
            PWR_STATE_LAYER_REC         : Power Consumption recovery state in uW
            
            
            NON VOLATILE REGISTER
            PWR_NVREG_POWERON           : Power Consumption for idle NVR
            BASE_DELAY_FACTOR           : Delay Factor corresponding to the
                                            smallest power consumption
            PWR_NVREG_RECOVERY_DEF      : Power Consumption during recovery (EN=1)
            PWR_NVREG_SAVE_DEF          : Power Consumption during save 
                                            (EN=1 and WE=1)s
        DNN information
        
        num_hidden_layers. You should not modify this value

    SIMULATION RESULTS
        The simulation results refer to a 4 layer DNN.
        This value should not be really modified.
"""

import re
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
import numpy as np
import os
import time
import sys
sys.path.insert(0,"../functions/")

from power_model import *


"""DNN information. Do not change!!"""
num_hidden_layers = 4
sizes = [30, 25, 15, 10]
#Demo values
#num_hidden_layer = 8
#sizes = [100,80,70,50,40,30,25,10]
"""OPTIONS"""
enable_plot_save = True
enable_sngl_plot_show = False
"""OUPUTFOLDER"""
OVERALL_performance_index_outputpath = "./plots/DB_vt_analysis_OVERALL_performance_index/"
SINGLE_performance_index_outputpath = "./plots/DB_vt_analysis_SINGLE_performance_index/"

try:
    os.mkdir(OVERALL_performance_index_outputpath)
except:
    pass
try:
    os.mkdir(SINGLE_performance_index_outputpath)
except:
    pass


def data_from_lines(allLines):
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
    pwr_csmpt = [0 for c in range(len(end_data_fixed_time["hazard_threshold_val"]))]
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


def line(x, n,m):
    y = m*x+n
    return y

def exp(x, A, lmbda,x0):
    y = A*2.71**(-lmbda*(x-x0))
    return y
    
def compute_fit_param(voltage_trace_name, sim_results, plt_show=False,NV_REG_FACTOR=2):
    """
    This function computes the performance-based characterization parameters
    for a given voltage trace.


    Parameters
    ----------
    voltage_trace_name : string
        voltage trace filename to characterize
    sim_results : dictionary
        dictionary collecting the simulation results parameters
    plt_show : TYPE, optional
        DESCRIPTION. The default is False.
    NV_REG_FACTOR: integer
        non-volatile register factor
    Returns
    -------
    lmbda           : float
        Fit decay factor
    max_throughput  : float
        Maximum throughput DNN
    prson_pwr_cmpt  : float
        Correlation and p-value for Person correlation coefficent
    """
    
    titlesize = 18
    xy_labelsize = 16
    xy_tickssize = 14
    #Loading voltage trace values
    #Loading voltage trace
    vt_path = "../../src/NORM/voltage_traces/"+voltage_trace_name+".txt"
    sngl_plots_path = SINGLE_performance_index_outputpath+"NV_REG_FACTOR_"+str(NV_REG_FACTOR)+"/"

    vt_file = open(vt_path,"r")
    allLines = vt_file.readlines()
    vt_file.close()
    vt_voltages_original = [int(line) for line in allLines]
    vt_voltages = vt_voltages_original
    
    #Computing decay factor for throughput
    throughput = sim_results[voltage_trace_name]["throughput"]
    pwr_cmpt = sim_results[voltage_trace_name]["total_power_consumption"]
    efficiency = sim_results[voltage_trace_name]["throughput_pwr_csmpt"]
    hzrd_th = sim_results[voltage_trace_name]["hazard_threshold_val"]
    
    float_type = np.dtype(float)
    pwr_cmpt = np.asarray(pwr_cmpt, dtype=float_type)
    hzrd_th = np.asarray(hzrd_th, dtype=float_type)
    throughput = np.asarray(throughput, dtype=float_type)
    
    wrng_values = hzrd_th
    #Computing number of oscillations around hazard threshold
    oscs = []
    for wrng_value in wrng_values:
        osc = 0
        for i in range(len(vt_voltages)-1):
            if vt_voltages[i] > wrng_value and vt_voltages[i+1] < wrng_value:
                osc += 1
        oscs.append(osc)
    
    #Plot power consumption versus hazard threshold
    if plt_show == True:
        fig = plt.figure(figsize=(10,6))
        ax1 = fig.gca()
        ax1.set_title("Total Power Consumption - Voltage Trace" + (re.search(r"\d+",voltage_trace_name).group()), fontsize=titlesize)
        #ax1.set_title("Voltage Trace"+(re.search(r"\d",voltage_trace_name).group()))
        ax1.plot(hzrd_th, pwr_cmpt, color = "blue")
        ax1.set_ylabel('Total Power Consumption[mW]', color='blue', fontsize=xy_labelsize)
        ax1.set_xlabel("Hazard Threshold [mV]", fontsize=xy_labelsize)
        ax1.tick_params(axis='x', labelsize=xy_tickssize)
        ax1.tick_params(axis='y', labelsize=xy_tickssize)
        ax2 = ax1.twinx()
        ax2.tick_params(axis='y', labelsize=xy_tickssize)
        ax2.plot(hzrd_th, oscs, color = "red") #The power consumption follows the oscillations of the voltage traces around the hazard threshold
        ax2.set_ylabel('Number of oscillations', color='red', fontsize=xy_labelsize)
        ax2.grid(True)
        
                
        if enable_plot_save == True:
            fig.savefig(sngl_plots_path+"TOTAL_POWER_CONSUMPTION_"+voltage_trace_name+".svg", dpi=1080)
            fig.savefig(sngl_plots_path+"TOTAL_POWER_CONSUMPTION_"+voltage_trace_name, dpi=1080)

        plt.show()
                
    #Fitting Throughput
    p0 = [throughput[0],0.005,hzrd_th[0]]
    print(voltage_trace_name.upper())
    print()
    #The method "trf" uses a Moore-Penrose pseudoinverse to compute the covariance matrix. (source: scipy.optimize_curve_fit documentation)
    #If the Jacobian matrix at the solution doesn’t have a full rank,
    #then ‘lm’ method returns a matrix filled with np.inf, on the
    #other hand ‘trf’ and ‘dogbox’ methods use Moore-Penrose
    #pseudoinverse to compute the covariance matrix.
    parameters, covariance = curve_fit(exp, hzrd_th, throughput,p0=p0,maxfev=100000,method='trf')
    print("The FITTED PARAMETERS  are:\n")
    print("(throughtput initial value, decay factor and initial hazard threshold)")
    print(parameters[0],parameters[1],parameters[2])
    print()
    A, lmbda,x0 = parameters
    throughput_fit = [exp(v,A,lmbda,x0) for v in hzrd_th]
    max_throughput = max(throughput)
    print("The COVARIANCE MATRIX is:\n")
    print(covariance)
    print()
    
    if plt_show == True:
        fig = plt.figure(figsize=(10,6))
        ax = fig.gca()
        ax.grid(True)
        ax.tick_params(axis='x', labelsize=xy_tickssize)
        ax.tick_params(axis='y', labelsize=xy_tickssize)
        ax.set_title("Throughput - Voltage Trace"+(re.search(r"\d+",voltage_trace_name).group()), fontsize=titlesize)
        ax.set_xlabel("Hazard Threshold [mV]", fontsize=xy_labelsize)
        ax.set_ylabel("Throughput [Op/s]", fontsize=xy_labelsize)
        ax.plot(hzrd_th, throughput, label="Experimental Throughput")
        ax.plot(hzrd_th, throughput_fit, label="Throughput Fit")
        ax.legend()
        if enable_plot_save == True:
                fig.savefig(sngl_plots_path+"./THROUGHPUT_"+voltage_trace_name, dpi=1080, bbox_inches="tight")
        plt.show()
    
    if plt_show == True:
        fig = plt.figure(figsize=(10,6))
        ax1 = fig.gca()
        ax1.set_title(r"Efficiency - Voltage Trace" + (re.search(r"\d+",voltage_trace_name).group()),fontsize=titlesize)
        #ax1.set_title("Voltage Trace"+(re.search(r"\d",voltage_trace_name).group()))
        ax1.plot(hzrd_th, efficiency, color = "blue")
        ax1.tick_params(axis='x', labelsize=xy_tickssize)
        ax1.tick_params(axis='y', labelsize=xy_tickssize)
        ax1.set_ylabel(r'$\frac{Throughput}{Power Consumption} [\frac{Op/s}{mW}]$', color='blue',fontsize=int(xy_labelsize*1.7))
        ax1.set_xlabel("Hazard Threshold [mV]",fontsize=xy_labelsize)
        plt.grid(True)
        if enable_plot_save == True:
                fig.savefig(sngl_plots_path+"./EFFICIENCY_"+voltage_trace_name+"_NVREG_FACTOR", dpi=1080, bbox_inches="tight")
        plt.show()
   
    
    #Correlating Power consumption with the number of oscillations around
    #hazard threshold Pearson correlation coefficient
    pwr_cmpt_corr, pwr_cmpt_pvalue = pearsonr(oscs, pwr_cmpt)
    
    prson_pwr_cmpt = pwr_cmpt_corr, pwr_cmpt_pvalue
    print("CORRELATION POWER CONSUMPTION - VOLTAGE TRACE OSCILLATIONS")
    print("Pearson correlation coefficient:", pwr_cmpt_corr)
    print("p-value:", pwr_cmpt_pvalue)
    print("__________________________________________")
    print()
    return(lmbda, max_throughput, prson_pwr_cmpt)


if __name__ == "__main__":
    
    """NVREG_FACTOR = 2"""
    NV_REG_FACTOR = 2
    
    voltage_trace_names = ["voltage_trace"+str(i) for i in range (1,11)]
    results_filename = "DB_results_fixedtime_NVREG_DELAY_FACTOR"+str(NV_REG_FACTOR)+".txt"
    DB_results_4layerDNN_paths = ["./results/DB_results/4layer_80/"+voltage_trace_name+"/"+results_filename for voltage_trace_name in voltage_trace_names]
    
    DB_results_files = [open(path,"r") for path in DB_results_4layerDNN_paths]
    DB_results_allLines = [file.readlines() for file in DB_results_files]
    sim_results = {}
    for vt_no in range(len(voltage_trace_names)):
        key = voltage_trace_names[vt_no]
        allLines = DB_results_allLines[vt_no]
        sim_results[key] = data_from_lines(allLines)
        
    [file.close() for file in DB_results_files]
    
    [overall_data(sim_results[sim_result],NV_REG_FACTOR=2) for sim_result in sim_results]
    
    #Computing fit parameters
    print("#################START NVR_FACTOR"+str(NV_REG_FACTOR)+"##########################")
    time.sleep(1)
    sngl_plots_path = SINGLE_performance_index_outputpath+"NV_REG_FACTOR_"+str(NV_REG_FACTOR)+"/"
    try:
        os.mkdir(sngl_plots_path)
    except:
        pass
    vt_ps = [compute_fit_param(voltage_trace_name, sim_results,plt_show=enable_sngl_plot_show,NV_REG_FACTOR=NV_REG_FACTOR) for voltage_trace_name in voltage_trace_names]
    
    trace_names = ["trace"+re.search(r"\d+",voltage_trace_name).group() for voltage_trace_name in voltage_trace_names]
    decays_2 = [p[0] for p in vt_ps]
    As_2 = [p[1] for p in vt_ps]
    prson_pwr_cmpt_2 =[p[2][0] for p in vt_ps]
    
    print("#################END NVR_FACTOR"+str(NV_REG_FACTOR)+"##########################")
    print("Press Enter to continue..")
    input()
    
    figsize = (14,4)
    fontsize = 16
    if enable_sngl_plot_show == False:
        bar_width = 0.75
        plt.figure(1, figsize=figsize)
        plt.xticks([i for i in range(len(trace_names))], trace_names, fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.bar([i for i in range(len(trace_names))], decays_2, label="NVM LATENCY FACTOR=2",width=bar_width)
        plt.title("Decay Factor of THROUGHPUT", fontsize=fontsize)
        plt.xlabel("Trace", fontsize=fontsize)
        plt.ylabel("Decay factor $\lambda$", fontsize=fontsize)
        #if enable_plot_save==True:
        #     fig.savefig("./DECAY_FACTOR", dpi=1080)
         #plt.xticks(fontsize=10)
    
    
        plt.figure(2, figsize=figsize)
        plt.xticks([i for i in range(len(trace_names))], trace_names, fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.bar([i for i in range(len(trace_names))], As_2, label="NVM LATENCY FACTOR=2",width=bar_width)
        plt.title("Amplitude A of Throughput Curve", fontsize=fontsize)
        plt.xlabel("Harvesting Scenario", fontsize=fontsize)
        plt.ylabel("Throughput [Op/s]", fontsize=fontsize)
        #plt.xticks(fontsize=10)
        # if enable_plot_save==True:
        #     fig_tp.savefig("./MAX_THROUGHPUT", dpi=1080)
    
    
        plt.figure(3, figsize=figsize)
        plt.xticks([i for i in range(len(trace_names))], trace_names, fontsize=fontsize)
        plt.yticks(fontsize=fontsize)
        plt.bar([i for i in range(len(trace_names))], prson_pwr_cmpt_2, label="NVM LATENCY FACTOR=2",width=bar_width)
        plt.title("Correlation Voltage Trace Oscillations and Power Consumption", fontsize=fontsize)
        #plt.xticks(fontsize=10)
        plt.xlabel("Harvesting Scenario", fontsize=fontsize)
        plt.ylabel("Correlation coefficient", fontsize=fontsize)
        if enable_plot_save==True:
            plt.savefig("./singleNVR_CORRELATION", dpi=1080)    
            plt.savefig("./singleNVR_CORRELATION.svg", dpi=1080)
    if enable_sngl_plot_show == False:
        fig = plt.figure(1)
        
        fig = plt.figure(2)
        
        fig = plt.figure(3)
        
    plt.show()
    
    
    
    
    
    
        
    
    
    
    
