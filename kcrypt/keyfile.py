# keyfile.py
#
# Copyright (C) 2012  Fabian Di Milia, All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author(s): Fabian Di Milia <info@2blabla.ch>

from PyQt4 import QtGui, QtCore, uic
from generic import *

class showKeyfile(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi('./Ui/keyfile.ui', self)
        
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)
        
        # Setup signal and slots
        self.selectKeyfile.accepted.connect(self.openSelectKeyfile)
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.onButtonApply)
        self.lineKeyfile.textChanged.connect(self.enableButtonApply)
        
    def enableButtonApply(self):
        if self.lineKeyfile.text():
            self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(True)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)    
    
    def openSelectKeyfile(self):
        keyfile = QtGui.QFileDialog.getSaveFileName(self, self.tr('Save Random Keyfile'), '~')
        self.lineKeyfile.setText(keyfile)
        
    def onButtonApply(self):
        ret = genKeyfile(str(self.lineKeyfile.text()))
        
        if ret:
            QtGui.QMessageBox.warning(self, self.tr('Error!'), ret, QtGui.QMessageBox.Close)
        else:
            if QtGui.QMessageBox.information(self, self.tr('Successfully!'), self.tr('Keyfile successfully saved'), QtGui.QMessageBox.Close) == QtGui.QMessageBox.Close:
                self.close()

