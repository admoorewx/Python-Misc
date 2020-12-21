import sys
import icon_sources
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *



class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        self.setCentralWidget(self.tabs)


        #self.browser = QWebEngineView()
        #self.browser.setUrl( QUrl("http://www.spc.noaa.gov"))
        #self.setCentralWidget(self.browser)
        #self.setWindowIcon(QIcon(":/icons/bug.png"))
        #self.setWindowIcon(QIcon(":/icons/bug.png"))

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(16,16))
        self.addToolBar(navtb)

        back_but = QAction( QIcon(":/icons/back.png"), "Back", self)
        back_but.setStatusTip("Back to previous page")
        back_but.triggered.connect(lambda: self.tabs.currentWidget().back())
        navtb.addAction(back_but)

        forward_but = QAction( QIcon(":/icons/forward.png"), "Forward", self)
        forward_but.setStatusTip("Forward to next page")
        forward_but.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(forward_but)

        reload_but = QAction( QIcon(":/icons/reload.png"), "Reload", self)
        reload_but.setStatusTip("Reload the page")
        reload_but.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_but)

        home_but = QAction( QIcon(":/icons/home.png"), "Home", self)
        home_but.setStatusTip("Return to home page")
        home_but.triggered.connect(self.navigate_home)
        navtb.addAction(home_but)

        self.httpsicon = QLabel()
        self.httpsicon.setPixmap( QPixmap(":/icons/globe.png"))
        navtb.addWidget(self.httpsicon)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        stop_btn = QAction(QIcon(":/icons/stop.png"), "Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)

        self.add_new_tab(QUrl("www.spc.noaa.gov"), "SPC")

        self.show()
        self.setWindowTitle("Web Test")
        self.setWindowIcon(QIcon(":/icons/bug.png"))

        #self.tabs.currentWidget().urlChanged.connect(self.update_urlbar)
        #self.tabs.currentWidget().loadFinished.connect(self.update_title)





    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("http://www.spc.noaa.gov"))

    def navigate_to_url(self, browser=None):
        if browser != self.tabs.currentWidget():
            return
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.browser.setUrl(q)

    def update_urlbar(self,q, browser=None):
        if browser != self.tabs.currentWidget():
            return

        if q.scheme() == "https":
            self.httpsicon.setPixmap( QPixmap(":/icons/locked.png"))
        else:
            self.httpsicon.setPixmap(QPixmap(":/icons/unlocked.png"))
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)



    def update_title(self, browser=None):
        if browser != self.tabs.currentWidget():
            return
        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle(title)

    def tab_open_doubleclick(self,i):
        if i == -1:
            self.add_new_tab()

    def add_new_tab(self,qurl=None,label="NWS"):
        if qurl is None:
            qurl = QUrl("www.weather.gov")
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser,label)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))

        browser.loadFinished.connect( lambda _, i=i, browser=browser:
                                      self.tabs.setTabText(i, browser.page().title()))

    def current_tab_changed(self,i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self,i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)


app = QApplication(sys.argv)
app.setApplicationName("Web Test")
app.setApplicationVersion("1.0")
window = MainWindow()
window.show()

app.exec_()


# class Color(QWidget): # Used to change the background color
#     def __init__(self, color, *args, **kwargs):
#         super(Color, self).__init__(*args, **kwargs)
#         self.setAutoFillBackground(True)
#         palette = self.palette()
#         palette.setColor(QPalette.Window, QColor(color))
#         self.setPalette(palette)
#
#
# class CustomDialog(QDialog):
#
#     def __init__(self, *args, **kwargs):
#         super(CustomDialog, self).__init__(*args, **kwargs)
#
#         self.setWindowTitle("HELLO!")
#
#         buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
#
#         self.buttonBox = QDialogButtonBox(buttons)
#         self.buttonBox.accepted.connect(self.accept)
#         self.buttonBox.rejected.connect(self.reject)
#
#         self.layout = QVBoxLayout()
#         self.layout.addWidget(self.buttonBox)
#         self.setLayout(self.layout)
#
#
# class MainWindow(QMainWindow):
#     def __init__(self, *args, **kwargs):
#         super(MainWindow, self).__init__(*args, **kwargs)
#
#
#         toolbar = QToolBar("Tools")
#         toolbar.setIconSize(QSize(16,16))
#         self.addToolBar(toolbar)
#
#         button_action = QAction(QIcon(":/icons/bug.png"), "Button", self)
#         #button_action = QAction(QIcon("H:/Python/Python-Misc/fugueIcons/icons/bug.png"), "Button", self)
#         button_action.setStatusTip("This is a button")
#         button_action.triggered.connect(self.onMyToolBarButtonClick)
#         button_action.setCheckable(True)
#         toolbar.addAction(button_action)
#
#         button2 = QAction(QIcon(":/icons/cactus.png"), "Button2", self)
#         button2.setStatusTip("This is another button")
#         button2.triggered.connect(self.onMyToolBarButtonClick)
#         toolbar.addAction(button2)
#         self.setStatusBar(QStatusBar(self))
#
#
#     def onMyToolBarButtonClick(self, s):
#         print("click", s)
#
#         dlg = CustomDialog(self)
#         if dlg.exec_():
#             print("Success!")
#         else:
#             print("Cancel!")




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


#
# app = QApplication(sys.argv)
#
# window = MainWindow()
# window.show()
#
# app.exec_()

