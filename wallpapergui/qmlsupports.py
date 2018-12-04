from PySide2.QtCore import QObject, Property, Signal
from PySide2.QtQml import qmlRegisterType
from .geo import Rect, Point

class QMLPackage:
    def __init__(self, name=None, versionmajor=0, versionminor=0):
        self.name = name
        self.versionmajor = versionmajor
        self.versionminor = versionminor
        self.registerredTypes = {}
    def registerType(self, typeClass, typeName):
        if not typeName in self.registerredTypes:
            qmlRegisterType(typeClass, self.name, self.versionmajor, self.versionminor, typeName)
            self.registerredTypes[typeName] = typeClass

def make_property(pname, pcls):
    def setter(self, val):
        return setattr(self, pname, val)
    def getter(self):
        return getattr(self, pname)
    changed = Signal(pcls)
    return Property(pname, read=getter, write=setter, notify=changed)

class MouseEvent(QObject):
    def __init__(self, qmouseevent=None, widget=None):
        super().__init__()
        widgetpos = Rect(qrect=widget.geometry()).lefttop if widget else Point(0,0)
        self._pos = Point(qpoint=qmouseevent.pos()) - widgetpos
        self._globalPos = Point(qpoint=qmouseevent.globalPos())
    def getX(self):
        return self._pos.x
    def setX(self, val):
        self._pos.x = val
        self.xChanged.emit(self.getX())
    xChanged = Signal(int)
    x = Property(int, getX, setX, notify=xChanged)
    def getY(self):
        return self._pos.y
    def setY(self, val):
        self._pos.y = val
        self.yChanged.emit(self.getY())
    yChanged = Signal(int)
    y = Property(int, getY, setY, notify=yChanged)
    def getGlobalX(self):
        return self._globalPos.x
    def setGlobalX(self, val):
        self._globalPos.x = val
        self.globalXChanged.emit(self.getGlobalX())
    globalXChanged = Signal(int)
    globalX = Property(int, getGlobalX, setGlobalX, notify=globalXChanged)
    def getGlobalY(self):
        return self._globalPos.y
    def setGlobalY(self, val):
        self._globalPos.y = val
        self.globalYChanged.emit(self.getGlobalY())
    globalYChanged = Signal(int)
    globalY = Property(int, getGlobalY, setGlobalY, notify=globalYChanged)

package = QMLPackage("com.pythondesktop", 1, 0)
package.registerType(MouseEvent, "MouseEvent")

from PySide2.QtGui import QMouseEvent
