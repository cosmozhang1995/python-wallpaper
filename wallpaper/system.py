import os, sys

class SystemInfo:
    @property
    def appdatadir(self):
        appdatadir = os.getenv("APPDATA")
        appdatadir = os.path.join(appdatadir, "python-wallpaper")
        if not os.path.isdir(appdatadir): os.mkdir(appdatadir)
        return appdatadir
    @property
    def execpath(self):
        if getattr( sys, 'frozen', False ) :
            return os.path.realpath(os.path.dirname(sys.executable))
        else :
            return os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
    

system = SystemInfo()
