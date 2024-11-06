import os
import torch

def get_device():
    """
    Function to return the appropriate device based on CUDA availability
    and print the device type.
    
    Returns:
    str: Device type ("cuda" or "cpu").
    """
    # Automatically set USE_CUDA based on the availability of a CUDA device
    USE_CUDA = torch.cuda.is_available()
    # Determine the device type
    device = "cuda" if USE_CUDA else "cpu"
    
    # Print the device being used
    print(f"Using device: {device}")
    
    return device
