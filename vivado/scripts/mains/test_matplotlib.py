# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 23:04:22 2023

Engineer: Michele Pio Fragasso


Description:
    --File description
"""

import matplotlib.pyplot as plt

# sample dictionary
data = {0: [1, 2, 3, 4], 1: [2, 4, 6, 8], 2: [3, 6, 9, 12]}

# plot each set of values and save each figure
for key in data.keys():
    plt.figure() # create a new figure
    plt.plot(data[0], data[key], label="Value")
    plt.title(f"Plot of values for Value {key}")
    plt.xlabel("Abscissa values")
    plt.ylabel("Values")
    plt.legend()
    plt.savefig(f"plot_{key}.png") # save the figure to a file