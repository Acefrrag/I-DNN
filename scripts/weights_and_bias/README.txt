To generate the raw file WeightsandBiases.txt you need:
è
-network2.py
-trainNN (which is the top level)
-mnist.pkl.gz
-mnistZyNet.py

To generate the fixed-point representation the script genWeightsBias.py is used.
It will generate a number of files. For each neuron of the DNN there will be the bias and the weights for that neuron.
For every neuron we have two files: one for the bias and the other one for the weights which will be in number equal to the number of inputs
to that neuron.

To generate the validation data:


