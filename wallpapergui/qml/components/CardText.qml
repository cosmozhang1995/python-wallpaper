import QtQuick 2.11
import QtQuick.Controls 2.4

Text {
  id: label
  property int hpadding: 15
  color: "white"
  text: ""
  font.family: "\"Segoe UI\", Arial"
  font.pixelSize: 18
  leftPadding: this.hpadding
  rightPadding: this.hpadding
  lineHeight: 24
  lineHeightMode: Text.FixedHeight
  verticalAlignment: Text.AlignVCenter
}