# Tangled on 2025-08-18T10:12:08

# Minimal STAC-like dataset (Week 1)
# Tangles to `geogfm/data/datasets/stac_dataset.py`
#| auto-imports: true
from __future__ import annotations
from typing import List, Optional
from pathlib import Path
import random
import numpy as np
import torch
from torch.utils.data import Dataset
import rasterio as rio

class StacLikeDataset(Dataset):
    """Minimal dataset reading GeoTIFF files under a directory, or generating synthetic data.
    Returns images sized to (C, H, W) where H=W=image_size and divisible by patch size.
    """
    def __init__(self, root_dir: str, split: str = "train", image_size: int = 64, in_channels: int = 3, length: int = 64, seed: int = 42):
        self.root = Path(root_dir)
        self.split = split
        self.image_size = int(image_size)
        self.in_channels = int(in_channels)
        self.length = int(length)
        self.rng = random.Random(seed)
        self.files: List[Path] = []
        if self.root.exists():
            for p in self.root.rglob("*.tif"):
                self.files.append(p)
        if split == "val":
            self.files = self.files[::5]
        elif split == "train":
            self.files = [p for i, p in enumerate(self.files) if i % 5 != 0]

    def __len__(self) -> int:
        return max(len(self.files), self.length)

    def _load_or_synthesize(self, idx: int) -> np.ndarray:
        if self.files:
            path = self.files[idx % len(self.files)]
            with rio.open(path) as src:
                arr = src.read(out_shape=(min(self.in_channels, src.count), self.image_size, self.image_size))
                if arr.shape[0] < self.in_channels:
                    pad = np.zeros((self.in_channels - arr.shape[0], self.image_size, self.image_size), dtype=arr.dtype)
                    arr = np.concatenate([arr, pad], axis=0)
                return arr.astype(np.float32)
        # synthetic fallback
        self.rng.seed(idx)
        return np.random.rand(self.in_channels, self.image_size, self.image_size).astype(np.float32)

    def __getitem__(self, idx: int) -> torch.Tensor:
        arr = self._load_or_synthesize(idx)
        return torch.from_numpy(arr)
