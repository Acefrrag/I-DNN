# -*- coding: utf-8 -*-
"""
Created on Mon Dec 26 20:11:38 2022

Engineer: Michele Pio Fragasso


Description:
    --This file is used to generate the binary handwritten image
    --dataWidth is always 32 bits
    --IntSize equals the neuron input/output Integer size resulting from the
    --the DNN training.
    --To retrieve this, check the bias Integer Size in the file dataFormatFile.txt
    --you can find it inside 
    --training report generated by the DNN training script. 
"""

import sys
sys.path.insert(0, "../functions/")

import TestData as genData

dataWidth = 32
IntSize = 14
dataset_index = 1570

tr_d, va_d, te_data = genData.load_data()
genData.gensetofTestData(dataWidth, IntSize,10,te_data)
#genData.genTestData(dataWidth=dataWidth, IntSize=IntSize,testDataNum=dataset_index,te_d = te_data)
