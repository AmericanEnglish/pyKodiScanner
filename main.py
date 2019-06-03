from getpass import getuser
from os import listdir
from os.path import exists
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget,  QCheckBox, QTextEdit, QPushButton, QMessageBox, QFileDialog
from PyQt5.QtCore import QSize, QTimer
from multiprocessing import active_children, Queue
import sqlite3
import re

from workers import VideoWorker

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

        self.fileOutputDir = "./"
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

        
        self.option1ProgressLabel = QLabel("", self)
        self.option1ProgressLabel.hide()

    
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
        gridLayout.addWidget(self.option1ProgressLabel,7,0,1,4)
        # Find Kodi database
        # self.databases = self.getDatabases()
        
        self.getDatabases()

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
        r = re.compile("[\\:\\w&.\\-\\/]+MyVideos\\d+.db$")
        videoDatabase = list(filter(r.match, self.databases))[0]
        if self.allOptions['option1'].isChecked():
            # Establish a connection to the movie database
            connection = sqlite3.connect(videoDatabase)
            cursor = connection.cursor()
            # Get the movie name, movie path, movie filename
            cursor.execute("""SELECT DISTINCT strPath,strFilename FROM files
                            INNER JOIN movie
                            ON files.idFile = movie.idFile
                            INNER JOIN path 
                            ON files.idPath = path.idPath;""")
            allKnownMovies = cursor.fetchall()
            self.updateText("Found {} files in Kodi...".format(len(allKnownMovies)))
            connection.close()
            p += 1
            mediaDirectory = QFileDialog.getExistingDirectory(self, "Select Media Directory To Scan")
            if mediaDirectory == "":
                self.updateText("Media directory cannot be ignored for option 1! Skipping...")
            else:
                # Definitely broken!
                # Start a thread safe queue
                self.queue = Queue()
                # Setup a timer
                self.option1Timer = QTimer(self)
                self.option1Timer.setInterval(1000)
                self.option1Timer.timeout.connect(self.updateMovieDirectoriesScanned)
                # Spin up a process
                self.activeProcess = VideoWorker(self.queue, mediaDirectory, allKnownMovies, 
                        self.fileOutputDir + "/Missing Movies.csv")
                # Start a timer for checking and updating the files found marker
                self.option1Timer.start()


        if self.allOptions['option2'].isChecked():
            # Establish a connection to the movie database
            connection = sqlite3.connect(videoDatabase)
            cursor = connection.cursor()
            # Get the movie name, movie path, movie filename
            cursor.execute("SELECT DISTINCT c00 FROM movie;")
            allKnownMovies = sorted(cursor.fetchall())
            allKnownMovies = list(map(lambda nameTup: '"{}"'.format(nameTup[0]), allKnownMovies))
            # Point out possible duplicates?
            cursor.execute("""SELECT movie.c00,cnt,strPath FROM movie
                            INNER JOIN files
                            ON files.idFile = movie.idFile
                            INNER JOIN path
                            ON path.idPath = files.idPath
                            LEFT JOIN (
                            SELECT c00, COUNT(c00) AS cnt FROM movie 
                            GROUP BY c00
                            ) AS temptable
                            ON movie.c00 = temptable.c00
                            WHERE cnt > 1;""")
            duplicates = sorted(cursor.fetchall())
            duplicates = list(map(lambda entry: ",".join(
                list(map(lambda item: '"{}"'.format(item), entry))), duplicates))
            self.updateText("Writing out a CSV of movie names from Kodi...")
            with open("{}/All Movies.csv".format(self.fileOutputDir), "w") as outfile:
                outfile.write("Title\n")
                outfile.write("\n".join(allKnownMovies))
            self.updateText("{}/All Movies.csv".format(self.fileOutputDir))
            with open("{}/All Duplicate Movies.csv".format(self.fileOutputDir), "w") as outfile:
                outfile.write("Title,Total,Path\n")
                outfile.write("\n".join(duplicates))
            self.updateText("{}/All Duplicate Movies.csv".format(self.fileOutputDir))
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
    
    # Possibly broken
    def updateMovieDirectoriesScanned(self):
        latest = None
        # Check if active
        qsize = self.queue.qsize()
        totalActive = active_children()
        # Check the queue
        for num in range(qsize):
            latest = self.queue.get()
                    
        if totalActive != 0:
            if latest is not None:
                self.option1ProgressLabel.show()
                self.option1ProgressLabel.setText("Located {} files in media storage...".format(str(latest)))
        else:
            if latest is not None:
                self.option1ProgressLabel.hide()
                self.updateText("Safe finish: {} files not imported into Kodi".format(latest))
                self.updateText("{}/Missing Movies.csv")
                self.option1Timer.stop()




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
            databaseRoot = "C:/Users/{}/AppData/Roaming/Kodi/userdata/Database".format(getuser())
        
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
            self.databases = databases
        else:
            # Need a better work around
            if databaseRoot == "" or databaseRoot != "C:/Users/{}/AppData/Roaming/Kodi/userdata/Database".format(getuser()):
                exit()
            self.updateText("No databases found at {}".format(databaseRoot))
            self.updateText("A new location must be selected and must contain the userdata folder for kodi or the application will crash")
            # Allow the user to pick a directory but see files
            # databaseRoot = QFileDialog.getExistingDirectory(self, "Select Database Location",QFileDialog.)
            databaseRoot = QFileDialog.getExistingDirectory(self, "Select Database Location")
            self.getDatabases(databaseRoot=databaseRoot)


if __name__ == "__main__":
    from sys import argv, exit
    app = QtWidgets.QApplication(argv)
    mainWin = Main()
    mainWin.show()
    exit(app.exec_())
