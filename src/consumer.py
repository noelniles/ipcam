import select
import threading
import time


def consume(queues, callback):
    while True:
        can_read, _, _ = select.select([queues], [], [])

        for r in can_read:
            item = r.get()
            callback(item.camera_id, item.timestamp, item.frameno, item.image)
            del item


