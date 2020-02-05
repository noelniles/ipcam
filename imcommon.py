import os
from datetime import datetime
from glob import glob
from pathlib import Path

import cv2
import tifffile

def ensure_directory_exists(path):
    """Make sure the archive path exists."""
    Path(path).mkdir(parents=True, exist_ok=True)

def start_frame(path):
    """Return the next consecutive frame number."""
    files = glob(str(path) + "/*.tif")
    if not files:
        return 0
    latest = max(files, key=os.path.getctime)
    base = os.path.basename(latest)
    return os.path.splitext(base)[0]

def save_tiff(path, im, prefix='', print_status=True):
    """Save a tiff with some metadata."""
    now = datetime.utcnow()
    meta = {
        'timestamp': now.isoformat()
    }
    fn = str(Path(path, prefix+'.tif'))
    tifffile.imsave(fn, data=im, metadata=meta)

    if print_status:
        print(f'saved: {fn}', end='\r')