# geogfm.interoperability.huggingface — Lightweight HF Hub helpers (Week 7).
# Tangled on 2025-10-30T16:01:30

from __future__ import annotations
from typing import Any, Dict

try:
    from huggingface_hub import hf_hub_download  # optional
except Exception:  # pragma: no cover
    hf_hub_download = None  # type: ignore


def ensure_hf_available() -> None:
    if hf_hub_download is None:
        raise ImportError("huggingface_hub is not installed in this environment")


def download_config(repo_id: str, filename: str = "config.json") -> str:
    """Download a config file from HF Hub and return local path."""
    ensure_hf_available()
    return hf_hub_download(repo_id, filename)


def download_weights(repo_id: str, filename: str = "pytorch_model.bin") -> str:
    ensure_hf_available()
    return hf_hub_download(repo_id, filename)


def load_external_model(repo_id: str, config_loader) -> Dict[str, Any]:
    """Outline for loading external model configs/weights.
    Returns a dict with paths for downstream loading.
    """
    cfg_path = download_config(repo_id)
    w_path = download_weights(repo_id)
    return {"config_path": cfg_path, "weights_path": w_path}
