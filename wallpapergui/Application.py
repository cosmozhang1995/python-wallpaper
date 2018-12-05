from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QFontDatabase
from PySide2.QtCore import QUrl
from wallpaper.system import system
import os

class Application(QApplication):
    def __init__(self, argv=[]):
        super().__init__(argv)
        self.add_fonts()
    def add_fonts(self):
        fontdir = os.path.join(system.execpath, "fonts")
        # filenames = os.listdir(fontdir)
        filenames = ["fa-solid-900.ttf"]
        for filename in filenames:
            suffix = filename.split(".")[-1].lower()
            if suffix in ["ttf"]:
                filepath = os.path.join(fontdir, filename)
                fontId = QFontDatabase.addApplicationFont(filepath)
                print("Added font:", QFontDatabase.applicationFontFamilies(fontId))
