# erase.py
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
from os import urandom
import parted
from generic import getPartitions

class showErase(QtGui.QDialog):
    # Method
    ZERO = ['\x00\x00\x00\x00']
    NSA_130_2 = ['random', 'random']
    GHOST =['\x00\x00\x00\x00', 'random']
    HMG_IS_5 = ['\x00\x00\x00\x00', '\xff\xff\xff\xff', 'random']
    DOD_E = ['7\x00\x00\x00', 'random', '\xff\x00\x00\x00']
    DOD_ECE = ['7\x00\x00\x00', 'random', '\xff\x00\x00\x00', 'random', '7\x00\x00\x00', 'random', '\xff\x00\x00\x00']
    CANADIAN_OPS_II = ['\x00\x00\x00\x00', '\xff\xff\xff\xff', '\x00\x00\x00\x00', '\xff\xff\xff\xff', '\x00\x00\x00\x00', '\xff\xff\xff\xff', 'random'] 
    VSITR = ['\x00\x00\x00\x00', '\xff\x00\x00\x00', '\x00\x00\x00\x00', '\xff\x00\x00\x00', '\x00\x00\x00\x00', '\xff\x00\x00\x00', '\xaa\x00\x00\x00']
    BRUCE_SCHNEIER = ['\xff\xff\xff\xff', '\x00\x00\x00\x00', 'random', 'random', 'random', 'random', 'random']
    GUTMAN = ['random', 'random', 'random', 'random', 'U\x00\x00\x00', '\xaa\x00\x00\x00', '$I\x92\x00', '\x92$I\x00', 'I\x92$\x00',
                   '\x00\x00\x00\x00', '\x11\x00\x00\x00', '"\x00\x00\x00', '3\x00\x00\x00', 'D\x00\x00\x00', 'U\x00\x00\x00', 'f\x00\x00\x00',
                   'w\x00\x00\x00', '\x88\x00\x00\x00', '\x99\x00\x00\x00', '\xaa\x00\x00\x00', '\xbb\x00\x00\x00', '\xcc\x00\x00\x00', 
                   '\xdd\x00\x00\x00', '\xee\x00\x00\x00', '\xff\x00\x00\x00', '$I\x92\x00', '\x92$I\x00', 'I\x92$\x00', '\xdb\xb6m\x00',
                   'm\xdb\xb6\x00', '\xb6m\xdb\x00', 'random', 'random', 'random', 'random']
       
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi('./Ui/erase.ui', self)

        # Disable ButtonOk
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        
        # Add Device/Partition
        self.comboDevice.addItems(getPartitions())
    
        # Signal and Slots
        self.buttonBox.accepted.connect(self.onButtonOk)
        self.buttonBox.button(QtGui.QDialogButtonBox.Close).clicked.connect(self.close)
        self.comboMethod.currentIndexChanged.connect(self.onMethodChange)
        self.comboDevice.currentIndexChanged.connect(self.enableButtonOk)
       
    def onMethodChange(self):
        if self.comboMethod.currentIndex() == 0:
            self.algo = self.ZERO
            self.labelPasses.setText('0/1')
        elif self.comboMethod.currentIndex() == 1:
            self.algo = self.NSA_130_2
            self.labelPasses.setText('0/2')
        elif self.comboMethod.currentIndex() == 2:
            self.algo = self.GHOST
            self.labelPasses.setText('0/2')
        elif self.comboMethod.currentIndex() == 3:
            self.algo = self.HMG_IS_5
            self.labelPasses.setText('0/3')
        elif self.comboMethod.currentIndex() == 4:
            self.algo = self.DOD_E
            self.labelPasses.setText('0/3')
        elif self.comboMethod.currentIndex() == 5:
            self.algo = self.DOD_ECE
            self.labelPasses.setText('0/7')
        elif self.comboMethod.currentIndex() == 6:
            self.algo = self.CANADIAN_OPS_II
            self.labelPasses.setText('0/7')
        elif self.comboMethod.currentIndex() == 7:
            self.algo = self.VSITR
            self.labelPasses.setText('0/7')
        elif self.comboMethod.currentIndex() == 8:
            self.algo = self.BRUCE_SCHNEIER
            self.labelPasses.setText('0/7')
        else:
            self.algo = self.GUTMAN
            self.labelPasses.setText('0/35')

    def enableButtonOk(self):
        if self.comboDevice.currentIndex() == 0:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)

    def onButtonOk(self):
        # Get size of Device/Partition
        self.size = int(parted.getDevice(str(self.comboDevice.currentText())).getSize('KB'))

        # Setup Progressbar
        self.progressBar.setFormat('%p%')
        self.progressBar.setMaximum(self.size)

        # Start Thread
        self.thread = Thread(self.algo, self.comboDevice.currentText(), self.size)
        self.thread.start()

        # Signal and Slots for QThread
        self.buttonBox.button(QtGui.QDialogButtonBox.Abort).clicked.connect(self.thread.stop)
        self.thread.finished.connect(self.onFinish)
        self.thread.cleaning.connect(self.progressBar.setFormat)
        self.thread.dataWritten.connect(self.progressBar.setValue)
        self.thread.currentPass.connect(self.labelPasses.setText)
        
        # Disable OK Button
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        # Set Cursor busy
        self.setCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))

    def onFinish(self):
        if self.thread.terminated:
            self.progressBar.setFormat(self.tr('Aborted'))
            
        else:
            self.progressBar.setFormat(self.tr('succsessfully completed'))
        self.progressBar.setValue(self.size)
        
        # Enable OK Button
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        # Set Cursor not busy
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

class Thread(QtCore.QThread):
    dataWritten = QtCore.pyqtSignal(int)
    currentPass = QtCore.pyqtSignal(str)
    cleaning = QtCore.pyqtSignal(str)
    terminated = False
    
    def __init__(self, algo, device, size):
        QtCore.QThread.__init__(self)
        self.algo = algo
        self.device = device
        self.size = size
        self.semaphore = QtCore.QSemaphore(1)
   
    def run(self):
        stat = 0
        f = open(self.device, 'wb')
 
        for method in self.algo:
            if self.semaphore.available() != 0:     
                if method == 'random':
                    data = urandom(1000)
                else:
                    data = method * 256
                        
                for i in xrange(self.size): # not Python 3000 compatible (range)
                    if self.semaphore.available() != 0:
                        f.write(data)
                        self.dataWritten.emit(i)
                    else:
                        self.terminated = True 
                        break
               
                f.seek(0)
                stat +=1
                self.currentPass.emit(str(stat)+'/'+str(len(self.algo)))
            else:
                self.terminated = True
                break
        self.cleaning.emit(self.tr('Finalize'))    
        f.close()
        
    def stop(self):
        self.semaphore.acquire(1)
