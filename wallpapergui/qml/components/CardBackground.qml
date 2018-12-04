import QtQuick 2.11
import QtQuick.Controls 2.4

Rectangle {
  id: rect
  property MouseArea mousearea: null
  property bool active: false
  anchors.fill: parent
  color: (this.active || (this.mousearea && this.mousearea.containsMouse)) ? "#d0000000" : "#b0000000"
}