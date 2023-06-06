# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 10:02:52 2023

Engineer: Michele Pio Fragasso

Description:
    This script generates the voltage trace necessary files to perform the
    testbench analysis.
    Most likely, you will need to run this only once, since system clock period
    and voltage trace timescale are set up only once.
    
    After running this generation script, the testbench should be run for
    sim_time amount of time.
        
Input:
    - vt_ts         : Voltage trace timescale in ns. It's the sampling time'
    - SC_P          : System clock period in ns.
    - sim_time      : Simulation time in us. If this value is biggere than the 
                        voltage trace time duration, it will produce a cut off
                        profile. As a result, during simulation the IE will
                        wrap around the voltage trace values.
    - shtdw_value   : Shut Down value in mV.
Output:
    - Trace files       : Contaning VHDL compatible voltage profile
                             to be reproduced with the IE, satisfying
                             the voltage trace timescale and siimulation
                             time
                          They are placed in ../../src/NORM/voltage_traces
                          and 
    - IE_PACKAGE.vhd    : VHDL packages to set up the parameters of the
                             intermittency emulator: num_elements_rom,
                             prescaler value, IE_MAX_VALUE

"""

import sys
sys.path.insert(0, "../functions/")

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
SC_P = 40           #System clock period
sim_time = 3_000    #Simulation time in us
vt_ts = 160         #Voltage Trace Timescale in ns 
w_len = int(sim_time/(vt_ts/1_000))

#Traces neglecting the initial power off
start_hzrd_value = shtdw_value + 200
for trace in traces:
    y_trace = trace["voltages"]
    indexes = [index for index, value in list(enumerate(y_trace)) if y_trace[index] < start_hzrd_value]
    start_index = min([i-1 for i, index in list(enumerate(indexes)) if indexes[i]-indexes[i-1]>1])-5
    trace["cut_v"] = y_trace[start_index:-1]
    trace["cut_v_samples"] = [int(x[0]) for x in list(enumerate(trace["cut_v"]))]
    
#Traces extract the first N samples to test the architecture with a subset of the trace
for trace in traces:
    trace["windowed_v"]= trace["cut_v"][0:w_len]
    trace["windowed_v_samples"]= [int(x[0]) for x in list(enumerate(trace["windowed_v"]))]
    trace["time"] = [float(x*vt_ts/1000) for x in trace["windowed_v_samples"]]
    
   
keys_map = {"trace_ID":"trace_ID", "windowed_v":"voltages", "windowed_v_samples":"samples"}
traces_new = [{keys_map[key]:value for key,value in old_trace.items() if key in keys_map} for old_trace in traces]
#Generate Voltage Traces
for trace in traces_new:
    misc.genVoltageTraceFile(trace, vt_ts=vt_ts, SC_p = SC_P)