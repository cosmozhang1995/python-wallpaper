import cv2
import os

class ImageItem:
    def __init__(self, filepath, **kwargs):
        self.image = cv2.imread(filepath)
        self.name = os.path.split(filepath)[1]
        if "name" in kwargs: self.name = kwargs["name"]
    def save(self, topath):
        cv2.imwrite(topath, self.image)
