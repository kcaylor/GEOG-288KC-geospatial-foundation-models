# Tangled on 2025-10-30T16:29:49

"""Week 1: Core Tools and Data Access functions for geospatial AI."""

import sys
import importlib.metadata
import warnings
import os
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path
import time
import logging

# Core geospatial libraries
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
import numpy as np
import pandas as pd

#Include matplotlib for plt use.
import matplotlib.pyplot as plt

from pystac_client import Client
import planetary_computer as pc


warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def configure_gdal_environment() -> dict:
    """
    Configure GDAL/PROJ environment variables for HPC and local systems.

    This function addresses common GDAL/PROJ configuration issues, particularly
    on HPC systems where proj.db may not be found or version mismatches exist.

    Returns
    -------
    dict
        Dictionary with configuration status and detected paths
    """
    config_status = {
        'gdal_configured': False,
        'proj_configured': False,
        'gdal_data_path': None,
        'proj_lib_path': None,
        'warnings': []
    }

    try:
        import osgeo
        from osgeo import gdal, osr

        # Enable GDAL exceptions for better error handling
        gdal.UseExceptions()

        # Try to find PROJ data directory
        proj_lib_candidates = [
            os.environ.get('PROJ_LIB'),
            os.environ.get('PROJ_DATA'),
            os.path.join(sys.prefix, 'share', 'proj'),
            os.path.join(sys.prefix, 'Library', 'share', 'proj'),  # Windows
            '/usr/share/proj',  # Linux system
            os.path.expanduser('~/mambaforge/share/proj'),
            os.path.expanduser('~/miniconda3/share/proj'),
            os.path.expanduser('~/anaconda3/share/proj'),
        ]

        # Find valid PROJ directory
        proj_lib_path = None
        for candidate in proj_lib_candidates:
            if candidate and os.path.isdir(candidate):
                proj_db = os.path.join(candidate, 'proj.db')
                if os.path.isfile(proj_db):
                    proj_lib_path = candidate
                    break

        if proj_lib_path:
            os.environ['PROJ_LIB'] = proj_lib_path
            os.environ['PROJ_DATA'] = proj_lib_path
            config_status['proj_lib_path'] = proj_lib_path
            config_status['proj_configured'] = True
            logger.info(f"PROJ configured: {proj_lib_path}")
        else:
            config_status['warnings'].append(
                "Could not locate proj.db - coordinate transformations may fail")

        # Try to find GDAL data directory
        gdal_data_candidates = [
            os.environ.get('GDAL_DATA'),
            gdal.GetConfigOption('GDAL_DATA'),
            os.path.join(sys.prefix, 'share', 'gdal'),
            os.path.join(sys.prefix, 'Library', 'share', 'gdal'),  # Windows
            '/usr/share/gdal',  # Linux system
        ]

        gdal_data_path = None
        for candidate in gdal_data_candidates:
            if candidate and os.path.isdir(candidate):
                gdal_data_path = candidate
                break

        if gdal_data_path:
            os.environ['GDAL_DATA'] = gdal_data_path
            gdal.SetConfigOption('GDAL_DATA', gdal_data_path)
            config_status['gdal_data_path'] = gdal_data_path
            config_status['gdal_configured'] = True
            logger.info(f"GDAL_DATA configured: {gdal_data_path}")

        # Additional GDAL configuration for network access
        gdal.SetConfigOption('GDAL_DISABLE_READDIR_ON_OPEN', 'EMPTY_DIR')
        gdal.SetConfigOption(
            'CPL_VSIL_CURL_ALLOWED_EXTENSIONS', '.tif,.tiff,.vrt')
        gdal.SetConfigOption('GDAL_HTTP_TIMEOUT', '300')
        gdal.SetConfigOption('GDAL_HTTP_MAX_RETRY', '5')

        # Test PROJ functionality
        try:
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(4326)
            config_status['proj_test_passed'] = True
        except Exception as e:
            config_status['warnings'].append(f"PROJ test failed: {str(e)}")
            config_status['proj_test_passed'] = False

        return config_status

    except Exception as e:
        logger.error(f"Error configuring GDAL environment: {e}")
        config_status['warnings'].append(f"Configuration error: {str(e)}")
        return config_status


def verify_environment(required_packages: list) -> dict:
    """
    Verify that all required packages are installed.

    Parameters
    ----------
    required_packages : list
        List of package names to verify

    Returns
    -------
    dict
        Dictionary with package names as keys and versions as values
    """
    results = {}
    missing_packages = []

    for package in required_packages:
        try:
            version = importlib.metadata.version(package)
            results[package] = version
        except importlib.metadata.PackageNotFoundError:
            missing_packages.append(package)
            results[package] = None

    # Report results
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        return results

    logger.info(f"All {len(required_packages)} packages verified")
    return results

# Configure logging for production-ready code
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def setup_planetary_computer_auth() -> bool:
    """
    Configure authentication for Microsoft Planetary Computer.

    Uses environment variables and .env files for credential discovery,
    with graceful degradation to anonymous access.

    Returns
    -------
    bool
        True if authenticated, False for anonymous access
    """
    # Try environment variables first (production)
    auth_key = os.getenv('PC_SDK_SUBSCRIPTION_KEY') or os.getenv('PLANETARY_COMPUTER_API_KEY')

    # Fallback to .env file (development)
    if not auth_key:
        env_file = Path('.env')
        if env_file.exists():
            try:
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith(('PC_SDK_SUBSCRIPTION_KEY=', 'PLANETARY_COMPUTER_API_KEY=')):
                            auth_key = line.split('=', 1)[1].strip().strip('"\'')
                            break
            except Exception:
                pass  # Continue with anonymous access

    # Configure authentication
    if auth_key and len(auth_key) > 10:
        try:
            pc.set_subscription_key(auth_key)
            logger.info("Planetary Computer authentication successful")
            return True
        except Exception as e:
            logger.warning(f"Authentication failed: {e}")

    logger.info("Using anonymous access (basic rate limits)")
    return False

def search_sentinel2_scenes(
    bbox: List[float],
    date_range: str,
    cloud_cover_max: float = 20,
    limit: int = 10
) -> List:
    """
    Search Sentinel-2 Level 2A scenes using STAC API.

    Parameters
    ----------
    bbox : List[float]
        Bounding box as [west, south, east, north] in WGS84
    date_range : str
        ISO date range: "YYYY-MM-DD/YYYY-MM-DD"
    cloud_cover_max : float
        Maximum cloud cover percentage
    limit : int
        Maximum scenes to return

    Returns
    -------
    List[pystac.Item]
        List of STAC items sorted by cloud cover (ascending)
    """
    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=pc.sign_inplace
    )

    search_params = {
        "collections": ["sentinel-2-l2a"],
        "bbox": bbox,
        "datetime": date_range,
        "query": {"eo:cloud_cover": {"lt": cloud_cover_max}},
        "limit": limit
    }

    search_results = catalog.search(**search_params)
    items = list(search_results.items())

    # Sort by cloud cover (best quality first)
    items.sort(key=lambda x: x.properties.get('eo:cloud_cover', 100))

    logger.info(f"Found {len(items)} Sentinel-2 scenes (cloud cover < {cloud_cover_max}%)")
    return items

def search_STAC_scenes(
    bbox: list,
    date_range: str,
    cloud_cover_max: float = 100.0,
    limit: int = 10,
    collection: str = "sentinel-2-l2a",
    stac_url: str = "https://planetarycomputer.microsoft.com/api/stac/v1",
    client_modifier=None,
    extra_query: dict = None
) -> list:
    """
    General-purpose function to search STAC scenes using a STAC API.

    Parameters
    ----------
    bbox : List[float]
        Bounding box as [west, south, east, north] in WGS84
    date_range : str
        ISO date range: "YYYY-MM-DD/YYYY-MM-DD"
    cloud_cover_max : float, optional
        Maximum cloud cover percentage (default: 100.0)
    limit : int, optional
        Maximum scenes to return (default: 10)
    collection : str, optional
        STAC collection name (default: "sentinel-2-l2a")
    stac_url : str, optional
        STAC API endpoint URL (default: MPC STAC)
    client_modifier : callable, optional
        Optional function to modify the STAC client (e.g., for auth)
    extra_query : dict, optional
        Additional query parameters for the search

    Returns
    -------
    List[pystac.Item]
        List of STAC items sorted by cloud cover (ascending, if available).

    Examples
    --------
    >>> # Search for Sentinel-2 scenes (default) on the Microsoft Planetary Computer (default) 
    >>> # over a bounding box in Oregon in January 2022
    >>> bbox = [-123.5, 45.0, -122.5, 46.0]
    >>> date_range = "2022-01-01/2022-01-31"
    >>> items = search_STAC_scenes(bbox, date_range, cloud_cover_max=10, limit=5)

    >>> # Search for Landsat 8 scenes from a different STAC endpoint
    >>> landsat_url = "https://earth-search.aws.element84.com/v1"
    >>> items = search_STAC_scenes(
    ...     bbox,
    ...     "2021-06-01/2021-06-30",
    ...     collection="landsat-8-c2-l2",
    ...     stac_url=landsat_url,
    ...     cloud_cover_max=20,
    ...     limit=3
    ... )

    >>> # Add an extra query to filter by platform
    >>> items = search_STAC_scenes(
    ...     bbox,
    ...     date_range,
    ...     extra_query={"platform": {"eq": "sentinel-2b"}}
    ... )
    """
    # Open the STAC client, with optional modifier (e.g., for MPC auth)
    if client_modifier is not None:
        catalog = Client.open(stac_url, modifier=client_modifier)
    else:
        catalog = Client.open(stac_url)

    # Build query parameters
    search_params = {
        "collections": [collection],
        "bbox": bbox,
        "datetime": date_range,
        "limit": limit
    }

    # Add cloud cover filter if present
    if cloud_cover_max < 100.0:
        search_params["query"] = {"eo:cloud_cover": {"lt": cloud_cover_max}}
    if extra_query:
        # Merge extra_query into search_params['query']
        if "query" not in search_params:
            search_params["query"] = {}
        search_params["query"].update(extra_query)

    search_results = catalog.search(**search_params)
    items = list(search_results.items())

    # Sort by cloud cover if available
    items.sort(key=lambda x: x.properties.get('eo:cloud_cover', 100))

    logger.info(
        f"Found {len(items)} scenes in collection '{collection}' (cloud cover < {cloud_cover_max}%)"
    )
    return items

def load_sentinel2_bands(
    item,
    bands: List[str] = ['B04', 'B03', 'B02', 'B08'],
    subset_bbox: Optional[List[float]] = None,
    max_retries: int = 3
) -> Dict[str, Union[np.ndarray, str]]:
    """
    Load Sentinel-2 bands with optional spatial subsetting.

    Parameters
    ----------
    item : pystac.Item
        STAC item representing the satellite scene
    bands : List[str]
        Spectral bands to load
    subset_bbox : Optional[List[float]]
        Spatial subset as [west, south, east, north] in WGS84
    max_retries : int
        Number of retry attempts per band

    Returns
    -------
    Dict[str, Union[np.ndarray, str]]
        Band arrays plus georeferencing metadata
    """
    from rasterio.windows import from_bounds
    from rasterio.warp import transform_bounds

    band_data = {}
    successful_bands = []
    failed_bands = []

    for band_name in bands:
        if band_name not in item.assets:
            failed_bands.append(band_name)
            continue

        asset_url = item.assets[band_name].href

        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                # URL signing for authenticated access
                signed_url = pc.sign(asset_url)

                # Memory-efficient loading with rasterio
                with rasterio.open(signed_url) as src:
                    # Validate data source
                    if src.width == 0 or src.height == 0:
                        raise ValueError(f"Invalid raster dimensions: {src.width}x{src.height}")

                    if subset_bbox:
                        # Intelligent subsetting with CRS transformation
                        try:
                            # Transform bbox to source CRS if needed
                            if src.crs != rasterio.crs.CRS.from_epsg(4326):
                                subset_bbox_src_crs = transform_bounds(
                                    rasterio.crs.CRS.from_epsg(4326), src.crs, *subset_bbox
                                )
                            else:
                                subset_bbox_src_crs = subset_bbox

                            # Calculate reading window
                            window = from_bounds(*subset_bbox_src_crs, src.transform)

                            # Ensure window is within raster bounds
                            window = window.intersection(
                                rasterio.windows.Window(0, 0, src.width, src.height)
                            )

                            if window.width > 0 and window.height > 0:
                                data = src.read(1, window=window)
                                transform = src.window_transform(window)
                                bounds = rasterio.windows.bounds(window, src.transform)
                                if src.crs != rasterio.crs.CRS.from_epsg(4326):
                                    bounds = transform_bounds(src.crs, rasterio.crs.CRS.from_epsg(4326), *bounds)
                            else:
                                # Fall back to full scene
                                data = src.read(1)
                                transform = src.transform
                                bounds = src.bounds
                        except Exception:
                            # Fall back to full scene on subset error
                            data = src.read(1)
                            transform = src.transform
                            bounds = src.bounds
                    else:
                        # Load full scene
                        data = src.read(1)
                        transform = src.transform
                        bounds = src.bounds

                    if data.size == 0:
                        raise ValueError("Loaded data has zero size")

                    # Store band data and metadata
                    band_data[band_name] = data
                    if 'transform' not in band_data:
                        band_data.update({
                            'transform': transform,
                            'crs': src.crs,
                            'bounds': bounds,
                            'scene_id': item.id,
                            'date': item.properties['datetime'].split('T')[0]
                        })

                    successful_bands.append(band_name)
                    break

            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    failed_bands.append(band_name)
                    logger.warning(f"Failed to load band {band_name}: {str(e)[:50]}")
                    break

    # Validate results
    if len(successful_bands) == 0:
        raise Exception(f"Failed to load any bands from scene {item.id}")

    if failed_bands:
        logger.warning(f"Failed to load {len(failed_bands)} bands: {failed_bands}")

    logger.info(f"Successfully loaded {len(successful_bands)} bands: {successful_bands}")
    return band_data

def get_subset_from_scene(
    item,
    x_range: Tuple[float, float] = (25, 75),
    y_range: Tuple[float, float] = (25, 75),
) -> List[float]:
    """
    Intelligent spatial subsetting using percentage-based coordinates.

    This approach provides several advantages:
    1. Resolution Independence: Works regardless of scene size or pixel resolution
    2. Reproducibility: Same percentage always gives same relative location
    3. Scalability: Easy to create systematic grids for batch processing
    4. Adaptability: Can adjust subset size based on scene characteristics

    Parameters
    ----------
    item : pystac.Item
        STAC item containing scene geometry
    x_range : Tuple[float, float]
        Longitude percentage range (0-100)
    y_range : Tuple[float, float]
        Latitude percentage range (0-100)

    Returns
    -------
    List[float]
        Subset bounding box [west, south, east, north] in WGS84

    Design Pattern: Template Method with Spatial Reasoning
    - Provides consistent interface for varied spatial operations
    - Encapsulates coordinate system complexity
    - Enables systematic spatial sampling strategies
    """
    # Extract scene geometry from STAC metadata
    scene_bbox = item.bbox  # [west, south, east, north]

    # Input validation for percentage ranges
    if not (0 <= x_range[0] < x_range[1] <= 100):
        raise ValueError(
            f"Invalid x_range: {x_range}. Must be (min, max) with 0 <= min < max <= 100"
        )
    if not (0 <= y_range[0] < y_range[1] <= 100):
        raise ValueError(
            f"Invalid y_range: {y_range}. Must be (min, max) with 0 <= min < max <= 100"
        )

    # Calculate scene dimensions in geographic coordinates
    scene_width = scene_bbox[2] - scene_bbox[0]  # east - west
    scene_height = scene_bbox[3] - scene_bbox[1]  # north - south

    # Convert percentages to geographic coordinates
    west = scene_bbox[0] + (x_range[0] / 100.0) * scene_width
    east = scene_bbox[0] + (x_range[1] / 100.0) * scene_width
    south = scene_bbox[1] + (y_range[0] / 100.0) * scene_height
    north = scene_bbox[1] + (y_range[1] / 100.0) * scene_height

    subset_bbox = [west, south, east, north]

    return subset_bbox

def get_scene_info(item):
    """
    Extract comprehensive scene characteristics for adaptive processing.

    Parameters
    ----------
    item : pystac.Item
        STAC item to analyze

    Returns
    -------
    Dict
        Scene characteristics including dimensions and geographic metrics

    Design Pattern: Information Expert
    - Centralizes scene analysis logic
    - Provides basis for adaptive processing decisions
    - Enables consistent scene characterization across workflows
    """
    bbox = item.bbox
    width_deg = bbox[2] - bbox[0]
    height_deg = bbox[3] - bbox[1]

    # Approximate conversion to kilometers (suitable for most latitudes)
    center_lat = (bbox[1] + bbox[3]) / 2
    width_km = width_deg * 111 * np.cos(np.radians(center_lat))
    height_km = height_deg * 111

    info = {
        "scene_id": item.id,
        "date": item.properties["datetime"].split("T")[0],
        "bbox": bbox,
        "width_deg": width_deg,
        "height_deg": height_deg,
        "width_km": width_km,
        "height_km": height_km,
        "area_km2": width_km * height_km,
        "center_lat": center_lat,
        "center_lon": (bbox[0] + bbox[2]) / 2,
    }

    return info

def normalize_band(
    band: np.ndarray, percentiles: Tuple[float, float] = (2, 98), clip: bool = True
) -> np.ndarray:
    """
    Percentile-based radiometric enhancement for optimal visualization.

    This normalization approach addresses several challenges:
    1. Dynamic Range: Raw satellite data often has poor contrast
    2. Outlier Robustness: Percentiles ignore extreme values
    3. Visual Optimization: Results in pleasing, interpretable images
    4. Statistical Validity: Preserves relative data relationships

    Parameters
    ----------
    band : np.ndarray
        Raw satellite band values
    percentiles : Tuple[float, float]
        Lower and upper percentiles for stretching
    clip : bool
        Whether to clip values to [0, 1] range

    Returns
    -------
    np.ndarray
        Normalized band values optimized for visualization

    Design Pattern: Strategy Pattern for Enhancement
    - Encapsulates different enhancement algorithms
    - Provides consistent interface for various normalization strategies
    - Handles edge cases (NaN, infinite values) robustly
    """
    # Handle NaN and infinite values robustly
    valid_mask = np.isfinite(band)
    if not np.any(valid_mask):
        return np.zeros_like(band)

    # Calculate percentiles on valid data only
    p_low, p_high = np.percentile(band[valid_mask], percentiles)

    # Avoid division by zero
    if p_high == p_low:
        return np.zeros_like(band)

    # Linear stretch based on percentiles
    normalized = (band - p_low) / (p_high - p_low)

    # Optional clipping to [0, 1] range
    if clip:
        normalized = np.clip(normalized, 0, 1)

    return normalized

def create_rgb_composite(
    red: np.ndarray, green: np.ndarray, blue: np.ndarray, enhance: bool = True
) -> np.ndarray:
    """
    Create publication-quality RGB composite images.

    Parameters
    ----------
    red, green, blue : np.ndarray
        Individual spectral bands
    enhance : bool
        Apply automatic contrast enhancement

    Returns
    -------
    np.ndarray
        RGB composite with shape (height, width, 3)

    Design Pattern: Composite Pattern for Multi-band Operations
    - Combines multiple bands into unified representation
    - Applies consistent enhancement across all channels
    - Produces standard format for visualization libraries
    """
    # Apply enhancement to each channel
    if enhance:
        red_norm = normalize_band(red)
        green_norm = normalize_band(green)
        blue_norm = normalize_band(blue)
    else:
        # Simple linear scaling
        red_norm = red / np.max(red) if np.max(red) > 0 else red
        green_norm = green / np.max(green) if np.max(green) > 0 else green
        blue_norm = blue / np.max(blue) if np.max(blue) > 0 else blue

    # Stack into RGB composite
    rgb_composite = np.dstack([red_norm, green_norm, blue_norm])

    return rgb_composite

def calculate_ndvi(
    nir: np.ndarray, red: np.ndarray, epsilon: float = 1e-8
) -> np.ndarray:
    """
    Calculate Normalized Difference Vegetation Index with robust error handling.

    NDVI = (NIR - Red) / (NIR + Red)

    NDVI is fundamental to vegetation monitoring because:
    1. Physical Basis: Reflects chlorophyll absorption and cellular structure
    2. Standardization: Normalized to [-1, 1] range for comparison
    3. Temporal Stability: Enables change detection across seasons/years
    4. Ecological Meaning: Strong correlation with biomass and health

    Parameters
    ----------
    nir : np.ndarray
        Near-infrared reflectance (Band 8: 842nm)
    red : np.ndarray
        Red reflectance (Band 4: 665nm)
    epsilon : float
        Numerical stability constant

    Returns
    -------
    np.ndarray
        NDVI values in range [-1, 1]

    Design Pattern: Domain-Specific Language for Spectral Indices
    - Encapsulates spectral physics knowledge
    - Provides numerical stability for edge cases
    - Enables consistent index calculation across projects
    """
    # Convert to float for numerical precision
    nir_float = nir.astype(np.float32)
    red_float = red.astype(np.float32)

    # Calculate NDVI with numerical stability
    numerator = nir_float - red_float
    denominator = nir_float + red_float + epsilon

    ndvi = numerator / denominator

    # Handle edge cases (both bands zero, etc.)
    ndvi = np.where(np.isfinite(ndvi), ndvi, 0)

    return ndvi

def calculate_band_statistics(band: np.ndarray, name: str = "Band") -> Dict:
    """
    Comprehensive statistical characterization of satellite bands.

    Parameters
    ----------
    band : np.ndarray
        Input band array
    name : str
        Descriptive name for reporting

    Returns
    -------
    Dict
        Complete statistical summary including percentiles and counts

    Design Pattern: Observer Pattern for Data Quality Assessment
    - Provides standardized quality metrics
    - Enables data validation and quality control
    - Supports automated quality assessment workflows
    """
    valid_mask = np.isfinite(band)
    valid_data = band[valid_mask]

    if len(valid_data) == 0:
        return {
            "name": name,
            "min": np.nan,
            "max": np.nan,
            "mean": np.nan,
            "std": np.nan,
            "median": np.nan,
            "valid_pixels": 0,
            "total_pixels": band.size,
        }

    stats = {
        "name": name,
        "min": float(np.min(valid_data)),
        "max": float(np.max(valid_data)),
        "mean": float(np.mean(valid_data)),
        "std": float(np.std(valid_data)),
        "median": float(np.median(valid_data)),
        "valid_pixels": int(np.sum(valid_mask)),
        "total_pixels": int(band.size),
        "percentiles": {
            "p25": float(np.percentile(valid_data, 25)),
            "p75": float(np.percentile(valid_data, 75)),
            "p95": float(np.percentile(valid_data, 95)),
        },
    }

    return stats

def plot_band_comparison(
    bands: Dict[str, np.ndarray],
    rgb: Optional[np.ndarray] = None,
    ndvi: Optional[np.ndarray] = None,
    title: str = "Multi-band Analysis",
) -> None:
    """
    Create comprehensive multi-panel visualization for satellite analysis.

    This function demonstrates several visualization principles:
    1. Adaptive Layout: Automatically adjusts grid based on available data
    2. Consistent Scaling: Uniform treatment of individual bands
    3. Specialized Colormaps: Scientific colormaps for different data types
    4. Context Information: Titles, colorbars, and interpretive text

    Parameters
    ----------
    bands : Dict[str, np.ndarray]
        Individual spectral bands to visualize
    rgb : Optional[np.ndarray]
        True color composite for context
    ndvi : Optional[np.ndarray]
        Vegetation index with specialized colormap
    title : str
        Overall figure title

    Design Pattern: Facade Pattern for Complex Visualizations
    - Simplifies complex matplotlib operations
    - Provides consistent visualization interface
    - Handles layout complexity automatically
    """
    # Calculate layout
    n_panels = (
        len(bands) + (1 if rgb is not None else 0) + (1 if ndvi is not None else 0)
    )
    n_cols = min(3, n_panels)
    n_rows = (n_panels + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5 * n_cols, 4 * n_rows))
    if n_panels == 1:
        axes = [axes]
    elif n_rows > 1:
        axes = axes.flatten()

    panel_idx = 0

    # RGB composite
    if rgb is not None:
        axes[panel_idx].imshow(rgb)
        axes[panel_idx].set_title("RGB Composite", fontweight="bold")
        axes[panel_idx].axis("off")
        panel_idx += 1

    # Individual bands
    for band_name, band_data in bands.items():
        if panel_idx < len(axes):
            normalized = normalize_band(band_data)
            axes[panel_idx].imshow(normalized, cmap="gray", vmin=0, vmax=1)
            axes[panel_idx].set_title(f"Band: {band_name}", fontweight="bold")
            axes[panel_idx].axis("off")
            panel_idx += 1

    # NDVI with colorbar
    if ndvi is not None and panel_idx < len(axes):
        im = axes[panel_idx].imshow(ndvi, cmap="RdYlGn", vmin=-0.5, vmax=1.0)
        axes[panel_idx].set_title("NDVI", fontweight="bold")
        axes[panel_idx].axis("off")

        cbar = plt.colorbar(im, ax=axes[panel_idx], shrink=0.6)
        cbar.set_label("NDVI Value", rotation=270, labelpad=15)
        panel_idx += 1

    # Hide unused panels
    for idx in range(panel_idx, len(axes)):
        axes[idx].axis("off")

    plt.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()

def save_geotiff(
    data: np.ndarray,
    output_path: Union[str, Path],
    transform,
    crs,
    band_names: Optional[List[str]] = None,
) -> None:
    """
    Export georeferenced data using industry-standard GeoTIFF format.

    This function embodies several geospatial best practices:
    1. Standards Compliance: Uses OGC-compliant GeoTIFF format
    2. Metadata Preservation: Maintains CRS and transform information
    3. Compression: Applies lossless compression for efficiency
    4. Band Description: Documents spectral band information

    Parameters
    ----------
    data : np.ndarray
        Data array (2D for single band, 3D for multi-band)
    output_path : Union[str, Path]
        Output file path
    transform : rasterio.transform.Affine
        Geospatial transform matrix
    crs : rasterio.crs.CRS
        Coordinate reference system
    band_names : Optional[List[str]]
        Descriptive names for each band

    Design Pattern: Builder Pattern for Geospatial Data Export
    - Constructs complex geospatial files incrementally
    - Ensures all required metadata is preserved
    - Provides extensible framework for additional metadata
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle both 2D and 3D arrays
    if data.ndim == 2:
        count = 1
        height, width = data.shape
    else:
        count, height, width = data.shape

    # Write GeoTIFF with comprehensive metadata
    with rasterio.open(
        output_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=count,
        dtype=data.dtype,
        crs=crs,
        transform=transform,
        compress="deflate",  # Lossless compression
        tiled=True,  # Cloud-optimized structure
        blockxsize=512,  # Optimize for cloud access
        blockysize=512,
    ) as dst:
        if data.ndim == 2:
            dst.write(data, 1)
            if band_names:
                dst.set_band_description(1, band_names[0])
        else:
            for i in range(count):
                dst.write(data[i], i + 1)
                if band_names and i < len(band_names):
                    dst.set_band_description(i + 1, band_names[i])

    logger = logging.getLogger(__name__)
    logger.info(f"Saved GeoTIFF: {output_path}")

def create_scene_tiles(item, tile_size: Tuple[int, int] = (3, 3)):
    """
    Create systematic spatial partitioning for parallel processing workflows.

    This tiling approach enables several advanced patterns:
    1. Parallel Processing: Independent tiles can be processed simultaneously
    2. Memory Management: Process large scenes without loading entirely
    3. Quality Control: Test processing on representative tiles first
    4. Scalability: Extend to arbitrary scene sizes and processing resources

    Parameters
    ----------
    item : pystac.Item
        STAC item to partition
    tile_size : Tuple[int, int]
        Grid dimensions (nx, ny)

    Returns
    -------
    List[Dict]
        Tile metadata with bounding boxes and processing information

    Design Pattern: Strategy Pattern for Spatial Partitioning
    - Provides flexible tiling strategies for different use cases
    - Encapsulates spatial mathematics complexity
    - Enables systematic quality control and testing
    """
    tiles = []
    nx, ny = tile_size

    scene_info = get_scene_info(item)

    logger.info(f"Creating {nx}×{ny} tile grid ({nx * ny} total tiles)")

    for i in range(nx):
        for j in range(ny):
            # Calculate percentage ranges for this tile
            x_start = (i / nx) * 100
            x_end = ((i + 1) / nx) * 100
            y_start = (j / ny) * 100
            y_end = ((j + 1) / ny) * 100

            # Generate tile bounding box
            tile_bbox = get_subset_from_scene(
                item, x_range=(x_start, x_end), y_range=(y_start, y_end)
            )

            # Package tile metadata for processing
            tile_info = {
                "tile_id": f"{i}_{j}",
                "row": j,
                "col": i,
                "bbox": tile_bbox,
                "x_range": (x_start, x_end),
                "y_range": (y_start, y_end),
                "area_percent": ((x_end - x_start) * (y_end - y_start)) / 100.0,
                "processing_priority": "high"
                if (i == nx // 2 and j == ny // 2)
                else "normal",  # Center tile first
            }

            tiles.append(tile_info)

    return tiles

def test_subset_functionality(item):
    """
    Automated quality assurance for data loading pipelines.

    This testing approach demonstrates:
    1. Smoke Testing: Verify basic functionality before full processing
    2. Representative Sampling: Test with manageable data subset
    3. Error Detection: Identify issues early in processing pipeline
    4. Performance Validation: Ensure acceptable loading performance

    Parameters
    ----------
    item : pystac.Item
        STAC item to test

    Returns
    -------
    bool
        True if subset functionality is working correctly

    Design Pattern: Chain of Responsibility for Quality Assurance
    - Implements systematic testing hierarchy
    - Provides early failure detection
    - Validates core functionality before expensive operations
    """
    try:
        # Test with small central area (minimal data transfer)
        test_bbox = get_subset_from_scene(item, x_range=(40, 60), y_range=(40, 60))

        # Load minimal data for testing
        test_data = load_sentinel2_bands(
            item,
            bands=["B04"],  # Single band reduces test time
            subset_bbox=test_bbox,
            max_retries=2,
        )

        if "B04" in test_data:
            return True
        else:
            logger.error(f"Subset test failed: no data returned")
            return False

    except Exception as e:
        logger.error(f"Subset test failed: {str(e)[:50]}...")
        return False

from typing import Any


def export_analysis_results(
    output_dir: str = "week1_output",
    ndvi: Optional[np.ndarray] = None,
    rgb_composite: Optional[np.ndarray] = None,
    band_data: Optional[Dict[str, np.ndarray]] = None,
    transform: Optional[Any] = None,
    crs: Optional[Any] = None,
    scene_metadata: Optional[Dict] = None,
    ndvi_stats: Optional[Dict] = None,
    aoi_bbox: Optional[List[float]] = None,
    subset_bbox: Optional[List[float]] = None,
) -> Path:
    """Export analysis results to structured output directory.

    Args:
        output_dir: Output directory path
        ndvi: NDVI array to export
        rgb_composite: RGB composite array to export
        band_data: Dictionary of band arrays to cache
        transform: Geospatial transform
        crs: Coordinate reference system
        scene_metadata: Scene metadata dictionary
        ndvi_stats: NDVI statistics dictionary
        aoi_bbox: Area of interest bounding box
        subset_bbox: Subset bounding box

    Returns:
        Path to output directory
    """
    from pathlib import Path
    import json
    from datetime import datetime

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    cache_dir = output_path / "cache"
    cache_dir.mkdir(exist_ok=True)

    # Export NDVI if available
    if ndvi is not None and transform is not None and crs is not None:
        ndvi_path = output_path / "ndvi.tif"
        save_geotiff(
            data=ndvi,
            output_path=ndvi_path,
            transform=transform,
            crs=crs,
            band_names=["NDVI"],
        )
        logger.debug(f"Exported NDVI to {ndvi_path.name}")

    # Export RGB composite if available
    if rgb_composite is not None and transform is not None and crs is not None:
        rgb_bands = np.transpose(rgb_composite, (2, 0, 1))  # HWC to CHW
        rgb_path = output_path / "rgb_composite.tif"
        save_geotiff(
            data=rgb_bands,
            output_path=rgb_path,
            transform=transform,
            crs=crs,
            band_names=["Red", "Green", "Blue"],
        )
        logger.debug(f"Exported RGB composite to {rgb_path.name}")

    # Cache individual bands
    if band_data:
        cached_bands = []
        for band_name, band_array in band_data.items():
            if band_name.startswith("B") and isinstance(band_array, np.ndarray):
                band_path = cache_dir / f"{band_name}.npy"
                np.save(band_path, band_array)
                cached_bands.append(band_name)
        logger.debug(f"Cached {len(cached_bands)} bands: {cached_bands}")

    # Create metadata
    metadata = {
        "processing_date": datetime.now().isoformat(),
        "aoi_bbox": aoi_bbox,
        "subset_bbox": subset_bbox,
    }

    if scene_metadata:
        metadata["scene"] = scene_metadata
    if ndvi_stats:
        metadata["ndvi_statistics"] = ndvi_stats

    # Save metadata
    metadata_path = output_path / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    logger.info(f"Analysis results exported to: {output_path.absolute()}")
    return output_path

def load_week1_data(output_dir: str = "week1_output") -> Dict[str, Any]:
    """Load processed data from Week 1."""
    from pathlib import Path
    import json
    import numpy as np
    import rasterio

    output_path = Path(output_dir)
    if not output_path.exists():
        raise FileNotFoundError(f"Directory not found: {output_path}")

    data = {}

    # Load metadata
    metadata_path = output_path / "metadata.json"
    if metadata_path.exists():
        with open(metadata_path) as f:
            data["metadata"] = json.load(f)

    # Load NDVI
    ndvi_path = output_path / "ndvi.tif"
    if ndvi_path.exists():
        with rasterio.open(ndvi_path) as src:
            data["ndvi"] = src.read(1)
            data["transform"] = src.transform
            data["crs"] = src.crs

    # Load cached bands
    cache_dir = output_path / "cache"
    if cache_dir.exists():
        data["bands"] = {}
        for band_file in cache_dir.glob("*.npy"):
            band_name = band_file.stem
            data["bands"][band_name] = np.load(band_file)

    return data


# Export the analysis results
scene_meta = None
if "best_scene" in locals():
    scene_meta = {
        "id": best_scene.id,
        "date": best_scene.properties["datetime"],
        "cloud_cover": best_scene.properties["eo:cloud_cover"],
        "platform": best_scene.properties.get("platform", "Unknown"),
    }

output_dir = export_analysis_results(
    ndvi=ndvi if "ndvi" in locals() else None,
    rgb_composite=rgb_composite if "rgb_composite" in locals() else None,
    band_data=band_data if "band_data" in locals() else None,
    transform=transform if "transform" in locals() else None,
    crs=crs if "crs" in locals() else None,
    scene_metadata=scene_meta,
    ndvi_stats=ndvi_stats if "ndvi_stats" in locals() else None,
    aoi_bbox=santa_barbara_bbox if "santa_barbara_bbox" in locals() else None,
    subset_bbox=subset_bbox if "subset_bbox" in locals() else None,
)

logger.info("Data exported - use load_week1_data() to reload")
