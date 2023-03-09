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
i=7
trace_name = "voltage_trace"+str(i)+".txt"
filename = [traces_path+trace_name]
lines = np.loadtxt(filename,ndmin=1,dtype=np.dtype(float))
trace = [{"trace_ID": str(i),\
           "voltages": [line[1]*1000 for line in lines],\
           "samples": [x[0] for x in list(enumerate(lines))]}]

#Plotting data
shtdw_value = 2300
hazard_threshold_sample = 2600
full_trace_fig_path = "./plots/full_voltage_trace/"
enable_plots_save = False
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