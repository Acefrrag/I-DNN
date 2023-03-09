# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 14:47:13 2023

Engineer: Michele Pio Fragasso


Description:
    --File description
"""
import sys
sys.path.insert(0,"../functions/")

import mnist_loader

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Define your dataset
class MyDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        inputs, target = self.data[index]
        inputs = torch.tensor(inputs, dtype=torch.float)
        target = torch.tensor(target, dtype=torch.float)
        return inputs, target

class FourLayerDNN(nn.Module):
    def __init__(self):
        super(FourLayerDNN, self).__init__()
        self.fc1 = nn.Linear(784, 30)
        self.fc2 = nn.Linear(30, 25)
        self.fc3 = nn.Linear(25, 15)
        self.fc4 = nn.Linear(15, 10)

    def forward(self, x):
        x = x.view(-1, 784) # Flatten input
        x = nn.functional.relu(self.fc1(x))
        x = nn.functional.relu(self.fc2(x))
        x = nn.functional.relu(self.fc3(x))
        x = nn.functional.relu(self.fc4(x))
        return x
# Define your data in a list

#Loading dataset from MNIST package
#DNN TRAINING  
training_data, validation_data, test_data = mnist_loader.load_data_wrapper()
train_data = [[data[0], [out[0] for out in data[1]]] for data in list(training_data)]
val_data = list(validation_data)
test_data = list(test_data)
test_data_pytorch = [[data[0], [1 if i==data[1] else 0 for i in range(10) ]] for data in test_data]
                 

# Instantiate your datasets and data loaders
train_dataset = MyDataset(train_data)
val_dataset = MyDataset(val_data)
test_dataset = MyDataset(test_data)

train_loader = DataLoader(train_dataset, batch_size=100, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=100, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=1, shuffle=False)


# Instantiate your model and set up the optimizer and loss function
model = FourLayerDNN()
optimizer = optim.SGD(model.parameters(), lr=0.75)
criterion = nn.MSELoss()

# Train your model using the data
num_epochs = 10
for epoch in range(num_epochs):
    running_loss = 0.0
    for i, data in enumerate(train_loader, 0):
        inputs, labels = data
        optimizer.zero_grad()
        outputs = model(inputs.float())
        loss = criterion(outputs, labels.float())
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    print('Epoch [%d], Loss: %.4f' % (epoch+1, running_loss/len(train_loader)))

print('Finished Training')

correct = 0
total = 0
with torch.no_grad():
    for data in val_loader:
        inputs, labels = data
        outputs = model(inputs)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

accuracy = 100 * correct / total
print('Accuracy of the network on the validation set: %d %%' % accuracy)