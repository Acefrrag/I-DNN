# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 09:12:10 2023

Engineer: Michele Pio Fragasso


Description:
    --This script studies the power consumption for different voltage traces
    at different hazard thresholds, for a given DNN architecture.
    --It was used to validate the power consumption model.
"""



import analysis_vt as vt_lib
import matplotlib.pyplot as plt
import re

def compute_pwr_cmpt_breakdown(sim_result, hzrd_threshold_index, num_hidden_layers):
    """
    

    Parameters
    ----------
    sim_results : TYPE
        This contain the simulation results for different hazard thresholds
        sim_result should already contain the power consumption values

    Returns
    -------
    None.

    """
    save=0
    rec=0
    data_mv=0
    compute=0
    sleep=0
    index = hzrd_threshold_index
    
    
    nvregs_save_pwr_cmps = [sim_result["nv_reg"+str(i)+"_inst_pwr_save_state"] for i in range(1, num_hidden_layers+1)]
    nvregs_rec_pwr_cmps = [sim_result["nv_reg"+str(i)+"_inst_pwr_rec_state"] for i in range(1, num_hidden_layers+1)]
    I_layers_compute_pwr_cmps = [sim_result["nv_reg"+str(i)+"_inst_pwr_save_state"] for i in range(1, num_hidden_layers+1)]
    move_save_cmps = [sim_result["I_layer"+str(i)+"_inst_pwr_save_state"] for i in range(1, num_hidden_layers+1)]
    move_rec_cmps = [sim_result["I_layer"+str(i)+"_inst_pwr_rec_state"] for i in range(1, num_hidden_layers+1)]
    I_layer_idle_pwr_cmps  =[sim_result["I_layer"+str(i)+"_inst_pwr_save_state"] for i in range(1, num_hidden_layers+1)]
    nv_regs_idle_pwr_cmps =[sim_result["nv_reg"+str(i)+"_inst_pwr_poweron_state"] for i in range(1, num_hidden_layers+1)]
    
    for k in range(len(nvregs_save_pwr_cmps)):
        sleep = I_layer_idle_pwr_cmps[k][index] + nv_regs_idle_pwr_cmps[k][index]
        save = nvregs_save_pwr_cmps[k][index] + nvregs_rec_pwr_cmps[k][index]
        rec = nvregs_rec_pwr_cmps[k][index]
        compute = I_layers_compute_pwr_cmps[k][index]
        data_mv = move_save_cmps[k][index] + move_rec_cmps[k][index]
    
    overall = sleep+save+rec+compute+data_mv
        
    return(save, rec, data_mv, compute, sleep, overall)


if __name__ == "__main__":
    
    #STUDY OF POWER CONSUMPTION FOR DIFFERENT DELAYS
    #I plot it for the original simulation I carried
    #They are performed on voltage trace 2 for different NV_REG_DELAY_FACTORS
    NV_REG_DELAY_FACTORS = [2, 5, 11]#, 8, 11]
    num_hidden_layers = 4
    voltage_tracename = "voltage_trace2"
    DB_results_DELAYS_path = "./results/DB_results/4layer_80/powerpoint_voltagetrace2"
    DB_results_DELAYS_path = "./results/DB_results/4layer_80/"+voltage_tracename
    #Plotting power consumption for different
    #INCREASING THE NV_REG_DELAY, decreases the overal power consumption e
    results_path_list = []
    for NV_REG_FACTOR in NV_REG_DELAY_FACTORS:
        results_path_list.append(DB_results_DELAYS_path+"/DB_results_fixedtime_NVREG_DELAY_FACTOR"+str(NV_REG_FACTOR)+".txt")
    results_name = "DB"
    
    #Loading DB_results
    DB_results_files = [open(path,"r") for path in results_path_list]
    DB_results_allLines = [file.readlines() for file in DB_results_files]
    sim_results_DELAYS = {}
    i=0
    for NV_REG_FACTOR in NV_REG_DELAY_FACTORS:
        key = "NV_REG_FACTOR"+str(NV_REG_FACTOR)
        allLines = DB_results_allLines[i]
        sim_results_DELAYS[key] = vt_lib.data_from_lines(allLines)
        i += 1
    
    
    [file.close() for file in DB_results_files]
    
    #Computing Power Consumption and Throughput per Power COnsumtpion
    [vt_lib.overall_data(sim_results_DELAYS[sim_result], NV_REG_FACTOR=int(re.search(r"\d+", sim_result).group())) for sim_result in sim_results_DELAYS.keys()]
    
    #Plotting POWER CONSUMTPION VERSUS HAZARD THRESHOLD
    
    pwr_cmpts =  [sim_results_DELAYS[sim_result]["total_power_consumption"] for sim_result in sim_results_DELAYS.keys()]
    hzrds = [sim_results_DELAYS[sim_result]["hazard_threshold_val"] for sim_result in sim_results_DELAYS.keys()]
    efficiency = [sim_results_DELAYS[sim_result]["throughput_pwr_csmpt"] for sim_result in sim_results_DELAYS.keys()]
    
    
    #So as we can see the throuput per power consumption is normalized with respect to the NV_REG
    #This justifies the choice of the power consumption values
    #The power consumption values for the NV_REGs were chosen according to 2 criteria
    #1) Power consumption of NON_VOLATILE REGISTER should decrease as the DELAY FACTOR
    #increases
    #2) Throuput per power consumption should be comparable for different DELAYS
    #same order of magnitude
    #3) The power consumption should be greater for backup operation. Save and Recovery
    #must be expensive operations
    
    #The power consumption of the layers just 1 criteria:
    #1) The layer computation power consumption  shoyld increase as the number of neurons per 
    #layer increases(more weight memory acceess, more MAC operations)
    
    
    #These two plots whow how the power consumption and throughput per power consumption
    #changes depending the spped of the NV_REG. From here i Show the fullfillment of criteria 1 and 2
    fig = plt.figure()
    ax = fig.gca()
    ax.plot(hzrds[0], pwr_cmpts[0], label="NV_REG_DELAY_FACTOR=2")
    ax.plot(hzrds[1], pwr_cmpts[1], label="NV_REG_DELAY_FACTOR=5")
    # ax.plot(hzrds[2], pwr_cmpts[2], label="NV_REG_DELAY_FACTOR=8")
    ax.plot(hzrds[2], pwr_cmpts[2], label="NV_REG_DELAY_FACTOR=11")
    ax.set_xlabel("Hazard Threshold [mV]")
    ax.set_ylabel("Power Consumption [mW]")
    plt.xlim(2500, 4000)
    plt.grid(True)
    plt.legend()
    ax.set_title("Power Consumption - Voltage Trace 2 - 4-layer DNN")
    plt.savefig("pwr_cmpt", dpi=1080)
    plt.show()
    
    
    #DNN efficiency per different NV_REG_DELAYS
    fig = plt.figure()
    ax = fig.gca()
    ax.plot(hzrds[0], efficiency[0], label="NV_REG_DELAY_FACTOR=2")
    ax.plot(hzrds[1], efficiency[1], label="NV_REG_DELAY_FACTOR=5")
    # ax.plot(hzrds[2], throughput_per_pwr[2], label="NV_REG_DELAY_FACTOR=8")
    ax.plot(hzrds[2], efficiency[2], label="NV_REG_DELAY_FACTOR=11")
    ax.set_xlabel("Hazard Threshold [mV]")
    ax.set_ylabel(r"$\frac{Throughput}{Power Consumption}$ [$\frac{Op/s}{W}$]")
    plt.xlim(2500, 4000)
    plt.grid(True)
    plt.legend()
    ax.set_title("DNN Efficiency")
    plt.savefig("Throughput_per_pwr", dpi=1080)
    plt.show()
    #Efficiency for given hazard threshold
    # hzrd_value = 3900
    # indexes_DELAYS = []
    # k=0
    # for FACTOR in NV_REG_DELAY_FACTORS:
    #     indexes = [index for index in range(len(hzrds[k])) if hzrds[k][index] > hzrd_value]
    #     indexes_DELAYS.append(min(indexes))
    #     k+=1
    # for p in range(2):
    #     index = indexes_DELAYS[p]
    #     print(hzrds[p][index])
               
               
    #POWER CONSUMPTION FOR SINGLE HAZARD THERSHOLD
    available_thresholds = sim_results_DELAYS["NV_REG_FACTOR2"]["hazard_threshold_val"]
    print("The available threshold are:\n")
    print(available_thresholds)
    print("Insert the value of threshold to analyze")
    threshold = int(input())
    indexes = [index if available_thresholds[index] == threshold else -1 for index in range(len(available_thresholds))]
    index = max(indexes)
    
    #Study of the power consumption per DNN components
    #Here we are gonna plot power consumption bar charts for a given hazard threshold,
    #and a given voltage trace.
    #From here I should show the fulfillment of criteria 3
        
    
    
    #Power consumption Breakdown
    sim_result = sim_results_DELAYS["NV_REG_FACTOR2"]
    (save, rec, data_mv, layers, sleep, overall) = compute_pwr_cmpt_breakdown(sim_result, hzrd_threshold_index=index, num_hidden_layers=4)
    labels = ["Data Saves", "Data Recovery", "Backup Data Movement","Layers", "Sleep", "Overall"]
    
    pwr_cmpt_breakdown = (save, rec, data_mv, layers, sleep, overall)
    fig,ax = plt.subplots()
    ax = fig.gca()
    patterns = ['/', 'O', 'x', '*', '+', '|']
    colors = ['red', 'green', 'blue', 'yellow', 'purple', "pink"]
    for i in range(len(labels)):
        ax.bar(i, pwr_cmpt_breakdown[i], color = colors[i], label=labels[i], hatch=patterns[i])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.35), ncol=3)
    ax.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
    ax.set_title("Power Consumption Breakdown", pad=15)
    ax.set_ylabel("Power Consumption [mW]")
    ax.set_xlabel("Breakdown")
    ax.set_yscale("log")
    ax.grid(True)
    #plt.ylim(10**(-1),10**1)
    fig.savefig("pwr_brkdwn", dpi=1080)
    plt.show()
    
    #Study of power conusmption for different layers
    #From here i show the fullfiment of criteria 1 for layer power consumtpinon values.
    
    
    