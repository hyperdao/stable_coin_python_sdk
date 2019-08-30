from PyQt5 import QtCore, QtGui, QtWidgets
from pcm_main import PcmMainWindow
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = PcmMainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
