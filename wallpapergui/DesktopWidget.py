import sys,os

from PyQt5.QtCore import Qt, QObject, pyqtSlot, QPoint, QSize, QUrl, QEvent, QTimer
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QPainter, QColor, QIcon, QMouseEvent, QResizeEvent, QFont

import requests
import json
import datetime
import time
import ctypes
from ctypes import wintypes

from wallpaper.wallpaper import set_wallpaper
from wallpaper.userconfig import UserConfig
from wallpaper.system import system
from wallpaper.manager.bing import BingManager

from .utils import setTimeout
from .geo import Rect, Point

class WINDOWPOS(ctypes.Structure):
    _fields_ = [("hwnd", wintypes.HWND),
                ("hwndInsertAfter", wintypes.HWND),
                ("x", ctypes.c_int),
                ("y", ctypes.c_int),
                ("cx", ctypes.c_int),
                ("cy", ctypes.c_int),
                ("flags", ctypes.c_uint)]

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

class DesktopWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.hParent = 0
        self.ready = False
        # properties
        self.userconfig = UserConfig()
        self.manager = BingManager()
        self.wallpaperitem = None
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.onTimerTimeout)
        self.timerClear = True
        # mouse dragging properties
        self.dragging = False
        self.mousePressPos = None
        self.mousePressWindowPos = QPoint(100,100)
        self.windowPosition = self.loadWindowPosition(None)
        self.holdWindowPosition = False
        if self.windowPosition is None:
            monitor = MonitorInfo.get(primary=True)
            self.windowPosition = WindowPosition(monitor=monitor, x=0, y=0, width=0, height=0, anchor=WindowPosition.ANCHOR_LEFT|WindowPosition.ANCHOR_TOP)
        # set as frameless transparent window
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        # build layout
        self.buildLayout()
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
        # action_close = QAction(menu)
        # action_close.setText("Close")
        # action_close.triggered.connect(self.onTrayActionClose)
        # menu.addAction(action_close)
        # self.systemTrayMenu = menu
        # self.systemTray.setContextMenu(self.systemTrayMenu)

    def buildLayout(self):
        self.setStyleSheet("""
            QLabel,
            QPushButton {
                font-size: 18px;
                font-family: "Segoe UI", Arial;
                background-color: rgba(0,0,0,192);
                color: white;
                padding: 5
            }
            QPushButton {
                font: "Font Awesome 5 Free";
            }
            QPushButton:hover {
                background-color: rgba(0,0,0,224);
            }
            """)
        self.layout = QVBoxLayout()
        class CHBoxLayout(QHBoxLayout):
            def minimumSize(self):
                size = super().minimumSize()
                return QSize(250, size.height())
            def maximumSize(self):
                size = super().maximumSize()
                return QSize(400, size.height())
        self.layoutUpper = CHBoxLayout()
        self.labelUpper = QLabel()
        self.layoutUpper.addWidget(self.labelUpper)
        self.layout.addLayout(self.layoutUpper)
        self.layoutMiddle = CHBoxLayout()
        self.labelTitle = QLabel("Hello World")
        self.labelTitle.setFixedHeight(40)
        self.layoutMiddle.addWidget(self.labelTitle)
        buttonfont = QFont()
        buttonfont.setFamily("Font Awesome 5 Free")
        buttonfont.setPointSize(18)
        self.buttonSettings = QPushButton()
        self.buttonSettings.setFont(buttonfont)
        self.buttonSettings.setText("\uf1de")
        self.buttonSettings.setFixedSize(40,40)
        self.layoutMiddle.addWidget(self.buttonSettings)
        self.buttonRefresh = QPushButton()
        self.buttonRefresh.setFont(buttonfont)
        self.buttonRefresh.setText("\uf2f1")
        self.buttonRefresh.setFixedSize(40,40)
        self.layoutMiddle.addWidget(self.buttonRefresh)
        self.layout.addLayout(self.layoutMiddle)
        self.setLayout(self.layout)


    def calculateWindowPosition(self, force_anchor=0):
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
        if rect.hcenter < monitor.work.hcenter or force_anchor & WindowPosition.ANCHOR_LEFT:
            anchor |= WindowPosition.ANCHOR_LEFT
            posx = rect.left
        elif rect.hcenter > monitor.work.hcenter or force_anchor & WindowPosition.ANCHOR_RIGHT:
            anchor |= WindowPosition.ANCHOR_RIGHT
            posx = rect.right
        else:
            anchor |= WindowPosition.ANCHOR_HCENTER
            posx = rect.hcenter
        if rect.vcenter < monitor.work.vcenter or force_anchor & WindowPosition.ANCHOR_TOP:
            anchor |= WindowPosition.ANCHOR_TOP
            posy = rect.top
        elif rect.vcenter > monitor.work.vcenter or force_anchor & WindowPosition.ANCHOR_BOTTOM:
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
        # resultgeo = Rect(winpos.left + winpos.monitor.work.left - rectDesktop.left, winpos.top + winpos.monitor.work.top - rectDesktop.top, width=winpos.width, height=winpos.height)
        resultgeo = Rect(winpos.left + winpos.monitor.work.left - rectDesktop.left, winpos.top + winpos.monitor.work.top - rectDesktop.top, width=self.sizeHint().width(), height=self.sizeHint().height())
        # print("resultgeo", resultgeo.left, resultgeo.top, resultgeo.width, resultgeo.height)
        win32gui.MoveWindow(self.winId(), resultgeo.left, resultgeo.top, resultgeo.width, resultgeo.height, True)
        if self.hParent and not self.holdWindowPosition:
            self.windowPosition = self.calculateWindowPosition()
            # print("moveWindow", self.windowPosition.left, self.windowPosition.top)

    def nativeEvent(self, eventType, message):
        msg = wintypes.MSG.from_address(int(message))
        if self.ready:
            if eventType==b'windows_generic_MSG':
                if msg.message == win32con.WM_WINDOWPOSCHANGING:
                    params = WINDOWPOS.from_address(int(msg.lParam))
                    print("WM_WINDOWPOSCHANGING", int(params.hwndInsertAfter))
                    params.hwndInsertAfter = win32con.HWND_BOTTOM
                    # winId = self.winId()
                    # if not winId is None:
                    #     print("Move to bottom")
                    #     win32gui.SetWindowPos(self.winId(), win32con.HWND_BOTTOM, 0, 0, 0, 0, win32con.SWP_NOMOVE|win32con.SWP_NOSIZE)
        return super().nativeEvent(eventType, message)

    def show(self):
        super().show()
        # hDesktop = findDesktopIconWnd()
        # win32gui.SetParent(self.winId(), hDesktop)
        # self.hParent = hDesktop
        # lWinStyle = win32gui.GetWindowLong(self.winId(), win32con.GWL_STYLE)
        # lWinStyle = lWinStyle & (~win32con.WS_CAPTION)
        # lWinStyle = lWinStyle & (~win32con.WS_SYSMENU)
        # lWinStyle = lWinStyle & (~win32con.WS_MAXIMIZEBOX)
        # lWinStyle = lWinStyle & (~win32con.WS_MINIMIZEBOX)
        # lWinStyle = lWinStyle & (~win32con.WS_SIZEBOX)
        # win32gui.SetWindowLong(self.winId(), win32con.GWL_STYLE, lWinStyle)
        # print(hDesktop, self.winId())
        # def delayedMove():
        #     self.moveWindow(self.windowPosition)
        # setTimeout(delayedMove, 0.01)
        # # self.moveWindow(self.windowPosition)
        # # self.timer.start()
        def delayedReady():
            self.ready = True
        setTimeout(delayedReady, 0.01)

    def onTrayActionClose(self):
        self.close()
    def onTrayActionChange(self):
        self.changeWallpaper()
    def onTrayActionReload(self):
        self.web.reload()
        self.web.page().setWebChannel(self.webchan)

    # def moveEvent(self, event):
    #     super().moveEvent(event)
    #     winpos = self.calculateWindowPosition()
    #     print("moveEvent", winpos.left, winpos.top, self.windowPosition.left, self.windowPosition.top)
    #     if winpos.left != self.windowPosition.left or winpos.top != self.windowPosition.top or winpos.width != self.windowPosition.width or winpos.height != self.windowPosition.height:
    #         self.moveWindow(self.windowPosition)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.labelUpper.setVisible(True)
    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.labelUpper.setVisible(False)
        self.labelTitle.setText("HHHH")
        self.update()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.dragging = True
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.mousePressPos:
            pos = Point(qpoint=event.globalPos())
            dx = pos.x - self.mousePressPos.x
            dy = pos.y - self.mousePressPos.y
            winpos = self.mousePressWindowPos.copy()
            winpos.x += dx
            winpos.y += dy
            self.moveWindow(winpos)
        elif self.dragging:
            self.mousePressPos = Point(qpoint=event.globalPos())
            self.mousePressWindowPos = self.calculateWindowPosition(force_anchor=WindowPosition.ANCHOR_LEFT|WindowPosition.ANCHOR_TOP)
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.dragging = False
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
            self.saveWindowPosition(self.calculateWindowPosition())



    def resizeEvent(self, event):
        print("resizeEvent")
        super().resizeEvent(event)
        # print("onResizeEvent", event.oldSize(), event.size(), self.quick.sizeHint())
        # winpos = self.windowPosition.copy()
        # print("get windowPosition", self.windowPosition.width, self.windowPosition.height)
        # if not self.hParent:
        #     # this is the initialization of windowPosition
        #     winpos.width = self.width()
        #     winpos.height = self.height()
        #     self.windowPosition = winpos
        # else:
        #     print("before resize", winpos.width, winpos.height)
        #     winpos.width += event.size().width() - event.oldSize().width()
        #     winpos.height += event.size().height() - event.oldSize().height()
        #     print("after resize", winpos.width, winpos.height)
        #     self.moveWindow(winpos)

    def onHoldWindowPosition(self, holding):
        self.holdWindowPosition = holding

    def setupTimer(self):
        if self.manager.status.updatetime is None:
            self.changeWallpaper()
        else:
            dt = datetime.datetime.now() - self.manager.status.updatetime
            if dt > datetime.timedelta(0):
                self.timer.stop()
                self.timer.start(dt.seconds*1000)
            else:
                self.changeWallpaper()

    def changeWallpaper(self, with_update=True):
        wallpaperitem = self.manager.random()
        if wallpaperitem is None:
            self.manager.update(lambda: self.changeWallpaper(with_update=False))
        else:
            set_wallpaper(wallpaperitem.imagepath)
            self.quick.holder.wallpaperInfo = wallpaperitem.info
            if with_update:
                self.manager.update()
            self.timerClear = True

    @pyqtSlot()
    def onTimerTimeout(self):
        # print("DesktopWidget", self.width(), self.height())
        if not self.timerClear: return
        if self.manager.status.updatetime is None:
            self.changeWallpaper()
        else:
            dt = datetime.datetime.now() - self.manager.status.updatetime
            if dt > datetime.timedelta(seconds=self.userconfig.interval):
                self.changeWallpaper()


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
            if monitor is None:
                monitor = MonitorInfo.get(primary=True)
            return WindowPosition(monitor=monitor, x=int(values[1]), y=int(values[2]), width=int(values[3]), height=int(values[4]), anchor=int(values[5]))
        else:
            return default

    @pyqtSlot()
    def onButtonSettings(self):
        pass
    @pyqtSlot()
    def onButtonRefresh(self):
        self.changeWallpaper()





