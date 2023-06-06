# -*- coding: utf-8 -*-
"""
Created on Fri May  5 10:32:02 2023

Engineer: Michele Pio Fragasso


Description:
    This script computes the relu range for a full size input
    and cut off size input (due to limited output register size)
"""

import numpy as np
import matplotlib.pyplot as plt
import os


size_input = 8
frac_size_input = 5
int_size_input = size_input-frac_size_input

size_cut = 4
frac_size_cut = 2
int_size_cut = size_cut-frac_size_cut

min_input = -2**(int_size_input-1)+2**(-frac_size_input)
max_input = 2**(int_size_input-1)

min_cut = -2**(int_size_cut-1)+2**(-frac_size_cut)
max_cut = 2**(int_size_cut-1)

range_input = np.arange(min_input, max_input,  step=2**(-frac_size_input))
range_cut = np.arange(min_cut, max_cut,  step=2**(-frac_size_cut))


def relu(x):
    if x > 0:
        return(x)
    else:
        return(0)

relu_values = [relu(x) for x in range_input]
relu_values_cut = [relu(x) for x in range_cut]


fontsize=13
fig = plt.figure()
ax = fig.gca()

#Plotting full size range ReLU
ax.plot(range_input, relu_values, color="blue", label = "ReLU applied to SUM\_REG\_OUT register")
#Plotting cut-off size ReLU
ax.plot(range_cut, relu_values_cut, color="red", label = "Cut-off ReLU")
#Plottin tails of the cut-off size ReLU for presentation
zero_input_range = np.arange(min_input, 0, 2**(-frac_size_input))
zero_values = np.zeros(len(zero_input_range))
ax.plot(zero_input_range, zero_values, color = "red")
max_cut_ReLU = max(relu_values_cut)
max_cut_input_range = np.arange(max(range_cut), max_input, 2**(-frac_size_input))
max_cut_ReLU_range = np.ones(len(max_cut_input_range))*max_cut_ReLU
ax.plot(max_cut_input_range, max_cut_ReLU_range, color="red")
plt.grid(True)
plt.title("ReLU with and without overflow", fontsize = fontsize)
plt.xlabel("x", fontsize=fontsize)
plt.ylabel("ReLU(x)",fontsize=fontsize)
plt.legend()

ReLU_plot_folder ="./plots/ReLU_implemeted/"
try:
    os.mkdir(ReLU_plot_folder)
except:
    pass
plt.savefig(ReLU_plot_folder+"ReLU_implemented.svg", dpi=1080)

plt.show()






