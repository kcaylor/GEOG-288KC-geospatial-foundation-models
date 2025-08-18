# Tangled on 2025-08-18T10:12:08

# Channel-wise normalization utilities (Week 1)
# Tangles to `geogfm/data/transforms/normalization.py`
from __future__ import annotations
import numpy as np
from typing import Tuple, Dict, Any, Optional

Array = np.ndarray

def minmax_normalize(data: Array, global_min: Optional[Array] = None, global_max: Optional[Array] = None) -> tuple[Array, dict]:
    bands, height, width = data.shape
    normalized = np.zeros_like(data, dtype=np.float32)
    if global_min is None or global_max is None:
        mins = np.array([data[i].min() for i in range(bands)], dtype=np.float32)
        maxs = np.array([data[i].max() for i in range(bands)], dtype=np.float32)
        src = "local"
    else:
        mins, maxs, src = global_min.astype(np.float32), global_max.astype(np.float32), "global"
    for i in range(bands):
        rng = maxs[i] - mins[i]
        if rng > 0:
            normalized[i] = (data[i] - mins[i]) / rng
        else:
            normalized[i] = 0
    stats = {"source": src, "mins": mins, "maxs": maxs, "output_range": (float(normalized.min()), float(normalized.max()))}
    return normalized, stats


def zscore_normalize(data: Array, global_mean: Optional[Array] = None, global_std: Optional[Array] = None) -> tuple[Array, dict]:
    bands, height, width = data.shape
    normalized = np.zeros_like(data, dtype=np.float32)
    if global_mean is None or global_std is None:
        means = np.array([data[i].mean() for i in range(bands)], dtype=np.float32)
        stds = np.array([data[i].std() for i in range(bands)], dtype=np.float32)
        src = "local"
    else:
        means, stds, src = global_mean.astype(np.float32), global_std.astype(np.float32), "global"
    for i in range(bands):
        if stds[i] > 0:
            normalized[i] = (data[i] - means[i]) / stds[i]
        else:
            normalized[i] = 0
    stats = {"source": src, "means": means, "stds": stds, "output_mean": float(normalized.mean()), "output_std": float(normalized.std())}
    return normalized, stats
