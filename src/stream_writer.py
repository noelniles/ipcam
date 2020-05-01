import cv2


class StreamWriter:
    def __init__(self, uri):
        self.cap = cv2.VideoCapture(uri)