import QtQuick 2.0
import QtQuick.Controls 2.4

BlockButton {
  id: root
  readonly property string icon_sliders_h: "\uf1de"
  readonly property string icon_question: "\uf128"
  readonly property string icon_sync_alt: "\uf2f1"
  font.family: "Font Awesome 5 Free"
  width: this.height
  label.hpadding: 0
  label.anchors.horizontalCenter: label.parent.horizontalCenter
  cardtext.horizontalAlignment: Text.AlignHCenter
}