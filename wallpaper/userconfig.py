import os, json
from .system import system

class UserConfig:
    def __init__(self):
        self.configpath = os.path.join(system.appdatadir, "userconfig.json")
        self.limit = None
        self.interval = 3600
        self.load()
    def load(self, filepath=None):
        if filepath is None: filepath = self.configpath
        if os.path.isfile(filepath):
            file = open(filepath, "rb")
            jsondata = json.loads(file.read().decode("utf-8"))
            file.close()
            if "limit" in jsondata: self.limit = jsondata["limit"]
            if "interval" in jsondata: self.interval = jsondata["interval"]
    def save(self, filepath=None):
        if filepath is None: filepath = self.configpath
        jsondata = {}
        jsondata["limit"] = self.limit
        jsondata["interval"] = self.interval
        file = open(filepath, "wb")
        file.write(json.dumps(jsondata, indent=4).encode("utf-8"))
        file.close()

