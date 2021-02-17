#!/usr/bin/env python
# -*- coding: utf-8 -*-

# main.py
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

from PyQt4 import QtGui, QtCore
from kcrypt import kcrypt
from generic import readConfig, availableLanguage
import sys


def loadLang():
    default_lang = readConfig('Language','default', False).split('_')[1]
    available_lang = availableLanguage()
    
    kcryptTrans = QtCore.QTranslator()
    qtTrans = QtCore.QTranslator()

    if default_lang:
        if default_lang in available_lang[1].keys():
            kcryptTrans.load(available_lang[1][default_lang] + '_'+ QtCore.QLocale.system().name() + '.qm', './lang') 
            qtTrans.load('qt_' + default_lang, QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath))
            
    return kcryptTrans, qtTrans


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    # Don't close the app if all windows are hidden
    app.setQuitOnLastWindowClosed(False)
    
    # Install translation for KCrypt and Qt Dialogs    
    kcryptTrans = loadLang()
    app.installTranslator(kcryptTrans[0])
    app.installTranslator(kcryptTrans[1])
    
    # Load UTF-8
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
    # Start Kcrypt
    main = kcrypt() 
    main.show() 
    sys.exit(app.exec_())