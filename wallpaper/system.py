import os

class SystemInfo:
    @property
    def appdatadir(self):
        appdatadir = os.getenv("APPDATA")
        appdatadir = os.path.join(appdatadir, "python-wallpaper")
        if not os.path.isdir(appdatadir): os.mkdir(appdatadir)
        return appdatadir

system = SystemInfo()
