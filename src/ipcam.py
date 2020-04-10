#!/usr/bin/env python
import argparse
import json
import logging
import re
import subprocess
import threading
import time
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from systemd.journal import JournaldLogHandler

import cv2

from imcommon import ensure_directory_exists, save_tiff, start_frame
from imcommon import in_time_window
from imcommon import is_daylight


logger  = logging.getLogger(__name__)
handler = JournaldLogHandler()
fmt     = logging.Formatter('[%(levelname)]s %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class CameraThreadConfig:
    def __init__(self, config_file):
        self.config_file    = config_file
        self.data           = self.parse_config()
        self.archive_exists = False

    def parse_config(self):
        with open(self.config_file, 'r') as f:
            s = f.read()
            return json.loads(s)

    def by_id(self, camera_id):
        d = {}
        d['location'] = self.data['location']

        for camera in self.data['cameras']:
            if camera['id'] == camera_id:
                d['camera'] = camera
                return d

    def n_cameras(self):
        return len(self.data['cameras'])


class CameraThread(threading.Thread):
    def __init__(self, config, debug=False):
        super(CameraThread, self).__init__()
        self.debug          = debug
        self.config         = config
        self.camid          = config['camera']['id']
        self.addr           = config['camera']['url']
        self.archive        = config['camera']['archive']
        self.sleep          = config['camera']['sleep']
        self.start_video    = config['camera']['start_video']
        self.stop_video     = config['camera']['stop_video']
        self.video_archive  = config['camera']['video_archive']
        self.location       = config['location']
        self.prefix         = start_frame(self.archive)
        self.nth_frame      = int(self.prefix)
        self.cap            = cv2.VideoCapture(self.addr)

        ensure_directory_exists(self.archive)

    def finish(self):
        self.cap.release()

    def capture(self):
        ok = False
        if self.cap.isOpened():
            ok, im = self.cap.read()
        else:
            logger.error(f'opening video stream from {self.addr}')

        while True:
            if ok and is_daylight(self.location) or ok and self.debug:
                self.nth_frame += 1
                if in_time_window(self.start_video, self.stop_video):
                    # Time to save video.
                    now = datetime.utcnow().date().strftime('%Y%m%d-%H%M%S')
                    path = str(Path(self.video_archive, now))
                    save_tiff(path, im, prefix=str(self.nth_frame))
                else:
                    # Time to save stills.
                    save_tiff(self.archive, im, prefix=str(self.nth_frame))
                    time.sleep(self.sleep)

                ok, im = self.cap.read()
            else:
                pass

        self.finish()

    def run(self):
        self.running = True
        self.capture()

def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config_file', type=str, required=True, help='path to a config file')
    ap.add_argument('--debug', action='store_true')
    return ap.parse_args()

def main(args):
    confs = CameraThreadConfig(args.config_file)
    ncams = confs.n_cameras()

    for i in range(ncams):
        config = confs.by_id(i)
        t      = CameraThread(config, debug=args.debug)
        t.start()

if __name__ == '__main__':
    args  = cli()
    main(args)

