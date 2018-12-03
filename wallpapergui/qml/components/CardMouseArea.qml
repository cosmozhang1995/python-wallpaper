import QtQuick 2.11
import QtQuick.Controls 2.4

MouseArea {
  id: mousearea
  hoverEnabled: true
  anchors.fill: parent
  cursorShape: this.pressed ? Qt.ClosedHandCursor : Qt.OpenHandCursor
}