# Tangled on 2025-10-30T16:29:45

"""Week 2: Advanced preprocessing functions for Sentinel-2 data."""

import logging
import numpy as np
import pandas as pd
import xarray as xr
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from geogfm.c01 import load_sentinel2_bands, setup_planetary_computer_auth, search_sentinel2_scenes

# Configure logger for minimal output
logger = logging.getLogger(__name__)

def create_cloud_mask(scl_data, good_classes: List[int]) -> np.ndarray:
    """
    Create binary cloud mask from Scene Classification Layer.

    Educational note: np.isin checks if each pixel value is in our 'good' list.
    Returns True for clear pixels, False for clouds/shadows.

    Args:
        scl_data: Scene Classification Layer data (numpy array or xarray DataArray)
        good_classes: List of SCL values considered valid pixels

    Returns:
        Binary mask array (True for valid pixels)
    """
    # Handle both numpy arrays and xarray DataArrays
    if hasattr(scl_data, 'values'):
        scl_values = scl_data.values
    else:
        scl_values = scl_data

    return np.isin(scl_values, good_classes)

def apply_cloud_mask(band_data: Dict[str, Union[np.ndarray, xr.DataArray]],
                     scl_data: Union[np.ndarray, xr.DataArray],
                     good_pixel_classes: List[int],
                     target_resolution: int = 20) -> Tuple[Dict[str, xr.DataArray], float]:
    """
    Apply SCL-based cloud masking to spectral bands.

    Args:
        band_data: Dictionary of band DataArrays
        scl_data: Scene Classification Layer DataArray
        good_pixel_classes: List of SCL values considered valid
        target_resolution: Target resolution for resampling bands

    Returns:
        masked_data: Dictionary with masked bands
        valid_pixel_fraction: Fraction of valid pixels
    """
    from scipy.ndimage import zoom

    # Get SCL data and ensure it's at target resolution
    scl_array = scl_data
    if hasattr(scl_data, 'values'):
        scl_values = scl_data.values
    else:
        scl_values = scl_data

    # Create cloud mask from SCL
    good_pixels = create_cloud_mask(scl_data, good_pixel_classes)

    # Get target shape from SCL (typically 20m resolution)
    target_shape = scl_values.shape

    # Apply mask to spectral bands
    masked_data = {}
    # Map Sentinel-2 bands to readable names
    band_mapping = {'B04': 'red', 'B03': 'green', 'B02': 'blue', 'B08': 'nir'}

    for band_name in ['B04', 'B03', 'B02', 'B08']:
        if band_name in band_data:
            band_array = band_data[band_name]

            # Get band values (handle both numpy arrays and xarray DataArrays)
            if hasattr(band_array, 'values'):
                band_values = band_array.values
            else:
                band_values = band_array

            # Resample band to match SCL resolution if needed
            if band_values.shape != target_shape:
                # Calculate zoom factors for each dimension
                zoom_factors = (
                    target_shape[0] / band_values.shape[0],
                    target_shape[1] / band_values.shape[1]
                )

                # Use scipy zoom for robust resampling
                try:
                    band_values = zoom(band_values, zoom_factors, order=1)
                    logger.debug(f"Resampled {band_name} from {band_values.shape} to {target_shape}")
                except Exception as e:
                    logger.warning(f"Failed to resample {band_name}: {e}")
                    continue

            # Ensure shapes match after resampling
            if band_values.shape != target_shape:
                logger.warning(f"Shape mismatch for {band_name}: {band_values.shape} vs {target_shape}")
                continue

            # Mask invalid pixels with NaN
            masked_values = np.where(good_pixels, band_values, np.nan)

            # Use meaningful band names (red, green, blue, nir)
            readable_name = band_mapping[band_name]

            # Create DataArray with coordinates if available
            if hasattr(scl_array, 'coords') and hasattr(scl_array, 'dims'):
                masked_data[readable_name] = xr.DataArray(
                    masked_values,
                    coords=scl_array.coords,
                    dims=scl_array.dims
                )
            else:
                # Create with named dimensions for better compatibility
                dims = ['y', 'x'] if len(masked_values.shape) == 2 else ['dim_0', 'dim_1']
                masked_data[readable_name] = xr.DataArray(
                    masked_values,
                    dims=dims
                )

    # Calculate valid pixel fraction
    valid_pixel_fraction = np.sum(good_pixels) / good_pixels.size

    # Store SCL and mask for reference
    if hasattr(scl_data, 'coords') and hasattr(scl_data, 'dims'):
        masked_data['scl'] = scl_data
        masked_data['cloud_mask'] = xr.DataArray(
            good_pixels,
            coords=scl_data.coords,
            dims=scl_data.dims
        )
    else:
        # Create with named dimensions for consistency
        dims = ['y', 'x'] if len(good_pixels.shape) == 2 else ['dim_0', 'dim_1']
        masked_data['scl'] = xr.DataArray(scl_data, dims=dims)
        masked_data['cloud_mask'] = xr.DataArray(good_pixels, dims=dims)

    return masked_data, valid_pixel_fraction

def load_scene_with_cloudmask(item, target_crs: str = 'EPSG:32611',
                              target_resolution: int = 20,
                              good_pixel_classes: List[int] = [4, 5, 6],
                              subset_bbox: Optional[List[float]] = None) -> Tuple[Optional[Dict[str, xr.DataArray]], float]:
    """
    Load a Sentinel-2 scene with cloud masking applied using geogfm functions.

    Args:
        item: STAC item
        target_crs: Target coordinate reference system
        target_resolution: Target pixel size in meters
        good_pixel_classes: List of SCL values considered valid
        subset_bbox: Optional spatial subset as [west, south, east, north] in WGS84

    Returns:
        masked_data: dict with masked bands
        valid_pixel_fraction: fraction of valid pixels
    """
    try:
        # Use the tested function from geogfm.c01
        band_data = load_sentinel2_bands(
            item,
            bands=['B04', 'B03', 'B02', 'B08', 'SCL'],
            subset_bbox=subset_bbox,
            max_retries=3
        )

        if not band_data or 'SCL' not in band_data:
            logger.warning(f"No data or missing SCL for scene {item.id}")
            return None, 0

        # Apply cloud masking using SCL with target resolution
        masked_data, valid_fraction = apply_cloud_mask(
            band_data, band_data['SCL'], good_pixel_classes, target_resolution
        )

        return masked_data, valid_fraction

    except Exception as e:
        logger.error(f"Error loading scene {item.id}: {str(e)}")
        return None, 0

def process_single_scene(item, target_crs: str = 'EPSG:32611',
                         target_resolution: int = 20,
                         min_valid_fraction: float = 0.3,
                         good_pixel_classes: List[int] = [4, 5, 6],
                         subset_bbox: Optional[List[float]] = None) -> Optional[Dict]:
    """
    Process a single scene with validation.

    Args:
        item: STAC item
        target_crs: Target coordinate reference system
        target_resolution: Target pixel size in meters
        min_valid_fraction: Minimum fraction of valid pixels required
        good_pixel_classes: List of SCL values considered valid
        subset_bbox: Optional spatial subset as [west, south, east, north] in WGS84

    Returns:
        Scene data dictionary or None if invalid
    """
    data, valid_frac = load_scene_with_cloudmask(
        item, target_crs=target_crs, target_resolution=target_resolution,
        good_pixel_classes=good_pixel_classes, subset_bbox=subset_bbox
    )

    if data and valid_frac > min_valid_fraction:
        return {
            'id': item.id,
            'date': item.properties['datetime'].split('T')[0],
            'data': data,
            'valid_fraction': valid_frac,
            'item': item
        }
    else:
        logger.info(f"Skipped {item.id[:30]} (valid fraction: {valid_frac:.1%})")
        return None

def process_scene_batch(scene_items: List, max_workers: int = 4,
                        target_crs: str = 'EPSG:32611',
                        target_resolution: int = 20,
                        min_valid_fraction: float = 0.3,
                        good_pixel_classes: List[int] = [4, 5, 6],
                        subset_bbox: Optional[List[float]] = None) -> List[Dict]:
    """
    Process multiple scenes in parallel with cloud masking and reprojection.

    Args:
        scene_items: List of STAC items
        max_workers: Number of parallel workers
        target_crs: Target coordinate reference system
        target_resolution: Target resolution in meters
        min_valid_fraction: Minimum valid pixel fraction
        good_pixel_classes: List of SCL values considered valid
        subset_bbox: Optional spatial subset

    Returns:
        processed_scenes: List of processed scene data
    """
    logger.info(f"Processing {len(scene_items)} scenes with {max_workers} workers")

    # Use partial to pass additional parameters
    process_func = partial(
        process_single_scene,
        target_crs=target_crs,
        target_resolution=target_resolution,
        min_valid_fraction=min_valid_fraction,
        good_pixel_classes=good_pixel_classes,
        subset_bbox=subset_bbox
    )

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_func, scene_items))

    # Filter successful results
    processed_scenes = [result for result in results if result is not None]

    logger.info(f"Successfully processed {len(processed_scenes)} scenes")
    return processed_scenes

def create_temporal_mosaic(processed_scenes, method: str = 'median'):
    """
    Create a temporal mosaic from multiple processed scenes.

    Args:
        processed_scenes: List of processed scene dictionaries
        method: Compositing method ('median', 'mean', 'max')

    Returns:
        mosaic_data: Temporal composite as xarray Dataset
    """
    if not processed_scenes:
        logger.warning("No scenes to mosaic")
        return None

    # Group data by band
    bands = ['red', 'green', 'blue', 'nir']
    band_stacks = {}
    dates = []

    # Find minimum common shape across all scenes
    min_shape = None
    for scene in processed_scenes:
        scene_shape = scene['data']['red'].shape
        if min_shape is None:
            min_shape = scene_shape
        else:
            min_shape = tuple(min(a, b) for a, b in zip(min_shape, scene_shape))

    for band in bands:
        band_data = []
        for scene in processed_scenes:
            # Trim to common shape to handle slight size mismatches
            band_array = scene['data'][band]
            if band_array.shape != min_shape:
                band_array = band_array[:min_shape[0], :min_shape[1]]
            band_data.append(band_array)
            if band == 'red':  # Only collect dates once
                dates.append(scene['date'])

        # Stack along time dimension
        band_stack = xr.concat(band_data, dim='time')
        band_stack = band_stack.assign_coords(time=dates)

        # Apply temporal compositing
        if method == 'median':
            band_stacks[band] = band_stack.median(dim='time', skipna=True)
        elif method == 'mean':
            band_stacks[band] = band_stack.mean(dim='time', skipna=True)
        elif method == 'max':
            band_stacks[band] = band_stack.max(dim='time', skipna=True)

    # Create mosaic dataset
    mosaic_data = xr.Dataset(band_stacks)

    # Add metadata
    mosaic_data.attrs['method'] = method
    mosaic_data.attrs['n_scenes'] = len(processed_scenes)
    mosaic_data.attrs['date_range'] = f"{min(dates)} to {max(dates)}"

    logger.info(f"Mosaic created from {len(processed_scenes)} scenes using {method}")
    return mosaic_data

def build_temporal_datacube(processed_scenes, chunk_size='auto'):
    """
    Build an analysis-ready temporal data cube.

    Args:
        processed_scenes: List of processed scenes
        chunk_size: Dask chunk size for memory management

    Returns:
        datacube: xarray Dataset with time dimension
    """
    if not processed_scenes:
        return None

    # Sort scenes by date
    processed_scenes.sort(key=lambda x: x['date'])

    # Extract dates and data
    dates = [pd.to_datetime(scene['date']) for scene in processed_scenes]
    bands = ['red', 'green', 'blue', 'nir']

    # Find minimum common shape across all scenes
    min_shape = None
    for scene in processed_scenes:
        scene_shape = scene['data']['red'].shape
        if min_shape is None:
            min_shape = scene_shape
        else:
            min_shape = tuple(min(a, b) for a, b in zip(min_shape, scene_shape))

    # Build data arrays for each band
    band_cubes = {}

    for band in bands:
        # Stack all scenes for this band
        band_data = []
        for scene in processed_scenes:
            # Trim to common shape to handle slight size mismatches
            band_array = scene['data'][band]
            if band_array.shape != min_shape:
                band_array = band_array[:min_shape[0], :min_shape[1]]
            band_data.append(band_array)

        # Create temporal stack
        band_cube = xr.concat(band_data, dim='time')
        band_cube = band_cube.assign_coords(time=dates)

        # Add chunking for large datasets
        if chunk_size == 'auto':
            # Get actual dimension names from the data
            dims = band_cube.dims
            if len(dims) == 3:  # time, dim_0, dim_1 or time, y, x
                chunks = {dims[0]: 1, dims[1]: 512, dims[2]: 512}
            else:
                chunks = {}
        else:
            chunks = chunk_size

        # Only apply chunking if chunks are specified
        if chunks:
            band_cubes[band] = band_cube.chunk(chunks)
        else:
            band_cubes[band] = band_cube

    # Create dataset
    datacube = xr.Dataset(band_cubes)

    # Add derived indices
    datacube['ndvi'] = ((datacube['nir'] - datacube['red']) /
                        (datacube['nir'] + datacube['red'] + 1e-8))

    # Enhanced Vegetation Index (EVI)
    datacube['evi'] = (2.5 * (datacube['nir'] - datacube['red']) /
                       (datacube['nir'] + 6 * datacube['red'] - 7.5 * datacube['blue'] + 1))

    # Add metadata
    datacube.attrs.update({
        'title': 'Sentinel-2 Analysis-Ready Data Cube',
        'description': 'Cloud-masked, reprojected temporal stack',
        'n_scenes': len(processed_scenes),
        'time_range': f"{dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}",
        'crs': str(datacube['red'].rio.crs) if hasattr(datacube['red'], 'rio') and datacube['red'].rio.crs else 'Unknown',
        'resolution': 'Variable (depends on original scene resolution)'
    })

    logger.info(f"Data cube created: {datacube['red'].shape}, {len(dates)} time steps")
    return datacube

class Sentinel2Preprocessor:
    """
    Scalable Sentinel-2 preprocessing pipeline using geogfm functions.
    """

    def __init__(self, output_dir: str = "preprocessed_data", target_crs: str = 'EPSG:32611',
                 target_resolution: int = 20, max_cloud_cover: float = 15,
                 good_pixel_classes: List[int] = [4, 5, 6]):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.target_crs = target_crs
        self.target_resolution = target_resolution
        self.max_cloud_cover = max_cloud_cover
        self.good_pixel_classes = good_pixel_classes

        # Set up authentication once during initialization
        setup_planetary_computer_auth()

    def search_scenes(self, bbox: List[float], start_date: str, end_date: str,
                      limit: int = 100) -> List:
        """Search for Sentinel-2 scenes using geogfm standardized function."""
        # Ensure authentication is set up
        setup_planetary_computer_auth()

        # Use our standardized search function
        date_range = f"{start_date}/{end_date}"
        items = search_sentinel2_scenes(
            bbox=bbox,
            date_range=date_range,
            cloud_cover_max=self.max_cloud_cover,
            limit=limit
        )

        logger.info(f"Found {len(items)} scenes")
        return items

    def process_scene(self, item, save_individual: bool = True, subset_bbox: Optional[List[float]] = None) -> Optional[Dict]:
        """Process a single scene with cloud masking using geogfm functions."""
        scene_id = item.id
        output_path = self.output_dir / f"{scene_id}_processed.nc"

        # Skip if already processed
        if output_path.exists():
            if save_individual:
                return str(output_path)
            else:
                # Load existing data for in-memory processing
                return xr.open_dataset(output_path)

        # Process scene using our enhanced function
        data, valid_frac = load_scene_with_cloudmask(
            item, self.target_crs, self.target_resolution, self.good_pixel_classes, subset_bbox
        )

        if data and valid_frac > 0.3:
            if save_individual:
                try:
                    # Convert to xarray Dataset
                    scene_ds = xr.Dataset(data)
                    scene_ds.attrs.update({
                        'scene_id': scene_id,
                        'date': item.properties['datetime'].split('T')[0],
                        'cloud_cover': item.properties.get('eo:cloud_cover', 0),
                        'valid_pixel_fraction': valid_frac,
                        'processing_crs': self.target_crs,
                        'processing_resolution': self.target_resolution
                    })

                    # Save to NetCDF using scipy engine (no netcdf4 required)
                    scene_ds.to_netcdf(output_path, engine='scipy')
                except Exception as e:
                    logger.error(f"Save error for {scene_id}: {str(e)[:50]}")

            return data
        else:
            logger.info(f"Skipped {scene_id} (valid fraction: {valid_frac:.1%})")
            return None

    def create_time_series_cube(self, processed_data_list, cube_name: str = "datacube"):
        """Create and save temporal data cube."""
        if not processed_data_list:
            logger.warning("No data to create cube")
            return None

        cube_path = self.output_dir / f"{cube_name}.nc"

        # Build temporal stack
        dates = []
        band_stacks = {band: [] for band in ['red', 'green', 'blue', 'nir']}

        for data in processed_data_list:
            if data:
                # Handle dictionary format, string file path, or xarray Dataset
                if isinstance(data, dict):
                    # Dictionary format from fresh processing
                    for band in band_stacks.keys():
                        if band in data:
                            band_stacks[band].append(data[band])
                elif isinstance(data, str):
                    # File path - load the file first
                    loaded_ds = xr.open_dataset(data)
                    for band in band_stacks.keys():
                        if band in loaded_ds.data_vars:
                            band_data = loaded_ds[band]
                            if 'time' in band_data.dims and band_data.dims['time'] > 1:
                                band_data = band_data.isel(time=0)
                            elif 'time' in band_data.dims:
                                band_data = band_data.squeeze('time')
                            band_stacks[band].append(band_data)
                else:
                    # xarray Dataset from loaded file - extract individual bands
                    for band in band_stacks.keys():
                        if band in data.data_vars:
                            # If the loaded data has a time dimension, select the first time slice
                            band_data = data[band]
                            if 'time' in band_data.dims and band_data.dims['time'] > 1:
                                # Multiple time slices in saved file - take first one
                                band_data = band_data.isel(time=0)
                            elif 'time' in band_data.dims:
                                # Single time slice - remove time dimension
                                band_data = band_data.squeeze('time')

                            band_stacks[band].append(band_data)

        # Create dataset
        cube_data = {}

        for band, stack in band_stacks.items():
            if stack:
                # Check that all scenes have this band
                if len(stack) == len(processed_data_list):
                    try:
                        cube_data[band] = xr.concat(stack, dim='time')
                    except Exception as e:
                        logger.error(f"Failed to concatenate {band}: {e}")
                else:
                    logger.warning(f"{band} missing from some scenes ({len(stack)}/{len(processed_data_list)})")

        if cube_data:
            try:
                datacube = xr.Dataset(cube_data)
            except Exception as e:
                logger.error(f"Failed to create dataset: {e}")
                return None

            # Add vegetation indices
            datacube['ndvi'] = ((datacube['nir'] - datacube['red']) /
                                (datacube['nir'] + datacube['red'] + 1e-8))

            # Save cube using scipy engine (no netcdf4 required)
            try:
                datacube.to_netcdf(cube_path, engine='scipy')
            except Exception:
                zarr_path = cube_path.with_suffix('.zarr')
                datacube.to_zarr(zarr_path)

            logger.info(f"Data cube saved: {cube_path}")
            return datacube

        return None
