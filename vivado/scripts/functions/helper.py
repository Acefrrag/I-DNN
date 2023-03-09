# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 18:31:25 2023

Engineer: Michele Pio Fragasso


Description:
    --File description
"""

import sys
import os

##---------------------------------------------------------------------- Functions
def cleanup ():
    operative_system = sys.platform
    if operative_system == "linux" :
        try:
            os.remove("./vivado.log")
            os.remove("./vivado.jou")
        except FileNotFoundError:
            print("\t-> files to be deleted are not found, proceeding.... \n")
    else:
        try:
            os.remove(".\\vivado.log")
            os.remove(".\\vivado.jou")
        except FileNotFoundError:
            print("\t-> files to be deleted are not found, proceeding.... \n")
##--------------------------------------------------------------------------------
    ##--------------------------------------------helper functions
def printlnres(string):
    print("puts $fp \"" + string + "\"")
def printres(string):
    print("puts -nonewline $fp \"" + string + "\"")
def printnlterminal(string):
    print("puts \"" + string + "\"")
    print("flush stdout")
    ##------------------------------------------------------------
