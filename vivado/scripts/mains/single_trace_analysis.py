# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 21:55:00 2023

Engineer: Michele Pio Fragasso


Description:
    --File description
"""

import sys
sys.path.insert(0, "../functions/")

import matplotlib.pyplot as plt
import matplotlib as mtplt
import numpy as np
import misc
import os

#Make plots directory
try:
    os.mkdir("./plots")
except:
    pass



#Loading all voltage traces and plotting them
traces_path = "../files/voltage_traces/"
i=1#Trace number
filenames = [traces_path+str(i)+".txt" for i in range(1,11)]
lines = [np.loadtxt(filenames[i-1],ndmin=1,dtype=np.dtype(float)) for i in range(1,11)]
traces = [{"trace_ID": str(i),\
           "voltages": [line[1]*1000 for line in lines[i-1]],\
           "samples": [x[0] for x in list(enumerate(lines[i-1]))]} for i in range(1, 11)]
trace = traces[i]
voltage_trace_timescale_ns = 160
simulation_time_us = 3_000
window_length = int(simulation_time_us/(voltage_trace_timescale_ns/1000))
#Plotting data
shtdw_value = 2300
hazard_threshold_sample = 2600
full_trace_fig_path = "./plots/full_voltage_trace/"
enable_plots_save = True
try:
    os.mkdir(full_trace_fig_path)
except:
    pass

plt.figure()
plt.title("Data Trace "+trace["trace_ID"])
plt.xlabel("Sample")
plt.ylabel("Voltage[mV]")
plt.plot(trace["samples"],trace["voltages"],color ="blue")
plt.axhline(shtdw_value, color="red",label="Shutdown Threshold")
plt.axhline(hazard_threshold_sample, color="green",label="Hazard Threshold")
plt.legend()
plt.grid()
if enable_plots_save == True:
    plt.savefig(fname=full_trace_fig_path+"trace_"+trace["trace_ID"],dpi=1060)
plt.show()

#Maximum number of neurons analysis
trace["neurons"] = {}
wrng_value_step = 30
wrng_values = [x for x in range(2300, 3000, wrng_value_step)]
for NV_REG_DELAY_FACTOR in range(2, 12):
    key = "NV_REG_DELAY_FACTOR_"+str(NV_REG_DELAY_FACTOR)
    trace["neurons"][key] = [misc.compute_max_neuron_number(trace,voltage_trace_timescale=voltage_trace_timescale_ns,wrng_value=wrng_value, shtdw_value=shtdw_value,NV_REG_DELAY_FACTOR=NV_REG_DELAY_FACTOR) for wrng_value in wrng_values]
#Plotting and saving results
max_number_neurons_fig_path = "./plots/max_number_neurons/"

try:
    os.mkdir(max_number_neurons_fig_path)
except:
    pass
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


key = "NV_REG_DELAY_FACTOR_2"
#A target neuron number is selected
neuron_target = 30
neurons = trace["neurons"][key]
indexes = [index for index, value in list(enumerate(wrng_values)) if neurons[index] >= neuron_target]
index = min(indexes)
hazard_target = wrng_values[index]
neuron_target_rounded = neurons[index]
thresholds_vs_neurons_fig_path =  "./plots/threshold_vs_neurons_path/"
try:
    os.mkdir(thresholds_vs_neurons_fig_path)
except:
    pass
plt.figure()
plt.title("Hazard thresholds vs Maximum number of neurons - Trace no. "+str(trace["trace_ID"]))
plt.xlabel("Maximum number of neurons within the DNN")
plt.ylabel("Hazard threshold [mV]")
#plt.text(neuron_target,hazard_target,'Neuron Target value'+str(neuron_target))
plt.plot(neuron_target_rounded, hazard_target, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
plt.axvline(neuron_target_rounded)
txt = plt.text(neuron_target_rounded+10, hazard_target+100, "Target: ("+str(neuron_target_rounded)+" ,"+ str(hazard_target)+" mV )", bbox=dict(facecolor='blue', alpha=0.5))
                
i = 2
for key in trace["neurons"].keys():
    label = "DELAY_FACTOR = " + str(i)
    plt.plot( trace["neurons"][key], wrng_values,label=label)
    i += 1
plt.grid()
plt.legend(prop={'size': 6})

if enable_plots_save == True:
    plt.savefig(fname=thresholds_vs_neurons_fig_path+"trace_"+trace["trace_ID"],dpi=1060)

plt.show()

#Hazard Threshold Sample Percentage analysis
trace["wrng_perc"] = np.zeros(len(wrng_values))
trace["shtdwn_perc"] = 0
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
    perc = float(wrng_perc)/len(trace["voltages"])*100
    trace["shtdwn_perc"] = perc
    c += 1
    
    
#Plotting results
hzrd_prc_path = "./plots/hazard_perc/"
try:
    os.mkdir(hzrd_prc_path)
except:
    pass
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

shtdwn_prc_path = "./plots/shtdwn_perc/"
try:
    os.mkdir(shtdwn_prc_path)
except:
    pass
plt.figure()
plt.rcParams['text.usetex'] = True
plt.title("Shutdown samples percentage w.r.t. Threshold")
plt.xlabel("Hazard Threshold [mV]")
plt.ylabel("$\\frac{Shutdown Samples}{Samples}[\\%]$")
plt.axhline(trace["shtdwn_perc"])
plt.grid()
if enable_plots_save == True:
    plt.savefig(fname=shtdwn_prc_path+"trace_"+trace["trace_ID"],dpi=1060)
plt.show()



#Traces neglecting the initial power off
vt_jmpstart_path = "./plots/vt_jmpstart/"
try:
    os.mkdir(vt_jmpstart_path)
except:
    pass
y_trace = trace["voltages"]
indexes = [index for index, value in list(enumerate(y_trace)) if y_trace[index] < shtdw_value]
start_index = min([i-1 for i, index in list(enumerate(indexes)) if indexes[i]-indexes[i-1]>1])-5
trace["cut_v"] = y_trace[start_index:-1]
trace["cut_v_samples"] = [int(x[0]) for x in list(enumerate(trace["cut_v"]))]
#Plotting
plt.plot(trace["cut_v_samples"], trace["cut_v"], color="blue")
plt.grid()
plt.title("Voltage Trace jumpstarted plotted from the first value.")
plt.xlabel("Sample")
plt.ylabel("Voltage [mV]")
plt.axhline(shtdw_value, color="red",label="Shutdown Threshold")
plt.axhline(hazard_threshold_sample, color="green",label="Hazard Threshold")
plt.legend()
if enable_plots_save == True:
    plt.savefig(fname=vt_jmpstart_path+"trace_"+trace["trace_ID"],dpi=1060)
plt.show()



#Traces extract the first windows_length samples to test the architecture with a subset of the trace

vt_w_path = "./plots/vt_window/"
try:
    os.mkdir(vt_w_path)
except:
    pass
trace["extract_v"]= trace["cut_v"][0:window_length]
trace["extract_v_samples"]= [int(x[0]) for x in list(enumerate(trace["extract_v"]))]
trace["time"] = [float(x*voltage_trace_timescale_ns/1000) for x in trace["extract_v_samples"]]
plt.plot(trace["time"], trace["extract_v"], color="blue")
plt.title("Voltage Trace no."+trace["trace_ID"]+" - Voltage versus Time")
plt.xlabel("Time [us]")
plt.ylabel("Voltage [mV]")
plt.grid()
plt.axhline(shtdw_value, color="red",label="Shutdown Threshold")
plt.axhline(hazard_threshold_sample, color="green",label="Hazard Threshold")
plt.legend()
if enable_plots_save == True:
    plt.savefig(fname=vt_w_path+"trace"+trace["trace_ID"],dpi=1060)
plt.show()
    


# #Compute number of oscillation around the hazard threshold
# #An oscillation is counted when we go from a lower to higher value than the hazard threshold 
# trace["osc_count"] = []
# k = 0
# for wrng_value in wrng_values:
#     osc_count = 0
#     for i in range(len(trace["extract_v"])-1):
#         if trace["extract_v"][i+1] < wrng_value and trace["extract_v"][i] > wrng_value:
#             osc_count += 1
#     trace["osc_count"].append(osc_count)
#     k += 1

# plt.plot(wrng_values, trace["osc_count"])
# plt.grid()
# plt.show()

    
    