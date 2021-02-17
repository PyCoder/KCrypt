# accept.py
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
import os, os.path

class showAccept(QtGui.QDialog):
    def __init__(self, choice, device, fs, mountPoint, cipher, key_size, size, size_sufix, getMapping, passphrase=None, key_file=None):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi('./Ui/accept.ui', self)
                
        self.choice = choice
        self.device = device
        self.fs = fs
        self.mountPoint = mountPoint
        self.cipher = cipher
        self.key_size = key_size
        self.size = size
        self.size_sufix = size_sufix
        self.getMapping = getMapping
        self.passphrase = passphrase
        self.key_file = key_file
        
        # Workaround, because pycrypt blocks the GUI-Thread
        self.timer = QtCore.QTimer(self)        
        self.timer.singleShot(500, self.startThread)
        
    def startThread(self):
        self.thread = Thread(self.choice, self.device, self.passphrase, self.key_file, self.cipher, self.key_size, self.size, self.size_sufix, self.fs, self.mountPoint)
        self.thread.setStatusLabel.connect(self.statusLabel.setText)
        self.thread.setValue.connect(self.progressBar.setValue)
        self.thread.setMaximum.connect(self.progressBar.setMaximum)
        self.setCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))               
        self.thread.finished.connect(self.onFinish)
        self.thread.start()

    def onFinish(self):
            self.getMapping()
            self.close()        

class Thread(QtCore.QThread):
    setStatusLabel = QtCore.pyqtSignal(str)
    setValue = QtCore.pyqtSignal(int)
    setMaximum = QtCore.pyqtSignal(int)
    
    def __init__(self, choice, device, passphrase, key_file, cipher, key_size, size, size_sufix, fs, mountPoint):
        QtCore.QThread.__init__(self)
        self.choice = choice
        self.device = device
        self.passphrase = passphrase
        self.key_file = key_file
        self.cipher = cipher
        self.key_size = key_size
        self.size = size
        self.size_sufix = size_sufix
        self.fs = fs
        self.mountPoint = mountPoint
    
    def run(self):
        if self.choice == 0:
            steps = (self.createContainer, self.device, self.createLUKS)
            
            for i in range(len(steps)):
                if i == 1:
                    self.setStatusLabel.emit('Add Loop Device...')
                    self.device = addLoop(self.device)[1]
                else:
                    steps[i]()
        else:
            self.createLUKS()
            
    def createContainer(self):
        self.setStatusLabel.emit('Creating Imagefile..')
               
        if self.size_sufix =='MB':
            multi = 1024
        else:
            multi = 1024 * 1024
            
        self.setMaximum.emit(self.size * multi)
        
        f = open(self.device,  'wb')
        for i in xrange(self.size * multi): # Not Python 3000 compatible
            f.write('\x00' * 1024 )
            self.setValue.emit(i)
        f.close()
        self.setMaximum.emit(0)
        
    def createLUKS(self):
        self.setStatusLabel.emit('Creating LUKS Device...')
        luks_format(self.device, self.passphrase, self.cipher, self.key_size, self.key_file)
        self.setStatusLabel.emit('Fatching LUKS ID...')
        luksID = 'luks-' + luks_uuid(self.device)
        self.setStatusLabel.emit('Opening LUKS Device...')
        luks_open(self.device, luksID, self.passphrase, self.key_file)
        self.setStatusLabel.emit('Formating...')
        format('/dev/mapper/' + luksID, self.fs)
        
        self.setStatusLabel.emit('Mounting...')
        if self.mountPoint:
            self.mountPoint = self.mountPoint
        else:
            self.mountPoint = '/media/' + luksID
            
        if not os.path.exists(self.mountPoint):
            os.mkdir(self.mountPoint)
            
        mountDevice(self.mountPoint, '/dev/mapper/' + luksID, self.fs)
