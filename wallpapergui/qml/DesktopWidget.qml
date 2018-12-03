import QtQuick 2.11
import QtQuick.Layouts 1.11
import QtQuick.Controls 2.4

import "./components"

Item {
  id: root
  width: rootlayout.width + 10
  height: rootlayout.height + 10
  property bool dragging: title_button.mousearea.pressed
  property bool showbuttons: !this.dragging && (mousearea.containsMouse || rootlayout.hover) // && !this.dragging
  signal mouseEntered()
  signal mouseMoved()
  signal mouseExited()
  MouseArea {
    id: mousearea
    hoverEnabled: true
    anchors.fill: rootlayout
  }
  ColumnLayout {
    id: rootlayout
    spacing: 5
    property bool hover: title_button.mousearea.containsMouse || fabutton.mousearea.containsMouse
    anchors.left: parent.left
    anchors.top: parent.top
    anchors.margins: 5
    Component {
      id: connectionBlockButton
      Connections {
        target: parent.mousearea
        function detectShownButtons() { fabutton.visible = !root.dragging && (mousearea.containsMouse || rootlayout.hover); }
        onEntered: { rootlayout.hover = true; detectShownButtons(); }
        onExited: { rootlayout.hover = false; detectShownButtons(); }
      }
    }
    RowLayout {
    }
    RowLayout {
      spacing: 5
      BlockButton {
        id: title_button
        text: "Hello World"
        Layout.minimumWidth: 200
        Layout.maximumWidth: 300
        // Loader { sourceComponent: connectionBlockButton }
      }
      FAButton {
        id: fabutton
        visible: false
        text: "\uf1de"
        Layout.fillHeight: true
        // Loader { sourceComponent: connectionBlockButton }
      }
    }
  }
}


