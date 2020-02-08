import os
from datetime import datetime
from glob import glob
from pathlib import Path

import cv2
import tifffile


def in_time_window(start, stop):
    t = datetime.utcnow()

    start_hour, start_minute = map(int, start.split(':'))
    stop_hour, stop_minute   = map(int, stop.split(':'))
    
    start_time = datetime(t.year, t.month, t.day, hour=start_hour, minute=start_minute)

    if start_hour > stop_hour:
        start_time = datetime(t.year, t.month, t.day-1, hour=start_hour, minute=start_minute)
        end_time   = datetime(t.year, t.month, t.day, hour=stop_hour, minute=stop_minute)
    else:
        start_time = datetime(t.year, t.month, t.day, hour=start_hour, minute=start_minute)
        end_time   = datetime(t.year, t.month, t.day, hour=stop_hour, minute=stop_minute)

    if start_time <= t <= end_time:
        return True

    print('start: ', start_time.isoformat())
    print('now: ', t.isoformat())
    print('end: ', end_time.isoformat())
    print('Not time')
    return False

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
    ensure_directory_exists(path)
    now = datetime.utcnow()
    meta = {
        'timestamp': now.isoformat()
    }
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    fn = str(Path(path, prefix+'.tif'))
    tifffile.imsave(fn, data=im, metadata=meta)

    if print_status:
        print(f'saved: {fn}', end='\r')