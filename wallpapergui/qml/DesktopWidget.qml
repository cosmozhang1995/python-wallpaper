import QtQuick 2.11
import QtQuick.Layouts 1.11
import QtQuick.Controls 2.4

import "./components"

Item {
  id: root
  width: rootlayout.width
  height: rootlayout.height
  property bool dragging: title_button.mousearea.pressed
  property bool showbuttons: !this.dragging && (mousearea.containsMouse || rootlayout.containsMouse) // && !this.dragging
  MouseArea {
    id: mousearea
    hoverEnabled: true
    anchors.fill: rootlayout
  }
  ColumnLayout {
    id: rootlayout
    spacing: 5
    property bool containsMouse: title_button.mousearea.containsMouse || fabutton.mousearea.containsMouse
    RowLayout {
    }
    RowLayout {
      spacing: 5
      BlockButton {
        id: title_button
        text: "Hello World"
        Layout.minimumWidth: 200
        Layout.maximumWidth: 300
      }
      FAButton {
        id: fabutton
        visible: root.showbuttons
        text: "\uf1de"
        Layout.fillHeight: true
      }
    }
  }
}

