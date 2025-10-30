# Tangled on 2025-10-30T16:01:48

criterion = nn.CrossEntropyLoss()

import torch
import torch.nn as nn

def train_one_epoch(model, train_loader, criterion, optimizer, device):
    """
    Train for one epoch.

    Parameters
    ----------
    model : nn.Module
        The model to train
    train_loader : DataLoader
        Training data loader
    criterion : nn.Module
        Loss function
    optimizer : torch.optim.Optimizer
        Optimizer for parameter updates
    device : torch.device
        Device to run on

    Returns
    -------
    tuple
        (average_loss, accuracy)
    """
    model.train() # Set model to training mode

    running_loss = 0.0 # Running loss
    correct = 0 # Correct predictions
    total = 0 # Total predictions

    for images, labels in train_loader:
        # Move data to device
        images = images.to(device) # Move data to device
        labels = labels.to(device) # Move data to device

        # Zero gradients
        optimizer.zero_grad()

        # Forward pass
        outputs = model(images)

        # TerraTorch models return ModelOutput object
        # Extract the tensor
        if hasattr(outputs, 'output'):
            outputs = outputs.output # Extract tensor from ModelOutput

        # Compute loss
        loss = criterion(outputs, labels) 

        # Backward pass
        loss.backward()

        # Update parameters
        optimizer.step()

        # Track metrics
        running_loss += loss.item() # Add loss to running loss
        _, predicted = outputs.max(1) # Get predicted class
        total += labels.size(0) # Add number of labels to total
        # Add number of correct predictions to total
        correct += predicted.eq(labels).sum().item()

    epoch_loss = running_loss / len(train_loader) # Calculate average loss
    epoch_acc = correct / total # Calculate average accuracy

    return epoch_loss, epoch_acc
