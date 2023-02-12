"""
network2.py
~~~~~~~~~~~~~~

An improved version of network.py, implementing the stochastic
gradient descent learning algorithm for a feedforward neural network.
Improvements include the addition of the cross-entropy cost function,
regularization, and better initialization of network weights.  Note
that I have focused on making the code simple, easily readable, and
easily modifiable.  It is not optimized, and omits many desirable
features.

Revision: Michele Pio Fragasso
Added method to compute the minimum integer part size to successfully compute
the output of the DNN without overflow.

"""

#### Libraries
# Standard library
import json
import random
import sys
import math
import Sigmoid
import misc

# Third-party libraries
import numpy as np


#### Define the quadratic and cross-entropy cost functions

class QuadraticCost(object):

    @staticmethod
    def fn(a, y):
        """Return the cost associated with an output ``a`` and desired output
        ``y``.

        """
        return 0.5*np.linalg.norm(a-y)**2

    @staticmethod
    def delta(z, a, y):
        """Return the error delta from the output layer."""
        return (a-y) * relu(z)

class CrossEntropyCost(object):

    @staticmethod
    def fn(a, y):
        """Return the cost associated with an output ``a`` and desired output
        ``y``.  Note that np.nan_to_num is used to ensure numerical
        stability.  In particular, if both ``a`` and ``y`` have a 1.0
        in the same slot, then the expression (1-y)*np.log(1-a)
        returns nan.  The np.nan_to_num ensures that that is converted
        to the correct value (0.0).

        """
        return np.sum(np.nan_to_num(-y*np.log(a)-(1-y)*np.log(1-a)))

    @staticmethod
    def delta(z, a, y):
        """
        Return the error delta from the output layer.  Note that the
        parameter ``z`` is not used by the method.  It is included in
        the method's parameters in order to make the interface
        consistent with the delta method for other cost classes.
        """
        return (a-y)


#### Main Network class
class Network(object):

    def __init__(self, sizes, act_fun_type = "ReLU", cost=CrossEntropyCost):
        """
        The list ``sizes`` contains the number of neurons in the respective
        layers of the network.  For example, if the list was [2, 3, 1]
        then it would be a three-layer network, with the first layer
        containing 2 neurons, the second layer 3 neurons, and the
        third layer 1 neuron.  The biases and weights for the network
        are initialized randomly, using
        ``self.default_weight_initializer`` (see docstring for that
        method).

        

        Parameters
        ----------
        sizes : integer
            The size of every layer of the DNN to train. It does not include
            the size of the output layer.
        cost : class, optional
            DESCRIPTION. The default is CrossEntropyCost.

        Returns
        -------
        None.

        """
        self.num_layers = len(sizes)
        self.num_hidden_layers = self.num_layers-1
        self.sizes = sizes
        self.default_weight_initializer()
        self.cost=cost
        self.act_fun_type = act_fun_type
        #Data Format Atributes
        self.neuroninputSize = 0
        self.neuroninputIntSize = 0
        self.neuroninputFracSize = 0
        self.neuronweightSize = 0
        self.neuronweightIntSize = 0
        self.neuronweightFracSize = 0
        self.sigmoidinputSize = 0
        self.sigmoidinputIntSize = 0
        self.sigmoidinputFracSize = 0

    def default_weight_initializer(self):
        """Initialize each weight using a Gaussian distribution with mean 0
        and standard deviation 1 over the square root of the number of
        weights connecting to the same neuron.  Initialize the biases
        using a Gaussian distribution with mean 0 and standard
        deviation 1.

        Note that the first layer is assumed to be an input layer, and
        by convention we won't set any biases for those neurons, since
        biases are only ever used in computing the outputs from later
        layers.

        """
        self.biases = [np.random.randn(y, 1) for y in self.sizes[1:]]
        self.weights = [np.random.randn(y, x)/np.sqrt(x)
                        for x, y in zip(self.sizes[:-1], self.sizes[1:])]

    def large_weight_initializer(self):
        """Initialize the weights using a Gaussian distribution with mean 0
        and standard deviation 1.  Initialize the biases using a
        Gaussian distribution with mean 0 and standard deviation 1.

        Note that the first layer is assumed to be an input layer, and
        by convention we won't set any biases for those neurons, since
        biases are only ever used in computing the outputs from later
        layers.

        This weight and bias initializer uses the same approach as in
        Chapter 1, and is included for purposes of comparison.  It
        will usually be better to use the default weight initializer
        instead.

        """
        self.biases = [np.random.randn(y, 1) for y in self.sizes[1:]]
        self.weights = [np.random.randn(y, x)
                        for x, y in zip(self.sizes[:-1], self.sizes[1:])]

    def feedforward(self, a):
        """Return the output of the network if ``a`` is input."""
        for b, w in zip(self.biases, self.weights):
            if self.act_fun_type == "ReLU":
                a = relu(np.dot(w, a)+b)
            else: #Sigmoid
                a = sigmoid(np.dot(w, a)+b)
        return a

    def SGD(self, training_data, epochs, mini_batch_size, eta,
            lmbda = 0.0,
            evaluation_data=None,
            monitor_evaluation_cost=False,
            monitor_evaluation_accuracy=False,
            monitor_training_cost=False,
            monitor_training_accuracy=False):
        """
        Train the neural network using mini-batch stochastic gradient
        descent.  The ``training_data`` is a list of tuples ``(x, y)``
        representing the training inputs and the desired outputs.  The
        other non-optional parameters are self-explanatory, as is the
        regularization parameter ``lmbda``.  The method also accepts
        ``evaluation_data``, usually either the validation or test
        data.  We can monitor the cost and accuracy on either the
        evaluation data or the training data, by setting the
        appropriate flags.  The method returns a tuple containing four
        lists: the (per-epoch) costs on the evaluation data, the
        accuracies on the evaluation data, the costs on the training
        data, and the accuracies on the training data.  All values are
        evaluated at the end of each training epoch.  So, for example,
        if we train for 30 epochs, then the first element of the tuple
        will be a 30-element list containing the cost on the
        evaluation data at the end of each epoch. Note that the lists
        are empty if the corresponding flag is not set.

        Parameters
        ----------
        training_data : list
            Dataset to train the neural network
        epochs : integer
            Number of epochs for training the neural network
        mini_batch_size : TYPE
            DESCRIPTION.
        eta : float
            learning rate
        lmbda : TYPE, optional
            DESCRIPTION. The default is 0.0.
        evaluation_data : TYPE, optional
            DESCRIPTION. The default is None.
        monitor_evaluation_cost : TYPE, optional
            DESCRIPTION. The default is False.
        monitor_evaluation_accuracy : TYPE, optional
            DESCRIPTION. The default is False.
        monitor_training_cost : TYPE, optional
            DESCRIPTION. The default is False.
        monitor_training_accuracy : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        evaluation_cost : TYPE
            DESCRIPTION.
        evaluation_accuracy : TYPE
            DESCRIPTION.
        training_cost : TYPE
            DESCRIPTION.
        training_accuracy : TYPE
            DESCRIPTION.

        """
        if evaluation_data: n_data = len(evaluation_data)
        n = len(training_data)
        evaluation_cost, evaluation_accuracy = [], []
        training_cost, training_accuracy = [], []
        for j in range(epochs):
            random.shuffle(training_data)
            mini_batches = [
                training_data[k:k+mini_batch_size]
                for k in range(0, n, mini_batch_size)]
            for mini_batch in mini_batches:
                self.update_mini_batch(
                    mini_batch, eta, lmbda, len(training_data))
            print ("Epoch %s training complete" % j)
            if monitor_training_cost:
                cost = self.total_cost(training_data, lmbda)
                training_cost.append(cost)
                print ("Cost on training data: {}".format(cost))
            if monitor_training_accuracy:
                accuracy = self.accuracy(training_data, convert=True)
                training_accuracy.append(accuracy)
                print ("Accuracy on training data: {} / {}".format(
                    accuracy, n))
            if monitor_evaluation_cost:
                cost = self.total_cost(evaluation_data, lmbda, convert=True)
                evaluation_cost.append(cost)
                print ("Cost on evaluation data: {}".format(cost))
            if monitor_evaluation_accuracy:
                accuracy = self.accuracy(evaluation_data)
                evaluation_accuracy.append(accuracy)
                print ("Accuracy on evaluation data: {} / {}".format(
                    self.accuracy(evaluation_data), n_data))
            print
        return evaluation_cost, evaluation_accuracy, \
            training_cost, training_accuracy

    def update_mini_batch(self, mini_batch, eta, lmbda, n):
        """Update the network's weights and biases by applying gradient
        descent using backpropagation to a single mini batch.  The
        ``mini_batch`` is a list of tuples ``(x, y)``, ``eta`` is the
        learning rate, ``lmbda`` is the regularization parameter, and
        ``n`` is the total size of the training data set.

        """
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        for x, y in mini_batch:
            delta_nabla_b, delta_nabla_w = self.backprop(x, y)
            nabla_b = [nb+dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
            nabla_w = [nw+dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
        self.weights = [(1-eta*(lmbda/n))*w-(eta/len(mini_batch))*nw
                        for w, nw in zip(self.weights, nabla_w)]
        self.biases = [b-(eta/len(mini_batch))*nb
                       for b, nb in zip(self.biases, nabla_b)]

    def backprop(self, x, y):
        """Return a tuple ``(nabla_b, nabla_w)`` representing the
        gradient for the cost function C_x.  ``nabla_b`` and
        ``nabla_w`` are layer-by-layer lists of numpy arrays, similar
        to ``self.biases`` and ``self.weights``."""
        nabla_b = [np.zeros(b.shape) for b in self.biases]
        nabla_w = [np.zeros(w.shape) for w in self.weights]
        # feedforward
        activation = x
        activations = [x] # list to store all the activations, layer by layer
        zs = [] # list to store all the z vectors, layer by layer
        for b, w in zip(self.biases, self.weights):
            z = np.dot(w, activation)+b
            zs.append(z)
            activation = sigmoid(z)
            activations.append(activation)
        # backward pass
        delta = (self.cost).delta(zs[-1], activations[-1], y)
        nabla_b[-1] = delta
        nabla_w[-1] = np.dot(delta, activations[-2].transpose())
        # Note that the variable l in the loop below is used a little
        # differently to the notation in Chapter 2 of the book.  Here,
        # l = 1 means the last layer of neurons, l = 2 is the
        # second-last layer, and so on.  It's a renumbering of the
        # scheme in the book, used here to take advantage of the fact
        # that Python can use negative indices in lists.
        for l in range(2, self.num_layers):
            z = zs[-l]
            sp = sigmoid_prime(z)
            delta = np.dot(self.weights[-l+1].transpose(), delta) * sp
            nabla_b[-l] = delta
            nabla_w[-l] = np.dot(delta, activations[-l-1].transpose())
        return (nabla_b, nabla_w)

    def accuracy(self, data, convert=False):
        """Return the number of inputs in ``data`` for which the neural
        network outputs the correct result. The neural network's
        output is assumed to be the index of whichever neuron in the
        final layer has the highest activation.

        The flag ``convert`` should be set to False if the data set is
        validation or test data (the usual case), and to True if the
        data set is the training data. The need for this flag arises
        due to differences in the way the results ``y`` are
        represented in the different data sets.  In particular, it
        flags whether we need to convert between the different
        representations.  It may seem strange to use different
        representations for the different data sets.  Why not use the
        same representation for all three data sets?  It's done for
        efficiency reasons -- the program usually evaluates the cost
        on the training data and the accuracy on other data sets.
        These are different types of computations, and using different
        representations speeds things up.  More details on the
        representations can be found in
        mnist_loader.load_data_wrapper.

        """
        if convert:
            results = [(np.argmax(self.feedforward(x)), np.argmax(y))
                       for (x, y) in data]
        else:
            results = [(np.argmax(self.feedforward(x)), y)
                        for (x, y) in data]
        return sum(int(x == y) for (x, y) in results)

    def total_cost(self, data, lmbda, convert=False):
        """Return the total cost for the data set ``data``.  The flag
        ``convert`` should be set to False if the data set is the
        training data (the usual case), and to True if the data set is
        the validation or test data.  See comments on the similar (but
        reversed) convention for the ``accuracy`` method, above.
        """
        cost = 0.0
        for x, y in data:
            a = self.feedforward(x)
            if convert: y = vectorized_result(y)
            cost += self.cost.fn(a, y)/len(data)
        cost += 0.5*(lmbda/len(data))*sum(
            np.linalg.norm(w)**2 for w in self.weights)
        return cost

    def save(self, weights_filename):
        """Save the neural network to the file ``filename``."""
        data = {"sizes": self.sizes,
                "weights": [w.tolist() for w in self.weights],
                "biases": [b.tolist() for b in self.biases],
                "act_fun_type": self.act_fun_type,
                "cost": str(self.cost.__name__)}
        f = open(weights_filename, "w")
        json.dump(data, f)
        f.close()
        
    def compute_DataFormat(self, validation_data):
        """
        Method that computes the best size for the neuron input and weights
        to compute the DNN output without overflow.

        Returns
        -------
        neuron_input_Width : integer
            DESCRIPTION.
        neuron_input_IntWidth : integer
            DESCRIPTION.
        neuron_weight_Width : integer
            DESCRIPTION.
        neuron_weight_IntWidth : integer
            DESCRIPTION.

        """
        #Computing integer part of the weight
        max_weight = 0
        min_weight = 1000
        for w in zip(self.weights):
            w_max = np.amax(w)
            w_min = np.amin(w)
            if w_max > max_weight:
                max_weight = w_max
            if w_min < min_weight:
                min_weight = w_min
        neuron_weight_IntWidth = int(math.ceil(max(math.log(abs(max_weight),2),math.log(abs(min_weight),2))))+1#+1 is to be safer + 1 is for the sign.
        max_sum = 0
        min_sum = 1000
        #Computing integer part of the neuron input
        for dataset_index in range(len(validation_data)):
            inputs = validation_data[dataset_index][0]
            for (b, w) in zip(self.biases, self.weights):
                w_sums = np.dot(w,inputs)+b
                for sums in w_sums:
                    if sums > max_sum:
                        max_sum = sums
                    if sums < min_sum:
                        min_sum = sums
                if self.act_fun_type == "ReLU":
                    inputs = relu(w_sums)
                else:
                    inputs = sigmoid(w_sums)
        neuron_input_IntWidth = int(math.ceil(max(math.log(abs(max_sum),2),math.log(abs(min_sum),2))))+2#+ 1 is for the sign.
        
        self.neuroninputSize = 32
        self.neuroninputIntSize = neuron_input_IntWidth
        self.neuroninputFracSize = self.neuroninputSize - self.neuroninputIntSize
        self.neuronweightSize = 32
        self.neuronweightIntSize = neuron_weight_IntWidth
        self.neuronweightFracSize = self.neuronweightSize - self.neuronweightIntSize 

    def assignSigSize(self, sigmoid_inputSize, sigmoid_inputIntSize):
        self.sigmoidinputSize = sigmoid_inputSize
        self.sigmoidinputIntSize = sigmoid_inputIntSize
        self.sigmoidinputFracSize = self.sigmoidinputSize-self.sigmoidinputIntSize

    
    def generateSigmoid(self, path):
        Sigmoid.genSigContent(dest_path="../files/sigmoid/",outputdataWidth=self.neuroninputSize,outputdataIntWidth=self.neuroninputIntSize,inputSize=self.sigmoidinputSize,inputIntWidth=self.sigmoidinputIntSize)
        (sigmoid_inputSize, sigmoid_inputIntSize) = misc.sigmoid_extract_size("..\\\\files\sigmoid")
        return
#### Loading a Network
def load(filename):
    """Load a neural network from the file ``filename``.  Returns an
    instance of Network.

    """
    f = open(filename, "r")
    data = json.load(f)
    f.close()
    #getattr takes the attribute of an object. The first parameter is the object, the second attribute is the attribute name
    #sys.modules[__name__] supposedly is the 
    cost = getattr(sys.modules[__name__], data["cost"])
    act_fun_type = data["act_fun_type"]
    net = Network(data["sizes"],act_fun_type=act_fun_type,cost=cost)
    net.weights = [np.array(w) for w in data["weights"]]
    net.biases = [np.array(b) for b in data["biases"]]
    return net

#### Miscellaneous functions
def vectorized_result(j):
    """Return a 10-dimensional unit vector with a 1.0 in the j'th position
    and zeroes elsewhere.  This is used to convert a digit (0...9)
    into a corresponding desired output from the neural network.

    """
    e = np.zeros((10, 1))
    e[j] = 1.0
    return e

def sigmoid(z):
    """The sigmoid function."""
    return 1.0/(1.0+np.exp(-z))
    #return np.maximum(z,0)

def sigmoid_prime(z):
    """Derivative of the sigmoid function."""
    return sigmoid(z)*(1-sigmoid(z))
    #return 1. * (z > 0)

def relu(z):
    return(np.maximum(z,0))
