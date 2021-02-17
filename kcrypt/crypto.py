# crypto.py
#
# Copyright (C) 2009  Red Hat, Inc.  All rights reserved.
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
# Author(s): Dave Lehman <dlehman@redhat.com>
#            Martin Sivak <msivak@redhat.com>
#            Fabian Di Milia <info@2blabla.ch>

import os
from pycryptsetup import CryptSetup
from subprocess import *
from os.path import isfile

def askyes(question):
    return True

def dolog(priority, text):
    pass

def askpassphrase(text):
    return None

def is_luks(device):
    cs = CryptSetup(device=device, yesDialog = askyes, logFunc = dolog, passwordDialog = askpassphrase)
    return cs.isLuks()

def luks_uuid(device):
    cs = CryptSetup(device=device, yesDialog = askyes, logFunc = dolog, passwordDialog = askpassphrase)
    return cs.luksUUID()

def luks_format(device,
                passphrase=None,
                cipher=None, key_size=None, key_file=None):
    if not passphrase:
        return False
    
    # Workaround because the new api don't let me override a luks_device, without erase the header
    if is_luks(device) == 0:
        f = open(device, 'wb')
        f.write('\x00\x00\x00\x00' * 120)
        f.close()

    cs = CryptSetup(device=device, yesDialog = askyes, logFunc = dolog, passwordDialog = askpassphrase)

    #None is not considered as default value and pycryptsetup doesn't accept it
    #so we need to filter out all Nones
    kwargs = {}

    # Split cipher designator to cipher name and cipher mode
    cipherType = None
    cipherMode = None
    if cipher:
        cparts = cipher.split("-")
        cipherType = "".join(cparts[0:1])
        cipherMode = "-".join(cparts[1:])
    
    if cipherType: kwargs["cipher"]  = cipherType
    if cipherMode: kwargs["cipherMode"]  = cipherMode
    if   key_size: kwargs["keysize"]  = key_size

    rc = cs.luksFormat(**kwargs)
    if rc:
        return False

    # activate first keyslot
    cs.addKeyByVolumeKey(newPassphrase = passphrase)
    if rc:
        return False
    
def luks_open(device, name, passphrase=None, key_file=None):
    cs = CryptSetup(device=device, yesDialog = askyes, logFunc = dolog, passwordDialog = askpassphrase)
    if passphrase:
        rc = cs.activate(passphrase = passphrase, name = name)
    else:
        key_file = open(key_file, 'r').read()
        rc = cs.activate(passphrase = key_file, name = name)
    
    if rc == 0:
        return True
    elif rc == 1:
        return True
    else:
        return False

def luks_close(name):
    cs = CryptSetup(name=name, yesDialog = askyes, logFunc = dolog, passwordDialog = askpassphrase)
    rc = cs.deactivate()

    if rc:
        return False

def luks_addKey(device,
                 new_passphrase=None,
                 passphrase=None, key_file=None):
    try:
        cs = CryptSetup(device=device, yesDialog = askyes, logFunc = dolog, passwordDialog = askpassphrase)
        cs.addKeyByPassphrase(passphrase, new_passphrase)
        return True
    
    except RuntimeError:
        return False

def luks_removeKey(device,
                   del_passphrase=None,
                   passphrase=None,
                   key_file=None):
    try:
        cs = CryptSetup(device=device, yesDialog = askyes, logFunc = dolog, passwordDialog = askpassphrase)
        cs.removePassphrase(del_passphrase)
        return True
    except RuntimeError:
        return False
    
def luks_status(device):
    cs = CryptSetup(device = device, yesDialog = askyes, logFunc = dolog, passwordDialog = askpassphrase)
    return cs.info()

def luks_header_backup(device, file):
    cmd = Popen(['cryptsetup', 'luksHeaderBackup', device, '--header-backup-file', file], stdout=PIPE, stderr=PIPE).communicate()[1]
    return cmd
    
def luks_header_restore(device, file):
    cmd = Popen(['cryptsetup', 'luksHeaderRestore', device, '--header-backup-file', file], stdout=PIPE, stdin=PIPE, stderr=PIPE).communicate(input='YES')[1]
    return cmd

def luks_dump(device):
    cmd = Popen(['cryptsetup', 'luksDump', device], stdout=PIPE, stderr=PIPE).communicate()[0]
    return cmd

# Workaround for new API, cause pycryptsetup 0.0.14 infos doesn't show the name!
def cryptsetup_status(name):
    try:
        status = Popen(['cryptsetup', 'status', name], stdout=PIPE, stderr=PIPE).communicate()[0].split('\n')[4][11:]
        return status
    except:
        return False
