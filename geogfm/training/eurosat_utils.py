# Tangled on 2025-10-30T16:29:44

import torch

def select_prithvi_bands(sample):
    """
    Select the 6 bands Prithvi was trained on from EuroSAT's 13 bands.

    Parameters
    ----------
    sample : dict
        TorchGeo sample with 'image' and 'label' keys

    Returns
    -------
    dict
        Sample with 6-band image
    """
    # EuroSAT band order: [B01, B02, B03, B04, B05, B06, B07, B08, B8A, B09, B10, B11, B12]
    # Prithvi bands: [B02, B03, B04, B08, B11, B12]
    # Indices: [1, 2, 3, 7, 11, 12]

    image = sample['image']
    selected_bands = image[[1, 2, 3, 7, 11, 12], :, :]

    return {
        'image': selected_bands,
        'label': sample['label']
    }

def normalize_prithvi(sample):
    """
    Normalize imagery for Prithvi using per-sample normalization.

    In production, you would want to use global statistics from the training set.
    For this demo, we use per-sample percentile normalization.

    Parameters
    ----------
    sample : dict
        Sample with 'image' and 'label'

    Returns
    -------
    dict
        Sample with normalized image
    """
    image = sample['image']

    # Normalize each band independently using 2nd-98th percentile
    normalized = torch.zeros_like(image)
    for c in range(image.shape[0]):
        band = image[c]
        p2, p98 = torch.quantile(band, torch.tensor([0.02, 0.98]))
        normalized[c] = torch.clamp((band - p2) / (p98 - p2 + 1e-8), 0, 1)

    return {
        'image': normalized,
        'label': sample['label']
    }
