import QtQuick 2.11
import QtQuick.Layouts 1.11
import QtQuick.Controls 2.4

import "./components"

ColumnLayout {
  id: root
  spacing: 5
  property bool dragging: title_button.mousearea.pressed
  RowLayout {

  }
  RowLayout {
    spacing: 5
    height: 40
    BlockButton {
      id: title_button
      text: "Hello World"
      Layout.minimumWidth: 200
      Layout.maximumWidth: 300
      Layout.fillHeight: true
    }
    FAButton {
      text: "\uf1de"
      Layout.fillHeight: true
      Layout.preferredWidth: this.height
    }
  }
}
