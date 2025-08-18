# Tangled on 2025-08-18T10:12:08

# Typed configuration schemas (Week 1)
# Tangles to `geogfm/core/config.py`

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class ModelConfig:
    architecture: str = "gfm_vit"
    in_channels: int = 3
    image_size: int = 64
    patch_size: int = 16
    embed_dim: int = 128
    depth: int = 4
    num_heads: int = 4
    mlp_ratio: float = 4.0


@dataclass
class DataConfig:
    dataset: str = "stac"
    root_dir: str = "data/out"  # or a small sample dir
    split: str = "train"
    image_size: int = 64
    in_channels: int = 3
    length: int = 64  # synthetic length fallback
    num_workers: int = 0
    batch_size: int = 8
    seed: int = 42


@dataclass
class TrainConfig:
    epochs: int = 1
    batch_size: int = 8
    optimizer: Dict[str, Any] = field(
        default_factory=lambda: {"name": "adamw", "lr": 2e-4})
    device: str = "cpu"
