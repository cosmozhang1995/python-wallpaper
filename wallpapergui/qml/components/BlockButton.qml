import QtQuick 2.0
import QtQuick.Controls 2.4

Item {
  id: root
  height: 40
  width: cardtext.width
  property alias text: cardtext.text
  property alias font: cardtext.font
  property alias label: cardtext
  property alias mousearea: cardbg.mousearea
  CardBackground {
    id: cardbg
    anchors.fill: parent
  }
  CardText {
    id: cardtext
    text: "Hello World"
    anchors.verticalCenter: parent.verticalCenter
  }
}