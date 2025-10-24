```python
import os, pathlib

# Specify the full path to where you want your data to be located:
BASE = "/home/caylor/hf_cache" 

# Setup environment variables that are used by the HF library:
os.environ["HF_HOME"]            = os.path.join(BASE, "hfhome")
os.environ["HF_HUB_CACHE"]       = os.path.join(BASE, "hub")
os.environ["HF_DATASETS_CACHE"]  = os.path.join(BASE, "datasets")
os.environ["TRANSFORMERS_CACHE"] = os.path.join(BASE, "transformers")

# Ensure all the necessary folders are created:
for p in [os.environ["HF_HOME"], os.environ["HF_HUB_CACHE"],
          os.environ["HF_DATASETS_CACHE"], os.environ["TRANSFORMERS_CACHE"]]:
    pathlib.Path(p).mkdir(parents=True, exist_ok=True)

```


```python
# Import necessary modules from the library
from datasets import load_dataset
from datasets import DownloadConfig
```


```python
# The download config needs your local HF_HUB_CACHE location:
dc = DownloadConfig(cache_dir=os.environ["HF_HUB_CACHE"])

ds = load_dataset("glue", "mrpc",
                  cache_dir=os.environ["HF_DATASETS_CACHE"])
```


```python
ds
```




    DatasetDict({
        train: Dataset({
            features: ['sentence1', 'sentence2', 'label', 'idx'],
            num_rows: 3668
        })
        validation: Dataset({
            features: ['sentence1', 'sentence2', 'label', 'idx'],
            num_rows: 408
        })
        test: Dataset({
            features: ['sentence1', 'sentence2', 'label', 'idx'],
            num_rows: 1725
        })
    })




```python

```
