# Tangled on 2025-08-18T10:12:08

# DataLoader builders (Week 1)
# Tangles to `geogfm/data/loaders.py`
#| eval: false
from __future__ import annotations
from typing import Tuple
from torch.utils.data import DataLoader
from geogfm.core.config import DataConfig
from geogfm.data.datasets.stac_dataset import StacLikeDataset


def build_dataloader(cfg: DataConfig) -> Tuple[DataLoader, DataLoader]:
    train_ds = StacLikeDataset(cfg.root_dir, split="train", image_size=cfg.image_size, in_channels=cfg.in_channels, length=cfg.length, seed=cfg.seed)
    val_ds = StacLikeDataset(cfg.root_dir, split="val", image_size=cfg.image_size, in_channels=cfg.in_channels, length=max(8, cfg.length // 5), seed=cfg.seed)
    train_dl = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True, num_workers=cfg.num_workers, pin_memory=False)
    val_dl = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=cfg.num_workers, pin_memory=False)
    return train_dl, val_dl
