import json

#Edit - Michele Pio Fragasso
#This script has been modified to be compatible to the VHDL DNN architecture.
#The bias size must be twice as the weight size ( since  it is added to the product w_i*x_i of t he weighted sum).
#Bits for numbers.
#Also in VHDL when loading lines of bits from files the number of characters
#must correspond to the size of the VHDL signal.
dataWidth = 32
#Integer part width in bits of the weights
weightIntWidth = 16
biasdataWidth = dataWidth#modified
#Bias Integer part width.
biasWidth = dataWidth#biasdataWidth=biasWidth
dataIntWidth = weightIntWidth#modified 
inputFile = "WeightsAndBiases.txt"
dataFracWidth = dataWidth-dataIntWidth
weightFracWidth = dataWidth-weightIntWidth
biasIntWidth = dataIntWidth
biasFracWidth = biasWidth-biasIntWidth
outputPath = "./w_b/"
headerPath = "./"
#The output bits are arranged from the least significant bit. The output is supposed to be padded with the remaining number of zero to the left of the sequence


#It returns the number converted as a base 10 natural number.
def DtoB(num,dataWidth,fracBits):						#funtion for converting into two's complement format
	if num >= 0:
		num = num * (2**fracBits) #Shift the number to the left by fracBits
		num = int(num)#We take only the part that can be represented with the bit we have.
		d = num
	else:
		num = -num #we make the number positive
		num = num * (2**fracBits)		#number of fractional bits shift
		num = int(num)
		if num == 0:
			d = 0
		else:
			d = 2**dataWidth - num #This will always be a natural number. Where did we put the minus bit? It's inside the operator
	return d

def genWeightsAndBias(dataWidth,weightFracWidth,biasFracWidth,inputFile):
	weightIntWidth = dataWidth-weightFracWidth
	biasIntWidth = dataWidth-biasFracWidth
	myDataFile = open(inputFile,"r")
	weightHeaderFile = open(headerPath+"weightValues.h","w")
	myData = myDataFile.read()
	myDict = json.loads(myData)
	myWeights = myDict['weights']
	myBiases = myDict['biases']
	weightHeaderFile.write("int weightValues[]={")
	for layer in range(0,len(myWeights)):
		for neuron in range(0,len(myWeights[layer])):
			fi = 'w_'+str(layer+1)+'_'+str(neuron)+'.mif'
			f = open(outputPath+fi,'w')
			for weight in range(0,len(myWeights[layer][neuron])):
				if 'e' in str(myWeights[layer][neuron][weight]):#Probably it means the number is close to 0
					p = format(0,'0'+str(dataWidth)+'b')
				else:
					if myWeights[layer][neuron][weight] > 2**(weightIntWidth-1):#positive overflow
						myWeights[layer][neuron][weight] = 2**(weightIntWidth-1)-2**(-weightFracWidth)
					elif myWeights[layer][neuron][weight] < -2**(weightIntWidth-1):#negative overflow
						myWeights[layer][neuron][weight] = -2**(weightIntWidth-1)
					wInDec = DtoB(myWeights[layer][neuron][weight],dataWidth,weightFracWidth)#conversion in corresponding integer.
					p = wInDec.__format__('0'+str(dataWidth)+'b')
				f.write(p+'\n')
				weightHeaderFile.write(str(wInDec)+',')
			f.close()
	weightHeaderFile.write('0};\n')
	weightHeaderFile.close()
	
	biasHeaderFile = open(headerPath+"biasValues.h","w")
	biasHeaderFile.write("int biasValues[]={")
	for layer in range(0,len(myBiases)):
		for neuron in range(0,len(myBiases[layer])):
			fi = 'b_'+str(layer+1)+'_'+str(neuron)+'.mif'
			p = myBiases[layer][neuron][0]
			if 'e' in str(p): #To remove very small values with exponents
				res = '0'
			else:
				if p > 2**(biasIntWidth-1):
					p = 2**(biasIntWidth-1)-2**(-biasFracWidth)
				elif p < -2**(biasIntWidth-1):
					p = -2**(biasIntWidth-1)
				bInDec = DtoB(p,dataWidth,biasFracWidth)
				res = bInDec.__format__('0'+str(biasWidth)+'b')
			f = open(outputPath+fi,'w')
			f.write(res)
			biasHeaderFile.write(str(bInDec)+',')
			f.close()
	biasHeaderFile.write('0};\n')
	biasHeaderFile.close()
			
if __name__ == "__main__":
	genWeightsAndBias(dataWidth,weightFracWidth,biasFracWidth,inputFile)