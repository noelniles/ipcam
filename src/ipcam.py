#!/usr/bin/env python
import argparse
import json
import logging
import os
import re
import subprocess
import threading
import time
from datetime import datetime
from datetime import timedelta
from glob import glob
from multiprocessing import Process
from multiprocessing import Pool
from pathlib import Path
from systemd.journal import JournaldLogHandler

import cv2
from natsort import natsorted

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

class Camera:
    def __init__(self, addr, camid):
        self.camid = camid
        self.addr = addr
        self.cap  = cv2.VideoCapture()

    def grab(self):
        self.cap.open(self.addr)

        if self.cap.isOpened():
            ok, im = self.cap.read()

            if not ok:
                logger.warn('problem reading image from stream')
                return None

            return im

        self.cap.close()

class CameraList:
    def __init__(self):
        self.cams = []

    def append(self, value):
        self.cams.append(value)

    def __len__(self):
        return len(self.cams)

    def __getitem__(self, key):
        return self.cams[key]

    def __setitem__(self, key, value):
        self.cams.insert(key, value)

class Archive:
    def __init__(self, config):
        self.config = config
        self.paths  = []
        self.image_directories = []
        self.video_directories = []

        for c in config.data['cameras']:
            imdir = Path(c['archive']) 
            vdir  = Path(c['video_archive'])
            imdir.mkdir(parents=True, exist_ok=True)
            vdir.mkdir(parents=True, exist_ok=True)
            self.image_directories.append(imdir)
            self.video_directories.append(vdir)

    def save(self, camera_id, frameno, image, video=False):
        if video:
            save_tiff(self.video_directories[camera_id], image, prefix=str(frameno))
        else:
            save_tiff(self.image_directories[camera_id], image, prefix=str(frameno))

    def next_prefix(self, camera_id, video=False):
        """Return the next consecutive frame number."""
        if video:
            path = self.video_directories[camera_id]
        else:
            path = self.image_directories[camera_id]

        files = glob(str(path) + "/*.tif")
        files = natsorted(files, reverse=True)
        base = os.path.basename(files[0])
        return os.path.splitext(base)[0]
        #if not files:
        #    return 0
        #print(files)
        #latest = max(files, key=os.path.getctime)
        #base = os.path.basename(latest)
        #return os.path.splitext(base)[0]


def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config_file', type=str, required=True, help='path to a config file')
    ap.add_argument('--debug', action='store_true')
    return ap.parse_args()

def main(args):
    confs    = CameraThreadConfig(args.config_file)
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

    # Initialize the frame numbers.
    for cam in cams:
        framenos[cam.camid] = int(archive.next_prefix(cam.camid))

    while True:
        for i, cam in enumerate(cams):
            if is_daylight(location) or args.debug:
                im = cam.grab()

                print(framenos)
                if im is not None:
                    print(framenos[i])
                    framenos[i] += 1

                archive.save(cam.camid, framenos[i], im)
        
        time.sleep(sleep)
        



    
if __name__ == '__main__':
    args  = cli()
    main(args)

