from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

class Color(QWidget): # Used to change the background color
    def __init__(self, color, *args, **kwargs):
        super(Color, self).__init__(*args, **kwargs)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class CustomDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super(CustomDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle("HELLO!")

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)


        toolbar = QToolBar("Tools")
        toolbar.setIconSize(QSize(16,16))
        self.addToolBar(toolbar)

        button_action = QAction(QIcon("H:/Python/Python-Misc/fugueIcons/icons/bug.png"), "Button", self)
        button_action.setStatusTip("This is a button")
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        button_action.setCheckable(True)
        toolbar.addAction(button_action)

        button2 = QAction(QIcon("H:/Python/Python-Misc/fugueIcons/icons/burn.png"), "Button2", self)
        button2.setStatusTip("This is another button")
        button2.triggered.connect(self.onMyToolBarButtonClick)
        toolbar.addAction(button2)
        self.setStatusBar(QStatusBar(self))


    def onMyToolBarButtonClick(self, s):
        print("click", s)

        dlg = CustomDialog(self)
        if dlg.exec_():
            print("Success!")
        else:
            print("Cancel!")




########## Tabs! ################
        # tabs = QTabWidget()
        # tabs.setDocumentMode(True)
        # tabs.setTabPosition(QTabWidget.North)
        # tabs.setMovable(True)
        # for n, color in enumerate(['red','green','blue','yellow']):
        #     tabs.addTab( Color(color), color)
        # self.setCentralWidget(tabs)

######### Signals and slots - Event Handling ########
        #self.windowTitleChanged.connect(self.onWindowTitleChange)
        #self.windowTitleChanged.connect(lambda x: self.my_custom_fn())
        #self.windowTitleChanged.connect(lambda x: self.my_custom_fn(x))
        #self.windowTitleChanged.connect(lambda x: self.my_custom_fn(x,25))

######## Enter Text example code ########
    #     self.setWindowTitle("Test")
    #     widget = QLineEdit()
    #     widget.setMaxLength(10)
    #     widget.setPlaceholderText("Enter your text")
    #     # widget.setReadOnly(True) # uncomment this to make readonly
    #     widget.returnPressed.connect(self.return_pressed)
    #     widget.selectionChanged.connect(self.selection_changed)
    #     widget.textChanged.connect(self.text_changed)
    #     widget.textEdited.connect(self.text_edited)
    #     self.setCentralWidget(widget)
    # def return_pressed(self):
    #     print("Return pressed!")
    #     self.centralWidget().setText("BOOM!")
    # def selection_changed(self):
    #     print("Selection changed")
    #     print(self.centralWidget().selectedText())
    # def text_changed(self, s):
    #     print("Text changed...")
    #     print(s)
    # def text_edited(self, s):
    #     print("Text edited...")
    #     print(s)


######## Toolbar and buttons with icons ########
        # toolbar = QToolBar("Tools")
        # toolbar.setIconSize(QSize(16,16))
        # self.addToolBar(toolbar)
        #
        # button_action = QAction(QIcon("H:/Python/Python-Misc/fugueIcons/icons/bug.png"), "Button", self)
        # button_action.setStatusTip("This is a button")
        # button_action.triggered.connect(self.onMyToolBarButtonClick)
        # button_action.setCheckable(True)
        # toolbar.addAction(button_action)
        #
        # button2 = QAction(QIcon("H:/Python/Python-Misc/fugueIcons/icons/burn.png"), "Button2", self)
        # button2.setStatusTip("This is another button")
        # button2.triggered.connect(self.onMyToolBarButtonClick)
        # toolbar.addAction(button2)
        # self.setStatusBar(QStatusBar(self))
    # def onMyToolBarButtonClick(self,s):
    #     print("Clicked",s)


######### Signals and slots - Event Handling ########
#     def onWindowTitleChange(self,s):
#         print(s)
#     def my_custom_fn(self, a="Hello there.", b=5):
#         print(a,b)
#     def contextMenuEvent(self, event):
#         print("Context Menu Event!")
#         super(MainWindow, self).contextMenuEvent(event)



app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()

