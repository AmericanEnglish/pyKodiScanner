from getpass import getuser
from os import listdir
from os.path import exists
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget,  QCheckBox, QTextEdit, QPushButton, QMessageBox, QFileDialog
from PyQt5.QtCore import QSize    
import sqlite3
import re

from locateMedia import *
class Main(QMainWindow):
    def __init__(self):
        # Initialize the super class
        super().__init__()

        # self.setMinimumSize(QSize(640, 480))
        self.setMinimumWidth(480)
        self.setWindowTitle("pyJulieScanner - A Kodi Database Scanner")

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        gridLayout = QGridLayout(self)
        centralWidget.setLayout(gridLayout)
        self.allOptions = {}

        # title.setAlignment(QtCore.Qt.AlignCenter)
        # gridLayout.addWidget(title, 0, 0)

        # Setup checkboxes for possible tasks
        checkboxLabel = QLabel("Perform the following actions:", self)
        option1 = QCheckBox("Produce a file containing all movies Kodi does not see",  self)
        option2 = QCheckBox("Produce a file containing all movies Kodi sees", self)
        option3 = QCheckBox("Check TV shows for missing seasons", self)

        self.fileOutputDir = ""
        self.fileOutputDirText = "Output Files to: "
        self.fileOutputDirButton = QPushButton(self.fileOutputDirText, self)
        self.fileOutputDirLabel = QLabel(self.fileOutputDir, self)
        # Connect it to setting the outputdir
        self.fileOutputDirButton.clicked.connect(self.setOutputDir)

        self.allOptions["option1"] = option1
        self.allOptions["option2"] = option2
        self.allOptions["option3"] = option3

        # The log area
        self.logText = QTextEdit("",self)
        self.logText.setReadOnly(True)

        # Action button!
        self.doButton = QPushButton("Do Checked Tasks", self)
        # Connect a function to the button
        self.doButton.clicked.connect(self.doAllPossibleActions)
        


    
        gridLayout.addWidget(checkboxLabel, 0, 0, 1, 3)
        gridLayout.addWidget(option1, 1, 0, 1, 3)
        gridLayout.addWidget(option2, 2, 0, 1, 3)
        gridLayout.addWidget(option3, 3, 0, 1, 3)
        gridLayout.addWidget(self.fileOutputDirButton, 4, 0, 1, 1)
        gridLayout.addWidget(self.fileOutputDirLabel, 4, 1, 1, 3)
        # gridLayout.addWidget(self.fileOutputDirText, 4, 1)
        gridLayout.addWidget(QLabel("Log:"), 5, 0)
        gridLayout.addWidget(self.logText, 6,0,1,4)
        gridLayout.addWidget(self.doButton, 5, 3)

        # Find Kodi database
        # self.databases = self.getDatabases()

        
        # Find all media that Kodi doesn't see
        # Find all media that Kodi sees
        # Find missing TV Show seasons
    
    def doAllPossibleActions(self):
        if not self.fileOutputDir:
            # Get a file output location
            self.setOutputDir()
            if self.fileOutputDir is None or not self.fileOutputDir:
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("No Output Directory Selected!")
                msg.exec()
                self.updateText("No actions selected!")
                return None
        p = 0
        # If a current job is running, kill it!
        # Setup a QTimer that periodically updates the progress while checking if they're active
        r = re.compile("[\\:\\w&.\\-\\/]+MyVideos\\d+.db$")
        videoDatabase = filter(r.match, self.databases)
        if self.allOptions['option1'].isChecked():
            # Establish a connection to the movie database
            connection = sqlite3.connect(videoDatabase)
            cursor = connection.cursor()
            # Get the movie name, movie path, movie filename
            cursor.execute("SELECT idMovie, idFile FROM movie;")

            allKnownMovies = cursor.fetchall()
            connection.close()
            p += 1
            
            # self.updateText("Found {} missing movies!".format(numMissing))
            # Write out the file
        if self.allOptions['option2'].isChecked():
            # Establish a connection to the movie database
            connection = sqlite3.connect(videoDatabase)
            cursor = connection.cursor()
            # Get the movie name, movie path, movie filename
            cursor.execute("SELECT c00 FROM movie;")
            allKnownMovies = cursor.fetchall()

            # Get the movie name, movie path, movie filename
            p += 1
            # self.updateText("Found {} movies logged by Kodi...".format(numFound))
            # Write out the file
        if self.allOptions['option3'].isChecked():
            connection = sqlite3.connect(videoDatabase)
            cursor = connection.cursor()
            # cursor.execute("SELECT idMovie, idFile, c00 FROM movie")
            # allKnownShows = cursor.fetchall()
            connection.close()
            set.updateText("Option 3 is not yet available")
            p += 1
            # self.updateText("Found {} missing seasons".format(numMissing))
            # Write out the file

        if p == 0:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText("No Actions Selected!")
            msg.exec()
            self.updateText("No actions selected!")
        return None

    def setOutputDir(self):
        self.fileOutputDir = QFileDialog.getExistingDirectory(self, "Select Media Location")
        self.fileOutputDirLabel.setText(self.fileOutputDir)
        self.updateText("Output directory selected as:\n{}".format(self.fileOutputDir))
        return None

    def updateText(self, moreText):
        self.logText.setText("{}{}{}".format(self.logText.toPlainText(), moreText, "\n"))
        self.logText.verticalScrollBar().setValue(self.logText.verticalScrollBar().maximum())
        return None

    def getDatabases(self, databaseRoot=None):
        # For windows only
        if databaseRoot is None:
            databaseRoot = "C:/Users/{}/AppData/Roaming/kodi/userdata".format(getuser())
        
        databases = []
        if exists(databaseRoot):
            allfiles = listdir(databaseRoot)
            for afile in allfiles:
                if afile[-3:] == ".db":
                    databases.append(afile)
            if databases == []:
                self.updateText("Directory exists but no databases found? Program will crash if ran further")
            else:
                databases = list(map(lambda database: "{}/{}".format(databaseRoot, database), databases))
                self.updateText("Databases found: {}".format(databases))
        else:
            # Need a better work around
            if databaseRoot == "" or databaseRoot != "C:/Users/{}/AppData/Roaming/kodi/userdata".format(getuser()):
                exit()
            self.updateText("No databases found at {}".format(databaseRoot))
            self.updateText("A new location must be selected and must contain the userdata folder for kodi or the application with crash")
            # Allow the user to pick a directory but see files
            # databaseRoot = QFileDialog.getExistingDirectory(self, "Select Database Location",QFileDialog.)
            databaseRoot = QFileDialog.getExistingDirectory(self, "Select Database Location")
            databases = self.getDatabases(databaseRoot=databaseRoot)

        return databases


if __name__ == "__main__":
    from sys import argv, exit
    app = QtWidgets.QApplication(argv)
    mainWin = Main()
    mainWin.show()
    mainWin.getDatabases()
    exit(app.exec_())
