# add_del_key.py
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
from generic import getLuksPartitions
from crypto import luks_addKey, luks_removeKey
from os.path import isfile
from unlock import showUnlock

class showAddDelKey(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi('./Ui/add_del_key.ui', self)
        
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)
        
        # Get all Luks partitions
        partitions = getLuksPartitions()
        
        # Fill comboBoxs
        self.addBox.addItems(partitions)
        self.removeBox.addItems(partitions)
        
        # Setup signal and slots
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.onButtonApply)
        self.addButtonBox.accepted.connect(self.openNewKeyfile)
        self.removeButtonBox.accepted.connect(self.openDelKeyfile)
        self.tabWidget.currentChanged.connect(self.enableButtonApply)
        self.new_keyfile.textChanged.connect(self.enableButtonApply)
        self.del_keyfile.textChanged.connect(self.enableButtonApply)
        
    def enableButtonApply(self):
        if self.tabWidget.currentIndex() == 0:
            if self.addBox.currentIndex() != 0 and self.new_keyfile.text():
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(True)
            else:
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)
        else:
            if self.removeBox.currentIndex() != 0 and self.del_keyfile.text():
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(True)
            else:
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)
                
    def openNewKeyfile(self):
        keyfile = QtGui.QFileDialog.getOpenFileName(self, self.tr('Select Keyfile'), '~')
        self.new_keyfile.setText(keyfile) 
        
    def openDelKeyfile(self):
        keyfile = QtGui.QFileDialog.getOpenFileName(self, self.tr('Select Keyfile To Remove'), '~')
        self.del_keyfile.setText(keyfile)
        
    def onButtonApply(self):
        unlock = showUnlock(self)
        unlock.exec_() 
        passphrase = str(unlock.linePassphrase.text())
        
        if passphrase:
            self.setCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
            
            if self.tabWidget.currentIndex() == 0:
                if isfile(passphrase):
                    ret = luks_addKey(str(self.addBox.currentText()), str(self.new_keyfile.text()), None, passphrase)
                else:
                    ret = luks_addKey(str(self.addBox.currentText()), str(self.new_keyfile.text()), passphrase, None)
            else:
                if isfile(passphrase):
                    ret = luks_removeKey(str(self.removeBox.currentText()), str(self.del_keyfile.text()), None, passphrase)
                else:
                    ret = luks_removeKey(str(self.removeBox.currentText()), str(self.del_keyfile.text()), passphrase, None)
 
            if not ret:
                QtGui.QMessageBox.warning(self, self.tr('Error!'), self.tr('Could not unlock device'), QtGui.QMessageBox.Close)
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            else:
                if QtGui.QMessageBox.information(self, self.tr('Successfully!'), self.tr('Keyfile successfully added/removed'), QtGui.QMessageBox.Close) == QtGui.QMessageBox.Close:
                    self.close()
