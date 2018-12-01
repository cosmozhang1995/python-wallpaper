import QtQuick 2.11
import QtQuick.Layouts 1.11
import QtQuick.Controls 2.4

import "./components"

Column {
  padding: 5
  spacing: 5
  Row {
    padding: 5
    spacing: 5
    BlockButton {
      text: "Hello World\u4f60"
    }
    FAButton {
      text: "\uf1de"
    }
  }
}
