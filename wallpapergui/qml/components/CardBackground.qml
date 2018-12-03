import QtQuick 2.0
import QtQuick.Controls 2.4

Rectangle {
  id: rect
  property alias mousearea: rect_ma
  anchors.fill: parent
  color: rect_ma.containsMouse ? "#d0000000" : "#b0000000"
  MouseArea {
    id: rect_ma
    hoverEnabled: true
    anchors.fill: parent
    cursorShape: this.pressed ? Qt.ClosedHandCursor : Qt.OpenHandCursor
  }
}