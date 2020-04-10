#!/usr/bin/env python
import argparse
import logging
import time
from pathlib import Path
from systemd.journal import JournaldLogHandler

from archive  import Archive
from cameras  import CameraConfig, CameraList, Camera
from imcommon import in_time_window
from imcommon import is_daylight


logger  = logging.getLogger(__name__)
handler = JournaldLogHandler()
fmt     = logging.Formatter('[%(levelname)]s %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config_file', type=str, required=True, help='path to a config file')
    ap.add_argument('--debug', action='store_true')
    return ap.parse_args()

def main(args):
    confs    = CameraConfig(args.config_file)
    ncams    = confs.n_cameras()
    cams     = CameraList()
    archive  = Archive(confs)
    framenos = [0]*ncams
    location = confs.data['location']
    sleep    = confs.data['cameras'][0]['sleep']

    for c in confs.data['cameras']:
        camid = c['id']
        addr  = c['url']
        cam = Camera(addr, camid)
        cams.append(cam)
        framenos[cam.camid] = int(archive.next_prefix(cam.camid))

    while True:
        for i, cam in enumerate(cams):
            if is_daylight(location) or args.debug:
                im = cam.grab()

                if im is not None:
                    framenos[i] += 1

                archive.save(cam.camid, framenos[i], im)
        
        time.sleep(sleep)
    
if __name__ == '__main__':
    args  = cli()
    main(args)

