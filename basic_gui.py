from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


def window():
    xpos = 200
    ypos = 200
    width = 400
    height = 400
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.setGeometry(xpos, ypos, width, height)
    win.setWindowTitle("Obs. Mon.")

    label = QtWidgets.QLabel(win)
    label.setText("METAR Monitor")
    label.move(150,10)
    win.show()
    sys.exit(app.exec_())

window()