import os, sys
from wallpapergui.Application import Application
from wallpapergui.DesktopWidget import DesktopWidget

sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    app = Application()
    app_exitcode = None
    kbdint = False
    widget = DesktopWidget()
    widget.show()
    sys.exit(app.exec_())

