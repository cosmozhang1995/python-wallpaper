import sys,os

from PySide2.QtCore import Qt, QPoint
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QSystemTrayIcon, QMenu, QAction
from PySide2.QtGui import QPainter, QColor, QIcon

import requests
import json

from wallpaper.wallpaper import set_wallpaper
from wallpaper.image import ImageItem
from wallpaper.system import system

import win32con, win32gui, win32api
def findDesktopIconWnd():
    def EnumWindowsCallback(hwnd, params):
        wflags = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE);
        if not (wflags & win32con.WS_VISIBLE): return True
        sndWnd = win32gui.FindWindowEx(hwnd, None, "SHELLDLL_DefView", None)
        if not sndWnd: return True
        targetWnd = win32gui.FindWindowEx(sndWnd, None, "SysListView32", "FolderView")
        if not targetWnd: return True;
        params.append(targetWnd)
        return True
    results = []
    win32gui.EnumWindows(EnumWindowsCallback, results)
    return results[0] if len(results) > 0 else None

class DesktopWidget(QWidget):
    def __init__(self):
        super().__init__()
        # default styles
        self.bgcolor = "rgba(0,0,0,172)" # QColor(0, 0, 0, 0x99)
        self.bgcolor_hover = "rgba(0,0,0,204)" # QColor(0, 0, 0, 0xcc)
        self.txtcolor = "#ffffff" # QColor(255, 255, 255)
        self.txtpadding = 8
        self.fontsize = 18
        self.fontfamily = "\"Segoe UI\", Arial";
        # self.fontfamily = "\"Microsoft YaHei\", Arial";
        # other properties
        self.imageitem = None
        # mouse dragging properties
        self.mousePressPos = None
        self.mousePressWindowPos = QPoint(100,100)
        self.mouseEnterred = False
        self.windowPosition = self.loadWindowPosition(QPoint(0,0))
        # build layout
        self.text = QLabel("Hello World")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.text)
        self.setLayout(self.layout)
        self.updateWidgetStyles()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # build system tray menu
        self.systemTray = QSystemTrayIcon(self)
        self.systemTray.setIcon(QIcon("images/bing.png"))
        self.systemTray.setToolTip("Bing Wallpaper")
        self.systemTray.show()
        menu = QMenu(self)
        action_change = QAction(menu)
        action_change.setText("Change Wallpaper")
        action_change.triggered.connect(self.onTrayActionChange)
        menu.addAction(action_change)
        action_close = QAction(menu)
        action_close.setText("Close")
        action_close.triggered.connect(self.onTrayActionClose)
        menu.addAction(action_close)
        self.systemTrayMenu = menu
        self.systemTray.setContextMenu(self.systemTrayMenu)

    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     alpha = 0x7f if self.mouseEnterred else 0x00
    #     painter.fillRect(self.rect(), QColor(0xff, 0xff, 0xff, alpha))

    def show(self):
        super().show()
        hDesktop = findDesktopIconWnd()
        win32gui.SetParent(self.winId(), hDesktop)
        lWinStyle = win32gui.GetWindowLong(self.winId(), win32con.GWL_STYLE)
        lWinStyle = lWinStyle & (~win32con.WS_CAPTION)
        lWinStyle = lWinStyle & (~win32con.WS_SYSMENU)
        lWinStyle = lWinStyle & (~win32con.WS_MAXIMIZEBOX)
        lWinStyle = lWinStyle & (~win32con.WS_MINIMIZEBOX)
        lWinStyle = lWinStyle & (~win32con.WS_SIZEBOX)
        win32gui.SetWindowLong(self.winId(), win32con.GWL_STYLE, lWinStyle)
        # win32gui.SetLayeredWindowAttributes(self.winId(), 0, 0, win32con.LWA_ALPHA)
        # win32gui.ShowWindowAsync
        win32gui.MoveWindow(self.winId(), self.windowPosition.x(), self.windowPosition.y(), self.width(), self.height(), True)
        print(hDesktop, self.winId())

    def onTrayActionClose(self):
        self.close()
    def onTrayActionChange(self):
        self.changeWallpaper()

    def enterEvent(self, event):
        self.mouseEnterred = True
        self.updateWidgetStyles()
    def leaveEvent(self, event):
        self.mouseEnterred = False
        self.updateWidgetStyles()

    def mousePressEvent(self, event):
        self.mousePressPos = event.globalPos()
        self.mousePressWindowPos = self.windowPosition
        self.updateWidgetStyles()
    def mouseMoveEvent(self, event):
        if self.mousePressPos:
            pos = event.globalPos()
            dx = pos.x() - self.mousePressPos.x()
            dy = pos.y() - self.mousePressPos.y()
            win32gui.MoveWindow(self.winId(), self.mousePressWindowPos.x() + dx, self.mousePressWindowPos.y() + dy, self.width(), self.height(), True)
    def mouseReleaseEvent(self, event):
        if self.mousePressPos:
            pos = event.globalPos()
            self.mousePressWindowPos += pos - self.mousePressPos
            self.windowPosition = self.mousePressWindowPos
            self.mousePressPos = None
            self.updateWidgetStyles()
            self.saveWindowPosition(self.windowPosition)

    def changeWallpaper(self):
        imagelist = requests.get("https://cn.bing.com/HPImageArchive.aspx?format=js&idx=0&n=100&nc=1543399734692&pid=hp&FORM=BEHPTB&ensearch=1").text
        imagelist = json.loads(imagelist)["images"]
        imageitem_jsonfile_path = os.path.join(system.appdatadir, "imageitem.json")
        if len(imagelist) == 0:
            print("No wallpapers available")
            return
        imageindex = 0
        if os.path.isfile(imageitem_jsonfile_path):
            file = open(imageitem_jsonfile_path, "rb")
            filecontent = file.read().decode("utf-8")
            file.close()
            oldimageitem = json.loads(filecontent)
            oldimageindex = oldimageitem["index"]
            if oldimageindex >= len(imagelist) or oldimageitem["hsh"] != imagelist[oldimageindex]:
                imageindex = (oldimageindex + 1) % len(imagelist)
        imageitem = imagelist[imageindex]
        imageitem["index"] = imageindex
        imageitem_json_str = json.dumps(imageitem)
        file = open(imageitem_jsonfile_path, "wb")
        file.write(imageitem_json_str.encode("utf-8"))
        file.close()
        imagedata = requests.get("https://cn.bing.com" + imageitem["url"]).content
        postfix = imageitem["url"].split(".")[-1]
        imagedata_savepath = os.path.join(system.appdatadir, "download."+postfix)
        file = open(imagedata_savepath, "wb")
        file.write(imagedata)
        file.close()
        set_wallpaper(ImageItem(imagedata_savepath))
        self.imageitem = imageitem

    def updateWidgetStyles(self):
        textstyles = ""
        if self.mouseEnterred:
            textstyles += "background-color: %s;" % self.bgcolor_hover
        else:
            textstyles += "background-color: %s;" % self.bgcolor
        textstyles += "border: none;"
        textstyles += "color: %s;" % self.txtcolor
        textstyles += "padding: %dpx;" % self.txtpadding
        textstyles += "font-size: %dpx;" % self.fontsize
        textstyles += "font-family: %s;" % self.fontfamily
        self.text.setStyleSheet(textstyles)
        if self.mousePressPos:
            self.setCursor(Qt.ClosedHandCursor)
        else:
            self.setCursor(Qt.OpenHandCursor)

    def saveWindowPosition(self, pos):
        savingfilepath = os.path.join(system.appdatadir, "window-position.txt")
        file = open(savingfilepath, "w")
        file.write("%d,%d" % (pos.x(),pos.y()))
        file.close()

    def loadWindowPosition(self, default=None):
        savingfilepath = os.path.join(system.appdatadir, "window-position.txt")
        if os.path.isfile(savingfilepath):
            file = open(savingfilepath, "r")
            filecontent = file.read()
            file.close()
            values = [int(word.strip()) for word in filecontent.split(",")]
            return QPoint(values[0], values[1])
        else:
            return default
