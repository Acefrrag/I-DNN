import mnist_loader
import network2
import json

#Loading the data and dividind the dataset between training and validation data.
training_data, validation_data, test_data = mnist_loader.load_data_wrapper()
#Creating the layers of the DNN. The layers' neuron number are enumerated. starting from
#the input layer until the output layer.
net = network2.Network([784, 30, 20, 10])#change the number of layers or number of neurons in each layer here
#Validation Data Creatiion
validation_data = list(validation_data)
#Training Data Creation
training_data = list(training_data)
#Computing the weights and bias for every neuron.
#Input format: training data, number of iterations, ..., Learning Rate
net.SGD(training_data, 30, 10, 0.1, lmbda=5.0,evaluation_data=validation_data, monitor_evaluation_accuracy=True)
#Saving the weights and biases in a file.
net.save("WeightsAndBiases.txt")

#GENERATING I-DNN.vhd
