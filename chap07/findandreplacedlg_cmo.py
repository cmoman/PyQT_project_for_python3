import re
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSlot, pyqtSignal
import ui_findandreplacedlg

class FindAndReplaceDlg(QtGui.QDialog, ui_findandreplacedlg.Ui_FindAndReplaceDlg):
    
    found = pyqtSignal(int)
    notfound = pyqtSignal()
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.__text = text
        self.__index = 0
        self.setupUi(self) # calls QtCore.QMetaObject.connectSlotsByName()
        
        self.updateUI()
    
    @pyqtSlot(str)
    def on_findLineEdit_textEdited(self, text):
        self.__index=0
        self.updateUI()
        
    def makeRegex(self):
        findText=self.findLineEdit.text()
        if self.syntaxComboBox.currentText() == "Literal":
            findText = re.escape(findText)
        flags = re.MULTILINE|re.DOTALL|re.UNICODE
        
        if not self.caseCheckBox.isChecked():
            flags|=re.IGNORECASE
        if self.wholeCheckBox.isChecked():
            findText=r"\b{}\b".format(findText)
        return re.compile(findText, flags)
    
    @pyqtSlot()
    def on_findButton_clicked(self):
        regex  = self.makeRegex()
        match = regex.search(self.__text, self.__index)
        
        if match is not None:
            self.__index=match.end()
            self.found.emit(match.start())
        else:
            self.notfound.emit()
        
    @pyqtSlot()
    def on_replaceButton_clicked(self):
        regex = self.makeRegex()
        self.__text=regex.sub(self.replaceLineEdit.text(),self.__text,1)
        
    @pyqtSlot()
    def on_replaceAllButton_clicked(self):
        regex = self.makeRegex()
        self.__text = regex.sub(self.replaceLineEdit.text(),
                                self.__text)  
        
    def updateUI(self):
        enable = bool(self.findLineEdit.text())
        self.findButton.setEnabled(enable)
        self.replaceButton.setEnabled(enable)
        self.replaceAllButton.setEnabled(enable) 
    
    def text(self):
        return self.__text        
        
if __name__ == "__main__":
    import sys

    text = """US experience shows that, unlike traditional patents,
software patents do not encourage innovation and R&D, quite the
contrary. In particular they hurt small and medium-sized enterprises
and generally newcomers in the market. They will just weaken the market
and increase spending on patents and litigation, at the expense of
technological innovation and research. Especially dangerous are
attempts to abuse the patent system by preventing interoperability as a
means of avoiding competition with technological ability.
--- Extract quoted from Linus Torvalds and Alan Cox's letter
to the President of the European Parliament
http://www.effi.org/patentit/patents_torvalds_cox.html"""

    def found(where):
        print("Found at {}".format(where))

    def nomore():
        print("No more found")

    app = QtGui.QApplication(sys.argv)
    form = FindAndReplaceDlg(text)
    
    
    form.found.connect(found)
    form.notfound.connect(nomore)

    
    #form.connect(form, SIGNAL("found"), found)
    #form.connect(form, SIGNAL("notfound"), nomore)
    form.show()
    app.exec_()
    print(form.text())
