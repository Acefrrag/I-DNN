# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 09:08:19 2023

Engineer: Michele Pio Fragasso


Description:
    --This script compares the results for all different voltage traces for
    --a given DELAY_FACTOR
"""

import re
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
import numpy as np

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
    
    num_hidden_layers = 4
    sizes = [30, 25, 15, 10]
    PWR_STATE_LAYER_IDLE = 1/1_000_000
    PWR_STATE_LAYER_COMP_DEF = 100/1_000_000
    BASE_NEURONS = 30 #Number of neurons for which the layer uses PWR_COMP_DEF during computation
    PWR_STATE_LAYER_COMP =  [neurons*PWR_STATE_LAYER_COMP_DEF/BASE_NEURONS for neurons in sizes]
    PWR_STATE_LAYER_SAVE = 20/1_000_000
    PWR_STATE_LAYER_REC = 20/1_000_000
    #INSTANTANEUOS POWER CONSUMPTION NVREG
    PWR_NVREG_POWERON = 1/1_000000
    BASE_DELAY_FACTOR = 2
    PWR_NVREG_RECOVERY_DEF = 10000/1_000_000
    PWR_NVREG_SAVE_DEF = 10000/1_000_000
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

# def exp(x, A, lmbda,x0,c,d):
#     y = A*2.71**(-lmbda*(x-x0)+c)+d
#     return y

def exp(x, A, lmbda,x0):
    y = A*2.71**(-lmbda*(x-x0))
    return y
    
def compute_fit_param(voltage_trace_name, sim_results, plt_show=False):
    
    
    #Loading voltage trace values
    #Loading voltage trace
    vt_path = "../../src/NORM/voltage_traces/"+voltage_trace_name+".txt"
    vt_file = open(vt_path,"r")
    allLines = vt_file.readlines()
    vt_file.close()
    vt_voltages_original = [int(line) for line in allLines]
    #vt_voltages = vt_voltages_original
    vt_voltages = vt_voltages_original
    
    #Computing decay factor for throughput
    
    if voltage_trace_name == "voltage_trace3":
        print("ciao")
    throughput = sim_results[voltage_trace_name]["throughput"]
    pwr_cmpt = sim_results[voltage_trace_name]["total_power_consumption"]
    efficiency = sim_results[voltage_trace_name]["throughput_pwr_csmpt"]
    hzrd_th = sim_results[voltage_trace_name]["hazard_threshold_val"]
    
    float_type = np.dtype(float)
    
    pwr_cmpt = np.asarray(pwr_cmpt, dtype=float_type)
    hzrd_th = np.asarray(hzrd_th, dtype=float_type)
    throughput = np.asarray(throughput, dtype=float_type)
    
    wrng_values = hzrd_th
    #Number of oscillations around hazard threshold
    oscs = []
    for wrng_value in wrng_values:
        osc = 0
        for i in range(len(vt_voltages)-1):
            if vt_voltages[i] > wrng_value and vt_voltages[i+1] < wrng_value:
                osc += 1
        oscs.append(osc)
    
    #Plot power consumption versus hazard threshold
    if plt_show == True:
        fig = plt.figure()
        ax1 = fig.gca()
        ax1.set_title("Total Power Consumption - Voltage Trace" + (re.search(r"\d+",voltage_trace_name).group()))
        #ax1.set_title("Voltage Trace"+(re.search(r"\d",voltage_trace_name).group()))
        ax1.plot(hzrd_th, pwr_cmpt, color = "blue")
        ax1.set_ylabel('Total Power Consumption[mW]', color='blue')
        ax1.set_xlabel("Hazard Threshold [mV]")
        ax2 = ax1.twinx()
        ax2.plot(hzrd_th, oscs, color = "red") #The power consumption follows the oscillations of the voltage traces around the hazard threshold
        ax2.set_ylabel('Number of oscillations', color='red')
        ax2.grid(True)
        
        if enable_plot_save == True:
            if voltage_trace_name == "voltage_trace1":
                fig.savefig("./TOTAL_POWER_CONSUMPTION", dpi=1080)
        plt.show()
        
    # if voltage_trace_name=="voltage_trace6":
    #     fig = plt.figure()
    #     ax = fig.gca()
    #     ax.grid(True)
    #     ax.set_title("Voltage Trace"+(re.search(r"\d",voltage_trace_name).group()))
    #     ax.plot(hzrd_th, throughput)
    #     plt.show()
        
    #Fitting Throughput
    p0 = [throughput[0],0.005,hzrd_th[0]]
    print(voltage_trace_name)
    parameters, covariance = curve_fit(exp, hzrd_th, throughput,p0=p0,maxfev=100000)
    print(covariance)
    A, lmbda,x0 = parameters
    throughput_fit = [exp(v,A,lmbda,x0) for v in hzrd_th]
    max_throughput = max(throughput)
    
    
    #plt_show=False
    if plt_show == True:
        fig = plt.figure()
        ax = fig.gca()
        ax.grid(True)
        ax.set_title("Throughput - Voltage Trace"+(re.search(r"\d+",voltage_trace_name).group()))
        ax.set_xlabel("Hazard Threshold [mV]")
        ax.set_ylabel("Throughput [Op/s]")
        ax.plot(hzrd_th, throughput, label="Experimental Throughput")
        ax.plot(hzrd_th, throughput_fit, label="Throughout Fit")
        ax.legend()
        if enable_plot_save == True:
            if voltage_trace_name == "voltage_trace3":
                fig.savefig("./THROUGHPUT", dpi=1080, bbox_inches="tight")
        plt.show()
    
    #plt_show=False
    if plt_show == True:
        fig = plt.figure()
        ax1 = fig.gca()
        ax1.set_title(r"Efficiency - Voltage Trace" + (re.search(r"\d+",voltage_trace_name).group()))
        #ax1.set_title("Voltage Trace"+(re.search(r"\d",voltage_trace_name).group()))
        ax1.plot(hzrd_th, efficiency, color = "blue")
        ax1.set_ylabel(r'$\frac{Throughput}{Power Consumption} [\frac{Op/s}{mW}$', color='blue')
        ax1.set_xlabel("Hazard Threshold [mV]")
        plt.grid(True)
        if enable_plot_save == True:
            if voltage_trace_name == "voltage_trace1":
                fig.savefig("./EFFICIENCY_vt1_NVREG_FACTOR", dpi=2080, bbox_inches="tight")
        plt.show()
   
    
    #Correlating Power consumption with the number of oscillations around hazard threshold
    #Pearson correlation coefficient
    pwr_cmpt_corr, pwr_cmpt_pvalue = pearsonr(oscs, pwr_cmpt)
    
    prson_pwr_cmpt = pwr_cmpt_corr, pwr_cmpt_pvalue
    print("Pearson correlation coefficient:", pwr_cmpt_corr)
    print("p-value:", pwr_cmpt_pvalue)
    
    return(lmbda, max_throughput, prson_pwr_cmpt)


if __name__ == "__main__":
    #ANALYSIS OF DIFFERENT VOLTAGE TRACES RESULTS FOR A GIVEN NV_REG_FACTOR
    NV_REG_FACTOR = 2
    num_hidden_layers = 4
    enable_plot_save = True
    voltage_trace_names = ["voltage_trace"+str(i) for i in range (1,11)]
    #voltage_trace_names = ["voltage_trace1","voltage_trace2","voltage_trace3", "voltage_trace4","voltage_trace5", "voltage_trace6","voltage_trace8", "voltage_trace9", "voltage_trace10"]
    indexes = [2,8]
    #voltage_trace_names = ["voltage_trace"+str(i) for i in range(1,11)]
    results_filename = "DB_results_fixedtime_NVREG_DELAY_FACTOR"+str(NV_REG_FACTOR)+".txt"
    DB_results_4layerDNN_paths = ["./results/4layer_80/"+voltage_trace_name+"/"+results_filename for voltage_trace_name in voltage_trace_names]
    
    DB_results_files = [open(path,"r") for path in DB_results_4layerDNN_paths]
    DB_results_allLines = [file.readlines() for file in DB_results_files]
    sim_results = {}
    for vt_no in range(len(voltage_trace_names)):
        key = voltage_trace_names[vt_no]
        allLines = DB_results_allLines[vt_no]
        sim_results[key] = data_from_lines(allLines)
        
    [file.close() for file in DB_results_files]
    
    [overall_data(sim_results[sim_result],NV_REG_FACTOR=2) for sim_result in sim_results]
    
    vt_ps = [compute_fit_param(voltage_trace_name, sim_results,plt_show=False) for voltage_trace_name in voltage_trace_names]
    # vt1_p = compute_fit_param("voltage_trace1", sim_results, plt_show=True)
    # vt2_p = compute_fit_param("voltage_trace2", sim_results, plt_show=True)
    # vt8_p = compute_fit_param("voltage_trace8", sim_results, plt_show=True)
    
    trace_names = ["trace"+re.search(r"\d+",voltage_trace_name).group() for voltage_trace_name in voltage_trace_names]
    #vt_ps = [vt1_p, vt2_p, vt8_p]
    decays = [p[0] for p in vt_ps]
    As = [p[1] for p in vt_ps]
    prson_pwr_cmpt =[p[2][0] for p in vt_ps]
    #•cs = [p[4] for p in vt_ps
    
    
    
    bar_width = 0.25
    plt.figure(1)
    plt.bar(trace_names, decays, label="NV_REG_FACTOR=2",width=bar_width)
    plt.title("Decay Factor of THROUGHPUT")
    plt.xlabel("Trace")
    plt.ylabel("Decay factor $\lambda$")
    # if enable_plot_save==True:
    #     fig.savefig("./DECAY_FACTOR", dpi=1080)
    # #plt.xticks(fontsize=10)
    
    
    plt.figure(2)
    plt.bar(trace_names, As, label="NVREG_FACTOR2",width=bar_width)
    plt.title("Throughput Amplitude A")
    plt.xlabel("Trace")
    plt.ylabel("Maximum THROUGHPUT [Op/s]")
    #plt.xticks(fontsize=10)
    # if enable_plot_save==True:
    #     fig_tp.savefig("./MAX_THROUGHPUT", dpi=1080)
    
    
    plt.figure(3)
    plt.bar(trace_names, prson_pwr_cmpt, label="NV_REG_FACTOR=2",width=bar_width)
    plt.title("Correlation Voltage Trace Oscillations and Power Consumption")
    #plt.xticks(fontsize=10)
    plt.xlabel("Trace")
    plt.ylabel("Correlation coefficient")
    # if enable_plot_save==True:
    #     fig_corr.savefig("./CORRELATION", dpi=1080)
        
    NV_REG_FACTOR = 5
    num_hidden_layers = 4
    enable_plot_save = False
    voltage_trace_names = ["voltage_trace"+str(i) for i in range (1,11)]
    #voltage_trace_names = ["voltage_trace1","voltage_trace2","voltage_trace3", "voltage_trace4","voltage_trace5", "voltage_trace6","voltage_trace8", "voltage_trace9", "voltage_trace10"]
    #voltage_trace_names = ["voltage_trace"+str(i) for i in range(1,11)]
    results_filename = "DB_results_fixedtime_NVREG_DELAY_FACTOR"+str(NV_REG_FACTOR)+".txt"
    DB_results_4layerDNN_paths = ["./results/4layer_80/"+voltage_trace_name+"/"+results_filename for voltage_trace_name in voltage_trace_names]
    
    DB_results_files = [open(path,"r") for path in DB_results_4layerDNN_paths]
    DB_results_allLines = [file.readlines() for file in DB_results_files]
    sim_results = {}
    for vt_no in range(len(voltage_trace_names)):
        key = voltage_trace_names[vt_no]
        allLines = DB_results_allLines[vt_no]
        sim_results[key] = data_from_lines(allLines)
        
    [file.close() for file in DB_results_files]
    
    [overall_data(sim_results[sim_result],NV_REG_FACTOR=NV_REG_FACTOR) for sim_result in sim_results]
    
    vt_ps = [compute_fit_param(voltage_trace_name, sim_results, plt_show=False) for voltage_trace_name in voltage_trace_names]
    # vt1_p = compute_fit_param("voltage_trace1", sim_results, plt_show=True)
    # vt2_p = compute_fit_param("voltage_trace2", sim_results, plt_show=True)
    # vt8_p = compute_fit_param("voltage_trace8", sim_results, plt_show=True)
    
    trace_names = ["trace"+re.search(r"\d+",voltage_trace_name).group() for voltage_trace_name in voltage_trace_names]
    #vt_ps = [vt1_p, vt2_p, vt8_p]
    decays = [p[0] for p in vt_ps]
    As = [p[1] for p in vt_ps]
    prson_pwr_cmpt =[p[2][0] for p in vt_ps]
    #•cs = [p[4] for p in vt_ps]
    
    plt.figure(1)
    plt.bar([i + bar_width for i in range(len(trace_names))], decays, label="NV_REG_FACTOR=5",width=bar_width)
    # if enable_plot_save==True:
    #     fig_decay.savefig("./DECAY_FACTOR", dpi=1080)
    # #plt.xticks(fontsize=10)
    plt.legend()

    
    plt.figure(2)
    plt.bar([i + bar_width for i in range(len(trace_names))], As, label="NV_REG_FACTOR=5",width=bar_width)
    #plt.xticks(fontsize=10)
    # if enable_plot_save==True:
    #     fig_tp.savefig("./MAX_THROUGHPUT", dpi=1080)
    plt.legend()

    
    
    plt.figure(3)
    plt.bar([i + bar_width for i in range(len(trace_names))], prson_pwr_cmpt, label="NV_REG_FACTOR=5",width=bar_width)
    
    # if enable_plot_save==True:
    #     fig_corr.savefig("./CORRELATION", dpi=1080)

   
    
    
    NV_REG_FACTOR = 11
    num_hidden_layers = 4
    enable_plot_save = False
    voltage_trace_names = ["voltage_trace"+str(i) for i in range (1,11)]
    #voltage_trace_names = ["voltage_trace1","voltage_trace2","voltage_trace3", "voltage_trace4","voltage_trace5", "voltage_trace6","voltage_trace8", "voltage_trace9", "voltage_trace10"]
    #voltage_trace_names = ["voltage_trace"+str(i) for i in range(1,11)]
    results_filename = "DB_results_fixedtime_NVREG_DELAY_FACTOR"+str(NV_REG_FACTOR)+".txt"
    DB_results_4layerDNN_paths = ["./results/4layer_80/"+voltage_trace_name+"/"+results_filename for voltage_trace_name in voltage_trace_names]
    
    DB_results_files = [open(path,"r") for path in DB_results_4layerDNN_paths]
    DB_results_allLines = [file.readlines() for file in DB_results_files]
    sim_results = {}
    for vt_no in range(len(voltage_trace_names)):
        key = voltage_trace_names[vt_no]
        allLines = DB_results_allLines[vt_no]
        sim_results[key] = data_from_lines(allLines)
        
    [file.close() for file in DB_results_files]
    
    [overall_data(sim_results[sim_result],NV_REG_FACTOR=NV_REG_FACTOR) for sim_result in sim_results]
    
    vt_ps = [compute_fit_param(voltage_trace_name, sim_results, plt_show=False) for voltage_trace_name in voltage_trace_names]
    # vt1_p = compute_fit_param("voltage_trace1", sim_results, plt_show=True)
    # vt2_p = compute_fit_param("voltage_trace2", sim_results, plt_show=True)
    # vt8_p = compute_fit_param("voltage_trace8", sim_results, plt_show=True)
    
    trace_names = ["trace"+re.search(r"\d+",voltage_trace_name).group() for voltage_trace_name in voltage_trace_names]
    #vt_ps = [vt1_p, vt2_p, vt8_p]
    decays = [p[0] for p in vt_ps]
    As = [p[1] for p in vt_ps]
    prson_pwr_cmpt =[p[2][0] for p in vt_ps]
    #•cs = [p[4] for p in vt_ps]
    
    plt.figure(1)
    plt.bar([i + 2*bar_width for i in range(len(trace_names))], decays, label="NV_REG_FACTOR=11",width=bar_width)
    # if enable_plot_save==True:
    #     fig_decay.savefig("./DECAY_FACTOR", dpi=1080)
    # #plt.xticks(fontsize=10)
    plt.legend()
    plt.grid(True)
    plt.savefig("./DECAY_FACTOR", dpi=1080)
    
    plt.figure(2)
    plt.bar([i + 2*bar_width for i in range(len(trace_names))], As, label="NV_REG_FACTOR=11",width=bar_width)
    #plt.xticks(fontsize=10)
    # if enable_plot_save==True:
    #     fig_tp.savefig("./MAX_THROUGHPUT", dpi=1080)
    plt.legend()
    plt.grid(True)
    plt.savefig("./MAX_THROUGHPUT", dpi=1080)
    
    
    plt.figure(3)
    plt.bar([i + 2*bar_width for i in range(len(trace_names))], prson_pwr_cmpt, label="NV_REG_FACTOR=11",width=bar_width)
    plt.grid(True)
    plt.legend()
    plt.savefig("./CORRELATION", dpi=1080)
    
    # if enable_plot_save==True:
    #     fig_corr.savefig("./CORRELATION", dpi=1080)

    
    # fig = plt.figure()
    # ax = fig.gca()
    # ax.bar(voltage_trace_names, cs)
    # ax.set_title("c factor per Voltage Trace - 4-layer DNN")
    # plt.show()
    
    
    if enable_plot_save == True:
        fig = plt.figure(1)
        
        fig = plt.figure(2)
        
        fig = plt.figure(3)
        
    plt.show()
    
    
    
    
    
    
        
    
    
    
    
