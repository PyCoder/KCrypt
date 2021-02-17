# backup_restore.py
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
from crypto import *

class showBackupRestore(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi('./Ui/backup_restore.ui', self)
        
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)
        
        # Get partitions
        luks_partitions = getLuksPartitions()
        partitions = getPartitions()
        
        # Fill the comboBoxs
        self.restoreBox.addItems(partitions)
        self.backupBox.addItems(luks_partitions)

        # Setup signal and slots
        self.buttonBox_Backup.accepted.connect(self.onButtonSaveFile)
        self.buttonBox_Restore.accepted.connect(self.onButtonOpenFile)
        self.tabWidget.currentChanged.connect(self.enableButtonApply)
        self.backupBox.currentIndexChanged.connect(self.enableButtonApply)
        self.restoreBox.currentIndexChanged.connect(self.enableButtonApply)
        self.lineBackup.textChanged.connect(self.enableButtonApply)
        self.lineRestore.textChanged.connect(self.enableButtonApply)
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.onButtonApply)
        
    def enableButtonApply(self):
        if self.tabWidget.currentIndex() == 0:
            if self.backupBox.currentIndex() != 0 and self.lineBackup.text():
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(True)
            else: 
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)
        else:
            if self.restoreBox.currentIndex() != 0 and self.lineRestore.text():
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(True)
            else:
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)  
    
    def onButtonOpenFile(self):
        self.file = QtGui.QFileDialog.getOpenFileName(self, self.tr('Open Header-File'), '~')
        self.lineRestore.setText(self.file)
    
    def onButtonSaveFile(self):
        self.file = QtGui.QFileDialog.getSaveFileName(self, self.tr('Save Header-File'), '~')
        self.lineBackup.setText(self.file)
          
    def onButtonApply(self):
        if self.tabWidget.currentIndex() == 0 and self.lineBackup.text():
            ret = luks_header_backup(str(self.backupBox.currentText()), str(self.lineBackup.text()))
        else:
            ret = luks_header_restore(str(self.restoreBox.currentText()), str(self.lineRestore.text()))

        if ret:
            QtGui.QMessageBox.warning(self, self.tr('Error!'), ret, QtGui.QMessageBox.Close)
        else:
            if QtGui.QMessageBox.information(self, self.tr('Successfully!'), 'Successfully restored/backuped', QtGui.QMessageBox.Close) == QtGui.QMessageBox.Close:
                self.close()
