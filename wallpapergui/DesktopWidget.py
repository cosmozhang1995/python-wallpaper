import sys,os

from PySide2.QtCore import Qt, QObject, Signal, Slot, QPoint, QUrl, QEvent
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QSystemTrayIcon, QMenu, QAction
from PySide2.QtGui import QPainter, QColor, QIcon
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWebChannel import QWebChannel

import requests
import json

from wallpaper.wallpaper import set_wallpaper
from wallpaper.image import ImageItem
from wallpaper.system import system
from wallpaper.manager.bing import BingManager

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
        self.fontfamily = "\"Segoe UI\", Arial"
        # self.fontfamily = "\"Microsoft YaHei\", Arial";
        # other properties
        self.manager = BingManager()
        self.imageitem = None
        # mouse dragging properties
        self.mousePressPos = None
        self.mousePressWindowPos = QPoint(100,100)
        self.mouseEnterred = False
        self._windowPosition = self.loadWindowPosition(QPoint(0,0))
        self.hidden = True
        # build layout
        self.webchandelegate = DesktopWidget.WebChannelDelegate(self)
        self.webchan = QWebChannel()
        self.webchan.registerObject("context", self.webchandelegate)
        self.web = QWebEngineView()
        self.web.load(QUrl.fromLocalFile(os.path.join(system.execpath, "wallpapergui", "www", "DesktopWidget.html")))
        self.web.page().setWebChannel(self.webchan)
        self.web.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.web.setStyleSheet("background:transparent")
        self.web.page().setBackgroundColor(QColor(0,0,0,0))
        self.layout = QVBoxLayout()
        self.layout.setMargin(0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.web)
        self.setLayout(self.layout)
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
        action_reload = QAction(menu)
        action_reload.setText("Reload")
        action_reload.triggered.connect(self.onTrayActionReload)
        menu.addAction(action_reload)
        action_close = QAction(menu)
        action_close.setText("Close")
        action_close.triggered.connect(self.onTrayActionClose)
        menu.addAction(action_close)
        self.systemTrayMenu = menu
        self.systemTray.setContextMenu(self.systemTrayMenu)

    @property
    def windowPosition(self):
        if not self.hidden and self.isVisible():
            h = self.winId()
            hDesktop = findDesktopIconWnd()
            rect = win32gui.GetWindowRect(h)
            rectDesktop = win32gui.GetWindowRect(hDesktop)
            self._windowPosition = QPoint(rect[0] - rectDesktop[0], rect[1] - rectDesktop[1])
        return self._windowPosition
    

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
        win32gui.MoveWindow(self.winId(), self.windowPosition.x(), self.windowPosition.y(), self.width(), self.height(), True)
        print(hDesktop, self.winId())
        self.hidden = False

    def onTrayActionClose(self):
        self.close()
    def onTrayActionChange(self):
        self.changeWallpaper()
    def onTrayActionReload(self):
        self.web.reload()
        self.web.page().setWebChannel(self.webchan)

    class WebChannelDelegate(QObject):
        def __init__(self, parent):
            super().__init__(parent)
            self.onDebug.connect(parent.onDebug)
            self.onMousePressEvent.connect(parent.onMousePressEvent)
            self.onMouseMoveEvent.connect(parent.onMouseMoveEvent)
            self.onMouseReleaseEvent.connect(parent.onMouseReleaseEvent)
            self.onResizeWindow.connect(parent.onResizeWindow)
        onDebug = Signal(str)
        @Slot(str)
        def debug(self, operation):
            self.onDebug.emit(operation)
        onMousePressEvent = Signal(int, int)
        @Slot(int, int)
        def mousePressEvent(self, x, y):
            self.onMousePressEvent.emit(x,y)
        onMouseMoveEvent = Signal(int, int)
        @Slot(int, int)
        def mouseMoveEvent(self, x, y):
            self.onMouseMoveEvent.emit(x,y)
        onMouseReleaseEvent = Signal(int, int)
        @Slot(int, int)
        def mouseReleaseEvent(self, x, y):
            self.onMouseReleaseEvent.emit(x,y)
        onResizeWindow = Signal(int, int)
        @Slot(int, int)
        def resizeWindow(self, w, h):
            self.onResizeWindow.emit(w,h)

    def onDebug(self, operation):
        eval(operation)
    def onResizeWindow(self, w, h):
        win32gui.MoveWindow(self.winId(), self.windowPosition.x(), self.windowPosition.y(), w, h, True)

    def onMousePressEvent(self, x, y):
        self.mousePressPos = QPoint(x,y)
        self.mousePressWindowPos = self.windowPosition
    def onMouseMoveEvent(self, x, y):
        if self.mousePressPos:
            pos = QPoint(x,y)
            dx = pos.x() - self.mousePressPos.x()
            dy = pos.y() - self.mousePressPos.y()
            win32gui.MoveWindow(self.winId(), self.mousePressWindowPos.x() + dx, self.mousePressWindowPos.y() + dy, self.width(), self.height(), True)
    def onMouseReleaseEvent(self, x, y):
        if self.mousePressPos:
            pos = QPoint(x,y)
            self.mousePressWindowPos += pos - self.mousePressPos
            self.mousePressPos = None
            self.saveWindowPosition(self.windowPosition)

    def changeWallpaper(self):
        def callback():
            self.imageitem = self.manager.next()
            set_wallpaper(self.imageitem.imagepath)
            print("here we set wallpaper")
        self.manager.update(callback)


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
