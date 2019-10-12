import sys, os
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
from PyQt5 import QtCore, QtGui, QtWidgets
from pcm_main import PcmMainWindow
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = PcmMainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
