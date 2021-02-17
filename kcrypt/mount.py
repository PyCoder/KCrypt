# mount.py
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
from unlock import showUnlock
from generic import mountDevice, addLoop, removeLoop
from crypto import is_luks, luks_open, luks_uuid
from os.path import isfile,isdir 
from os import stat, mkdir
from stat import S_ISBLK, ST_MODE

class showMount(QtGui.QDialog):
    def __init__(self, getMapping, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi('./Ui/mount.ui', self)
        
        self.getMapping = getMapping
        
        # Disable Apply Button
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)
        
        self.lineMount.setPlaceholderText('auto mount point')

        # Signal and Slots
        self.selectDevice.accepted.connect(self.openSelectDevice)
        self.selectMount.accepted.connect(self.openSelectMount)
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.onButtonApply)
        self.lineDevice.textChanged.connect(self.enableButtonApply)
        self.lineMount.textChanged.connect(self.enableButtonApply)
            
    def enableButtonApply(self):
        try:
            if isfile(str(self.lineDevice.text())) or S_ISBLK(stat(str(self.lineDevice.text()))[ST_MODE]):
                if isdir(str(self.lineMount.text())) or self.lineMount.text().isEmpty():
                    self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(True)
                else:
                    self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)
            else:
                self.buttonBox.button(QtGui.QDialogButtonBox.Apply).setEnabled(False)  
        except OSError:
            pass
        
    def openSelectDevice(self):
        device = QtGui.QFileDialog.getOpenFileName(self, self.tr('Select Device Or Container'), '~')
        self.lineDevice.setText(device)
            
    def openSelectMount(self):
        mount = QtGui.QFileDialog.getExistingDirectory(self, self.tr('Select Mount-Point'), '~', QtGui.QFileDialog.ShowDirsOnly)
        self.lineMount.setText(mount)

    def onFinish(self):
        self.getMapping()
        self.close()
        
    def onError(self, reason):
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        if reason == 0:
            QtGui.QMessageBox.warning(self, self.tr('Error!'), self.tr('Wrong password or keyfile'), QtGui.QMessageBox.Close) 
        else:
            QtGui.QMessageBox.warning(self, self.tr('Error!'), self.tr('Selected device is not a luks device'), QtGui.QMessageBox.Close)
    
    def onButtonApply(self):
        unlock = showUnlock(self)
        unlock.exec_() 
        passphrase = str(unlock.linePassphrase.text())
    
        self.setCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        
        self.thread = Thread(str(self.lineDevice.text()), str(self.lineMount.text()), str(self.comboBox.currentText()), passphrase, passphrase)
        self.thread.finished.connect(self.onFinish)
        self.thread.emitError.connect(self.onError)
        self.thread.start()

class Thread(QtCore.QThread):
    emitError = QtCore.pyqtSignal(int)
    
    def __init__(self, device, mountpoint, fs, passphrase, key_file):
        QtCore.QThread.__init__(self)
        self.device = device
        self.mountpoint = mountpoint
        self.fs = fs
        self.passphrase = passphrase
        self.key_file = key_file
        
    def run(self):
        if isfile(self.device):
            lo = addLoop(self.device)
            self.device = lo[1]

        if is_luks(self.device) == 0:
            luksID = 'luks-' + luks_uuid(self.device)
            
            if luks_open(self.device, luksID, self.passphrase, self.key_file):
                if not self.mountpoint:
                    mkdir('/media/' + luksID)
                    self.mountpoint = '/media/' + luksID
                mountDevice(self.mountpoint, '/dev/mapper/' + luksID, self.fs)
            else:
                if '/dev/loop' in self.device:
                    removeLoop(self.device)          
                self.emitError.emit(0)
        else:
            self.emitError.emit(1)
