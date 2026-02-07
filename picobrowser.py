#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QToolBar, QAction, QLineEdit
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pico Browser")
        self.resize(1200, 750)

        # ---------- TAB ----------
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_urlbar)
        self.setCentralWidget(self.tabs)

        # ---------- TOOLBAR ----------
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        back_btn = QAction("◀", self)
        back_btn.triggered.connect(self.go_back)
        toolbar.addAction(back_btn)

        forward_btn = QAction("▶", self)
        forward_btn.triggered.connect(self.go_forward)
        toolbar.addAction(forward_btn)

        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(self.reload_page)
        toolbar.addAction(reload_btn)

        new_tab_btn = QAction("+", self)
        new_tab_btn.triggered.connect(lambda: self.add_tab())
        toolbar.addAction(new_tab_btn)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.load_url)
        toolbar.addWidget(self.urlbar)

        # Prima tab
        self.add_tab(QUrl("https://duckduckgo.com"))

    # ---------- TAB LOGIC ----------
    def add_tab(self, qurl=None):
        if qurl is None or isinstance(qurl, bool):
            qurl = QUrl("https://duckduckgo.com")

        web = QWebEngineView()
        web.setUrl(qurl)

        index = self.tabs.addTab(web, "Nuova tab")
        self.tabs.setCurrentIndex(index)

        web.urlChanged.connect(
            lambda qurl, w=web: self.update_tab_title(w, qurl)
        )
        web.titleChanged.connect(
            lambda title, w=web: self.tabs.setTabText(
                self.tabs.indexOf(w), title[:20]
            )
        )

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def current_web(self):
        return self.tabs.currentWidget()

    # ---------- NAVIGAZIONE ----------
    def load_url(self):
        url = self.urlbar.text()
        if not url.startswith("http"):
            url = "https://" + url
        self.current_web().setUrl(QUrl(url))

    def update_urlbar(self, index):
        web = self.tabs.widget(index)
        if web:
            self.urlbar.setText(web.url().toString())

    def update_tab_title(self, web, qurl):
        index = self.tabs.indexOf(web)
        if index != -1:
            self.tabs.setTabText(index, qurl.host())

    def go_back(self):
        self.current_web().back()

    def go_forward(self):
        self.current_web().forward()

    def reload_page(self):
        self.current_web().reload()

# ---------- AVVIO ----------
app = QApplication(sys.argv)
browser = Browser()
browser.show()
sys.exit(app.exec_())
