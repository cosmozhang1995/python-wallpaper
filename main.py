import sys, os
from PySide2.QtWidgets import QApplication
from wallpapergui.DesktopWidget import DesktopWidget

sys.path.append(os.path.dirname(__file__))

if __name__ == "__main__":
    app = QApplication([])
    widget = DesktopWidget()
    widget.show()
    sys.exit(app.exec_())

