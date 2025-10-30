# PROJ Database Version Mismatch - Fix Documentation

## Problem Description

When importing TorchGeo or using rasterio, you may encounter this error:

```
CRSError: The EPSG code is unknown. PROJ: proj_create_from_database:
/path/to/proj.db contains DATABASE.LAYOUT.VERSION.MINOR = 2 whereas
a number >= 6 is expected. It comes from another PROJ installation.
```

## Root Cause

This error occurs when:

1. Your conda environment has a **newer PROJ library** (e.g., PROJ 9.7) that expects database schema version 6+
2. But the system finds an **older PROJ database** (schema version 2) from a different installation
3. Even though `PROJ_DATA` environment variable is correctly set, the PROJ library may have hardcoded fallback paths to the older database

## Diagnosis

Check for multiple PROJ databases on your system:

```bash
# Find all proj.db files
find ~/mambaforge ~/miniconda3 /opt/homebrew -name "proj.db" 2>/dev/null

# Check database versions
sqlite3 /path/to/proj.db "SELECT key, value FROM metadata WHERE key LIKE 'DATABASE.LAYOUT.VERSION%';"
```

Expected output for a working database:
```
DATABASE.LAYOUT.VERSION.MAJOR|1
DATABASE.LAYOUT.VERSION.MINOR|6
```

If you find a database with `MINOR = 2`, that's the problematic old database.

## Solution

### Quick Fix

Remove or rename the old PROJ database from the base conda/mamba installation:

```bash
# For mambaforge users
mv ~/mambaforge/share/proj/proj.db ~/mambaforge/share/proj/proj.db.old

# For miniconda users
mv ~/miniconda3/share/proj/proj.db ~/miniconda3/share/proj/proj.db.old

# For Homebrew PROJ installations
mv /opt/homebrew/share/proj/proj.db /opt/homebrew/share/proj/proj.db.old
```

### Verification

After removing the old database, test that everything works:

```bash
conda activate geoAI

# Test 1: Basic PROJ functionality
python -c "from rasterio.crs import CRS; print('✓ PROJ works:', CRS.from_epsg(4326))"

# Test 2: TorchGeo import
python -c "from torchgeo.datasets import EuroSAT; print('✓ TorchGeo works!')"

# Test 3: Check database location
python -c "import os, pyproj; print('✓ Using database:', os.path.join(pyproj.datadir.get_data_dir(), 'proj.db'))"
```

All three tests should pass without errors.

### Permanent Prevention

Update your `environment.yml` to explicitly use conda-forge for geospatial packages:

```yaml
dependencies:
  # Geospatial core libraries - explicit conda-forge channel
  - conda-forge::proj>=9.7
  - conda-forge::gdal>=3.10
  - conda-forge::rasterio>=1.4
  - conda-forge::pyproj>=3.7
  - conda-forge::fiona>=1.10
  - conda-forge::geopandas>=1.1
  - conda-forge::shapely>=2.1
```

The `conda-forge::` prefix ensures all geospatial packages come from the same channel with compatible versions.

## Why This Happens

### Database Schema Evolution

PROJ database schema has evolved over time:
- **MINOR = 0**: PROJ 4.x-6.x (very old)
- **MINOR = 2**: PROJ 7.x-8.x (2019-2022)
- **MINOR = 6**: PROJ 9.x+ (2023+)

Newer PROJ libraries require newer schemas for enhanced functionality (better datum transformations, updated EPSG codes, etc.).

### Common Scenarios

1. **Multiple Conda Environments**: Base environment has old PROJ, new environment has new PROJ
2. **System vs Conda PROJ**: Homebrew/system PROJ conflicts with conda PROJ
3. **Mixed Package Sources**: Installing some packages via conda, others via pip
4. **Leftover Files**: Old PROJ installations not fully cleaned up

## Alternative Solutions

### If You Need the Base Database

If other environments need the old database, create a fresh environment instead:

```bash
# Remove old environment
conda env remove -n geoAI

# Recreate from updated environment.yml
conda env create -f environment.yml
```

### If Problems Persist

Check for environment variable conflicts:

```bash
# Check shell configuration files
grep -r "PROJ_LIB\|PROJ_DATA" ~/.zshrc ~/.bashrc ~/.bash_profile

# Remove any PROJ variables from shell configs
# They should be set automatically by conda activation scripts
```

## Technical Details

### How PROJ Finds Its Database

PROJ searches for `proj.db` in this order:

1. `PROJ_DATA` environment variable (if set)
2. Compiled-in default path (usually `/usr/local/share/proj` or similar)
3. Relative to executable location (`../share/proj`)
4. System default locations

Even with `PROJ_DATA` set correctly, step 2 can cause issues if the compiled-in path points to an old database.

### Database Schema Check

To manually verify database compatibility:

```bash
# Check schema version
sqlite3 /path/to/proj.db << EOF
SELECT key, value FROM metadata
WHERE key LIKE 'DATABASE.LAYOUT.VERSION%';
EOF

# Check EPSG version (should be recent)
sqlite3 /path/to/proj.db << EOF
SELECT key, value FROM metadata
WHERE key = 'EPSG.VERSION';
EOF
```

Modern databases should have:
- `DATABASE.LAYOUT.VERSION.MINOR >= 6`
- `EPSG.VERSION` from 2024 or later (v11.x+)

## For Course Instructors

### Student Setup

Add this check to the environment verification script:

```python
import sqlite3
import os
import pyproj

proj_data = pyproj.datadir.get_data_dir()
proj_db = os.path.join(proj_data, 'proj.db')

conn = sqlite3.connect(proj_db)
cursor = conn.cursor()
cursor.execute("SELECT value FROM metadata WHERE key = 'DATABASE.LAYOUT.VERSION.MINOR'")
minor_version = int(cursor.fetchone()[0])
conn.close()

if minor_version < 6:
    print(f"⚠️  PROJ database is outdated (schema v{minor_version})")
    print("   Run: conda remove proj && conda install -c conda-forge proj>=9.7")
else:
    print(f"✓ PROJ database is up to date (schema v{minor_version})")
```

### Prevention in Course Materials

1. **Always specify conda-forge** for geospatial packages in environment files
2. **Pin PROJ version** to >= 9.7 in `environment.yml`
3. **Include verification script** in setup instructions
4. **Document this issue** in troubleshooting guide

## References

- [PROJ Migration Guide](https://proj.org/en/latest/development/migration.html)
- [PROJ Database Schema](https://proj.org/en/latest/specifications/projjson.html)
- [Conda-Forge PROJ Package](https://github.com/conda-forge/proj-feedstock)
- [Rasterio PROJ Integration](https://rasterio.readthedocs.io/en/latest/topics/switch.html)
