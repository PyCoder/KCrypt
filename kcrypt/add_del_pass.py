# add_del_pass.py
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

class showAddDelPass(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi('./Ui/add_del_pass.ui', self)
        
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)
        
        # Get Luks partitions
        partitions = getLuksPartitions()
        
        # Fill comboBoxs
        self.addBox.addItems(partitions)
        self.removeBox.addItems(partitions)
    
        # Setup signal and slots
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.onButtonApply)
        self.addBox.currentIndexChanged.connect(self.enableButtonApply)
        self.removeBox.currentIndexChanged.connect(self.enableButtonApply)
        self.tabWidget.currentChanged.connect(self.enableButtonApply)
        self.new_passphrase.textChanged.connect(self.enableButtonApply)
        self.verify_passphrase.textChanged.connect(self.enableButtonApply)
        self.del_passphrase.textChanged.connect(self.enableButtonApply)
        
    def enableButtonApply(self):
        if self.tabWidget.currentIndex() == 0:
            if self.addBox.currentIndex() != 0 and self.new_passphrase.text() and self.verify_passphrase.text() and self.new_passphrase.text() == self.verify_passphrase.text():
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(True)
            else:
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)
        else:
            if self.removeBox.currentIndex() != 0 and self.del_passphrase.text():
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(True)
            else:
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)
        
    def onButtonApply(self):
        if self.new_passphrase.text() == self.verify_passphrase.text():
            unlock = showUnlock(self)
            unlock.exec_() 
            passphrase = str(unlock.linePassphrase.text())
            
            if passphrase:
                self.setCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
                       
                if self.tabWidget.currentIndex() == 0:
                    if isfile(passphrase):
                        ret = luks_addKey(str(self.addBox.currentText()), str(self.new_passphrase.text()), None, passphrase)
                    else:
                        ret = luks_addKey(str(self.addBox.currentText()), str(self.new_passphrase.text()), passphrase, None)
                else:
                    if isfile(passphrase):
                        ret = luks_removeKey(str(self.removeBox.currentText()), str(self.del_passphrase.text()), None, passphrase)
                    else:
                        ret = luks_removeKey(str(self.removeBox.currentText()), str(self.del_passphrase.text()), passphrase, None)                
                        
                if ret:
                    if QtGui.QMessageBox.information(self, self.tr('Successfully!'), self.tr('Passphrase successfully added/removed'), QtGui.QMessageBox.Close) == QtGui.QMessageBox.Close:
                        self.close()
                else:
                    QtGui.QMessageBox.warning(self, self.tr('Error!'), self.tr('Could not unlock device'), QtGui.QMessageBox.Close)
                    self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        else:
            QtGui.QMessageBox.warning(self,self.tr('Passphrase do not match!'),self.tr('Passphrase do not match'), QtGui.QMessageBox.Close)
