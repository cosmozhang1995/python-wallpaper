var context;

function document_ready(context) {
  var wrapperEl = $("#main-wrapper");
  var wrapperWidth = 0;
  var wrapperHeight = 0;
  var checkWrapperSize = function() {
    var w = wrapperEl.width();
    var h = wrapperEl.height();
    if (w != wrapperWidth || h != wrapperHeight) {
      wrapperWidth = w;
      wrapperHeight = h;
      context.resizeWindow(w, h);
    }
  };
  window.checkWrapperSize = checkWrapperSize;
  checkWrapperSize();
  // forbid default actions
  $(document).on("click", function(event) {
    console.log(event);
  });
  // drag page to move the context window
  $(document).on("mousedown", function(event) {
    context.mousePressEvent(event.screenX, event.screenY)
  });
  $(document).on("mousemove", function(event) {
    context.mouseMoveEvent(event.screenX, event.screenY)
  });
  $(document).on("mouseup", function(event) {
    context.mouseReleaseEvent(event.screenX, event.screenY)
  });
}

new QWebChannel(qt.webChannelTransport, function(channel) {
  var context = channel.objects.context;
  $(function() {
    document_ready(context);
  })
});
