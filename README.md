# I-DNN
Intermittent Deep Neural Network exploiting NORM Framework


## Bugs

If the NV_REG_DELAY  (within COMMON_PACKAGE.vhd) is set to:

'''
constant FRAM_MAX_DELAY_NS                  : INTEGER := MASTER_CLK_PERIOD_NS*2;
'''

the recovery of the state produces a fatal error. In particular the addra, used to access the volatile registers of the I-layer
goes beyond the maximum admissible value (31 (the volatile registers are 32 in total)).
