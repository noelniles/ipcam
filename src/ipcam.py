#!/usr/bin/env python
import argparse
import logging
import sys
import time
from pathlib import Path
from datetime import datetime
from systemd.journal import JournaldLogHandler

from archive  import Archive
from cameras  import CameraConfig, CameraList, Camera
from imcommon import in_time_window, is_daylight


logger  = logging.getLogger(__name__)
handler = JournaldLogHandler()
fmt     = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config_file', type=str, required=True, help='path to a config file')
    ap.add_argument('--debug', action='store_true')
    return ap.parse_args()

def main(args):
    confs       = CameraConfig(args.config_file)
    ncams       = confs.n_cameras()
    cams        = CameraList()
    archive     = Archive(confs)
    framenos    = [0]*ncams
    location    = confs.data['location']
    sleep       = confs.data['cameras'][0]['sleep']
    start_video = confs.data['cameras'][0]['start_video']
    stop_video  = confs.data['cameras'][0]['stop_video']

    for c in confs.data['cameras']:
        camid = c['id']
        addr  = c['url']
        cam   = Camera(addr, camid)
        cams.append(cam)
        framenos[cam.camid] = int(archive.next_prefix(cam.camid))

    while True:
        if is_daylight(location) or args.debug:

            for i, cam in enumerate(cams):
                im        = cam.grab()
                timestamp = datetime.now()

                if im is None:
                    break

                framenos[i] += 1
                archive.save_image(cam.camid, timestamp, framenos[i], im)

            time.sleep(sleep)

if __name__ == '__main__':
    args  = cli()
    main(args)
