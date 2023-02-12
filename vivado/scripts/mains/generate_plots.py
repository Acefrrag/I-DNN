import sys
sys.path.insert(0, "../functions/")

from matplotlib import pyplot as plt
import re
import os
import network2



results_plots_path = "./plots/DB_results_plots/"
DB_result_log_path = "./results/DB_result_log.txt"
try:
    os.mkdir(results_plots_path)
except:
    pass
NV_REG_FACTORS = [2,5,8,11]
results_path_list = []
for NV_REG_FACTOR in NV_REG_FACTORS:
    results_path_list.append("./results/Simulation5/DB_results_fixedtime_NVREG_DELAY_FACTOR"+str(NV_REG_FACTOR)+".txt")
results_name = "DB"

##----------------------------------------------------------------------- Defaults

##-------------------------------------------------------------------------------- 

##----------------------------------------------------Arguments parsing and checks
##--------------------------------------------------------------------------------


#list containg handlers to figures. There is a figure for every vivado simulation object.
#Every figure will contain the set of plot with different NV_REG_DELAY factors.
#The number of the figures must be equal to the number of object loaded from the simulation environment
#So we scan though the file to compute this number.
#DETERMINING NUMBER OF ELEMENTS
#I take the first file to determine the number of simmulation objects
DB_result_log = open(DB_result_log_path,"r")
allLines = DB_result_log.readlines()
for i, line in enumerate(allLines):
    if "number_simulation_objects" in line:
        number_objects = int(re.search("\d+", line).group())
result_figures_list = []
end_data_fixed_time_simulations = []


    
net = network2.load("../files/weights_n_biases/training_01-17-23_00-31-56/WeightsAndBiases.txt")
number_neurons = net.sizes[1:]
num_hidden_layers = len(number_neurons)

i_factor = 0
for results_path in results_path_list:
    NV_REG_FACTOR = NV_REG_FACTORS[i_factor]

    results_file = open(results_path, 'r')
    allLines = results_file.readlines()
    
    data_fix_time_tmp = []
    data_fix_val_tmp = []
    start_fix_time = 0
    start_fix_val= 0
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
        if "Fixed value simulation start" in line:    
            start_fix_val = 1
        else:
            if start_fix_val == 1:
                if "Fixed value simulation end" not in line:
                    data_fix_val_tmp.append(str(line.strip()))
                else:
                    start_fix_val = 0
    
    names_fixed_time = list(filter(None,data_fix_time_tmp.pop(0).split(";")))
    #names_fixed_val= list(filter(None,data_fix_val_tmp.pop(0).split(";")))
    
    #This is a list of lists.
    #Every list will host the set of signal values of specific object
    #(simulation time, power_apprx_value, etc....)
    # at the end of each test
    
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
            item = int(re.sub("[^0-9]", "",item))
            end_data_fixed_time[key].append(item*divide)
            

    

    #Extracting number neurons per layer
    
    for i,data in enumerate(data_fix_val_tmp):
        data=list(filter(lambda x: None if '' else str(x),data.split(";")))
        for j,item in enumerate(data):
            divide = 1
            if "ms" in item:
                divide = 10**3
            elif "ns" in item:
                divide = 10**-3
            elif "ps" in item:
                divide = 10**-9
            else:
                None
            item = int(re.sub("[^0-9]", "",item))
            end_data_fixed_val[key].append(item*divide)
    
    # print(names_fixed_time)
    # print(end_data_fixed_time)
    # print(names_fixed_val)
    # print(end_data_fixed_val)
    
    results_file.close()
    ##---------------------------------------------------------------------Plot reults
    # Plot fixed time graphs
        
    #Plot hazard threshold versus power approximation values
    #Layer_PAs
    #Versus idle_state
    end_data_fixed_time_simulations.append(end_data_fixed_time)
    i_factor += 1
    

test_no = 0
for NV_REG_FACTOR in NV_REG_FACTORS:
    #Computing data consumption
    #The power consumption of the layer should be proportional to the number
    #of the neurons in the layer, when computing the weighted sum.
    #We load the trained neural network to load this value.
    #Computing total power consumeption per simulation
    #Creating power consumption table
    #INSTANTANTEUOS POWER CONSUMPTION LAYERS
    #nanowatts/1_000_000
    PWR_STATE_LAYER_IDLE = 1/1_000_000
    PWR_STATE_LAYER_COMP_DEF = 100/1_000_000
    BASE_NEURONS = 30 #Number of neurons for which the layer uses PWR_COMP_DEF during computation
    PWR_STATE_LAYER_COMP =  [neurons*PWR_STATE_LAYER_COMP_DEF/BASE_NEURONS for neurons in number_neurons]
    PWR_STATE_LAYER_SAVE = 20/1_000_000
    PWR_STATE_LAYER_REC = 20/1_000_000
    #INSTANTANEUOS POWER CONSUMPTION NVREG
    PWR_NVREG_POWERON = 1/1_000_000
    BASE_DELAY_FACTOR = 2
    PWR_NVREG_RECOVERY_DEF = 10000/1_000_000
    PWR_NVREG_SAVE_DEF = 10000/1_000_000
    PWR_NVREG_RECOVERY = ((BASE_DELAY_FACTOR/NV_REG_FACTOR)**1)*PWR_NVREG_RECOVERY_DEF
    PWR_NVREG_SAVE = ((BASE_DELAY_FACTOR/NV_REG_FACTOR)**1)*PWR_NVREG_SAVE_DEF

    end_data_fixed_time = end_data_fixed_time_simulations[test_no]
    for i in range(num_hidden_layers):
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_idle_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_idle_state"
        inst_pwr = [PWR_STATE_LAYER_IDLE*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_compute_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_compute_state"
        inst_pwr = [PWR_STATE_LAYER_COMP[i]*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_save_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_save_state"
        inst_pwr = [PWR_STATE_LAYER_SAVE*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_rec_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_rec_state"
        inst_pwr = [PWR_STATE_LAYER_REC*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_poweron_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_poweron_state"
        inst_pwr = [PWR_NVREG_POWERON*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_rec_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_rec_state"
        inst_pwr = [PWR_NVREG_RECOVERY*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_save_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_save_state"
        inst_pwr = [PWR_NVREG_SAVE*value for value in end_data_fixed_time[key_pwr_apprx]]
        end_data_fixed_time_simulations[test_no][key_pwr_csmpt] = inst_pwr
    test_no += 1
    
#Computing Total Power Consumtpion, Normalized Throughput and Throughput/Power Consumption
test_no = 0
for NV_REG_FACTOR in NV_REG_FACTORS:
    pwr_csmpt = [0 for c in range(len(end_data_fixed_time["hazard_threshold_val"]))]
    for i in range(num_hidden_layers):
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_idle_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_idle_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_compute_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_compute_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_save_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_save_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
        key_pwr_apprx = "I_layer"+str(i+1)+"_pwr_apprx_values_rec_state"
        key_pwr_csmpt = "I_layer"+str(i+1)+"_inst_pwr_rec_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_poweron_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_poweron_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_rec_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_rec_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
        key_pwr_apprx = "nv_reg"+str(i+1)+"_pwr_apprx_values_save_state"
        key_pwr_csmpt = "nv_reg"+str(i+1)+"_inst_pwr_save_state"
        pwr_csmpt = [pwr_csmpt[k]+end_data_fixed_time_simulations[test_no][key_pwr_csmpt][k] for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
    end_data_fixed_time_simulations[test_no]["total_power_consumption"] = pwr_csmpt
    end_data_fixed_time_simulations[test_no]["throughput"] = [end_data_fixed_time_simulations[test_no]["executed_batches"][k]/end_data_fixed_time_simulations[test_no]["time"][k] for k in range(len(end_data_fixed_time["time"]))]
    end_data_fixed_time_simulations[test_no]["throughput_pwr_csmpt_W"] = [end_data_fixed_time_simulations[test_no]["throughput"][k]/end_data_fixed_time_simulations[test_no]["total_power_consumption"][k]*1000 for k in range(len(end_data_fixed_time["hazard_threshold_val"]))]
    test_no += 1
    #Computing Throughput
               
        
number_objects = len(end_data_fixed_time_simulations[0])


for i in range(number_objects):
    result_figures_list.append(plt.figure())
test_no = 0
#ax = []
for NV_REG_FACTOR in NV_REG_FACTORS:
    names_fixed_time = list(end_data_fixed_time_simulations[test_no].keys())
    end_data_fixed_time = end_data_fixed_time_simulations[test_no]
    for i in range(number_objects):
        key_xaxis = "hazard_threshold_val"
        key_yaxis = names_fixed_time[i]
        #ax.append(result_figures_list[i].gca())
        ax = result_figures_list[i].gca()
        title = "Fixed Time Results - Hazard Threshold vs."+names_fixed_time[i]
        xlabel = "Hazard Threshold [mV]"
        ylabel = names_fixed_time[i]
        if "inst_pwr" in title:
            ylabel += " [mW]"
        if "apprx_values" in title:
            ylabel += " [No. Cycles]"
        if "total" in title:
            ylabel += " [mW]"
        if "throughput" in title and "throughput_pwr" not in title:
            ylabel += "[Op/s]"
        if "throughput_pwr"  in title:
            ylabel += "[Op/s/mW]"
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.plot(end_data_fixed_time[key_xaxis],end_data_fixed_time[key_yaxis], label="NVREG_FACTOR="+str(NV_REG_FACTOR))
        ax.legend()
        ax.grid(True)
    test_no += 1
plt.show()


#PLOTTING AND SAVING PLOT FOR FINDING OPTIMAL VALUE
#THORUGHPUT OF NVREG _FACTOR = 2
NV_REG_FACTOR = 2
index = [index for index,value in list(enumerate(NV_REG_FACTORS)) if NV_REG_FACTORS[index] == NV_REG_FACTOR][0]
end_data_fixed_time = end_data_fixed_time_simulations[index]

#OPTIMAL VALUE GIVEN NUMBER NEURONS
#Plotting the optimal value starting from the target hazard threshold
hazard_target = 2480 #Valur found from singl trace analysis
#Searching for the maximum in the right neighbourhood
indexes = [index for index, value in list(enumerate(end_data_fixed_time[names_fixed_time[0]])) if value > hazard_target]
index = min(indexes)
section_throughput = end_data_fixed_time[names_fixed_time[-1]][index:]
index_opt = section_throughput.index(max(section_throughput))
opt_throughput = section_throughput[index_opt]
opt_threshold = end_data_fixed_time[names_fixed_time[0]][index_opt+index]
optimal_value_neurons_plot = "opt_value_neurons"
key_xaxis = "hazard_threshold_val"
key_yaxis = names_fixed_time[-1]
#ax.append(result_figures_list[i].gca())
fig = plt.figure()
axis = fig.gca()
title = "Fixed Time Results - Hazard Threshold vs."+names_fixed_time[-1]
xlabel = "Hazard Threshold [mV]"
ylabel = names_fixed_time[i]
if "inst_pwr" in title:
    ylabel += " [mW]"
if "apprx_values" in title:
    ylabel += " [No. Cycles]"
if "total" in title:
    ylabel += " [mW]"
if "throughput" in title and "throughput_pwr" not in title:
    ylabel += "[Op/s]"
if "throughput_pwr"  in title:
    ylabel += "[Op/s/mW]"
axis.set_title(title)
axis.set_xlabel(xlabel)
axis.set_ylabel(ylabel)
axis.plot(end_data_fixed_time[key_xaxis],end_data_fixed_time[key_yaxis], color="crimson",label="NVREG_FACTOR="+str(NV_REG_FACTOR))
axis.legend()
axis.grid(True)
#Computing Throughput, Normalized 
axis.plot(opt_threshold, opt_throughput, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
axis.text(opt_threshold+100, opt_throughput+1000, "Optimal Value: ("+ str(int(opt_threshold))+" mV ,"+str(int(opt_throughput))+" OP/s/mW )",bbox = dict(facecolor='blue', alpha=0.5))
fig.savefig(results_plots_path+optimal_value_neurons_plot,dpi=1260)

#OPTIMAL VALUE GIVEN THROUGHPUT SPECIFICATION
#TARGET THROGUHTPUT VALUE
throughput_target_figname = "throughput_target"
throughput_target = 10_000
indexes = [index for index, value in list(enumerate(end_data_fixed_time[names_fixed_time[-2]])) if value <= throughput_target]
index = min(indexes)
throughput_rounded = end_data_fixed_time[names_fixed_time[-2]][index]
hazard_target = end_data_fixed_time[names_fixed_time[0]][index]
#Plotting data of throughput figure
key_xaxis = "hazard_threshold_val"
key_yaxis = names_fixed_time[-2]
#ax.append(result_figures_list[i].gca())
fig = plt.figure()
axis = fig.gca()
title = "Fixed Time Results - Hazard Threshold vs."+names_fixed_time[-2]
xlabel = "Hazard Threshold [mV]"
ylabel = names_fixed_time[i]
if "inst_pwr" in title:
    ylabel += " [mW]"
if "apprx_values" in title:
    ylabel += " [No. Cycles]"
if "total" in title:
    ylabel += " [mW]"
if "throughput" in title and "throughput_pwr" not in title:
    ylabel += "[Op/s]"
if "throughput_pwr"  in title:
    ylabel += "[Op/s/mW]"
axis.set_title(title)
axis.set_xlabel(xlabel)
axis.set_ylabel(ylabel)
axis.plot(end_data_fixed_time[key_xaxis],end_data_fixed_time[key_yaxis], color="crimson",label="NVREG_FACTOR="+str(NV_REG_FACTOR))
axis.legend()
axis.grid(True)
axis.axhline(throughput_target)
axis.plot(hazard_target, throughput_rounded, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
axis.text(hazard_target+100, throughput_rounded+1000, "Target: "+str(int(hazard_target))+" mV , "+str(int(throughput_target))+" Op/s", bbox = dict(facecolor='blue', alpha=0.5))
fig.savefig(results_plots_path+throughput_target_figname+"",dpi=1060)


#OPTIMAL HAZARD THRESHOLD
#Finding optimal Hazard threshold
optimal_threshold_throughput_figname = "optimal_threshold_throughput"
section_throughput = end_data_fixed_time[names_fixed_time[-1]][index:]
index_opt = section_throughput.index(max(section_throughput))
opt_throughput = section_throughput[index_opt]
opt_threshold = end_data_fixed_time[names_fixed_time[0]][index_opt+index]
#Plotting
key_xaxis = "hazard_threshold_val"
key_yaxis = names_fixed_time[-1]
#ax.append(result_figures_list[i].gca())
fig = plt.figure()
axis = fig.gca()
title = "Fixed Time Results - Hazard Threshold vs."+names_fixed_time[-1]
xlabel = "Hazard Threshold [mV]"
ylabel = names_fixed_time[i]
if "inst_pwr" in title:
    ylabel += " [mW]"
if "apprx_values" in title:
    ylabel += " [No. Cycles]"
if "total" in title:
    ylabel += " [mW]"
if "throughput" in title and "throughput_pwr" not in title:
    ylabel += "[Op/s]"
if "throughput_pwr"  in title:
    ylabel += "[Op/s/mW]"
axis.set_title(title)
axis.set_xlabel(xlabel)
axis.set_ylabel(ylabel)
axis.plot(end_data_fixed_time[key_xaxis],end_data_fixed_time[key_yaxis], color="crimson",label="NVREG_FACTOR="+str(NV_REG_FACTOR))
axis.legend()
axis.grid(True)
#Computing Throughput, Normalized 
axis.plot(opt_threshold, opt_throughput, marker="o", markersize=5, markeredgecolor="red", markerfacecolor="green")
axis.text(opt_threshold+100, opt_throughput+1000, "Optimal Value: ("+ str(int(opt_threshold))+" mV ,"+str(int(opt_throughput))+" OP/s/mW )",bbox = dict(facecolor='blue', alpha=0.5))
fig.savefig(results_plots_path+optimal_threshold_throughput_figname+"",dpi=1260)
        

#SAVING PLOT
print("Saving Plots...")
for i in range(number_objects):
    fig = result_figures_list[i]
    key_yaxis = names_fixed_time[i]
    fig.savefig(results_plots_path+key_yaxis,dpi=1060)
print("Finished Saving!")

