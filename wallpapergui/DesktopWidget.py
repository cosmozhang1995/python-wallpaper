import sys,os

from PySide2.QtCore import Qt, QObject, Signal, Slot, QPoint, QSize, QUrl, QEvent
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QSystemTrayIcon, QMenu, QAction
from PySide2.QtGui import QPainter, QColor, QIcon
from PySide2.QtQuickWidgets import QQuickWidget

import requests
import json

from wallpaper.wallpaper import set_wallpaper
from wallpaper.image import ImageItem
from wallpaper.system import system
from wallpaper.manager.bing import BingManager

from .geo import Rect, Point

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
    # return 0x10010 # this is the root

class MonitorInfo:
    def __init__(self, winapi_monitorinfo):
        self.monitor = Rect(left   = winapi_monitorinfo["Monitor"][0],
                            top    = winapi_monitorinfo["Monitor"][1],
                            right  = winapi_monitorinfo["Monitor"][2],
                            bottom = winapi_monitorinfo["Monitor"][3])
        self.work = Rect(left   = winapi_monitorinfo["Work"][0],
                         top    = winapi_monitorinfo["Work"][1],
                         right  = winapi_monitorinfo["Work"][2],
                         bottom = winapi_monitorinfo["Work"][3])
        self.flag = winapi_monitorinfo["Flags"]
        self.device = winapi_monitorinfo["Device"]
    @property
    def primary(self):
        return bool(self.flag & win32con.MONITORINFOF_PRIMARY)
    @classmethod
    def all(cls):
        return [MonitorInfo(win32api.GetMonitorInfo(item[0])) for item in win32api.EnumDisplayMonitors(None, None)]
    @classmethod
    def get(cls, primary=None, device=None):
        monitors = [MonitorInfo(win32api.GetMonitorInfo(item[0])) for item in win32api.EnumDisplayMonitors(None, None)]
        for monitor in monitors:
            if primary and not monitor.primary: continue
            if device and not monitor.device == device: continue
            return monitor
        return None

class WindowPosition:
    ANCHOR_LEFT = 1 << 0
    ANCHOR_HCENTER = 1 << 1
    ANCHOR_RIGHT = 1 << 2
    ANCHOR_TOP = 1 << 3
    ANCHOR_VCENTER = 1 << 4
    ANCHOR_BOTTOM = 1 << 5
    def __init__(self, monitor=0, x=0, y=0, width=0, height=0, anchor=None):
        if anchor is None: anchor = WindowPosition.ANCHOR_LEFT | WindowPosition.ANCHOR_TOP
        self.monitor = monitor
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.anchor = anchor
    def copy(self):
        return WindowPosition(monitor=self.monitor, x=self.x, y=self.y, width=self.width, height=self.height, anchor=self.anchor)
    @property
    def left(self):
        if self.anchor & WindowPosition.ANCHOR_LEFT:
            return self.x
        elif self.anchor & WindowPosition.ANCHOR_RIGHT:
            return self.x - self.width
        else:
            return int(self.x - self.width/2)
    @property
    def right(self):
        return self.left + self.width
    @property
    def top(self):
        if self.anchor & WindowPosition.ANCHOR_TOP:
            return self.y
        elif self.anchor & WindowPosition.ANCHOR_BOTTOM:
            return self.y - self.height
        else:
            return int(self.y - self.height/2)
    @property
    def bottom(self):
        return self.top + self.height

class DesktopWidget(QQuickWidget):
    def __init__(self):
        super().__init__()
        self.hParent = 0
        # default styles
        self.bgcolor = "rgba(0,0,0,172)" # QColor(0, 0, 0, 0x99)
        self.bgcolor_hover = "rgba(0,0,0,204)" # QColor(0, 0, 0, 0xcc)
        self.txtcolor = "#ffffff" # QColor(255, 255, 255)
        self.txtpadding = 8
        self.fontsize = 18
        self.fontfamily = "\"Segoe UI\", Arial"
        # self.fontfamily = "\"Microsoft YaHei\", Arial";
        # other properties
        self.manager = BingManager()
        self.imageitem = None
        # mouse dragging properties
        self.mousePressPos = None
        self.mousePressWindowPos = QPoint(100,100)
        self.mouseEnterred = False
        self.windowPosition = self.loadWindowPosition(None)
        self.holdWindowPosition = False
        if self.windowPosition is None:
            monitor = MonitorInfo.get(primary=True)
            self.windowPosition = WindowPosition(monitor=monitor, x=0, y=0, width=0, height=0, anchor=WindowPosition.ANCHOR_LEFT|WindowPosition.ANCHOR_TOP)
        # set as frameless transparent window
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        # self.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        self.setClearColor(Qt.transparent)
        # self.setAutoFillBackground(True)
        # self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        # load qml source
        qmlsrc = QUrl.fromLocalFile(os.path.join(os.path.dirname(system.abspath(__file__)), "qml", "DesktopWidget.qml"))
        self.setSource(qmlsrc)
        # # build system tray menu
        # self.systemTray = QSystemTrayIcon(self)
        # self.systemTray.setIcon(QIcon("images/bing.png"))
        # self.systemTray.setToolTip("Bing Wallpaper")
        # self.systemTray.show()
        # menu = QMenu(self)
        # action_change = QAction(menu)
        # action_change.setText("Change Wallpaper")
        # action_change.triggered.connect(self.onTrayActionChange)
        # menu.addAction(action_change)
        # action_reload = QAction(menu)
        # action_reload.setText("Reload")
        # action_reload.triggered.connect(self.onTrayActionReload)
        # menu.addAction(action_reload)
        # action_close = QAction(menu)
        # action_close.setText("Close")
        # action_close.triggered.connect(self.onTrayActionClose)
        # menu.addAction(action_close)
        # self.systemTrayMenu = menu
        # self.systemTray.setContextMenu(self.systemTrayMenu)

    def calculateWindowPosition(self):
        h = self.winId()
        rect = Rect(winapi_rect=win32gui.GetWindowRect(h))
        monitors = MonitorInfo.all()
        overlaps = [(rect & monitor.work) for monitor in monitors]
        overlapareas = [(region.area if region else -1) for region in overlaps]
        imonitor = sorted(range(len(monitors)), key = lambda i: -overlapareas[i])[0]
        if overlapareas[imonitor] > 0 or not self.windowPosition:
            monitor = monitors[imonitor]
        else:
            monitor = self.windowPosition.monitor
        anchor = 0
        if rect.hcenter < monitor.work.hcenter:
            anchor |= WindowPosition.ANCHOR_LEFT
            posx = rect.left
        elif rect.hcenter > monitor.work.hcenter:
            anchor |= WindowPosition.ANCHOR_RIGHT
            posx = rect.right
        else:
            anchor |= WindowPosition.ANCHOR_HCENTER
            posx = rect.hcenter
        if rect.vcenter < monitor.work.vcenter:
            anchor |= WindowPosition.ANCHOR_TOP
            posy = rect.top
        elif rect.vcenter > monitor.work.vcenter:
            anchor |= WindowPosition.ANCHOR_BOTTOM
            posy = rect.bottom
        else:
            anchor |= WindowPosition.ANCHOR_HCENTER
            posy = rect.vcenter
        posx -= monitor.work.left
        posy -= monitor.work.top
        return WindowPosition(monitor=monitor, x=posx, y=posy, width=rect.width, height=rect.height, anchor=anchor)


    def moveWindow(self, winpos):
        hDesktop = findDesktopIconWnd()
        rectDesktop = Rect(winapi_rect=win32gui.GetWindowRect(hDesktop))
        # win32gui.MoveWindow(self.winId(), winpos.left + winpos.monitor.work.left - rectDesktop.left, winpos.top + winpos.monitor.work.top - rectDesktop.top, winpos.width, winpos.height, True)
        win32gui.MoveWindow(self.winId(), winpos.left + winpos.monitor.work.left - rectDesktop.left, winpos.top + winpos.monitor.work.top - rectDesktop.top, self.width(), self.height(), True)
        if not self.holdWindowPosition:
            self.windowPosition = self.calculateWindowPosition()

    def show(self):
        super().show()
        hDesktop = findDesktopIconWnd()
        win32gui.SetParent(self.winId(), hDesktop)
        self.hParent = hDesktop
        lWinStyle = win32gui.GetWindowLong(self.winId(), win32con.GWL_STYLE)
        lWinStyle = lWinStyle & (~win32con.WS_CAPTION)
        lWinStyle = lWinStyle & (~win32con.WS_SYSMENU)
        lWinStyle = lWinStyle & (~win32con.WS_MAXIMIZEBOX)
        lWinStyle = lWinStyle & (~win32con.WS_MINIMIZEBOX)
        lWinStyle = lWinStyle & (~win32con.WS_SIZEBOX)
        win32gui.SetWindowLong(self.winId(), win32con.GWL_STYLE, lWinStyle)
        self.moveWindow(self.windowPosition)
        print(hDesktop, self.winId())

    def onTrayActionClose(self):
        self.close()
    def onTrayActionChange(self):
        self.changeWallpaper()
    def onTrayActionReload(self):
        self.web.reload()
        self.web.page().setWebChannel(self.webchan)

    # def onResizeWindow(self, w, h):
    #     winpos = self.windowPosition.copy()
    #     winpos.width = w
    #     winpos.height = h
    #     self.moveWindow(winpos)

    def mousePressEvent(self, event):
        self.mousePressPos = Point(qpoint=event.globalPos())
        self.mousePressWindowPos = self.windowPosition
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if self.mousePressPos:
            pos = Point(qpoint=event.globalPos())
            dx = pos.x - self.mousePressPos.x
            dy = pos.y - self.mousePressPos.y
            winpos = self.mousePressWindowPos.copy()
            winpos.x += dx
            winpos.y += dy
            self.moveWindow(winpos)
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        if self.mousePressPos:
            pos = Point(qpoint=event.globalPos())
            dx = pos.x - self.mousePressPos.x
            dy = pos.y - self.mousePressPos.y
            winpos = self.mousePressWindowPos.copy()
            winpos.x += dx
            winpos.y += dy
            self.moveWindow(winpos)
            self.mousePressWindowPos = None
            self.mousePressPos = None
            self.saveWindowPosition(self.windowPosition)
        super().mouseReleaseEvent(event)

    def onHoldWindowPosition(self, holding):
        self.holdWindowPosition = holding

    def onRequestAnchorTopStatus(self, callback):
        self.web.page().runJavaScript("%s(%s);" % (callback, ("true" if (self.windowPosition.anchor & WindowPosition.ANCHOR_TOP) else "false")))

    def changeWallpaper(self):
        def callback():
            self.imageitem = self.manager.next()
            set_wallpaper(self.imageitem.imagepath)
        self.manager.update(callback)


    def saveWindowPosition(self, pos):
        savingfilepath = os.path.join(system.appdatadir, "window-position.txt")
        file = open(savingfilepath, "w")
        file.write("%s,%d,%d,%d,%d,%d" % (pos.monitor.device, pos.x, pos.y, pos.width, pos.height, pos.anchor))
        file.close()

    def loadWindowPosition(self, default=None):
        savingfilepath = os.path.join(system.appdatadir, "window-position.txt")
        if os.path.isfile(savingfilepath):
            file = open(savingfilepath, "r")
            filecontent = file.read()
            file.close()
            values = [word.strip() for word in filecontent.split(",")]
            monitor = MonitorInfo.get(device=values[0])
            if monitor is None: monitor = MonitorInfo.get(primary=True)
            return WindowPosition(monitor=monitor, x=int(values[1]), y=int(values[2]), width=int(values[3]), height=int(values[4]), anchor=int(values[5]))
        else:
            return default
