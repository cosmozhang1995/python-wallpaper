import QtQuick 2.0
import QtQuick.Controls 2.4

Label {
  id: label
  property alias text: label.text
  property alias font: label.font
  color: "white"
  text: ""
  font.family: "\"Segoe UI\", Arial"
  font.pixelSize: 18
  leftPadding: 10
  rightPadding: 10
  lineHeight: 40
  lineHeightMode: Text.FixedHeight
  verticalAlignment: Text.AlignVCenter
  background: Rectangle {
    id: rect
    color: rect_ma.containsMouse ? "#d0000000" : "#b0000000"
    MouseArea {
      id: rect_ma
      hoverEnabled: true
      anchors.fill: parent
      cursorShape: this.pressed ? Qt.ClosedHandCursor : Qt.OpenHandCursor
    }
  }
}