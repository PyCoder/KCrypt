# language.py
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
from generic import readConfig, writeConfig, availableLanguage

class showLanguage(QtGui.QDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi('./Ui/language.ui', self)
        
        # Fill languageBox with available language in ./lang
        self.languageBox.addItems(availableLanguage()[0].keys())
        
        # Find current language in kcrypt.conf
        current_language = self.languageBox.findText(readConfig('Language','default', False).split('_')[0])
                
        # Set current index to the current language in kcrypt.conf
        if current_language >= 0:
            self.languageBox.setCurrentIndex(current_language)
        
        # Signal and Slots
        self.buttonBox.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.onButtonApply)
        
    def onButtonApply(self):
        selected_language = str(self.languageBox.currentText())
        
        if selected_language == 'English':
            writeConfig('Language', 'default', 'English_en')
        else:
            writeConfig('Language', 'default', selected_language + '_' + availableLanguage()[0][selected_language])
        self.close()