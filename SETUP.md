# Setup Instructions

## Fixing the Transformers Cache Migration Issue

If you're encountering the error:
```
ImportError: cannot import name 'cached_download' from 'huggingface_hub'
```

This is a compatibility issue between `sentence-transformers` and `huggingface_hub`. Follow these steps to resolve it:

### Solution 1: Update Dependencies (Recommended)

1. **Uninstall conflicting packages:**
   ```bash
   pip uninstall sentence-transformers transformers huggingface-hub -y
   ```

2. **Install updated compatible versions:**
   ```bash
   pip install -r requirements.txt
   ```

### Solution 2: Clean Install

If the above doesn't work, perform a clean installation:

1. **Remove your virtual environment:**
   ```bash
   rm -rf venv
   ```

2. **Create a new virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Completing the Cache Migration

The transformers cache migration is a one-time operation. If you interrupted it, you can complete it manually:

```python
import transformers
transformers.utils.move_cache()
```

Or simply delete the old cache and let it rebuild:
```bash
rm -rf ~/.cache/huggingface/transformers
```

## Verification

After installation, verify everything works:

```python
from sentence_transformers import SentenceTransformer

# This should work without errors
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Installation successful!")
```

## Dependency Versions

The following versions are known to work together:
- `sentence-transformers >= 2.2.0`
- `transformers >= 4.26.0`
- `huggingface-hub >= 0.11.0`

These versions use the new `hf_hub_download` API instead of the deprecated `cached_download`.
