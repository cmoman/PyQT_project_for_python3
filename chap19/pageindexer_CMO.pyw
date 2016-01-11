#!/usr/bin/env python3
# Copyright (c) 2008-10 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

import collections
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import walker_CMO as walker


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.fileCount = 0
        self.filenamesForWords = collections.defaultdict(set)
        self.commonWords = set()
        self.lock = QReadWriteLock()
        self.path = QDir.homePath()
        pathLabel = QLabel("Indexing path:")
        self.pathLabel = QLabel()
        self.pathLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        self.pathButton = QPushButton("Set &Path...")
        self.pathButton.setAutoDefault(False)
        findLabel = QLabel("&Find word:")
        self.findEdit = QLineEdit()
        findLabel.setBuddy(self.findEdit)
        commonWordsLabel = QLabel("&Common words:")
        self.commonWordsListWidget = QListWidget()
        commonWordsLabel.setBuddy(self.commonWordsListWidget)
        filesLabel = QLabel("Files containing the &word:")
        self.filesListWidget = QListWidget()
        filesLabel.setBuddy(self.filesListWidget)
        filesIndexedLabel = QLabel("Files indexed")
        self.filesIndexedLCD = QLCDNumber()
        self.filesIndexedLCD.setSegmentStyle(QLCDNumber.Flat)
        wordsIndexedLabel = QLabel("Words indexed")
        self.wordsIndexedLCD = QLCDNumber()
        self.wordsIndexedLCD.setSegmentStyle(QLCDNumber.Flat)
        commonWordsLCDLabel = QLabel("Common words")
        self.commonWordsLCD = QLCDNumber()
        self.commonWordsLCD.setSegmentStyle(QLCDNumber.Flat)
        self.statusLabel = QLabel("Click the 'Set Path' "
                                  "button to start indexing")
        self.statusLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)

        topLayout = QHBoxLayout()
        topLayout.addWidget(pathLabel)
        topLayout.addWidget(self.pathLabel, 1)
        topLayout.addWidget(self.pathButton)
        topLayout.addWidget(findLabel)
        topLayout.addWidget(self.findEdit, 1)
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(filesLabel)
        leftLayout.addWidget(self.filesListWidget)
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(commonWordsLabel)
        rightLayout.addWidget(self.commonWordsListWidget)
        middleLayout = QHBoxLayout()
        middleLayout.addLayout(leftLayout, 1)
        middleLayout.addLayout(rightLayout)
        bottomLayout = QHBoxLayout()
        bottomLayout.addWidget(filesIndexedLabel)
        bottomLayout.addWidget(self.filesIndexedLCD)
        bottomLayout.addWidget(wordsIndexedLabel)
        bottomLayout.addWidget(self.wordsIndexedLCD)
        bottomLayout.addWidget(commonWordsLCDLabel)
        bottomLayout.addWidget(self.commonWordsLCD)
        bottomLayout.addStretch()
        layout = QVBoxLayout()
        layout.addLayout(topLayout)
        layout.addLayout(middleLayout)
        layout.addLayout(bottomLayout)
        layout.addWidget(self.statusLabel)
        self.setLayout(layout)
        
        self.setWindowTitle("Page Indexer")

        self.walker = walker.Walker(self.lock)
        #self.connect(self.walker, SIGNAL("indexed(QString)"), self.indexed, SLOT("indexed(QString)"))
        #self.connect(self.walker, SIGNAL("finished(bool)"), self.finished, SLOT("finished(bool)"))
        
        self.connect(self.walker, SIGNAL("indexed(QString)"), self, SLOT("indexed(QString)"))
        self.connect(self.walker, SIGNAL("finished(bool)"), self, SLOT("finished(bool)"))        
        
        self.connect(self.pathButton, SIGNAL("clicked()"), self.setPath)
        self.connect(self.findEdit, SIGNAL("returnPressed()"), self.find)

        self.threadx = QThread()
        self.connect(self.walker, SIGNAL("stopped(bool)"), self.threadx, SLOT('quit()'))
        
        self.connect(self, SIGNAL("destroyed()"), self.walker, SLOT("deleteLater()"))
        self.connect(self, SIGNAL("destroyed()"), self.threadx, SLOT("deleteLater()"))
        
        self.walker.moveToThread(self.threadx)

    @pyqtSlot() # from pathButton
    def setPath(self):
        self.pathButton.setEnabled(False)
        if self.threadx.isRunning():
            self.walker.stop() # this methods will return a signal to stop the threads
            self.threadx.wait()
        path = QFileDialog.getExistingDirectory(self,
                    "Choose a Path to Index", self.path)
        if not path:
            self.statusLabel.setText("Click the 'Set Path' "
                                     "button to start indexing")
            self.pathButton.setEnabled(True)
            return
        self.path = QDir.toNativeSeparators(path)
        self.findEdit.setFocus()
        self.pathLabel.setText(self.path)
        self.statusLabel.clear()
        self.filesListWidget.clear()
        self.fileCount = 0
        self.filenamesForWords = collections.defaultdict(set)
        self.commonWords = set()
        self.walker.initialize(self.path,
                self.filenamesForWords, self.commonWords)
        self.threadx.start()
        self.walker.run()

    @pyqtSlot() # from FindButton
    def find(self):
        word = self.findEdit.text()
        if not word:
            self.statusLabel.setText("Enter a word to find in files")
            return
        self.statusLabel.clear()
        self.filesListWidget.clear()
        word = word.lower()
        if " " in word:
            word = word.split()[0]
        with QReadLocker(self.lock):
            found = word in self.commonWords
        if found:
            self.statusLabel.setText(
                    "Common words like '{}' are not indexed".format(word))
            return
        with QReadLocker(self.lock):
            files = self.filenamesForWords.get(word, set()).copy()
        if not files:
            self.statusLabel.setText(
                    "No indexed file contains the word '{}'".format(word))
            return
        files = [QDir.toNativeSeparators(name) for name in
                 sorted(files, key=str.lower)]
        self.filesListWidget.addItems(files)
        self.statusLabel.setText(
                "{} indexed files contain the word '{}'".format(
                len(files), word))

    @pyqtSlot(str) # from walker object
    def indexed(self, fname):
        print('arrived {}'.format(fname))
        self.statusLabel.setText(fname)
        self.fileCount += 1
        if self.fileCount % 25 == 0:
            self.filesIndexedLCD.display(self.fileCount)
            with QReadLocker(self.lock):
                indexedWordCount = len(self.filenamesForWords)
                commonWordCount = len(self.commonWords)
            self.wordsIndexedLCD.display(indexedWordCount)
            self.commonWordsLCD.display(commonWordCount)
        elif self.fileCount % 101 == 0:
            self.commonWordsListWidget.clear()
            with QReadLocker(self.lock):
                words = self.commonWords.copy()
            self.commonWordsListWidget.addItems(sorted(words))

    @pyqtSlot(bool) # from walker object
    def finished(self, completed):
        self.statusLabel.setText("Indexing complete"
                                 if completed else "Stopped")
        self.finishedIndexing()


    def reject(self):
        if self.threadx.isRunning():
            self.walker.stop()
            self.finishedIndexing()
        else:
            self.accept()


    def closeEvent(self, event=None):
        self.walker.stop()
        self.threadx.wait()


    def finishedIndexing(self):
        self.threadx.wait()
        self.filesIndexedLCD.display(self.fileCount)
        self.wordsIndexedLCD.display(len(self.filenamesForWords))
        self.commonWordsLCD.display(len(self.commonWords))
        self.pathButton.setEnabled(True)


app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()

