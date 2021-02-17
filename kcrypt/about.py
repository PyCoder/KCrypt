# about.py
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

from PyQt4 import QtGui,  QtCore, uic
from version import version

class showAbout(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi('./Ui/about.ui', self)
        self.label.setPixmap(QtGui.QPixmap('./icons/about-logo.png'))
                
        # Setup Text 
        text = unicode(self.tr('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
                <html><head><meta name="qrichtext" content="1" /><style type="text/css">
                p, li { white-space: pre-wrap; }
                </style></head><body style=" font-family:'MS Shell Dlg 2'; font-size:7.8pt; font-weight:400; font-style:normal;">
                <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style=" font-family:'Sans Serif'; font-size:14pt; font-weight:600;">KCrypt</span></p>
                <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">
                <span style=" font-family:'Sans Serif'; font-size:11pt; font-weight:600;">Version %s</span></p></body></html>''')) % version
        self.textBrowser.setText(text)