# -*- coding: utf-8 -*-
"""
Created on %(date)s

Engineer: Michele Pio Fragasso

Description:
This file is used to compute a generic neuron output given the neuron weights,
bias and inputs.
It uses the same format as the the hardware architecture implemented in VHDL,
that is a fixed point notation for representing the weights, input and bias. 
"""

import sys
sys.path.insert(0,"../functions/")

import DNN_tester

#Main Parameters

###Integer Part Width
neuronweight_IntWidth = 16
neuroninput_IntWidth = 16
neuronbias_IntWidth = neuronweight_IntWidth+neuroninput_IntWidth
### Neuron folder path
neuron_folder = "neuron_folder1"

neuron_ws = DNN_tester.neuron_weighted_sum(neuron_folder=neuron_folder, neuronweight_IntWidth = neuronweight_IntWidth, neuronbias_IntWidth = neuronbias_IntWidth, neuroninput_IntWidth = neuroninput_IntWidth)



# def twoscomplement(number, N):
#     """
#     This functions computes the 2s complement of an integer number with respect to N bits

#     Parameters
#     ----------
#     bitstring : integer
#         Number to be complemented w.r.t. 2^N
#     Returns
#     -------
#     2s complement of number w.r.t. N

#     """
#     twocompl = 2**N - number
#     return(twocompl)

# def bitstring_to_decimal(bitstring):
#     """
#     This function converts a string a bits into the decimal representation

#     Parameters
#     ----------
#     bitstring : string
#         String of bits, they must contain '0' or '1'

#     Returns
#     -------
#     number: integer
#         Base 10 representation of the number

#     """
#     number = 0
#     N = len(bitstring)
#     for i in range(N):
#         weight = (N-1)-i
#         bit = int(bitstring[i])
#         digit = bit*2**weight
#         number = number + digit
#     return(number)
        

# #Generating the fractional number from their bit representation
# #If the number is positive(MSbit=0), the representation corresponds to the base 2 of the number
# #If the number is negative(MSbit=1), the representation corresponds to 2's complement of the module of the number
# weights_integer_sfixed = np.zeros(number_weights, dt_int)   #integer representation of the sfixed numbers
# weights_sfixed = np.zeros(number_weights, dt_float)         #floating point representation of the weights (to easily perform operations)
# inputs_integer_sfixed = np.zeros(number_inputs, dt_int)
# inputs_sfixed = np.zeros(number_weights, dt_float)
# bias_integer_sfixed = np.zeros(1, dtint64)
# bias_sfixed = np.zeros(1, dt_float)


# for j in range(number_weights):
#     #Determining sign of the number
#     if weights_str[j][0] == '1':
#         sign = -1
#     else:
#         sign = 1;
#     #Obtaining the signed representation of the fixed number. To be given to the rig function
#     if sign == 1:
#         weights_integer_sfixed[j] = bitstring_to_decimal(weights_str[j])
#     else:
#         weights_integer_sfixed[j] = sign*twoscomplement(bitstring_to_decimal(weights_str[j]), neuronweight_Width)
#     weights_sfixed[j] = weights_integer_sfixed[j]/(2**neuronweight_FracWidth)


# for j in range(number_inputs):
#     #Determining sign of the number
#     if inputs_str[j][0] == '1':
#         sign = -1
#     else:
#         sign = 1;
#     #Obtaining the signed representation of the fixed number. To be given to the rig function
#     if sign == 1:
#         inputs_integer_sfixed[j] = bitstring_to_decimal(inputs_str[j])
#     else:
#         inputs_integer_sfixed[j] = sign*twoscomplement(bitstring_to_decimal(inputs_str[j]), neuroninput_Width)
#     inputs_sfixed[j] = inputs_integer_sfixed[j]/(2**neuroninput_FracWidth)
    
    
# if bias_str[0] == '1':
#     sign = -1
# else:
#     sign = 1
# if sign == 1:   
#     bias_integer_sfixed = bitstring_to_decimal(bias_str[0])
# else:
#     bias_integer_sfixed = sign*twoscomplement(bitstring_to_decimal(bias_str[0]), neuronbias_Width)
#     bias_sfixed = bias_integer_sfixed/(2**neuronbias_FracWidth)
      
# weighted_sum = np.dot(inputs_sfixed, weights_sfixed)+bias_sfixed
    
    


    
    
             

                



