function document_ready(context) {
  window.context = context;
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
  window.requestAnchorStatusCallback = function(result) {
    window.anchor_top = result;
    var mousepressed = false;
    // forbid default actions
    $(document).on("click", function(event) {
    });
    // drag page to move the context window
    $("#title-bar-wrapper").on("mousedown", function(event) {
      mousepressed = true;
      context.mousePressEvent(event.screenX, event.screenY)
    });
    $(document).on("mousemove", function(event) {
      if (!mousepressed) return;
      context.mouseMoveEvent(event.screenX, event.screenY)
    });
    $(document).on("mouseup", function(event) {
      if (!mousepressed) return;
      context.mouseReleaseEvent(event.screenX, event.screenY)
      mousepressed = false;
      if (!wrapperEl.is(":hover")) wrapperEl.trigger("mouseout");
    });
    // hover to activate title buttons
    wrapperEl.on("mouseenter", function(event) {
      if (!wrapperEl.is(":hover")) return;
      context.holdWindowPosition(true);
      if (window.anchor_top) $(".content-block").detach().removeClass('beyond').addClass('below').insertAfter('#title-bar-wrapper');
      else $(".content-block").detach().removeClass('below').addClass('beyond').insertBefore('#title-bar-wrapper');
      $(".content-block").removeClass('hidden');
      $(".title-button").removeClass('hidden');
      checkWrapperSize();
      context.holdWindowPosition(false);
    });
    wrapperEl.on("mouseout", function(event) {
      if (mousepressed) return;
      if (wrapperEl.is(":hover")) return;
      context.holdWindowPosition(true);
      $(".title-button").addClass('hidden');
      $(".content-block").addClass('hidden');
      checkWrapperSize();
      context.holdWindowPosition(false);
    });
    // // click to activate content block
    // $("#button-info").on("click", function(event) {
    //   $(".content-block").toggleClass('hidden');
    //   checkWrapperSize();
    // });
  };
  context.requestAnchorTopStatus("window.requestAnchorStatusCallback");
}

new QWebChannel(qt.webChannelTransport, function(channel) {
  var context = channel.objects.context;
  $(function() {
    document_ready(context);
  })
});
