# kcrypt.py
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
import re, os, urllib2
from generic import *
from crypto import *
from about import showAbout
from mount import showMount
from wizard import showWizard
from password import showPassword
from erase import showErase
from backup_restore import showBackupRestore
from systemtrayicon import showSystemTrayIcon
from add_del_pass import showAddDelPass
from add_del_key import showAddDelKey
from keyfile import showKeyfile
from language import showLanguage
from version import version, URL

class kcrypt(QtGui.QMainWindow):
    def __init__(self): 
        QtGui.QMainWindow.__init__(self) 
        self.ui = uic.loadUi('./Ui/kcrypt.ui', self)
        
        # Start functions
        self.checkSystemTryIcon()
        self.checkDeleteMountpoint()
        self.checkPermission()
        self.checkUpdate()
        
        # Setup window title
        text = unicode(self.tr('KCrypt %s - A Luks Frontend')) % version
        self.setWindowTitle(text)

        # Signal and Slots 
        self.buttonBox.button(QtGui.QDialogButtonBox.Close).clicked.connect(QtGui.qApp.quit)
       
        # MenuButtons
        self.actionAbout.triggered.connect(self.About)
        self.actionMount.triggered.connect(self.Mount)
        self.actionDismount_Luks_Volume.triggered.connect(self.Dismount)
        self.actionCreate_Random_Password.triggered.connect(self.Password)
        self.actionCreate_New_Luks_Volume.triggered.connect(self.Wizard)
        self.actionSecure_Erase.triggered.connect(self.Erase)
        self.actionBackup_Restore_Header.triggered.connect(self.BackupRestore)
        self.actionChange_Password.triggered.connect(self.AddDelPass)
        self.actionChange_Keyfile.triggered.connect(self.AddDelKey)
        self.actionShow_SystemTrayIcon.triggered.connect(self.toggleSystemTrayIcon)
        self.actionCreate_Random_Keyfile.triggered.connect(self.Keyfile)
        self.actionLanguage.triggered.connect(self.ChangeLanguage)
        self.actionDelete_Mountpoint.triggered.connect(self.toggleDeleteMountPoint)

        # QPushButton and QDialogButtonBox
        self.mountButton.clicked.connect(self.Mount)
        self.dismountButton.clicked.connect(self.Dismount)
        self.createButton.clicked.connect(self.Wizard)

    # Menu entries
    def activateSystemTrayIcon(self, bool = True):
        if readConfig('SystemTrayIcon',  'show'):
            self.systemTrayIcon= showSystemTrayIcon(self)
            self.systemTrayIcon.show()
        else:
            self.actionShow_SystemTrayIcon.setChecked(False)
    
    def toggleSystemTrayIcon(self, bool):
        if bool:
            self.systemTrayIcon= showSystemTrayIcon(self)
            self.systemTrayIcon.show()
        else:
            del self.systemTrayIcon
            
        self.actionShow_SystemTrayIcon.setChecked(bool)
        writeConfig('SystemTrayIcon', 'show', bool)
        writeConfig('CloseEvent', 'minimize',  bool)
    
    def toggleDeleteMountPoint(self, bool):
        if bool:
            writeConfig('Delete Mount Point', 'default', bool)
            self.actionDelete_Mountpoint.setChecked(True)
        else:
            writeConfig('Delete Mount Point', 'default', bool)
            self.actionDelete_Mountpoint.setChecked(False)
            
    def checkPermission(self):
        if os.getuid() != 0:
            self.msg = QtGui.QMessageBox(self)   
            self.msg.setIcon(QtGui.QMessageBox.Information)
            self.msg.setWindowTitle(self.tr('No root permisson!'))
            self.msg.setText(self.tr('Running KCrypt without root permission'))
            self.msg.addButton(QtGui.QMessageBox.Close)
            self.msg.setVisible(True)
        else:
            self.getMapping()
            
    def checkSystemTryIcon(self):
        if QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            self.activateSystemTrayIcon()
        else:
            self.actionShow_SystemTrayIcon.setEnabled(False)
            self.actionShow_SystemTrayIcon.setChecked(False)
            writeConfig('CloseEvent', 'minimize',  'False')
        
    def checkDeleteMountpoint(self):
        if readConfig('Delete Mount Point', 'default', True):
            self.actionDelete_Mountpoint.setChecked(True)
    
    def About(self):
        ab = showAbout()
        ab.exec_()

    def Dismount(self):
        if self.tableWidget.rowCount() != 0 and self.tableWidget.currentRow() != -1:
            name = str(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())
            device = self.tableWidget.item(self.tableWidget.currentRow(), 1).text()
            mountpoint = self.tableWidget.item(self.tableWidget.currentRow(), 2).text()
            
            if checkBlockDevice(device):
                ret = umountDevice(mountpoint)
                #if ret not empty (True)  raise QMessageBox (Error)
                if ret:
                    QtGui.QMessageBox.warning(self, self.tr('Error!'), ret, QtGui.QMessageBox.Close)
                else:
                    luks_close(name)
                    self.tableWidget.removeRow(self.tableWidget.currentRow())
            else:
                ret = umountDevice(mountpoint)
                #if ret not empty (True)  raise QMessageBox (Error)
                if ret:
                    QtGui.QMessageBox.warning(self, self.tr('Error!'), ret, QtGui.QMessageBox.Close)
                else:
                    luks_close(name)
                    removeLoop(device)
                    self.tableWidget.removeRow(self.tableWidget.currentRow())
            
            if readConfig('Delete Mount Point', 'default', True) and os.path.exists(mountpoint):
                os.rmdir(mountpoint)
            elif mountpoint == '/media/' + name and os.path.exists(mountpoint):
                os.rmdir(mountpoint)
        
    def Mount(self):
        mnt = showMount(self.getMapping, self)
        mnt.exec_()

    def Password(self):
        pwd = showPassword(self)
        pwd.exec_()
        
    def Keyfile(self):
        keyfile = showKeyfile(self)
        keyfile.exec_()

    def Wizard(self):
        wiz = showWizard(self.getMapping, None)
        wiz.exec_()
        
    def Erase(self):
        erase = showErase(self)
        erase.exec_()
    
    def BackupRestore(self):
        br = showBackupRestore(self)
        br.exec_()
    
    def AddDelPass(self):
        adp = showAddDelPass(self)
        adp.exec_()
    
    def AddDelKey(self):
        adk = showAddDelKey(self)
        adk.exec_()
        
    def ChangeLanguage(self):
        lang = showLanguage(self)
        lang.exec_()
        
    # reimplementation of closeevent 
    def closeEvent(self, event):
        if readConfig('CloseEvent',  'minimize'):
            self.hide()
            event.ignore()
        else:
            QtGui.qApp.quit()
            
###    Check LUKS Devices for old pycryptsetup <0.0.11
###    def getLuks(self):
###        self.luks_list = []
###        for mapping in self.map_list:
###            self.current_mapping = luks_status(mapping)
###            print self.current_mapping
###            if self.current_mapping >0:
###                if is_luks(self.current_mapping['device']) == 0:
###                    self.getMounts()
###        self.addItems()

    # Workaround for new API, cause pycryptsetup 0.1.4 doesn't show the name
    def getLuks(self):
        self.luks_list = []
        for mapping in self.map_list:
            current_device = cryptsetup_status(mapping)
            if current_device:
                self.current_mapping =luks_status(current_device)
                self.current_mapping['name'] = mapping
                if is_luks(self.current_mapping['device']) == 0:
                    self.getMounts()
                self.addItems()

    def getMapping(self):
        self.map_list = os.listdir('/dev/mapper')
        self.getLuks()
        
    def addItems(self):
        for luks in self.luks_list:
            if self.tableWidget.findItems(luks['name'], QtCore.Qt.MatchExactly): 
                pass
            else:
                self.tableWidget.insertRow(self.tableWidget.rowCount())
                self.tableWidget.setItem(self.tableWidget.rowCount()-1, 0, QtGui.QTableWidgetItem(unicode(luks['name'])))
                self.tableWidget.setItem(self.tableWidget.rowCount()-1, 1, QtGui.QTableWidgetItem(luks['device']))
                self.tableWidget.setItem(self.tableWidget.rowCount()-1, 2, QtGui.QTableWidgetItem(unicode(luks['mount-point'])))
                self.tableWidget.setItem(self.tableWidget.rowCount()-1, 3, QtGui.QTableWidgetItem(luks['cipher']))
                self.tableWidget.setItem(self.tableWidget.rowCount()-1, 4, QtGui.QTableWidgetItem(luks['cipher_mode']))
                self.tableWidget.setItem(self.tableWidget.rowCount()-1, 5, QtGui.QTableWidgetItem(luks['filesystem']))
                        
    def getMounts(self):
        f = open('/etc/mtab', 'r')
        mount_list = re.findall('/dev/mapper/(.*) (/.*?) ([\w]+)', f.read())
        for mount in mount_list:
            if self.current_mapping['name'] in mount:
                self.current_mapping.update({'filesystem' : mount[2], 'mount-point' : mount[1]})
                self.luks_list.append(self.current_mapping)  
        
    def checkUpdate(self):
        try:
            new_version = urllib2.urlopen(URL).read()[:-1]
            if version < new_version:
                QtGui.QMessageBox.information(self, self.tr('Update available!'),
                    unicode(self.tr('''<center><b>KCrypt v%s available!</b><br>Please visit:<br>
                    <a href=http://2blabla.ch> http://2blabla.ch</a></center>''')) % new_version, QtGui.QMessageBox.Close)
        except urllib2.URLError, urllib2.HTTPError:
            pass
