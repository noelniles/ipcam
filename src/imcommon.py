import os
from datetime import datetime
from datetime import timezone
from glob import glob
from pathlib import Path

import cv2
import pytz
import tifffile
from astral import LocationInfo
from astral.sun import sun
from astral import Observer


def is_daylight(location):
    """True if it's daylight at the location."""
    now   = datetime.now(timezone.utc)
    lat   = float(location['latitude'])
    lon   = float(location['longitude'])
    obs   = Observer(latitude=lat, longitude=lon)
    today = now.date()
    s     = sun(obs, date=today)

    return s['sunrise'] <= now < s['sunset']

def in_time_window(start, stop):
    """True if the time is in between start and stop."""
    t = datetime.now()

    start_hour, start_minute = map(int, start.split(':'))
    stop_hour, stop_minute   = map(int, stop.split(':'))
    
    start_time = datetime(t.year, t.month, t.day, hour=start_hour, minute=start_minute)
    stop_time  = datetime(t.year, t.month, t.day)

    return start_time <= t < stop_time

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