#!/usr/bin/env python
import argparse
import logging
import sys
import time
from guppy import hpy
from pathlib import Path
from queue   import Queue
from datetime import datetime
from systemd.journal import JournaldLogHandler
from threading import Thread

from archive  import Archive
from cameras  import CameraConfig, CameraList, Camera
from consumer import consume
from imcommon import in_time_window
from imcommon import is_daylight
from pollable_queue import PollableQueue

H = hpy()

logger  = logging.getLogger(__name__)
handler = JournaldLogHandler()
fmt     = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class BufferItem:
    def __init__(self, timestamp, frameno, camera_id, image):
        self.timestamp = timestamp
        self.frameno   = frameno
        self.camera_id = camera_id
        self.image     = image

class Frame:
    _fields_ = [
        ('timestamp')
    ]
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
    start_video = confs.data['cameras'][0]['start_video']
    stop_video = confs.data['cameras'][0]['stop_video']

    q = PollableQueue(maxsize=4)
    vq = PollableQueue(maxsize=4)

    for c in confs.data['cameras']:
        camid = c['id']
        addr  = c['url']
        cam = Camera(addr, camid)
        cams.append(cam)
        framenos[cam.camid] = int(archive.next_prefix(cam.camid))
    
    image_thread = Thread(target=consume, args=(q, archive.save_image))
    video_thread = Thread(target=consume, args=(vq, archive.save_video))
    image_thread.start()
    video_thread.start()

    while True:
        if is_daylight(location) or args.debug:
            is_video_time = in_time_window(start_video, stop_video)
            for i, cam in enumerate(cams):
                im        = cam.grab()
                timestamp = datetime.now()

                if im is None:
                    logger.warning(f'empty image from camera {cam.camid}')
                    continue

                framenos[i] += 1
                buffer_item = BufferItem(timestamp, framenos[i], cam.camid, im)
                print(H.heap())
                if is_video_time or args.debug:
                    q.put(buffer_item)
                else:
                    vq.put(buffer_item)
            
            if not is_video_time or not args.debug:
                time.sleep(sleep)


if __name__ == '__main__':
    args  = cli()
    main(args)

