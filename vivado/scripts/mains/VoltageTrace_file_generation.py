# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 10:02:52 2023

Engineer: Michele Pio Fragasso


Description:
    --This file generates the voltage trace necessary files to perform the testbench analysis:
        
        -trace files of 5000 samples
        -packages to set up the parameters of the intermittency emulator.
        
"""

import sys
sys.path.insert(0, "../functions/")

import matplotlib.pyplot as plt
import numpy as np
import misc

#Loading all voltage traces and plotting them
traces_path = "../files/voltage_traces/"
filenames = [traces_path+str(i)+".txt" for i in range(1,11)]
lines = [np.loadtxt(filenames[i-1],ndmin=1,dtype=np.dtype(float)) for i in range(1,11)]
traces = [{"trace_ID": str(i),\
           "voltages": [line[1]*1000 for line in lines[i-1]],\
           "samples": [x[0] for x in list(enumerate(lines[i-1]))]} for i in range(1, 11)]
    
#These values are chosen after analysing the voltage traces, using the python script traceanalysis.py script
shtdw_value = 2300
wrng_value = 2500
system_clock_period = 40
voltage_trace_timescale = 80
window_length = 10000

    
#Traces neglecting the initial power off, and then cutting the first 5000 samples
start_sample_value = shtdw_value + 200
for trace in traces:
    y_trace = trace["voltages"]
    indexes = [index for index, value in list(enumerate(y_trace)) if y_trace[index] < start_sample_value]
    start_index = min([i-1 for i, index in list(enumerate(indexes)) if indexes[i]-indexes[i-1]>1])-5
    trace["cut_v"] = y_trace[start_index:-1]
    trace["cut_v_samples"] = [int(x[0]) for x in list(enumerate(trace["cut_v"]))]
    
#Traces extract the first 5000 samples to test the architecture with a subset of the trace
for trace in traces:
    trace["extract_v"]= trace["cut_v"][0:window_length]
    trace["extract_v_samples"]= [int(x[0]) for x in list(enumerate(trace["extract_v"]))]
    trace["time"] = [float(x*voltage_trace_timescale/1000) for x in trace["extract_v_samples"]]
    
    
keys_map = {"trace_ID":"trace_ID", "extract_v":"voltages", "extract_v_samples":"samples"}
traces_new = [{keys_map[key]:value for key,value in old_trace.items() if key in keys_map} for old_trace in traces]
#Generate Voltage Traces
for trace in traces_new:
    misc.genVoltageTraceFile(trace, voltage_trace_timescale=80)