# Tangled on 2025-08-18T10:12:08

# Patch extraction utilities (Week 1)
# Tangles to `geogfm/data/transforms/patchify.py`
#| auto-imports: true
from __future__ import annotations
import numpy as np

Array = np.ndarray

def crop_to_patches(data: Array, patch_size: int, stride: int) -> Array:
    """
    Crop image to dimensions that allow complete patch extraction.

    Args:
        data: (bands, height, width) array
        patch_size: size of patches to extract
        stride: step size between patches

    Returns:
        cropped: (bands, new_height, new_width) array
    """
    bands, height, width = data.shape

    # TODO: Calculate how many complete patches fit
    patches_h = (height - patch_size) // stride + 1
    patches_w = (width - patch_size) // stride + 1

    # TODO: Calculate the required dimensions
    new_height = (patches_h - 1) * stride + patch_size
    new_width = (patches_w - 1) * stride + patch_size

    # TODO: Crop the data
    cropped = data[:, :new_height, :new_width]

    print(f"✓ Cropped from {height}×{width} to {new_height}×{new_width}")
    print(
        f"✓ Will generate {patches_h}×{patches_w} = {patches_h*patches_w} patches")

    return cropped

# Patch extraction with spatial metadata (Week 1)
# Tangles (append) to `geogfm/data/transforms/patchify.py`
#| tangle-mode: append
#| auto-import: true

def extract_patches(
    data: Array,
    patch_size: int,
    stride: int
) -> Array:
    """
    Extract patches.

    Args:
        data: (bands, height, width) normalized array
        patch_size: size of patches
        stride: step between patches

    Returns:
        patches: (n_patches, bands, patch_size, patch_size) array
    """
    bands, height, width = data.shape
    patches = []
    for r in range(0, height - patch_size + 1, stride):
        for c in range(0, width - patch_size + 1, stride):
            patches.append(data[:, r:r+patch_size, c:c+patch_size])
    return np.stack(patches, axis=0)


def extract_patches_with_metadata(
    data: Array,
    patch_size: int,
    stride: int,
    transform
) -> Tuple[Array, Array]:
    """
    Extract patches with their spatial coordinates.

    Args:
        data: (bands, height, width) normalized array
        patch_size: size of patches
        stride: step between patches
        transform: rasterio transform object

    Returns:
        patches: (n_patches, bands, patch_size, patch_size) array
        coordinates: (n_patches, 4) array of [min_x, min_y, max_x, max_y]
    """
    bands, height, width = data.shape
    patches = []
    coordinates = []

    # TODO: Iterate through patch positions
    for row in range(0, height - patch_size + 1, stride):
        for col in range(0, width - patch_size + 1, stride):
            # TODO: Extract patch from all bands
            patch = data[:, row:row+patch_size, col:col+patch_size]
            patches.append(patch)

            # TODO: Calculate real-world coordinates using transform
            min_x, max_y = transform * (col, row)  # Top-left
            max_x, min_y = transform * \
                (col + patch_size, row + patch_size)  # Bottom-right
            coordinates.append([min_x, min_y, max_x, max_y])

    patches = np.array(patches)
    coordinates = np.array(coordinates)

    print(f"✓ Extracted {len(patches)} patches")
    print(f"✓ Patch shape: {patches.shape}")
    print(f"✓ Coordinate shape: {coordinates.shape}")

    return patches, coordinates

# Reconstruction from patches (Week 1)
# Tangles (append) to `geogfm/data/transforms/patchify.py`
#| tangle-mode: append

def reconstruct_from_patches(
    patches: Array,
    height: int,
    width: int,
    patch_size: int
) -> Array:
    """
    Reassemble a (bands, H, W) image from non-overlapping square patches.

    Parameters
    ----------
    patches : Array
        Patches in row-major scan order with shape (N, bands, patch_size, patch_size),
        where N must equal (height // patch_size) * (width // patch_size).
    height : int
        Target image height in pixels.
    width : int
        Target image width in pixels.
    patch_size : int
        Size of each square patch in pixels. Assumes stride == patch_size (no overlap).

    Returns
    -------
    Array
        Reconstructed image of shape (bands, height, width).

    Notes
    -----
    - Assumes patches are laid out left-to-right, top-to-bottom (row-major).
    - Ignores any remainder if `height` or `width` is not divisible by `patch_size`
      (i.e., only the `grid_h * patch_size` by `grid_w * patch_size` area is filled).
    - No blending is performed (because there is no overlap).

    Examples
    --------
    >>> # Suppose height=width=64, patch_size=32, bands=13
    >>> # patches.shape == (4, 13, 32, 32), ordered row-major
    >>> img = reconstruct_from_patches(patches, 64, 64, 32)
    >>> img.shape
    (13, 64, 64)
    """
    bands = patches.shape[1]
    grid_h = height // patch_size
    grid_w = width // patch_size
    out = np.zeros((bands, height, width), dtype=patches.dtype)
    idx = 0
    for r in range(grid_h):
        for c in range(grid_w):
            out[:, r*patch_size:(r+1)*patch_size, c *
                patch_size:(c+1)*patch_size] = patches[idx]
            idx += 1
    return out
