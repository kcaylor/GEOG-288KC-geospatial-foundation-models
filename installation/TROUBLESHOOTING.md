# Troubleshooting Guide

## Quick Links to Common Issues

- **[PROJ Database Version Mismatch](PROJ_DATABASE_FIX.md)** - "CRSError: DATABASE.LAYOUT.VERSION.MINOR = 2 whereas >= 6 is expected"
- **GDAL/Rasterio Issues** - See sections below
- **GPU/MPS Issues** - See sections below
- **Import Errors** - See sections below for GEOG 288KC

This guide provides solutions to common issues encountered when setting up and using the GEOG 288KC environment on the UCSB AI Sandbox.

## Quick Diagnostic Commands

```bash
# Check environment
conda info --envs
conda list | head -20

# Check GPU status
nvidia-smi
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

# Run validation
python installation/scripts/validate_environment.py

# Test GPU
python installation/scripts/test_gpu_setup.py
```

## Common Installation Issues

### 1. Conda Environment Creation Fails

**Symptoms:**
- `conda env create -f environment-gpu.yml` fails
- Package conflicts or solver errors

**Solutions:**

```bash
# Clear conda cache and try again
conda clean --all
conda env create -f installation/environment-gpu.yml

# If still failing, create minimal environment first
conda create -n geoAI python=3.11 -y
conda activate geoAI
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia -y
pip install -r installation/requirements-gpu.txt
```

**For GRIT Support:**
- Check if conda-forge channel is accessible
- Verify network connectivity to package repositories
- Consider using mamba instead: `mamba env create -f installation/environment-gpu.yml`

### 2. CUDA/GPU Not Detected

**Symptoms:**
- `torch.cuda.is_available()` returns `False`
- `nvidia-smi` shows GPUs but PyTorch can't access them

**Diagnostic Steps:**

```bash
# Check NVIDIA driver
nvidia-smi

# Check CUDA installation
nvcc --version

# Check PyTorch CUDA compatibility
python -c "import torch; print(torch.version.cuda)"
```

**Solutions:**

```bash
# Reinstall PyTorch with correct CUDA version
conda activate geoAI

# For CUDA 11.8
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia --force-reinstall

# For CUDA 12.1
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia --force-reinstall
```

**For GRIT Support:**
- Verify CUDA driver version matches installed CUDA toolkit
- Check if multiple CUDA versions are causing conflicts
- Ensure users are in correct groups for GPU access

### 3. Foundation Model Download Failures

**Symptoms:**
- Models fail to download from HuggingFace Hub
- Authentication errors
- Network timeout errors

**Solutions:**

```bash
# Re-authenticate with HuggingFace
huggingface-cli login

# Set longer timeout
export HF_HUB_DOWNLOAD_TIMEOUT=300

# Use different cache directory if disk space is an issue
export HF_HOME=/path/to/larger/storage/.cache/huggingface

# Re-run installation
bash installation/scripts/install_foundation_models.sh
```

**Alternative Model Sources:**
```bash
# Download specific models manually
python -c "
from huggingface_hub import snapshot_download
snapshot_download('ibm-nasa-geospatial/Prithvi-100M', local_dir='models/prithvi')
"
```

### 4. Earth Engine Authentication Issues

**Symptoms:**
- `ee.Initialize()` fails
- Authentication errors when accessing Earth Engine

**Solutions:**

```bash
# Standard authentication
earthengine authenticate

# Force re-authentication
earthengine authenticate --force

# Check authentication status
python -c "import ee; ee.Initialize(); print('Earth Engine authenticated successfully')"
```

**Service Account Setup (for automated systems):**
```bash
# Set service account credentials
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"

# Initialize with service account
python -c "
import ee
ee.Initialize(ee.ServiceAccountCredentials('your-service-account@project.iam.gserviceaccount.com', 'path/to/key.json'))
"
```

### 5. Memory Issues

**Symptoms:**
- CUDA out of memory errors
- System running out of RAM
- Slow performance

**Solutions:**

**Reduce Memory Usage:**
```python
# Reduce batch size
batch_size = 8  # instead of 32

# Use gradient checkpointing
model.gradient_checkpointing_enable()

# Clear GPU cache regularly
import torch
torch.cuda.empty_cache()

# Use mixed precision training
from torch.cuda.amp import autocast, GradScaler
scaler = GradScaler()

with autocast():
    outputs = model(inputs)
```

**Monitor Memory Usage:**
```bash
# Monitor GPU memory
watch -n 1 nvidia-smi

# Monitor system memory
watch -n 1 free -h

# Profile memory usage in Python
pip install memory_profiler
%load_ext memory_profiler
%memit your_function()
```

### 6. Jupyter Kernel Issues

**Symptoms:**
- geoAI kernel not available in Jupyter
- Packages not found in notebooks
- Kernel crashes

**Solutions:**

```bash
# Reinstall kernel
conda activate geoAI
python -m ipykernel install --user --name geoai --display-name "GeoAI"

# List available kernels
jupyter kernelspec list

# Remove old kernels if needed
jupyter kernelspec uninstall old-kernel-name

# Test kernel
jupyter console --kernel=geoai
```

**Quarto Integration:**
```bash
# Verify Quarto can find kernel
quarto check jupyter

# Test specific kernel
quarto render test.qmd --execute
```

### 7. Package Import Errors

**Symptoms:**
- `ModuleNotFoundError` for installed packages
- Version conflicts
- Import hangs or crashes

**Diagnostic Steps:**

```bash
# Check if package is installed
conda activate geoAI
python -c "import torchgeo; print(torchgeo.__version__)"

# Check package location
python -c "import torchgeo; print(torchgeo.__file__)"

# List all installed packages
conda list | grep torch
pip list | grep torch
```

**Solutions:**

```bash
# Reinstall problematic packages
pip install torchgeo --force-reinstall

# Check for conflicts
conda env export > current_env.yml
# Review for version conflicts

# Clean install if necessary
conda activate geoAI
pip install --no-deps --force-reinstall package_name
```

## Performance Optimization Issues

### 8. Slow Model Loading

**Symptoms:**
- Models take very long to load
- Timeouts during model download

**Solutions:**

```python
# Use local cache
import os
os.environ['HF_HOME'] = '/path/to/fast/storage/.cache'

# Load from local directory
from transformers import AutoModel
model = AutoModel.from_pretrained("/local/path/to/model", local_files_only=True)

# Use model checkpointing
torch.save(model.state_dict(), 'model_checkpoint.pth')
model.load_state_dict(torch.load('model_checkpoint.pth'))
```

### 9. Slow Data Loading

**Symptoms:**
- Training slow due to data loading bottleneck
- High CPU usage during data loading

**Solutions:**

```python
# Optimize DataLoader
from torch.utils.data import DataLoader

dataloader = DataLoader(
    dataset,
    batch_size=32,
    num_workers=8,  # Adjust based on CPU cores
    pin_memory=True,
    persistent_workers=True,
    prefetch_factor=2
)

# Use faster data formats
# Convert to HDF5, Zarr, or preprocessed tensors
import h5py
with h5py.File('data.h5', 'w') as f:
    f.create_dataset('images', data=image_array, compression='gzip')
```

## Network and Connectivity Issues

### 10. Download Failures

**Symptoms:**
- Models fail to download
- Network timeouts
- SSL certificate errors

**Solutions:**

```bash
# Use different mirror
pip install -i https://pypi.org/simple/ package_name

# Increase timeout
pip install --timeout 300 package_name

# Disable SSL verification (not recommended for production)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org package_name

# Use conda instead of pip
conda install -c conda-forge package_name
```

## Environment Management Issues

### 11. Environment Corruption

**Symptoms:**
- Packages suddenly stop working
- Import errors for previously working packages
- Conflicting versions

**Solutions:**

```bash
# Create fresh environment
conda deactivate
conda env remove -n geoAI
conda env create -f installation/environment-gpu.yml

# Or update existing environment
conda activate geoAI
conda env update -f installation/environment-gpu.yml --prune
```

### 12. Disk Space Issues

**Symptoms:**
- Installation fails due to insufficient space
- Models can't be saved
- Cache directories full

**Solutions:**

```bash
# Check disk usage
df -h
du -sh ~/.cache/huggingface/

# Clean conda cache
conda clean --all

# Clean pip cache
pip cache purge

# Move cache to different location
export HF_HOME=/path/to/larger/storage/.cache/huggingface
export TORCH_HOME=/path/to/larger/storage/.cache/torch

# Clean up old model checkpoints
find ~/geoAI -name "*.pth" -type f -mtime +7 -ls
```

## Getting Help

### Self-Diagnosis Checklist

Before asking for help, run these commands and include the output:

```bash
# System information
echo "Environment: $CONDA_DEFAULT_ENV"
python --version
nvidia-smi
df -h

# Package versions
python -c "import torch, torchvision, transformers; print(f'PyTorch: {torch.__version__}, Transformers: {transformers.__version__}')"

# GPU test
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, GPUs: {torch.cuda.device_count()}')"

# Run validation
python installation/scripts/validate_environment.py
```

### Support Channels

1. **Course Instructors:**
   - Kelly Caylor: caylor@ucsb.edu
   - Anna Boser: annaboser@ucsb.edu

2. **Technical Support:**
   - UCSB GRIT: Submit ticket at grit.ucsb.edu
   - Course GitHub Issues: https://github.com/kcaylor/GEOG-288KC-geospatial-foundation-models/issues

3. **Student Support:**
   - Course Slack channel for peer help
   - Office hours: Fridays 2-5pm

### When Reporting Issues

Include the following information:

1. **Environment details:**
   ```bash
   conda env export > environment_debug.yml
   # Attach this file
   ```

2. **Error messages:**
   - Full error traceback
   - Command that caused the error

3. **System information:**
   ```bash
   nvidia-smi > nvidia_info.txt
   python installation/scripts/validate_environment.py > validation_report.txt
   ```

4. **What you were trying to do:**
   - Specific steps to reproduce
   - Expected vs. actual behavior

### Emergency Procedures

**For Complete System Failure:**

1. **Save your work:**
   ```bash
   # Backup important files
   cp -r ~/geoAI/your_project ~/backup/
   ```

2. **Fresh installation:**
   ```bash
   conda env remove -n geoAI
   cd ~/geoAI
   git pull origin main  # Get latest version
   bash installation/scripts/install_foundation_models.sh
   ```

3. **Contact support** if issues persist

**For GRIT Support - System-wide Issues:**

1. Check if issue affects multiple users
2. Verify hardware status (GPU, storage, network)
3. Check for system updates that might have affected the environment
4. Review user access permissions and quotas

---

## Known Issues and Workarounds

### Issue: CUDA Version Mismatch
- **Problem:** PyTorch compiled with different CUDA version than system
- **Workaround:** Use conda to install matching versions
- **Status:** Monitor CUDA updates on AI Sandbox

### Issue: HuggingFace Rate Limiting
- **Problem:** Too many download requests
- **Workaround:** Use authentication tokens and retry with exponential backoff
- **Status:** Consider caching popular models locally

### Issue: Memory Fragmentation
- **Problem:** GPU memory becomes fragmented during long training sessions
- **Workaround:** Restart kernel periodically, use `torch.cuda.empty_cache()`
- **Status:** Ongoing - monitor PyTorch updates

---

*Last updated: August 2025*  
*For the latest troubleshooting information, check the course repository.*