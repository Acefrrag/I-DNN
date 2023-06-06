# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 16:03:25 2023

Engineer: Michele Pio Fragasso


Description:
    This script perform tests to analyze the throughput for DNN with different
    dimensions
    
    The key findings of this analysis are:
        1) DNN no of MACs affect throguhput (only amplitude of throuput)
        2) The trhoutput decay factor is still higly dependent on the voltage trace, which is barely affect by the DNN dimension.
        3) The correlation was also not affected. So it makes sense to use the correlation as a characterization of voltage profiles, given that we don't modify the latency of the NV_REG'
    
    You can find the plots @ "./plots/DNN_analysis_plots"
    
    This script is intended to be used for a given set of DNN architectures.
"""

import re
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
import numpy as np
import os

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


def compute_noMAC_layer(input_size, output_size):
    no_MACs = input_size*output_size
    return(no_MACs)

def compute_noMACs_DNN(DNN_architecture_filename):
    """
    This functin produces the number of MACs for a given DNN. It measures how
    many arithmetic operations are carried out by the DNN. The more MACs, the
    more operations a DNN needs to perform for an inference, the less the
    throughput.

    Parameters
    ----------
    DNN_architecture_filename : complete path to the DNN architecture descriptor.
        DESCRIPTION.

    Returns
    -------
    None.

    """
    
    f = open(DNN_architecture_filename, "r")
    allLines = f.readlines()
    f.close()
    #The parathesis are eliminated and contents split and inserted in an array
    sizes_str = allLines[0][1:-1].split(";")
    sizes = [int(x) for x in sizes_str]
    
    #Computing MAC operation given the sizes
    
    no_MACs=0
    for i in range(len(sizes)-1):
        input_size = sizes[i]
        output_size = sizes[i+1]
        no_MACs+=compute_noMAC_layer(input_size, output_size)
    return(no_MACs)

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

    #Computing throughput and throughput per power consumption
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
    
def compute_fit_param(voltage_trace_name, test, sim_results, plt_show=False):
    
    
    #Loading voltage trace values
    #Loading voltage trace
    vt_path = "../../src/NORM/voltage_traces/"+voltage_trace_name+".txt"
    vt_file = open(vt_path,"r")
    allLines = vt_file.readlines()
    vt_file.close()
    vt_voltages_original = [int(line) for line in allLines]
    #vt_voltages = vt_voltages_original
    vt_voltages = vt_voltages_original
    
    
    print("\n\n\nDNN Architecture: " + test+"\n")
    #Computing decay factor for throughput
    
    throughput = sim_results[test]["throughput"]
    pwr_cmpt = sim_results[test]["total_power_consumption"]
    hzrd_th = sim_results[test]["hazard_threshold_val"]
    
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
        ax1.set_title("Total Power Consumption - DNN " + test)
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
        
        
    #Fitting Throughput
    p0 = [throughput[0],0.001,hzrd_th[0]]
    parameters, covariance = curve_fit(exp, hzrd_th, throughput,p0=p0,maxfev=100000, method='trf')
    A, lmbda,x0 = parameters
    throughput_fit = [exp(v,A,lmbda,x0) for v in hzrd_th]
    print("Covariance Matrix:")
    print(covariance)
    print("")
    print("Fit Parameters (Maximum thorughput, Decay Factor and initial threshold):")
    print(A, lmbda, x0)
    
    if plt_show == True:
        fig = plt.figure()
        ax = fig.gca()
        ax.grid(True)
        ax.set_title("Throughput - DNN " + test)
        ax.set_xlabel("Hazard Threshold [mV]")
        ax.set_ylabel("Throughput [Op/s]")
        ax.plot(hzrd_th, throughput)
        ax.plot(hzrd_th, throughput_fit)
        if enable_plot_save == True:
            if voltage_trace_name == "voltage_trace3":
                fig.savefig("./THROUGHPUT", dpi=1080)
        plt.show()
    
    
    #Correlating Power consumption with the number of oscillations around hazard threshold
    #Pearson correlation coefficient
    pwr_cmpt_corr, pwr_cmpt_pvalue = pearsonr(oscs, pwr_cmpt)
    
    prson_pwr_cmpt = pwr_cmpt_corr, pwr_cmpt_pvalue
    print("Pearson correlation coefficient:", pwr_cmpt_corr)
    print("p-value:", pwr_cmpt_pvalue)
    
    return(lmbda, throughput[0], prson_pwr_cmpt)


if __name__ == "__main__":
    #ANALYSIS OF DIFFERENT DNNs
    output_path = "./plots/DB_analysis_DNN_plots/"
    try:
        os.mkdir(output_path)
    except:
        pass
    
    #tests=["4layer_80", "8layer_240", "12layer_395", "8layer_470"]
    tests=["4_layer_140", "6_layer_150", "8_layer_240", "8_layer_290", "10_layer_355", "12_layer_395", "12_layer_435", "8_layer_470"]
    #These files include the dimensions of every neuron inside 
    DNN_architecture_filenames = ["./DNN_architectures/architecture_"+tests[i]+".txt" for i in range(len(tests))]
    nos_MACs=[compute_noMACs_DNN(DNN_architecture_filename) for DNN_architecture_filename in DNN_architecture_filenames]
    #labels=["4-layer DNN", "8-layer DNN","12-layer DNN","8-layer DNN"]#Contains the labels to put on bar charts
    labels=["4-layer DNN", "6-layer DNN", "8-layer DNN", "8-layer DNN", "10-layer DNN", "12-layer DNN", "12-layer DNN", "8-layer DNN"]
    x_labels=[str(nos_MACs[i]) for i in range(len(nos_MACs))]
    #colors=["red", "blue", "green", "yellow"]
    colors = ["red", "blue", "green", "yellow", "purple", "magenta", "orange", "grey"]
    pattern=["+","*","|","O"]
    voltage_tracename = "voltage_trace2"
    print("DNN analysis. Voltage trace: "+voltage_tracename)
    NV_REG_FACTOR = 2
    #tests=["4layer_80_powerpoint", "8layer_240", "12layer_395", "8layer_470"]
    tests=[tests[i]+"_thesisdefence" for i in range(len(tests))]
    results_filename = "DB_results_fixedtime_NVREG_DELAY_FACTOR"+str(NV_REG_FACTOR)+".txt"
    DB_resultspaths = ["./results/DB_results/"+tests[i]+"/"+voltage_tracename+"/"+results_filename for i in range(len(tests))]    
    DB_results_files = [open(path,"r") for path in DB_resultspaths]
    DB_results_allLines = [file.readlines() for file in DB_results_files]
    sim_results = {}
    for DNN_no in range(len(tests)):
        key = tests[DNN_no]
        allLines = DB_results_allLines[DNN_no]
        sim_results[key] = data_from_lines(allLines)
        
    [file.close() for file in DB_results_files]
    
    [overall_data(sim_results[sim_result], NV_REG_FACTOR=NV_REG_FACTOR) for sim_result in sim_results]
    
    DNNtest_ps = [compute_fit_param(voltage_trace_name=voltage_tracename,test=test, sim_results=sim_results, plt_show=False) for test in tests]
    
    test_names = tests
    decays = [p[0] for p in DNNtest_ps]
    As = [p[1] for p in DNNtest_ps]
    prson_pwr_cmpt =[p[2][0] for p in DNNtest_ps]
    
    decay_var = np.var(decays)
    decay_mean = np.mean(decays)
    decay_rel_var_perc = decay_var/decay_mean*100
    
    
    #PLOTTING DECAY FACTOR THROUGHPUT
    #figsize = None#(10,4)
    figsize = (14,4)
    titlesize = 18
    fontsize = 16
    legendfontsize = 11.5
    bar_width = 0.35
    #Rectangle for 4 DNNs simulations
    rect = Rectangle(xy=(-bar_width/2,1.19*max(decays)), width=2.85, height=0.00035, edgecolor='black', facecolor='none')
    #Rectangle for 8 DNNs simulations
    #rect = Rectangle(xy=(-bar_width/2,1.19*max(prson_pwr_cmpt)), width=2.85, height=0.3, edgecolor='black', facecolor='none')
    fig = plt.figure(1, figsize=figsize)
    ax = fig.gca()
    #The set_xticks method is used for a 4 DNNs test
    #ax.set_xticks([i for i in range(len(x_labels))], x_labels, fontsize=fontsize)
    #This one below is used for a set of 8 DNNs
    ax.set_xticks([i for i in range(len(x_labels))], x_labels, fontsize=fontsize/1.2)
    for i in range(len(labels)):
        ax.bar(i, decays[i], label=labels[i], color = colors[i],width=bar_width)
    #Legend for 4 DNNs test
    #ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.40), ncol=3, fontsize=legendfontsize)
    #Legend for 8 DNN test
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.50), ncol=3, fontsize=legendfontsize)
    ax.set_title("Decay Factor of THROUGHPUT",pad=15, fontsize=fontsize)
    ax.set_xlabel("DNN no. of MACs", fontsize=fontsize)
    ax.set_ylabel("Decay factor $\lambda$", fontsize=fontsize)
    [ax.annotate(str(round(decays[i],4)), xy=(i-bar_width/2,1.03*decays[i]),weight="bold") for i in range(len(x_labels))]
    ax.annotate(r"Decay Mean Value $\bar{\sigma}$="+str(round(decay_mean,5)),xy = (-bar_width/2,1.2*max(decays)),weight="bold")
    ax.annotate(r"Decay Variance: $\sigma_{\lambda}$="+str(round(decay_var,10)),xy = (-bar_width/2,1.30*max(decays)),weight="bold")
    ax.annotate(r"Decay Relative Variance: $\sigma_{\lambda} \%$="+str(round(decay_rel_var_perc,5))+"%",xy = (-bar_width/2,1.40*max(decays)),weight="bold")
    ax.add_patch(rect)
    ax.margins(y=55*max(decays))
    ax.grid(True)
    plt.savefig(output_path+"DNNs_DECAY_FACTOR", dpi=1080, bbox_inches="tight")
    
    xy_tickssize=14
    #PLOTTING INITIAL THROUGHPUT
    fig = plt.figure(2, figsize = figsize)
    ax = fig.gca()
    #ax.set_xticks([i for i in range(len(x_labels))], x_labels, fontsize=fontsize)
    # for i in range(len(labels)):
    #     #ax.bar(i, As[i], label=labels[i],width=bar_width,color=colors[i])
    #     ax.plot(nos_MAC[i], As[i])
    ax.scatter(nos_MACs, As)
    ax.plot(nos_MACs, As, linestyle="--")
    #ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.40), ncol=3, fontsize=legendfontsize)
    ax.set_title("Amplitude A of Throghput curve",pad=15, fontsize=titlesize)
    ax.set_xlabel("DNN no. of MACs", fontsize=fontsize)
    ax.set_ylabel("Throughput [Op/s]", fontsize=fontsize)
    ax.tick_params(axis='x',labelsize=xy_tickssize)
    ax.tick_params(axis='y',labelsize=xy_tickssize)
    #Annotate for 4 DNNs tests
    #[ax.annotate(str(int(As[i]))+"\n"+ labels[i], xy = (nos_MACs[i]+1000,As[i]+1000), weight="bold") for i in range(len(x_labels)-1)]
    #Annotate for 8 DNNs tests
    [ax.annotate(str(int(As[i])), xy = (nos_MACs[i],As[i]), weight="bold") for i in range(len(x_labels)-1)]
    #Annotate for 4 DNNs tests
    #ax.annotate(str(int(As[-1]))+"\n"+ labels[-1], xy = (nos_MACs[-1]-20000,As[-1]+1000), weight="bold")
    #Annotate for 8 DNNs tests
    ax.annotate(str(int(As[-1])), xy = (nos_MACs[-1]-4000,As[-1]+250), weight="bold")
    ax.margins(y=0.18)
    ax.grid(True)
    plt.savefig(output_path+"DNNs_MAX_THROUGHPUT", dpi=1080, bbox_inches="tight")
    
    
    
    #PLOTTING CORRELATION POWER CONSUMPTION VT OSCILLATIONS
    corr_var = np.var(prson_pwr_cmpt)
    corr_mean = np.mean(prson_pwr_cmpt)
    corr_rel_perc_var = corr_var/corr_mean*100
    #Rectangle for 4 DNNs simulations
    #rect = Rectangle(xy=(-bar_width/2,1.19*max(prson_pwr_cmpt)), width=2.85, height=0.3, edgecolor='black', facecolor='none')
    #Rectangle for 8 DNNs simulations
    rect = Rectangle(xy=(-bar_width/2,1.19*max(prson_pwr_cmpt)), width=2.85, height=0.3, edgecolor='black', facecolor='none')
    fig = plt.figure(3, figsize = figsize)
    ax = fig.gca()
    ax.set_xticks([i for i in range(len(x_labels))], x_labels, fontsize=fontsize/1.2)
    for i in range(len(labels)):
        ax.bar(i, prson_pwr_cmpt[i], label=labels[i],width=bar_width,color=colors[i])
    ax.set_title("Correlation Voltage Trace Oscillations and Power Consumption", pad=15,fontsize=fontsize)
    #Legend for 4 DNNs test
    #ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.40), ncol=3, fontsize=legendfontsize)
    #Legend for 8 DNN test
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.50), ncol=3, fontsize=legendfontsize)
    [ax.annotate(str(int(prson_pwr_cmpt[i])), xy = (i-bar_width/2,prson_pwr_cmpt[i]+1000), weight="bold") for i in range(len(x_labels))]
    ax.margins(y=0.05)
    ax.annotate(r"Correlation Relative Variance: $\sigma_{\lambda} \%$="+str(round(corr_rel_perc_var,5))+"%",xy = (-bar_width/2,1.40*max(prson_pwr_cmpt)),weight="bold")
    ax.annotate(r"Correlation Variance: $\sigma_{\lambda}$="+str(round(corr_var,8)),xy = (-bar_width/2,1.30*max(prson_pwr_cmpt)),weight="bold")
    ax.annotate(r"Correlation Mean Value $\bar{\sigma}$="+str(round(corr_mean,5)),xy = (-bar_width/2,1.2*max(prson_pwr_cmpt)),weight="bold")
    ax.set_xlabel("DNN no. of MACs", fontsize=fontsize)
    ax.set_ylabel("Correlation coefficient", fontsize=fontsize)
    ax.grid(True)
    ax.add_patch(rect)
    
    #fig_corr.savefig("./CORRELATION", dpi=1080)
    plt.savefig(output_path+"DNNs_CORRELATION", dpi=1080, bbox_inches="tight")
    plt.show()
    