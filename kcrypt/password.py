# password.py
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
from generic import genRandomPasswd

class showPassword(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi('./Ui/password.ui', self)
        
        # Disable ButtonOk
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)
        
        # validator
        self.length.setValidator(QtGui.QIntValidator(0,10000, self))

        # Signals and Slots
        self.buttonBox.accepted.connect(self.genPasswd)
        self.length.textChanged.connect(self.enableButtonOk)

    def enableButtonOk(self):
        if self.length.text() and self.length.text()[0] != '0':
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setEnabled(False)

    def genPasswd(self):
        self.output.clear()

        for i in range(10):
            pwd = genRandomPasswd(str(self.strength.currentText()), int(self.length.text()))
            self.output.appendPlainText(pwd)
        
