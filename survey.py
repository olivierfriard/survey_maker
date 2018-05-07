#!/usr/bin/env python3
"""
Survey maker
2018 (c) Olivier Friard
"""

import os
import sys
import time
import datetime
import json
import pathlib
import subprocess
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QInputDialog, QLineEdit, QFrame, QComboBox, QMessageBox,
                             QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QFormLayout, QSpinBox)

WINDOWS_VLC_PATH = '""c:\\Program Files\\VideoLAN\\VLC\\vlc.exe" --no-osd -f --play-and-exit "{beep}" "{video}" "{beep}""'

LINUX_VLC_PATH = 'cvlc  --no-osd -f --play-and-exit  --no-osd -f --play-and-exit "{beep}" "{video}" "{beep}" '


def date_iso():
    return datetime.datetime.now().isoformat().split(".")[0].replace("T", "_").replace(":", "")


class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("")

        self.font_size = int(app.desktop().screenGeometry().height() / 1200 * 36)

        self.position = 0
        self.pages = {}

        dd = json.loads(open(SURVEY_CONFIG_FILE).read())
        for idx in dd.keys():
            self.pages[int(idx)] = dd[idx]

        # create results file
        if not os.path.isfile(pathlib.Path(SURVEY_CONFIG_FILE).with_suffix('.tsv')):
            try:
                with open(pathlib.Path(SURVEY_CONFIG_FILE).with_suffix('.tsv'), "w") as f_out:
                    out = "Id\t"
                    for idx in sorted(self.pages.keys()):
                        if "text" not in self.pages[idx]:
                            if "name" in self.pages[idx]:
                                out += self.pages[idx]["name"] + "\t"
                            else:
                                out += "\t"
                    f_out.write(out + "\n")
            except:
                QMessageBox.critical(self, "Errore", "Il file dei risultati non può essere creato")

        self.initUI()

        self.setWindowTitle(date_iso())


    def initUI(self):

        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        self.showFullScreen() 

        self.vboxlayout= QVBoxLayout()

        self.tw = QTabWidget()
        self.tw.tabBar().setVisible(False)
        self.tabs = []
        self.widgets = []

        for i in sorted(self.pages.keys()):
            self.tabs.append(QWidget())
            if "question" in self.pages[i]:
                label  = QLabel(self.pages[i]["question"])
                label.setStyleSheet("font-size:{}px".format(self.font_size))
            else:
                label  = QLabel()

            if self.pages[i]["type"] == "text":
                text = QLabel(self.pages[i]["text"])
                text.setStyleSheet("font-size:{}px".format(self.font_size))
                self.widgets.append("text")

                layout = QFormLayout()
                layout.addRow(label, text)
                self.tabs[-1].setLayout(layout)
                
            if self.pages[i]["type"] == "open_int":
                sp = QSpinBox()
                sp.setStyleSheet("font-size:{}px".format(self.font_size))
                sp.setMinimum(self.pages[i]["limits"][0])
                sp.setMaximum(self.pages[i]["limits"][1])
                self.widgets.append(sp)
                
                layout = QFormLayout()
                layout.addRow(label, sp)
                self.tabs[-1].setLayout(layout)

            if self.pages[i]["type"] == "open_text":
                le = QLineEdit()
                le.setStyleSheet("font-size:{}px".format(self.font_size))
                self.widgets.append(le)

                layout = QFormLayout()
                layout.addRow(label, le)
                self.tabs[-1].setLayout(layout)

            if self.pages[i]["type"] == "closed":
                self.setStyleSheet("QComboBox { min-height: 40px; min-width: 60px; }" "QComboBox QAbstractItemView::item { min-height: 40px; min-width: 60px; }")
                cb = QComboBox()
                
                #cb.view().setMinimumHeight(240)
                cb.setStyleSheet("font-size:{}px".format(self.font_size))
                cb.addItems(self.pages[i]["choices"])
                self.widgets.append(cb)

                layout = QFormLayout()
                layout.addRow(label, cb)
                self.tabs[-1].setLayout(layout)

            if self.pages[i]["type"] == "video":
                if not os.path.isfile(self.pages[i]["path"]):
                    QMessageBox.critical(self, "Errore", "Il video {} non è stato trovato".format(self.pages[i]["path"]))
                    sys.exit()
                self.widgets.append("video")

            if self.pages[i]["type"] == "end":
                layout = QFormLayout()
                pb = QPushButton("Fine")
                pb.setStyleSheet("font-size:{font_size}px; height:120px; color: white; background-color: rgb(255, 0, 0); border:0px;".format(font_size=self.font_size))
                pb.clicked.connect(self.pb_end)
                layout.addRow(pb)
                self.widgets.append(pb)
                self.tabs[-1].setLayout(layout)

            self.tw.addTab(self.tabs[-1], "Tab {}".format(i))
            self.tw.setTabEnabled(i, False)
        
        self.tw.setTabEnabled(0, True)
        self.tw.setCurrentIndex(self.position)
        self.vboxlayout.addWidget(self.tw)

        self.hboxlayout= QHBoxLayout()
        
        self.start_button = QPushButton("PRECEDENTE", self)

        self.start_button.setStyleSheet("font-size:{font_size}px; width: 120px; height:120px; color: white; background-color: rgb(0, 0, 255); border:0px;".format(font_size=self.font_size))
        self.start_button.clicked.connect(self.previous)
        self.hboxlayout.addWidget(self.start_button)

        self.next_button = QPushButton("SUCCESSIVO")
        self.next_button.setStyleSheet("font-size:{font_size}px; width: 120px; height:120px; color: white; background-color: rgb(0, 0, 255); border:0px;".format(font_size=self.font_size))
        self.next_button.clicked.connect(self.next)
        self.hboxlayout.addWidget(self.next_button)

        self.vboxlayout.addLayout(self.hboxlayout)

        self.widget.setLayout(self.vboxlayout)
        self.show()


    def pb_end(self):

        result = QMessageBox.question(self, "Conferma", "Sicuro di avere finito?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
         
        if result == QMessageBox.No:
            return

        try:
            with open(self.windowTitle() + ".tsv", "w") as f_out:
                for idx in sorted(self.pages.keys()):
                    if "results" in self.pages[idx]:
                        f_out.write("{}\t{}\n".format(self.pages[idx]["name"], self.pages[idx]["results"]))
        except:
            QMessageBox.critical(self, "Errore", "I dati non sono stati salvati")

        try:
            with open(pathlib.Path(SURVEY_CONFIG_FILE).with_suffix('.tsv'), "a") as f_out:
                out = self.windowTitle() + "\t"
                for idx in sorted(self.pages.keys()):
                    if "results" in self.pages[idx]:
                        out += "{}\t".format(self.pages[idx]["results"])
                out += "\n"
                f_out.write(out)
        except:
            QMessageBox.critical(self, "Errore", "I dati non sono stati salvati in {}".format(pathlib.Path(SURVEY_CONFIG_FILE).with_suffix('.tsv')))

        self.close()

    def previous(self):
        """
        go to previous question
        """
        self.tw.setTabEnabled(self.position, False)
        self.position -= 1
        
        if self.position in self.pages:
            if "condition" in self.pages[self.position]:
                if self.pages[self.position]["condition"][0] < 0:
                    if self.pages[self.position + self.pages[self.position]["condition"][0]]["results"] != self.pages[self.position]["condition"][1]:
                        self.pages[self.position]["results"] = "-"
                        self.position -= 1
                else:
                    if self.pages[self.pages[self.position]["condition"][0]]["results"] != self.pages[self.position]["condition"][1]:
                        self.pages[self.position]["results"] = "-"
                        self.position -= 1

        self.tw.setTabEnabled(self.position, True)
        self.tw.setCurrentIndex(self.position)

    def next(self):
        """
        go to the next question
        """

        value = ""
        if self.pages[self.position]["type"] not in ["video", "text"]:

            if isinstance(self.widgets[self.position], QSpinBox):
                value = str(self.widgets[self.position].value())
            if isinstance(self.widgets[self.position], QLineEdit):
                value = str(self.widgets[self.position].text())
            if isinstance(self.widgets[self.position], QComboBox):
                value = str(self.widgets[self.position].currentText())
            print("value", value)
    
            if not value:
                return
            self.pages[self.position]["results"] = value

        self.tw.setTabEnabled(self.position, False)
        self.position += 1

        if self.position in self.pages:
            if "condition" in self.pages[self.position]:
                if self.pages[self.position]["condition"][0] < 0:
                    if self.pages[self.position + self.pages[self.position]["condition"][0]]["results"] != self.pages[self.position]["condition"][1]:
                        self.pages[self.position]["results"] = "-"
                        self.position += 1
                else:
                    if self.pages[self.pages[self.position]["condition"][0]]["results"] != self.pages[self.position]["condition"][1]:
                        self.pages[self.position]["results"] = "-"
                        self.position += 1

        self.tw.setTabEnabled(self.position, True)
        self.tw.setCurrentIndex(self.position)

        if self.pages[self.position]["type"] == "video":
            self.pages[self.position]["results"] = self.pages[self.position]["path"]
            
            if sys.platform.startswith("linux"):
                vlc_path = LINUX_VLC_PATH
                

            if sys.platform.startswith("win"):
                vlc_path = WINDOWS_VLC_PATH

            cmd = vlc_path.format(video=self.pages[self.position]["path"],
                                  beep="beep.wav" if "beep" in self.pages[self.position] and self.pages[self.position]["beep"] == "true" else "")
            print(cmd)
            os.system(cmd)


if __name__ == '__main__':
    
    if len(sys.argv) == 1:
        print("The survey configuration file was not found")
        sys.exit()
    else:
        SURVEY_CONFIG_FILE = sys.argv[1]
        if not os.path.isfile(SURVEY_CONFIG_FILE):
            print("{} not found".format(SURVEY_CONFIG_FILE))
            sys. exit()
    
    app = QApplication(sys.argv)
    app.setApplicationDisplayName(SURVEY_CONFIG_FILE)
    ex = App()
    sys.exit(app.exec_())
