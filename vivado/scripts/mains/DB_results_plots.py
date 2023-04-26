# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 23:13:55 2023

Engineer: Michele Pio Fragasso


Description:
    --This plot produces the end-of-simulation values for a given simulation
    results
    INPUTS:
        results_path: path to the DB results that have aggregated already.
"""

import re
import matplotlib.pyplot as plt
import os

#INPUTS
results_path = "./results/DB_results/DB_results_fixedtme_NVREG_DELAY_FACTOR2_demo.txt"
plt_show=False
plt_save=True

try:
    f = open(results_path, "r")
    allLines = f.readlines()
    results = {}
    line_key_index = 2
    line_start_data_index = 3
    #Loading dictionary keys
    keys = re.split(r'\W+', allLines[line_key_index])[:-1]
    for key in keys:
        results[key] = []
    #Filling the dictionary with values
    for i, line in enumerate(allLines[line_start_data_index:-1]):
        items = re.split(r';', line)[:-1]
        #Factor to transform the time into a us time unit
        if keys[i] == "time":
            item = items[i]
            if "ms" in item:
                factor = 10**-3
            else:
                if "us" in item:
                    factor = 10**-6
                else:
                     if "ns" in item:
                         factor = 10**-9
                     else:
                         factor = 1
                             #print(items[i])
        items = [re.sub(r'\D+',"",items[i]) for i in range(len(items))]
        end_values = items 
        [results[key].append(int(end_values[i])) for i,key in enumerate(keys)]
except:
    pass


#Plotting data
#figures = [plt.figure() for i in range(len(keys))]
rect = [1,1,1,1] #Standard dimensions of axes
for i in range(len(results)):
    plt.figure()
    plt.plot(results["hazard_threshold_val"], results[keys[i]])
    plt.title(keys[i]+" vs. Hazard Threshold")
    plt.xlabel("Hazard Threshold [mV]")
    plt.ylabel(keys[i])
    plt.grid()
    #plt.close(figure)
    if plt_save==True:
        plt.savefig("./plots/DB_plots/"+keys[i], dpi=1080)

# if plt_save==True:
#     try:
#         os.mkdir("./plots/DB_plots/")
#     except:
#         pass
#     for i,fig in enumerate(figures):
#         # new_fig = plt.figure()
#         # new_manager = new_fig.canvas.manager
#         # new_manager.canvas.figure = fig
#         # fig.set_canvas(new_manager.canvas)
#         fig.savefig("./plots/DB_plots/"+keys[i], dpi=1080)
    
if plt_show == True:
    plt.show()