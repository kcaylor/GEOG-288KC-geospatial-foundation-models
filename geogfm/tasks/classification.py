# geogfm.tasks.classification — Simple classification head (Week 8).
# Tangled on 2025-10-30T16:29:25

from __future__ import annotations
import torch
import torch.nn as nn

class ClassificationHead(nn.Module):
    def __init__(self, embed_dim: int, num_classes: int):
        super().__init__()
        self.fc = nn.Linear(embed_dim, num_classes)

    def forward(self, tokens: torch.Tensor) -> torch.Tensor:
        # tokens: (B, N, D). Use mean pooling over tokens.
        x = tokens.mean(dim=1)
        return self.fc(x)
