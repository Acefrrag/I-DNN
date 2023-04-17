# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 10:21:28 2023

Engineer: Michele Pio Fragasso


Description:
    This script produces the voltage traces to visually inspect them with
    respect to the hazard threshold and power off threshold.
    It also include other options which can enable manually by the users
    
    It is meant to be used before the voltage trace generation script.
    
Input:
    -vt_ts                      : voltage trace timescale in ns.
    -shtdwn_value               : shutdown value to display in mV.
    -hazard_threshold_display   : hazard threshold to display in mV
    -sim_time                   : simulation time in us.

Output:
    -Voltage trace plots: For every voltage trace, different plots are
    
OPTIONS:
    -vts_raw_samples_plt_show   : to plot the raw voltage traces
    -vts_window_plt_show        : to plot the window of the voltage trace
    -vts_jumpstart_plt_show     : to plot the voltage trace from the first
                                     "active" voltage (that is the voltage above
                                      power-off threshold)
"""

import sys
sys.path.insert(0, "../functions/")

import matplotlib.pyplot as plt
import numpy as np
import misc
import os

#INPUTS
vt_ts = 160 #voltage timescale in ns
#Plotting data
shtdw_value = 2300
hazard_threshold_display = 2600
sim_time = 3_000#Simulation time in us




#OPTIONS
vts_raw_samples_plt_show = False
vts_window_plt_show = True
#Voltage traces cut to the first above-poweroff threshold
vts_jumpstart_plt_show = False
enable_plots_save = False
#ANALYSIS OPTIONS
active_percentage_analysis = False
max_neurons_analysis = False


window_length = int(sim_time/(vt_ts/1000))

#Make plots directory
try:
    os.mkdir("./plots")
except:
    pass



#Loading all voltage traces and plotting them
traces_path = "../files/voltage_traces/"
filenames = [traces_path+str(i)+".txt" for i in range(1,11)]
lines = [np.loadtxt(filenames[i-1],ndmin=1,dtype=np.dtype(float)) for i in range(1,11)]
vt_full = [{"trace_ID": str(i),\
           "voltages": [line[1]*1000 for line in lines[i-1]],\
           "samples": [x[0] for x in list(enumerate(lines[i-1]))]} for i in range(1, 11)]
wlen = int(sim_time/(vt_ts/1_000))
traces = vt_full
#Plotting and saving all voltage traces
full_trace_fig_path = "./plots/full_voltage_trace/"
try:
     os.mkdir(full_trace_fig_path)
except:
    pass
if vts_raw_samples_plt_show == True:
    for trace in traces:
        plt.figure()
        plt.title("Data Trace "+trace["trace_ID"])
        plt.xlabel("Sample")
        plt.ylabel("Voltage[mV]")
        plt.plot(trace["samples"],trace["voltages"],color ="blue")
        plt.axhline(shtdw_value, color="red",label="Shutdown Threshold")
        plt.axhline(hazard_threshold_display, color="green",label="Hazard Threshold")
        plt.legend()
        plt.grid()
        if enable_plots_save == True:
            plt.savefig(fname=full_trace_fig_path+"trace_"+trace["trace_ID"],dpi=1060)
        plt.show()

#Windowing the voltage trace

#Maximum number of neurons analysis
for trace in traces:
    trace["neurons"] = {}
wrng_value_step = 30
wrng_values = [x for x in range(2500, 3000, wrng_value_step)]
if max_neurons_analysis == True:
    for trace in traces:
        for NV_REG_DELAY_FACTOR in range(2, 12):
            key = "NV_REG_DELAY_FACTOR_"+str(NV_REG_DELAY_FACTOR)
            trace["neurons"][key] = [misc.compute_max_neuron_number(trace,vt_ts=vt_ts,wrng_value=wrng_value, shtdw_value=shtdw_value,NV_REG_DELAY_FACTOR=NV_REG_DELAY_FACTOR) for wrng_value in wrng_values]
    #Plotting and saving results
    max_number_neurons_fig_path = "./plots/max_number_neurons/"
    try:
        os.mkdir(max_number_neurons_fig_path)
    except:
        pass
    for trace in traces:
        plt.figure()
        plt.title("Maximum number of neurons vs. hazard threshold. - Trace no. "+str(trace["trace_ID"]))
        plt.xlabel("Hazard threshold [mV]")
        plt.ylabel("Maximum number of admissible neurons")
        i = 2
        for key in trace["neurons"].keys():
            label = "DELAY_FACTOR = " + str(i)
            plt.plot(wrng_values, trace["neurons"][key],label=label)
            i += 1
        plt.grid()
        plt.legend(prop={'size': 6})
        if enable_plots_save == True:
            plt.savefig(fname=max_number_neurons_fig_path+"trace_"+trace["trace_ID"],dpi=1060)
        plt.show()


#Hazard Threshold Sample Percentage analysis
if active_percentage_analysis == True:
    for trace in traces:
            trace["wrng_perc"] = np.zeros(len(wrng_values))
            c = 0
            usefull_perc = 0
            shtdw_perc = 0
            for wrng_value in wrng_values:
                wrng_perc = 0
                for voltage in trace["voltages"]:
                    if voltage>wrng_value:
                        usefull_perc += 1
                    elif voltage <= shtdw_value:
                        shtdw_perc +=1
                    if voltage <= wrng_value and voltage > shtdw_value:
                        wrng_perc += 1
                perc = float(wrng_perc)/len(trace["voltages"])*100
                trace["wrng_perc"][c] = perc
                c += 1
    #Plotting results
    hzrd_prc_path = "./plots/hazard_perc/"
    try:
        os.mkdir(hzrd_prc_path)
    except:
        pass
    for trace in traces:
         plt.figure()
         plt.rcParams['text.usetex'] = True
         plt.title("Hazard samples percentage w.r.t. Threshold")
         plt.xlabel("Hazard Threshold [mV]")
         plt.ylabel("$\\frac{Hazard Samples}{Samples}[\\%]$")
         plt.plot(wrng_values, trace["wrng_perc"])
         plt.grid()
         if enable_plots_save == True:
             plt.savefig(fname=hzrd_prc_path+"trace_"+trace["trace_ID"],dpi=1060)
         plt.show()
    
    
#Traces neglecting the initial power off
vt_jmpstart_path = "./plots/vt_jmpstart/"
try:
    os.mkdir(vt_jmpstart_path)
except:
    pass
for trace in traces:
    y_trace = trace["voltages"]
    indexes = [index for index, value in list(enumerate(y_trace)) if y_trace[index] < shtdw_value]
    start_index = min([i-1 for i, index in list(enumerate(indexes)) if indexes[i]-indexes[i-1]>1])-5
    trace["cut_v"] = y_trace[start_index:-1]
    trace["cut_v_samples"] = [int(x[0]) for x in list(enumerate(trace["cut_v"]))]
if vts_jumpstart_plt_show == True:
    for trace in traces:
        plt.plot(trace["cut_v_samples"], trace["cut_v"], color="blue")
        plt.grid()
        plt.title("Voltage Trace jumpstarted plotted from the first value.")
        plt.xlabel("Sample")
        plt.ylabel("Voltage [mV]")
        plt.axhline(shtdw_value, color="red",label="Shutdown Threshold")
        plt.axhline(hazard_threshold_display, color="green",label="Hazard Threshold")
        plt.legend()
        if enable_plots_save == True:
            plt.savefig(fname=vt_jmpstart_path+"trace_"+trace["trace_ID"],dpi=1060)
        plt.show()
        

vt_w_path = "./plots/vt_window/"
try:
    os.mkdir(vt_w_path)
except:
    pass
#Traces extract the first windows_length samples to test the architecture with a subset of the trace
for trace in traces:
    trace["extract_v"]= trace["cut_v"][0:window_length]
    trace["extract_v_samples"]= [int(x[0]) for x in list(enumerate(trace["extract_v"]))]
    trace["time"] = [float(x*vt_ts/1000) for x in trace["extract_v_samples"]]
for trace in traces:
    plt.plot(trace["time"], trace["extract_v"], color="blue")
    plt.title("Voltage Trace no."+trace["trace_ID"]+" - Voltage versus Time")
    plt.xlabel("Time [us]")
    plt.ylabel("Voltage [mV]")
    plt.grid()
    plt.axhline(shtdw_value, color="red",label="Shutdown Threshold")
    plt.axhline(hazard_threshold_display, color="green",label="Hazard Threshold")
    plt.legend()
    if enable_plots_save == True:
        plt.savefig(fname=vt_w_path+"trace"+trace["trace_ID"],dpi=1060)
    plt.show()
    

    

    




    


