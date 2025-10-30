# geogfm.inference.sliding_window — Window generator for patch traversal (Week 9).
# Tangled on 2025-10-30T16:29:24

from __future__ import annotations
import numpy as np
from typing import Iterator, Tuple

Array = np.ndarray

def window_slices(height: int, width: int, patch_size: int, stride: int) -> Iterator[Tuple[slice, slice]]:
    for r in range(0, height - patch_size + 1, stride):
        for c in range(0, width - patch_size + 1, stride):
            yield slice(r, r + patch_size), slice(c, c + patch_size)
