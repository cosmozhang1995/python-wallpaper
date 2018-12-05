import QtQuick 2.11
import QtQuick.Layouts 1.11
import QtQuick.Controls 2.4
import QtQml 2.11

import "./components"

Item {
  id: root
  width: rootlayout.width + 10
  height: rootlayout.height + 10
  property bool dragging: title_button.mousearea.pressed
  property bool showbuttons: mousearea.containsMouse || rootlayout.hover
  MouseArea {
    id: mousearea
    hoverEnabled: true
    anchors.fill: rootlayout
  }
  Timer {
    interval: 1000
    repeat: true
    running: true
    onTriggered: {
      console.log(title_button.width, title_button.height)
    }
  }
  Column {
    id: rootlayout
    spacing: 5
    property bool hover: false
    anchors.left: parent.left
    anchors.top: parent.top
    anchors.margins: 5
    property bool _entered: false
    signal entered()
    signal exited()
    Timer {
      id: delayedExitTimer
      interval: 100
      repeat: false
      onTriggered: function() {
        if (rootlayout._entered) {
          rootlayout._entered = false;
          rootlayout.exited();
        }
      }
    }
    function delayedExit() {
      cancelDelayedExit();
      delayedExitTimer.start();
    }
    function cancelDelayedExit() {
      if (delayedExitTimer.running) {
        delayedExitTimer.stop();
      }
    }
    Connections {
      target: holder
      onMouseMoved: function(event) {
        if (event.x >= rootlayout.x && event.x < rootlayout.x + rootlayout.width &&
            event.y >= rootlayout.y && event.y < rootlayout.y + rootlayout.height) {
          if (!rootlayout._entered) {
            rootlayout._entered = true;
            rootlayout.entered();
          } else {
            rootlayout.cancelDelayedExit();
          }
        } else {
          rootlayout.delayedExit();
        }
      }
      onMouseExited: function() {
        rootlayout.delayedExit();
      }
    }
    Connections {
      target: rootlayout
      onEntered: { rootlayout.hover = true; }
      onExited: { rootlayout.hover = false; }
    }
    Item {
      id: content_block_upper
      // visible: fabutton_info.active
      visible: root.showbuttons
      height: content_block_upper_cardtext.height
      width: mainrow.width
      CardBackground {
        id: content_block_upper_cardbg
        anchors.fill: content_block_upper_cardtext
      }
      CardText {
        id: content_block_upper_cardtext
        width: parent.width
        wrapMode: Text.WordWrap
        text: holder.content
        topPadding: 10
        bottomPadding: 10
      }
    }
    RowLayout {
      id: mainrow
      spacing: 5
      BlockButton {
        id: title_button
        text: holder.title
        Layout.minimumWidth: 250
        Layout.maximumWidth: 400
        Layout.preferredWidth: this.cardtext.contentWidth
        cardtext.width: this.width
      }
      FAButton {
        id: fabutton_config
        visible: root.showbuttons
        text: this.icon_sliders_h
        Layout.fillHeight: true
        Connections {
          target: fabutton_config.mousearea
          onClicked: { holder.onButtonSettings() }
        }
      }
      FAButton {
        id: fabutton_refresh
        visible: root.showbuttons
        text: this.icon_sync_alt
        Layout.fillHeight: true
        Connections {
          target: fabutton_refresh.mousearea
          onClicked: { holder.onButtonRefresh() }
        }
      }
    }
  }
}


