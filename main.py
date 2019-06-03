import sys
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget,  QCheckBox, QTextEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QSize    

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


        
        # Find all media that Kodi doesn't see
        # Find all media that Kodi sees
        # Find missing TV Show seasons
    
    def doAllPossibleActions(self):
        p = 0
        # If a current job is running, kill it!
        # Setup a QTimer that periodically updates the progress while checking if they're active
        if self.allOptions['option1'].isChecked():
            p += 1
            locateMissingMedia()
            # self.updateText("Found {} missing movies!".format(numMissing))
            # Write out the file
        if self.allOptions['option2'].isChecked():
            p += 1
            # self.updateText("Found {} movies logged by Kodi...".format(numFound))
            # Write out the file
        if self.allOptions['option3'].isChecked():
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


    def updateText(self, moreText):
        self.logText.setText("{}{}{}".format(self.logText.toPlainText(), moreText, "\n"))
        self.logText.verticalScrollBar().setValue(self.logText.verticalScrollBar().maximum())
        return None

# This should be run by an external process
# This is very very slow when on the scale of terabytes - Cython? SWIG?
def locateMissingMedia(self, outputDir, selectedDirectory, db):
    # Open connection to the database
    # Gather all information needed from the database
    # Media name, media location
    # Gather all media name and locations from selectedDirectory
    # This is slow perhaps use C/C++ with Cython/SWIG to make it faster
    # Use list -> set -> difference -> list to remove matching entries
    # Write out file that contains the name and locations of all missing media
    # Return the number of entries missing
    pass
# This should be run by an external process - Entirely in python is fine
def outputKnownMedia(self, outputDir, selectedDirectory, db):
    # Open connection to the database
    # Gather all information needed from the database
    # Media name, media location
    # Write out a file that contains the name and locations of all known media
    # Return the number of entries found
    pass

if __name__ == "__main__":
    from sys import argv
    app = QtWidgets.QApplication(argv)
    mainWin = Main()
    mainWin.show()
    sys.exit(app.exec_())
