import json 
import logging

import cv2
from systemd.journal import JournaldLogHandler

logger  = logging.getLogger(__name__)
handler = JournaldLogHandler()
fmt     = logging.Formatter('[%(levelname)]s %(message)s')
handler.setFormatter(fmt)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)



class CameraConfig:
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