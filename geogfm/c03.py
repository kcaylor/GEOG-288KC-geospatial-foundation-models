# Tangled on 2025-10-30T16:01:50

import matplotlib.pyplot as plt
import torch
from geogfm.c01 import load_sentinel2_bands
from scipy.ndimage import zoom
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import torch
import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import warnings

from geogfm.c02 import load_scene_with_cloudmask
from geogfm.c01 import setup_planetary_computer_auth, search_sentinel2_scenes

import logging
logger = logging.getLogger(__name__)

# Setup authentication
setup_planetary_computer_auth()

warnings.filterwarnings('ignore')

# Configure GDAL/PROJ environment before importing rasterio
proj_path = os.path.join(sys.prefix, 'share', 'proj')
if os.path.exists(proj_path):
    os.environ['PROJ_LIB'] = proj_path
    os.environ['PROJ_DATA'] = proj_path


logger.debug(f"PyTorch: {torch.__version__}")
logger.debug(f"CUDA available: {torch.cuda.is_available()}")

# Select best available device: CUDA (NVIDIA GPU) > CPU
# Note: MPS has compatibility issues with some operations (adaptive pooling)
# See: https://github.com/pytorch/pytorch/issues/96056
if torch.cuda.is_available():
    device = torch.device('cuda')
    logger.info("Using CUDA for acceleration")
else:
    device = torch.device('cpu')
    if torch.backends.mps.is_available():
        logger.info("Using CPU (MPS available but has compatibility issues with TerraTorch)")
    else:
        logger.info("Using CPU (no GPU acceleration available)")
