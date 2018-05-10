#!/usr/bin/env python3
"""

Survey maker
Copyright 2018 Olivier Friard

This file is part of "Survey maker".

  "Survey maker" is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  any later version.

  "Survey maker" is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not see <http://www.gnu.org/licenses/>.


"""

import os
import sys
import time
import datetime
import json
import pathlib
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QInputDialog, QLineEdit, QFrame, QComboBox, QMessageBox,
                             QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QFormLayout, QSpinBox)
from PyQt5.QtCore import QSettings 

__version__ = "0.0.4"
__version_date__ = "2018-05-10"


def date_iso():
    return datetime.datetime.now().isoformat().split(".")[0].replace("T", "_").replace(":", "")


class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.setWindowTitle("")

        self.font_size = int(app.desktop().screenGeometry().height() / 1200 * 36)

        self.position = 0
        self.pages = {}

        try:
            dd = json.loads(open(SURVEY_CONFIG_FILE).read())
        except:
            QMessageBox.critical(self, "Errore", "Il file {} non è corretto.".format(SURVEY_CONFIG_FILE))
            sys.exit()
            
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
                    video_path = PROJECT_DIR / pathlib.Path(self.pages[i]["path"])
                    if video_path.exists():
                        video_path = str(video_path)
                    else:
                        QMessageBox.critical(self, "Errore", "Il video {} non è stato trovato".format(self.pages[i]["path"]))
                        sys.exit()
                    self.pages[i]["path"] = video_path

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

        # single survey
        single_tests_dir = PROJECT_DIR / pathlib.Path(SURVEY_CONFIG_FILE).with_suffix('.single_tests')
        if not os.path.isdir(single_tests_dir):
            os.mkdir(single_tests_dir)
        
        single_file_name = str(single_tests_dir / pathlib.Path(self.windowTitle() + ".tsv"))
        try:
            with open(single_file_name, "w") as f_out:
                for idx in sorted(self.pages.keys()):
                    if "results" in self.pages[idx]:
                        f_out.write("{}\t{}\n".format(self.pages[idx]["name"], self.pages[idx]["results"]))
        except:
            QMessageBox.critical(self, "Errore", "I dati non sono stati salvati")

        if gdrive_cmd:
            os.system(gdrive_cmd.format(single_file_name))

        # all results
        all_results_file_name = str(pathlib.Path(SURVEY_CONFIG_FILE).with_suffix('.tsv'))
        try:
            with open(all_results_file_name, "a") as f_out:
                out = self.windowTitle() + "\t"
                for idx in sorted(self.pages.keys()):
                    if "results" in self.pages[idx]:
                        out += "{}\t".format(self.pages[idx]["results"])
                out += "\n"
                f_out.write(out)
        except:
            QMessageBox.critical(self, "Errore", "I dati non sono stati salvati in {}".format(all_results_file_name))

        if gdrive_cmd:
            os.system(gdrive_cmd.format(all_results_file_name))

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

        # mask previous and net buttons
        if self.pages[self.position]["type"] == "end":
            self.start_button.setVisible(False)
            self.next_button.setVisible(False)


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
            self.pages[self.position]["results"] = os.path.basename(self.pages[self.position]["path"])

            beep_path = ""
            if "beep" in self.pages[self.position] and self.pages[self.position]["beep"]:
                beep_path = self.pages[self.position]["beep"]
                if not os.path.isfile(beep_path):
                    beep_path = PROJECT_DIR / pathlib.Path(beep_path)
                    if beep_path.exists():
                        beep_path = str(beep_path)
                    else:
                        beep_path = ""
            cmd = VLC_CMD.format(video=self.pages[self.position]["path"],
                                 beep=beep_path)
            print(cmd)
            os.system(cmd)


if __name__ == '__main__':
    
    if len(sys.argv) == 1:
        print("The survey project file was not found")
        sys.exit()
    else:
        SURVEY_CONFIG_FILE = sys.argv[1]
        if not os.path.isfile(SURVEY_CONFIG_FILE):
            print("{} not found".format(SURVEY_CONFIG_FILE))
            sys. exit()

    PROJECT_DIR = pathlib.Path(SURVEY_CONFIG_FILE).parent

    # check for VLC path
    if sys.platform.startswith("win"):
        p = PROJECT_DIR / pathlib.Path("survey.config")
        if p.exists():
            settings = QSettings(str(p), QSettings.IniFormat)
            vlc_path = settings.value("VLC_path")
            
            print("vlc path:", vlc_path)
    
            VLC_CMD = '""###VLC_PATH###" --no-osd -f --play-and-exit "{beep}" "{video}" "{beep}""'.replace("###VLC_PATH###", vlc_path)
        else:
            VLC_CMD = '""c:\\Program Files\\VideoLAN\\VLC\\vlc.exe" --no-osd -f --play-and-exit "{beep}" "{video}" "{beep}""'

        print("VLC CMD", VLC_CMD)

    gdrive_cmd = ""
    p = PROJECT_DIR / pathlib.Path("survey.config")
    if p.exists():
        settings = QSettings(str(p), QSettings.IniFormat)
        gdrive_cmd = settings.value("google_drive")
        print("google drive command: {}".format(gdrive_cmd))


    if sys.platform.startswith("linux"):
        VLC_CMD = 'cvlc  --no-osd -f --play-and-exit  --no-osd -f --play-and-exit "{beep}" "{video}" "{beep}" '

    
    app = QApplication(sys.argv)
    app.setApplicationDisplayName(SURVEY_CONFIG_FILE)
    ex = App()
    sys.exit(app.exec_())
