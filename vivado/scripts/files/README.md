# Folder description:

## Input_file

This folder contains the input training files (training_files.txt) used to reconfigure the I-DNN.
It is used by "trainNN.py" reconfiguration script.

## MNIST_package

This folder contains the MNIST sample of the handwritten number recognition files.
It is used by the "trainNN.py" reconfiguration script

## voltage_traces

This folder contains the raw voltage_traces collected in the PERSIST LAB @ Clemson University.

They are used by "VoltageTrace_file_generation.py" to generate VHDL compatible voltage traces
which are reproduced in simulation by IE (Intermittency Emulator).

## weights_n_biases

Folder containing the DNN models, VHDL compatible data and entities.

These files are produced by the "trainNN.py" script.


For more information read the documentation within the python scripts.

