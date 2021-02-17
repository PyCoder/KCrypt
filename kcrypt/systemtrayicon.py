# systemtrayicon.py
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

class showSystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self,  parent):
        QtGui.QSystemTrayIcon.__init__(self, parent=None)
        self.parent = parent
        
        self.setIcon(QtGui.QIcon('./icons/icon.png'))
        self.activated.connect(self.iconActivated)
     
        # Setup icon and contextmenu
        label = QtGui.QLabel('<b>KCrypt</b>', parent)
        label.setAlignment(QtCore.Qt.AlignHCenter)
        labelAction = QtGui.QWidgetAction(parent)
        labelAction.setDefaultWidget(label)
    
        restoreAction = QtGui.QAction(self.tr('Restore'), parent)
        restoreAction.triggered.connect(parent.showNormal)
        quitAction = QtGui.QAction(QtGui.QIcon('./icons/exit.png'), self.tr('&Quit       CTRL+X'), self)
        quitAction.triggered.connect(QtGui.qApp.quit)
    
        trayIconMenu = QtGui.QMenu(parent)
        trayIconMenu.addAction(labelAction)
        trayIconMenu.addSeparator()
        trayIconMenu.addAction(restoreAction)
        trayIconMenu.addAction(quitAction)
        
        self.setContextMenu(trayIconMenu)
        
    # Setup icon actions
    def iconActivated(self, reason):
        if reason == QtGui.QSystemTrayIcon.Trigger:
            if self.parent.isVisible():
                self.parent.hide()
            else:
                self.parent.setVisible(True)
