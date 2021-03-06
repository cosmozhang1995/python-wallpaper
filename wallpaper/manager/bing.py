import os
from ..system import system
import requests
import threading, time
import datetime
import cv2
import json
import re
import random

hosturl = "https://cn.bing.com"

class BingWallpaperInfo:
    def __init__(self, wallpaper):
        jsonfile = open(wallpaper.jsonpath, "rb")
        jsondata = json.loads(jsonfile.read().decode("utf-8"))
        jsonfile.close()
        self.startdate = datetime.datetime.strptime(jsondata["startdate"], "%Y%m%d")
        self.enddate = datetime.datetime.strptime(jsondata["enddate"], "%Y%m%d")
        self.url = hosturl + jsondata["url"]
        self.copyright = jsondata["copyright"]
        self.copyrightlink = jsondata["copyrightlink"]
        self.copyrightonly = jsondata["copyrightonly"]
        self.title = jsondata["title"]
        self.caption = jsondata["caption"]
        self.desc = jsondata["desc"]
        self.hsh = jsondata["hsh"]

class BingWallpaper:
    def __init__(self, manager=None, date=None, hsh=None, postfix="jpg", name=None, config=None):
        self.manager = manager
        self.date = date
        self.hsh = hsh
        self.postfix = postfix
        if not config is None:
            self.date = datetime.datetime.strptime(config["startdate"], "%Y%m%d")
            self.hsh = config["hsh"]
            self.postfix = config["url"].split(".")[-1]
        elif not name is None:
            name = name.split(".")
            nameparts = name[0].split("-")
            self.date = datetime.datetime.strptime("-".join(nameparts[0:-1]), "%Y-%m-%d")
            self.hsh = nameparts[-1]
            self.postfix = name[-1]
        self._info = None
        self._image = None
    @property
    def name(self):
        return  "%s-%s.%s" % (self.date.strftime("%Y-%m-%d"), self.hsh, self.postfix)
    @property
    def jsonpath(self):
        return os.path.join(self.manager.datadir, self.name + ".json")
    @property
    def imagepath(self):
        return os.path.join(self.manager.datadir, self.name)
    @property
    def info(self):
        if self._info is None:
            self._info = BingWallpaperInfo(self)
        return self._info
    @property
    def image(self):
        if self._image is None:
            self._image = cv2.imread(self.imagepath)
        return self._image
    sortkey = lambda item: item.name

class BingWallpaperStatus:
    def __init__(self, item=None, updatetime=None, json=None, filepath=None):
        self.item = item
        self.updatetime = updatetime
        if filepath:
            self.load(filepath)
        if json:
            self.json = json
    @property
    def json(self):
        return {
            "name": self.item.name if self.item else None,
            "updatetime": self.updatetime.strftime("%Y-%m-%d %H:%M:%S") if self.updatetime else None
        }
    @json.setter
    def json(self, val):
        if isinstance(val, str): val = json.loads(val)
        self.item = BingWallpaper(name=val["name"]) if "name" in val else None
        self.updatetime = datetime.datetime.strptime(val["updatetime"], "%Y-%m-%d %H:%M:%S") if "updatetime" in val else None
    def update(self, fileitem, savepath=None):
        self.item = fileitem
        self.updatetime = datetime.datetime.now()
        if savepath:
            self.save(savepath)
    def save(self, filepath):
        file = open(filepath, "wb")
        file.write(json.dumps(self.json, indent=4).encode("utf-8"))
        file.close()
    def load(self, filepath):
        if os.path.isfile(filepath):
            file = open(filepath, "rb")
            self.json = file.read().decode("utf-8")
            file.close()

class BingManager:
    def __init__(self):
        self.vendordir = os.path.join(system.appdatadir, "bing-wallpapers")
        if not os.path.isdir(self.vendordir): os.mkdir(self.vendordir)
        self.datadir = os.path.join(self.vendordir, "downloads")
        if not os.path.isdir(self.datadir): os.mkdir(self.datadir)
        self.statusfile = os.path.join(self.vendordir, "status.json")
        self.files = [re.match(r"((\d+\-\d+\-\d+\-\w+)\.(\w+))\.json", fname) for fname in os.listdir(self.datadir)]
        self.files = list(filter(lambda fname: not fname is None, self.files))
        self.files = [BingWallpaper(manager=self, name=fname.group(1)) for fname in self.files]
        self.files.sort(key=BingWallpaper.sortkey)
        self.newfiles = []
        self._in_update = False
        self._update_callbacks = []
        self.curridx = -1
        self.status = BingWallpaperStatus(filepath=self.statusfile)
    def update(self, callback=None):
        if callback:
            self._update_callbacks.append(callback)
        if self._in_update:
            return
        self._in_update = True
        thread = threading.Thread(target=self.thread_fn_load_images)
        thread.setDaemon(True)
        thread.start()
    def thread_fn_load_images(self):
        try:
            imagelist = requests.get(hosturl + "/HPImageArchive.aspx?format=js&idx=0&n=100&pid=hp&FORM=BEHPTB&ensearch=1").text
        except requests.exceptions.RequestException as e:
            print("<WARNING> BingManager update failed")
            print("   ", e)
            self._in_update = False
            return
        imagelist = json.loads(imagelist)["images"]
        hshes = [item.hsh for item in self.files]
        newimagelist = []
        for imageitem in imagelist:
            if not imageitem["hsh"] in hshes:
                newimagelist.append(imageitem)
        outlist = [None for item in newimagelist]
        for i in range(len(newimagelist)):
            thread = threading.Thread(target=self.thread_fn_download_image, args=(imagelist, outlist, i))
            thread.setDaemon(True)
            thread.start()
        while True:
            all_completed = True
            for item in outlist:
                if item is None:
                    all_completed = False
                    break
            if all_completed:
                break
            time.sleep(0.05)
        outlist = list(filter(lambda item: isinstance(item, BingWallpaper), outlist))
        outlist.sort(key=BingWallpaper.sortkey)
        self.files = self.files + outlist
        self.newfiles = self.newfiles + outlist
        for cb in self._update_callbacks:
            cb()
        self._update_callbacks = []
        self._in_update = False
    def thread_fn_download_image(self, imagelist, outlist, i):
        wallpaperitem = BingWallpaper(manager=self, config=imagelist[i])
        try:
            imagedata = requests.get(hosturl + imagelist[i]["url"]).content
        except requests.exceptions.RequestException:
            print("<WARNING> BingManager failed to download image %s" % hosturl + imagelist[i]["url"])
            print("   ", e)
            outlist[i] = False
            return
        file = open(wallpaperitem.imagepath, "wb")
        file.write(imagedata)
        file.close()
        imageitem_json_str = json.dumps(imagelist[i])
        file = open(wallpaperitem.jsonpath, "wb")
        file.write(imageitem_json_str.encode("utf-8"))
        file.close()
        outlist[i] = wallpaperitem
    def next(self):
        fileitem = None
        if len(self.newfiles) > 0:
            newfile = self.newfiles[0]
            self.newfiles = self.newfiles[1:]
            fileitem = newfile
        elif len(self.files) > 0:
            self.curridx = (self.curridx + 1) % len(self.files)
            fileitem = self.files[self.curridx]
        self.status.update(fileitem, savepath=self.statusfile)
        return fileitem
    def random(self, **kwargs):
        filterfn = None
        limit = None
        if "filter" in kwargs: filterfn = kwargs["filter"]
        if "limit" in kwargs: limit = kwargs["limit"]
        filelist = self.files
        if filterfn: filelist = list(filter(filterfn, filelist))
        if limit: filelist = filelist[-limit:]
        if len(filelist) > 0:
            fileitem = filelist[int(random.random()*len(filelist))]
            self.newfiles = list(filter(lambda item: item.name != fileitem.name, self.newfiles))
        else:
            fileitem = None
        self.status.update(fileitem, savepath=self.statusfile)
        return fileitem

    


