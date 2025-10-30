# geogfm.inference.tiling — Naive tiled apply and stitch-back (Week 9).
# Tangled on 2025-10-30T16:29:24

from __future__ import annotations
import numpy as np
from typing import Callable
from geogfm.inference.sliding_window import window_slices

Array = np.ndarray

def apply_tiled(model_apply: Callable[[Array], Array], image: Array, patch_size: int, stride: int) -> Array:
    """Apply a function over tiles and stitch back naively (no overlaps blending)."""
    bands, height, width = image.shape
    output = np.zeros_like(image)
    for rs, cs in window_slices(height, width, patch_size, stride):
        pred = model_apply(image[:, rs, cs])  # (C, P, P)
        output[:, rs, cs] = pred
    return output
