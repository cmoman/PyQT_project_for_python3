#!/usr/bin/env python3
# Cmo version

import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import moviedata_cmo as moviedata
import ui_addeditmoviedlg_cmo as ui_addeditmoviedlg

class AddEditMoviveDlg(QtGui.QDialog, ui_addeditmoviedlg.Ui_AddEditMovieDlg):
    def __init__(self, movies, movie=None, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        self.movies = movies
        self.movie = movie
        self.acqu
            