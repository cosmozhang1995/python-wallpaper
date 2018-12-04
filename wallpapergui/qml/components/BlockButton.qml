import QtQuick 2.0
import QtQuick.Controls 2.4

Item {
  id: root
  height: 40
  property alias text: cardtext.text
  property alias font: cardtext.font
  property alias label: cardtext
  property alias mousearea: cardma
  property alias cardtext: cardtext
  property alias active: cardbg.active
  CardBackground {
    id: cardbg
    anchors.fill: parent
    mousearea: cardma
  }
  CardText {
    id: cardtext
    text: "Hello World"
    anchors.verticalCenter: parent.verticalCenter
    elide: Text.ElideRight
    clip: true
  }
  CardMouseArea {
    id: cardma
  }
}