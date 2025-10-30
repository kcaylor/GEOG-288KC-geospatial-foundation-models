# Tangled on 2025-10-30T16:29:12

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import zoom
import logging

from geogfm.c01 import setup_planetary_computer_auth, search_sentinel2_scenes, load_sentinel2_bands

logger = logging.getLogger(__name__)
setup_planetary_computer_auth()

# Select device - prefer CUDA, then CPU
# Note: MPS (Apple Silicon) has compatibility issues with TerraTorch's UperNet decoder
# (adaptive pooling operations). Use CPU for broader compatibility.
if torch.cuda.is_available():
    device = torch.device('cuda')
    logger.info(f"Using CUDA GPU: {torch.cuda.get_device_name(0)}")
else:
    device = torch.device('cpu')
    if torch.backends.mps.is_available():
        logger.info("Using CPU (MPS has compatibility issues with TerraTorch UperNet)")
    else:
        logger.info("Using CPU (no GPU acceleration available)")
