import sys, os, signal, threading
from PySide2.QtWidgets import QApplication
from wallpapergui.DesktopWidget import DesktopWidget

sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "7777"
    app = QApplication([])
    app_exitcode = None
    kbdint = False
    widget = DesktopWidget()
    widget.show()
    # def thread_fn_guard():
    #     def exit(signum, frame):
    #         print("detected keyboard interrupt.")
    #         kbdint = True
    #     signal.signal(signal.SIGINT, exit)
    #     signal.signal(signal.SIGTERM, exit)
    #     while app_exitcode is None:
    #         if kbdint:
    #             widget.close()
    # def thread_fn_guard():
    #     try:
    #         while app_exitcode is None:
    #             pass
    #     except KeyboardInterrupt:
    #         print("detected keyboard interrupt.")
    #         kbdint = True
    #         widget.close()
    # thread_guard = threading.Thread(target=thread_fn_guard)
    # thread_guard.setDaemon(True)
    # thread_guard.start()
    def thread_fn_app():
        app_exitcode = app.exec_()
    thread_fn_app()
    sys.exit(app_exitcode)

