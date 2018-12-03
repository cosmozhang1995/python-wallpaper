import QtQuick 2.11
import QtQuick.Controls 2.4

Item {
  id: mousearea
  property MouseArea garea: null
  signal clicked()
  signal pressed()
  signal released()
  signal doubleClicked()
  signal positionChanged()
  signal pressAndHold()
  Component.onCompleted: {
    Object.defineProperty(this, "hoverEnabled", {
        get: function() { return this._garea_availble && this.garea.hoverEnabled && this._hoverEnabled },
        set: function(val) { this._hoverEnabled = val; }
      });
  }
  property bool _isPressed: false;
  property bool _garea_availble: garea ? true : false
  property bool _hoverEnabled: false
  property bool _absContainsMouse: _garea_availble && garea.containsMouse && this.contains(Qt.point(garea.mouseX, garea.mouseY))
  property bool hasMouse: this.hoverEnabled ? this._absContainsMouse : this.isPressed && this._absContainsMouse
  property bool isPressed: this._isPressed
  property bool hoverEnabled: false
  property var cursorShape: Qt.ArrowCursor
  function _containsEventPosition (event) { return this.contains(Qt.point(event.x, event.y)); }
  Connections {
    target: garea
    onClicked: function(event) { if (mousearea._containsEventPosition(event)) mousearea.clicked(event); }
    onPressed: function(event) { if (mousearea._absContainsMouse) { mousearea.pressed(event); mousearea._isPressed = true; } }
    onReleased: function(event) { if (mousearea.isPressed) { mousearea.released(event); mousearea._isPressed = false; } }
    onDoubleClicked: function(event) { if (mousearea._containsEventPosition(event)) mousearea.doubleClicked(event); }
    onPositionChanged: function(event) { if (mousearea.hasMouse) mousearea.positionChanged(event); }
    onPressAndHold: function(event) { if (mousearea.hasMouse) mousearea.pressAndHold(event); }
  }
  Connections {
    target: mousearea
    onClicked: function() { console.log("onClicked") }
    onPressed: function() { console.log("onPressed") }
    onReleased: function() { console.log("onReleased") }
    onDoubleClicked: function() { console.log("onDoubleClicked") }
    onPositionChanged: function() { console.log("onPositionChanged") }
    onPressAndHold: function() { console.log("onPressAndHold") }
  }
}