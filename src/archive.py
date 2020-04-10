import os
from pathlib import Path
from glob    import glob

from imcommon import save_tiff
from natsort  import natsorted


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
        if not files:
            return 0
        files = natsorted(files, reverse=True)
        base = os.path.basename(files[0])
        return os.path.splitext(base)[0]