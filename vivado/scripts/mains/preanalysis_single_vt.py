# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 21:55:00 2023

Revised 03/04/2023

Engineer: Michele Pio Fragasso

Description:
    This script is used to perform a single voltage profile analysis.
    
    It computes the minimum hazard threshold for a given DNN architecture for
    different NV_REG_DELAY factors (ranging from 2 to 11). In this way the
    simulation for different hazard thresholds can be done, by setting up
    correct hazard threshold.
    
    This scripts scans through hazard threshold ranging between wrng_start and
    wrng_end, looking for the minimum hazard threshold that can guarantee no
    data corruption during backup for the given DNN maximum layer size.
    
INPUTS:
    #Voltage trace parameters
    
    i           : voltage trace number. A number between 0 and 9 to select
                    voltage traces between 1 and 10.
    vt_ts       : voltage trace timescale in us.
    sim_time    : simulation time in us.
    
    #Analysis parameters
    
    shtdwn_value: shutdown value in mV.
    hazard_threshold_display : used for display a hazard threshold in mV
    wrng_start      :analysis warning start value, which is the starting 
                        voltage trace value to start analysing the profile.
    wrng_end        :analysis warning end value, which is the ending voltage
                        trace value.
    wrng_step       :analysis warning step, increment of the hazard threshold
                        during analysis
    DNN_max_size    :maximum size of the layer withing the DNN. Used to determing
                        the minimum hazard threshold for backup success.
                        
    #Options paramaters
    
    enable_plots_save   :  Boolean value to enable plot save
    plt_show            :  Boolean to enable plot shoW
    
    
OUTPUTS:
    min_hzrds           : list of minimum hazards for different NV_REG_DELAYS
    Minimum Hazards File: file containing the the minimum hazard threshodl
    the format is:
        "vt-analysis-report_vt-<id>_sim-time-<sim_time>_vt-ts-<vt_ts>_size-<size>"
"""

import sys
sys.path.insert(0, "../functions/")

import matplotlib.pyplot as plt
import matplotlib as mtplt
mtplt.rcParams['text.usetex'] = True
import numpy as np
import misc
import os

#INPUTS
#Voltage trace parameters
vt_ts = 160
trace_number=9#They range from 0 to 9
sim_time = 3_000
shtdw_value = 2300
#Analsysis parameters
wrng_start = 2_300
wrng_final = 4_500
wrng_step = 50
DNN_max_size = 30
#Plot Options
enable_plots_save = False
plt_show = False

#SECONDARY INPUTS (not really necessary)
#Hazazrd threshold to visualize it on plot
hazard_threshold_display = 2600

#PATHS
traces_path = "../files/voltage_traces/"
full_trace_fig_path = "./plots/full_voltage_trace/"
max_number_neurons_fig_path = "./plots/max_number_neurons/"
thresholds_vs_neurons_fig_path =  "./plots/threshold_vs_neurons_path/"
hzrd_prc_path = "./plots/hazard_perc/"
shtdwn_prc_path = "./plots/shtdwn_perc/"
vt_jmpstart_path = "./plots/vt_jmpstart/"
vt_w_path = "./plots/vt_window/"
min_hazards_results = "./min_hazards_res/"
#MAKING DIRECTORIES
#Make plots directory

try:
    os.mkdir("./plots")
except:
    pass
#MAKING FULL TRACE
try:
    os.mkdir(full_trace_fig_path)
except:
    pass
try:
    os.mkdir(max_number_neurons_fig_path)
except:
    pass
try:
    os.mkdir(thresholds_vs_neurons_fig_path)
except:
    pass
try:
    os.mkdir(hzrd_prc_path)
except:
    pass
try:
    os.mkdir(shtdwn_prc_path)
except:
    pass
try:
    os.mkdir(vt_jmpstart_path)
except:
    pass
try:
    os.mkdir(vt_w_path)
except:
    pass
try:
    os.mkdir(min_hazards_results)
except:
    pass


"""
LOADING SELECTED VOLTAGE TRACE
"""
filenames = [traces_path+str(i)+".txt" for i in range(1,11)]
lines = [np.loadtxt(filenames[i-1],ndmin=1,dtype=np.dtype(float)) for i in range(1,11)]
traces = [{"trace_ID": str(i),\
           "voltages": [line[1]*1000 for line in lines[i-1]],\
           "samples": [x[0] for x in list(enumerate(lines[i-1]))]} for i in range(1, 11)]
trace = traces[trace_number]
wlen = int(sim_time/(vt_ts/1000))
#PLOTTING SELECTED VOLTAGE TRACE
if plt_show == True:
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
    
"""
MAXIMUM DNN LAYER SIZE VS. HAZARD THRESHOLDS FOR DIFFERENT NV_REG_DELAY
Description: In this section the maximum DNN layer size is computed versus
the hazard threshold for different NV_REG_DELAY_FACTOR

#Notes: It uses the function misc.compute_max_neuron_number which
extract the sim_time window from the voltage trace
"""
wrng_values = [x for x in range(wrng_start, wrng_final, wrng_step)]
trace["neurons"] = {}
for NV_REG_DELAY_FACTOR in range(2, 12):
    key = "NV_REG_DELAY_FACTOR_"+str(NV_REG_DELAY_FACTOR)
    trace["neurons"][key] = [misc.compute_max_neuron_number(trace,vt_ts=vt_ts,wrng_value=wrng_value, shtdw_value=shtdw_value,NV_REG_DELAY_FACTOR=NV_REG_DELAY_FACTOR,sim_time=sim_time) for wrng_value in wrng_values]
#PLOTTING NEURONS VS. HAZARD TH AND SAVING DATA
if plt_show == True: 
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
"""
#MINIMUM HAZARD THRESHOLD VS MAX DNN LAYER SIZE
#Description: In this section the minimum hazard threshold able to guarantee
correct backup is computed for different maximum DNN LAYER sizes. Done for
different NV_REG_FACTOR
"""
DELAYS = range(2,12)
keys = ["NV_REG_DELAY_FACTOR_"+str(DELAY) for DELAY in DELAYS]
min_hzrds= []
rnd_neurons = []
for key in keys:
    #A target neuron number is selected
    neuron_target = DNN_max_size
    neurons = trace["neurons"][key]
    indexes = [index for index, value in list(enumerate(wrng_values)) if neurons[index] >= neuron_target]
    index = min(indexes)
    hazard_target = wrng_values[index]
    neuron_target_rounded = neurons[index]
    min_hzrds.append(hazard_target)
    #list of rounded neurons
    rnd_neurons.append(neuron_target_rounded)
trace["min_hazards"] = min_hzrds
#PLOTTING MINIMUM HAZARD VS HZ_TH AND SAVING DATA
if plt_show == True:
    plt.figure()
    plt.title("Hazard thresholds vs Maximum number of neurons - Trace no. "+str(trace["trace_ID"]))
    plt.xlabel("Maximum number of neurons within the DNN")
    plt.ylabel("Hazard threshold [mV]")
    #plt.text(neuron_target,hazard_target,'Neuron Target value'+str(neuron_target))
    [plt.plot(rnd_neurons[k], min_hzrds[k], marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green") for k in range(4)]
    plt.axvline(neuron_target)
    # arrowstyle = ptch.ArrowStyle.CurveA()
    # arrowprops = dict(facecolor='black', arrowstyle=arrowstyle)
    # [plt.annotate("Target: ("+str(rnd_neurons[k])+" ,"+ str(min_hzrds[k])+" mV )",xy = (rnd_neurons[k], min_hzrds[k]),xytext=(neuron_target_rounded+100, hazard_target+k*100) , arrowprops=arrowprops, bbox=dict(facecolor='blue', alpha=0.5)) for k in range(4)]
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


"""SHUTDOWN PERCENTAGE VS. HZ_TH
Description: In this section the shutdown percentage over total number of
voltage trace sample is computed for different hazard threshold. It is useful
to have an overview of the energy budget of the voltage trace, which is the
capability of the DNN to progress forward.
"""
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
#PLOTTING HAZARD PERCENTAGE
if plt_show == True:
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
#PLOTTING SHUTDOWN PERCENTAGE
if plt_show == True:
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

"""
VOLTAGE TRACE JUMPSTARTED @ FIRST POWER ON VALUE
"""
y_trace = trace["voltages"]
start_hzrd_value = shtdw_value + 200
indexes = [index for index, value in list(enumerate(y_trace)) if y_trace[index] < start_hzrd_value]
start_index = min([i-1 for i, index in list(enumerate(indexes)) if indexes[i]-indexes[i-1]>1])-5
trace["cut_v"] = y_trace[start_index:-1]
trace["cut_v_samples"] = [int(x[0]) for x in list(enumerate(trace["cut_v"]))]
#PLOTTING
if plt_show == True:
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
"""
VOLTAGE TRACE windowed for sim_time. It's the trace the DNN will be tested with
"""
trace["windowed_v"]= trace["cut_v"][0:wlen]
trace["windowed_v_samples"]= [int(x[0]) for x in list(enumerate(trace["windowed_v"]))]
trace["time"] = [float(x*vt_ts/1000) for x in trace["windowed_v_samples"]]

if plt_show == True:
    plt.plot(trace["time"], trace["windowed_v"], color="blue")
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
"""
Plot max number of neurons and percentage of power on value wrt total samples
"""
trace["active_perc"] = []
for wrng_value in wrng_values:
    active_perc = 0
    for voltage in trace["windowed_v"]:
        if voltage > wrng_value:
            active_perc += 1
    active_perc = active_perc/len(trace["windowed_v"])*100
    trace["active_perc"].append(active_perc)
#PLOTTING RESULTS

if plt_show == True:
    fig = plt.figure()
    # Plot the first set of data on the primary y-axis
    ax1 = fig.gca()
    ax1.plot(wrng_values, trace["neurons"]["NV_REG_DELAY_FACTOR_2"], color='blue', label="NV_REG_FACTOR2")
    ax1.set_ylabel('Max Number of neurons', color='blue')
    ax1.set_xlabel("Hazard Threshold [mV]")
    #ax1.xlabel("Hazard Threshold [mV]")
    ax1.tick_params(axis='y', labelcolor='blue')
    # Create a second y-axis and plot the second set of data
    ax2 = ax1.twinx()
    ax2.plot(wrng_values, trace["active_perc"], color='red')
    ax2.set_ylabel(r'Active Percentage [$\frac{Active samples}{Total Samples}$ \%]', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    # Set the title and show the plot
    ax1.set_title('Max Number of neurons and active percentage')
    ax1.grid(True)
    if enable_plots_save == True:
        fig.savefig("ActivePerc", dpi=1080)
        plt.show()
        
#Printing minimum hazard
print("Minimum Hazard for different NV_REG_DELAY_FACTORS: \n")
print("DNN Max Layer Size: " +str(DNN_max_size)+"\n")
print("Voltage Trace number "+str(trace_number+1)+"\n")
i = 0
for FACTOR in DELAYS:
    print("NV_REG_DELAY_FACTOR = "+str(FACTOR)+ " Minimum Hazard: " + str(min_hzrds[i]) + "\n")
    i+=1

#Printing minimum hazards on file
folderpath = min_hazards_results+"vt-analysis-report_sim-time-"+str(sim_time)+"_vt-ts-"+str(vt_ts)+"_size-"+str(DNN_max_size)+"/"
try:
    os.mkdir(folderpath)
except:
    pass
f = open(folderpath+"vt-analysis-report_vt-"+str(trace_number+1)+"_sim-time-"+str(sim_time)+"_vt-ts-"+str(vt_ts)+"_size-"+str(DNN_max_size)+".txt", "w")
sys.stdout = f
print("Minimum Hazard for different NV_REG_DELAY_FACTORS: \n")
print("DNN Max Layer Size: " +str(DNN_max_size)+"\n")
print("Voltage Trace number "+str(trace_number+1)+"\n")
i = 0
for FACTOR in DELAYS:
    print("NV_REG_DELAY_FACTOR = "+str(FACTOR)+ " Minimum Hazard: " + str(min_hzrds[i]) + "\n")
    i+=1
f.close()
sys.stdout = sys.__stdout__




    


