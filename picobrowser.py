#!/usr/bin/env python3
import sys
import json
import os

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QToolBar, QAction, QLineEdit, QInputDialog,
    QMessageBox, QFileDialog
)

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl

BOOKMARK_FILE = "bookmarks.json"


class Browser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pico Browser")
        self.resize(1200, 750)

        self.apply_modern_theme()

        self.base_dir = os.path.dirname(os.path.realpath(__file__))

        # USER AGENT + DOWNLOAD
        self.profile = QWebEngineProfile.defaultProfile()

        self.profile.setHttpUserAgent(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.profile.downloadRequested.connect(self.on_download_requested)

        # TAB
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_urlbar)
        self.setCentralWidget(self.tabs)

        # TOOLBAR
        toolbar = QToolBar()
        toolbar.setMovable(False)
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

        bookmark_btn = QAction("★", self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        toolbar.addAction(bookmark_btn)

        show_bookmarks_btn = QAction("📚", self)
        show_bookmarks_btn.triggered.connect(self.show_bookmarks)
        toolbar.addAction(show_bookmarks_btn)

        delete_bookmark_btn = QAction("🗑", self)
        delete_bookmark_btn.triggered.connect(self.delete_bookmark)
        toolbar.addAction(delete_bookmark_btn)

        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("Cerca o inserisci URL...")
        self.urlbar.returnPressed.connect(self.load_url)
        toolbar.addWidget(self.urlbar)

        self.add_tab()

    # ---------------- NEW TAB PAGE ----------------
    def get_new_tab_url(self):

        newtab_path = os.path.join(self.base_dir, "newtab.html")

        if os.path.exists(newtab_path):
            return QUrl.fromLocalFile(newtab_path)

        return QUrl("https://duckduckgo.com")

    # ---------------- DOWNLOAD ----------------
    def on_download_requested(self, download):

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Salva file",
            download.path()
        )

        if path:
            download.setPath(path)
            download.accept()

            QMessageBox.information(self, "Download", "Download avviato!")

    # ---------------- TEMA ----------------
    def apply_modern_theme(self):
        self.setStyleSheet("""
            QMainWindow { background: #f5f6f7; }

            QToolBar {
                background: #ffffff;
                spacing: 6px;
                padding: 6px;
                border-bottom: 1px solid #ddd;
            }

            QLineEdit {
                background: #ffffff;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
            }

            QLineEdit:focus { border: 1px solid #4a90e2; }

            QTabWidget::pane { border: none; background: #ffffff; }

            QTabBar::tab {
                background: #e9eaec;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 8px;
            }

            QTabBar::tab:selected {
                background: #ffffff;
                border: 1px solid #ddd;
            }

            QTabBar::tab:hover { background: #dcdcdc; }
        """)

    # ---------------- TAB ----------------
    def add_tab(self, qurl=None):

        if qurl is None:
            qurl = self.get_new_tab_url()

        web = QWebEngineView()
        web.setUrl(qurl)

        index = self.tabs.addTab(web, "Nuova tab")
        self.tabs.setCurrentIndex(index)

        web.titleChanged.connect(
            lambda title, w=web:
            self.tabs.setTabText(self.tabs.indexOf(w), title[:20])
        )

        web.urlChanged.connect(
            lambda url, w=web:
            self.update_urlbar(self.tabs.indexOf(w))
        )

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    def current_web(self):
        return self.tabs.currentWidget()

    # ---------------- NAVIGAZIONE ----------------
    def load_url(self):

        url = self.urlbar.text()

        if not url.startswith("http"):
            url = "https://" + url

        self.current_web().setUrl(QUrl(url))

    def update_urlbar(self, index):
        web = self.tabs.widget(index)

        if web:
            self.urlbar.setText(web.url().toString())

    def go_back(self):
        self.current_web().back()

    def go_forward(self):
        self.current_web().forward()

    def reload_page(self):
        self.current_web().reload()

    # ---------------- SEGNALIBRI ----------------
    def add_bookmark(self):

        url = self.current_web().url().toString()
        title = self.current_web().title()

        bookmarks = self.load_json(BOOKMARK_FILE)
        bookmarks.append({"title": title, "url": url})
        self.save_json(BOOKMARK_FILE, bookmarks)

        QMessageBox.information(self, "Segnalibro", "Segnalibro salvato!")

    def show_bookmarks(self):

        bookmarks = self.load_json(BOOKMARK_FILE)

        if not bookmarks:
            QMessageBox.information(self, "Segnalibri", "Nessun segnalibro")
            return

        items = [b["title"] for b in bookmarks]
        item, ok = QInputDialog.getItem(self, "Segnalibri", "Apri:", items, 0, False)

        if ok:
            for b in bookmarks:
                if b["title"] == item:
                    self.add_tab(QUrl(b["url"]))

    # ⭐ NUOVA funzione elimina segnalibro
    def delete_bookmark(self):

        bookmarks = self.load_json(BOOKMARK_FILE)

        if not bookmarks:
            QMessageBox.information(self, "Segnalibri", "Nessun segnalibro da eliminare")
            return

        items = [b["title"] for b in bookmarks]

        item, ok = QInputDialog.getItem(
            self,
            "Elimina segnalibro",
            "Scegli segnalibro da eliminare:",
            items,
            0,
            False
        )

        if ok:
            bookmarks = [b for b in bookmarks if b["title"] != item]
            self.save_json(BOOKMARK_FILE, bookmarks)

            QMessageBox.information(self, "Segnalibri", "Segnalibro eliminato!")

    # ---------------- JSON ----------------
    def load_json(self, filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return []

    def save_json(self, filename, data):
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)


# ---------------- AVVIO ----------------
app = QApplication(sys.argv)
browser = Browser()
browser.show()
sys.exit(app.exec_())
