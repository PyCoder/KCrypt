# wizard.py
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

from PyQt4 import QtGui, QtCore, Qt, uic
from generic import getPartitions, supportedFS
from accept import showAccept

class showWizard(QtGui.QWizard):
    def __init__(self, getMapping, parent):
        QtGui.QWizard.__init__(self, parent)
        self.ui = uic.loadUi('./Ui/wizard/wizard.ui', self)

        # Get Mappings
        self.getMapping = getMapping
        
        # Setup supported, filesystems, ciphers and get partitions
        filesystems = supportedFS()
        ciphers = ['aes-xts-plain', 'serpent-xts-plain', 'twofish-xts-plain','aes-cbc-essiv:sha256', 'serpent-cbc-essiv:sha256', 'twofish-cbc-essiv:sha256']
        partitions = getPartitions()

        # Setup windowtitle, style and logo
        self.setWindowTitle(self.tr('KCrypt Creation Wizard'))
        self.setPixmap(QtGui.QWizard.WatermarkPixmap, QtGui.QPixmap('./icons/wizard-logo.png'))

        # Setup pages
        self.addPage(choice())
        self.addPage(container(filesystems))
        self.addPage(partition(partitions,  filesystems))
        self.addPage(encryption(ciphers))
        self.addPage(overview())
     
    def accept(self):
        if self.field('container').toBool():
            choice = 0
            device = str(self.field('contPath').toString())
            mountPoint = str(self.field('contMount').toString())
            fs = str(self.field('contFsBox').toString())
        else:
            choice = 1
            device = str(self.field('partBox').toString())
            mountPoint = str(self.field('partMount').toString())
            fs = str(self.field('partFsBox').toString())
         
        accept = showAccept(choice, device, fs, mountPoint, str(self.field('cipherBox').toString()), 512, self.field('size').toInt()[0], str(self.field('sizeBox').toString()), self.getMapping, str(self.field('passphrase_0').toString()), None)
        accept.exec_()
        self.close()
        
class choice(QtGui.QWizardPage):
    def __init__(self):
        QtGui.QWizardPage.__init__(self)
        self.ui = uic.loadUi('./Ui/wizard/choice.ui', self)

        # Page title and subtitle
        self.setTitle(self.tr('Welcome to KCrypt creation wizard'))
        self.setSubTitle(self.tr('Chose between encrypted disk image or partition'))

        # Register fields for next button
        self.registerField('container*', self.container)
        self.registerField('partition*', self.partition)

    def nextId(self):
        if self.container.isChecked():
            return 1
        else:
            return 2

    def isComplete(self):
        if self.container.isChecked() or self.partition.isChecked():
            return True
        else:
            return False
        
class container(QtGui.QWizardPage):
    def __init__(self,  filesystems):
        QtGui.QWizardPage.__init__(self)
        self.ui = uic.loadUi('./Ui/wizard/container.ui', self)
        
        # Page title and subtitle
        self.setTitle(self.tr('Container Settings:'))
        self.setSubTitle(self.tr('Creating a encrypted File, that can be looped!'))

        # Create combobox
        self.FsBox.addItems(filesystems)

        # Create lineedit
        self.mountPath.setPlaceholderText(self.tr('auto mount point'))

        # Setup Validator
        self.size.setValidator(QtGui.QIntValidator(1, 1000000000, self))

        # Register fields for next button
        self.registerField('contFsBox', self.FsBox,  'currentText',  QtCore.SIGNAL('currentIndexChanged()'))
        self.registerField('sizeBox', self.sizeBox,  'currentText',  QtCore.SIGNAL('currentIndexChanged()'))
        self.registerField('contPath*', self.contPath)
        self.registerField('contMount', self.mountPath)
        self.registerField('size*', self.size)

        # Singals and slots
        self.selectFile.accepted.connect(self.openSaveFile)
        self.selectMount.accepted.connect(self.openMountPoint)

    def openSaveFile(self):
        saveFile = QtGui.QFileDialog.getSaveFileName(self, self.tr('Create Container'), '~')
        self.contPath.setText(saveFile)
    
    def openMountPoint(self):
        mountPoint = QtGui.QFileDialog.getExistingDirectory(self, self.tr('Select Mount-Point'), '~', QtGui.QFileDialog.ShowDirsOnly)
        self.mountPath.setText(mountPoint)
        
    def nextId(self):
        return 3

class partition(QtGui.QWizardPage):
    def __init__(self,  partitions, filesystems):
        QtGui.QWizardPage.__init__(self)
        self.ui = uic.loadUi('./Ui/wizard/partition.ui', self)

        # Setup text and subtext
        self.setTitle(self.tr('Partition Settings:'))
        self.setSubTitle(self.tr('Creating a encryted device or partition!'))
        
        # Create lineedit
        self.mountPath.setPlaceholderText(self.tr('auto mount point'))

        # Create combobox
        self.partBox.addItem(self.tr('None'))
        self.partBox.addItems(partitions) 
        self.FsBox.addItems(filesystems)

        # Register fields for next button
        self.registerField('partBox', self.partBox, 'currentText', QtCore.SIGNAL('currentIndexChanged()'))
        self.registerField('checkPartBox*', self.partBox)
        self.registerField('partFsBox', self.FsBox, 'currentText', QtCore.SIGNAL('currentIndexChanged()'))
        self.registerField('partMount', self.mountPath)
        
        # Singals and slots
        self.selectMount.accepted.connect(self.openMountPoint)
        
    def openMountPoint(self):
        mountPoint = QtGui.QFileDialog.getExistingDirectory(self, self.tr('Select Mount-Point'), '~', QtGui.QFileDialog.ShowDirsOnly)
        self.mountPath.setText(mountPoint)
    
    def isComplete(self):
        if self.field('checkPartBox').toInt()[0] == 0:
            return False
        else:
            return True
    
class encryption(QtGui.QWizardPage):
    def __init__(self,  ciphers):
        QtGui.QWizardPage.__init__(self)
        self.ui = uic.loadUi('./Ui/wizard/encryption.ui', self)

#        # Setup text and subtext
        self.setTitle(self.tr('Encryption Settings:'))
        self.setSubTitle(self.tr('Hint: Use a strong password!'))

#        # Create combobox
        self.cipherBox.addItems(ciphers)

        # Register fields for next button
        self.registerField('passphrase_0*', self.passphrase_0)
        self.registerField('passphrase_1*', self.passphrase_1)
        self.registerField('cipherBox',  self.cipherBox,  'currentText',  QtCore.SIGNAL('currentIndexChanged()'))
        
    def validatePage(self):
        if str(self.passphrase_0.text()).isalpha() or str(self.passphrase_0.text()).isdigit() and len(self.passphrase_0.text()) <20:
            ret = QtGui.QMessageBox.warning(self,self.tr('Password insecure!'), self.tr('Do you want to use the passphrase anyway?'), QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
            if ret == QtGui.QMessageBox.No:
                self.passphrase_0.setText('')
                self.passphrase_1.setText('')
                return False
            else:
                return True
        else:
            return True
        
    def isComplete(self):
        if self.passphrase_0.text() and self.passphrase_1.text() and self.passphrase_0.text() == self.passphrase_1.text():
            if len(self.passphrase_0.text()) <20:
                self.seclevelPixmap.setPixmap(QtGui.QPixmap('./icons/low.png'))
            elif len(self.passphrase_0.text()) >20 and len(self.passphrase_0.text()) <40:
                self.seclevelPixmap.setPixmap(QtGui.QPixmap('./icons/medium.png'))
            else:
                self.seclevelPixmap.setPixmap(QtGui.QPixmap('./icons/high.png'))
            return True
        else:
            self.seclevelPixmap.setPixmap(QtGui.QPixmap('./icons/default.png'))
            return False

class overview(QtGui.QWizardPage):
    def __init__(self):
        QtGui.QWizardPage.__init__(self)
        self.ui = uic.loadUi('./Ui/wizard/overview.ui', self)

        # Setup text and subtext
        self.setTitle(self.tr('Overview:'))
        self.setSubTitle(self.tr('Hint: Check your settings!'))
    
    def initializePage(self):
        if self.field('container').toBool():
            self.FS.setText(self.field('contFsBox').toString())
            self.device.setText(self.field('contPath').toString())
            self.mount.setText(self.field('contMount').toString())
        else:
            self.FS.setText(self.field('partFsBox').toString())
            self.device.setText(self.field('partBox').toString())
            self.mount.setText(self.field('partMount').toString())
        
        if self.mount.text().isEmpty():
            self.mount.setText('/media/luksUUID')
            
        self.cipher.setText(self.field('cipherBox').toString())
