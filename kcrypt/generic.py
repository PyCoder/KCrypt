# generic.py
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

from crypto import *
from subprocess import *
import string, os, sys, re, ConfigParser

# Check supported filesystems
def supportedFS():
    supported = []
    fs_list = ['ext4', 'ext3', 'ext2', 'xfs', 'jfs', 'btrfs', 'vfat', 'msdos']
    mkfs_list = (os.listdir('/sbin/'), os.listdir('/usr/sbin'))
    for i in fs_list:
        if 'mkfs.' + i in mkfs_list[0] or 'mkfs.' + i in mkfs_list[1]:
            supported.append(i)
    return supported

# Read from ./config/kcrypt.conf
def readConfig(section, option, bool=True):
    config = ConfigParser.RawConfigParser()
    config.read('./config/kcrypt.conf')
    if bool:
        return config.getboolean(section, option)
    else:
        return config.get(section, option)

# Write to ./config/kcrypt.conf
def writeConfig(section, option, value):
    config = ConfigParser.RawConfigParser()
    config.read('./config/kcrypt.conf')
    config.set(section, option, value)
    f = open('./config/kcrypt.conf', 'wb')
    config.write(f)
    f.close()

# Check partitions
def getPartitions():
    device_type = {'IDE':3, 'SCSI':8, 'MD':9}
    partitions = []
    f = open('/proc/partitions' ,'r') 
    device_list = re.findall('(\w{2,})\n', f.read())[1:]
    device_list.sort()
    for device in device_list:
        if os.major(os.lstat('/dev/' + device).st_rdev) in device_type.values():
            partitions.append('/dev/' + device) 
    f.close()
    return partitions

# Check luks partitions
def getLuksPartitions():
    luks = []
    partitions = getPartitions()
    for i in partitions:
        if  is_luks(i) == 0:
            luks.append(i)
    return luks

# Check if Blockdevice
def checkBlockDevice(device):
    info = os.lstat(device)
    if os.major(info.st_rdev) == 7:
        return False
    else:
        return True
    
# Losetup loop-device device
def addLoop(device):
    free = Popen(['losetup', '-f'], stdout=PIPE).communicate()[0][:-1]
    cmd = Popen(['losetup', free, device], stdout=PIPE, stderr=PIPE).communicate()[1]
    return cmd, free
    
# Losetup -d loop-device
def removeLoop(device):
    cmd = Popen(['losetup', '-d', device], stdout=PIPE, stderr=PIPE).communicate()[1]
    return cmd

# Simple mount
def mountDevice(mnt, device, fs):
    cmd = Popen(['mount', '-t', fs, device, mnt], stdout=PIPE, stderr=PIPE).communicate()[1]
    return cmd

# Simple umount
def umountDevice(device):
    cmd = Popen(['umount', device], stdout=PIPE, stderr=PIPE).communicate()[1]
    return cmd
    
# Simple formater
def format(device, fs):
    mkfs = 'mkfs.%s' % fs
    
    if fs == 'jfs' or  fs == 'xfs':
        args = [mkfs,  '-f',  device]
    else: 
        args = [mkfs,  device]
        
    cmd = Popen(args, stdout=PIPE, stderr=PIPE).communicate()[1]
    return cmd

# Inspired by Red Hat's Anaconda-Code (crypto.py) 
def genRandomPasswd(strength, length):
    GENERATED_PASSPHRASE_LENGTH = length

    if strength == 'Low':
        GENERATED_PASSPHRASE_CHARSET = string.letters
    elif strength == 'Medium':
        GENERATED_PASSPHRASE_CHARSET = string.letters + string.digits
    else:
        GENERATED_PASSPHRASE_CHARSET = string.letters + string.digits + string.punctuation
    
    rnd = os.urandom(GENERATED_PASSPHRASE_LENGTH)
    cs = GENERATED_PASSPHRASE_CHARSET
    raw = "".join([cs[ord(c) % len(cs)] for c in rnd])

    return raw

# Simple KeyFile filled with random chars
def genKeyfile(path):
    data = genRandomPasswd(None, 4096)
    f = open(path, 'w')
    f.write(data)
    f.close()
    
# List aviable Language in ./lang and split it    
def availableLanguage():
    aviable_lang = os.listdir('./lang')
    lang_list = {}
    reverse_list = {}
    for lang in aviable_lang:
        lang_list[lang[:-6]] = lang[-5:-3]
        reverse_list[lang[-5:-3]] = lang[:-6]
    return lang_list, reverse_list
