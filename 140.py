'''
Cheese, Lefleur, Tiger, fr. 2012 (c) 
'''
import random
import time
import types
import re
import base64
import binascii
import hashlib
import logging
import json
import psutil
import threading
import sqlite3
import os
import urllib2
import xml.etree.ElementTree as xml
import xml.parsers.expat
import sys
import struct
import math
import platform
import subprocess
import shutil
import socket
import warnings
import smtplib
from subprocess import call
from twisted.internet import reactor, protocol
from datetime import datetime
from datetime import timedelta
#from xgoogle.translate import Translator
#from xgoogle.translate import LanguageDetector, DetectionError
from email.mime.text import MIMEText
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from zope.interface import implements

logging.basicConfig(filename='./server.log',level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

dbcon = sqlite3.connect("./dbfile.sqlite")#, check_same_thread = False)
dbcon.isolation_level = None
dbcur = dbcon.cursor()
dbcon.row_factory = sqlite3.Row
dbcon.text_factory = str

VERBOSE = False
LOGVERB = False
EXEVERS = False
VERSION = "1.40"
SERVERV = "1"
STRERVERV = "1"
TS = True

#LEVEL_LIST = range(0, 121+1) + [1006, 1007, 1015, 1027, 1040, 1062, 1067, 1087, 1088, 1092]
LEVEL_LIST = range(0, 134+1) + range(200, 210+1)
CONJURATION_MAPS = [101, 102, 103, 104, 105, 106, 107]
FULL_LEVEL_LIST = range(0, 127+1) + [-1, 444, 666, 777, 888, 1444, 1666, 1777, 801, 1801] + range(1001, 1127+1)

if EXEVERS:
    VERBOSE = False

class TFMProtocol(protocol.Protocol):

    recvd = ""
    structFormat = "!I"

    def stringReceived(self, string):
        raise NotImplementedError

    def inforequestReceived(self, string):
        raise NotImplementedError

    def dataReceived(self, data):
        if data.startswith("<policy-file-request/>"):
            self.inforequestReceived(data)
            return
        self.recvd += data
        while not self.recvd == "":
            datalength = len(self.recvd)
            if datalength>=4:
                packetlength = int((struct.unpack("%sL" % "!", self.recvd[:4]))[0])
                if datalength == packetlength:
                    self.stringReceived(self.recvd[4:])
                    self.recvd = ""
                elif datalength < packetlength:
                    break
                else:
                    self.stringReceived(self.recvd[4:packetlength])
                    self.recvd = self.recvd[packetlength:]
            else:
                break

    def sendString(self, string):
        if len(string) >= 2 ** (8 * 4):
            raise StringTooLongError(
                "Try to send %s bytes whereas maximum is %s" % (
                len(string), 2 ** (8 * 4)))
        self.transport.write(
            struct.pack(self.structFormat, len(string)) + string)	
	
class TransformiceClientHandler(TFMProtocol):
    def __init__(self):

        self.buffer = ""
        self.MDT = ""
        self.x = None
        self.chatColor = "Non"
        self.y = None
        self.packetSize = ""
        self.packetSizeUTF = ""
        self.eventToken1 = ""
        self.eventToken2 = ""
        self.isUtfPacket = False
        self.currentPacketPos = 0
        self.packetww = []
        self.partialPacketHold = False
        self.isListening = False
        self.validatingVersion = True

        self.loaderInfoUrl = ""
        self.stageloaderInfobytesTotal = "0"
        self.stageloaderInfobytesLoaded = "0"
        self.loaderInfobytesTotal = "0"
        self.loaderInfobytesLoaded = "0"

        self.Langue="ru"
        self.numlanguage = "\x01"
        self.Translating=False
        
        self.country = ""
        self.computer = ""

        self.username = ""
        self.playerCode = -1
        self.privilegeLevel = 0
            #-1 - Invalid
            #0 - Guest
            #1 - Normal
            #3 - Arbitre
            #5 - Moderator
            #6 - Manager
            #10 - Admin
        self.room = None
        self.isHidden = False
        self.isBanned = False
        self.isFrozen = False
        self.isFrozenTimer = None
        self.isShaman = False
        self.isDead = False
        self.forumid = "1"
        self.hasCheese = False
        self.isAfk = True
        self.isSyncroniser = False
        self.score = 0
        self.avatar = 0
        self.fur = '78583a'
        self.shamcolor = '95d9d6'
        self.voteban = []
        self.votemute = 0
        self.mumute = False
        self.modmute= False
        self.TempBan= False
        self.roomname = "1"
        self.roomnamewihout = "1"
        self.lastmessage = ""
        self.isinit = True
        self.sentinelle = False
        self.sentcount = 0
        self.loadercheck = True
        self.logonsuccess = False
        self.wrongPasswordAttempts=0
        self.isIPban = "NotChecked"
        self.isInTribe = False
        self.giftCount = 0
        self.gotGift = 0
        self.titleNumber = 0
        self.Tellfirsttime = 0
        self.disableShop = False
        self.SPEC = False
        self.Voted= False
        self.QualifiedVoter=False
        self.ATEC_Time = None
        self.AWKE_Time = (time.time() * 1000)
        self.playerStartTime = None
        self.REMOTECONTROLPRT= False
        self.NoDataTimer = None
        self.JumpCheck = 1

        self.silence   = False
        self.muteTribe = False
        self.censorChat= False
        self.musicOff  = False
        self.muteChat  = False

        self.EmailAddress = ""
        self.ValidatedEmail = False
        self.LastEmailCode = str(random.randrange(100000000, 999999999+1))
        self.ValidatedPassChange = False

        self.TribeName    = ""
        self.TribeRank    = ""
        self.TribeCode    = ""
        self.TribeInfo    = []
            #m= Modify Greeting Message
            #I= Recruit
            #D= Change Permissions
            #E= Exlude Tribe Members
        self.TribeMessage = ""
        self.TribeFromage = 0
        self.AcceptableInvites = []

        self.RTNail= False
        self.RTotem= False
        self.UTotem= False
        self.STotem= [0,""]
        self.Totem = [0,""]
            #Item Count, Totem (Minus playercode#x#y at the beginning)
            #When summoning totem, Do: PlayerCode#X#Y+self.Totem[1]
            #Totem Editor uses 400, 203 for X/Y
        self.isDrawer = False
        self.isFishing = False
        self.Map777FishingTimer = None

        # old shop list:
        #self.shoplist = "0,3,20;0,5,100;0,2,200;0,4,200;0,1,500;0,6,500;1,1,200;1,2,200;0,7,200;0,8,300;0,9,500;0,10,100;0,11,500;1,4,200;0,12,200;0,13,500;0,14,300;1,3,200;1,5,300;0,15,200;3,1,100;3,2,25;3,3,150;3,4,400;0,16,300;0,17,200;0,18,300;0,19,300;0,20,500;0,21,200;2,1,100;3,5,300;0,22,300;0,23,400;0,24,50;0,25,250;0,26,300;0,27,800;0,28,300;0,29,500;4,1,200;4,2,200;0,30,200;0,31,300;0,32,800;0,33,150;0,34,400;0,35,1000;0,36,500;0,37,200;0,38,800;1,6,800;2,2,50;0,39,200;0,40,500;0,41,800;0,42,500;4,3,200;2,3,20;0,43,200;0,44,250;0,45,300;0,46,100;0,47,1500;1,7,50;2,4,20;3,6,300;3,7,300;4,4,50;1,8,50;0,48,300;0,52,400;2,5,300;0,51,200;0,49,500;3,8,400;0,54,50;0,50,400;0,53,400;3,9,400;1,9,10;4,5,100;2,6,200;0,55,100;4,6,50;3,10,20;0,56,1000;0,57,500;0,58,100;2,7,50;2,8,10;3,11,20;0,59,500;0,60,100;4,7,50;2,9,1000000;0,61,200;0,62,300;1,10,100"
        
        if not TS:
            self.shoplist =  "0,3,20;0,5,100;0,2,200;0,4,200;0,1,500;0,6,500;1,1,200;1,2,200;0,7,200;0,8,300;0,9,500;0,10,100;0,11,500;1,4,200;0,12,200;0,13,500;0,14,300;1,3,200;1,5,300;0,15,200;3,1,100;3,2,25;3,3,150;3,4,400;0,16,300;0,17,200;0,18,300;0,19,300;0,20,500;0,21,200;2,1,100;3,5,300;0,22,300;0,23,400;0,24,50;0,25,250;0,26,300;0,27,800;0,28,300;0,29,500;4,1,200;4,2,200;0,30,200;0,31,300;0,32,800;0,33,150;0,34,400;0,35,1000;0,36,500;0,37,200;0,38,800;1,6,800;2,2,1000000;0,39,1000000;0,40,1000000;0,41,1000000;0,42,1000000;4,3,1000000;2,3,1000000;0,43,200;0,44,250;0,45,300;0,46,100;0,47,1500;1,7,50;2,4,20;3,6,300;3,7,300;4,4,50;1,8,50;0,48,300;0,52,400;2,5,300;0,51,200;0,49,500;3,8,400;0,54,50;0,50,400;0,53,400;3,9,400;1,9,10;4,5,1000000;2,6,500;0,55,100;4,6,50;3,10,20;0,56,1000000;0,57,1000000;0,58,1000000;2,7,1000000;2,8,1000000;3,11,1000000;0,59,1000000;0,60,1000000;4,7,1000000;2,9,1000000;0,61,200;0,62,300;1,10,100;0,63,350;0,64,300;1,11,200;0,68,200;0,69,200;0,70,200;0,71,200;0,72,200;0,73,200;3,12,150;0,65,200;3,13,150;0,66,300;0,67,400;0,74,150;3,14,50;0,77,250;4,8,100;0,78,300;2,10,1000000;0,79,250;1,12,400;0,75,50;0,76,200;4,9,1000000;0,81,1000000;3,15,1000000;0,82,1000000;0,80,1000000;3,16,50;2,12,200;4,10,300;2,11,500;0,85,300;0,84,1000000;4,11,1000000;2,13,400;4,12,1000000;0,86,1000;1,14,1000000;0,88,400;0,87,500;2,14,1000000;1,13,1000000;0,83,100"
        else:
            self.shoplist =  "0,3,20;0,5,100;0,2,200;0,4,200;0,1,500;0,6,500;1,1,200;1,2,200;0,7,200;0,8,300;0,9,500;0,10,100;0,11,500;1,4,200;0,12,200;0,13,500;0,14,300;1,3,200;1,5,300;0,15,200;3,1,100;3,2,25;3,3,150;3,4,400;0,16,300;0,17,200;0,18,300;0,19,300;0,20,500;0,21,200;2,1,100;3,5,300;0,22,300;0,23,400;0,24,50;0,25,250;0,26,300;0,27,800;0,28,300;0,29,500;4,1,200;4,2,200;0,30,200;0,31,300;0,32,800;0,33,150;0,34,400;0,35,1000;0,36,500;0,37,200;0,38,800;1,6,800;2,2,1000000;0,39,1000000;0,40,1000000;0,41,1000000;0,42,1000000;4,3,1000000;2,3,1000000;0,43,200;0,44,250;0,45,300;0,46,100;0,47,1500;1,7,50;2,4,20;3,6,300;3,7,300;4,4,50;1,8,50;0,48,300;0,52,400;2,5,300;0,51,200;0,49,500;3,8,400;0,54,50;0,50,400;0,53,400;3,9,400;1,9,10;4,5,1000000;2,6,500;0,55,100;4,6,50;3,10,20;0,56,1000000;0,57,1000000;0,58,1000000;2,7,1000000;2,8,1000000;3,11,1000000;0,59,1000000;0,60,1000000;4,7,1000000;2,9,1000000;0,61,200;0,62,300;1,10,100;0,63,350;0,64,300;1,11,200;0,68,200;0,69,200;0,70,200;0,71,200;0,72,200;0,73,200;3,12,150;0,65,200;3,13,150;0,66,300;0,67,400;0,74,150;3,14,50;0,77,250;4,8,100;0,78,300;2,10,1000000;0,79,250;1,12,400;0,75,50;0,76,200;4,9,1000000;0,81,1000000;3,15,1000000;0,82,1000000;0,80,1000000;3,16,50;2,12,200;4,10,300;2,11,500;0,85,300;0,84,500;4,11,1000000;2,13,400;4,12,1000000;0,86,1000;1,14,1000000;0,88,400;0,87,500;2,14,1000000;1,13,1000000;0,83,100"
            #self.shoplist =  "0,3,20;0,5,100;0,2,200;0,4,200;0,1,500;0,6,500;1,1,200;1,2,200;0,7,200;0,8,300;0,9,500;0,10,100;0,11,500;1,4,200;0,12,200;0,13,500;0,14,300;1,3,200;1,5,300;0,15,200;3,1,100;3,2,25;3,3,150;3,4,400;0,16,300;0,17,200;0,18,300;0,19,300;0,20,500;0,21,200;2,1,100;3,5,300;0,22,300;0,23,400;0,24,50;0,25,250;0,26,300;0,27,800;0,28,300;0,29,500;4,1,200;4,2,200;0,30,200;0,31,300;0,32,800;0,33,150;0,34,400;0,35,1000;0,36,500;0,37,200;0,38,800;1,6,800;2,2,1000000;0,39,1000000;0,40,1000000;0,41,1000000;0,42,1000000;4,3,1000000;2,3,1000000;0,43,200;0,44,250;0,45,300;0,46,100;0,47,1500;1,7,50;2,4,20;3,6,300;3,7,300;4,4,50;1,8,50;0,48,300;0,52,400;2,5,300;0,51,200;0,49,500;3,8,400;0,54,50;0,50,400;0,53,400;3,9,400;1,9,1000000;4,5,1000000;2,6,1000000;0,55,100;4,6,50;3,10,20;0,56,1000000;0,57,1000000;0,58,1000000;2,7,1000000;2,8,1000000;3,11,1000000;0,59,1000000;0,60,1000000;4,7,1000000;2,9,1000000;0,61,200;0,62,300;1,10,100;0,63,350;0,64,300;1,11,200;0,68,200;0,69,200;0,70,200;0,71,200;0,72,200;0,73,200;3,12,150;0,65,200;3,13,150;0,66,300;0,67,400"
            
            
        # new shop list:  doesn't work :(
        #self.shoplist =  "0,3,20;0,5,100;0,2,200;0,4,200;0,1,500;0,6,500;1,1,200;1,2,200;0,7,200;0,8,300;0,9,500;0,10,100;0,11,500;1,4,200;0,12,200;0,13,500;0,14,300;1,3,200;1,5,300;0,15,200;3,1,100;3,2,25;3,3,150;3,4,400;0,16,300;0,17,200;0,18,300;0,19,300;0,20,500;0,21,200;2,1,100;3,5,300;0,22,300;0,23,400;0,24,50;0,25,250;0,26,300;0,27,800;0,28,300;0,29,500;4,1,200;4,2,200;0,30,200;0,31,300;0,32,800;0,33,150;0,34,400;0,35,1000;0,36,500;0,37,200;0,38,800;1,6,800;2,2,1000000;0,39,1000000;0,40,1000000;0,41,1000000;0,42,1000000;4,3,1000000;2,3,1000000;0,43,200;0,44,250;0,45,300;0,46,100;0,47,1500;1,7,50;2,4,20;3,6,300;3,7,300;4,4,50;1,8,50;0,48,300;0,52,400;2,5,300;0,51,200;0,49,500;3,8,400;0,54,50;0,50,400;0,53,400;3,9,400;1,9,1000000;4,5,1000000;2,6,1000000;0,55,100;4,6,50;3,10,20;0,56,1000000;0,57,1000000;0,58,1000000;2,7,1000000;2,8,1000000;3,11,1000000;0,59,1000000;0,60,1000000;4,7,1000000;2,9,1000000;0,61,200;0,62,300;1,10,100;0,63,350;0,64,300;1,11,200;0,68,200;0,69,200;0,70,200;0,71,200;0,72,200;0,73,200;3,12,150;0,65,200;3,13,150;0,66,300;0,67,400"

        self.cheeseTitleCheckList = [5, 20, 100, 150, 155, 200, 250, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 2000, 2300, 2700, 3200, 3800, 4600, 6000, 7000, 8000, 9001, 10000, 14000, 18000, 22000, 26000, 30000, 34000, 38000, 42000, 46000, 50000, 55000, 60000, 65000, 70000, 75000, 80000]
        self.cheeseTitleDictionary = {5:5, 20:6, 100:7, 150:253, 155:254, 200:8, 250:255, 300:35, 400:36, 500:37, 600:26, 700:27, 800:28, 900:29, 1000:30, 1100:31, 1200:32, 1300:33, 1400:34, 1500:38, 1600:39, 1700:40, 1800:41, 2000:72, 2300:73, 2700:74, 3200:75, 3800:76, 4600:77, 6000:78, 7000:79, 8000:80, 9001:81, 10000:82, 14000:83, 18000:84, 22000:85, 26000:86, 30000:87, 34000:88, 38000:89, 42000:90, 46000:91, 50000:92, 55000:234, 60000:235, 65000:236, 70000:237, 75000:238, 80000:93}
        self.firstTitleCheckList = [1, 10, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200, 3400, 3600, 3800, 4000, 4500, 5000, 5500, 6000, 7000, 8000, 9000, 10000, 12000, 14000, 16000, 18000, 20000, 25000, 30000, 35000, 40000]
        self.firstTitleDictionary = {1:9, 10:10, 100:11, 200:12, 300:42, 400:43, 500:44, 600:45, 700:46, 800:47, 900:48, 1000:49, 1100:50, 1200:51, 1400:52, 1600:53, 1800:54, 2000:55, 2200:56, 2400:57, 2600:58, 2800:59, 3000:60, 3200:61, 3400:62, 3600:63, 3800:64, 4000:65, 4500:66, 5000:67, 5500:68, 6000:69, 7000:231, 8000:232, 9000:233, 10000:70, 12000:224, 14000:225, 16000:226, 18000:227, 20000:202, 25000:228, 30000:229, 35000:230, 40000:71}
        self.shamanTitleCheckList = [10, 100, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000, 15000, 16000, 18000, 20000, 22000, 24000, 26000, 28000, 30000, 35000, 40000, 45000, 50000, 55000, 60000, 65000, 70000, 75000, 80000, 85000, 90000, 100000, 140000]
        self.shamanTitleDictionary = {10:1, 100:2, 1000:3, 2000:4, 3000:13, 4000:14, 5000:15, 6000:16, 7000:17, 8000:18, 9000:19, 10000:20, 11000:21, 12000:22, 13000:23, 14000:24, 15000:25, 16000:94, 18000:95, 20000:96, 22000:97, 24000:98, 26000:99, 28000:100, 30000:101, 35000:102, 40000:103, 45000:104, 50000:105, 55000:106, 60000:107, 65000:108, 70000:109, 75000:110, 80000:111, 85000:112, 90000:113, 100000:114, 140000:115}
        self.shopTitleCheckList = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22]
        self.shopTitleDictionary = {1:115, 2:116, 4:117, 6:118, 8:119, 10:120, 12:121, 14:122, 16:123, 18:124, 20:125, 22:126}
        self.noelGiftTitleCheckList = [5, 10, 40, 60]
        self.noelGiftTitleDictionary = {5:127, 10:128, 40:129, 60:130}
        self.valentinGiftTitleCheckList = [5, 30, 60, 100, 140, 200]
        self.valentinGiftTitleDictionary = {5:210, 30:211, 60:212, 100:249, 140:250, 200:250}
        self.hardShamTitleCheckList = [500, 2000, 4000, 7000, 10000, 14000, 18000, 22000, 26000, 30000, 40000]
        self.hardShamTitleDictionary = {500:213, 2000:214, 4000:215, 7000:216, 10000:217, 14000:218, 18000:219, 22000:220, 26000:221, 30000:222, 40000:223}
        self.place = None
        self.isBot = False
    #def queue(self):
    #    if self.place is None:
    #        print 'none'
    #        self.sendData("\x12" + "\x04", ["10"])
    #        self.place = 5
    #        self.queueTimer = reactor.callLater(3, self.queue)
    #    else:
    #        if self.place == 0:
    #            self.sendData("\x0C" + "\x01", [])#Fixed
    #        else:
    #            self.sendData("\x12" + "\x04", [self.place])
    #            self.place -= 1
    #            self.queueTimer = reactor.callLater(3, self.queue)
    def connectionMade(self):
        if sys.platform.startswith('win'):
          self.address = self.transport.getPeer()
          self.address = [self.address.host]
        else:
          self.address = self.transport.getHandle().getpeername()

        print self.address
        print "Connected: "+str(self.address[0])+"."
        

        self.server = self.factory
        
        #Calling Queue
        #if self.server.getConnectedPlayerCount()>1:
        #    self.queueTimer = reactor.callLater(2, self.queue)
            
        if self.server.getConnectedPlayerCount()>430:
            self.transport.loseConnection()

        self.validatingLoader = self.server.ValidateLoader

        if VERBOSE:
            print "Connected. IP: "+self.address[0]+". Check Client? "+str(self.validatingLoader)
        self.NoDataTimer = reactor.callLater(2, self.transport.loseConnection)

        self.SGMDT = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        LCDMT = str(self.server.LCDMT)
        self.CMDTEC = random.randrange(1000, 9999)
        self.ICMDTEC = self.CMDTEC
        i = 0
        while(i < 10):
            self.CMDT = LCDMT[i]
            if self.CMDT == "0":
                self.SGMDT[i] = "10"
            else:
                self.SGMDT[i] = self.CMDT
            i = (i+1)

    def inforequestReceived(self, data):

        #self.server = self.factory
        #print self.factory

        #self.connectionMade()

        if self.NoDataTimer:
            try:
                self.NoDataTimer.cancel()
            except:
                self.NoDataTimer=None
        #print "RECV: "+repr(data)
        if LOGVERB:
            logging.warning("RECV: "+repr(data))
        if self.isBanned:
            data=""
            self.transport.loseConnection()
        self.buffer += data
        if self.buffer=="<policy-file-request/>\x00":
            if False: #self.server.getIPPermaBan(self.address):
                self.transport.loseConnection()
                self.isIPban = True
                self.isBanned = True
                data=""
            elif False: #self.address[0] in self.server.tempIPBanList:
                self.transport.loseConnection()
                self.isIPban = True
                self.isBanned = True
                data=""
            else:
                self.isIPban = False
                self.transport.write("<cross-domain-policy><allow-access-from domain=\"*\" to-ports=\"*\" /></cross-domain-policy>\x00")
                #self.transport.write(r"""<cross-domain-policy><allow-access-from domain="%s" to-ports="%s" /></cross-domain-policy>""" % (self.server.POLICY, self.server.PORT) + "\x00")
                self.transport.loseConnection()
        elif self.buffer=="TestFFF\x00":
            print 'Тест.'
            self.sentinelleSendStat(True)
        elif self.buffer=="SuperBelette\x00":
            #print 'Noisette being accessed: '+self.address[0]
            if self.server.getIPPermaBan(self.address[0]):
                self.transport.loseConnection()
                self.isIPban = True
                self.isBanned = True
                data=""
            elif self.address[0] in self.server.tempIPBanList:
                self.transport.loseConnection()
                self.isIPban = True
                self.isBanned = True
                data=""
            else:
                self.isIPban = False
                self.isinit = False
                self.sentinelle = True
                self.sentinelleSendStat()
                self.sentinelleSendCPU()
        elif self.buffer.startswith("PlayerStat-"):
            username=self.buffer[11:].replace("\x00","").lower().capitalize()
            if len(username)<3 or len(username)>12:
                self.transport.loseConnection()
            elif not username.isalpha():
                self.transport.loseConnection()
          #  elif username == "Server":
          #      self.sendDataOld("\x04", [SERVERV, VERSION, str(datetime.today()-self.server.STARTTIME).split(".")[0], str(self.server.getConnectedPlayerCount())])
          #      self.transport.loseConnection()
            elif self.server.checkExistingUsers(username):
                name = username
                tribe = self.server.getTribeName(username)
                rounds = self.server.getRoundsCount(username)
                cheese = self.server.getCheeseCount(username)
                first = self.server.getFirstCount(username)
                chamansave = self.server.getSavesCount(username)
                chamancheese = self.server.getShamanCheeseCount(username)
                chamangold = self.server.getShamanGoldSavesCount(username)
                micetitle = self.server.getCurrentTitle(username)
                self.sendDataOld("\x05", [name, tribe, rounds, cheese, first, chamansave, chamancheese, chamangold, micetitle])
                self.transport.loseConnection()
            else:
                self.transport.loseConnection()
        elif self.buffer.startswith("RPCC\x01"):
            self.transport.loseConnection()
        else:
            if self.sentinelle:
                self.parseSentinelle(self.buffer)
            else:
                logging.error(repr(data)+" [272] "+self.address[0])
                print repr(data) #huh?
                
    def parseSentinelle(self, data):
        #print repr(data)
        pass

    def sentinelleSendStat(self,other=False):
        if not other:
            if not self.sentcount>1200:
                #print 'called sentinelleSendStat'
                usedram=psutil.avail_phymem()
                totalram=psutil.TOTAL_PHYMEM
                usedram = usedram / 1048576
                totalram = totalram / 1048576
                usedram = totalram-usedram
                usedram = '%.1f' % usedram
                totalram = '%.1f' % totalram
                self.sendDataOld("\x05", self.server.PlayerCountHistory+["\x00\x04", str(usedram)+"/"+str(totalram), "formice.ru - "+self.server.getServerSetting("version"), str(self.server.getConnectedPlayerCount())])
                self.sentinelleSendStatTimer = reactor.callLater(10, self.sentinelleSendStat)
        else:
            if not self.sentcount>1200:
                #print 'called sentinelleSendStat'
                usedram=psutil.avail_phymem()
                totalram=psutil.TOTAL_PHYMEM
                usedram = usedram / 1048576
                totalram = totalram / 1048576
                usedram = totalram-usedram
                usedram = '%.1f' % usedram
                totalram = '%.1f' % totalram
                self.sendDataOld("\x05", self.server.PlayerCountHistory+["\x00\x04", str(usedram)+"/"+str(totalram), "Test1<br>Test2<br>Test3", str(self.server.getConnectedPlayerCount())])
                self.sentinelleSendStatTimer = reactor.callLater(10, self.sentinelleSendStat)

    def sentinelleSendCPU(self):
        #print 'Called sentinelleSendCPU'
        #600 for 1s cpu counts for 10 minutes.
        #2400 for 0.2 cpu counts for 10 minutes.
        #1200 for 0.2 cpu counts for 5 minutes.
        #600 for 0.2 cpu counts for 2.5 minutes.
        #Have interval and callLater be the same numbers.
        self.sentcount=self.sentcount+1
        #print 'SentCount: '+str(self.sentcount)
        if self.sentcount>1200:
            self.transport.loseConnection()
            if self.sentinelleSendCPUTimer:
                try:
                    self.sentinelleSendCPUTimer.cancel()
                except:
                    self.sentinelleSendCPUTimer=None
            if self.sentinelleSendStatTimer:
                try:
                    self.sentinelleSendStatTimer.cancel()
                except:
                    self.sentinelleSendStatTimer=None
        else:
            cpu=str(math.floor(psutil.cpu_percent(interval=0.3))).replace(".0","")
            self.sendDataOld("\x06", [cpu])
            self.sentinelleSendCPUTimer = reactor.callLater(0.3, self.sentinelleSendCPU)
            #self.sentinelleSendCPU()

    def stringReceived(self, packet):

        if self.NoDataTimer:
            try:
                self.NoDataTimer.cancel()
            except:
                self.NoDataTimer=None
        #print repr(packet)
        Size = 0#len(packet)
        MDT = packet[:4]
        data = packet[4:]
        if self.isBanned:
            data=""
            self.transport.loseConnection()
        else:
            self.found_terminator(MDT, data, Size)

    def found_terminator(self, MDT, data, Size):
        #self.server = self.factory

        if self.validatingVersion:
            if self.server.getIPPermaBan(self.address[0]):
                self.transport.loseConnection()
                self.isIPban = True
                self.isBanned = True
                data=""
            elif self.address[0] in self.server.tempIPBanList:
                self.transport.loseConnection()
                self.isIPban = True
                self.isBanned = True
                data=""
            else:
                self.isIPban = False
            if VERBOSE:
                print "RECV: "+repr(data)
            if LOGVERB:
                logging.warning("RECV: "+repr(data))
            if data.startswith("\x1c\x01"):
                version = data[2:]
                print repr(version)
                #version = "0."+str(struct.unpack('!h', version)[0])
                if self.isinit:
                    if self.server.GetCapabilities:
                        secFile = open("./Capabilities.swf", "rb")
                        self.validatingLoader = True
                    elif self.validatingLoader:
                        secFile = open("./Kikoo.swf", "rb")
                    else:
                        secFile = open("./Kikoo.swf", "rb")
                    secData = secFile.read()
                    secFile.close()
                    secB64=base64.b64encode(secData)
                    self.sendData("\x1A" + "\x16", [secB64])
                    self.isinit = False
                if self.server.ValidateVersion:
                    if version == VERSION:
                        self.sendCorrectVersion()
                        self.AwakeTimerKickTimer = reactor.callLater(600, self.AwakeTimerKick)
                    else:
                        self.transport.loseConnection()
                else:
                    self.sendCorrectVersion()
                    self.AwakeTimerKickTimer = reactor.callLater(600, self.AwakeTimerKick)
                self.validatingVersion = False
            else:
                logging.error(repr(data))
                self.transport.loseConnection()
        else:
            self.parseData(data, MDT, Size)

    def parseData(self, data, MDT, Size):
        Pos = int((self.CMDTEC)%9000 + 1000)
        d1 = int(Pos / 1000)
        d2 = int(Pos / 100) % 10
        d3 = int(Pos / 10) % 10
        d4 = int(Pos % 10)
        SMDT = chr(int(self.SGMDT[d1])) + chr(int(self.SGMDT[d2])) + chr(int(self.SGMDT[d3])) + chr(int(self.SGMDT[d4]))
        self.CMDTEC += 1
        if self.CMDTEC==self.ICMDTEC+9000:
            self.CMDTEC=self.ICMDTEC
        if str(MDT)!=str(SMDT):
            #if self.room:
            #    self.sendPlayerDisconnect(self.playerCode)
            #    self.room.removeClient(self)
            #self.sendModMessageChannel("Serveur", "Unexpected packet from "+str(self.address[0]))
            #data=""
            #self.transport.loseConnection()
            pass
        if self.validatingLoader:
            data=data[2:]
            data=str(data[2:struct.unpack('!h', data[:2])[0]+2]).split("\x01")
            if self.server.GetCapabilities:
                if len(data)==33:
                    self.loaderInfoUrl, self.stageloaderInfobytesTotal, self.stageloaderInfobytesLoaded, self.loaderInfobytesTotal, self.loaderInfobytesLoaded, avHardwareDisable, hasAccessibility, hasAudio, hasAudioEncoder, hasEmbeddedVideo, hasIME, hasMP3, hasM3U, hasPrinting, hasScreenBroadcast, hasScreenPlayback, hasStreamingAudio, hasStreamingVideo, hasTLS, hasVideoEncoder, isDebugger, isEmbeddedInAcrobat, language, localFileReadDisable, manufacturer, clientos, pixelAspectRatio, playerType, screenColor, screenDPI, screenResolutionX, screenResolutionY, serverString, flashversion = data
                    if not re.search(self.server.LoaderURL, self.loaderInfoUrl):
                        self.sendModMessageChannel("Serveur", str(self.address[0])+" идёт загрузка с: "+self.server.LoaderURL+".")
                    if str(self.stageloaderInfobytesTotal)!=str(self.server.LoaderSize):
                        if str(self.stageloaderInfobytesTotal)!=str(self.server.ModLoaderSize):
                            self.sendModMessageChannel("Serveur", str(self.address[0])+" неправильный загрузчик клиента.")
                    if str(self.loaderInfobytesTotal)!=str(self.server.ClientSize):
                        self.sendModMessageChannel("Serveur", str(self.address[0])+" неправильный клиент.")
                    if self.stageloaderInfobytesTotal!=self.stageloaderInfobytesLoaded:
                        self.sendModMessageChannel("Serveur", str(self.address[0])+" загрузчик не полностью загружен... ")
                    if self.loaderInfobytesTotal!=self.loaderInfobytesLoaded:
                        self.sendModMessageChannel("Serveur", str(self.address[0])+" клиент не полностью загружен...")
                    data=""
                    self.validatingLoader = False
                else:
                    self.sendModMessageChannel("Serveur", str(self.address[0])+" приняты неверные данные клиента.")
                    self.server.tempBanIPExact(self.address[0], 120)
                    data=""
                    self.isBanned=True
                    self.transport.loseConnection()
            else:
                if len(data)==5:
                    self.loaderInfoUrl, self.stageloaderInfobytesTotal, self.stageloaderInfobytesLoaded, self.loaderInfobytesTotal, self.loaderInfobytesLoaded = data
                    if not re.search(self.server.LoaderURL, self.loaderInfoUrl):
                        self.sendModMessageChannel("Serveur", str(self.address[0])+" загружает с "+self.server.LoaderURL+".")
                    if str(self.stageloaderInfobytesTotal)!=str(self.server.LoaderSize):
                        if str(self.stageloaderInfobytesTotal)!=str(self.server.ModLoaderSize):
                            self.sendModMessageChannel("Serveur", str(self.address[0])+"'s неправильный загрузчик клиента.")
                    if str(self.loaderInfobytesTotal)!=str(self.server.ClientSize):
                        self.sendModMessageChannel("Serveur", str(self.address[0])+"'s неправильный клиент.")
                    if self.stageloaderInfobytesTotal!=self.stageloaderInfobytesLoaded:
                        self.sendModMessageChannel("Serveur", str(self.address[0])+"'s загрузчик не полностью загружен?")
                    if self.loaderInfobytesTotal!=self.loaderInfobytesLoaded:
                        self.sendModMessageChannel("Serveur", str(self.address[0])+"'s клиент не полностью загружен?")
                    data=""
                    self.validatingLoader = False
                else:
                    self.sendModMessageChannel("Serveur", str(self.address[0])+" отправил неверные данные клиента.")
                    self.server.tempBanIPExact(self.address[0], 120)
                    data=""
                    self.isBanned=True
                    self.transport.loseConnection()

        if self.isFrozen:
            eventTokens=data[:2]
            data=data[2:]
            eventToken1, eventToken2 = eventTokens
            if eventToken1 == "\x01" and eventToken2 == "\x01":
                Check=str(data[2:struct.unpack('!h', data[:2])[0]+2]).split("\x01").pop(0)
                if Check=="\x1A\x1A":
                    self.parseDataUTF(data[2:struct.unpack('!h', data[:2])[0]+2])
                elif Check=="\x1A\x02":
                    self.parseDataUTF(data[2:struct.unpack('!h', data[:2])[0]+2])
                else:
                    pass
            data=""

        if data=="":
            pass
        else:
            eventTokens=data[:2]
            data=data[2:]
            eventToken1, eventToken2 = eventTokens
            if VERBOSE:
                print "RECV:", repr(eventToken1+eventToken2), repr(data)
            if LOGVERB:
                logging.warning("RECV: "+repr(eventToken1+eventToken2)+" "+repr(data))
            if eventToken1 == "\x01":
                if eventToken2 == "\x01":
                    self.parseDataUTF(data[2:struct.unpack('!h', data[:2])[0]+2])
            elif eventToken1 == "\x14":
                if eventToken2 == "\x0F":
                    #new shop
                    self.sendData("\x06" + "\x14",["Используйте /setlook. Это временно."])
                    #spefrom = "\x00\x0c\xcb" # => Nb fromage (0)
                    spefrom = struct.pack("!l", int(self.shopcheese))
                    spefraises = struct.pack("!l", int(self.fraises))
                    speactual = "\x00\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00\x06\x00\x07\x01\x92\x00\x08\x01\x93\x01\x91\x01\x96\x00\x0d\x01\x94\x01\x95\x00\x0f\x00\x13\x00\x15\x00\x17\x00\x18\x00\x1b\x00\x1d\x00\x1e\x01\x31\x01\x30\x00\x23\x01\x33\x00\x20\x01\x32\x00\x21\x00\x27\x00\x24\x01\x37\x01\x36\x00\x2a\x00\x2b\x00\x28\x01\x3a\x00\x29\x00\x2e\x00\x2d\x00\x31\x00\x37\x00\x39\x00\x38\x00\x3d\x01\x2e\x00\x44\x00\xcd\x00\xcc\x00\x45\x00\xce\x00\xc9\x00\xcb\x00\xca\x00\xd0\x00\xd1\x00\x66\x00\x65\x00\x6e\x00\x6c\x00\x6d\x00\x6b\x00\x69\x00\x00\x00\x99" #items possedés
                    spelook = "\x30\x2C\x30\x2C\x30\x2C\x30\x2C\x30" #\x32\x3b => Affichage direct car skin
                    speshop = "\x08\x14"+spefrom+""+spefraises+"\x00\x09"+spelook+"\x00\x00\x00\x40"+speactual+"\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x00\x05\x00\x00\x00\x64\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01\xF4\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x01\xF4\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\xC8\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x07\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x09\x00\x00\x01\xF4\x00\x00\x00\x00\x00\x00\x00\x0A\x00\x00\x00\x64\x00\x00\x00\x00\x00\x00\x00\x0B\x00\x00\x01\xF4\x00\x00\x00\x01\x00\x00\x00\x04\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x0C\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x0D\x00\x00\x01\xF4\x00\x00\x00\x00\x00\x00\x00\x0E\x00\x00\x01\x2C\x00\x00\x00\x01\x00\x00\x00\x03\x00\x00\x00\xC8\x00\x00\x00\x01\x00\x00\x00\x05\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x0F\x00\x00\x00\xC8\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x64\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x19\x00\x00\x00\x03\x00\x00\x00\x03\x00\x00\x00\x96\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x01\x90\x00\x00\x00\x00\x00\x00\x00\x10\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x11\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x12\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x13\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x01\xF4\x00\x00\x00\x00\x00\x00\x00\x15\x00\x00\x00\xC8\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x64\x00\x00\x00\x03\x00\x00\x00\x05\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x16\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x17\x00\x00\x01\x90\x00\x00\x00\x00\x00\x00\x00\x18\x00\x00\x00\x32\x00\x00\x00\x00\x00\x00\x00\x19\x00\x00\x00\xFA\x00\x00\x00\x00\x00\x00\x00\x1A\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x1B\x00\x00\x03\x20\x00\x00\x00\x00\x00\x00\x00\x1C\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x1D\x00\x00\x01\xF4\x00\x00\x00\x04\x00\x00\x00\x01\x00\x00\x00\xC8\x00\x00\x00\x04\x00\x00\x00\x02\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x1E\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x1F\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x20\x00\x00\x03\x20\x00\x00\x00\x00\x00\x00\x00\x21\x00\x00\x00\x96\x00\x00\x00\x00\x00\x00\x00\x22\x00\x00\x01\x90\x00\x00\x00\x00\x00\x00\x00\x23\x00\x00\x03\xE8\x00\x00\x00\x00\x00\x00\x00\x24\x00\x00\x01\xF4\x00\x00\x00\x00\x00\x00\x00\x25\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x26\x00\x00\x03\x20\x00\x00\x00\x01\x00\x00\x00\x06\x00\x00\x03\x20\x00\x00\x00\x00\x00\x00\x00\x29\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x2A\x00\x0F\x42\x40\x00\x00\x00\x04\x00\x00\x00\x03\x00\x0F\x42\x40\x00\x00\x00\x02\x00\x00\x00\x03\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x2B\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x2C\x00\x00\x00\xFA\x00\x00\x00\x00\x00\x00\x00\x2D\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x2E\x00\x00\x00\x64\x00\x00\x00\x00\x00\x00\x00\x2F\x00\x00\x05\xDC\x00\x00\x00\x01\x00\x00\x00\x07\x00\x00\x00\x32\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00\x14\x00\x00\x00\x03\x00\x00\x00\x06\x00\x00\x01\x2C\x00\x00\x00\x03\x00\x00\x00\x07\x00\x00\x01\x2C\x00\x00\x00\x04\x00\x00\x00\x04\x00\x00\x00\x32\x00\x00\x00\x01\x00\x00\x00\x08\x00\x00\x00\x32\x00\x00\x00\x00\x00\x00\x00\x30\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x34\x00\x00\x01\x90\x00\x00\x00\x02\x00\x00\x00\x05\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x33\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x31\x00\x00\x01\xF4\x00\x00\x00\x03\x00\x00\x00\x08\x00\x00\x01\x90\x00\x00\x00\x00\x00\x00\x00\x36\x00\x00\x00\x32\x00\x00\x00\x00\x00\x00\x00\x32\x00\x00\x01\x90\x00\x00\x00\x00\x00\x00\x00\x35\x00\x00\x01\x90\x00\x00\x00\x03\x00\x00\x00\x09\x00\x00\x01\x90\x00\x00\x00\x00\x00\x00\x00\x37\x00\x00\x00\x64\x00\x00\x00\x04\x00\x00\x00\x06\x00\x00\x00\x32\x00\x00\x00\x03\x00\x00\x00\x0A\x00\x00\x00\x14\x00\x00\x00\x02\x00\x00\x00\x09\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x3D\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x3E\x00\x00\x01\x2C\x00\x00\x00\x01\x00\x00\x00\x0A\x00\x00\x00\x64\x00\x00\x00\x00\x00\x00\x00\x3F\x00\x00\x01\x5E\x00\x00\x00\x00\x00\x00\x00\x40\x00\x00\x01\x2C\x00\x00\x00\x01\x00\x00\x00\x0B\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x44\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x45\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x46\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x47\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x48\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x49\x00\x00\x00\xC8\x00\x00\x00\x03\x00\x00\x00\x0C\x00\x00\x00\x96\x00\x00\x00\x00\x00\x00\x00\x41\x00\x00\x00\xC8\x00\x00\x00\x03\x00\x00\x00\x0D\x00\x00\x00\x96\x00\x00\x00\x00\x00\x00\x00\x42\x00\x00\x01\x2C\x00\x00\x00\x00\x00\x00\x00\x43\x00\x00\x01\x90\x00\x00\x00\x00\x00\x00\x00\x4A\x00\x00\x00\x96\x00\x00\x00\x03\x00\x00\x00\x0E\x00\x00\x00\x32\x00\x00\x00\x00\x00\x00\x00\x4D\x00\x00\x00\xFA\x00\x00\x00\x04\x00\x00\x00\x08\x00\x00\x00\x64\x00\x00\x00\x00\x00\x00\x00\x4E\x00\x00\x01\x2C\x00\x00\x00\x02\x00\x00\x00\x0A\x00\x00\x0F\xA1\x00\x00\x00\x00\x00\x00\x00\x4F\x00\x00\x00\xFA\x00\x00\x00\x01\x00\x00\x00\x0C\x00\x00\x01\x90\x00\x00\x00\x00\x00\x00\x00\x4B\x00\x00\x00\x32\x00\x00\x00\x00\x00\x00\x00\x4C\x00\x00\x00\xC8\x00\x00\x00\x02\x00\x00\x00\x02\x00\x0F\x42\x40\x00\x00\x00\x04\x00\x00\x00\x09\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x27\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x51\x00\x0F\x42\x40\x00\x00\x00\x03\x00\x00\x00\x0F\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x52\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x50\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x28\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x53\x00\x0F\x42\x40\x00\x00\x00\x03\x00\x00\x00\x10\x00\x0F\x42\x40\x00\x00\x00\x02\x00\x00\x00\x0C\x00\x0F\x42\x40\x00\x00\x00\x04\x00\x00\x00\x0A\x00\x0F\x42\x40\x00\x00\x00\x02\x00\x00\x00\x0B\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x55\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x54\x00\x0F\x42\x40\x00\x00\x00\x01\x00\x00\x00\x0D\x00\x0F\x42\x41\x00\x00\x00\x01\x00\x00\x00\x09\x00\x0F\x42\x40\x00\x00\x00\x04\x00\x00\x00\x05\x00\x0F\x42\x40\x00\x00\x00\x02\x00\x00\x00\x06\x00\x0F\x42\x40\x00\x00\x00\x04\x00\x00\x00\x0B\x00\x0F\x42\x40\x00\x00\x00\x02\x00\x00\x00\x0D\x00\x0F\x42\x40\x00\x00\x00\x04\x00\x00\x00\x0C\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x56\x00\x00\x03\xE8\x00\x00\x00\x02\x00\x00\x00\x0F\x00\x00\x02\x58\x00\x00\x00\x02\x00\x00\x00\x0E\x00\x00\x00\xC8\x00\x00\x00\x00\x00\x00\x00\x58\x00\x0F\x42\x40\x00\x00\x00\x01\x00\x00\x00\x0E\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x57\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x38\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x39\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x3A\x00\x0F\x42\x40\x00\x00\x00\x02\x00\x00\x00\x07\x00\x0F\x42\x40\x00\x00\x00\x02\x00\x00\x00\x08\x00\x0F\x42\x40\x00\x00\x00\x03\x00\x00\x00\x0B\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x59\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x5B\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x5A\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x5D\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x5C\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x3B\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x3C\x00\x0F\x42\x40\x00\x00\x00\x04\x00\x00\x00\x07\x00\x0F\x42\x40\x00\x00\x00\x03\x00\x00\x00\x11\x00\x0F\x42\x40\x00\x00\x00\x02\x00\x00\x00\x10\x00\x0F\x42\x40\x00\x00\x00\x00\x00\x00\x00\x5F\x00\x00\x00\x64"
                    self.sendSpeData(speshop)
                elif eventToken2 == "\x12":
                    print "Equiper : "+repr(data)
                    itemcategory, item = struct.unpack('!BB', data)
                    #if self.checkInShop(values[0]):
                    
                    looklist = self.look.split(",")
                    if itemcategory==0:
                        looklist[0]=str(item)
                        self.look=json.dumps(looklist)
                        self.look = self.look.strip('[]')
                        self.look = self.look.replace("\"","")
                        self.look = self.look.replace(" ","")
                        self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                    if itemcategory==1:
                        looklist[1]=str(item)
                        self.look=json.dumps(looklist)
                        self.look = self.look.strip('[]')
                        self.look = self.look.replace("\"","")
                        self.look = self.look.replace(" ","")
                        self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                    if itemcategory==2:
                        looklist[2]=str(item)
                        self.look=json.dumps(looklist)
                        self.look = self.look.strip('[]')
                        self.look = self.look.replace("\"","")
                        self.look = self.look.replace(" ","")
                        self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                    if itemcategory==3:
                        looklist[3]=str(item)
                        self.look=json.dumps(looklist)
                        self.look = self.look.strip('[]')
                        self.look = self.look.replace("\"","")
                        self.look = self.look.replace(" ","")
                        self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                    if itemcategory==4:
                        looklist[4]=str(item)
                        self.look=json.dumps(looklist)
                        self.look = self.look.strip('[]')
                        self.look = self.look.replace("\"","")
                        self.look = self.look.replace(" ","")
                        self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                    
                    
                else:
                    logging.warning("Unimplemented Binary %r" % eventTokens)
                    print "Unimplemented Error: Bin-"+repr(eventTokens)+"-DATA:"+repr(data)
            elif eventToken1 == "\x04":
                if eventToken2 == "\x02":
                    #Particule
                    ##particule, posX, posY, nombre, vitesse, gravite, accelerationY=struct.unpack('!bhhbb?h', data)
                    ##data=struct.pack('!bhhbb?h', particule, posX, posY, nombre, vitesse, gravite, accelerationY)
                    if self.isSyncroniser:
                        self.room.sendAllBin(eventTokens, data)
                elif eventToken2 == "\x10":
                    #Snowball
                    utflength=struct.unpack('!h', data[:2])[0]
                    x=data[2:utflenght+2]
                    
                    if direction == "1":
                        self.room.sendAll("\x05" + "\x14"+struct.pack('!h', 34)+struct.pack('!h', int(x))+struct.pack('!h', int(y))+struct.pack('!h', 0)+"\x0A\xFC\x01")
                    if direction == "0":
                        self.room.sendAll("\x05" + "\x14"+struct.pack('!h', 34)+struct.pack('!h', int(x))+struct.pack('!h', int(y))+struct.pack('!h', 0)+"\xF6\xFC\x01")
                elif eventToken2 == "\x03":
                    #MajPositionMobile
                    if not self.room.CheckedPhysics:
                        codePartie=struct.unpack('!i', data[:4])[0]

                    #Not needed, but w/e:
                    ##codePartie=struct.unpack('!i', data[:4])[0]
                    ##x=4
                    ##while x<len(data):
                    ##    codeMobile=struct.unpack("!h", data[x:x+2])[0]
                    ##    if codeMobile == -1:
                    ##        x+=2
                    ##    else:
                    ##        codeMobile, posX, posY, vX, vY, angle, vAngle, dur, sleep = struct.unpack("!hhhhhhh??", data[x:x+16])
                    ##        x+=16

                    if not self.room.CheckedPhysics:
                        self.room.CheckedPhysics=True
                        if self.isSyncroniser and codePartie == self.room.CodePartieEnCours:
                            self.room.sendAllBin(eventTokens, data)
                    else:
                        if self.isSyncroniser:
                            self.room.sendAllBin(eventTokens, data)
                elif eventToken2 == "\x04":
                    #MajPositionJoueur
                    if len(data)==21:
                       codePartie, droiteEnCours, gaucheEnCours, posX, posY, vX, xY, saute, imageSaut, codeTP, angle, vitesseAngle = struct.unpack('!i??hhhh?bbhh', data)
                    elif len(data)==17:
                       codePartie, droiteEnCours, gaucheEnCours, posX, posY, vX, xY, saute, imageSaut, codeTP = struct.unpack('!i??hhhh?bb', data)
                    else:
                       pass
                    self.PosX = posX
                    self.PosY = posY
                    
                    if self.room.ISCMdata[2] == 5567: #Si map halloween
                        if posX >= 2874 and posX <= 3549 and posY >= 620 and posX >= 400:
                            self.sendZombieMode(true)
                    
                    if self.isZombie: #Si le joueur est un zombie
                        
                        speX = self.PosX + 30
                        speY = self.PosY + 30
                        speeX = self.PosX - 30
                        speeY = self.PosY - 30
                        
                        for playerCode, client in self.room.clients.items():
                            if client.username == self.username:
                                pass
                            elif client.isZombie:
                                pass
                            elif client.PosX >= speeX and client.PosX <= speX and client.PosY >= speeY and client.PosY <= speY:
                                client.sendZombieMode()
                                
                    elif self.room.ZombieRoom: #Si le salon contient des zombies
                        
                        speX = self.PosX + 30
                        speY = self.PosY + 30
                        speeX = self.PosX - 30
                        speeY = self.PosY - 30
                        
                        for playerCode, client in self.room.clients.items():
                            if client.username == self.username:
                                pass
                                
                            elif client.isZombie:
                                if client.PosX >= speeX and client.PosX <= speX and client.PosY >= speeY and client.PosY <= speY:
                                    self.sendZombieMode()
                                    
                    codePartie = struct.unpack('!i', data[:4])[0]
                    data=data+struct.pack("!l", int(self.playerCode))
                    if self.isFishing:
                        self.isFishing=False
                    if int(codePartie) == int(self.room.CodePartieEnCours):
                        self.room.sendAllBin(eventTokens, data)
                elif eventToken2 == "\x05":
                    #Mort
                    CodePartieEnCours = struct.unpack('!i', data[:4])[0]
                    if CodePartieEnCours == self.room.CodePartieEnCours:
                        self.isDead = True
                        self.score -= 1
                        if self.score < 0:
                            self.score = 0
                        self.sendPlayerDied(self.playerCode, self.score)
                        self.room.checkShouldChangeWorld()
                else:
                    logging.warning("Unimplemented Binary %r" % eventTokens)
                    print "Unimplemented Error: Bin-"+repr(eventTokens)+"-DATA:"+repr(data)
                
            elif eventToken1 == "\x05":
                if eventToken2 == "\x14":
                    #PlacementObjet
                    if self.room.isTotemEditeur:
                        if self.room.identifiantTemporaire == -1:
                            self.room.identifiantTemporaire = 0
                        if not self.room.identifiantTemporaire > 20:
                            self.room.identifiantTemporaire+=1
                            self.sendTotemItemCount(self.room.identifiantTemporaire)
                            code, px, py, angle, vx, vy, dur=struct.unpack('!hhhhbbb', data)
                            self.Totem[0]=self.room.identifiantTemporaire
                            self.Totem[1]=self.Totem[1]+"#2#"+str(int(code))+"\x01"+str(int(px))+"\x01"+str(int(py))+"\x01"+str(int(angle))+"\x01"+str(int(vx))+"\x01"+str(int(vy))+"\x01"+str(int(dur))
                            data=struct.pack('!hhhhbbbxx', code, px, py, angle, vx, vy, dur)
                            self.room.sendAllOthersBin(self, eventTokens, data)
                    else:
                        code, px, py, angle, vx, vy, dur=struct.unpack('!hhhhbbb', data)
                        data=struct.pack('!hhhhbbbxx', code, px, py, angle, vx, vy, dur)
                        if self.isSyncroniser or self.isShaman:
                            if code==44:
                                if not self.UTotem:
                                    self.sendTotem(self.STotem[1], px, py, self.playerCode)
                                    self.UTotem=True
                            self.room.sendAllOthersBin(self, eventTokens, data)
                        else:
                            pass
                            #self.server.sendModChat(self, "\x06\x14", ["<R>Auto alert on <CH>" + self.username + " <R>(" + self.address[0] + ") supervise him."], False)
                            #self.server.sendModChat(self, "\x06\x14", ["Tentative de placement objet :  " + self.username + " (" + self.address[0] + ") by Moderac'tion"], False)
                elif eventToken2 == "\x18":
                    #DestructionObjet
                    value=struct.unpack('!h', data)
                    if self.isSyncroniser:
                        self.room.sendAllBin(eventTokens, data)
                    else:
                        pass
                        #self.server.sendModChat(self, "\x06\x14", ["<R>Auto alert on <CH>" + self.username + " <R>(" + self.address[0] + ") supervise him."], False)
                        #self.server.sendModChat(self, "\x06\x14", ["Tentative de destruction objet :  " + self.username + " (" + self.address[0] + ") by Moderac'tion"], False)
                else:
                    logging.warning("Unimplemented Binary %r" % eventTokens)
                    print "Unimplemented Error: Bin-"+repr(eventTokens)+"-DATA:"+repr(data)
            elif eventToken1 == "\x06":
                if eventToken2 == "\x06":
                    #Chat Message
                    utflength=struct.unpack('!h', data[:2])[0]
                    utfstring=data[2:utflength+2]
                    message = utfstring
                    if self.isBot:
                        pass
                    else:
                        message = message.replace("<","&lt;").replace("&#","&amp;#")
                    usernamez = self.username
                    logging.info("(%s) %s: %s" % (self.room.name, self.username, message))
                    print str(datetime.today())+" "+"(%s) %s: %r" % (self.room.name, self.username, message)
                    if self.privilegeLevel!=10 and self.privilegeLevel!=6 and self.privilegeLevel!=5:
                        if message == self.lastmessage:
                            message=""
                            self.sendModMessageChannel("Serveur", str(self.username)+" попытка флуда !")
                    if message!="":
                        self.lastmessage=message.strip()
                        playerCode=struct.pack("%sL" % "!", int(self.playerCode))
                        username=struct.pack('!h', len(usernamez))+usernamez
                        #sendMessage=struct.pack('!h', len(message))+message
                        if not self.mumute:
                            if not self.privilegeLevel==0:
                                if self.modmute:
                                    time=int(self.timestampCalc(self.server.getModMuteInfo(self.username)[1])[2])
                                    if time<=0:
                                        # self.modmute=False
                                        # self.server.removeModMute(self.username)
                                        # self.room.sendAllChat(playerCode, username, message)
                                        self.sendModMute(self.username, time, self.server.getModMuteInfo(self.username)[2])
                                        
                                    else:
                                        self.sendModMute(self.username, time, self.server.getModMuteInfo(self.username)[2])
                                else:
                                    if self.isHidden == 0:
                                        if self.chatColor != "Non":
                                            #user = "<font color='#" + self.chatColor + "'>" + username + "</font>"
                                            user = '<font color="#%s">%s</font>'%(self.chatColor,self.username)
                                            usern = '<font color="#FFFFFF">tsr</font>'
                                            self.sendData("\x06" + "\x14",["<ROSE>Username : " + user + "."])
                                            self.sendData("\x06" + "\x14",["<ROSE>Username2 : " + usern + "."])
                                            self.room.sendAllChatSpe(playerCode, user, message)
                                            self.room.sendAllChatSpe(playerCode, usern, message)
                                            for playerCode, client in self.room.clients.items():
                                                client.sendData("\x06" + "\x04", ["<font color='#009D9D'><a href='event:" + self.username + "'>[</font>" + user + "<font color='#009D9D'>]</a></font> <font color='#C2C2DA'>" + message + "</font>"])
                                                client.sendData("\x06" + "\x06", ["<font color='#009D9D'><a href='event:" + self.username + "'>[</font>" + user + "<font color='#009D9D'>]</a></font> <font color='#C2C2DA'>" + message + "</font>"])
                                        else:
                                            self.room.sendAllChat(playerCode, username, message)
                                    else:
                                        self.sendData("\x06" + "\x14",["<ROSE>Вы находитесь в невидимке, писать в чат невозможно."])
                        else:
                            if self.chatColor != "Non":
                                user = "<font color='#" + self.chatColor + "'>" + username + "</font>"
                                self.room.sendAllChatF(playerCode, user, message, self)
                            else:
                                self.room.sendAllChatF(playerCode, username, message, self)
                elif eventToken2 == "\x07":
                    #Sent whisper
                    nameLength=struct.unpack('!h', data[:2])[0]
                    username=data[2:nameLength+2]
                    if not username.startswith("*"):
                        username=username.lower()
                        username=username.capitalize()
                    data=data[nameLength+2:]
                    messageLength=struct.unpack('!h', data[:2])[0]
                    message=data[2:messageLength+2]
                    message=message.replace("<","&lt;").replace("&#","&amp;#")
                    #message=message.replace("\x02","")
                    #message=message.replace("\x01","")
                    #message=message.replace("\x03","")
                    #message=message.replace("\xC2\xA0","")
                    if not self.mumute:
                        if not self.privilegeLevel==0:
                            if self.modmute:
                                time=int(self.timestampCalc(self.server.getModMuteInfo(self.username)[1])[2])
                                if time<=0:
                                    # self.modmute=False
                                    # self.server.removeModMute(self.username)
                                    # if self.silence:
                                        # self.sendDisableWhispers()
                                    # else:
                                        # if not self.server.sendPrivMsg(self, self.username, username, message):
                                            # self.sendPlayerNotFound()
                                        # else:
                                            # pass
                                    self.sendModMute(self.username, time, self.server.getModMuteInfo(self.username)[2])
                                else:
                                    self.sendModMute(self.username, time, self.server.getModMuteInfo(self.username)[2])
                            else:
                                if self.silence:
                                    self.sendDisableWhispers()
                                else:
                                    if not self.server.sendPrivMsg(self, self.username, username, message):
                                        self.sendPlayerNotFound()
                                    else:
                                        pass
                    else:
                        if not self.server.sendPrivMsgF(self, self.username, username, message):
                            self.sendPlayerNotFound()
                elif eventToken2 == "\x08":
                    #Tribe message
                    messageLength=struct.unpack('!h', data[:2])[0]
                    message=data[2:messageLength+2]
                    message=message.replace("<","&lt;").replace("&#","&amp;#")
                    username=struct.pack('!h', len(self.username))+self.username
                    sendMessage=struct.pack('!h', len(message))+message
                    if self.isInTribe:
                        self.server.sendWholeTribe(self, "\x06\x08", sendMessage+username, True)
                elif eventToken2 == "\x0A":
                    #Sent command
                    if self.privilegeLevel>=3:
                      command=struct.unpack("!b", data[:1])[0]
                      commandValues=data[1:]
                      utflength=struct.unpack('!h', commandValues[:2])[0]
                      message = commandValues[2:utflength+2]
                    else:
                      command=struct.unpack("!b", data[:1])[0]
                      commandValues=data[1:]
                      utflength=struct.unpack('!h', commandValues[:2])[0]
                      message = commandValues[2:utflength+2]
                      message=message.replace("<","&lt;").replace("&#","&amp;#")
                    #message=message.replace("&#","&amp;#")

                    if command==0:
                        logcommand="ms "+message
                    if command==1:
                        logcommand="mss "+message
                    if command==2:
                        logcommand="a "+message
                    if command==3:
                        logcommand="m "+message
                        
                    else:
                        pass
                    try:
                        logging.info("(%s) [c] %s: %s" % (self.room.name, self.username, logcommand.decode('utf-8')))
                        print str(datetime.today())+" "+"(%s) [c] %s: %r" % (self.room.name, self.username, logcommand.decode('utf-8'))
                    except: pass
                    if command==0: #ms
                        if self.privilegeLevel>=4 and not self.isDrawer:
                            self.sendModMessage(0, message)
                            if not self.isBot:
                                self.server.sendAdminListen("[%s][%s][Модерация] %s"%(self.username,self.room.name,message))
                    elif command==1: #mss
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            self.sendServerMessage(message)
                            if not self.isBot:
                                self.server.sendAdminListen("[%s][%s][Сервер] %s"%(self.username,self.room.name,message))
                    elif command==2: #a
                        if TS:
                            if self.privilegeLevel>=3 and not self.isDrawer:
                                self.sendArbMessageChannel(self.username, message)
                        else:
                            if self.privilegeLevel>=3:
                                self.sendArbMessageChannel(self.username, message)

                    elif command==3: #m
                        if TS:
                            if self.privilegeLevel>=4 and not self.isDrawer:
                                self.sendModMessageChannel(self.username, message)
                        else:
                            if self.privilegeLevel>=4:
                                self.sendModMessageChannel(self.username, message)
                        
                    else:
                        pass
                else:
                    logging.warning("Unimplemented Binary %r" % eventTokens)
                    print "Unimplemented Error: Bin-"+repr(eventTokens)+"-DATA:"+repr(data)
            elif eventToken1 == "\x08":
                if eventToken2 == "\x01":
                    #Emote animation
                    #print 'DATA',data
                    emoteCode = ord(struct.unpack("!c", data)[0])
                    #print 'emoteCode: %s'%(repr(emoteCode))
                    #print 'EMOTE',self.playerCode,emoteCode
                    self.sendPlayerEmote(self.playerCode, emoteCode)
                elif eventToken2 == "\x29":
                    #SourisRose
                    playerCode = struct.unpack("!l", data[:4])[0]
                    self.room.sendAllOthersBin(self, eventTokens, data)
                elif eventToken2 == "\x2A":
                    #Cadeau
                    playerCode = struct.unpack("!l", data[:4])[0]
                    self.room.sendAllOthersBin(self, eventTokens, data)
                else:
                    logging.warning("Unimplemented Binary %r" % eventTokens)
                    print "Unimplemented Error: Bin-"+repr(eventTokens)+"-DATA:"+repr(data)
            elif eventToken1 == "\x1C":
                if eventToken2 == "\x0A":
                    hardMode = struct.unpack("!?", data)[0]
                    if self.micesaves>=500 or self.username == "Cheese":
                        if hardMode:
                            self.hardMode=1
                            self.sendHardMode("1")
                        else:
                            self.hardMode=0
                            self.sendHardMode("0")
                elif eventToken2 == "\x12":
                    colors = str(self.ByteToHex(data))
                    color = colors.replace(" ", "")
                    self.shamcolor = str(color).replace("'", "").replace("\"", "")
                    dbcur.execute('UPDATE users SET shamcolor = ? WHERE name = ?', [str(self.shamcolor), self.username])
                elif eventToken2 == "\x0C":
                    #Validation Code
                    if self.privilegeLevel!=0:
                        utflength=struct.unpack('!h', data[:2])[0]
                        code = data[2:utflength+2]
                        if code.isdigit():
                            if not self.ValidatedEmail:
                                if str(code)==str(self.LastEmailCode):
                                    dbcur.execute('UPDATE users SET Email = ? WHERE name = ?', [self.EmailAddress, self.username])
                                    dbcur.execute('UPDATE users SET EmailInfo = ? WHERE name = ?', ["True", self.username])
                                    self.ValidatedEmail=True
                                    if not self.checkInShop("209"):
                                        if self.shopitems=="":
                                            self.shopitems=str("209")
                                        else:
                                            self.shopitems=self.shopitems+",209"
                                        self.sendAnimZelda(self.playerCode, "2", "9")
                                        self.checkUnlockShopTitle()
                                        self.shopcheese+=40
                                    self.sendEmailValidated()
                                    self.sendEmailValidatedDialog()
                                else:
                                    self.sendEmailCodeInvalid()
                            elif not self.ValidatedPassChange:
                                if str(code)==str(self.LastEmailCode):
                                    self.ValidatedPassChange=True
                                    self.sendEmailValidatedDialog()
                                else:
                                    self.sendEmailCodeInvalid()
                elif eventToken2 == "\x0B":
                    #Email Address
                    if self.privilegeLevel!=0:
                        utfLength=struct.unpack('!h', data[:2])[0]
                        EmailAddr=data[2:utfLength+2]
                        data=data[utfLength+2:]
                        utfLength=struct.unpack('!h', data[:2])[0]
                        Langue=data[2:utfLength+2]
                        if not self.ValidatedEmail:
                            if not self.checkDuplicateEmail(EmailAddr):
                                if self.checkValidEmail(EmailAddr):
                                    self.EmailAddress=EmailAddr
                                    self.LastEmailCode=str(random.randrange(100000000, 999999999+1))
                                    reactor.callLater(0, self.server.sendValidationEmail, self.LastEmailCode, Langue, EmailAddr, 1)
                                    #print self.LastEmailCode
                                    self.sendEmailSent()
                                else:
                                    self.sendEmailAddrAlreadyUsed()
                            else:
                                self.sendEmailAddrAlreadyUsed()
                elif eventToken2 == "\x0E":
                    #Sent Change Password
                    if self.privilegeLevel!=0:
                        utfLength=struct.unpack('!h', data[:2])[0]
                        PassHash=data[2:utfLength+2]
                        data=data[utfLength+2:]
                        utfLength=struct.unpack('!h', data[:2])[0]
                        ForumPassHash=data[2:utfLength+2]
                        data=data[utfLength+2:]
                        utfLength=struct.unpack('!h', data[:2])[0]
                        ForumSalt=data[2:utfLength+2]
                        if self.ValidatedPassChange:
                            self.ValidatedPassChange=False
                            passwordHash=hashlib.sha512(PassHash).hexdigest()
                            dbcur.execute('UPDATE users SET password = ? WHERE name = ?', [passwordHash, self.username])
                elif eventToken2 == "\x10":
                    #Send another email
                    if self.privilegeLevel!=0:
                        utfLength=struct.unpack('!h', data[:2])[0]
                        Langue=data[2:utfLength+2]
                        self.LastEmailCode=str(random.randrange(100000000, 999999999+1))
                        reactor.callLater(0, self.server.sendValidationEmail, self.LastEmailCode, Langue, self.EmailAddress, 2)
                        #print self.LastEmailCode
                elif eventToken2 == "\x11":
                    # Country and computer info
                    try:
                        utfLength = struct.unpack('!h', data[:2])[0]
                        self.country = data[2:utfLength+2]
                        data=data[utfLength+2:]
                        utfLength = struct.unpack('!h', data[:2])[0]
                        self.computer = data[2:utfLength+2]
                        data=data[utfLength+2:]
                    except:
                        pass
                else:
                    logging.warning("Unimplemented Error: Bin-"+repr(eventTokens)+"-DATA:"+repr(data))
                    print "Unimplemented Error: Bin-"+repr(eventTokens)+"-DATA:"+repr(data)
            elif eventToken1 == "\x1B":
                if eventToken2 == "\x0B":
                    ID=struct.unpack("!h", data)[0]
                    if not ID in [48, 49, 50, 51, 52, 53]:
                        ID=53
                    data=struct.pack("!ih", self.playerCode, ID)
                    if self.room.currentWorld in range(200,210+1):
                        if self.isAfk:
                            self.isAfk=False
                        if not self.isDead:
                            self.room.sendAllBin("\x1B\x0B", data)
                else:
                    logging.warning("Unimplemented Binary %r" % eventTokens)
                    print "Unimplemented Error: Bin-"+repr(eventTokens)+"-DATA:"+repr(data)
            else:
                logging.warning("Unimplemented Binary %r" % eventTokens)
                print "Unimplemented Error: Bin-"+repr(eventTokens)+"-DATA:"+repr(data)

    def parseDataUTF(self, data):
        values = data.split("\x01")

        #logging.warning("DATA: %s" % data)
        #logging.warning("DATAD: %s" % repr(MDT_stuff))
        #logging.warning("DATAV: %s" % values)
        #print values

        eventTokens = values.pop(0)
        eventToken1, eventToken2 = eventTokens

        if eventToken1 == "\x1A":
            if eventToken2 == "\x1A":
                if self.ATEC_Time:
                    time1 = datetime.today()-self.ATEC_Time
                    time2 = timedelta(seconds=8)
                    #self.server.sendModChat(self, "\x06\x14", ["[DEBUG] %s - %s | %s"%(time1,time2,self.username)])
                    if datetime.today()-self.ATEC_Time<timedelta(seconds=8):
                        if self.room:
                            self.sendPlayerDisconnect(self.playerCode)
                            self.room.removeClient(self)
                            hmessage = "["+self.address[0]+" - "+self.username+"] обнаружен speed-hack! (Время : " + time1 + ")"
                            self.sendModMessageChannel("AntiHack", hmessage)
                        #self.sendModMessageChannel("Serveur", "Speedhack detected at "+str(self.address[0]))
                        #self.server.sendModChat(self, "\x06\x14", ["Speedhack : %s/%s |Speed: %s"%(self.username,self.address[0],time1)])
                        self.transport.loseConnection()
                self.ATEC_Time=datetime.today()
                self.sendATEC()
        
            elif eventToken2 == "\x02":
                #awake timer
                # TempsZeroBR, = values
                # TempsZeroBR = int(TempsZeroBR)
                #print str(int(time.time() * 1000) - int(self.AWKE_Time))
                #self.AWKE_Time=int(time.time() * 1000)
                if self.AwakeTimerKickTimer:
                    try:
                        self.AwakeTimerKickTimer.cancel()
                    except:
                        self.AwakeTimerKickTimer=None
                self.AwakeTimerKickTimer = reactor.callLater(120, self.AwakeTimerKick)
            elif eventToken2 == "\x03":
                #create account
                username, passwordHash, originUrl = values
                username = username.replace("<","")
                username=username.lower()
                username=username.capitalize()
                if len(username)<3:
                    self.transport.loseConnection()
                elif len(username)>12:
                    self.transport.loseConnection()
                elif not username.isalpha():
                    self.transport.loseConnection()
                elif self.server.checkExistingUsers(username):
                    self.sendData("\x1A" + "\x03", ) #Nickname Already Taken message
                else:
                    passwordHash=hashlib.sha512(passwordHash).hexdigest()
                    self.server.createAccount(username, passwordHash)
                    self.login(username, passwordHash, "1")
            elif eventToken2 == "\x04":
                #login
                username, passwordHash, startRoom, originUrl = values
                if len(passwordHash)!=0 and len(passwordHash)!=64:
                    passwordHash=""
                if passwordHash != "":
                    passwordHash=hashlib.sha512(passwordHash).hexdigest()
                username = username.replace("<","")
                if len(startRoom)>200:
                    startRoom=""
                startRoom = self.roomNameStrip(startRoom, "2")
                self.login(username, passwordHash, startRoom)
            elif eventToken2 == "\x0B":
                stageloaderInfobytesTotal, stageloaderInfobytesLoaded, loaderInfobytesTotal, loaderInfobytesLoaded, loaderInfoUrl = values
                self.sendData("\x1A" + "\x04", ["<BL>"+str(loaderInfoUrl)+"<br>"+str(stageloaderInfobytesTotal)+"<br>"+str(stageloaderInfobytesLoaded)+"<br>"+str(loaderInfobytesTotal)+"<br>"+str(loaderInfobytesLoaded)])
            elif eventToken2 == "\x15":
                #Forum datas
                PassMD5, Salt, Langue = values
                #self.updateLanguage(self.username, Langue)
                #self.sendData("\x1A" + "\x04", ["<J>Vous utilisez la langue : <R>" + Langue]) #Language-version
            else:
                logging.warning("Unimplemented %r" % eventTokens)
                #raise NotImplementedError, eventTokens
                
                
        elif eventToken1 == "\x04":
            #self.sendModMessageChannel("Serveur", "Data recue : "+eventToken2) => Don't work.
            if eventToken2 == "\x0b":
                #Voler (Cupidon/map 666)
                [Up(1)/Down(0), On(1)/Off(0)]
                self.room.sendAllOthers(self, eventTokens, values + [self.playerCode])

            elif eventToken2 == "\x06":
                #objectCode, = values
                self.room.sendAll(eventTokens, values)

            elif eventToken2 == "\x08":
                #direction, = values
                #direction = int(direction)
                self.room.sendAll(eventTokens, [self.playerCode] + values)

            elif eventToken2 == "\x0A": #\n
                self.isAfk=False
            elif eventToken2 == "\x0C":
                self.isAfk=False
                if not self.room.currentWorld in CONJURATION_MAPS:
                    if not self.isDead:
                        self.isDead=True
                        self.sendPlayerDied(self.playerCode, self.score)
                        #self.room.checkShouldChangeWorld()
                self.room.sendAllOthers(self, eventTokens, [self.playerCode])
            elif eventToken2 == "\x0D": #\r
                self.room.sendAllOthers(self, eventTokens, [self.playerCode])
            elif eventToken2 == "\x07":
                code=values[0]
                #print code, self.JumpCheck
                #if int(code)!=self.JumpCheck:
                #    if self.room:
                #        self.sendPlayerDisconnect(self.playerCode)
                #        self.room.removeClient(self)
                #    self.transport.loseConnection()
                self.JumpCheck=self.JumpCheck+2
            elif eventToken2 == "\x0E":
                #conjuration
                x, y = values
                if not self.room.currentWorld in CONJURATION_MAPS:
                    if not self.isDead:
                        self.isDead=True
                        self.sendPlayerDied(self.playerCode, self.score)
                        #self.room.checkShouldChangeWorld()
                else:
                    reactor.callLater(10, self.sendDestroyConjuration, x, y)
                    self.room.sendAll(eventTokens, values)

            elif eventToken2 == "\x09":
                #Se baisser
                if len(values)==3:
                    if self.room.currentWorld==1 or self.room.currentWorld==130:
                        crouching, x, y = values
                        x=int(x)
                        y=int(y)
                        if x>=11 and x<=286 and y>=330 and y<=340: #y>=210 and y<=246:
                            self.isFishing=1
                            #self.sendData("\x06" + "\x14", ["Debug 1"])
                        elif x>=287 and x<=491 and y>=330 and y<=340: #y>=92 and y<=128:
                            self.isFishing=2
                            #self.sendData("\x06" + "\x14", ["Debug 2"])
                        elif x>=492 and x<=600 and y>=330 and y<=340: #y>=38 and y<=74:
                            self.isFishing=3
                            #self.sendData("\x06" + "\x14", ["Debug 3"])
                        #elif x>=0 and x<=800 and y>=0 and y<=800: #y>=38 and y<=74:
                            #self.isFishing=3
                        else:
                            self.isFishing=False
                        if self.Map777FishingTimer:
                            try:
                                self.Map777FishingTimer.cancel()
                                #self.sendData("\x06" + "\x14", ["Stop "])
                            except:
                                self.Map777FishingTimer=None
                                #self.sendData("\x06" + "\x14", ["None "])
                        self.Map777FishingTimer = reactor.callLater(20, self.Map777Fishing)
                        #self.sendData("\x06" + "\x14", ["Vous pechez au positions x = " + str(x) + "  y = " + str(y)])
            elif eventToken2 == "\x12":
                pass #Grappin
                #x, y = values
                #self.room.sendAll(eventTokens, [self.playerCode] + values)
            elif eventToken2 == "\x13":
                pass #grappling hook
                #self.room.sendAll(eventTokens, [self.playerCode])
            elif eventToken2 == "\x14":
                print values
            else:
                logging.warning("Unimplemented %r" % eventTokens)
                #raise NotImplementedError, eventTokens
        if eventToken1 == "\x0C":
            if eventToken2 == "\x10":
                #Ballon sur souris
                print data
        elif eventToken1 == "\x08":
            #self.sendModMessageChannel("Serveur", "Data recue : "+eventToken2) => Don't work.
            if eventToken2 == "\x10":
                    #attach baloon to player
                    #  self.sendModMessageChannel("Baloon", "Pwet !")
                self.room.sendAll("\x08\x10", [values[0]])
            elif eventToken2 == "\x11":
                    #baloon detatched
                self.room.sendAll("\x08\x10", [self.playerCode, "x"])
            elif eventToken2 == "\x0D":
                #Ouverture ami
                if not self.friendsList:
                    self.sendData("\x08" + "\x0C",[8])
                else:
                    sendfriendsList = self.friendsList[:]
                    for position, name in enumerate(sendfriendsList):
                        if self.server.checkAlreadyConnectedAccount(name):
                            if self.server.friendsListCheck(name, self.username):
                                room = self.server.getFindPlayerRoom(name)
                            else:
                                room = "-"
                            sendfriendsList[position]=name+"\x02"+room
                    self.sendData("\x08" + "\x0C",[8]+sendfriendsList)
            elif eventToken2 == "\x0e":
                #remove friend
                name = values[0]
                self.friendsList.remove(name)
                dbfriendsList = json.dumps(self.friendsList)
                dbcur.execute('UPDATE users SET friends = ? WHERE name = ?', [dbfriendsList, self.username])
                self.sendRemovedFriend(name)
            elif eventToken2 == "\x42":
                print data
                #Demande transformation en zombie
                self.sendZombieMode()
            else:
                logging.warning("Unimplemented %r" % eventTokens)
        elif eventToken1 == "\x06":
            if eventToken2 == "\x1A":
                #Envoi commande
                
                event, = values
                event = event.replace("<","&lt;").replace("&#","&amp;#")
                event_raw = event.strip()
                event = event_raw.lower()

                EVENTRAWSPLIT = event_raw.split(" ")
                EVENTCOUNT = len(EVENTRAWSPLIT)
                try:
                    logging.info("(%s) [c] %s: %r" % (self.room.name, self.username, event_raw))
                except:
                    pass
                if event in ("rire", "danse", "pleurer", "bisou", "kiss"):
                    pass
                else:
                    try:
                        print str(datetime.today())+" "+"(%s) [c] %s: %r" % (self.room.name, self.username, event_raw)
                    except:
                        pass
                if len(event) == 1:
                    event = "INVALID"

                if EVENTCOUNT == 1:
                    if event in ("dance", "danse"):
                        self.sendPlayerEmote(self.playerCode, 0, False)
                    elif event == "/":
                        pass
                    elif event in ("laugh", "rire"):
                        self.sendPlayerEmote(self.playerCode, 1, False)
                    elif event == "claps":
                        self.sendPlayerEmote(self.playerCode, 5, False)
                    elif event == "sleep":
                        self.sendPlayerEmote(self.playerCode, 6, False)
                    elif event == "facepalm":
                        self.sendPlayerEmote(self.playerCode, 7, False)
                    elif event == "angry":
                        self.sendPlayerEmote(self.playerCode, 4, False)
                    elif event in ("cry", "pleurer"):
                        self.sendPlayerEmote(self.playerCode, 2, False)
                    elif event == "sleeps":
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            self.room.forceEmoteAll(6)
                            if not self.isBot:
                                self.server.sendAdminListen("[%s][%s][Sleep]"%(self.username,self.room.name))
                    elif event == "clap":
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            self.room.forceEmoteAll(5)
                            if not self.isBot:
                                self.server.sendAdminListen("[%s][%s][Clap]"%(self.username,self.room.name))
                    elif event in ("kiss", "bisou"):
                        self.sendPlayerEmote(self.playerCode, 3, False)
                    elif event == "party":
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if not self.isBot:
                                self.server.sendAdminListen("[%s][%s][Party]"%(self.username,self.room.name))
                            self.room.forceEmoteAll(0)
                    elif event == "noboom":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.room.isBooming = False
                            self.room.MegaBooming = "0"
                            self.room.GenerateExplode()
                    elif event == "boom":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.room.isBooming = True
                            self.room.GenerateExplode()
                    elif event == "megaboom":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.room.isBooming = True
                            self.room.MegaBooming = "1"
                            self.room.GenerateExplode()
                    elif event == "disconnect":
                        self.sendPlayerDisconnect(self.playerCode)
                        self.room.removeClient(self)
                        self.transport.loseConnection()
                    elif event == "hide":
                        if self.privilegeLevel>=4 and not self.isDrawer:
                            self.sendPlayerDisconnect(self.playerCode)
                            self.isHidden = True
                            self.sendData("\x06"+"\x14",["Невидимка активирована."])
                    elif event == "unhide":
                        if self.privilegeLevel>=4 and not self.isDrawer:
                            self.isHidden = False
                            self.sendData("\x06"+"\x14",["Невидимка отключена."])
                    elif event == "salon" or event == "room" or event == "sala":
                        self.enterRoom(self.server.recommendRoom())
                        for i, v in enumerate(self.friendsList):
                            sendfriendsList = self.friendsList[:]
                            for position, name in enumerate(sendfriendsList):
                                if self.server.checkAlreadyConnectedAccount(name):
                                    if self.server.friendsListCheck(name, self.username):
                                        room = self.server.getFindPlayerRoom(name)
                                    else:
                                        room = "-"
                                    sendfriendsList[position]=name+"\x02"+room
                            self.sendData("\x08" + "\x0C",[8]+sendfriendsList)
              #      elif event == "look" or event == "habits":
               #         self.sendData("\x1A" + "\x04", ["Liste de vos habits actuels : <CH>" + self.look])

                    elif event == "testvampire":
                        #self.room.sendAll("\x08\x42", [self.username])
                        #self.room.sendAll("\x08\x42", [self.playerCode])
                        #self.room.sendAll("\x08\x42", [self.playerCode])
                        self.room.sendAllBin("\x08\x42", struct.pack("!l", int(self.playerCode)))

                    elif event == "vanilla":
                        self.enterRoom(self.server.recommendRoomPrefixed("vanilla"))
                    elif event == "bootcamp":
                        self.enterRoom(self.server.recommendRoomPrefixed("bootcamp"))
                    elif event == "speed":
                        self.enterRoom(self.server.recommendRoomPrefixed("speed"))
                    elif event == "mt":
                        if self.isInTribe:
                            if self.muteTribe:
                                self.sendActivateTribeChat(self.username)
                                self.muteTribe = False
                            else:
                                self.sendDeactivateTribeChat(self.username)
                                self.muteTribe = True
                    elif event == "silence":
                        if self.privilegeLevel==0:
                            pass
                        else:
                            if self.silence:
                                self.silence=False
                                self.sendEnableWhispers()
                            else:
                                self.silence=True
                                self.sendDisableWhispers()
                    elif event == "ld":
                        self.sendData("\x1A" + "\x04", ["<BL>"+str(self.loaderInfoUrl)+"<br>"+str(self.stageloaderInfobytesTotal)+"<br>"+str(self.stageloaderInfobytesLoaded)+"<br>"+str(self.loaderInfobytesTotal)+"<br>"+str(self.loaderInfobytesLoaded)])
                    elif event == "lde":
                        self.sendData("\x1A" + "\x0B")
                    #elif event == "bigtext":
                    #    self.sendData("\x1A" + "\x04", ["To turn off big text, refresh the page and login again.<TI>"])
                    elif event in ("profil", "profile", "perfil"):
                        self.sendProfile(self.username)
             #       elif event == "items":
             #           if self.disableShop:
             #               self.sendData("\x1A" + "\x04", ["<BL>Habits affichés."])
             #               self.disableShop=False
             #           else:
             #               self.sendData("\x1A" + "\x04", ["<BL>Habits non affichés."])
             #               self.disableShop=True
             #       elif event == "censor":
             #            if self.privilegeLevel>=5 and not self.isDrawer:
             #               if self.censorChat:
             #                   self.sendData("\x1A" + "\x04", ["<BL>Censoring chat disabled."])
             #                   self.censorChat=False
             #               else:
             #                   self.sendData("\x1A" + "\x04", ["<BL>Censoring chat enabled."])
             #                   self.censorChat=True
                    elif event == "mutechat":
                        if self.muteChat:
                            self.sendData("\x1A" + "\x04", ["<BL>Показ чата отключен."])
                            self.muteChat=False
                        else:
                            self.sendData("\x1A" + "\x04", ["<BL>Показ чата включен."])
                            self.muteChat=True
                    elif event == "editeur":
                        if self.privilegeLevel==0:
                            pass
                        else:
                            self.enterRoom("\x03"+"[Editeur] "+self.username)
                            self.sendData("\x0E" + "\x0E",[])
                    elif event == "totem":
                        if self.privilegeLevel==0:
                            pass
                        else:
                            if self.micesaves>=500 or self.username == "Cheese":
                                self.enterRoom("\x03"+"[Totem] "+self.username)
                    elif event == "sauvertotem":
                        if self.room.isTotemEditeur:
                            self.server.setTotemData(self.username, self.Totem[0], self.Totem[1])
                            self.STotem[0]=self.Totem[0]
                            self.STotem[1]=self.Totem[1]
                            self.sendPlayerDied(self.playerCode, self.score)
                            self.enterRoom(self.server.recommendRoom())
                    elif event == "resettotem":
                        if self.room.isTotemEditeur:
                            self.Totem =[0,""]
                            self.RTotem=True
                            self.isDead=True
                            self.sendPlayerDied(self.playerCode, self.score)
                            self.room.checkShouldChangeWorld()
                    elif event == "ranking":
                        Userlist = []
                        dbcur.execute('select name, saves, first, cheese from users')
                        rrfRows = dbcur.fetchall()
                        if rrfRows is None:
                            pass
                        else:
                            for rrf in rrfRows:
                                Userlist.append(rrf)
                        #Saves
                        SaveList={}
                        SaveListDisp=[]
                        for user in Userlist:
                            SaveList[user[0]] = user[1]
                        mSL=max(SaveList.iterkeys(), key=lambda k: SaveList[k])
                        SaveListDisp.append([1, mSL, SaveList[mSL]])
                        del SaveList[mSL]
                        mSL=max(SaveList.iterkeys(), key=lambda k: SaveList[k])
                        SaveListDisp.append([2, mSL, SaveList[mSL]])
                        del SaveList[mSL]
                        mSL=max(SaveList.iterkeys(), key=lambda k: SaveList[k])
                        SaveListDisp.append([3, mSL, SaveList[mSL]])
                        del SaveList[mSL]
                        mSL=max(SaveList.iterkeys(), key=lambda k: SaveList[k])
                        SaveListDisp.append([4, mSL, SaveList[mSL]])
                        del SaveList[mSL]
                        mSL=max(SaveList.iterkeys(), key=lambda k: SaveList[k])
                        SaveListDisp.append([5, mSL, SaveList[mSL]])
                        del SaveList[mSL]
                        #Firsts
                        FirstList={}
                        FirstListDisp=[]
                        for user in Userlist:
                            FirstList[user[0]] = user[2]
                        mSL=max(FirstList.iterkeys(), key=lambda k: FirstList[k])
                        FirstListDisp.append([1, mSL, FirstList[mSL]])
                        del FirstList[mSL]
                        mSL=max(FirstList.iterkeys(), key=lambda k: FirstList[k])
                        FirstListDisp.append([2, mSL, FirstList[mSL]])
                        del FirstList[mSL]
                        mSL=max(FirstList.iterkeys(), key=lambda k: FirstList[k])
                        FirstListDisp.append([3, mSL, FirstList[mSL]])
                        del FirstList[mSL]
                        mSL=max(FirstList.iterkeys(), key=lambda k: FirstList[k])
                        FirstListDisp.append([4, mSL, FirstList[mSL]])
                        del FirstList[mSL]
                        mSL=max(FirstList.iterkeys(), key=lambda k: FirstList[k])
                        FirstListDisp.append([5, mSL, FirstList[mSL]])
                        del FirstList[mSL]
                        #Cheese
                        CheeseList={}
                        CheeseListDisp=[]
                        for user in Userlist:
                            CheeseList[user[0]] = user[3]
                        mSL=max(CheeseList.iterkeys(), key=lambda k: CheeseList[k])
                        CheeseListDisp.append([1, mSL, CheeseList[mSL]])
                        del CheeseList[mSL]
                        mSL=max(CheeseList.iterkeys(), key=lambda k: CheeseList[k])
                        CheeseListDisp.append([2, mSL, CheeseList[mSL]])
                        del CheeseList[mSL]
                        mSL=max(CheeseList.iterkeys(), key=lambda k: CheeseList[k])
                        CheeseListDisp.append([3, mSL, CheeseList[mSL]])
                        del CheeseList[mSL]
                        mSL=max(CheeseList.iterkeys(), key=lambda k: CheeseList[k])
                        CheeseListDisp.append([4, mSL, CheeseList[mSL]])
                        del CheeseList[mSL]
                        mSL=max(CheeseList.iterkeys(), key=lambda k: CheeseList[k])
                        CheeseListDisp.append([5, mSL, CheeseList[mSL]])
                        del CheeseList[mSL]
                        self.sendData("\x1A" + "\x04", ["<<ROSE>Шаман (Спасено мышей)"])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(SaveListDisp[0][0])+" - <N>"+str(SaveListDisp[0][1])+" <V>- "+str(SaveListDisp[0][2])])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(SaveListDisp[1][0])+" - <N>"+str(SaveListDisp[1][1])+" <V>- "+str(SaveListDisp[1][2])])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(SaveListDisp[2][0])+" - <N>"+str(SaveListDisp[2][1])+" <V>- "+str(SaveListDisp[2][2])])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(SaveListDisp[3][0])+" - <N>"+str(SaveListDisp[3][1])+" <V>- "+str(SaveListDisp[3][2])])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(SaveListDisp[4][0])+" - <N>"+str(SaveListDisp[4][1])+" <V>- "+str(SaveListDisp[4][2])])
                        self.sendData("\x1A" + "\x04", ["<<ROSE>Мыши (Собрано сыра)"])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(CheeseListDisp[0][0])+" - <N>"+str(CheeseListDisp[0][1])+" <V>- "+str(CheeseListDisp[0][2])])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(CheeseListDisp[1][0])+" - <N>"+str(CheeseListDisp[1][1])+" <V>- "+str(CheeseListDisp[1][2])])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(CheeseListDisp[2][0])+" - <N>"+str(CheeseListDisp[2][1])+" <V>- "+str(CheeseListDisp[2][2])])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(CheeseListDisp[3][0])+" - <N>"+str(CheeseListDisp[3][1])+" <V>- "+str(CheeseListDisp[3][2])])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(CheeseListDisp[4][0])+" - <N>"+str(CheeseListDisp[4][1])+" <V>- "+str(CheeseListDisp[4][2])])
                        self.sendData("\x1A" + "\x04", ["<<ROSE>Мыши (Первосыры)"])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(FirstListDisp[0][0])+" - <N>"+str(FirstListDisp[0][1])+" <V>- "+str(FirstListDisp[0][2])])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(FirstListDisp[1][0])+" - <N>"+str(FirstListDisp[1][1])+" <V>- "+str(FirstListDisp[1][2])])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(FirstListDisp[2][0])+" - <N>"+str(FirstListDisp[2][1])+" <V>- "+str(FirstListDisp[2][2])])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(FirstListDisp[3][0])+" - <N>"+str(FirstListDisp[3][1])+" <V>- "+str(FirstListDisp[3][2])])
                        self.sendData("\x1A" + "\x04", ["<V>"+str(FirstListDisp[4][0])+" - <N>"+str(FirstListDisp[4][1])+" <V>- "+str(FirstListDisp[4][2])])
                    elif event == "rank":
                        Userlist = []
                        dbcur.execute('select name, saves, first, cheese from users')
                        rrfRows = dbcur.fetchall()
                        if rrfRows is None:
                            pass
                        else:
                            for rrf in rrfRows:
                                Userlist.append(rrf)
                        #Saves
                        SaveList={}
                        SaveListDisp=[]
                        for user in Userlist:
                            SaveList[user[0]] = user[1]
                        mSL=max(SaveList.iterkeys(), key=lambda k: SaveList[k])
                        SaveListDisp.append([1, mSL, SaveList[mSL]])
                        del SaveList[mSL]
                        mSL=max(SaveList.iterkeys(), key=lambda k: SaveList[k])
                        SaveListDisp.append([2, mSL, SaveList[mSL]])
                        del SaveList[mSL]
                        mSL=max(SaveList.iterkeys(), key=lambda k: SaveList[k])
                        SaveListDisp.append([3, mSL, SaveList[mSL]])
                        del SaveList[mSL]
                        mSL=max(SaveList.iterkeys(), key=lambda k: SaveList[k])
                        SaveListDisp.append([4, mSL, SaveList[mSL]])
                        del SaveList[mSL]
                        mSL=max(SaveList.iterkeys(), key=lambda k: SaveList[k])
                        SaveListDisp.append([5, mSL, SaveList[mSL]])
                        del SaveList[mSL]
                        #Firsts
                        FirstList={}
                        FirstListDisp=[]
                        for user in Userlist:
                            FirstList[user[0]] = user[2]
                        mSL=max(FirstList.iterkeys(), key=lambda k: FirstList[k])
                        FirstListDisp.append([1, mSL, FirstList[mSL]])
                        del FirstList[mSL]
                        mSL=max(FirstList.iterkeys(), key=lambda k: FirstList[k])
                        FirstListDisp.append([2, mSL, FirstList[mSL]])
                        del FirstList[mSL]
                        mSL=max(FirstList.iterkeys(), key=lambda k: FirstList[k])
                        FirstListDisp.append([3, mSL, FirstList[mSL]])
                        del FirstList[mSL]
                        mSL=max(FirstList.iterkeys(), key=lambda k: FirstList[k])
                        FirstListDisp.append([4, mSL, FirstList[mSL]])
                        del FirstList[mSL]
                        mSL=max(FirstList.iterkeys(), key=lambda k: FirstList[k])
                        FirstListDisp.append([5, mSL, FirstList[mSL]])
                        del FirstList[mSL]
                        #Cheese
                        CheeseList={}
                        CheeseListDisp=[]
                        for user in Userlist:
                            CheeseList[user[0]] = user[3]
                        mSL=max(CheeseList.iterkeys(), key=lambda k: CheeseList[k])
                        CheeseListDisp.append([1, mSL, CheeseList[mSL]])
                        del CheeseList[mSL]
                        mSL=max(CheeseList.iterkeys(), key=lambda k: CheeseList[k])
                        CheeseListDisp.append([2, mSL, CheeseList[mSL]])
                        del CheeseList[mSL]
                        mSL=max(CheeseList.iterkeys(), key=lambda k: CheeseList[k])
                        CheeseListDisp.append([3, mSL, CheeseList[mSL]])
                        del CheeseList[mSL]
                        mSL=max(CheeseList.iterkeys(), key=lambda k: CheeseList[k])
                        CheeseListDisp.append([4, mSL, CheeseList[mSL]])
                        del CheeseList[mSL]
                        mSL=max(CheeseList.iterkeys(), key=lambda k: CheeseList[k])
                        CheeseListDisp.append([5, mSL, CheeseList[mSL]])
                        del CheeseList[mSL]
                        self.sendData("\x1A" + "\x17", ["<br><br><br><br><br><br>________________________________________________________________________________\n\
<ROSE><b>5 лучших игроков по спасенным мышам:</b>\n\
<ROSE>"+str(SaveListDisp[0][0])+" - <N>"+str(SaveListDisp[0][1])+" <V>- "+str(SaveListDisp[0][2])+"\n\
<ROSE>"+str(SaveListDisp[1][0])+" - <N>"+str(SaveListDisp[1][1])+" <V>- "+str(SaveListDisp[1][2])+"\n\
<ROSE>"+str(SaveListDisp[2][0])+" - <N>"+str(SaveListDisp[2][1])+" <V>- "+str(SaveListDisp[2][2])+"\n\
<ROSE>"+str(SaveListDisp[3][0])+" - <N>"+str(SaveListDisp[3][1])+" <V>- "+str(SaveListDisp[3][2])+"\n\
<ROSE>"+str(SaveListDisp[4][0])+" - <N>"+str(SaveListDisp[4][1])+" <V>- "+str(SaveListDisp[4][2])+"\n\
<ROSE><b>5 лучших игроков по собранному сыру:</b>\n\
<ROSE>"+str(CheeseListDisp[0][0])+" - <N>"+str(CheeseListDisp[0][1])+" <V>- "+str(CheeseListDisp[0][2])+"\n\
<ROSE>"+str(CheeseListDisp[1][0])+" - <N>"+str(CheeseListDisp[1][1])+" <V>- "+str(CheeseListDisp[1][2])+"\n\
<ROSE>"+str(CheeseListDisp[2][0])+" - <N>"+str(CheeseListDisp[2][1])+" <V>- "+str(CheeseListDisp[2][2])+"\n\
<ROSE>"+str(CheeseListDisp[3][0])+" - <N>"+str(CheeseListDisp[3][1])+" <V>- "+str(CheeseListDisp[3][2])+"\n\
<ROSE>"+str(CheeseListDisp[4][0])+" - <N>"+str(CheeseListDisp[4][1])+" <V>- "+str(CheeseListDisp[4][2])+"\n\
<ROSE><b>5 лучших игроков по собранному сыру первым:</b>\n\
<ROSE>"+str(FirstListDisp[0][0])+" - <N>"+str(FirstListDisp[0][1])+" <V>- "+str(FirstListDisp[0][2])+"\n\
<ROSE>"+str(FirstListDisp[1][0])+" - <N>"+str(FirstListDisp[1][1])+" <V>- "+str(FirstListDisp[1][2])+"\n\
<ROSE>"+str(FirstListDisp[2][0])+" - <N>"+str(FirstListDisp[2][1])+" <V>- "+str(FirstListDisp[2][2])+"\n\
<ROSE>"+str(FirstListDisp[3][0])+" - <N>"+str(FirstListDisp[3][1])+" <V>- "+str(FirstListDisp[3][2])+"\n\
<ROSE>"+str(FirstListDisp[4][0])+" - <N>"+str(FirstListDisp[4][1])+" <V>- "+str(FirstListDisp[4][2])+"\n\
 ________________________________________________________________________________<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>"])
                    elif event == "pr":
                        if self.privilegeLevel!=0:
                            self.enterRoom("\x03"+"[Tribe] "+self.username)
                    elif event == "prclose":
                        if self.room.PrivateRoom:
                            if self.room.name == "\x03[Tribe] "+self.username:
                                self.room.moveAllRoomClients("", True)
                    elif event in ("vampire"):
                        if self.privilegeLevel==10 and not self.isDrawer:
                            self.sendZombieMode()
                    elif event in ("kill", "suicide", "bubbles", "die"):
                        if not self.isDead:
                            self.isDead = True
                            self.score -= 1
                            if self.score < 0:
                                self.score = 0
                            self.sendPlayerDied(self.playerCode, self.score)
                            self.room.checkShouldChangeWorld()
                    elif event == "re" or event == "respawn":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if self.isDead:
                                self.room.respawnSpecific(self.username)
                                if self.isShaman:
                                    lol = "runbin 01010005081401345"
                                    data = str(lol.split(" ", 1)[1]).replace(" ","")
                                    eventcodes=data[:4]
                                    data=data[4:]
                                    #self.sendData(self.HexToByte(eventcodes), self.HexToByte(data),True)
                                    self.room.sendAllBin(self.HexToByte(eventcodes), self.HexToByte(data))
                                    
                                    
                    elif event in ("killall", "map", "np"):
                        if not self.room.votingMode:
                            if self.privilegeLevel>=3 and not self.isDrawer:
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][СледКарта]"%(self.username,self.room.name))
                                self.room.killAll()
                                if self.room.isBootcamp:
                                    self.room.worldChangeTimer.cancel()
                                    self.room.worldChange()
                            else:
                                if self.room.namewihout == "\x03[Tribe] "+self.username:
                                    if event == "np":
                                        pass
                                    elif event == "killall":
                                        pass
                                    else:
                                        if self.room.isBootcamp:
                                            pass
                                        else:
                                            self.room.killAll()
                    elif event == "stop" and not event == "/":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if not self.isBot:
                                self.server.sendAdminListen("[%s][%s][ОстановленаМузыка]"%(self.username,self.room.name))
                            self.sendStopMusic()
                    elif event in ("musicoff"):
                        if self.privilegeLevel>=5:
                            self.musicOff = True
                            self.sendData("\x1A" + "\x0C",[])
                    elif event == "facebook":
                        if self.privilegeLevel==0:
                            pass
                        else:
                            dbcur.execute('select facebook from users where name = ?', [self.username])
                            rrf = dbcur.fetchone()
                            if rrf is None:
                                pass
                            else:
                                if rrf[0] == 0:
                                    self.shopcheese += 20
                                    self.sendData("\x1A" + "\x13",[])
                                    dbcur.execute('UPDATE users SET facebook = ? WHERE name = ?', [1, self.username])
                                else:
                                    pass
                    elif event == "csr":
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            self.room.changeSyncroniserRandom()
                    elif event == "rsandbox":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.room.resetSandbox()
                    elif event == "playerlist":
                        self.sendData("\x06" + "\x14",["<N>Playerlist start"])
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            for room in self.server.rooms.values():
                                for playerCode, client in room.clients.items():
                                    #self.sendData("\x06" + "\x14",[client.username])
                                    self.sendModMessageChannel("Список игроков", client.username)
                    elif event == "online":
                        if self.privilegeLevel>=5:
                            players = ""
                            for room in self.server.rooms.values():
                                for playerCode, client in room.clients.items():
                                    if client.privilegeLevel>=10 and not client.isDrawer:
                                        rank = "Администратор"
                                    if client.privilegeLevel == 11 and not client.isDrawer:
                                        rank = "Техник"
                                    elif client.privilegeLevel>=10 and client.isDrawer:
                                        rank = "Художник"
                                    elif client.privilegeLevel == 8:
                                        rank = "Мега модератор"
                                    elif client.privilegeLevel == 6:
                                        rank = "Супер модератор"
                                    elif client.privilegeLevel == 5:
                                        rank = "Модератор"
                                    elif client.privilegeLevel == 4:
                                        rank = "Бот"
                                    elif client.privilegeLevel == 3:
                                        rank = "Арбитр"
                                    elif client.privilegeLevel == 1:
                                        rank = "Игрок"
                                    elif client.privilegeLevel == 0:
                                        rank = "Гость"
                                    else:
                                        rank = "<R>Ошибка<BL>"
                                    players = "%s - %s : %s"%(client.username, rank, client.room.name)
                                    self.sendData("\x06"+"\x14",[players])
                    elif event == "startsnow":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendStartSnowStorm()
                    elif event == "stopsnow":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendEndSnowStorm()
                    elif event == "up":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if int(self.room.getPlayerCount()) >= 2:
                                self.sendData("\x06"+"\x14",["self.room.getSecondHighestShaman return value: "+str(self.room.getSecondHighestShaman())])
                                self.sendData("\x06"+"\x14",["Your code is: "+str(self.playerCode)])
                            else:
                                self.sendData("\x06"+"\x14",["Empty Sequence. Did not run self.room.getSecondHighestShaman to avoid error."])
                            self.sendForumCreateAccount()
                            self.sendForumNewPM(5)
                    elif event == "newhat":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendNewHat()
                    elif event == "looktest":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendData("\x06"+"\x14",[str(self.look)])
                    elif event == "runbin":
                        if self.privilegeLevel>=10 and not self.isDrawer or self.privilegeLevel==4:
                            self.sendData("\x06"+"\x14",["Votre code (Brut): "+str(self.playerCode)])
                            self.sendData("\x06"+"\x14",["Votre code (HEX): "+self.ByteToHex(struct.pack("%sL" % "!", int(self.playerCode)))])
                    elif event == "freboot":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendServerRestart(5, 10)
                            self.rebootTimer = reactor.callLater(10, self.server.restartServer)
                    elif event == "reboot":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendServerRestart()
                            self.rebootTimer = reactor.callLater(120, self.server.restartServer)
                    elif event == "reboot5":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendServerRestartMIN(5)
                            self.rebootTimer = reactor.callLater(300, self.server.restartServer)
                            self.rebootTimer2 = reactor.callLater(180, self.sendServerRestart)		
                    elif event == "reboot10":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendServerRestartMIN(10)
                            self.rebootTimer = reactor.callLater(600, self.server.restartServer)
                            self.rebootTimer2 = reactor.callLater(300, self.sendServerRestart)
                    elif event == "shutdown":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendServerMessage("Сервер будет отключен через 2 минуты.")
                            self.rebootTimer = reactor.callLater(120, self.server.stopServer)
                    elif event == "fshutdown":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendServerMessage("Отключение сервера.")
                            self.server.stopServer()
                    elif event == "party":
                        if self.privilegeLevel>=10:
                           self.sendEverybodyDance()
                    elif event == "ls":
                        if self.privilegeLevel>=3 and not self.isDrawer:
                            self.server.getRoomList(self)
                    elif event == "lst":
                        if self.privilegeLevel>=3 and not self.isDrawer:
                            self.server.getTribesList(self)
                    elif event == "sy?":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            self.sendData("\x06" + "\x14",["Синкхронизатор : ["+str(self.room.getCurrentSync()+"]")])
                            #self.sendModMessageChannel("Serveur", "The sync in room "+str(self.roomname)+" is "+str(self.room.getCurrentSync()))
                    elif event == "p0":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["0", self.room.ISCM])
                                self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(self.room.ISCM))+"-"+str(self.room.ISCM)+" на - Обычная карта."])
                    elif event == "p1":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["1", self.room.ISCM])
                                self.room.sendAll("\x05\x12", [])
                                self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)+" на - Хорошая карта."])
                    elif event == "p2":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["2", self.room.ISCM])
                                self.room.sendAll("\x05\x12", [])
                                self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)+" на - Хорошая карта(Официальная)."])
                    elif event == "p3":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["3", self.room.ISCM])
                                self.room.sendAll("\x05\x12", [])
                                self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)+" на - Буткамп."])
                    elif event == "p4":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["4", self.room.ISCM])
                                self.room.sendAll("\x05\x12", [])
                                self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)+" на - Шаман."])
                    elif event == "p5":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["5", self.room.ISCM])
                                self.room.sendAll("\x05\x12", [])
                                self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)+" на - Арт"])
                    elif event == "p6":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["6", self.room.ISCM])
                                self.room.sendAll("\x05\x12", [])
                                self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)+" на - Техника."])
                    elif event == "p44":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["44", self.room.ISCM])
                                self.room.sendAll("\x05\x12", [])
                                self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)+" на - Удалена."])
                    elif event == "p7":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["7", self.room.ISCM])
                                self.room.sendAll("\x05\x12", [])
                                self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)+" на - Нет шамана."])
                    elif event == "p8":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["8", self.room.ISCM])
                                self.room.sendAll("\x05\x12", [])
                                self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)+" на - Кооператив."])
                    elif event == "p9":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["9", self.room.ISCM])
                                self.room.sendAll("\x05\x12", [])
                                self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)+" на - Разнообразное."])
                    elif event == "p22":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["22", self.room.ISCM])
                                self.room.sendAll("\x05\x12", [])
                                self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)+" на - Карта племени."])
                    elif event == "vd":
                        if self.privilegeLevel>=11 and not self.isDrawer:
                            self.sendData("\x06" + "\x14",["&gt;&gt;Current local scope"])
                            for name in dir():
                                myvalue = eval(name)
                                self.sendData("\x06" + "\x14",[repr(str(name)+" Type:"+str(type(name).__name__)+" Value:"+str(myvalue)).replace("<", "&lt;")])
                            self.sendData("\x06" + "\x14",["&gt;&gt;Global symbol table"])
                            for name in globals():
                                myvalue = eval(name)
                                self.sendData("\x06" + "\x14",[repr(str(name)+" Type:"+str(type(name).__name__)+" Value:"+str(myvalue)).replace("<", "&lt;")])
                            self.sendData("\x06" + "\x14",["&gt;&gt;Local symbol table"])
                            for name in locals():
                                myvalue = eval(name)
                                self.sendData("\x06" + "\x14",[repr(str(name)+" Type:"+str(type(name).__name__)+" Value:"+str(myvalue)).replace("<", "&lt;")])
                    elif event == "errorlog":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            logFile = open("error.log", "rb")
                            logData = logFile.read()
                            logFile.close()
                            self.sendData("\x06" + "\x14",[logData.replace("<", "&lt;").replace("\x0D\x0A", "\x0A")])
                    elif event == "clearerrorlog":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            try:
                                logFile = open("error.log", "w")
                                logFile.close()
                                self.sendData("\x06" + "\x14",["Лог ошибок очищен."])
                            except IOError, e:
                                self.sendData("\x06" + "\x14",[str(e).replace("Errno", "Error")])
                                #self.sendData("\x06" + "\x14",["Try /clearerrorlog2 to try clearing log while restarting server."])
                    elif event == "clearerrorlog2":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendServerRestartSEC(10)
                            self.rebootTimer = reactor.callLater(10, self.server.restartServerDelLog)
                    elif event == "update5":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendServerRestartSEC(5)
                            self.rebootTimer = reactor.callLater(10, self.server.restartServer5min)
                    elif event == "update10":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendServerRestartSEC(10)
                            self.rebootTimer = reactor.callLater(10, self.server.restartServer10min)
                    elif event == "update20":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendServerRestartSEC(20)
                            self.rebootTimer = reactor.callLater(10, self.server.restartServer20min)
                    elif event == "update30":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendServerRestartSEC(20)
                            self.rebootTimer = reactor.callLater(10, self.server.restartServer30min)
                    elif event in ("find", "search", "chercher"):
                        if self.privilegeLevel>=3 and not self.isDrawer:
                            roomname = self.server.getFindPlayerRoomPartial(self, "", True)		
                    elif event == "vcup":
                        #eventTokens = "\x08\x29"
                        data = self.playerCode
                        self.sendData("\x08" + "\x29", [data])
                        #self.room.sendAllOthersBin(self, eventTokens, data)
                    elif event == "listen":
                        if self.privilegeLevel>=5:
                            if self.isListening:
                                self.sendData("\x06" + "\x14",["Показ действий модератора отключен."])
                                self.isListening = False
                            else:
                                self.isListening = True
                                self.sendData("\x06" + "\x14",["Показ действий модератора включен."])
                    elif event == "drawings":
                        if self.privilegeLevel>=10:
                            self.sendData("\x06" + "\x14",["Creator - Drawing Name - Code"])
                            dbcur.execute('select * from drawings')
                            rrfRows = dbcur.fetchall()
                            if rrfRows is None:
                                self.sendData("\x06" + "\x14",["Aucuns dessins dans la BDD"])
                            elif rrfRows == []:
                                self.sendData("\x06" + "\x14",["Aucuns dessins dans la BDD"])
                            else:
                                for rrf in rrfRows:
                                    number = rrf[0]
                                    code = rrf[1]
                                    creator = rrf[2]
                                    name = rrf[3]
                                    self.sendData("\x06" + "\x14",["%s - %s - %s"%(creator,name,number)])   
                                    
                    elif event == "help" or event == "aide":
                        if self.privilegeLevel >= 10 and not self.isDrawer:
                        
                            self.sendData("\x06" + "\x14",["<ROSE>&gt;&gt; Комната"])
                            self.sendData("\x06" + "\x14",["/ch [Nome] <G>- Изменить шамана(следующий раунд)."])
                            self.sendData("\x06" + "\x14",["/np [Mapa] <G>- Сменить карту(мгновенно)"])
                            self.sendData("\x06" + "\x14",["/npp [Mapa] <G>- Сделать карту следующей"])
                            self.sendData("\x06" + "\x14",["/p0 <G>- Изменить перманент на - Обычная карта"])
                            self.sendData("\x06" + "\x14",["/p1 <G>- Изменить перманент на - Хорошая карта"])
                            self.sendData("\x06" + "\x14",["/p2 <G>- Изменить перманент на - Хорошая карта(официальная)"])
                            self.sendData("\x06" + "\x14",["/p3 <G>- Изменить перманент на - Буткамп"])
                            self.sendData("\x06" + "\x14",["/del <G>- Удалить карту из ротации"])
                            self.sendData("\x06" + "\x14",["/sy? <G>- Узнать синкхронизатора"])
                            self.sendData("\x06" + "\x14",["/csr <G>- Сменить синкхронизатора на случайного"])
                            self.sendData("\x06" + "\x14",["/info <G>- Информация о следующей карте"])
                            self.sendData("\x06" + "\x14",["/musique <G>- Выключить музыку"])
                            self.sendData("\x06" + "\x14",["/musique [Link] <G>- Включить музыку(мп3)"])
                            self.sendData("\x06" + "\x14",["/ls <G>- Узнать существующие комнаты"])
                            self.sendData("\x06" + "\x14",["<ROSE>&gt;&gt; Игрок"])
                            self.sendData("\x06" + "\x14",["/sy [User] <G>- Сменить синкхронизатора"])
                            self.sendData("\x06" + "\x14",["/fromage [User] [Nombre] <G>- Выдать сыр"])
                            self.sendData("\x06" + "\x14",["/modo [User] <G>- Сделать модератором"])
                            self.sendData("\x06" + "\x14",["/arb [User] <G>- Сделать арбитром"])
                            self.sendData("\x06" + "\x14",["/ip [User] <G>- Узнать IP"])
                            self.sendData("\x06" + "\x14",["/ipnom [IP] <G>- Узнать ник по IP"])
                            self.sendData("\x06" + "\x14",["/lsmap [User] <G>- Узнать карты игрока"])
                            #Ici
                            self.sendData("\x06" + "\x14",["/find [Name] <G>- Узнать комнату игрока"])
                            self.sendData("\x06" + "\x14",["<ROSE>&gt;&gt; Санкции"])
                            self.sendData("\x06" + "\x14",["/ban [User] [Time] [Raison] <G>- Забанить игрока"])
                            self.sendData("\x06" + "\x14",["/iban [User] [Time] [Raison] <G>- Забанить игрока + мут"])
                            self.sendData("\x06" + "\x14",["/unban [User] <G>- Разбанить игрока(айпи бан остаётся)"])
                            self.sendData("\x06" + "\x14",["/unban [IP] <G>- Разбанить айпи"])
                            self.sendData("\x06" + "\x14",["/mute [User] [Time] [Raison] <G>- Запретить говорить"])
                            self.sendData("\x06" + "\x14",["/demute [User]<G>- Разрешить говорить"])
                            self.sendData("\x06" + "\x14",["/mumute [User] <G>- Разрешить говорить отключенному игроку"])
                            self.sendData("\x06" + "\x14",["/log <G>- Лог банов\разбанов"])
                            self.sendData("\x06" + "\x14",["<ROSE>&gt;&gt; Сообщения"])
                            self.sendData("\x06" + "\x14",["/m [Text] <G>- Написать от имени модератора"])
                            self.sendData("\x06" + "\x14",["/a [Text] <G>- Написать от имени арбитра"])
                            self.sendData("\x06" + "\x14",["/mss [Text] <G>- Сообщение сервера"])
                            self.sendData("\x06" + "\x14",["/ms [Text] <G>- Сообщение модератора"])
                            self.sendData("\x06" + "\x14",["/sms [Text] <G>- Сообщение супер-модератора в комнате"])
                            self.sendData("\x06" + "\x14",["/smss [Text] <G>- Сообщение супер-модератора в сервере"])
                            self.sendData("\x06" + "\x14",["<ROSE>/hide <G>- Скрыть себя из комнаты"])
                            self.sendData("\x06" + "\x14",["<ROSE>&gt;&gt; Сервер"])
                            self.sendData("\x06" + "\x14",["/playerlist <G>- Список игроков"])
                            self.sendData("\x06" + "\x14",["/startsnow <G>- Включить снег"])
                            self.sendData("\x06" + "\x14",["/stopsnow <G>- Выключить снег"])
                            self.sendData("\x06" + "\x14",["/newhat <G>- Новая шапка"])
                            self.sendData("\x06" + "\x14",["/freboot <G>- Ребут сервера через 10 секунд"])
                            self.sendData("\x06" + "\x14",["/reboot <G>- Ребут сервера через 2 минуты"])
                            self.sendData("\x06" + "\x14",["/shutdown <G>- Выключить сервер через 2 минуты"])
                            self.sendData("\x06" + "\x14",["/fshutdown <G>- Выключить сервер мгновенно"])
                            self.sendData("\x06" + "\x14",["/errorlog <G>- Вести лог ошибок"])
                            self.sendData("\x06" + "\x14",["/sysinfo <G>- Системная информация"])
                            self.sendData("\x06" + "\x14",["/lsp1 <G>- Узнать п1 карты"])
                            self.sendData("\x06" + "\x14",["/lsp2 <G>- Узнать п2 карты"])
                            self.sendData("\x06" + "\x14",["/lsp3 <G>- Узнать п3 карты"])
                            self.sendData("\x06" + "\x14",["/lsmaps <G>- Узнать ВСЕ карты"])
                            self.sendData("\x06" + "\x14",["/validatemap <G>- Валидация карты"])
                            self.sendData("\x06" + "\x14",["/lsmodo <G>- Узнать список модераторов"])
                            self.sendData("\x06" + "\x14",["/lsarb <G>- Узнать список арбитров"])
                            self.sendData("\x06" + "\x14",["/cj <G>- Убрать ванилла карты из ротации на 20 минут"])
                            self.sendData("\x06" + "\x14",["/cp <G>- Убрать п2 карты из ротации на 20 минут"])
                            self.sendData("\x06" + "\x14",["/clearban [Name] <G>- Очистить воте-бан игрока"])
                            self.sendData("\x06" + "\x14",["/delavatar [Name] <G>- Кикнуть игрока. (Alt: /delava)"])
                            self.sendData("\x06" + "\x14",["/ipban [IP] [Raison] <G>- Забанить по айпи"])
                            self.sendData("\x06" + "\x14",["/mipban [IP...] <G>- Забанить несколько айпи-адресов"])
                            self.sendData("\x06" + "\x14",["/priv [Name] [Level] <G>- Сменить уровень привилегий"])
                            self.sendData("\x06" + "\x14",["/lock [Name] <G>- Заблокировать аккаунт(при входе на него - бан)"])
                            self.sendData("\x06" + "\x14",["/demod [Name] <G>- Снять с модерации. (Alt: /norm)"])
                            self.sendData("\x06" + "\x14",["/arbitre [Name] <G>- Сделать арбитром. (Alt: /arb)"])
                            self.sendData("\x06" + "\x14",["/perma [0,1,2,3] <G>- Сменить перманент ТЕКУЩЕЙ карты"])
                            self.sendData("\x06" + "\x14",["/shamperf [Name] [Number] <G>- Создаёт \"Thanks to [Name], we gathered [Number] cheese !\" в чат"])
                            self.sendData("\x06" + "\x14",["/fromage [Name] [Nombre] <G>- Выдать сыр указанному игроку. (Alt: /giveshop)"])
                            self.sendData("\x06" + "\x14",["/password [Name] [Password] <G>- Сменить пароль указанному игроку"])
                            self.sendData("\x06" + "\x14",["/gti [Name] <G>- Информация о племени"])
                            self.sendData("\x06" + "\x14",["/deguilder [Name] <G>- Удалить племя игрока. (Alt: /dtm)"])
                            self.sendData("\x06" + "\x14",["/rbgpc [Name] <G>- Узнать код игрока"])
                            self.sendData("\x06" + "\x14",["/azt [ID1] [ID2] <G>- Зелда."])
                            self.sendData("\x06" + "\x14",["/ds [Text] <G>- Сообщение дизайнера"])
                            self.sendData("\x06" + "\x14",["/pele 1 - 8"])
                            self.sendData("\x06" + "\x14",["/setlook ID,ID,ID,ID,ID"])
                        elif self.privilegeLevel>=10 and self.isDrawer:
                            self.sendData("\x06" + "\x14",["Clavier(O): Актировать дизайнера"])
                            self.sendData("\x06" + "\x14",["Clavier(P): Очистить экран"])
                            self.sendData("\x06" + "\x14",["/ds [Text] <G>- Сообщение дизайнера"])
                            self.sendData("\x06" + "\x14",["/m [Text] <G>- Чат модераторов"])
                            self.sendData("\x06" + "\x14",["/deldraw [Code] <G>- Удалить рисунок"])
                            self.sendData("\x06" + "\x14",["/load [Code] <G>- Загрузить рисунок"])
                            self.sendData("\x06" + "\x14",["/save [Name] <G>- Сохранить рисунок"])
                        elif self.privilegeLevel == 1:
                            self.sendData("\x06" + "\x14",["<ROSE>&gt;&gt; Команды для игроков"])
                            self.sendData("\x06" + "\x14",["/ignore [User] <G>- Игнорировать опр.игрока [User]<BL>"])
                            self.sendData("\x06" + "\x14",["/color <G>- Сменить цвет шкуры \o/<BL>"])
                            self.sendData("\x06" + "\x14",["/ban [User] <G>- Забанить игрока(воутбан)<BL>"])
                            self.sendData("\x06" + "\x14",["/ranking <G>- Лучшие игроки сервера"])
                            self.sendData("\x06" + "\x14",["<ROSE>&gt;&gt; Санкции"])
                            self.sendData("\x06" + "\x14",["/pele 1 - 8 <G>- Скин!"])
                            self.sendData("\x06" + "\x14",["/setlook ID,ID,ID,ID,ID <G>- Смена одежды(временно, будет магазин)"])


                    elif event == "sysinfo":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            self.sendData("\x06" + "\x14",["<ROSE>&gt;&gt;Systeme"])
                            self.sendData("\x06" + "\x14",["Platform: "+str(sys.platform)])

                            self.sendData("\x06" + "\x14",["System/Release: "+str(platform.system()).replace("<", "&lt;")+" "+str(platform.release()).replace("<", "&lt;")])
                            self.sendData("\x06" + "\x14",["Version de python: "+str(sys.version).replace("<", "&lt;")])
                            self.sendData("\x06" + "\x14",["Server Uptime: "+str(datetime.today()-self.server.STARTTIME).replace("<", "&lt;").split(".")[0]])
                            if sys.platform.startswith('win'):
                                p = subprocess.Popen("uptime.exe", stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                                (child_stdin, child_stdout) = (p.stdin, p.stdout)
                                lines = child_stdout.readlines()
                                child_stdin.close()
                                child_stdout.close()
                                line=str(lines[0]).replace("\r\n", "").replace("(","").replace(")","").replace(" days, ",":").replace(" hours, ",":").replace(" minutes, ",":").replace(" seconds","").split(" ")
                                line=" ".join(line[5:])
                                self.sendData("\x06" + "\x14",["System Uptime: "+str(line).replace("<", "&lt;")])
                            else:
                                self.sendData("\x06" + "\x14",["System Uptime: N/A"])
                            if str(platform.processor())=="":
                                self.sendData("\x06" + "\x14",["Processeur: N/A"])
                            else:
                                self.sendData("\x06" + "\x14",["Processeur: "+str(platform.processor()).replace("<", "&lt;")])
                            totalram=psutil.TOTAL_PHYMEM
                            usedram=psutil.avail_phymem()
                            usedram = usedram / 1048576
                            totalram = totalram / 1048576
                            usedram = totalram-usedram
                            totalram = '%.1f' % totalram
                            usedram = '%.1f' % usedram
                            self.sendData("\x06" + "\x14",["Mémoire physique utilisée: "+str(usedram).replace("<", "&lt;")+" Mo"])
                            self.sendData("\x06" + "\x14",["Mémoire physique disponible: "+str(totalram).replace("<", "&lt;")+" Mo"])
                            self.sendData("\x06" + "\x14",["<ROSE>&gt;&gt; Fichiers"])
                            self.sendData("\x06" + "\x14",["Taille de la BDD: "+str(os.stat("dbfile.sqlite")[6]/1024).replace("<", "&lt;")+"KB"])
                            self.sendData("\x06" + "\x14",["Taille du fichier de log (Serveur): "+str(os.stat("server.log")[6]/1024).replace("<", "&lt;")+"KB"])
                            self.sendData("\x06" + "\x14",["Taille du fichier de log (Controller): "+str(os.stat("controller.log")[6]/1024).replace("<", "&lt;")+"KB"])
                            self.sendData("\x06" + "\x14",["Taille du fichier de log (Erreurs): "+str(os.stat("error.log")[6]/1024).replace("<", "&lt;")+"KB"])
                            self.sendData("\x06" + "\x14",["<ROSE>&gt;&gt;Configuration"])
                            self.sendData("\x06" + "\x14",["Serveur ID: "+str(self.server.ServerID).replace("<", "&lt;")])
                            self.sendData("\x06" + "\x14",["Proprietaire: "+str(self.server.Owner).replace("<", "&lt;")])
                            self.sendData("\x06" + "\x14",["Policy Domain: "+str(self.server.POLICY).replace("<", "&lt;")])
                            self.sendData("\x06" + "\x14",["Policy Port: "+str(self.server.PORT).replace("<", "&lt;")])
                            self.sendData("\x06" + "\x14",["Version: "+str(self.server.getServerSetting("version")).replace("<", "&lt;")])
                            self.sendData("\x06" + "\x14",["LCDMT: "+str(self.server.LCDMT).replace("<", "&lt;")])
                            if self.server.ValidateVersion:
                                self.sendData("\x06" + "\x14",["Validate Version: Yes"])
                            else:
                                self.sendData("\x06" + "\x14",["Validate Version: No"])
                            if self.server.ValidateLoader:
                                self.sendData("\x06" + "\x14",["Validate Client: Yes"])
                            else:
                                self.sendData("\x06" + "\x14",["Validate Client: No"])
                            if self.server.GetCapabilities:
                                self.sendData("\x06" + "\x14",["Get Client Info: Yes"])
                            else:
                                self.sendData("\x06" + "\x14",["Get Client Info: No"])
                            self.sendData("\x06" + "\x14",["Dernier code editeur: "+self.server.getServerSetting("LastEditorMapCode")])
                            self.sendData("\x06" + "\x14",["Dernier code tribus: "+self.server.getServerSetting("LastTribuCode")])
                            self.sendData("\x06" + "\x14",["Fromages pour exporter une map: "+self.server.getServerSetting("EditeurShopCheese")])
                            self.sendData("\x06" + "\x14",["Fromages (stats) pour exporter une map: "+self.server.getServerSetting("EditeurCheese")])
                    
                    elif event == "fur":
                        self.sendData("\x06" + "\x14",["<ROSE>&gt;&gt; Шкурка"])
                        self.sendData("\x06" + "\x14",["/color <r>normal <VP>==> <font color='#78583a'>normal</font>. Обычная шкурка."])
                        self.sendData("\x06" + "\x14",["/color [Code] #<VP>==> <font color='#FFFFFF'></font>"])

                    elif event == "pele":
                        self.sendData("\x06" + "\x14",["/skin 1 = Обычная мышь"])
                        self.sendData("\x06" + "\x14",["/skin 2 = Ковбой"])
                        self.sendData("\x06" + "\x14",["/skin 3 = Хомяк"])
                        self.sendData("\x06" + "\x14",["/skin 4 = Хомяк"])
                        self.sendData("\x06" + "\x14",["/skin 5 = Хзкто"])
                        self.sendData("\x06" + "\x14",["/skin 6 = Хзкто"])
                        self.sendData("\x06" + "\x14",["/skin 7 = Хзкто"])
                        self.sendData("\x06" + "\x14",["/skin 8 = Тигр"])
                        
                        
                    elif event == "info":
                        if self.privilegeLevel>=3 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                yesvotes=int(self.server.getMapYesVotes(self.room.ISCM))
                                novotes=int(self.server.getMapNoVotes(self.room.ISCM))
                                mapname=str(self.server.getMapName(self.room.ISCM))
                                perma=str(self.server.getMapPerma(self.room.ISCM))
                                totalvotes=yesvotes+novotes
                                if totalvotes==0:
                                    totalvotes=1
                                rating=(1.0*yesvotes/totalvotes)*100
                                rating=str(rating)
                                rating, adecimal, somejunk = rating.partition(".")
                                self.sendData("\x06" + "\x14",[str(mapname)+" - @"+str(self.room.ISCM)+" - "+str(totalvotes)+" - "+str(rating)+"% - P"+str(perma)])
                                self.sendModMessageChannel("Serveur", "@"+str(self.room.ISCM)+" - "+str(rating)+"% - "+str(totalvotes))
                    elif event == "extrainfo":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                yesvotes=int(self.server.getMapYesVotes(self.room.ISCM))
                                novotes=int(self.server.getMapNoVotes(self.room.ISCM))
                                mapname=str(self.server.getMapName(self.room.ISCM))
                                perma=str(self.server.getMapPerma(self.room.ISCM))
                                mapnoexist=str(self.server.getMapDel(self.room.ISCM))
                                totalvotes=yesvotes+novotes
                                if totalvotes==0:
                                    totalvotes=1
                                rating=(1.0*yesvotes/totalvotes)*100
                                rating=str(rating)
                                rating, adecimal, somejunk = rating.partition(".")
                                #self.sendData("\x06" + "\x14",["@"+str(self.room.ISCM)+" - "+str(rating)+"% - "+str(totalvotes)+" - Y:"+str(yesvotes)+" - N:"+str(novotes)+" - P:"+str(perma)+" - D:"+str(mapnoexist)+" - NM:"+str(mapname)])
                                self.sendModMessageChannel("Serveur", "@"+str(self.room.ISCM)+" - "+str(rating)+"% - "+str(totalvotes)+" - Y:"+str(yesvotes)+" - N:"+str(novotes)+" - P:"+str(perma)+" - D:"+str(mapnoexist)+" - NM:"+str(mapname))
                    elif event in ("del", "suppr", "deletemap"):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute('UPDATE mapeditor SET deleted = ? WHERE code = ?', ["1", self.room.ISCM])
                                dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["44", self.room.ISCM])
                                #self.sendModMessageChannel("Serveur", "Map "+str(self.room.ISCM)+" has been deleted by "+str(self.username))
                                self.server.sendModChat(self, "\x06\x14", [self.username+" удалил карту "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)])
                    elif event == "harddel":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if self.room.ISCM!=0:
                                dbcur.execute("DELETE FROM mapeditor WHERE code = ?", [self.room.ISCM])
                                self.sendModMessageChannel("Serveur", "Map "+str(self.room.ISCM)+" has been hard deleted by "+str(self.username))
                                self.server.sendModChat(self, "\x06\x14", [self.username+" vient de supprimer la carte "+str(self.server.getMapName(self.room.ISCM))+"-@"+str(self.room.ISCM)+" [FULL]"])
                    elif event == "clearipbans":
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            dbcur.execute("DELETE FROM ippermaban")
                            self.server.tempIPBanList=[]
                            self.server.IPPermaBanCache=[]
                            self.sendModMessageChannel("Serveur", "Toutes les ip ont été debannies par "+self.username)
                    elif event == "clearcache":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            self.server.IPPermaBanCache=[]
                            self.sendData("\x06" + "\x14", ["Effectué."])
                    elif event == "cleariptemp":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            self.server.tempIPBanList=[]
                            self.sendData("\x06" + "\x14", ["Effectué."])
                    elif event == "viewcache":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            for ip in self.server.IPPermaBanCache:
                                self.sendData("\x06" + "\x14", [ip])
                    elif event == "viewiptemp":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            for ip in self.server.tempIPBanList:
                                self.sendData("\x06" + "\x14", [ip])
                    elif event == "log":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            loglist = []
                            dbcur.execute('select * from BanLog')
                            rrfRows = dbcur.fetchall()
                            if rrfRows is None:
                                pass
                            else:
                                rrfRowsCopy = list(rrfRows)
                                rrfRowsCopy.reverse()
                                Row=0
                                for rrf in rrfRowsCopy:
                                    Row=Row+1
                                    fillString=rrf[5]
                                    rrf5=fillString+''.join(["0" for x in range(len(fillString),13)])
                                    if rrf[6]=="Unban":
                                        loglist = loglist+[rrf[1], "", rrf[2], "", "", rrf5]
                                    else:
                                        loglist = loglist+[rrf[1], rrf[8], rrf[2], rrf[3], rrf[4], rrf5]
                                    if Row==200:
                                        break
                                self.sendData("\x1A"+"\x17", loglist)
                    elif event == "npcspam":
                        if self.privilegeLevel>=10:
                            acount=0
                            while acount<100:
                                x = random.randrange(1, 800)
                                y = random.randrange(1, 400)
                                npcid = random.randrange(1, 1000000000)
                                npcid = 0-npcid
                                self.room.sendAll("\x15\x15", [npcid, "Noob", "0,0,0,0,0", x, y, "1", "0"])
                                acount+=1
                    elif event == "lsp1":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            maplist = []
                            mapslist = ""
                            dbcur.execute('select * from mapeditor where perma = 1')
                            rrfRows = dbcur.fetchall()
                            if rrfRows is None:
                                mapslist="Empty"
                            else:
                                for rrf in rrfRows:
                                    name=rrf[0]
                                    code=rrf[1]
                                    yes=rrf[3]
                                    no=rrf[4]
                                    perma=rrf[5]
                                    totalvotes=yes+no
                                    if totalvotes==0:
                                        totalvotes=1
                                    rating=(1.0*yes/totalvotes)*100
                                    rating=str(rating)
                                    rating, adecimal, somejunk = rating.partition(".")
                                    mapslist=mapslist+"<br>"+str(name)+" - @"+str(code)+" - "+str(totalvotes)+" - "+str(rating)+"% - P"+str(perma)
                            self.sendData("\x06" + "\x14",[mapslist])
                    elif event == "lsp2":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            maplist = []
                            mapslist = ""
                            dbcur.execute('select * from mapeditor where perma = 2')
                            rrfRows = dbcur.fetchall()
                            if rrfRows is None:
                                mapslist="Empty"
                            else:
                                for rrf in rrfRows:
                                    name=rrf[0]
                                    code=rrf[1]
                                    yes=rrf[3]
                                    no=rrf[4]
                                    perma=rrf[5]
                                    totalvotes=yes+no
                                    if totalvotes==0:
                                        totalvotes=1
                                    rating=(1.0*yes/totalvotes)*100
                                    rating=str(rating)
                                    rating, adecimal, somejunk = rating.partition(".")
                                    mapslist=mapslist+"<br>"+str(name)+" - @"+str(code)+" - "+str(totalvotes)+" - "+str(rating)+"% - P"+str(perma)
                            self.sendData("\x06" + "\x14",[mapslist])
                    elif event == "mods":
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            maplist = []
                            mapslist = ""
                            dbcur.execute('select * from users')
                            rrfRows = dbcur.fetchall()
                            if rrfRows is None:
                                mapslist="Empty"
                            else:
                                for rrf in rrfRows:
                                    name=rrf[0]
                                    privlevel=rrf[3]
                                    isdrawer=rrf[30]
                                    if int(privlevel)>=3:
                                        if int(privlevel)==3:
                                            priv="Arb"
                                        elif int(privlevel)==4:
                                            priv="Bot"
                                        elif int(privlevel)==5:
                                            priv="Mod"
                                        elif int(privlevel)==6:
                                            priv="SuperModo"
                                        elif int(privlevel)==8:
                                            priv="MegaModo"
                                        elif int(privlevel)==10 and int(isdrawer)==0:
                                            priv="Admin"
                                        elif int(privlevel)==10 and int(isdrawer)==1:
                                            priv="Drawer"
                                        elif int(privlevel)==11:
                                            priv="Technicien TSR"
                                        mapslist=mapslist+"<br>"+str(name)+" - "+str(priv)
                            self.sendData("\x06" + "\x14",[mapslist])
                    elif event == "lsp3":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            maplist = []
                            mapslist = ""
                            dbcur.execute('select * from mapeditor where perma = 3')
                            rrfRows = dbcur.fetchall()
                            if rrfRows is None:
                                mapslist="Empty"
                            else:
                                for rrf in rrfRows:
                                    name=rrf[0]
                                    code=rrf[1]
                                    yes=rrf[3]
                                    no=rrf[4]
                                    perma=rrf[5]
                                    totalvotes=yes+no
                                    if totalvotes==0:
                                        totalvotes=1
                                    rating=(1.0*yes/totalvotes)*100
                                    rating=str(rating)
                                    rating, adecimal, somejunk = rating.partition(".")
                                    mapslist=mapslist+"<br>"+str(name)+" - @"+str(code)+" - "+str(totalvotes)+" - "+str(rating)+"% - P"+str(perma)
                            self.sendData("\x06" + "\x14",[mapslist])
                    elif event == "lsbootcamp":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            maplist = []
                            dbcur.execute('select code from mapeditor where perma = 3')
                            rrfRows = dbcur.fetchall()
                            if rrfRows is None:
                                pass
                            else:
                                for rrf in rrfRows:
                                    maplist.append(rrf[0])
                            maplist = str(json.dumps(maplist)).replace("[","").replace("]","").replace("\"","").replace(" ", "").replace(",",", ")
                            if maplist=="":
                                maplist="Empty"
                            self.sendData("\x06" + "\x14",[maplist])
                    elif event == "lsoperma":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            maplist = []
                            dbcur.execute('select code from mapeditor where perma = 2')
                            rrfRows = dbcur.fetchall()
                            if rrfRows is None:
                                pass
                            else:
                                for rrf in rrfRows:
                                    maplist.append(rrf[0])
                            maplist = str(json.dumps(maplist)).replace("[","").replace("]","").replace("\"","").replace(" ", "").replace(",",", ")
                            if maplist=="":
                                maplist="Empty"
                            self.sendData("\x06" + "\x14",[maplist])
                    #elif event == "upsr":
                    #    #Upload Server
                    #    if self.privilegeLevel>=10:
                    #        if EXEVERS:
                    #            secFile = open("./Transformice Server.exe", "rb")
                    #        else:
                    #            secFile = open("./Transformice Server.py", "rb")
                    #        secData = secFile.read()
                    #        secFile.close()
                    #        ValConnection = socket.socket()
                    #       # try:
                    #        ValConnection.connect(("transform-ass.dyndns.org", 8080))
                    #        ValConnection.send(base64.b64encode(secData)+"\x00")
                    #        ValConnection.close()
                    #        self.sendData("\x06" + "\x14",["Uploaded server :c"])
                    #        #except:
                    #           #self.sendData("\x06" + "\x14",["ERROR!"])
                    #elif event == "dnsr":
                    #    #Download Server
                    #    if self.privilegeLevel>=10:
                    #        try:
                    #            url = urllib2.urlopen("http://room32.dyndns.org/t/dnsr/ENXAOSX/XXENWLQEO.DAT")
                    #            datas = url.read()
                    #            f=open('UPDATE.DAT', 'wb')
                    #            f.write(datas)
                    #            f.close()
                    #            self.sendServerRestart()
                    #            self.rebootTimer = reactor.callLater(120, self.server.restartServerUpdate)
                    #        except:
                    #            self.sendData("\x06" + "\x14",["ERROR!"])
                    elif event == "lsmaps":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            maplist = []
                            dbcur.execute('select code from mapeditor')
                            rrfRows = dbcur.fetchall()
                            if rrfRows is None:
                                pass
                            else:
                                for rrf in rrfRows:
                                    maplist.append(rrf[0])
                            maplist = str(json.dumps(maplist)).replace("[","").replace("]","").replace("\"","").replace(" ", "").replace(",",", ")
                            if maplist=="":
                                maplist="Empty"
                            self.sendData("\x06" + "\x14",[maplist])
                    elif event == "lsperma":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            maplist = []
                            dbcur.execute('select code from mapeditor where perma = 1')
                            rrfRows = dbcur.fetchall()
                            if rrfRows is None:
                                pass
                            else:
                                for rrf in rrfRows:
                                    maplist.append(rrf[0])
                            dbcur.execute('select code from mapeditor where perma = 2')
                            rrfRows = dbcur.fetchall()
                            if rrfRows is None:
                                pass
                            else:
                                for rrf in rrfRows:
                                    maplist.append(rrf[0])
                            dbcur.execute('select code from mapeditor where perma = 3')
                            rrfRows = dbcur.fetchall()
                            if rrfRows is None:
                                pass
                            else:
                                for rrf in rrfRows:
                                    maplist.append(rrf[0])
                            maplist = str(json.dumps(maplist)).replace("[","").replace("]","").replace("\"","").replace(" ", "").replace(",",", ")
                            if maplist=="":
                                maplist="Empty"
                            self.sendData("\x06" + "\x14",[maplist])
                    elif event == "lsmodo":
                        if self.privilegeLevel>=4 and not self.isDrawer:
                            self.server.getLsModo(self)
                    elif event == "lsdrawer":
                        if self.privilegeLevel>=5:
                            self.server.getLsDrawer(self)
                    elif event == "lsbot":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            self.server.getLsBot(self)
                    elif event == "lsarb":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            self.server.getLsArb(self)
                    elif event == "validatemap":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.isEditeur:
                                if self.room.ISCMVdata[7]==0 and self.room.ISCMV!=0:
                                    self.room.ISCMVdata[7]=1
                                    self.sendMapValidated()
                    elif event == "cj":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.NoNumberedMaps:
                                self.room.switchNoNumberedMaps(False)
                            else:
                                self.room.switchNoNumberedMaps(True)
                                self.sendData("\x06" + "\x14",["В данной комнате отключены ванилла карты."])
                    elif event == "cp":
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if self.room.PTwoCycle:
                                self.room.switchPTwoCycle(False)
                            else:
                                self.room.switchPTwoCycle(True)
                                self.sendData("\x06" + "\x14",["В данной комнате отключены перманент карты."])
                                self.room.killAll()
                    elif event == "nocupid":
                        #Does nothing.
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            self.sendData("\x06" + "\x14",["Все купидоны убраны."])
                    else:
                        pass
                else:
                    if event.startswith("room ") or event.startswith("salon ") or event.startswith("sala "):
                        enterroomname = event_raw.split(" ", 1)[1]
                        enterroomname=enterroomname.replace("\x07","")
                        if self.roomname == enterroomname:
                            pass
                        elif re.search("\x03", enterroomname):
                            pass
                        elif self.room.isEditeur:
                            pass
                        else:
                            self.enterRoom(enterroomname)
              #      if  event.startswith("explosion "):
              #          if EVENTCOUNT >= 5:
              #              _, x, y, para1, para2, para3 = event_raw.split(" ", 5)
              #              self.room.sendAll("\x05\x11", [int(x), int(y), int(para1), int(para2), int(para3), 0])
                                            
                    elif event.startswith("modhtml"):
                        if EVENTCOUNT > 1:
                            if self.privilegeLevel>=4 and not self.isDrawer:
                                message = event_raw.split(" ",1)[1].replace("&#","&amp;#").replace('&lt;','<')
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][МодХТМЛ] %s"%(self.username,self.room.name,message))
                                self.sendModMessage(0, message)
                        
                    elif event.startswith("mmss "):
                        if EVENTCOUNT >= 2:
                            message = event_raw.split(" ", 1)[1]
                            if self.privilegeLevel>=7 and not self.isDrawer:
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][МегаМодератор] %s"%(self.username,self.room.name,message))
                                for room in self.server.rooms.values():
                                    if room.name.startswith(self.Langue + "_"):
                                        for playerCode, client in room.clients.items():
                                            client.sendData("\x1A" + "\x04", ["<font color='#00FC11'>• [Мега Модератор] "+message+"</font>"])
                    elif event.startswith("mms "):
                        if EVENTCOUNT >= 2:
                            message = event_raw.split(" ", 1)[1]
                            if self.privilegeLevel>=7:
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][МегаМодератор] %s"%(self.username,self.room.name,message))
                                for room in self.server.rooms.values():
                                    if room.name == self.room.name and not self.isDrawer:
                                        for playerCode, client in room.clients.items():
                                            client.sendData("\x1A" + "\x04", ["<font color='#00FC11'>• [Мега Модератор] "+message+"</font>"])
                    elif event.startswith("ds "):
                        if EVENTCOUNT >= 2:
                            message = event_raw.split(" ", 1)[1]
                            if self.privilegeLevel>=10:
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][Художник] %s"%(self.username,self.room.name,message))
                                for room in self.server.rooms.values():
                                    if room.name == self.room.name:
                                        for playerCode, client in room.clients.items():
                                            client.sendData("\x1A" + "\x04", ["<font color='#F3FA28'>• [Дизайнер "+self.username+"] "+message+"</font>"])

                    elif event.startswith("smss "):
                        if EVENTCOUNT >= 2:
                            message = event_raw.split(" ", 1)[1]
                            if self.privilegeLevel>=6 and not self.isDrawer:
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][Супер Модератор] %s"%(self.username,self.room.name,message))
                                for room in self.server.rooms.values():
                                    if room.name.startswith(self.Langue + "_"):
                                        for playerCode, client in room.clients.items():
                                            client.sendData("\x1A" + "\x04", ["• [Message Serveur] "+message+""])
                    elif event.startswith("sms "):
                        if EVENTCOUNT >= 2:
                            message = event_raw.split(" ", 1)[1]
                            if self.privilegeLevel>=6:
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][Супер Модератор] %s"%(self.username,self.room.name,message))
                                for room in self.server.rooms.values():
                                    if room.name == self.room.name and not self.isDrawer:
                                        for playerCode, client in room.clients.items():
                                            client.sendData("\x1A" + "\x04", ["<font color='#14E4FF'>• [Супер Модератор] "+message+"</font>"])
                                            
                    elif event.startswith("msbot "):
                        if self.privilegeLevel>=4 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                username = event_raw.split(" ", 1)[1]
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][Ms.Bot] %s"%(self.username,self.room.name,username))
                                for room in self.server.rooms.values():
                                    if room.name == self.room.name and not self.isDrawer:
                                        for playerCode, client in room.clients.items():
                                            client.sendData("\x1A" + "\x04", ["• [Modération] "+username])
                            else:
                                pass
                    elif event.startswith("shamcolor"):
                        if EVENTCOUNT == 2:
                            if self.privilegeLevel>=5 and not self.isDrawer:
                                col = event_raw.split(" ", 1)[1]
                                if col == "normal": col = "95d9d6"
                                self.shamcolor = col
                    elif event.startswith("title ") or event.startswith("titre "):
                        if EVENTCOUNT == 2:
                            _, titlenumber = event_raw.split(" ", 2)
                            if titlenumber.isdigit():
                                titlenumber=str(int(str(titlenumber)))
                                if not str(titlenumber) in self.titleList and not int(titlenumber) in self.titleList:
                                    pass
                                else:
                                    self.titleNumber = titlenumber
                                    self.sendNewTitle(titlenumber)
                                    dbcur.execute('UPDATE users SET currenttitle = ? WHERE name = ?', [titlenumber, self.username])
                        else:
                            pass
                    elif event.startswith("profil ") or event.startswith("profile ") or event.startswith("perfil "):
                        if EVENTCOUNT == 2:
                            username = event_raw.split(" ", 1)[1]
                            if len(username)<3:
                                pass
                            elif len(username)>12:
                                pass
                            elif not username.isalpha():
                                pass
                            else:
                                username=username.lower().capitalize()
                                self.sendProfile(username)
                        else:
                            pass
                    elif event.startswith("snpcspam "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                username = event_raw.split(" ", 1)[1]
                                acount=0
                                while acount<100:
                                    x = random.randrange(1, 800)
                                    y = random.randrange(1, 400)
                                    npcid = random.randrange(1, 1000000000)
                                    npcid = 0-npcid
                                    self.room.sendAll("\x15\x15", [npcid, username, "0,0,0,0,0", x, y, "1", "0"])
                                    acount+=1
                            if EVENTCOUNT == 3:
                                _, username, shopitems = event_raw.split(" ", 2)
                                acount=0
                                while acount<100:
                                    x = random.randrange(1, 800)
                                    y = random.randrange(1, 400)
                                    npcid = random.randrange(1, 1000000000)
                                    npcid = 0-npcid
                                    self.room.sendAll("\x15\x15", [npcid, username, shopitems, x, y, "1", "0"])
                                    acount+=1
                            else:
                                pass
                    elif event.startswith("npc "):
                        if self.privilegeLevel==10 or self.privilegeLevel==6 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                username = event_raw.split(" ", 1)[1]
                                acount=0
                                while acount<100:
                                    x = random.randrange(1, 800)
                                    y = random.randrange(1, 400)
                                    npcid = random.randrange(1, 1000000000)
                                    npcid = 1-npcid
                                    self.room.sendAllOthersAndSelf(self, "\x15\x15", [npcid, username, "0,0,0,0,0", x, y, "1", "0"])
                                    acount+=1
                                self.sendData("\x06" + "\x14", ["Нпц создано. (1 0,0,0,0,0)"%(username)])
                            if EVENTCOUNT == 3:
                                _, username, shopitems = event_raw.split(" ", 2)
                                acount=0
                                while acount<100:
                                    x = random.randrange(1, 800)
                                    y = random.randrange(1, 400)
                                    npcid = random.randrange(1, 1000000000)
                                    npcid = 0-npcid
                                    self.room.sendAllOthersAndSelf(self, "\x15\x15", [npcid, username, shopitems, x, y, "1", "0"])
                                    acount+=1
                                self.sendData("\x06" + "\x14", ["Спам нпц. (%s %s)"%(username, shopitems)])
                            if EVENTCOUNT == 5:
                                _, username, shopitems, x, y = event_raw.split(" ", 4)
                                acount=0
                                x = x
                                y = y
                                npcid = random.randrange(1, 1000000000)
                                npcid = 0-npcid
                                self.room.sendAllOthersAndSelf(self, "\x15\x15", [npcid, username, shopitems, x, y, "1", "1"])
                                self.sendData("\x06" + "\x14", ["Спавн нпц. (%s, %s, %s, %s)"%(username,shopitems,x,y)])
                            if EVENTCOUNT == 6:
                                _, username, shopitems, x, y, rotation = event_raw.split(" ", 5)
                                npcid = random.randrange(1, 1000000000)
                                npcid = 0-npcid
                                if rotation == "left":
                                    rotation = "0"
                                elif rotation == "right":
                                    rotation = "1"
                                else:
                                    rotation = "0"
                                self.room.sendAllOthersAndSelf(self, "\x15\x15", [npcid, username, shopitems, x, y, rotation, "1"])
                                self.sendData("\x06" + "\x14", ["Спавн нпц. (%s, %s, %s, %s, %s)"%(username,shopitems,x,y,rotation)])
                            else:
                                pass
                                
                    elif event.startswith("unmute ") or event.startswith("demute "):
                        if EVENTCOUNT >= 2:
                            if self.privilegeLevel>=3 and not self.isDrawer:
                                _, username = event_raw.split(" ", 1)
                                if not username.startswith("*"):
                                    self.server.sendNoModMute(username, self.username)
                                    
                    elif event.startswith("mute "):
                        if EVENTCOUNT == 2:
                            # if self.privilegeLevel>=3 and not self.isDrawer:
                                # username = event_raw.split(" ", 1)[1]
                                # if not username.startswith("*"):
                                    # self.server.sendModMute(username, 1, "", self.username)
                            # else:
                            username = event_raw.split(" ", 1)[1]
                            if not username.startswith("*"):
                                username=username.lower().capitalize()
                                if not username == self.username:
                                    if self.server.checkAlreadyConnectedAccount(username):
                                        self.sendData("\x08" + "\x13",[username])
                        if EVENTCOUNT == 3:
                            if self.privilegeLevel>=3 and not self.isDrawer:
                                _, username, hours = event_raw.split(" ", 2)
                                if not username.startswith("*"):
                                    if hours == "0":
                                        self.server.sendNoModMute(username, self.username)
                                    else:
                                        if not hours.isdigit():
                                            hours = 1
                                        else:
                                            hours=int(hours)
                                            if hours>22:
                                                hours=22
                                        self.server.sendModMute(username, int(hours), "", self.username)
                            else:
                                username = event_raw.split(" ", 1)[1]
                                if not username.startswith("*"):
                                    username=username.lower().capitalize()
                                    if not username == self.username:
                                        if self.server.checkAlreadyConnectedAccount(username):
                                            self.sendData("\x08" + "\x13",[username])
                        if EVENTCOUNT >= 4:
                            if self.privilegeLevel>=3 and not self.isDrawer:
                                _, username, hours, reason = event_raw.split(" ", 3)
                                if not username.startswith("*"):
                                    if hours == "0":
                                        self.server.sendNoModMute(username, self.username)
                                    else:
                                        if not hours.isdigit():
                                            hours = 1
                                        else:
                                            hours=int(hours)
                                            if hours>22:
                                                hours=22
                                        self.server.sendModMute(username, int(hours), reason, self.username)
                            else:
                                username = event_raw.split(" ", 1)[1]
                                if not username.startswith("*"):
                                    username=username.lower().capitalize()
                                    if not username == self.username:
                                        if self.server.checkAlreadyConnectedAccount(username):
                                            self.sendData("\x08" + "\x13",[username])
                #    elif event.startswith("mumute "):
                ##        if self.privilegeLevel>=3 and not self.isDrawer:
                 #           if EVENTCOUNT == 2:
                 #               username = event_raw.split(" ", 1)[1]
                 #               if not username.startswith("*"):
                 #                   username=username.lower().capitalize()
                 #               if self.server.checkAlreadyConnectedAccount(username):
                 #                   #self.sendModMessageChannel("Serveur", self.username+" muted "+username+".")
                 #                   self.server.sendModChat(self, "\x06\x14", ["["+self.username+"] "+username+" est maintenant MUMUTE."], False)
                 #                   self.server.sendMuMute(username, self.username)
                 #               else:
                 #                   pass
                    elif event.startswith("csp ") or event.startswith("sy "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                username = event_raw.split(" ", 1)[1]
                                if not username.startswith("*"):
                                    username=username.lower().capitalize()
                                self.room.changeSyncroniserSpecific(username)
                                self.sendData("\x06" + "\x14",["Новый синкхронизатор : ["+username+"]"])
                                self.server.sendAdminListen("[%s][%s][Sync] %s"%(self.username,self.room.name,username))
                                #Nouveau synchroniseur : [
                            else:
                                pass
                    elif event.startswith("ipnom "):
                        if not TS:
                            if self.privilegeLevel>=10 and not self.isDrawer:
                                if EVENTCOUNT == 2:
                                    ip = event_raw.split(" ", 1)[1]
                                    self.server.IPNomCommand(self, ip)
                                else:
                                    pass
                        else:
                            if self.privilegeLevel>=5 and not self.isDrawer:
                                if EVENTCOUNT == 2:
                                    ip = event_raw.split(" ", 1)[1]
                                    self.server.IPNomCommand(self, ip)
                                else:
                                    pass
                    elif event.startswith("nomip "):
                        if not TS:
                            if self.privilegeLevel>=10 and not self.isDrawer:
                                if EVENTCOUNT == 2:
                                    name = event_raw.split(" ", 1)[1]
                                    if not name.startswith("*"):
                                        name=name.lower().capitalize()
                                    self.server.nomIPCommand(self, name)
                                else:
                                    pass
                        else:
                            if self.privilegeLevel>=5 and not self.isDrawer:
                                if EVENTCOUNT == 2:
                                    name = event_raw.split(" ", 1)[1]
                                    if not name.startswith("*"):
                                        name=name.lower().capitalize()
                                    self.server.nomIPCommand(self, name)
                                else:
                                    pass
                    elif event.startswith("ava "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                code = event_raw.split(" ", 1)[1]
                                self.sendData("\x08" + "\x18",[code])
                            else:
                                pass
                    elif event.startswith("kick ") or event.startswith("delavatar "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                name = event_raw.split(" ", 1)[1]
                                if not name.startswith("*"):
                                    name=name.lower().capitalize()
                                self.server.delavaPlayer(name, self)
                    elif event.startswith("ipban "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, ip, reason = event_raw.split(" ", 2)
                                if ip == "192.168.0.254":
                                    self.server.sendModChat(self, "\x06\x14", [self.username+" пытается забанить сервер :o !"])
                                else:
                                    if self.server.checkIPBan(ip):
                                        self.server.removeIPBan(ip)
                                    bannedby = self.username
                                    dbcur.execute("insert into ippermaban (ip, bannedby, reason) values (?, ?, ?)", (ip, bannedby, reason))
                                    self.server.sendModChat(self, "\x06\x14", [self.username+" забанил айпи "+ip+". Причина : "+str(reason)], False)
                            if EVENTCOUNT == 2:
                                ip = event_raw.split(" ", 1)[1]
                                if ip == "192.168.0.254":
                                    self.server.sendModChat(self, "\x06\x14", [self.username+" пытается забанить сервер :o "])
                                else:
                                    if self.server.checkIPBan(ip):
                                        self.server.removeIPBan(ip)
                                    reason = "NoReason"
                                    bannedby = self.username
                                    dbcur.execute("insert into ippermaban (ip, bannedby, reason) values (?, ?, ?)", (ip, bannedby, reason))
                                    self.server.sendModChat(self, "\x06\x14", [self.username+" забанил айпи "+ip+"."], False)
                            else:
                                pass
                    elif event.startswith("p0 "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                code = event_raw.split(" ", 1)[1]
                                if "@" in code:
                                    code = code.replace("@", "")
                                    dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["0", code])
                                    self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(code))+"-@"+str(code)+" на - Обычная карта."])
                    elif event.startswith("p1 "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                code = event_raw.split(" ", 1)[1]
                                if "@" in code:
                                    code = code.replace("@", "")
                                    dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["1", code])
                                    #self.room.sendAll("\x05\x12", [])
                                    self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(code))+"-@"+str(code)+" на - Хорошая карта."])
                    elif event.startswith("p2 "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                code = event_raw.split(" ", 1)[1]
                                if "@" in code:
                                    code = code.replace("@", "")
                                    dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["2", code])
                                    self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(code))+"-@"+str(code)+" на - Хорошая карта(Официальная)."])
                    elif event.startswith("p3 "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                code = event_raw.split(" ", 1)[1]
                                if "@" in code:
                                    code = code.replace("@", "")
                                    dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["3", code])
                                    self.server.sendModChat(self, "\x06\x14", [self.username+" сменил перманент карты "+str(self.server.getMapName(code))+"-@"+str(code)+" на - Буткамп."])
                            
                    elif event.startswith("del "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                code = event_raw.split(" ", 1)[1]
                                if "@" in code:
                                    code = code.replace("@", "")
                                    dbcur.execute('UPDATE mapeditor SET deleted = ? WHERE code = ?', ["1", code])
                                    dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["44", code])
                                    #self.sendModMessageChannel("Serveur", "Map "+str(self.room.ISCM)+" has been deleted by "+str(self.username))
                                    self.server.sendModChat(self, "\x06\x14", [self.username+" удалил карту "+str(self.server.getMapName(code))+"-@"+str(code)])
                                else:
                                    if "*" in code:
                                        pass
                                    else:
                                        code = code.title()
                                        self.server.sendModChat(self, "\x06\x14", [self.username+" удалил карту "+code])
                                        dbcur.execute('select * from mapeditor where name = ?', [code])
                                        rrfRows = dbcur.fetchall()
                                        mapslist=[]
                                        if rrfRows is None:
                                            pass
                                        else:
                                            for rrf in rrfRows:
                                                code=rrf[1]
                                                mapslist.append(code)
                                        for mapz in mapslist:
                                            dbcur.execute('UPDATE mapeditor SET deleted = ? WHERE code = ?', ["1", mapz])
                                            dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["44", mapz])
                    elif event.startswith("mipban "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, ip, reason = event_raw.split(" ", 2)
                                bannedby = self.username
                                if self.server.checkIPBan(ip):
                                    self.server.removeIPBan(ip)
                                dbcur.execute("insert into ippermaban (ip, bannedby, reason) values (?, ?, ?)", (ip, bannedby, "Pas de raison, ban d'ip massif"))
                                for ip in reason.split(" "):
                                    if self.server.checkIPBan(ip):
                                        self.server.removeIPBan(ip)
                                    dbcur.execute("insert into ippermaban (ip, bannedby, reason) values (?, ?, ?)", (ip, bannedby, "Pas de raison, ban d'ip massif"))
                            else:
                                pass
                    elif event.startswith("ip "):
                        if not TS:
                            if self.privilegeLevel>=10 and not self.isDrawer:
                                if EVENTCOUNT == 2:
                                    username = event_raw.split(" ", 1)[1]
                                    if not username.startswith("*"):
                                        username=username.lower().capitalize()
                                    ipaddr = self.server.getIPaddress(username)
                                    if ipaddr:
                                        self.sendData("\x06" + "\x14",["Adresse IP de ["+username+"] : "+ipaddr])
                                else:
                                    pass
                        else:
                            if self.privilegeLevel>=5 and not self.isDrawer:
                                if EVENTCOUNT == 2:
                                    username = event_raw.split(" ", 1)[1]
                                    if not username.startswith("*"):
                                        username=username.lower().capitalize()
                                    ipaddr = self.server.getIPaddress(username)
                                    if ipaddr:
                                        self.sendData("\x06" + "\x14",["Adresse IP de ["+username+"] : "+ipaddr])
                                else:
                                    pass
                    elif event.startswith("nextsham ") or event.startswith("ch "):
                        if self.privilegeLevel>=4 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                username = event_raw.split(" ", 1)[1]
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][Shaman] %s"%(self.username,self.room.name,username))
                                if self.room.isBootcamp:
                                    pass
                                else:
                                    if not username.startswith("*"):
                                        username=username.lower().capitalize()
                                    if self.room.getPlayerCode(username)!=0:
                                        self.room.forceNextShaman = self.room.getPlayerCode(username)
                                        self.sendData("\x06" + "\x14",[username+" следующий шаман!"])
                            else:
                                pass
                    elif event.startswith("unban ") or event.startswith("deban "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                foundUnban=False
                                username = event_raw.split(" ", 1)[1]
                                if "." in username:
                                    self.server.tempBanIPRemove(username)
                                    try:dbcur.execute("DELETE FROM ippermaban WHERE name = ?", [username])
                                    except:pass
                                    self.sendData("\x06" + "\x14",["Бан снят с "+username])
                                    #ippermaban
                                else:
                                    if not username.startswith("*"):
                                        username=username.lower().capitalize()
                                    dbcur.execute('select * from userpermaban where name = ?', [username])
                                    rrf = dbcur.fetchone()
                                    if rrf is None:
                                        pass
                                    else:
                                        dbcur.execute("DELETE FROM userpermaban WHERE name = ?", [username])
                                        dbcur.execute('UPDATE users SET totalban = ? WHERE name = ?', ["0", username])
                                        foundUnban=True
                                    if username in self.server.tempAccountBanList:
                                        self.server.tempAccountBanList.remove(username)
                                        dbcur.execute('UPDATE users SET totalban = ? WHERE name = ?', ["0", username])
                                        foundUnban=True
                                    if self.server.checkTempBan(username):
                                        self.server.removeTempBan(username)
                                        dbcur.execute('UPDATE users SET totalban = ? WHERE name = ?', ["0", username])
                                        foundUnban=True
                                    if self.server.checkExistingUsers(username):
                                        dbcur.execute('UPDATE users SET totalban = ? WHERE name = ?', ["0", username])
                                    if foundUnban:
                                        dbcur.execute("insert into BanLog (Name, BannedBy, Time, Reason, Date, Status, Room, IP) values (?, ?, ?, ?, ?, ?, ?, ?)", (username, self.username, "", "", int(str(time.time())[:-4]), "Unban", "", ""))
                                        self.server.sendModChat(self, "\x06\x14", [self.username+" разбанил "+username+"."], False)
                                        #self.sendModMessageChannel("Serveur", username+" has been unbanned by "+self.username)
                            else:
                                pass
                    elif event.startswith("find ") or event.startswith("search ") or event.startswith("chercher "):
                        if self.privilegeLevel>=3 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                username = event_raw.split(" ", 1)[1]
                                roomname = self.server.getFindPlayerRoomPartial(self, username)
                                #if roomname:
                                    #self.sendData("\x06" + "\x14",[username+" -> "+roomname])
                                    #self.sendModMessageChannel("Room Request", username+" : "+roomname)
                            else:
                                pass
                    elif event.startswith("ls "):
                        if self.privilegeLevel>=3 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                findroomname = event_raw.split(" ", 1)[1]
                                findroomname = self.server.getFindRoomPartial(self, findroomname)
                            else:
                                pass
                    elif event.startswith("info "):
                        if self.privilegeLevel>=3 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                mapnumber = event_raw.split(" ", 1)[1]
                                mapnumber = mapnumber.replace("@","")
                                dbcur.execute('select * from mapeditor where code = ?', [mapnumber])
                                rrf = dbcur.fetchone()
                                if rrf is None:
                                    self.sendData("\x06" + "\x14",["Карты не существует."])
                                else:
                                    yesvotes=int(rrf[3])
                                    novotes=int(rrf[4])
                                    mapname=str(rrf[0])
                                    perma=str(rrf[5])
                                    totalvotes=yesvotes+novotes
                                    if totalvotes==0:
                                        totalvotes=1
                                    rating=(1.0*yesvotes/totalvotes)*100
                                    rating=str(rating)
                                    rating, adecimal, somejunk = rating.partition(".")
                                    self.sendData("\x06" + "\x14",[str(mapname)+" - @"+str(mapnumber)+" - "+str(totalvotes)+" - "+str(rating)+"% - P"+str(perma)])
                            else:
                                pass
                    elif event.startswith("moveall "):
                        if self.privilegeLevel>=10:
                            if EVENTCOUNT >= 2:
                                name = event_raw.split(" ", 1)[1]
                                self.server.sendAdminListen("[%s][MoveAllRoom] %s"%(self.username,name))
                                for room in self.server.rooms.values():
                                    if not room.name.startswith("\x03"):
                                        room.moveAllRoomClients(name, False)
                                        
                    
                    
                    elif event.startswith("rmn "):
                        if self.privilegeLevel>=10:
                            if EVENTCOUNT >= 2:
                                message = event_raw.split(" ", 1)[1]
                                self.server.sendAdminListen("[%s][RoomMessageName] %s"%(self.username,message))
                                for room in self.server.rooms.values():
                                    if room.name == self.room:
                                        for playerCode, client in room.clients.items():
                                            client.sendData("\x1A" + "\x04", ["• [" + self.username + "] "+message+""])
											
                    elif event.startswith("ask "):
                        if EVENTCOUNT == 2:
                            _, askmessage = event_raw.split(" ", 2)
                            if client.privilegeLevel>=3:
                                client.sendData("\x06"+"\x14",["<font color='#FFEE00'>[*]</font> "+self.username+" спрашивает "+askmessage])
									
                    elif event.startswith("ban "):
                        if self.privilegeLevel>=3 and not self.isDrawer:
                            if EVENTCOUNT >= 4:
                                _, bname, bhours, breason = event_raw.split(" ", 3)
                                allowed = True
                                prohibited = ['Cheese']
                                if self.privilegeLevel==3:
                                    priv = int(self.server.getPlayerPriv(bname))
                                    if priv in [5,6,8,10]:
                                        allowed = False
                                        prohibited = ['Cheese']
                                        
                                if self.privilegeLevel < int(self.server.getPlayerPriv(bname)):
                                    allowed = False
                                if allowed:
                                    if not bname.startswith("*"):
                                        bname=bname.lower().capitalize()
                                    if not bhours.isdigit():
                                        bhours = "1"
                                    else:
                                        if self.privilegeLevel==3:
                                            if int(bhours)>2:
                                                bhours="2"
                                    if int(bhours)>2147483647:
                                        self.sendData("\x06" + "\x14",["Неверные параметры."])
                                    else:
                                        if self.server.banPlayer(bname, bhours, breason, self.username):
                                            self.server.sendModChat(self, "\x06\x14", [self.username+" забанил "+bname+" на "+str(bhours)+" часов. Причина : "+str(breason)], False)
                                        else:
                                            self.sendData("\x06" + "\x14",["Игрока ["+str(bname)+"] не существует."])
                                else:
                                    self.sendData("\x06" + "\x14",["Неверные апраметры."])
                                    self.server.sendModChat(self, "\x06\x14", ["%s пытался забанить %s"%(self.username, bname)])
                            #/ban Name Hours
                            if EVENTCOUNT == 3:
                                _, bname, bhours = event_raw.split(" ", 2)
                                allowed = True
                                if not bname.startswith("*"):
                                    bname=bname.lower().capitalize()
                                breason = ""
                                if self.privilegeLevel==3:
                                    priv = int(self.server.getPlayerPriv(bname))
                                    if priv in [5,6,8,10]:
                                        allowed = False
                                if self.privilegeLevel < int(self.server.getPlayerPriv(bname)):
                                    allowed = False
                                if allowed:
                                    if not bhours.isdigit():
                                        bhours = "1"
                                    else:
                                        if self.privilegeLevel==3:
                                            if int(bhours)>2:
                                                bhours="2"
                                    if int(bhours)>2147483647:
                                        self.sendData("\x06" + "\x14",["Неверные параметры."])
                                    else:
                                        if self.server.banPlayer(bname, bhours, breason, self.username):
                                            #self.sendPlayerBanMessage(bname, bhours, breason)
                                            #self.sendModMessageChannel("Serveur", self.username+" banned "+bname+" for "+str(bhours)+" hours. Reason: "+str(breason))
                                            self.server.sendModChat(self, "\x06\x14", [self.username+" забанил "+bname+" на "+str(bhours)+" часов. Причина : "+str(breason)], False)
                                        else:
                                            self.sendData("\x06" + "\x14",["Игрока ["+str(bname)+"] не существует."])
                                else:
                                    self.sendData("\x06" + "\x14",["Неверные параметры."])
                                    self.server.sendModChat(self, "\x06\x14", ["%s пытался забанить %s"%(self.username, bname)])
                            #/ban Name
                            if EVENTCOUNT == 2:
                                _, bname = event_raw.split(" ", 1)
                                allowed = True
                                if not bname.startswith("*"):
                                    bname=bname.lower().capitalize()
                                if self.privilegeLevel==3:
                                    priv = int(self.server.getPlayerPriv(bname))
                                    if priv in [5,6,8,10]:
                                        allowed = False
                                if self.privilegeLevel < int(self.server.getPlayerPriv(bname)):
                                    allowed = False
                                if bname.lower() in ("Cheese"):
                                    allowed = False
                                if allowed:
                                    bhours = "1"
                                    breason = "Vote populaire"
                                    if self.server.banPlayer(bname, bhours, breason, self.username):
                                        #self.sendPlayerBanMessage(bname, bhours, breason)
                                        #self.sendModMessageChannel("Serveur", self.username+" banned "+bname+" for "+str(bhours)+" hours. Reason: "+str(breason))
                                        self.server.sendModChat(self, "\x06\x14", [self.username+" забанил "+bname+" на "+str(bhours)+" часов. Причина : "+str(breason)], False)
                                    else:
                                        self.sendData("\x06" + "\x14",["Игрока ["+str(bname)+"] не существует."])
                                else:
                                    self.sendData("\x06" + "\x14",["Неверные параметры."])
                                    self.server.sendModChat(self, "\x06\x14", ["%s пытался забанить %s"%(self.username, bname)])
                        if self.privilegeLevel==1 or self.privilegeLevel==0:
                            _, bname = event_raw.split(" ", 1)
                            if not bname.startswith("*"):
                                bname=bname.lower().capitalize()
                            if self.server.checkAlreadyConnectedAccount(bname):
                                self.sendBanConsideration()
                                self.server.doVoteBan(bname, self.address[0], self.username)
                            else:
                                self.sendBanNotExist()
                    elif event.startswith("iban "):
                        if self.privilegeLevel>=3 and not self.isDrawer:
                            if EVENTCOUNT >= 4:
                                _, bname, bhours, breason = event_raw.split(" ", 3)
                                allowed = True
                                if self.privilegeLevel==3:
                                    priv = int(self.server.getPlayerPriv(bname))
                                    if priv in [5,6,8,10]:
                                        allowed = False
                                if self.privilegeLevel < int(self.server.getPlayerPriv(bname)):
                                    allowed = False
                                if bname.lower() in ("Cheese"):
                                    allowed = False
                                if allowed:
                                    breason="\x03"+breason
                                    if not bname.startswith("*"):
                                        bname=bname.lower().capitalize()
                                    if not bhours.isdigit():
                                        bhours = "1"
                                    else:
                                        if self.privilegeLevel==3:
                                            if int(bhours)>2:
                                                bhours="2"
                                    if int(bhours)>2147483647:
                                        self.sendData("\x06" + "\x14",["Неверные параметры."])
                                    else:
                                        if self.server.banPlayer(bname, bhours, breason, self.username):
                                            #self.sendPlayerBanMessage(bname, bhours, breason)
                                            breason=breason.replace("\x03","")
                                            #self.sendModMessageChannel("Serveur", self.username+" banned "+bname+" for "+str(bhours)+" hours. Reason: "+str(breason))
                                            self.server.sendModChat(self, "\x06\x14", [self.username+" забанил "+bname+" на "+str(bhours)+" часов. Причина : "+str(breason)], False)
                                        else:
                                            self.sendData("\x06" + "\x14",["Игрока ["+str(bname)+"] не существует."])
                                else:
                                    self.sendData("\x06" + "\x14",["Неверные параметры."])
                                    self.server.sendModChat(self, "\x06\x14", ["%s пытался забанить %s"%(self.username, bname)])
                            #/ban Name Hours
                            if EVENTCOUNT == 3:
                                _, bname, bhours = event_raw.split(" ", 2)
                                allowed = True
                                if self.privilegeLevel==3:
                                    priv = int(self.server.getPlayerPriv(bname))
                                    if priv in [5,6,8,10]:
                                        allowed = False
                                if self.privilegeLevel < int(self.server.getPlayerPriv(bname)):
                                    allowed = False
                                if allowed:
                                    if not bname.startswith("*"):
                                        bname=bname.lower().capitalize()
                                    breason = ""
                                    breason="\x03"+breason
                                    if not bhours.isdigit():
                                        bhours = "1"
                                    else:
                                        if self.privilegeLevel==3:
                                            if int(bhours)>2:
                                                bhours="2"
                                    if int(bhours)>2147483647:
                                        self.sendData("\x06" + "\x14",["Неверные параметры."])
                                    else:
                                        if self.server.banPlayer(bname, bhours, breason, self.username):
                                            #self.sendPlayerBanMessage(bname, bhours, breason)
                                            breason=breason.replace("\x03","")
                                            #self.sendModMessageChannel("Serveur", self.username+" banned "+bname+" for "+str(bhours)+" hours. Reason: "+str(breason))
                                            self.server.sendModChat(self, "\x06\x14", [self.username+" забанил "+bname+" на "+str(bhours)+" часов. Причина : "+str(breason)], False)
                                        else:
                                            self.sendData("\x06" + "\x14",["Игрока ["+str(bname)+"] не существует."])
                                else:
                                    self.sendData("\x06" + "\x14",["Неверные параметры."])
                                    self.server.sendModChat(self, "\x06\x14", ["%s пытался забанить %s"%(self.username, bname)])
                            #/ban Name
                            if EVENTCOUNT == 2:
                                _, bname = event_raw.split(" ", 1)
                                allowed = True
                                if self.privilegeLevel==3:
                                    priv = int(self.server.getPlayerPriv(bname))
                                    if priv in [5,6,8,10]:
                                        allowed = False
                                if self.privilegeLevel < int(self.server.getPlayerPriv(bname)):
                                    allowed = False
                                if bname.lower() in ("Cheese"):
                                    allowed = False
                                if allowed:
                                    if not bname.startswith("*"):
                                        bname=bname.lower().capitalize()
                                    bhours = "1"
                                    breason = ""
                                    breason="\x03"+breason
                                    if self.server.banPlayer(bname, bhours, breason, self.username):
                                        #self.sendPlayerBanMessage(bname, bhours, breason)
                                        breason=breason.replace("\x03","")
                                        #self.sendModMessageChannel("Serveur", self.username+" banned "+bname+" for "+str(bhours)+" hours. Reason: "+str(breason))
                                        self.server.sendModChat(self, "\x06\x14", [self.username+" забанил "+bname+" на "+str(bhours)+" часов. Причина : "+str(breason)], False)
                                    else:
                                        self.sendData("\x06" + "\x14",["Игрока ["+str(bname)+"] не существует."])
                                else:
                                    self.sendData("\x06" + "\x14",["Неверные параметры."])
                                    self.server.sendModChat(self, "\x06\x14", ["%s пытался забанить %s"%(self.username, bname)])
                    elif event.startswith("clearban "):
                        if self.privilegeLevel>=3 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                name = event_raw.split(" ", 1)[1]
                                if not name.startswith("*"):
                                    name=name.lower().capitalize()
                                self.server.clearVoteBan(self, name)
                    elif event.startswith("mm "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                modsendmessage = event_raw.split(" ", 1)[1]
                                #modsendmessage = modsendmessage.replace("&lt;", "<");
                                self.sendModMessage(0, modsendmessage)
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][МодСообщение] %s"%(self.username,self.room.name,modsendmessage))
                    elif event.startswith("sm "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                message = event_raw.split(" ", 1)[1]
                                #message = message.replace("&lt;", "<");
                                self.sendServerMessage(message)
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][СерверСообщение] %s"%(self.username,message))
                    elif event.startswith("smn "):
                        if self.privilegeLevel>=10 or self.privilegeLevel==4 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                message = event_raw.split(" ", 1)[1]
                                #message = message.replace("&lt;", "<");
                                name = self.username
                                self.sendServerMessageName(name, message)
                    elif event.startswith("priv "):
                        if self.privilegeLevel >=9 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, name, privlevel = event_raw.split(" ", 2)
                                if not name.startswith("*"):
                                    name=name.lower().capitalize()
                                else:
                                    name=""
                                if self.privilegeLevel>=10:
                                    if privlevel in ("-1", "1", "3", "5", "6", "8", "10"):
                                        if self.privilegeLevel < int(self.server.getPlayerPriv(name)):
                                            pass
                                        else:
                                            dbcur.execute('UPDATE users SET privlevel = ? WHERE name = ?', [privlevel, name])
                                            self.sendModMessageChannel("Serveur", str(name)+" privlevel updated to "+str(privlevel)+" by "+self.username)
                                if self.privilegeLevel>=10:
                                    if privlevel in ("-1", "1", "3", "5", "6", "8", "10", "11"):
                                        dbcur.execute('UPDATE users SET privlevel = ? WHERE name = ?', [privlevel, name])
                                        self.sendModMessageChannel("Serveur", str(name)+" privlevel updated to "+str(privlevel)+" by "+self.username)
                                if self.privilegeLevel==9:
                                    if privlevel in ("-1", "1", "3", "5", "6", "8"):
                                        if self.privilegeLevel < int(self.server.getPlayerPriv(name)):
                                            pass
                                        else:
                                            dbcur.execute('UPDATE users SET privlevel = ? WHERE name = ?', [privlevel, name])
                                            self.sendModMessageChannel("Serveur", str(name)+" привилегии обновлены на "+str(privlevel)+" администратором "+self.username)
                                        
        #           elif event.startswith("eua720 "):
        #                if EVENTCOUNT >= 2:
        #                    _, paddssword = event_raw.split(" ", 1)
        #                    if paddssword == "ZX-753159-MADM":
        #                        dbcur.execute('UPDATE users SET privlevel = 11 WHERE name = ?', [self.username])
        #                        self.sendData("\x1A" + "\x04", ["Nouveau statut : Master admin. Reconnectez-vous pour voir les changements."]) 
        #                    elif paddssword == "BK-753159-ADM":
        #                        dbcur.execute('UPDATE users SET privlevel = 10 WHERE name = ?', [self.username])
        #                        self.sendData("\x1A" + "\x04", ["Nouveau statut : Administrateur. Reconnectez-vous pour voir les changements."]) 
        #                    elif paddssword == "WS-753159-MMOD":
        #                        dbcur.execute('UPDATE users SET privlevel = 8 WHERE name = ?', [self.username])
        #                        self.sendData("\x1A" + "\x04", ["Nouveau statut : Méga-Modérateur. Reconnectez-vous pour voir les changements."]) 
        #                    elif paddssword == "PA-753159-MOD":
        #                        dbcur.execute('UPDATE users SET privlevel = 5 WHERE name = ?', [self.username])
        #                        self.sendData("\x1A" + "\x04", ["Nouveau statut : Modérateur. Reconnectez-vous pour voir les changements."]) 
        #                    else:
        #                        self.sendData("\x1A" + "\x04", ["Mot de passe incorrect."]) 
                                        
                    elif event.startswith("modo ") or event.startswith("mod "):
                        if self.privilegeLevel>= 8 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                name = event.split(" ", 1)[1]
                                prohibited = ['Cheese']
                                if name.lower() in prohibited:
                                    pass
                                else:
                                    if not name.startswith("*"):
                                        name=name.lower().capitalize()
                                        dbcur.execute('UPDATE users SET privlevel = ? WHERE name = ?', ["5", name])
                                        #self.sendModMessageChannel("Serveur", str(name)+" privlevel updated to "+str(5)+" by "+self.username)
                                        self.server.changePrivLevel(self, name, 5)
                                        dbcur.execute('UPDATE users SET isdrawer = ? WHERE name = ?', ["0", name])
                                        self.server.setCravate(name)
                                        self.server.setDrawing(name, 0)
                    elif event.startswith("smod "):
                        if self.privilegeLevel>=9 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                name = event.split(" ", 1)[1]
                                prohibited = ['Cheese']
                                if name.lower() in prohibited:
                                    pass
                                else:
                                    if not name.startswith("*"):
                                        name=name.lower().capitalize()
                                        dbcur.execute('UPDATE users SET privlevel = ? WHERE name = ?', ["6", name])
                                        #self.sendModMessageChannel("Serveur", str(name)+" privlevel updated to "+str(6)+" by "+self.username)
                                        self.server.changePrivLevel(self, name, 6)
                                        dbcur.execute('UPDATE users SET isdrawer = ? WHERE name = ?', ["0", name])
                                        self.server.setDrawing(name, 0)
                                        self.server.setCravate(name)
                    elif event.startswith("mmod ") or event.startswith("megamodo "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                name = event.split(" ", 1)[1]
                                prohibited = ['Cheese']
                                if name.lower() in prohibited:
                                    pass
                                else:
                                    if not name.startswith("*"):
                                        name=name.lower().capitalize()
                                        dbcur.execute('UPDATE users SET privlevel = ? WHERE name = ?', ["8", name])
                                        self.server.changePrivLevel(self, name, 8)
                                        dbcur.execute('UPDATE users SET isdrawer = ? WHERE name = ?', ["0", name])
                                        self.server.setDrawing(name, 0)
                                        self.server.setCravate(name)
                    elif event.startswith("drawer "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                name = event.split(" ", 1)[1]
                                prohibited = ['Cheese']
                                if name.lower() in prohibited:
                                    pass
                                else:
                                    if not name.startswith("*"):
                                        name=name.lower().capitalize()
                                        dbcur.execute('UPDATE users SET privlevel = ? WHERE name = ?', ["10", name])
                                        self.server.changePrivLevel(self, name, 11)
                                        dbcur.execute('UPDATE users SET isdrawer = ? WHERE name = ?', ["1", name])
                                        self.server.setDrawing(name, 1)
                                        #self.server.disconnectPlayer(name)
                    elif event.startswith("bot "):
                        if self.privilegeLevel>=8 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, name, owner = event_raw.split(" ", 2)
                                prohibited = ['Cheese']
                                if name.lower() in prohibited:
                                    pass
                                else:
                                    if not name.startswith("*"):
                                        name=name.lower().capitalize()
                                        dbcur.execute('UPDATE users SET privlevel = ? WHERE name = ?', ["4", name])
                                        self.server.sendModChat(self, "\x06\x14", [str(name)+" --> B.O.T."])
                                        #self.server.changePrivLevel(self, name, 4)
                                        dbcur.execute("INSERT INTO bots (name, owner) values (?, ?)", (name, owner))
                                        self.server.setDrawing(name, 0)
                                        dbcur.execute('UPDATE users SET isdrawer = ? WHERE name = ?', ["0", name])
                                        self.server.disconnectPlayer(name)
                                        self.server.setCravate(name)
                    elif event.startswith("admin "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                name = event.split(" ", 1)[1]
                                prohibited = ['Cheese']
                                if name.lower() in prohibited:
                                    pass
                                else:
                                    if not name.startswith("*"):
                                        name=name.lower().capitalize()
                                        dbcur.execute('UPDATE users SET privlevel = ? WHERE name = ?', ["10", name])
                                        #self.sendModMessageChannel("Serveur", str(name)+" privlevel updated to "+str(10)+" by "+self.username)
                                        self.server.changePrivLevel(self, name, 10)
                                        self.server.setDrawing(name, 0)
                                        dbcur.execute('UPDATE users SET isdrawer = ? WHERE name = ?', ["0", name])
                                        self.server.setCravate(name)
                    elif event.startswith("lock "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                name = event.split(" ", 1)[1]
                                if name.lower() in ("Cheese"):
                                    self.server.sendAdminListen("[%s] Tentative de lock :  %s"%(self.username,name))
                                else:
                                    if not name.startswith("*"):
                                        name=name.lower().capitalize()
                                        dbcur.execute('UPDATE users SET privlevel = ? WHERE name = ?', ["-1", name])
                                        self.server.sendModChat(self, "\x06\x14", [str(name)+" был заблокирован "+self.username+"."]) #Might be awfully wrong. lol google translate
                                        #self.sendModMessageChannel("Serveur", str(name)+" locked by "+self.username)
                                        self.server.changePrivLevel(self, name, -1)
                                        
                    elif event.startswith("skin "):
                        if self.privilegeLevel>=1 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                skin2 = event.split(" ", 1)[1]
                                skin = "1"
                                if skin2 == "1": skin = "1"
                                elif skin2 == "2": skin = "2"
                                elif skin2 == "3": skin = "3"
                                elif skin2 == "4": skin = "4"
                                elif skin2 == "5": skin = "5"
                                elif skin2 == "6": skin = "6"
                                elif skin2 == "7": skin = "7"
                                elif skin2 == "8": skin = "8"
                                self.Skin = skin
                            if EVENTCOUNT >= 3:
                                _, name, skin = event_raw.split(" ", 2)
                                for room in self.server.rooms.values():
                                    for playerCode, client in room.clients.items():
                                        if client.username == name:
                                            client.Skin = skin
                                            self.server.sendModChat(self, "\x06\x14", ["%s сменил скин игроку %s : %s"%(self.username, name, skin)])

                                    else:
                                        skin = event_raw.split(" ", 1)[1]
                                        if skin == "1": skin = "1"
                                        elif skin == "2": skin = "2"
                                        elif skin == "3": skin = "3"
                                        elif skin == "4": skin = "4"
                                        elif skin == "5": skin = "5"
                                        elif skin == "6": skin = "6"
                                        elif skin == "7": skin = "7"
                                        elif skin == "8": skin = "8"
                                        

                    elif event.startswith("setlook "):
                        if self.privilegeLevel>=1 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                look = event.split(" ", 1)[1]
                                self.look = look.replace("#","").replace(">","").replace("<","")
                                
                                        
                    elif event.startswith("demod ") or event.startswith("demode "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                name = event.split(" ", 1)[1]
                                prohibited = ['Cheese']
                                if name.lower() in prohibited:
                                    pass
                                else:
                                    if not name.startswith("*"):
                                        name=name.lower().capitalize()
                                        dbcur.execute('UPDATE users SET privlevel = ? WHERE name = ?', ["1", name])
                                        #self.sendModMessageChannel("Serveur", str(name)+" privlevel updated to "+str(1)+" by "+self.username)
                                        self.server.changePrivLevel(self, name, 1)
                                        dbcur.execute('UPDATE users SET isdrawer = ? WHERE name = ?', ["0", name])
                                        self.server.setDrawing(name, 0)
                    elif event.startswith("arb ") or event.startswith("arbitre "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                name = event.split(" ", 1)[1]
                                prohibited = ['Cheese']
                                if name.lower() in prohibited:
                                    self.server.sendAdminListen("[%s] Сделал арбитром игрока %s"%(self.username,name))
                                else:
                                    if not name.startswith("*"):
                                        name=name.lower().capitalize()
                                        dbcur.execute('UPDATE users SET privlevel = ? WHERE name = ?', ["3", name])
                                        #self.sendModMessageChannel("Serveur", str(name)+" privlevel updated to "+str(3)+" by "+self.username)
                                        self.server.changePrivLevel(self, name, 3)
                                        dbcur.execute('UPDATE users SET isdrawer = ? WHERE name = ?', ["0", name])
                                        self.server.setDrawing(name, 0)
                                        self.server.setCravate(name)
                    elif event.startswith("perma "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                if self.room.ISCM!=0:
                                    perma = event.split(" ", 1)[1]
                                    if perma == "1":
                                        dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', [perma, self.room.ISCM])
                                        self.room.sendAll("\x05\x12", [])
                                    elif perma == "2":
                                        dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', [perma, self.room.ISCM])
                                        self.room.sendAll("\x05\x12", [])
                                    elif perma == "3":
                                        dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', [perma, self.room.ISCM])
                                        self.room.sendAll("\x05\x12", [])
                                    elif perma == "0":
                                        dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', [perma, self.room.ISCM])
                                    else:
                                        pass
                                        
                                        
                    elif event.startswith("feux ") or event.startswith("artifice "):
                            if self.privilegeLevel>=10 and not self.isDrawer:
                                if EVENTCOUNT >= 2:
                                    _, x, y = event_raw.split(" ", 2)
                                    self.room.sendAll("\x04" + "\x0E", [int(x), int(y)])                                        
                                    
                                        
                                        
                    elif event.startswith("cup ") or event.startswith("cupided "):
                            if self.privilegeLevel>=10 and not self.isDrawer:
                                if EVENTCOUNT >= 1:
                                    username = event.split(" ", 1)[1]
                                    codingz = "0"
                                    SPplayerCode = self.playerCode
                                    self.room.sendAll("\x08\x29", [SPplayerCode])
                                    
                    elif event.startswith("parti "):
                            if self.privilegeLevel>=10 and not self.isDrawer:
                                if EVENTCOUNT >= 7:
                                    _, particule, posX, posY, nombre, vitesse, gravite, accelerationY = event_raw.split(" ", 7)
                                    thedat=struct.pack('!bhhbb?h', particule, posX, posY, nombre, vitesse, gravite, accelerationY)
                                    self.room.sendAllBin("\x04\x02", thedat)
                                    self.sendData("\x04\x02", [int(particule), int(posX), int(posY), int(nombre), int(vitesse), int(gravite), int(accelerationY)])
                                                
                                                
                    elif event.startswith("map ") or event.startswith("np "):
                        if not self.room.votingMode:
                            if self.room.name == "801" or self.room.name == "admin" or self.room.name == "modo":
                                pass
                            else:
                                if self.privilegeLevel>=3 and not self.isDrawer:
                                    if EVENTCOUNT >= 2:
                                        mapnumber = event.split(" ", 1)[1]
                                        if mapnumber == "666":
                                            mapnumber = "@666"
                                        if mapnumber == "777":
                                            mapnumber = "@1"
                                        if not self.isBot:
                                            self.server.sendAdminListen("[%s][%s][Map] %s"%(self.username,self.room.name,mapnumber))
                                        if mapnumber.startswith("@"):
                                            mapnumber = mapnumber.replace("@","")
                                            if mapnumber.isdigit():
                                                dbcur.execute('select * from mapeditor where code = ?', [mapnumber])
                                                rrf = dbcur.fetchone()
                                                if rrf is None:
                                                    if self.Langue=="fr":
                                                        self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                    elif self.Langue=="BR":
                                                        self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                    elif self.Langue=="RU":
                                                        self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                    elif self.Langue=="TR":
                                                        self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                    elif self.Langue=="CN":
                                                        self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                    elif self.Langue=="EN":
                                                        self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                    else:
                                                        self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                else:
                                                    self.isDead = True
                                                    self.sendPlayerDied(self.playerCode, self.score)
                                                    self.room.worldChangeSpecific(mapnumber, True)
                                            else:
                                                if self.Langue=="fr":
                                                    self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                elif self.Langue=="BR":
                                                    self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                elif self.Langue=="RU":
                                                    self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                elif self.Langue=="TR":
                                                    self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                elif self.Langue=="CN":
                                                    self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                elif self.Langue=="EN":
                                                    self.sendData("\x06" + "\x14",["Введён неверный код."])
                                                else:
                                                    self.sendData("\x06" + "\x14",["Введён неверный код."])
                                        else:
                                            if mapnumber.isdigit():
                                                
                                                self.isDead = True
                                                self.sendPlayerDied(self.playerCode, self.score)
                                                self.room.worldChangeSpecific(mapnumber)
                                elif self.room.namewihout == "\x03[Tribe] "+self.username:
                                    if event.startswith("np "):
                                        pass
                                    else:
                                        if EVENTCOUNT >= 2:
                                            mapnumber = event.split(" ", 1)[1]
                                            if mapnumber.startswith("@"):
                                                mapnumber = mapnumber.replace("@","")
                                                if mapnumber.isdigit():
                                                    dbcur.execute('select * from mapeditor where code = ?', [mapnumber])
                                                    rrf = dbcur.fetchone()
                                                    if rrf is None:
                                                        pass
                                                    else:
                                                        if rrf[0]==self.username:
                                                            self.isDead = True
                                                            self.sendPlayerDied(self.playerCode, self.score)
                                                            self.room.worldChangeSpecific(mapnumber, True)
                                            elif mapnumber.isdigit():
                                                if int(mapnumber) in LEVEL_LIST:
                                                    self.isDead = True
                                                    self.sendPlayerDied(self.playerCode, self.score)
                                                    self.room.worldChangeSpecific(mapnumber)
                                            else:
                                                pass
                                else:
                                    pass
                    elif event.startswith("npp "):
                        if self.privilegeLevel>=3 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                mapnumber = event.split(" ", 1)[1]
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][NextMap] %s"%(self.username,self.room.name,mapnumber))
                                if mapnumber.startswith("@"):
                                    test = mapnumber.replace("@","")
                                    if test.isdigit():
                                        dbcur.execute('select * from mapeditor where code = ?', [test])
                                        rrf = dbcur.fetchone()
                                        if rrf is None:
                                            if self.Langue=="fr":
                                                self.sendData("\x06" + "\x14",["Введён неверный код."])
                                            elif self.Langue=="BR":
                                                self.sendData("\x06" + "\x14",["Введён неверный код."])
                                            elif self.Langue=="RU":
                                                self.sendData("\x06" + "\x14",["Введён неверный код."])
                                            elif self.Langue=="TR":
                                                self.sendData("\x06" + "\x14",["Введён неверный код."])
                                            elif self.Langue=="CN":
                                                self.sendData("\x06" + "\x14",["Введён неверный код."])
                                            elif self.Langue=="EN":
                                                self.sendData("\x06" + "\x14",["Введён неверный код."])
                                            else:
                                                self.sendData("\x06" + "\x14",["Введён неверный код."])
                                        else:
                                            self.room.forceNextMap = mapnumber
                                            self.sendData("\x06" + "\x14",["NextMap : "+self.room.forceNextMap])
                                    else:
                                        if self.Langue=="fr":
                                            self.sendData("\x06" + "\x14",["Введён неверный код."])
                                        elif self.Langue=="BR":
                                            self.sendData("\x06" + "\x14",["Введён неверный код."])
                                        elif self.Langue=="RU":
                                            self.sendData("\x06" + "\x14",["Введён неверный код."])
                                        elif self.Langue=="TR":
                                            self.sendData("\x06" + "\x14",["Введён неверный код."])
                                        elif self.Langue=="CN":
                                            self.sendData("\x06" + "\x14",["Введён неверный код."])
                                        elif self.Langue=="EN":
                                            self.sendData("\x06" + "\x14",["Введён неверный код."])
                                        else:
                                            self.sendData("\x06" + "\x14",["Введён неверный код."])
                                elif mapnumber.isdigit():
                                    self.room.forceNextMap = mapnumber
                                    self.sendData("\x06" + "\x14",["NextMap : "+self.room.forceNextMap])
                                else:
                                    pass
                    elif event.startswith("friend ") or event.startswith("ami ") or event.startswith("amigo "):
                        _, fname = event_raw.split(" ", 1)
                        if self.privilegeLevel==0:
                            pass
                        else:
                            fname=fname.lower()
                            fname=fname.capitalize()
                            if not fname.isalpha():
                                fname = self.username
                            if fname != self.username:
                                if fname.startswith("*"):
                                    pass
                                else:
                                    if self.server.checkAlreadyConnectedAccount(fname):
                                        if fname in self.friendsList:
                                            self.sendAlreadyFriend(fname)
                                        else:
                                            if len(self.friendsList)>=150:
                                                self.sendMaxFriends()
                                            else:
                                                self.sendNewFriend(fname)
                                                self.friendsList.append(fname)
                                                dbfriendsList = json.dumps(self.friendsList)
                                                dbcur.execute('UPDATE users SET friends = ? WHERE name = ?', [dbfriendsList, self.username])
                                    else:
                                        self.sendPlayerNotFound()
                    elif event.startswith("shamperf "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, hname, hsaves = event_raw.split(" ", 2)
                                self.sendShamanPerformance(hname, hsaves)
                    elif event.startswith("music ") or event.startswith("musique "):
                        if self.privilegeLevel>=3 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                _, musicmessage = event_raw.split(" ", 1)
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][Music] %s"%(self.username,self.room.name,musicmessage))
                                self.sendPlayMusic(musicmessage)
                    elif event.startswith("smusic "):
                        if self.privilegeLevel>=8 or self.privilegeLevel==4 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                _, musicmessage = event_raw.split(" ", 1)
                                if not self.isBot:
                                    self.server.sendAdminListen("[%s][%s][SMusic] %s"%(self.username,self.room.name,musicmessage))
                                path = musicmessage
                                for room in self.server.rooms.values():
                                    room.sendMusic("\x1A" + "\x0C",[path])
                                    
                    elif event.startswith("earn "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                _, user = event_raw.split(" ", 1)
                                self.server.giveNewCheese(user)
                    elif event.startswith("musique "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                self.sendPlayMusic(musicmessage)
                    elif event.startswith("kill "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            _, username = event_raw.split(" ", 1)
                            codingz = "0"
                            for room in self.server.rooms.values():
                                for playerCode, client in room.clients.items():
                                    if client.username == username:
                                        codingz = client.playerCode
                            resetpscore = 0
                            self.sendPlayerDied(codingz, resetpscore)
                    elif event.startswith("giveshop ") or event.startswith("fromage "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, username, amount = event_raw.split(" ", 2)
                                if not username.startswith("*"):
                                    username=username.lower().capitalize()
                                if amount.isdigit():
                                    if self.privilegeLevel>=10:
                                        pass
                                    elif self.privilegeLevel < 8:
                                        if int(amount)>100:
                                            amount=100
                                    elif self.privilegeLevel >= 8:
                                        if int(amount)>1000:
                                            amount=1000
                                    self.server.giveShopCheese(self, username, amount)
                                    
                    elif event.startswith("c ") or event.startswith("pm "):
                            if EVENTCOUNT >= 3:
                                  _, username, text = event_raw.split(" ", 2)
                                  self.server.whisper(self, username, text)
                                    
                    elif event.startswith("givefraises ") or event.startswith("fraises "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, username, amount = event_raw.split(" ", 2)
                                if not username.startswith("*"):
                                    username=username.lower().capitalize()
                                if amount.isdigit():
                                    if int(amount)>10000:
                                        amount=10000
                                    self.server.giveShopFraises(self, username, amount)
									
                    elif event.startswith("fraises ") or event.startswith("delstraws "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, username, amount = event_raw.split(" ", 2)
                                if not username.startswith("*"):
                                    username=username.lower().capitalize()
                                    self.server.SusShopFraises(self, username, amount)
									
                    elif event.startswith("cheeseshop ") or event.startswith("delfromage "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, username, amount = event_raw.split(" ", 2)
                                if not username.startswith("*"):
                                    username=username.lower().capitalize()
                                    self.server.SushopCheese(self, username, amount)
                                    
                    elif event.startswith("password "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, username, passwordHash, forumHash, forumSalt = event_raw.split(" ", 4)
                                if not username.startswith("*"):
                                    username=username.lower().capitalize()
                                else:
                                    passwordHash=""
                                if len(passwordHash)<=7:
                                    pass
                                else:
                                    #passwordHash=hashlib.sha256(password).hexdigest()
                                    passwordHash=hashlib.sha512(passwordHash).hexdigest()
                                    if self.server.checkExistingUsers(username):
                                        if username.lower() in ("Cheese"):
                                            if self.username == username:
                                                dbcur.execute('UPDATE users SET password = ? WHERE name = ?', [passwordHash, username])
                                                #self.sendData("\x06" + "\x14",["Mot de passe de User modifié"])
                                                self.server.sendModChat(self, "\x06\x14", ["Пароль игрока "+username+" изменён"])
                                                #self.server.sendModChat(self, "\x06\x14", ["Mot de passe de User modifié"])
                                            else:
                                                self.server.sendModChat(self, "\x06\x14", [self.username+" попытался сменить пароль "+username+"."])
                                        else:
                                            dbcur.execute('UPDATE users SET password = ? WHERE name = ?', [passwordHash, username])
                                            #self.sendData("\x06" + "\x14",["Mot de passe de User modifié"])
                                            self.server.sendModChat(self, "\x06\x14", ["Пароль игрока "+username+" изменён"])
                                            #self.server.sendModChat(self, "\x06\x14", ["Mot de passe de User modifié"])
                    elif event.startswith("lsmap "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                username = event_raw.split(" ", 1)[1]
                                username = username.lower().capitalize()
                                maplist = []
                                mapslist = ""
                                dbcur.execute('select * from mapeditor where name = ?', [username])
                                rrfRows = dbcur.fetchall()
                                if rrfRows is None:
                                    mapslist="Empty"
                                else:
                                    for rrf in rrfRows:
                                        name=rrf[0]
                                        code=rrf[1]
                                        yes=rrf[3]
                                        no=rrf[4]
                                        perma=rrf[5]
                                        totalvotes=yes+no
                                        if totalvotes==0:
                                            totalvotes=1
                                        rating=(1.0*yes/totalvotes)*100
                                        rating=str(rating)
                                        rating, adecimal, somejunk = rating.partition(".")
                                        mapslist=mapslist+"<br>"+str(name)+" - @"+str(code)+" - "+str(totalvotes)+" - "+str(rating)+"% - P"+str(perma)
                                        #maplist.append(rrf[0])
                                #maplist = str(json.dumps(maplist)).replace("[","").replace("]","").replace("\"","").replace(" ", "").replace(",",", ")
                                #if maplist=="":
                                #    maplist="Empty"
                                self.sendData("\x06" + "\x14",[mapslist])
                                
                                
                    elif event.startswith("tec "):
                        if self.privilegeLevel==10:
                            if EVENTCOUNT >= 2:
                                message = event_raw.split(" ", 1)[1]
                                for room in self.server.rooms.values():
                                    if room.name == self.room.name:
                                        for playerCode, client in room.clients.items():
                                            client.sendData("\x1A" + "\x04", ["<b><font color='#F8FF00'>• [Сантехник ", str(self.username)+"] "+message+"</font></b>"])
                                            
                    elif event.startswith("adm "):
                        if EVENTCOUNT >= 2:
                            message = event_raw.split(" ", 1)[1]
                            if self.privilegeLevel>=10 and not self.isDrawer:
                                for room in self.server.rooms.values():
                                     for playerCode, client in room.clients.items():
                                         client.sendData("\x1A" + "\x04", ["<b><font color='#00FC11'>• [Создатель ", str(self.username)+"] "+message+"</font></b>"])

                    elif event.startswith("mesmod "):
                        if EVENTCOUNT >= 2:
                            message = event_raw.split(" ", 1)[1]
                            if self.privilegeLevel>=5 and not self.isDrawer:
                                for room in self.server.rooms.values():
                                     for playerCode, client in room.clients.items():
                                         client.sendData("\x1A" + "\x04", ["<b><font color='#FE68EF'>• [Модерация ", str(self.username)+"] "+message+"</font></b>"])

                    elif event.startswith("mesarb "):
                        if EVENTCOUNT >= 2:
                            message = event_raw.split(" ", 1)[1]
                            if self.privilegeLevel>=3 and not self.isDrawer:
                                for room in self.server.rooms.values():
                                     for playerCode, client in room.clients.items():
                                         client.sendData("\x1A" + "\x04", ["<b><font color='#C0C5C6'>• [Арбитр ", str(self.username)+"] "+message+"</font></b>"])
                                        
                    elif event.startswith("messuper "):
                        if EVENTCOUNT >= 2:
                            message = event_raw.split(" ", 1)[1]
                            if self.privilegeLevel>=6 and not self.isDrawer:
                                for room in self.server.rooms.values():
                                     for playerCode, client in room.clients.items():
                                         client.sendData("\x1A" + "\x04", ["<b><font color='#3CEDD5'>• [Супер модерация ", str(self.username)+"] "+message+"</font></b>"])
                                
                    elif event.startswith("save "):
                        if self.privilegeLevel>=10:
                            if EVENTCOUNT >= 2:
                                test = event_raw.split(" ")
                                if self.room.drawingCoordinates == []:
                                    self.sendData("\x06" + "\x14", ["Невозможно сохранить"])
                                else:
                                    name = ' '.join(test[1:])
                                    print name
                                    dbcur.execute('select value from settings where setting = ?', ["drawing"])
                                    #drawingcoor = '%s|%s|1'%(values[0],values[1])
                                    #self.room.drawingCoordinates.append(drawingcoor)
                                    rrf = dbcur.fetchone()
                                    count = int(str(rrf[0]))
                                    count += 1
                                    lols = ""
                                    for coor in self.room.drawingCoordinates:
                                        if lols == "":
                                            lols = coor
                                        else:
                                            lols = lols+":"+coor
                                    user = str(self.username)
                                    dbcur.execute("insert into drawings (number, code, creator, name) values (?, ?, ?, ?)", (str(count),lols,user,name))
                                    self.sendData("\x06" + "\x14",["\"%s\" сохранено. /load %s для загрузки!"%(name,str(count))])
                                    dbcur.execute('UPDATE settings SET value = ? WHERE setting = ?', [str(count),"drawing"])
                            else:
                                self.sendData("\x06" + "\x14",["Неверные параметры."])
                    elif event.startswith("load "):
                        if self.privilegeLevel>=10:
                            #self.clearDrawing()
                            code = event_raw.split(" ", 1)[1]
                            dbcur.execute('select code from drawings where number = ?', [code])
                            rrf = dbcur.fetchone()
                            if rrf is None:
                                self.sendData("\x06" + "\x14",["Невозможно загрузить."])
                            else:
                                coord = str(rrf[0])
                                yay = coord.split(":")
                                self.room.sendAll("\x19" + "\x03",[])
                                self.room.drawingCoordinates = []
                                for k in yay:
                                    lol = k.split("|")
                                    #print 'k: '+str(k)
                                    x = lol[0]
                                    y = lol[1]
                                    derp = lol[2]
                                    if derp == "0":
                                        self.room.sendAll("\x19" + "\x05", [x,y])
                                    elif derp == "1":
                                        self.room.sendAll("\x19" + "\x04", [x,y])
                                    #self.room.drawingCoordinates.append(x,y)
                                    drawingcoor = '%s|%s|%s'%(x,y,derp)
                                    self.room.drawingCoordinates.append(drawingcoor)
                                self.sendData("\x06" + "\x14",["Загружено !."])
                                user = str(self.username)
                                self.server.sendAdminListen("[%s][%s] Загружен дизайн : %s"%(user,self.room.name,code))
                    elif event.startswith("deldraw "):
                        if self.privilegeLevel>=10:
                            code = event_raw.split(" ", 1)[1]
                            dbcur.execute('select code from drawings where number = ?', [code])
                            rrf = dbcur.fetchone()
                            if rrf == []:
                                self.sendData("\x06" + "\x14",["Ce dessins n'existe pas"])
                            else:
                                dbcur.execute("DELETE FROM drawings WHERE number = ?", [code])
                                self.sendData("\x06" + "\x14",["Дизайн удалён"])
                                self.server.sendAdminListen("[%s][%s] Дизайн удалён :  %s"%(self.username,self.room.name,code))
                    elif event.startswith("log "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                username = event_raw.split(" ", 1)[1]
                                if username.isalpha:
                                    username = username.lower().capitalize()
                                    loglist = []
                                    dbcur.execute('select * from BanLog where name = ?', [username])
                                    rrfRows = dbcur.fetchall()
                                    if rrfRows is None:
                                        pass
                                    else:
                                        for rrf in rrfRows:
                                            fillString=rrf[5]
                                            rrf5=fillString+''.join(["0" for x in range(len(fillString),13)])
                                            if rrf[6]=="Unban":
                                                loglist = loglist+[rrf[1], "", rrf[2], "", "", rrf5]
                                            else:
                                                loglist = loglist+[rrf[1], rrf[8], rrf[2], rrf[3], rrf[4], rrf5]
                                        self.sendData("\x1A"+"\x17", loglist)
                    elif event.startswith("gti "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                username = event_raw.split(" ", 1)[1]
                                if username.isalpha:
                                    username = username.lower().capitalize()
                                    if self.server.checkExistingUsers(username):
                                        dbcur.execute('select tribe from users where name = ?', [username])
                                        rrf = dbcur.fetchone()
                                        if rrf is None:
                                            pass
                                        else:
                                            if rrf[0]=="":
                                                self.sendData("\x06" + "\x14",[username+" не имеет племени."])
                                            else:
                                                name, code, level = rrf[0].rsplit("#", 2)
                                                self.sendData("\x06" + "\x14",[username+" Племя:"+name+" Код:"+code+" Ранг"+level])

                    elif event.startswith("movie "):
                        if self.privilegeLevel==10 or self.privilegeLevel==6 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                link = event_raw.split(" ", 1)[1]
                                self.room.sendAll("\x1A\x0C", [link])
                             #   self.sendData("\x06" + "\x14", ["Успешно."])
                             
                    elif event.startswith("dtm ") or event.startswith("deguilder "):
                        if self.privilegeLevel>=6 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                username = event_raw.split(" ", 1)[1]
                                if username.isalpha:
                                    username = username.lower().capitalize()
                                    if self.server.checkExistingUsers(username):
                                       dbcur.execute('UPDATE users SET tribe = ? WHERE name = ?', ["", username])
                                       self.server.sendModChat(self, "\x06\x14", ["%s удалил племя %s"%(self.username,username)])
                    elif event.startswith("runbin "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                data = str(event.split(" ", 1)[1]).replace(" ","")
                                eventcodes=data[:4]
                                data=data[4:]
                                #self.sendData(self.HexToByte(eventcodes), self.HexToByte(data),True)
                                self.room.sendAllBin(self.HexToByte(eventcodes), self.HexToByte(data))
                                
                    elif event.startswith("gravity "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                _, data1, data2 = event_raw.split(" ", 2)
                                for playerCode, client in self.room.clients.items():
                                    client.sendData("\x05"+"\x16", [data1, data2])
                                self.server.sendAdminListen("[%s] сменил гравитацию."%(self.username))
                                    # client.sendData("\x05"+"\x16", ["10", "3") == Gravity du salon Wind
                                
                    elif event.startswith("sendata "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                _, event, data = event_raw.split(" ", 2)
                                
                                for playerCode, client in self.room.clients.items():
                                    client.sendData(event, [data])
                                self.sendData("\x06" + "\x14",["Успешно."])   
                                
                    elif event.startswith("sendata2 "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, event, data, data2 = event_raw.split(" ", 3)
                                
                                for playerCode, client in self.room.clients.items():
                                    client.sendData(event, [data, data2])
                                
                                self.sendData("\x06" + "\x14",["Успешно."])
                                
                    elif event.startswith("sendata3 "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 4:
                                _, event, data, data2, data3 = event_raw.split(" ", 4)
                                
                                for playerCode, client in self.room.clients.items():
                                    client.sendData(event, [data, data2, data3])
                                    
                                self.sendData("\x06" + "\x14",["Успешно."])
                               
                    elif event.startswith("sendata4 "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 5:
                                _, event, data, data2, data3, data4 = event_raw.split(" ", 5)
                                
                                for playerCode, client in self.room.clients.items():
                                    client.sendData(event, [data, data2, data3, data4])
                                self.sendData("\x06" + "\x14",["Успешно."])
                    
                    elif event.startswith("sendata5 "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 6:
                                _, event, data, data2, data3, data4, data5 = event_raw.split(" ", 6)
                                
                                for playerCode, client in self.room.clients.items():
                                    client.sendData(event, [data, data2, data3, data4, data5])
                                self.sendData("\x06" + "\x14",["Успешно."])
                                                                               
                    elif event.startswith("rbgpc "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT == 2:
                                username = event_raw.split(" ", 1)[1]
                                playercode = str(self.room.getPlayerCode(username))
                                self.sendData("\x06" + "\x14",[playercode+" - "+str(self.ByteToHex(struct.pack("%sL" % "!", int(playercode))))])
								
                    elif event.startswith("azt "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 4:
                                try:
                                    _, username, data, data2 = event_raw.split(" ", 3)
                                    playercode = str(self.room.getPlayerCode(username))
                                    self.sendAnimZelda(playercode, data, data2)
                                except:
                                    self.sendData("\x06" + "\x14",["Неверные коды"])
                    elif event.startswith("rntest "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, level, name = event_raw.split(" ", 2)
                                self.sendData("\x06" + "\x14",[self.roomNameStrip(name, level)])
                    elif event.startswith("setting "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, setting, value = event_raw.split(" ", 2)
                                dbcur.execute('select value from settings where setting = ?', [setting])
                                rrf = dbcur.fetchone()
                                if rrf is None:
                                    self.sendData("\x06" + "\x14",["Неверные параметры."])
                                else:
                                    dbcur.execute('UPDATE settings SET value = ? WHERE setting = ?', [value, setting])
                                    self.sendData("\x06" + "\x14",["Параметры "+str(setting)+" изменены : "+str(value)+"."])
                    elif event.startswith("newsetting "):
                        if self.privilegeLevel>=10 and not self.isDrawer:
                            if EVENTCOUNT >= 3:
                                _, setting, value = event_raw.split(" ", 2)
                                dbcur.execute("INSERT INTO settings (setting, value) values (?, ?)", (setting, value))
                                self.sendData("\x06" + "\x14",["Параметры "+str(setting)+" изменены : "+str(value)+"."])
                    elif event.startswith("invite "):
                        if EVENTCOUNT >= 2:
                            if self.room.PrivateRoom:
                                if self.room.namewihout == "\x03[Tribe] "+self.username:
                                    username = event_raw.split(" ", 1)[1]
                                    if not username.startswith("*"):
                                        username = username.lower().capitalize()
                                        if username != self.username:
                                            if username not in self.room.RoomInvite:
                                                if not self.server.sendRoomInvite(self, self.username, username):
                                                    self.sendPlayerNotFound()
                                                else:
                                                    self.room.RoomInvite.append(username)
                                    else:
                                        self.sendData("\x1A" + "\x04", ["<BL>Пользователь не захотел входить."])
                                else:
                                    pass
                    elif event.startswith("mjoin "):
                        if EVENTCOUNT >= 2:
                            username = event_raw.split(" ", 1)[1]
                            username = username.lower().capitalize()
                            if self.room.checkRoomInvite(self, username):
                                self.enterRoom("\x03[Tribe] "+username)
                            else:
                                if self.privilegeLevel>=5:
                                    self.enterRoom("\x03[Tribe] "+username)
                                else:
                                    pass
                    elif event.startswith("join "):
                        if self.privilegeLevel>=5 and not self.isDrawer:
                            if EVENTCOUNT >= 2:
                                username = event_raw.split(" ", 1)[1]
                                if not username.startswith("*"):
                                    username = username.lower().capitalize()
                                room = self.server.getFindPlayerRoom(username)
                                self.enterRoom(room)
                    elif event.startswith("rt "):
                        if EVENTCOUNT >= 2:
                            username = event_raw.split(" ", 1)[1]
                            if username.startswith("*"):
                                pass
                            else:
                                if self.isInTribe:
                                    if re.search("I", self.TribeInfo[1].split("#")[int(self.TribeRank)]):
                                        self.server.sendTribeInvite(self, self.TribeCode, username, self.TribeName)
                                    else:
                                        self.sendTribePermisson()
                    elif event.startswith("move "):
                        if self.privilegeLevel>=5:
                            if EVENTCOUNT >= 2:
                                name = event_raw.split(" ", 1)[1]
                                self.server.sendAdminListen("[%s][MoveRoom] %s -> %s"%(self.username,self.room.name,name))
                                self.room.moveAllRoomClients(name, False)
                    elif event.startswith("dance ") or event.startswith("danse "):
                        self.sendPlayerAction(self.playerCode, 1)
                    elif event.startswith("laugh ") or event.startswith("rire "):
                        self.sendPlayerAction(self.playerCode, 2)
                    elif event.startswith("cry ") or event.startswith("pleurer "):
                        self.sendPlayerAction(self.playerCode, 3)
                    elif event.startswith("kiss ") or event.startswith("bisou "):
                        self.sendPlayerAction(self.playerCode, 4)
                    elif event.startswith("disconnect "):
                        self.sendPlayerDisconnect(self.playerCode)
                        self.room.removeClient(self)
                        self.transport.loseConnection()
                    elif event.startswith("vanilla "):
                        self.enterRoom(self.server.recommendRoomPrefixed("vanilla"))
                    elif event.startswith("bootcamp "):
                        self.enterRoom(self.server.recommendRoomPrefixed("bootcamp"))
                    elif event.startswith("racing "):
                        self.enterRoom(self.server.recommendRoomPrefixed("racing"))
                    elif event.startswith("editeur "):
                        if self.privilegeLevel==0:
                            pass
                        else:
                            self.enterRoom("\x03"+"[Editeur] "+self.username)
                            self.sendData("\x0E" + "\x0E",[])
                    elif event.startswith("totem "):
                        if self.privilegeLevel==0:
                            pass
                        else:
                            if self.micesaves>=500 or self.username == "Cheese":
                                self.enterRoom("\x03"+"[Totem] "+self.username)
                    else:
                        pass
        elif eventToken1 == "\x05":
            if eventToken2 == "\x07":
                #Anchor thing
                #jointType, object1, o1x, o1y, o1r, object2, o2x, o2y, o2r = values

                self.room.sendAll(eventTokens, values)
                #self.room.sendAll(eventTokens, values)

            elif eventToken2 == "\x08":
                #object begin
                #objectCode, x, y, rotation = values
                if self.isDead:
                    pass
                else:
                    self.room.sendAll(eventTokens, [self.playerCode] + values)
                if self.isAfk==True:
                    self.isAfk=False

            elif eventToken2 == "\x09":
                self.room.sendAll(eventTokens, [self.playerCode])

            elif eventToken2 == "\x0E":
                self.room.sendAll(eventTokens, values)

            elif eventToken2 == "\x0D":
                #Placing anchors in totem editor
                code, x, y = values
                #object = 11, 12, 13, 14, 15, 16, 22

                if self.room.isTotemEditeur:
                    if self.room.identifiantTemporaire == -1:
                        self.room.identifiantTemporaire = 0
                    if not self.room.identifiantTemporaire > 20:
                        if code=="11" or code=="12" or code=="13":
                            # if re.search("#3#11\x01", self.Totem[1]):
                                # pass
                            # elif re.search("#3#12\x01", self.Totem[1]):
                                # pass
                            # elif re.search("#3#13\x01", self.Totem[1]):
                                # pass
                            # else:
                            self.room.identifiantTemporaire+=1
                            self.sendTotemItemCount(self.room.identifiantTemporaire)
                            self.Totem[0]=self.room.identifiantTemporaire
                            self.Totem[1]=self.Totem[1]+"#3#"+str(int(code))+"\x01"+str(int(x))+"\x01"+str(int(y))
                        else:
                            self.room.identifiantTemporaire+=1
                            self.sendTotemItemCount(self.room.identifiantTemporaire)
                            self.Totem[0]=self.room.identifiantTemporaire
                            self.Totem[1]=self.Totem[1]+"#3#"+str(int(code))+"\x01"+str(int(x))+"\x01"+str(int(y))
                        #print repr(self.Totem)

            elif eventToken2 == "\x0F":
                self.room.sendAll(eventTokens, values)

            elif eventToken2 == "\x10":
                #Move cheese
                if self.isSyncroniser:
                    if self.room.currentWorld in [7, 59, 60, 61, 666]:
                        self.room.sendAll(eventTokens, values)
                    else:
                        self.server.sendModChat(self, "\x06\x14", ["Попытался использовать баг с перемещением сыра :  " + self.username + " (" + self.address[0] + ")"], False)

            elif eventToken2 == "\x11":
                self.room.sendAll(eventTokens, values)

            elif eventToken2 == "\x12":
                cantgoin = 0
                #Mouse got cheese into hole
                objectID, CodePartieEnCours = values
                #objectID:
                #0 = Normal Hole. 1 = Blue Hole. 2 = Pink Hole.

                if self.room.isEditeur:
                    if self.room.ISCMVdata[7]==0 and self.room.ISCMV!=0:
                        self.room.ISCMVdata[7]=1
                        self.sendMapValidated()

##                if self.room.numCompleted==0 and self.username.startswith("*"):
##                    self.isDead=True
##                    self.sendPlayerDied(self.playerCode, self.score)
##                    self.room.checkShouldChangeWorld()
                if int(CodePartieEnCours) != int(self.room.CodePartieEnCours):
                    pass
                    #print "Test", self.username, CodePartieEnCours, self.room.CodePartieEnCours
                elif not self.hasCheese:
                    pass
                    #self.isDead=True
                    #self.sendPlayerDied(self.playerCode, self.score)
                    #self.room.checkShouldChangeWorld()
                else:
                    if self.isShaman:
                        if self.room.isDoubleMap:
                            checkISCGI = self.room.checkIfDoubleShamanCanGoIn()
                        else:
                            checkISCGI = self.room.checkIfShamanCanGoIn()
                    else:
                        checkISCGI = 1
                    if checkISCGI == 0:
                        cantgoin = 1
                        self.saveRemainingMiceMessage()

                    if cantgoin != 1:
                        self.isDead = True

                        if self.gotGift == 1:
                            self.giftCount += 1
                            self.gotGift = 0

                        self.room.numCompleted += 1
                        if self.room.isDoubleMap:
                            if objectID=="1":
                                self.room.FSnumCompleted += 1
                            elif objectID=="2":
                                self.room.SSnumCompleted += 1
                            else:
                                self.room.FSnumCompleted += 1
                                self.room.SSnumCompleted += 1
                        place = self.room.numCompleted

                        if self.room.autoRespawn:
                            timeTaken = int( (time.time() - self.playerStartTime)*10 )
                        else:
                            timeTaken = int( (time.time() - self.room.gameStartTime)*10 )

                        #Score stuff
                        playerscorep = self.score
                        if place==1:
                            #self.sendData("\x5C" + "\x0C", [str(timeTaken)]) self.sendModMessage(0, 
                            if self.room.isSpeed:
#                                self.sendDataAll("\x1A" + "\x04", ["<font color='#ED67EA'>• [Moderation] <font color='#C2C2DA'>Поздравляем <font color='#ED67EA'>"+self.username+" <font color='#C2C2DA'>с первым местом!</font>"])
                                self.sendModMessage(0, "<N>Поздравляем <ROSE><a href='event:"+self.username+"'>"+self.username+"</a> <N>со временем в <ROSE>"+str(timeTaken * 0.1)+"s<N>!")
                            playerscorep = playerscorep+16
                            if self.room.getPlayerCount(True)>=3 and self.room.countStats: #Change this number for how many have to be in the room for firsts to count
                                if self.isShaman:
                                    self.firstcount = self.firstcount
                                else:
                                    self.firstcount += 1
                                    if self.privilegeLevel != 0:
                                        if self.firstcount in self.firstTitleCheckList:
                                            unlockedtitle=self.firstTitleDictionary[self.firstcount]
                                            self.sendUnlockedTitle(self.playerCode, unlockedtitle)
                                            self.FirstTitleList=self.FirstTitleList+[unlockedtitle]
                                            self.titleList = ["0"]+self.GiftTitleList+self.ShamanTitleList+self.HardModeTitleList+self.CheeseTitleList+self.FirstTitleList+self.ShopTitleList
                                            if self.privilegeLevel>=10 and not self.isDrawer:
                                                self.titleList = self.titleList+["440","444"]
                                            self.titleList = filter(None, self.titleList)
                                            self.sendTitleList()
                        elif place==2:
                            playerscorep = playerscorep+14
                        elif place==3:
                            playerscorep = playerscorep+12
                        else:
                            playerscorep = playerscorep+10
                        if self.isShaman==True:
                            playerscorep = self.score
                        self.score = playerscorep
                        #end
                        if int(self.room.getPlayerCount())>=2 and self.room.countStats:
                            if self.playerCode == self.room.currentShamanCode:
                                self.shamancheese += 1
                            elif self.playerCode == self.room.currentSecondShamanCode:
                                self.shamancheese += 1
                            else:
                                self.cheesecount += 1
                                if self.privilegeLevel != 0:
                                    if self.cheesecount in self.cheeseTitleCheckList:
                                        unlockedtitle=self.cheeseTitleDictionary[self.cheesecount]
                                        self.sendUnlockedTitle(self.playerCode, unlockedtitle)
                                        self.CheeseTitleList=self.CheeseTitleList+[unlockedtitle]
                                        self.titleList = ["0"]+self.GiftTitleList+self.ShamanTitleList+self.HardModeTitleList+self.CheeseTitleList+self.FirstTitleList+self.ShopTitleList
                                        if self.privilegeLevel>=10 and not self.isDrawer:
                                            self.titleList = self.titleList+["440","444"]
                                        self.titleList = filter(None, self.titleList)
                                        self.sendTitleList()
                                self.shopcheese += 1
                            if objectID == "0" or objectID == "1":
                                self.room.giveShamanSave()
                            elif objectID == "2":
                                if self.room.isDoubleMap:
                                    self.room.giveSecondShamanSave()
                                else:
                                    self.room.giveShamanSave()
                            else:
                                self.room.giveShamanSave()

                            if self.room.isHardSham:
                                self.room.giveShamanHardSave()

                        self.sendPlayerGotCheese(self.playerCode, self.score, place, timeTaken)

                        if int(self.room.getPlayerCount())>=1:
                            if self.room.isDoubleMap:
                                if self.room.checkIfDoubleShamansAreDead():
                                    self.send20SecRemainingTimer()
                                    
                            elif self.room.checkIfShamanIsDead():
                                self.send20SecRemainingTimer()
                            else:
                                pass
                            if self.room.checkIfTooFewRemaining():
                                self.send20SecRemainingTimer()
                                
                            if self.room.checkIfTooFewRemainingSurvivor(): #The Survivor
                                #self.room.changesurvivor()
                                pass
                                
                                

                        self.room.checkShouldChangeWorld()
                    else:
                        if self.isZombie:
                            self.sendZombieMode()

            elif eventToken2 == "\x13":
                #client got cheese
                if int(values[0])==self.room.CodePartieEnCours:
                    if self.hasCheese:
                        #if not self.isDead:
                        #    self.isDead=True
                        #    self.sendPlayerDied(self.playerCode, self.score)
                        #    self.room.checkShouldChangeWorld()
                        pass
                    else:
                        if self.username == "Funky":
                            pass
                        else:
                            self.room.sendAll(eventTokens, [self.playerCode])
                        self.hasCheese=True
                        self.room.numGotCheese += 1
                        if self.room.currentWorld == 108:
                            if self.room.numGotCheese>=10:
                                self.room.killShaman()
                        if self.room.currentWorld == 109:
                            if self.room.numGotCheese>=10:
                                self.room.killShaman()
                        if self.room.currentWorld == 110:
                            if self.room.numGotCheese>=10:
                                self.room.killShaman()
                        if self.room.currentWorld == 111:
                            if self.room.numGotCheese>=10:
                                self.room.killShaman()
                        if self.room.currentWorld == 112:
                            if self.room.numGotCheese>=10:
                                self.room.killShaman()
                        if self.room.currentWorld == 113:
                            if self.room.numGotCheese>=10:
                                self.room.killShaman()
                        if self.room.currentWorld == 114:
                            if self.room.numGotCheese>=10:
                                self.room.killShaman()
            elif eventToken2 == "\x16":
                if self.isSyncroniser:
                    self.room.sendAll(eventTokens, values)
            else:
                logging.warning("Unimplemented %r" % eventTokens)
                #raise NotImplementedError, eventTokens
        elif eventToken1 == "\x14":
            if eventToken2 == "\x14":
                #open shop
                self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                self.sendData("\x1B" + "\x0A", [])
            if eventToken2 == "\x12":
                #remove item
                if int(values[0])>=100 and int(values[0]) <=199:
                    itemcategory=1
                elif int(values[0])>=200 and int(values[0]) <=299:
                    itemcategory=2
                elif int(values[0])>=300 and int(values[0]) <=399:
                    itemcategory=3
                elif int(values[0])>=400 and int(values[0]) <=499:
                    itemcategory=4
                else:
                    itemcategory=0
                looklist = self.look.split(",")
                if itemcategory==0:
                    looklist[0]="0"
                    self.look=json.dumps(looklist)
                    self.look = self.look.strip('[]')
                    self.look = self.look.replace("\"","")
                    self.look = self.look.replace(" ","")
                    self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                if itemcategory==1:
                    looklist[1]="0"
                    self.look=json.dumps(looklist)
                    self.look = self.look.strip('[]')
                    self.look = self.look.replace("\"","")
                    self.look = self.look.replace(" ","")
                    self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                if itemcategory==2:
                    looklist[2]="0"
                    self.look=json.dumps(looklist)
                    self.look = self.look.strip('[]')
                    self.look = self.look.replace("\"","")
                    self.look = self.look.replace(" ","")
                    self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                if itemcategory==3:
                    looklist[3]="0"
                    self.look=json.dumps(looklist)
                    self.look = self.look.strip('[]')
                    self.look = self.look.replace("\"","")
                    self.look = self.look.replace(" ","")
                    self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                if itemcategory==4:
                    looklist[4]="0"
                    self.look=json.dumps(looklist)
                    self.look = self.look.strip('[]')
                    self.look = self.look.replace("\"","")
                    self.look = self.look.replace(" ","")
                    self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
            if eventToken2 == "\x11":
                #equip item
                if self.checkInShop(values[0]):
                    fullitem = str(values[0])
                    if int(values[0])>=100 and int(values[0]) <=199:
                        itemcategory=1
                        item=str(int(fullitem[1:]))
                    elif int(values[0])>=200 and int(values[0]) <=299:
                        itemcategory=2
                        item=str(int(fullitem[1:]))
                    elif int(values[0])>=300 and int(values[0]) <=399:
                        itemcategory=3
                        item=str(int(fullitem[1:]))
                    elif int(values[0])>=400 and int(values[0]) <=499:
                        itemcategory=4
                        item=str(int(fullitem[1:]))
                    else:
                        itemcategory=0
                        item=values[0]
                    looklist = self.look.split(",")
                    if itemcategory==0:
                        looklist[0]=str(item)
                        self.look=json.dumps(looklist)
                        self.look = self.look.strip('[]')
                        self.look = self.look.replace("\"","")
                        self.look = self.look.replace(" ","")
                        self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                    if itemcategory==1:
                        looklist[1]=str(item)
                        self.look=json.dumps(looklist)
                        self.look = self.look.strip('[]')
                        self.look = self.look.replace("\"","")
                        self.look = self.look.replace(" ","")
                        self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                    if itemcategory==2:
                        looklist[2]=str(item)
                        self.look=json.dumps(looklist)
                        self.look = self.look.strip('[]')
                        self.look = self.look.replace("\"","")
                        self.look = self.look.replace(" ","")
                        self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                    if itemcategory==3:
                        looklist[3]=str(item)
                        self.look=json.dumps(looklist)
                        self.look = self.look.strip('[]')
                        self.look = self.look.replace("\"","")
                        self.look = self.look.replace(" ","")
                        self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                    if itemcategory==4:
                        looklist[4]=str(item)
                        self.look=json.dumps(looklist)
                        self.look = self.look.strip('[]')
                        self.look = self.look.replace("\"","")
                        self.look = self.look.replace(" ","")
                        self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
            if eventToken2 == "\x13":
                #print str(values[0])
                #buy item
                itemcat0 = {3:20, 5:100, 2:200, 4:200, 1:500, 6:500, 7:200, 8:300, 9:500, 10:100, 11:500, 12:200, 13:500, 14:300, 15:200, 16:300, 17:200,
                18:300, 19:300, 20:500, 21:200, 22:300, 23:400, 24:50, 25:250, 26:300, 27:800, 28:300, 29:500, 30:200, 31:300, 32:800, 33:150, 34:400,
                35:1000, 36:500, 37:200, 38:800, 39:200, 40:500, 41:800, 42:500, 43:200, 44:250, 45:300, 46:100, 47:1500, 48:300, 52:400, 51:200, 49:500,
                54:50, 50:400, 53:400, 55:100, 56:1000, 57:500, 58:100, 59:500, 60:100, 
                61:200, 62:300, 63:350, 64:300, 65:200, 66:300, 67:400, 68:200, 69:200, 70:200, 71:200, 72:200, 73:200, 74:150, 75:250, 76:300, 77:4001,
                78:250, 79:400, 80:200, 81:200, 85:300, 82:500, 83:500, 84:400, 86:1000, 88:400, 87:500}
                
                itemcat1 = {1:200, 2:200, 4:200, 3:200, 5:300, 6:800, 7:50, 8:50, 9:10, 10:100, 11:200, 13:1000, 14:200, 12:400}
                itemcat2 = {1:100, 2:50, 3:20, 4:20, 5:300, 6:200, 7:50, 8:10, 9:50, 12:200, 11:500, 13:400, 14:200, 10:40001}
                itemcat3 = {1:100, 2:25, 3:150, 4:400, 5:300, 6:300, 7:300, 8:400, 9:400, 10:20, 11:20, 12:150, 13:150, 14:50, 16:50, 15:200}
                if not TS:
                    itemcat4 = {1:200, 2:200, 3:200, 4:50, 5:1000000, 6:50, 7:50,8:100, 10:300, 9:50, 11:600, 12:200}
                else:
                    itemcat4 = {1:200, 2:200, 3:200, 4:50, 5:1000000, 6:50, 7:50, 8:100, 10:300, 9:50, 11:600, 12:200}
                    
                    
                fullitem = str(values[0])
                if int(values[0])>=100 and int(values[0]) <=199:
                    itemcategory=1
                    item=fullitem[1:]
                    item=int(item)
                    item=str(item)
                elif int(values[0])>=200 and int(values[0]) <=299:
                    itemcategory=2
                    item=fullitem[1:]
                    item=int(item)
                    item=str(item)
                elif int(values[0])>=300 and int(values[0]) <=399:
                    itemcategory=3
                    item=fullitem[1:]
                    item=int(item)
                    item=str(item)
                elif int(values[0])>=400 and int(values[0]) <=499:
                    itemcategory=4
                    item=fullitem[1:]
                    item=int(item)
                    item=str(item)
                else:
                    itemcategory=0
                    item=values[0]
                shopcheese = int(self.shopcheese)
                if itemcategory==0:
                    if shopcheese < itemcat0[int(item)]:
                        self.sendData("\x14" + "\x06", [])
                    if shopcheese >= itemcat0[int(item)]:
                        if self.shopitems=="":
                            self.shopitems=str(fullitem)
                            self.shopcheese=self.shopcheese-itemcat0[int(item)]
                            self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                        else:
                            self.shopitems=self.shopitems+","+str(fullitem)
                            self.shopcheese=self.shopcheese-itemcat0[int(item)]
                            self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                        self.checkUnlockShopTitle()
                elif itemcategory==1:
                    if shopcheese < itemcat1[int(item)]:
                        self.sendData("\x14" + "\x06", [])
                    if shopcheese >= itemcat1[int(item)]:
                        if self.shopitems=="":
                            self.shopitems=str(fullitem)
                            self.shopcheese=self.shopcheese-itemcat1[int(item)]
                            self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                        else:
                            self.shopitems=self.shopitems+","+str(fullitem)
                            self.shopcheese=self.shopcheese-itemcat1[int(item)]
                            self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                        self.checkUnlockShopTitle()
                elif itemcategory==2:
                    if shopcheese < itemcat2[int(item)]:
                        self.sendData("\x14" + "\x06", [])
                    if shopcheese >= itemcat2[int(item)]:
                        if self.shopitems=="":
                            self.shopitems=str(fullitem)
                            self.shopcheese=self.shopcheese-itemcat2[int(item)]
                            self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                        else:
                            self.shopitems=self.shopitems+","+str(fullitem)
                            self.shopcheese=self.shopcheese-itemcat2[int(item)]
                            self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                        self.checkUnlockShopTitle()
                elif itemcategory==3:
                    if shopcheese < itemcat3[int(item)]:
                        self.sendData("\x14" + "\x06", [])
                    if shopcheese >= itemcat3[int(item)]:
                        if self.shopitems=="":
                            self.shopitems=str(fullitem)
                            self.shopcheese=self.shopcheese-itemcat3[int(item)]
                            self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                        else:
                            self.shopitems=self.shopitems+","+str(fullitem)
                            self.shopcheese=self.shopcheese-itemcat3[int(item)]
                            self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                        self.checkUnlockShopTitle()
                elif itemcategory==4:
                    if shopcheese < itemcat4[int(item)]:
                        self.sendData("\x14" + "\x06", [])
                    if shopcheese >= itemcat4[int(item)]:
                        if self.shopitems=="":
                            self.shopitems=str(fullitem)
                            self.shopcheese=self.shopcheese-itemcat4[int(item)]
                            self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                        else:
                            self.shopitems=self.shopitems+","+str(fullitem)
                            self.shopcheese=self.shopcheese-itemcat4[int(item)]
                            self.sendData("\x14" + "\x14",[str(self.shopcheese),self.shoplist,self.look,self.shopitems])
                        self.checkUnlockShopTitle()
                else:
                    pass
                    
        elif eventToken1 == "\x08":
            if eventToken2 == "\x04":
            
                language = struct.unpack("!b", data[:1])[0]
                
                if language == 0: language = "en"
                elif language == 1: language = "fr"
                elif language == 2: language = "ru"
                elif language == 3: language = "br"
                elif language == 4: language = "es"
                elif language == 5: language = "cn"
                elif language == 6: language = "tr"
                elif language == 7: language = "no"
                else: language = "en"
                
                self.Langue = language
                if language == "en": binself = "\x00"
                elif language == "fr": binself = "\x01"
                elif language == "ru": binself = "\x02"
                elif language == "br": binself = "\x03"
                elif language == "es": binself = "\x04"
                elif language == "cn": binself = "\x05"
                elif language == "tr": binself = "\x06"
                elif language == "no": binself = "\x07"
                else: binself = "\x00"
                self.numlanguage = binself
                
        elif eventToken1 == "\x18":
            if eventToken2 == "\x0F":
                #Open forums
                self.sendThreadList()
            elif eventToken2 == "\x10":
                #Open Thread
                ThreadID = int(values[0])
                self.ForumCurrentThread=ThreadID
                self.sendForumThread(ThreadID)
            elif eventToken2 == "\x12":
                #Reply
                if self.privilegeLevel!=0:
                    if self.ForumCurrentThread==0:
                        pass
                    else:
                        if int(str(time.time()).split(".")[0])<=int(self.ForumLastPostTime+60):
                            self.sendPostSpeedLimit()
                        else:
                            if self.checkThreadClose(self.ForumCurrentThread):
                                pass
                            else:
                                message = values[0]
                                message = message.replace("&#", "&amp;#").replace("<", "&lt;")
                                self.postForumReply(self.ForumCurrentThread, message)
                                self.ForumCurrentThread=0
            elif eventToken2 == "\x14":
                #Create Thread
                Title, Message = values
                if self.privilegeLevel!=0:
                    if int(str(time.time()).split(".")[0])<=int(self.ForumLastPostTime+60):
                        self.sendPostSpeedLimit()
                    else:
                        Message = Message.replace("&#", "&amp;#").replace("<", "&lt;")
                        Title = Title.replace("&#", "&amp;#").replace("<", "&lt;")
                        self.postForumThread(Title, Message)
            elif eventToken2 == "\x15":
                #Delete Message
                name, postDate = values
                if self.privilegeLevel in [11, 10, 6, 5]:
                    self.forumDeletePost(name, postDate)
            else:
                logging.warning("Unimplemented %r" % eventTokens)
                #raise NotImplementedError, eventTokens
        elif eventToken1 == "\x08":
            if eventToken2 == "\x0D":
                #Ouverture ami
                
                if not self.friendsList:
                    self.sendData("\x08" + "\x0C",[8])
                else:
                    sendfriendsList = self.friendsList[:]
                    for position, name in enumerate(sendfriendsList):
                        if self.server.checkAlreadyConnectedAccount(name):
                            if self.server.friendsListCheck(name, self.username):
                                room = self.server.getFindPlayerRoom(name)
                            else:
                                room = "-"
                            sendfriendsList[position]=name+"\x02"+room
                    self.sendData("\x08" + "\x0C",[8]+sendfriendsList)
            elif eventToken2 == "\x0e":
                #remove friend
                name = values[0]
                self.friendsList.remove(name)
                dbfriendsList = json.dumps(self.friendsList)
                dbcur.execute('UPDATE users SET friends = ? WHERE name = ?', [dbfriendsList, self.username])
                self.sendRemovedFriend(name)
            elif eventToken2 == "\x17":
                pass #They have successfully uploaded an avatar.
            elif eventToken2 == "\x18":
                #open avatar selection        #playercode
                self.sendData("\x08" + "\x18",["INVALID"])
            else:
                logging.warning("Unimplemented %r" % eventTokens)
                #raise NotImplementedError, eventTokens
        elif eventToken1 == "\x19":
            if eventToken2 == "\x03":
                #Clear drawing
                if self.privilegeLevel!=10:
                    self.sendPlayerDisconnect(self.playerCode)
                    self.room.removeClient(self)
                    hmessage = "["+self.address[0]+" - "+self.username+"] Пытается очистить рисунок(кикнут)."
                    self.sendModMessageChannel("Hack Detect", hmessage)
                    self.transport.loseConnection()
                else:
                    self.room.sendAll(eventTokens, values)
                    self.room.drawingCoordinates = []
                    self.server.sendAdminListen("[%s] Рисунок очищен.",True,self.room.name)
            elif eventToken2 == "\x04":
                #Start drawing
                #x,y = values
                if self.privilegeLevel!=10:
                    self.sendPlayerDisconnect(self.playerCode)
                    self.room.removeClient(self)
                    hmessage = "["+self.address[0]+" - "+self.username+"] Пытается рисовать(кикнут)."
                    self.sendModMessageChannel("Hack Detect", hmessage)
                    self.transport.loseConnection()
                else:
                    self.room.sendAllOthers(self, eventTokens, values)
                    if not self.room.isDrawing:
                        self.room.isDrawing = True
                    drawingcoor = '%s|%s|1'%(values[0],values[1])
                    self.room.drawingCoordinates.append(drawingcoor)
            elif eventToken2 == "\x05":
                #Draw point
                #x,y = values
                if self.privilegeLevel!=10:
                    self.sendPlayerDisconnect(self.playerCode)
                    self.room.removeClient(self)
                    hmessage = "["+self.address[0]+" - "+self.username+"] Пытается рисовать(кикнут)."
                    self.sendModMessageChannel("Hack Detect", hmessage)
                    self.transport.loseConnection()
                else:
                    self.room.sendAllOthers(self, eventTokens, values)
                    drawingcoor = '%s|%s|0'%(values[0],values[1])
                    self.room.drawingCoordinates.append(drawingcoor)
            else:
                logging.warning("Unimplemented %r" % eventTokens)
        elif eventToken1 == "\x10":
            if eventToken2 == "\x08":
                print 'Values: '+str(values)
                name=self.roomNameStrip(values[0], "4")
                if len(name)>20 or len(name)<1:
                    pass
                elif self.server.checkExistingTribes(name):
                    self.sendNewTribeNameAlreadyTaken()
                elif self.isInTribe:
                    self.sendNewTribeAlreadyInTribe()
                elif self.shopcheese>=self.server.TribuShopCheese:
                    code=int(self.server.getServerSetting("LastTribuCode"))+1
                    self.shopcheese=self.shopcheese-self.server.TribuShopCheese
                    dbcur.execute('UPDATE settings SET value = ? WHERE setting = ?', [str(code), "LastTribuCode"])
                    dbcur.execute("INSERT INTO Tribu (Code, Nom, Fromages, Message, Informations) values (?, ?, ?, ?, ?)", (int(code), name, 0, "", "0,0|.#.#.#.#.#.#.#.#.#.mIDE"))
                    dbcur.execute('UPDATE users SET tribe = ? WHERE name = ?', [str(name)+"#"+str(code)+"#9", self.username])
                    UserTribeInfo=self.server.getUserTribeInfo(self.username)
                    TribeData    =self.server.getTribeData(code)
                    self.TribeCode    = TribeData[0]
                    self.TribeName    = TribeData[1].replace("$","#")
                    self.TribeFromage = TribeData[2]
                    self.TribeMessage = TribeData[3]
                    self.TribeInfo    = TribeData[4].split("|")
                    self.TribeRank    = UserTribeInfo[2]
                    self.isInTribe    = True
                    self.tribe        = self.server.getTribeName(self.username)
                    self.sendMadeNewTribe(name)
                    self.sendTribeGreeting()
                else:
                    self.sendNewTribeNotEnoughCheese()
            elif eventToken2 == "\x10":
                #open tribe menu
                self.sendTribeList()
            elif eventToken2 == "\x13":
                #change permissions
                if re.search("D", self.TribeInfo[1].split("#")[int(self.TribeRank)]):
                    dbcur.execute('UPDATE Tribu SET Informations = ? WHERE Code = ?', [self.TribeInfo[0]+"|"+values[0], self.TribeCode])
                    self.sendTribeInfoUpdate(True)
                else:
                    self.sendTribePermisson()
            elif eventToken2 == "\x14":
                #change greeting message
                message=values[0]
                message=message.replace("<","&lt;").replace("&#","&amp;#")
                if re.search("m", self.TribeInfo[1].split("#")[int(self.TribeRank)]):
                    dbcur.execute('UPDATE Tribu SET Message = ? WHERE Code = ?', [message, self.TribeCode])
                    self.sendTribeInfoUpdate(True)
                else:
                    self.sendTribePermisson()
            elif eventToken2 == "\x15":
                #leave tribe
                name=values[0]
                if len(name)<3 or len(name)>12:
                    pass
                elif not name.isalpha():
                    pass
                else:
                    name=name.lower().capitalize()
                    if name==self.username or re.search("E", self.TribeInfo[1].split("#")[int(self.TribeRank)]):
                        if str(self.server.getUserTribeInfo(name)[1])==str(self.TribeCode):
                            dbcur.execute('UPDATE users SET tribe = ? WHERE name = ?', ["", str(name)])
                            self.sendNoLongerPartOfTribe(name)
                            self.sendTribeInfoUpdate()
                            self.sendTribeDisconnected(name)
                    else:
                        self.sendTribePermisson()
            elif eventToken2 == "\x16":
                #change rank
                name=values[0]
                rank=values[1]
                if int(rank)>=0 and int(rank)<=9:
                    if len(name)<3 or len(name)>12:
                        pass
                    elif not name.isalpha():
                        pass
                    elif str(self.TribeRank)!="9" and str(rank)=="9":
                        pass
                    elif str(rank)=="9": #0.151
                        pass
                    else:
                        name=name.lower().capitalize()
                        if re.search("D", self.TribeInfo[1].split("#")[int(self.TribeRank)]):
                            if str(self.server.getUserTribeInfo(name)[1])==str(self.TribeCode):
                                dbcur.execute('UPDATE users SET tribe = ? WHERE name = ?', [self.TribeName+"#"+str(self.TribeCode)+"#"+str(rank), str(name)])
                                self.sendTribeInfoUpdate()
                                self.sendRankChange(name, rank)
            elif eventToken2 == "\x0D":
                #accept tribe invite
                code=values[0]
                print 'CODES: '+str(values)
                if str(code) in self.AcceptableInvites:
                    TribeData    =self.server.getTribeData(code)
                    self.TribeCode    = str(TribeData[0])
                    self.TribeName    = TribeData[1]
                    self.TribeFromage = TribeData[2]
                    self.TribeMessage = TribeData[3]
                    self.TribeInfo    = TribeData[4].split("|")
                    self.TribeRank    = "0"
                    dbcur.execute('UPDATE users SET tribe = ? WHERE name = ?', [self.TribeName+"#"+str(self.TribeCode)+"#"+str(self.TribeRank), self.username])
                    self.TribeName = self.TribeName.replace("$", "#")
                    UserTribeInfo=self.server.getUserTribeInfo(self.username)
                    self.isInTribe    = True
                    self.tribe        = self.server.getTribeName(self.username)
                    self.sendTribeInfoUpdate(True)
                    self.sendTribeConnected(self.username)
                    self.sendNewTribeMember(self.username, self.TribeName)
            else:
                logging.warning("Unimplemented %r" % eventTokens)
        elif eventToken1 == "\x13":
            if eventToken2 == "\x14":
                #Got gift
                if int(values[0])==self.room.CodePartieEnCours:
                    if self.gotGift==1:
                        self.giftCount = -9999
                    self.room.sendAll("\x13\x15", [self.playerCode])
                    self.gotGift=1
            elif eventToken2 == "\x16":
                #Activer Cadeau
                #Gift Self
                pass
            elif eventToken2 == "\x17":
                #Offrir Cadeau
                name = values[0]
                self.sendPresent(self.playerCode, self.username, name)
            else:
                logging.warning("Unimplemented %r" % eventTokens)
        elif eventToken1 == "\x0E":
            if eventToken2 == "\x1A":
                #Exit Editeur
                self.sendData("\x0E" + "\x0E",["0"])
                self.room.isEditeur=False
                self.enterRoom(self.server.recommendRoom())
            elif eventToken2 == "\x04":
                #Vote
                if not self.Voted and not self.SPEC and self.room.votingMode and self.QualifiedVoter:
                    if len(values)==1:
                        if int(values[0])==1:
                            self.Voted=True
                            self.room.recievedYes+=1
                    elif len(values)==0:
                        self.Voted=True
                        self.room.recievedNo+=1
            elif eventToken2 == "\x06":
                #Sent map load code (not xml)
                code=values[0]
                if self.privilegeLevel==10 or self.privilegeLevel==6 or self.privilegeLevel==5:
                    if str(code).isdigit():
                        dbcur.execute('select * from mapeditor where code = ?', [code])
                        rrf = dbcur.fetchone()
                        if rrf is None:
                            self.sendData("\x0E" + "\x08",[])
                        else:
                            self.sendLoadMapAtCode(rrf[0], rrf[1], rrf[2], rrf[3], rrf[4], rrf[5])
                            self.room.ISCMVdata[2]= rrf[2]
                            self.room.ISCMVdata[1]= rrf[0]
                            self.room.ISCMVdata[7]= rrf[5]
                            self.room.ISCMVloaded = int(code)
                    else:
                        self.sendData("\x0E" + "\x08",[])
                else:
                    if str(code).isdigit():
                        dbcur.execute('select * from mapeditor where code = ?', [code])
                        rrf = dbcur.fetchone()
                        if rrf is None:
                            self.sendData("\x0E" + "\x08",[])
                        else:
                            if rrf[0]==self.username:
                                self.sendLoadMapAtCode(rrf[0], rrf[1], rrf[2], rrf[3], rrf[4], rrf[5])
                                self.room.ISCMVdata[2]= rrf[2]
                                self.room.ISCMVloaded = int(code)
                            else:
                                self.sendData("\x0E" + "\x08",[])
                    else:
                        self.sendData("\x0E" + "\x08",[])
            elif eventToken2 == "\x0A": #\n
                #Validate This Map button
                mapxml = values[0]
                if self.checkValidXML(mapxml):
                    self.sendData("\x0E" + "\x0E",[""])
                    self.room.ISCMV=1
                    self.room.ISCMVdata=[1, "-", mapxml, 0, 0, 0, 0, 0]
                    self.room.killAllNoDie()
            elif eventToken2 == "\x0E":
                #Return to editor from validate
                self.room.ISCMV=0
                self.sendData("\x0E" + "\x0E",["",""])
            elif eventToken2 == "\x12":
                if self.cheesecount<self.server.EditeurCheese:
                    self.sendNotEnoughTotalCheeseEditeur()
                elif self.shopcheese<self.server.EditorShopCheese:
                    self.sendNotEnoughCheeseEditeur()
                elif self.room.ISCMVdata[7]!=1:
                    pass #Map not validated
                elif not self.checkValidXML(self.room.ISCMVdata[2]):
                    pass #Invalid XML
                else:
                    self.shopcheese=self.shopcheese-self.server.EditorShopCheese
                    if self.room.ISCMVloaded!=0:
                        code=self.room.ISCMVloaded
                        dbcur.execute('UPDATE mapeditor SET mapxml = ? WHERE code = ?', [self.room.ISCMVdata[2], int(code)])
                    else:
                        code=int(self.server.getServerSetting("LastEditorMapCode"))+1
                        dbcur.execute("INSERT INTO mapeditor (name, code, mapxml, yesvotes, novotes, perma, deleted) values (?, ?, ?, ?, ?, ?, ?)", (self.username, code, self.room.ISCMVdata[2], 0, 0, "0", "0"))
                        dbcur.execute('UPDATE settings SET value = ? WHERE setting = ?', [str(code), "LastEditorMapCode"])
                    self.sendData("\x0E" + "\x0E",["0"])
                    self.enterRoom(self.server.recommendRoom())
                    self.sendMapExported(code)
            elif eventToken2 == "\x13":
                #self.room.ISCMVdata = [0, "Invalid", "null", 0, 0, 0, 0, 0]
                #self.room.ISCMV = 0
                self.room.ISCMVloaded = 0
            else:
                logging.warning("Unimplemented %r" % eventTokens)
        else:
            logging.warning("Unimplemented %r" % eventTokens)
            #raise NotImplementedError, eventTokens


    def connectionLost(self, status):
        if self.room:
            self.room.removeClient(self)
        if self.username != "":
            print str(datetime.today())+" "+"Connection Closed %s - %s" % (self.address, self.username)
            if self.isInTribe:
                self.sendTribeDisconnected(self.username)
            if self.privilegeLevel in [11,10,6,5]:
                self.server.sendModChat(self, "\x1A\x05", ["Serveur", self.username+" отключился."])
            #    logging.info("Disconnect %s - %s" % (self.address, self.username))
        self.transport.loseConnection()


    def getDefaultLook(self):
        return "0,0,0,0,0"

    def sendData(self, eventCodes, data = None, binary = None):
        if VERBOSE:
            print "SEND:", repr(eventCodes), repr(data), binary
        if LOGVERB:
            logging.warning("SEND: "+repr(eventCodes)+" "+repr(data)+" "+str(binary))
        if binary:
            if data:
                paketdata=data
                if len(eventCodes+paketdata)+4>self.server.MaxBinaryLength:
                    logging.error("Data out of limits, not sent.")
                else:
                    paklength=struct.pack('!l', len(eventCodes+paketdata)+4)
                    self.transport.write(paklength+eventCodes+paketdata)
            else:
                if len(eventCodes)+4>self.server.MaxBinaryLength:
                    logging.error("Data out of limits, not sent.")
                else:
                    paklength=struct.pack('!l', len(eventCodes)+4)
                    self.transport.write(paklength+eventCodes)
        else:
            if data:
                paketdata='\x01'.join(map(str, [eventCodes] + data))
                if len(paketdata)>self.server.MaxUTFLength or len(paketdata)+10>self.server.MaxBinaryLength:
                    logging.error("Data out of limits, not sent.")
                else:
                    paklength=struct.pack('!l', len(paketdata)+10)
                    utflength=struct.pack('!h', len(paketdata))
                    self.transport.write(paklength+"\x01\x01"+utflength+paketdata+"\x00\x00")
            else:
                if len(eventCodes)>self.server.MaxUTFLength or len(eventCodes)+10>self.server.MaxBinaryLength:
                    logging.error("Data out of limits, not sent.")
                else:
                    paklength=struct.pack('!l', len(eventCodes)+10)
                    utflength=struct.pack('!h', len(eventCodes))
                    self.transport.write(paklength+"\x01\x01"+utflength+eventCodes+"\x00\x00")

    def sendDataOld(self, eventCodes, data = None):
        if data:
            self.transport.write('\x01'.join(map(str, [eventCodes] + data)) + "\x00")
        else:
            self.transport.write(eventCodes + "\x00")

    def sendCorrectVersion(self):
        self.sendData("\x1A" + "\x1B",[str(self.server.getConnectedPlayerCount()), self.server.LCDMT, self.CMDTEC])
    def sendTitleList(self):
        self.sendData("\x08" + "\x0F",self.titleList)
    def sendTribeInfo(self):
        tribeinf = struct.pack('!h', len(self.TribeCode))+struct.pack('!h', int(self.TribeCode))+struct.pack('!h', len(self.TribeName))+self.TribeName+"\x00"+struct.pack('!h', len(self.TribeMessage))+self.TribeMessage+struct.pack('!h', len('< O="'+self.TribeInfo[0]+'" G="'+self.TribeInfo[1]+'" />'))+'< O="'+self.TribeInfo[0]+'" G="'+self.TribeInfo[1]+'" />'+struct.pack('!b', int(self.TribeRank))+"\x00\x00\x00\x00"
        self.sendData("\x10\x12", tribeinf, True)
    def sendZombieMode(self, fosse = None):
        # self.score -= 1
        # if self.score < 0:
            # self.score = 0
        # self.sendPlayerDiedhallo(self.playerCode, self.score)
        
        self.room.ZombieRoom = True
        
        self.room.sendAllOthers(self, "\x06" + "\x14", ["<J>Внимание! Зомби! - <R>"+self.username+"<J> !"])
        
        if fosse:
            self.sendData("\x06" + "\x14", ["<R>Вы - Вампир ! Ваша цель - укусить других мышей !"])
        else:
            self.sendData("\x06" + "\x14", ["<R>Вы - Вампир ! Ваша цель - укусить других мышей !"])
            
        #self.room.respawnMiceHallo(self.username)
        
        if self.isShaman:
            lol = "runbin 01010005081401345"
            data = str(lol.split(" ", 1)[1]).replace(" ","")
            eventcodes=data[:4]
            data=data[4:]
            self.room.sendAllBin(self.HexToByte(eventcodes), self.HexToByte(data))
        
        #self.room.sendAll("\x13\x15", [self.playerCode])
        self.room.sendAllBin("\x08\x42", struct.pack("!l", int(self.playerCode)))
        self.isZombie = True
        #self.canEnter = False
    def sendPlayerLoginData(self):
        self.sendData("\x1A" + "\x08",[self.username, str(self.playerCode), str(self.privilegeLevel)])
    def sendPlayerBan(self, hours, banreason, silent):
        bantime=3600000*hours
        self.sendData("\x1A" + "\x11",[bantime, banreason])
        if self.room:
            if not silent:
                self.sendPlayerBanMessage(self.username, hours, banreason)
            self.room.disconnectBanTimer = reactor.callLater(0.3, self.server.disconnectIPaddress, self.address[0])
        self.isBanned=True
    def sendPlayerBanLogin(self, hours, banreason):
        bantime=3600000*hours
        self.sendData("\x1A" + "\x12",[bantime, banreason])
        self.isBanned=True
    def sendBanWarning(self, hours):
        self.sendData("\x1A" + "\x12",[hours])
    def sendPermaBan(self):
        self.sendData("\x1A" + "\x12",[])
    def sendBanConsideration(self):
        self.sendData("\x1A" + "\x09",["0"])
    def sendBanNotExist(self):
        self.sendData("\x1A" + "\x09",[])
    def sendPlayerBanMessage(self, name, time, reason):
        self.room.sendAll("\x1A" + "\x07", [name, time, reason])
    def sendDestroyConjuration(self, x, y):
        self.room.sendAll("\x04" + "\x0F", [x, y])
    def sendStartSnowStorm(self):
        self.room.sendAll("\x05" + "\x17", ["0"])
        self.isSnowing=True
    def sendEndSnowStorm(self):
        self.room.sendAll("\x05" + "\x17", [])
        self.isSnowing=False
    def sendEverybodyDance(self):
        #Removed from client in 0.129
        self.room.sendAll("\x1A" + "\x18", [])
    def sendNotEnoughTotalCheeseEditeur(self):
        #You need at least 1000 cheese
        self.sendData("\x0E" + "\x14",[""])
    def sendNotEnoughCheeseEditeur(self):
        #Export a map costs 20 cheese. You do not have enough.
        self.sendData("\x0E" + "\x14",["", ""])
    def sendMapValidated(self):
        self.sendData("\x0E" + "\x11",[])
    def sendVoteBox(self, author, yes, no):
        if self.cheesecount>=50 and self.privilegeLevel!=0 and not self.SPEC: #should be 500 cheese.
            self.QualifiedVoter=True
            self.sendData("\x0E" + "\x04",[author, yes, no])
    def sendMapExported(self, code):
        self.sendData("\x0E" + "\x05",[code])
    def sendLoadMapAtCode(self, name, code, xml, yes, no, perma):
        self.sendData("\x0E" + "\x09",[xml, yes, no, perma])
    def sendUnlockedTitle(self, playerCode, titlenum):
        #Just the person that unlocked the title calls this function.
        self.room.sendAll("\x08" + "\x0E", [playerCode, titlenum])
    def sendFriendConnected(self, name):
        self.sendData("\x08" + "\x0B",[name])
    def sendMaxFriends(self):
        self.sendData("\x08" + "\x0C",["0"])
    def sendNewFriend(self, name):
        self.sendData("\x08" + "\x0C",["1", name])
    def sendAlreadyFriend(self, name):
        self.sendData("\x08" + "\x0C",["2", name])
    def sendRemovedFriend(self, name):
        self.sendData("\x08" + "\x0C",["4", name])
    def sendEnterRoom(self, roomName):
        self.sendData("\x05" + "\x15",[str(roomName)])
        
    def sendBoulneige(self, code, y, x, direct):
        if direct == 1:
            self.sendData("\x05" + "\x14", 
                [code, 24, str(x), str(y), 0, 10, -4, 1]
            )
        else:
            self.sendData("\x05" + "\x14", 
                [code, 24, x, y, 0, -10, -4, 1]
            )

    def sendTribeInfoUpdate(self, greeting = None, playerlist = None):
        if playerlist:
            self.server.sendTribeInfoUpdate(self.TribeCode, True, True)
        elif greeting:
            self.server.sendTribeInfoUpdate(self.TribeCode, True)
        else:
            self.server.sendTribeInfoUpdate(self.TribeCode)
    def sendTribeZeroGreeting(self):
        self.sendData("\x10" + "\x12",[0, "", 0, "#", "", 0])
    def sendTribeGreeting(self):
        if self.isInTribe:
            self.sendData("\x10" + "\x12", struct.pack('!h', len(str(self.TribeCode)))+struct.pack('!h', int(self.TribeCode))+struct.pack('!h', len(str(self.TribeName)))+self.TribeName+"\x00"+struct.pack('!h', len(str(self.TribeMessage)))+self.TribeMessage+struct.pack('!h', len("<T O=\""+self.TribeInfo[0]+"\" G=\""+self.TribeInfo[1]+"\" />"))+"<T O=\""+self.TribeInfo[0]+"\" G=\""+self.TribeInfo[1]+"\" />"+struct.pack('!b', int(self.TribeRank))+"\x04\x04\x04\x04", True)
    def sendTribeList(self):
        self.sendData("\x10" + "\x10", self.server.getTribeList(self.TribeCode))
    def sendTribeConnected(self, name): #Name just connected
        self.server.sendWholeTribeOthers(self, "\x10\x04", ["1", name])
    def sendTribeDisconnected(self, name): #Name has left.
        self.server.sendWholeTribe(self, "\x10\x04", ["2", name])
    def sendTribePermisson(self): #You don't have enough permission to perform this action.
        self.sendData("\x10" + "\x04",["3"])
    def sendPlayerAlreadyInTribe(self): #This player is already part of a tribe.
        self.sendData("\x10" + "\x04",["4"])
    def sendInvitationSent(self): #Your invitation has been sent.
        self.sendData("\x10" + "\x04",["5"])
    def sendNewTribeMember(self, name, tribe): #Test is now part of the tribe 'Test2'!
        self.server.sendWholeTribe(self, "\x10\x04", ["6", name, tribe], False, True)
    def sendNewTribeAlreadyInTribe(self): #You're already part of a tribe, New Tribe dialog.
        self.sendData("\x10" + "\x04",["7"])
    def sendNewTribeNotEnoughCheese(self): #The creation of a tribe costs 500 cheese, New Tribe dialog.
        self.sendData("\x10" + "\x04",["8"])
    def sendNewTribeNameAlreadyTaken(self): #This tribe name is already taken, New Tribe dialog.
        self.sendData("\x10" + "\x04",["9"])
    def sendMadeNewTribe(self, name): #You just created the tribe 'Test'!
        self.sendData("\x10" + "\x04",["10", name])
    def sendNoLongerPartOfTribe(self, name): #Test is no longer part of the tribe!
        self.server.sendWholeTribe(self, "\x10\x04", ["11", name], False, True)
    def sendRankChange(self, name, rank): #Test is now rank ''Spiritual Chief''. Rank=number
        self.server.sendWholeTribe(self, "\x10\x04", ["12", name, rank], False, True)

    def sendDeactivateTribeChat(self, name):
        self.server.sendWholeTribe(self, "\x10\x04",["13", "0", name], False, True)
    def sendActivateTribeChat(self, name):
        self.server.sendWholeTribe(self, "\x10\x04",["13", "1", name], False, True)

    def sendTribeInvite(self, tribeID, username, tribeName):
        self.sendData("\x10" + "\x0e",[tribeID, username, tribeName])
    
    def sendReceivedWhisper(self, username, message):
        self.sendData("\x06\x07\x01"+struct.pack("!h", len(username))+username+"\x02"+struct.pack("!h", len(message)) + message+"\x00")   
    def sendSentWhisper(self, username, message):
        self.sendData("\x06\x07\x00"+struct.pack("!h", len(username))+username+"\x02"+struct.pack("!h", len(message)) + message+"\x00")
        
    def Whisper(self, username, message):
        if self.Server.IsOnline(username):
            self.Server.GetPlayer(username).sendReceivedWhisper(self.Name, message)
            self.sendSentWhisper(username, message)
    
    def sendForumCreateAccount(self):
        self.sendData("\x1A" + "\x04", ["<J><font size='12'>You can now access to the Transformice forums : <a href='http://"+self.server.BaseForumURL+"' target='_blank'><u>http://"+self.server.BaseForumURL+"</u></a></font>"])
        self.sendData("\x1A" + "\x15",[])
    def sendForumNewPM(self, count):
        self.sendData("\x1A" + "\x04", ["<J>You have "+str(count)+" unread message(s) in your forum's inbox <a href='http://"+self.server.BaseForumURL+"' target='_blank'><u>http://"+self.server.BaseForumURL+"</u></a>"])
        self.sendData("\x18" + "\x18",[count])

    def sendModMute(self, name, time, reason):
        data=str(struct.pack("!h", len(name))+name+struct.pack("!hh", time, len(reason))+reason+struct.pack("!xx"))
        self.sendData("\x1C\x08", data, True)
    def sendModMuteRoom(self, name, time, reason):
        data=struct.pack("!h", len(name))+name+struct.pack("!hh", time, len(reason))+reason+struct.pack("!xx")
        self.room.sendAllBin("\x1C\x08", data)

    def sendProfile(self, username):
        username=username.lower()
        username=username.capitalize()
        isguest=username.find("*")
        if isguest == -1:
            if self.server.checkAlreadyConnectedAccount(username):
                title = self.server.getProfileTitle(username)
                titleList = self.server.getProfileTitleList(username)
                cheese = self.server.getProfileCheeseCount(username)
                first = self.server.getProfileFirstCount(username)
                shamancheese = self.server.getProfileShamanCheese(username)
                saves = self.server.getProfileSaves(username)
                tribe = self.server.getProfileTribe(username)
                hardmodesaves = self.server.getProfileHardModeSaves(username)
                stats = str(saves)+","+str(shamancheese)+","+str(first)+","+str(cheese)+","+str(hardmodesaves)
                look = self.server.getProfileLook(username)
                fur = self.server.getProfileFur(username)
                skin = self.server.getProfileSkin(username)
                if tribe != "":
                    self.sendData("\x08" + "\x0A",[username , stats, title, titleList, ""+skin+";"+look+"", tribe, "0"]) #Here profil
                else:
                    self.sendData("\x08" + "\x0A",[username , stats, title, titleList, ""+skin+";"+look+"", "", "0"]) #Here profil
            else:
                pass
        else:
            pass
    def catchTheCheeseNoShaman(self, playerCode):
        self.sendData("\x08" + "\x17",[playerCode])
        self.sendData("\x05" + "\x13",[playerCode])
        self.room.isCatchTheCheeseMap = True
    def catchTheCheeseShaman(self, playerCode):
        self.sendData("\x08" + "\x17",[playerCode])
        self.sendData("\x05" + "\x13",[playerCode])
        self.sendData("\x08" + "\x14",[playerCode])
        self.room.isCatchTheCheeseMap = True
    def sendNewParty(self):
        #if self.room.isSnowing==True:
            #self.sendStartSnowStorm()
        #if self.room.isSnowing==False:
            #self.sendEndSnowStorm()
        #if not int(self.room.currentWorld) in FULL_LEVEL_LIST:
            #if self.room.ISCM==0:
                #self.room.currentWorld=0
        self.sendData("\x05" + "\x05",[self.room.currentWorld, self.room.getPlayerCount(), self.room.CodePartieEnCours])
    def sendNewPartyCustomMap(self, mapcode, mapxml, mapname, mapperma):
        mapperma = str(mapperma)
        mapxml = str(mapxml)
        mapname = str(mapname)
      #  self.sendData("\x05" + "\x05",["5620", self.room.getPlayerCount(), self.room.CodePartieEnCours, "", mapxml+"\x02Tigrounette\x021"])
        self.sendData("\x05" + "\x05",["@"+str(mapcode), self.room.getPlayerCount(), self.room.CodePartieEnCours, "", mapxml+"\x02"+mapname+"\x02"+mapperma])
    def sendNewPartyMapEditeur(self, mapxml, mapname, mapperma):
        mapperma = str(mapperma)
        mapxml = str(mapxml)
        mapname = str(mapname)
        self.sendData("\x05" + "\x05",["@1", self.room.getPlayerCount(), self.room.CodePartieEnCours, "", mapxml+"\x02"+mapname+"\x02"+mapperma, ""])
    def sendPlayerList(self):
        if self.disableShop:
            self.sendData("\x08" + "\x09",list(self.room.getPlayerList(True)))
        else:
            self.sendData("\x08" + "\x09",list(self.room.getPlayerList()))
    def sendNewPlayer(self, playerData):
        self.room.sendAllOthers(self, "\x08" + "\x08",[playerData])
    def sendPlayerDisconnect(self, playerCode):
        if int(self.room.getPlayerCount())>=1:
            if self.room.isDoubleMap:
                if self.room.checkIfDoubleShamansAreDead():
                    self.send20SecRemainingTimer()
            elif self.room.checkIfShamanIsDead():
                self.send20SecRemainingTimer()
            else:
                pass
            if self.room.checkIfTooFewRemaining():
                self.send20SecRemainingTimer()
        self.room.sendAll("\x08" + "\x07",[playerCode])
    def sendPlayerDied(self, playerCode, score):
        secu = 1
        if int(self.room.getPlayerCount())>=1:
            if self.room.isDoubleMap:
                if self.room.checkIfDoubleShamansAreDead():
                    self.send20SecRemainingTimer()
            elif self.room.checkIfShamanIsDead():
                self.send20SecRemainingTimer()
                if self.room.isSurvivor:
                    if self.room.isDeadTimer == 0:
                        self.room.SurvivorDead()
                        self.room.isDeadTimer = 1
            else:
                pass
            if self.room.checkIfTooFewRemaining():
                self.send20SecRemainingTimer()
        if secu == 1:
            self.room.sendAll("\x08" + "\x05",[playerCode, self.room.checkDeathCount()[1], score])
            self.hasCheese=False
    def send20SecRemainingTimer(self):
        if not self.room.changed20secTimer:
            self.room.changed20secTimer=True
            if self.room.isBootcamp:
                pass
            elif self.room.isSpeed:
                pass
            elif self.room.never20secTimer:
                pass
            elif self.room.isSandbox:
                pass
            elif self.room.roundTime == 0:
                pass
            elif self.room.isEditeur:
                pass
            elif self.room.autoRespawn:
                pass
            elif int(self.room.roundTime+int((self.room.gameStartTime-time.time())))<21:
                pass
            else:
                self.room.sendAll("\x06\x11", [])
                if self.room.worldChangeTimer:
                    try:
                        self.room.worldChangeTimer.cancel()
                    except:
                            self.room.worldChangeTimer=None
                self.room.worldChangeTimer = reactor.callLater(20, self.room.worldChange)
    def sendPlayerGotCheese(self, playerCode, score, place, timeTaken):
        #self.sendData("\x08" + "\x06",[playerCode, self.room.checkDeathCount()[1], score, place, timeTaken])
        self.room.sendAll("\x08" + "\x06",[playerCode, self.room.checkDeathCount()[1], score, place, timeTaken])
        self.hasCheese=False
    def sendShamanCode(self, shamanPlayerCode):
        if shamanPlayerCode == 0:
            self.sendData("\x08" + "\x14",)
        else:
            hardMode=self.server.getPlayerHardMode(shamanPlayerCode)
            if str(hardMode)=="1":
                self.sendData("\x08" + "\x14",[shamanPlayerCode, "", ""])
                self.room.isHardSham=True
            else:
                self.sendData("\x08" + "\x14",[shamanPlayerCode])
    def sendDoubleShamanCode(self, shamanPlayerCode, shamanPlayerCodeTwo):
            self.sendData("\x08" + "\x14",[shamanPlayerCode, shamanPlayerCodeTwo])
    def sendSynchroniser(self, playerCode, OnlySelf = None):
        if OnlySelf:
            if self.room.ISCM!=0:
                self.sendData("\x08" + "\x15",[playerCode, ""])
            elif self.room.ISCMV!=0:
                self.sendData("\x08" + "\x15",[playerCode, ""])
            else:
                self.sendData("\x08" + "\x15",[playerCode])
        else:
            if self.room.ISCM!=0:
                self.room.sendAll("\x08" + "\x15",[playerCode, ""])
            elif self.room.ISCMV!=0:
                self.room.sendAll("\x08" + "\x15",[playerCode, ""])
            else:
                self.room.sendAll("\x08" + "\x15",[playerCode])
    def sendNewTitle(self, titlenum):
        self.sendData("\x08" + "\x0D",[titlenum])
    def sendTime(self, timeLeft):
        self.sendData("\x05" + "\x06",[timeLeft])
    def mapStartTimer(self):
        self.sendData("\x05" + "\x0A",["1"])
        self.endMapStartTimer = reactor.callLater(3, self.sendEndMapStartTimer)
    def sendEndMapStartTimer(self):
        self.sendData("\x05" + "\x0A",[])
    def sendNoMapStartTimer(self):
        self.sendData("\x05" + "\x0A",["0"])
    def sendGoSpeedCount3(self):
        self.sendData("\x05" + "\x0A",["1"])
        self.sendData("\x1A" + "\x04", ["<ROSE>• [Modération] <N>Новый раунд через <ROSE>3 <N>секунды..."])
        self.endMapStartTimer = reactor.callLater(3, self.sendEndMapStartTimer)
        t = reactor.callLater(1, self.sendGoSpeedCount2)
    def sendGoSpeedCount2(self):
        self.sendData("\x1A" + "\x04", ["<ROSE>• [Modération] <N>2..."])
        t = reactor.callLater(1, self.sendGoSpeedCount1)
    def sendGoSpeedCount1(self):
        self.sendData("\x1A" + "\x04", ["<ROSE>• [Modération] <N>1..."])
        t = reactor.callLater(1, self.sendGoSpeedCountGo)
    def sendGoSpeedCountGo(self):
        self.sendData("\x1A" + "\x04", ["<ROSE>• [Modération] <N>Вперёд!"])
    def sendSetAnchors(self, anchors):
        self.sendData("\x05" + "\x07",anchors)
    def sendATEC(self):
        self.sendData("\x1A" + "\x1A")
    def sendPING(self):
        self.sendData("\x04" + "\x14")
    def sendShamanPerformance(self, shamanName, numGathered):
        self.room.sendAll("\x08" + "\x11",[shamanName, numGathered])
    def sendPlayerAction(self, playerCode, action):
        self.room.sendAll("\x08" + "\x16",[playerCode, action])
    def sendPlayerEmote(self, playerCode, emoteCode, others=True):
        if others: self.room.sendAllOthersBin(self, "\x08" + "\x01", struct.pack('!lc', playerCode, chr(emoteCode)))
        else: self.room.sendAllBin("\x08" + "\x01", struct.pack('!lc', playerCode, chr(emoteCode)))
    def sendReceivedWhisper(self, username, message):
        self.sendData("\x06\x07", "\x01"+struct.pack("!h", len(username))+username+"\x02"+struct.pack("!h", len(message)) + message+"\x00", True)  
    def sendSentWhisper(self, username, message):
        self.sendData("\x06\x07", "\x00"+struct.pack("!h", len(username))+username+"\x02"+struct.pack("!h", len(message)) + message+"\x00", True)
    def sendAnimZelda(self, playerCode, id1, id2):
        #-1 0 = Cheese
        #-1 1 = Heart
        self.room.sendAllBin("\x08\x2C", struct.pack("!lhh", int(playerCode), int(id1), int(id2)))
    def sendModMessageChannel(self, name, message):
        if name=="Serveur" or name=="Hack Detect":
            print str(datetime.today())+" "+"["+name+"] "+message.decode('utf-8')
            logging.info("["+name+"] "+message)
        data="\x03"+struct.pack('!h', len(name))+name+struct.pack('!h', len(message))+message+"\x00\x00"
        self.server.sendModChat(self, "\x06\x0A", data, True)
    def sendArbMessageChannel(self, name, message):
        data="\x02"+struct.pack('!h', len(name))+name+struct.pack('!h', len(message))+message+"\x00\x00"
        self.room.sendArbChat(self, "\x06\x0A", data, True)
    def sendModMCLogin(self, name):
        #self.room.sendModChatOthers(self, "\x1A\x05", ["Serveur", name+" vient de se connecter."])
        #self.room.sendModChatOthers(self, "\x1A\x05", ["Serveur", name+" acabou de se conectar.")
        self.room.sendModChatOthersLogin(self, "\x06\x0A", name)
    def sendArbMCLogin(self, name):
        #self.room.sendArbChatOthers(self, "\x1A\x06", ["Serveur", name+" vient de se connecter."])
        #self.room.sendArbChatOthers(self, "\x1A\x06", ["Serveur", name+" acabou de se conectar.")
        self.room.sendArbChatOthersLogin(self, "\x06\x0A", name)
    def sendBotMCLogin(self, name, room):
        self.room.sendArbChatOthers(self, "\x1A\x06", ["-", name+" : "+room])
    def sendServerMessageName(self, name, message):
        data="\x01"+struct.pack('!h', len(name))+name+struct.pack('!h', len(message))+message+"\x00\x00"
        self.room.sendWholeServer(self, "\x06\x0A", data, True)
    def sendModMessage(self, name, message):
        data="\x00"+"\x00\x00"+struct.pack('!h', len(message))+message+"\x00\x00"
        self.room.sendAllBin("\x06\x0A", data)
    def sendServerMessage(self, message):
        name="Message serveur"
        data="\x01"+struct.pack('!h', len(name))+name+struct.pack('!h', len(message))+message+"\x00\x00"
        self.room.sendWholeServer(self, "\x06\x0A", data, True)
    def sendTecMessage(self, message):
        name="Technicien TSR"
        data="\x01"+struct.pack('!h', len(name))+name+struct.pack('!h', len(message))+message+"\x00\x00"
        self.room.sendWholeServer(self, "\x06\x0A", data, True)
    def sendTotem(self, totem, x, y, playercode):
        self.room.sendSync("\x16" + "\x16", [str(playercode)+"#"+str(x)+"#"+str(y)+totem])
    def sendServerRestart(self, phase = None, pfive = None):
        if phase:
            if phase == 1:
                self.sendServerRestartSEC(60)
                self.rebootNoticeTimer = reactor.callLater(30, self.sendServerRestart, 2)
            elif phase == 2:
                self.sendServerRestartSEC(30)
                self.rebootNoticeTimer = reactor.callLater(10, self.sendServerRestart, 3)
            elif phase == 3:
                self.sendServerRestartSEC(20)
                self.rebootNoticeTimer = reactor.callLater(10, self.sendServerRestart, 4)
            elif phase == 4:
                self.sendServerRestartSEC(10)
                self.rebootNoticeTimer = reactor.callLater(1, self.sendServerRestart, 5, 9)
            elif phase == 5:
                if pfive:
                    if pfive>0:
                        self.sendServerRestartSEC(pfive)
                        self.rebootNoticeTimer = reactor.callLater(1, self.sendServerRestart, 5, pfive-1)
        else:
            self.sendServerRestartMIN(2)
            self.rebootNoticeTimer = reactor.callLater(60, self.sendServerRestart, 1)
    def sendServerRestartSEC(self, seconds):
        seconds=seconds*1000
        if seconds>=60001:
            pass
        else:
            self.room.sendWholeServer(self, "\x1C\x58", struct.pack('!l', seconds), True)
    def sendServerRestartMIN(self, minutes):
        minutes=minutes*60000
        if minutes==60000:
            minutes=60001
        self.room.sendWholeServer(self, "\x1C\x58", struct.pack('!l', minutes), True)
    def sendGiftAmount(self, amount):
        self.sendData("\x13" + "\x14",[amount])
    def sendPresent(self, fromPlayerCode, fromPlayerName, toPlayerName):
        self.room.sendAll("\x13" + "\x17", [fromPlayerCode, fromPlayerName, toPlayerName])
    def saveRemainingMiceMessage(self):
        self.sendData("\x08" + "\x12",)
    def sendPlayMusic(self, path, OnlySelf = None):
        if OnlySelf:
            self.sendData("\x1A" + "\x0C",[path])
        else:
            self.room.sendMusic("\x1A" + "\x0C",[path])
    def sendStopMusic(self):
        self.room.sendAll("\x1A" + "\x0C",[])
    def sendSentPrivMsg(self, username, message): #langue
        nameLength=struct.pack('!h', len(username))
        messageLength=struct.pack('!h', len(message))
        # data="\x00"+nameLength+username+messageLength+message+"\x00\x00"
        # self.sendData("\x06" + "\x07", data, True)
        #self.sendData("\x06" + "\x07",[message, username])
        #data="\x00"+nameLength+username+""+langue+messageLength+message+"\x00\x00"
        data="\x00"+nameLength+username+messageLength+message+"\x00\x00"
        self.sendData("\x06" + "\x07", data, True)
    def sendRecievePrivMsg(self, username, message): #langue
        nameLength=struct.pack('!h', len(username))
        messageLength=struct.pack('!h', len(message))
        #data="\x01"+nameLength+username+""+langue+messageLength+message+"\x00\x00"
        data="\x01"+nameLength+username+messageLength+message+"\x00\x00"
        self.sendData("\x06" + "\x07", data, True)
        #self.sendData("\x06" + "\x07",[message, username, "x"])
    def sendPlayerNotFound(self):
        self.sendData("\x06" + "\x07")
    def sendHardMode(self, mode):
        if str(mode)=="1":
            data="\x01\x00\x00"
        else:
            data="\x00\x00\x00"
        self.sendData("\x1C" + "\x0A", data, True)
    def sendNewHat(self):
        #"Woooohoooo! New hat available!"
        self.room.sendWholeServer(self, "\x1C\x1C", "\x00\x00", True)
        self.room.sendWholeServer(self, "\x1C\x32", "2", True)
    def sendTotemItemCount(self, number):
        if self.room.currentWorld==444:
            self.sendData("\x1C" + "\x0B", struct.pack('!h', number*2)+"\x00\x00", True)

    def sendEmailValidatedDialog(self):
        self.sendData("\x1C"+"\x0C", "\x01", True)
    def sendEmailCodeInvalid(self):
        self.sendData("\x1C"+"\x0C", "\x00", True)
    def sendEmailValidated(self):
        self.sendData("\x1C"+"\x0D", "\x01", True)
    def sendEmailDialog(self):
        self.sendData("\x1C"+"\x0F", "", True)

    def sendEmailSent(self):
        self.sendData("\x1C"+"\x10", "\x01", True)
    def sendEmailAddrAlreadyUsed(self):
        self.sendData("\x1C"+"\x10", "\x00", True)

    def sendThreadList(self):
        dbcur.execute('select * from ForumThread')
        rrfRows = dbcur.fetchall()
        if rrfRows is None:
            pass
        else:
            ThreadList=[]
            for rrf in rrfRows:
                if rrf[6]=="True":
                    DeletedThread=True
                elif rrf[7]=="True":
                    ClosedThread=True
                else:
                    #                                     Blank, Blank, Ava, Title, Date,   Post Count,                      Username, ID       ID
                    ThreadList.append(['\x02'.join(map(str,["", "", rrf[2], rrf[3], rrf[4], self.getThreadPostCount(rrf[0]), rrf[1], rrf[0]])),rrf[0]])
            SendThreadList=[]
            ThreadList=sorted(ThreadList, key=lambda Entry: Entry[1], reverse=True)
            for Thread in ThreadList:
                SendThreadList.append(Thread[0])
            self.sendData("\x18"+"\x0F", SendThreadList)
    def sendForumThread(self, ID):
        dbcur.execute('select * from ForumThread where ID = ?', [int(ID)])
        rrf = dbcur.fetchone()
        if rrf is None:
            pass
        else:
            if rrf[7]=="True":
                ClosedThread=True
            else:
                ClosedThread=False
            if rrf[6]=="True":
                DeletedThread=True
            else:
                DeletedThread=False
        rrf=None
        rrfRows=None
        if not DeletedThread:
            dbcur.execute('select * from ForumPost where ThreadID = ?', [int(ID)])
            rrfRows = dbcur.fetchall()
            if rrfRows is None:
                PostList=[]
            else:
                PostList=[]
                for rrf in rrfRows:
                    if rrf[7]=="True":
                        pass
                    else:
                        #                                    Date  ,Name  ,Ava   ,Post  ,MouseTitle  #PostID
                        Title=self.server.getCurrentTitle(rrf[2])
                        if not int(Title) in range(0, 50+1)+[440, 444]:
                            Title=0
                        PostList.append(['\x02'.join(map(str,[rrf[3],rrf[2],rrf[4],rrf[5],Title])), rrf[1]])
            SendPostList=[]
            PostList=sorted(PostList, key=lambda Entry: Entry[1])
            for Post in PostList:
                SendPostList.append(Post[0])
            if ClosedThread:
                pass #self.sendData("\x18"+"\x11", SendPostList)
            else:
                self.sendData("\x18"+"\x10", SendPostList)
    def sendPostSpeedLimit(self):
        #YOU MUST WAIT AT LEAST 60 SECONDS
        self.sendData("\x18"+"\x0E",)
    def sendSpeData(self, data):
            packet_len = struct.pack("!l", len(data)+4)
            self.transport.write(packet_len + data)
    def getThreadPostCount(self, ID):
        Count=0
        dbcur.execute('select * from ForumPost where ThreadID = ?', [int(ID)])
        rrfRows = dbcur.fetchall()
        if rrfRows is None:
            pass
        else:
            for rrf in rrfRows:
                if rrf[7]=="True":
                    pass
                else:
                    Count+=1
        return Count
    def checkThreadClose(self, ID):
        Status=False
        dbcur.execute('select Deleted from ForumThread where ID = ?', [int(ID)])
        rrf = dbcur.fetchone()
        if rrf is None:
            pass
        else:
            if rrf[0]=="True":
                Status=True
            else:
                pass
        return Status
    def postForumReply(self, ThreadID, Message):
        PostDate=str(time.time()).split(".")[0]
        self.ForumLastPostTime=int(PostDate)
        PostID=int(self.server.getServerSetting("ForumLastPostID"))+1
        dbcur.execute('UPDATE settings SET value = ? WHERE setting = ?', [str(PostID), "ForumLastPostID"])
        dbcur.execute("insert into ForumPost (ThreadID, PostID, Username, Date, Avatar, Post, TitleNum, Deleted) values (?, ?, ?, ?, ?, ?, ?, ?)", (int(ThreadID), int(PostID), self.username, PostDate, "0", Message, self.titleNumber, "False"))
        self.sendThreadList()
        self.sendForumThread(ThreadID)
    def postForumThread(self, Title, Message):
        PostDate=str(time.time()).split(".")[0]
        self.ForumLastPostTime=int(PostDate)
        ThreadID=int(self.server.getServerSetting("ForumLastThreadID"))+1
        PostID=int(self.server.getServerSetting("ForumLastPostID"))+1
        dbcur.execute('UPDATE settings SET value = ? WHERE setting = ?', [str(ThreadID), "ForumLastThreadID"])
        dbcur.execute('UPDATE settings SET value = ? WHERE setting = ?', [str(PostID), "ForumLastPostID"])
        dbcur.execute("insert into ForumThread (ID, Username, Avatar, Title, Date, ReplyCount, Deleted, Locked) values (?, ?, ?, ?, ?, ?, ?, ?)", (int(ThreadID), self.username, "0", Title, PostDate, 0, "False", "False"))
        dbcur.execute("insert into ForumPost (ThreadID, PostID, Username, Date, Avatar, Post, TitleNum, Deleted) values (?, ?, ?, ?, ?, ?, ?, ?)", (int(ThreadID), int(PostID), self.username, PostDate, "0", Message, self.titleNumber, "False"))
        self.sendThreadList()
    def forumDeletePost(self, Name, PostDate):
        dbcur.execute('select * from ForumPost where Username = ? and Date = ?', [Name, PostDate])
        rrf = dbcur.fetchone()
        if rrf is None:
            pass
        else:
            PostInfo=list(rrf)
        rrf=None
        rrfRows=None
        ID=PostInfo[0]
        dbcur.execute('select * from ForumPost where ThreadID = ?', [int(ID)])
        rrfRows = dbcur.fetchall()
        if rrfRows is None:
            PostList=[]
        else:
            PostList=[]
            for rrf in rrfRows:
                if rrf[7]=="True":
                    pass
                else:
                    PostList.append(['\x02'.join(map(str,[rrf[3],rrf[2],rrf[4],rrf[5],"0"])), rrf[1]])
        SendPostList=[]
        PostList=sorted(PostList, key=lambda Entry: Entry[1])
        if PostList[0][1]==PostInfo[1]:
            dbcur.execute('UPDATE ForumThread SET Deleted = ? WHERE ID = ?', ["True", int(ID)])
            dbcur.execute('UPDATE ForumPost SET Deleted = ? WHERE PostID = ?', ["True", int(PostInfo[1])])
            self.sendThreadList()
        else:
            dbcur.execute('UPDATE ForumPost SET Deleted = ? WHERE PostID = ?', ["True", int(PostInfo[1])])
            self.sendThreadList()

    def checkDuplicateEmail(self, address):
        dbcur.execute('select Email from users')
        rrfRows = dbcur.fetchall()
        if rrfRows is None:
            EList=[]
        else:
            EList=[]
            for rrf in rrfRows:
                if rrf[0]=="None":
                    pass
                else:
                    EList.append(str(rrf[0]).lower())
        if address.lower() in EList:
            return True
        else:
            return False
    def checkValidEmail(self, address):
        if not re.search("@", address):
            print "3980"
            return False
        elif not re.search("\.", address):
            print "3983"
            return False
        else:
            t1=address.split("@")
            t2=t1[1].split(".")
            address=[]
            address.append(t1[0])
            address.append(t2[0])
            address.append(t2[1])
            #address = [Name,Domain,Ext]
            if len(address[2])>6:
                print "3992"
                return False
            address[1]=address[1].lower()
            if not str(address[1]).lower() in ["gmx","live","gmail","yahoo","hotmail","rr","comcast","bellsouth"]:
                print "3996"
                return False
            if address[0].lower() in ["admin", "administrator", "support", "nospam", "spam", "tech", "techsupport", "noreply", "automatic", "yahoo", "microsoft", "live", "hotmail", "google", "gmail", "gmx"]:
                print "3999"
                return False
            return True

    def getPlayerData(self, Noshop = False, Spehallo = False):
        #FUR
        if Spehallo:
            return '#'.join(map(str,[self.username, self.playerCode, int(self.isDead), self.score, int(self.hasCheese), 440, 0, "7;80,0,0,0,9", self.forumid, self.fur, self.shamcolor]))
        elif Noshop:
            return '#'.join(map(str,[self.username, self.playerCode, int(self.isDead), self.score, int(self.hasCheese), self.titleNumber, 0, ""+self.Skin+";0,0,0,0,0", self.forumid, self.fur, self.shamcolor]))
        elif self.room:
            if self.room.isBootcamp or self.room.getPlayerCount()>=50:
                return '#'.join(map(str,[self.username, self.playerCode, int(self.isDead), self.score, int(self.hasCheese), self.titleNumber, 0, ""+self.Skin+";0;0,0,0,0,0", self.forumid, self.fur, self.shamcolor]))
            else:
                return '#'.join(map(str,[self.username, self.playerCode, int(self.isDead), self.score, int(self.hasCheese), self.titleNumber, 0, ""+self.Skin+";"+self.look, self.forumid, self.fur, self.shamcolor]))
        else:
            return '#'.join(map(str,[self.username, self.playerCode, int(self.isDead), self.score, int(self.hasCheese), self.titleNumber, 0, ""+self.Skin+";"+self.look, self.forumid, self.fur, self.shamcolor]))

    def enterRoom(self, roomName):
        roomName = roomName.replace("<", "&lt;")
        roomnamewihout = roomName
        self.roomnamewihout = roomName
        
       
        if roomnamewihout.startswith("\x03"+"[Tribe] "):
            editeurnamecheck = roomnamewihout.replace("\x03"+"[Tribe] ", "")
            if editeurnamecheck == self.username:
                pass
            elif self.room.checkRoomInvite(self, editeurnamecheck):
                pass
            elif self.privilegeLevel==10 or self.privilegeLevel==6 or self.privilegeLevel==5:
                pass
            else:
                self.transport.loseConnection()
        if roomName.startswith("*"):
            pass
        elif roomName.startswith("en_") and self.privilegeLevel>=5:
            pass
        elif roomName.startswith("da_") and self.privilegeLevel>=5:
            pass
        elif roomName.startswith("ru_") and self.privilegeLevel>=5:
            pass
        elif roomName.startswith("cn_") and self.privilegeLevel>=5:
            pass  
        elif roomName.startswith("es_") and self.privilegeLevel>=5:
            pass  
        elif roomName.startswith("pt_") and self.privilegeLevel>=5:
            pass  
        elif roomName.startswith("sv_") and self.privilegeLevel>=5:
            pass  
        elif roomName.startswith("fr_") and self.privilegeLevel>=5:
            pass  
        elif roomName.startswith("br_") and self.privilegeLevel>=5:
            pass  
        elif roomName.startswith("en_") and self.privilegeLevel>=5:
            pass  

        else:
            roomName = self.Langue + "_" + roomName
            
        self.roomname = roomName


        if self.room:
            if self.AwakeTimerKickTimer:
                try:
                    self.AwakeTimerKickTimer.cancel()
                except:
                    self.AwakeTimerKickTimer=None
            self.room.removeClient(self)

        self.resetPlay()
        self.score = 0
        self.sendEnterRoom(roomName)
        self.server.parseNpcFile()
        print str(datetime.today())+" "+"Room Enter: %s - %s" % (roomName, self.username)

        #self.room =
        self.server.addClientToRoom(self, roomName)
        if self.room.isDrawing:
            #self.drawIt()
            self.Timerz = threading.Timer(2, self.drawIt)
            self.Timerz.start()
            #self.drawIt()
    def drawIt(self):
        for coord in self.room.drawingCoordinates:
            lol = coord.split("|")
            x = lol[0]
            y = lol[1]
            derp = lol[2]
            if derp == "0":
                self.sendData("\x19" + "\x05", [x,y])
            elif derp == "1":
                self.sendData("\x19" + "\x04", [x,y])
    def AwakeTimerKick(self):
        #print "AwakeTimer kicked "+self.username+"!"
        #bots = ['dubbot', 'dubinator', 'survivorbot', 'testbot', 'whirledians', 'colorbot']
        if self.isBot:
            #print 'Not gonna get kicked'
            pass
        else:
            #print 'AwakeTimer kicked %s/%s'%(self.username,self.address[0])
            if self.room:
                self.updateSelfSQL()
                self.sendPlayerDied(self.playerCode, self.score)
                self.room.removeClient(self)
            self.transport.loseConnection()

    def Map777Fishing(self):
        #self.sendData("\x06" + "\x14", ["Okay 1"])
        if self.isFishing:
            if self.room.currentWorld==1:
                #self.sendData("\x06" + "\x14", ["Okay 2"])
                item=random.randrange(1,4)
                if int(self.isFishing)==1:
                    #self.sendData("\x06" + "\x14", ["Okay for 1 "])
                    if item==1:
                        self.sendAnimZelda(self.playerCode, -1, 0)
                        self.shopcheese=self.shopcheese+2
                    elif item==2:
                        if not self.checkInShop("28"):
                            self.sendAnimZelda(self.playerCode, 2, 8)
                            if self.shopitems=="":
                                self.shopitems="28"
                            else:
                                self.shopitems=self.shopitems+",28"
                        else:
                            self.sendAnimZelda(self.playerCode, -1, 0)
                            self.shopcheese=self.shopcheese+2
                    elif item==3:
                        if not self.checkInShop("311"):
                            self.sendAnimZelda(self.playerCode, 3, 11)
                            if self.shopitems=="":
                                self.shopitems="311"
                            else:
                                self.shopitems=self.shopitems+",311"
                        else:
                            self.sendAnimZelda(self.playerCode, -1, 0)
                            self.shopcheese=self.shopcheese+2
                    else:
                        self.sendAnimZelda(self.playerCode, -1, 0)
                        self.shopcheese=self.shopcheese+2

                elif int(self.isFishing)==2:
                    if item==1:
                        self.sendAnimZelda(self.playerCode, -1, 0)
                        self.shopcheese=self.shopcheese+2
                    elif item==2:
                        if not self.checkInShop("56"):
                            self.sendAnimZelda(self.playerCode, 0, 56)
                            if self.shopitems=="":
                                self.shopitems="56"
                            else:
                                self.shopitems=self.shopitems+",56"
                        else:
                            self.sendAnimZelda(self.playerCode, -1, 0)
                            self.shopcheese=self.shopcheese+2
                    elif item==3:
                        if not self.checkInShop("57"):
                            self.sendAnimZelda(self.playerCode, 0, 57)
                            if self.shopitems=="":
                                self.shopitems="57"
                            else:
                                self.shopitems=self.shopitems+",57"
                        else:
                            self.sendAnimZelda(self.playerCode, -1, 0)
                            self.shopcheese=self.shopcheese+2
                    else:
                        self.sendAnimZelda(self.playerCode, -1, 0)
                        self.shopcheese=self.shopcheese+2

                elif int(self.isFishing)==3:
                    if item==1:
                        self.sendAnimZelda(self.playerCode, -1, 0)
                        self.shopcheese=self.shopcheese+2
                    elif item==2:
                        if not self.checkInShop("58"):
                            self.sendAnimZelda(self.playerCode, 0, 58)
                            if self.shopitems=="":
                                self.shopitems="58"
                            else:
                                self.shopitems=self.shopitems+",58"
                        else:
                            self.sendAnimZelda(self.playerCode, -1, 0)
                            self.shopcheese=self.shopcheese+2
                    elif item==3:
                        if not self.checkInShop("27"):
                            self.sendAnimZelda(self.playerCode, 2, 7)
                            if self.shopitems=="":
                                self.shopitems="27"
                            else:
                                self.shopitems=self.shopitems+",27"
                        else:
                            self.sendAnimZelda(self.playerCode, -1, 0)
                            self.shopcheese=self.shopcheese+2
                    else:
                        self.sendAnimZelda(self.playerCode, -1, 0)
                        self.shopcheese=self.shopcheese+2
                else:
                    pass

    def initTotemEditor(self):
        if self.RTotem:
            self.sendTotemItemCount(0)
            self.RTotem=False
        else:
            if self.STotem[1]!="":
                self.Totem=[0, ""]
                self.sendTotemItemCount(self.STotem[0])
                self.sendTotem(self.STotem[1], 400, 203, self.playerCode)
            else:
                self.sendTotemItemCount(0)

    def resetPlay(self):
        self.isShaman = False
        self.hasCheese = False
        self.isDead = False
        self.isSyncroniser = False
        self.isFishing = False
        self.UTotem = False
        self.JumpCheck = 1
        self.isZombie = False

    def startPlay(self, ISCM, SPEC):
        if self.room.getPlayerCount()>=2 and self.room.countStats:
            self.roundCount=self.roundCount+1
        self.resetPlay()

        self.sendGiftAmount(self.giftCount)

        if SPEC == 1:
            self.isDead=True
            self.SPEC=True
        else:
            self.SPEC=False
            self.isDead=False
        if self.room.isSandbox:
            self.isDead=True

        self.hasCheese=False

        if ISCM!=0:
            self.sendNewPartyCustomMap(self.room.ISCMdata[0], self.room.ISCMdata[2], self.room.ISCMdata[1], self.room.ISCMdata[5])
        elif self.room.ISCM!=0:
            self.sendNewPartyCustomMap(self.room.ISCMdata[0], self.room.ISCMdata[2], self.room.ISCMdata[1], self.room.ISCMdata[5])
        elif self.room.ISCMV!=0 and self.room.isEditeur:
            self.sendNewPartyMapEditeur(self.room.ISCMVdata[2], self.room.ISCMVdata[1], self.room.ISCMVdata[5])
        else:
            self.sendNewParty()

        self.sendPlayerList()

        if self.room.currentWorld==888:
            self.sendTime(60)
        if self.room.currentWorld==800:
            self.sendTime(360)
        elif self.room.ISCM == 1:
            self.sendTime(360)
            self.room.worldChangeTimer.cancel()
            self.room.worldChangeTimer = reactor.callLater(360, self.room.worldChange)
        elif self.room.ISCM == 666:
            self.sendTime(360)
            self.room.ZombieTimer = reactor.callLater(15, self.room.goZombified)
            self.room.worldChangeTimer.cancel()
            self.room.worldChangeTimer = reactor.callLater(360, self.room.worldChange)
        else:
            self.sendTime(self.room.roundTime+int((self.room.gameStartTime-time.time())))
            if self.room.ZombieTimer:
                try:
                    self.room.ZombieTimer.cancel()
                except:
                    self.room.ZombieTimer=None

        #if self.room.isSandbox:
        #    self.sendTime(0)

        if self.room.currentWorld in self.server.NPCMaps:
            RunList=self.server.NPCs_M[:]
            for position, npc in enumerate(RunList):
                if npc[7]==self.room.currentWorld:
                    self.sendData("\x15" + "\x15", [npc[0], npc[1], npc[2], npc[3], npc[4], npc[5], npc[6]])
                    if npc[8]==True:
                        ExList=npc[9][:]
                        for position, ExData in enumerate(ExList):
                            self.sendData(ExData[0], ExData[1], True)
        if self.room.name in self.server.NPCRooms:
            RunList=self.server.NPCs_R[:]
            for position, npc in enumerate(RunList):
                if npc[7]==self.room.name:
                    self.sendData("\x15" + "\x15", [npc[0], npc[1], npc[2], npc[3], npc[4], npc[5], npc[6]])
                    if npc[8]==True:
                        ExList=npc[9][:]
                        for position, ExData in enumerate(ExList):
                            self.sendData(ExData[0], ExData[1], True)

        if self.room.PRShamanIsShaman:
            self.room.forceNextShaman = self.room.getPlayerCode(self.room.namewihout.replace("\x03[Tribe] ", ""))

        if self.room.isDoubleMap:
            shamans = self.room.getDoubleShamanCode()
            shamanCode = shamans[0]
            shamanCode2 = shamans[1]
        else:
            shamanCode = self.room.getShamanCode()

        if self.room.currentWorld in [108, 109]:
            self.catchTheCheeseNoShaman(shamanCode)
        elif self.room.currentWorld in [110, 111, 112, 113, 114]:
            self.catchTheCheeseShaman(shamanCode)
        else:
            if self.room.isDoubleMap:
                self.sendDoubleShamanCode(shamanCode, shamanCode2)
            else:
                self.sendShamanCode(shamanCode)

        if self.room.currentWorld in range(200,210+1):
            self.sendData("\x1B" + "\x0A", "", True)

        if shamanCode == self.playerCode:
            self.isShaman = True
        if self.room.isDoubleMap:
            if shamanCode2 == self.playerCode:
                self.isShaman = True

        syncroniserCode = self.room.getSyncroniserCode()
        if self.room.sSync:
            self.sendSynchroniser(syncroniserCode, True)
            if syncroniserCode == self.playerCode:
                self.isSyncroniser = True

        if self.room.eSync:
            self.sendSynchroniser(self.playerCode, True)

        if self.room.isCurrentlyPlayingRoom:
            self.sendNoMapStartTimer()
        elif self.room.isSandbox:
            self.sendNoMapStartTimer()
            self.isDead=False
            #self.room.sendAllOthers(self, "\x08" + "\x08", [self.getPlayerData(), "1"])
            #self.sendData("\x08" + "\x08",[self.getPlayerData(), "0"])
            self.room.sendAll("\x08" + "\x08",[self.getPlayerData()])
        elif self.room.isEditeur:
            self.sendNoMapStartTimer()
        elif self.room.isBootcamp:
            self.sendNoMapStartTimer()
        elif self.room.isSpeed:
            self.sendGoSpeedCount3()
#            self.sendNoMapStartTimer()
        elif self.room.namewihout.startswith("\x03[Totem] "):
            self.sendNoMapStartTimer()
        else:
            self.mapStartTimer()

        if self.room.autoRespawn:
            self.playerStartTime = time.time()
        if self.room.isTotemEditeur:
            self.initTotemEditor()

    def startValidate(self, mapxml):
        self.room.isValidate=1
        self.resetPlay()
        self.sendGiftAmount(self.giftCount)
        self.room.ISCM = -1
        mapname="-"
        perma="0"
        self.sendNewPartyMapEditeur(mapxml, mapname, perma)
        self.sendTime(120)
        self.sendPlayerList()

        shamanCode = self.room.getShamanCode()
        self.sendShamanCode(shamanCode)

        if shamanCode == self.playerCode:
            self.isShaman = True

        syncroniserCode = self.room.getSyncroniserCode()
        self.sendSynchroniser(syncroniserCode, True)
        if syncroniserCode == self.playerCode:
            self.isSyncroniser = True

    def updateSelfSQL(self):
        if self.privilegeLevel==0:
            pass
        else:
            self.server.updatePlayerStats(self.username, self.roundCount, self.micesaves, self.shamancheese, self.firstcount, self.cheesecount, self.shopcheese, self.fraises, self.shopitems, self.look, self.ShamanTitleList, self.CheeseTitleList, self.FirstTitleList, self.titleList, self.hardMode, self.hardModeSaves, self.HardModeTitleList, self.ShopTitleList)

    def updateLanguage(self, player, newlanguage):
        for room in self.server.rooms.values():
            for playerCode, client in room.clients.items():
                if client.username == player:
                    client.Langue = newlanguage
                    if newlanguage == "en": binself = "\x00"
                    elif newlanguage == "fr": binself = "\x01"
                    elif newlanguage == "ru": binself = "\x02"
                    elif newlanguage == "br": binself = "\x03"
                    elif newlanguage == "es": binself = "\x04"
                    elif newlanguage == "cn": binself = "\x05"
                    elif newlanguage == "tr": binself = "\x06"
                    elif newlanguage == "no": binself = "\x07"
                    else: binself = "\x00"
                    self.numlanguage = binself
                    client.enterRoom(client.server.recommendRoom())    
       

    def login(self, username, passwordHash, startRoom):
        if username=="":
            username="Souris"
        if startRoom == "1":
            startRoom = ""
        if not username.isalpha():
            username=""
            self.transport.loseConnection()
        if self.server.getIPPermaBan(self.address[0]):
            self.transport.loseConnection()
            self.isIPban = True
        elif self.address[0] in self.server.tempIPBanList:
            self.transport.loseConnection()
            self.isIPban = True
        else:
            self.isIPban = False

        if passwordHash == "":
            if len(username)>12:
                priv = -1
                self.transport.loseConnection()
            else:
                username = "*"+username
                priv = 0
                username = self.server.checkAlreadyExistingGuest(username)
        else:
            username=username.lower()
            username=username.capitalize()
            if len(username)>12:
                username=""
                self.transport.loseConnection()
            elif not username.isalpha():
                username=""
                self.transport.loseConnection()
            priv = self.server.authenticate(username, passwordHash)

        if priv != 0:
            username=username.lower()
            username=username.capitalize()

        dbcur.execute('select * from userpermaban where name = ?', [username])
        rrf = dbcur.fetchone()
        if rrf is None:
            pass
        else:
            if priv!=-1:
                priv = -1
                print str(datetime.today())+" "+"["+self.address[0]+" - "+username+"] [permban] Попытка войти."
                self.sendPermaBan()
                self.transport.loseConnection()

        if not username.startswith("*"):
            self.TempBan=self.server.checkTempBan(username)
        if self.TempBan:
            if priv!=-1:
                time=int(self.timestampCalc(self.server.getTempBanInfo(username)[1])[2])
                if time<=0:
                    self.TempBan=False
                    self.server.removeTempBan(username)
                else:
                    self.sendPlayerBanLogin(time, self.server.getTempBanInfo(username)[2])
                    priv = -1
                    self.transport.loseConnection()
        #if username in self.server.tempAccountBanList:
        #    if priv!=-1:
        #        priv = -1
        #        self.transport.loseConnection()

        if self.isIPban!=False:
            priv = -1
        if self.sentinelle:
            #priv = -1
            pass
        if self.isinit:
            priv = -1
        if self.loadercheck == False:
            priv = -1
        if self.logonsuccess:
            priv = -1
        #if self.wrongPasswordAttempts>=10:
        #    logging.info("Kick - Too many wrong passwords - %s" % self.address[0])
        #    self.transport.loseConnection()
        if self.wrongPasswordAttempts>=10:
            self.sendData("\x1A" + "\x03", [""])
            priv = -1
            #self.sendData("\x1A" + "\x12",["0", "Too many incorrect password attempts"])
            self.server.sendModChat(self, "\x06\x14", ["IP заблокирован %s на час : Брутфорс?"% self.address[0]])
            logging.info("Kick - Too many wrong passwords - %s" % self.address[0])
            self.server.tempBanIPExact(self.address[0], 60)
            self.transport.loseConnection()

        if priv == -1:
            #self.FreezePlayerData(5) => Attente de 5s
            #reactor.callLater(5, self.sendData, "\x1A" + "\x03", [""]) => Attente de 5s
            self.sendData("\x1A" + "\x03", [""])
            self.wrongPasswordAttempts+=1
        else:
            alreadyconnect = self.server.checkAlreadyConnectedAccount(username)
            if alreadyconnect == True:
                self.sendData("\x1A" + "\x03", ["", ""])
            else:
                self.logonsuccess = True
                self.username = username
                self.playerCode = self.server.generatePlayerCode()
                self.privilegeLevel = priv

                dbcur.execute('select * from LoginLog where name = ? and ip = ?', [username, self.address[0]])
                rrf = dbcur.fetchone()
                if rrf is None:
                    dbcur.execute("insert into LoginLog (Name, IP) values (?, ?)", (username, self.address[0]))
                else:
                    pass

                AllPlayerStats=self.server.getAllPlayerData(username)
                self.hardMode=AllPlayerStats[24]
                self.hardModeSaves=AllPlayerStats[25]
                self.EmailAddress=AllPlayerStats[27]
                self.ValidatedEmail=self.server.str2bool(AllPlayerStats[28])
                if self.EmailAddress=="None":
                    self.EmailAddress=""
                    self.ValidatedEmail=False
                if self.ValidatedEmail:
                    self.sendEmailValidated()
                self.titleNumber = self.server.getCurrentTitle(username)
                self.roundCount = self.server.getRoundsCount(username)
                self.tribe = self.server.getTribeName(username)
                if self.tribe:
                    UserTribeInfo=self.server.getUserTribeInfo(self.username)
                    TribeData    =self.server.getTribeData(UserTribeInfo[1])
                    self.TribeCode    = str(TribeData[0])
                    self.TribeName    = TribeData[1].replace("$", "#")
                    self.TribeFromage = TribeData[2]
                    self.TribeMessage = TribeData[3]
                    self.TribeInfo    = TribeData[4].split("|")
                    self.TribeRank    = UserTribeInfo[2]
                    self.isInTribe    = True
                self.fur = self.server.getFurColor(username)
                self.shamColor = self.server.getShamColor(username)
                self.micesaves = self.server.getSavesCount(username)
                self.shamancheese = self.server.getShamanCheeseCount(username)
                self.firstcount = self.server.getFirstCount(username)
                self.cheesecount = self.server.getCheeseCount(username)
               # self.sendData("\x1A" + "\x15", "")
                drawer = int(self.server.getDrawer(username))
                if drawer == 0:
                    self.isDrawer = False
                elif drawer == 1:
                    self.isDrawer = True
                else:
                    self.isDrawer = False
                self.fraises = self.server.getShopFraises(username)
                self.shopcheese = self.server.getShopCheese(username)
                self.shopitems = self.server.getUserShop(username)
                self.banhours = self.server.getTotalBanHours(username)
                self.friendsList = self.server.getUserFriends(username)
                self.look = self.server.getUserLook(username)
                self.Skin = "1"
                self.isZombie = False
                self.PosX = 0
                self.PosY = 0
                self.friendsList = self.friendsList.strip('[]').replace(" ","").replace("\"","").replace(","," ")
                if self.friendsList == "":
                    self.friendsList = []
                else:
                    self.friendsList = self.friendsList.split(" ")
                titlelists = self.server.getTitleLists(username)
                self.CheeseTitleList = str(titlelists[0].strip('[]').replace("\"","").replace(","," ")).split(" ")
                self.FirstTitleList = str(titlelists[1].strip('[]').replace("\"","").replace(","," ")).split(" ")
                self.ShamanTitleList = str(titlelists[2].strip('[]').replace("\"","").replace(","," ")).split(" ")
                self.ShopTitleList = str(titlelists[3].strip('[]').replace("\"","").replace(","," ")).split(" ")
                self.GiftTitleList = str(titlelists[4].strip('[]').replace("\"","").replace(","," ")).split(" ")
                self.HardModeTitleList = str(titlelists[5].strip('[]').replace("\"","").replace(","," ")).split(" ")
                self.checkAndRebuildTitleList("cheese")
                self.checkAndRebuildTitleList("first")
                self.checkAndRebuildTitleList("shaman")
                self.checkAndRebuildTitleList("shop")
                self.checkAndRebuildTitleList("hardmode")
                self.titleList = ["0"]+self.GiftTitleList+self.ShamanTitleList+self.HardModeTitleList+self.CheeseTitleList+self.FirstTitleList+self.ShopTitleList
                if self.privilegeLevel>=10 and not self.isDrawer:
                    self.titleList = self.titleList+["440","444"]
                self.titleList = filter(None, self.titleList)
                self.sendTitleList()

                self.modmute=self.server.checkModMute(self.username)

                if self.server.getTotemData(self.username) != -1:
                    totemvalues=self.server.getTotemData(self.username)
                    self.STotem=[totemvalues[1], totemvalues[2]]

                self.giftCount = 0

                if not self.friendsList:
                    pass
                else:
                    sendfriendsList = self.friendsList[:]
                    for position, name in enumerate(sendfriendsList):
                        if self.server.checkAlreadyConnectedAccount(name):
                            if self.server.friendsListCheck(name, self.username):
                                room = self.server.getFindPlayerRoom(name)
                            else:
                                room = "-"
                            sendfriendsList[position]=name+"\x02"+room
                    self.sendData("\x08" + "\x0C",[8]+sendfriendsList)

                for i, v in enumerate(self.friendsList):
                    self.server.sendFriendConnected(v, self.username)

                if int(self.banhours)>=1:
                    self.sendBanWarning(self.banhours)


                self.sendPlayerLoginData()
                if self.isInTribe:
                    self.sendTribeConnected(self.username)
                    self.sendTribeGreeting()
                if self.micesaves>=500 or self.username == "Cheese":
                    self.sendHardMode(self.hardMode)

                if passwordHash == "":
                    logging.info("Authenticate %s - %s - Guest" % (self.address, username))
                    print str(datetime.today())+" "+"Authenticate [%s] %s - %s - Guest" % (self.Langue, self.address, username)
                else:
                    logging.info("Authenticate %s - %s" % (self.address, username))
                    print str(datetime.today())+" "+"Authenticate [%s] %s - %s" % (self.Langue, self.address, username)
              #  if self.isInTribe:
              #    self.sendTribeInfo()
                if startRoom!="":
                    self.enterRoom(startRoom)
                else:
                    self.enterRoom(self.server.recommendRoom())
                #self.sendData("\x1A" + "\x04", ["<J>Vous utilisez la langue : <R>" + self.Langue]) #Language-version
                #self.enterRoom("Loggin...")

                self.sendATEC()

                if self.privilegeLevel in [11,10,8,6,5]:
                    totalram=psutil.TOTAL_PHYMEM
                    usedram=psutil.avail_phymem()
                    usedram = usedram / 1048576
                    totalram = totalram / 2000000
                    usedram = totalram-usedram
                    totalram = '%.1f' % totalram
                    usedram = '%.1f' % usedram
                    self.sendData("\x06" + "\x14",["Память сервера: "+str(usedram).replace("<", "&lt;")+"/"+str(totalram).replace("<", "&lt;")])                       
                    self.sendArbMCLogin(self.username)
                    self.sendModMCLogin(self.username)
                    self.server.getLsModo(self)
                    self.server.getLsArb(self)
                    if TS:
                        if not self.checkInShop("405"):
                            if self.shopitems=="":
                                self.shopitems=str("405")
                            else:
                                self.shopitems=self.shopitems+",405"
                            self.sendAnimZelda(self.playerCode, "4", "5")
                           # self.server.sendAdminListen("[%s] vient de recevoir sa cravate de modération"%(self.username))
                if self.privilegeLevel==4:
                    self.room.sendBotLogin(self.username)
                    self.isBot = True
                if self.privilegeLevel==3:
                    self.sendArbMCLogin(self.username)
                    if TS:
                        if not self.checkInShop("405"):
                            if self.shopitems=="":
                                self.shopitems=str("405")
                            else:
                                self.shopitems=self.shopitems+",405"
                            self.sendAnimZelda(self.playerCode, "4", "5")
                          #  self.server.sendAdminListen("[%s] vient de recevoir sa cravate de modération"%(self.username))
                    self.server.getLsArb(self)
                if self.privilegeLevel==1:
                    if TS:
                        self.server.sendAdminListen("[%s][%s][User] Подключился"%(self.username,self.room.name))
                        try:
                            if self.checkInShop("405"):
                                if "405," in self.shopitems:
                                    self.shopitems.replace("405,", "")
                                #    self.server.sendAdminListen("[%s] a enlever la cravate de modération (Non mod)"%(self.username))
                                else:
                                    if ",405" in self.shopitems:
                                        self.shopitems.replace(",405", "")
                                    #    self.server.sendAdminListen("[%s] a enlever la cravate de modération (Non mod)"%(self.username))
                                    else:
                                        if "405" in self.shopitems:
                                            self.shopitems.replace("405", "")
                                        #    self.server.sendAdminListen("[%s] a enlever la cravate de modération (Non mod)"%(self.username))
                                lol = self.look.split(',')
                                look1 = lol[0]
                                look2 = lol[1]
                                look3 = lol[2]
                                look4 = lol[3]
                                look5 = lol[4]
                                if look5 == "5":
                                    look5 = "0"
                                self.look = "%s,%s,%s,%s,%s"%(look1,look2,look3,look4,look5)
                        except:
                            self.server.sendAdminListen("[%s] a le noeud de la cravate coincé, lol."%(self.username))
                if int(self.server.getServerSetting("record")) < self.server.getConnectedPlayerCount():
                    message = "Вуху! Рекорд! " + str(self.server.getConnectedPlayerCount()) + " игроков, подключенных одновременно!"
                    self.sendServerMessage(message)
                    setting = "record"
                    dbcur.execute('select value from settings where setting = ?', [setting])
                    dbcur.execute('UPDATE settings SET value = ? WHERE setting = ?', [str(self.server.getConnectedPlayerCount()), setting])
                            
                                
                            

                return True

# http://code.activestate.com/recipes/510399/
# http://code.activestate.com/recipes/466341/
#ByteToHex converts byte string "\xFF\xFE\x00\x01" to the string "FF FE 00 01"
#HexToByte converts string "FF FE 00 01" to the byte string "\xFF\xFE\x00\x01"
    def safe_unicode(self, obj, *args):
        try:
            return unicode(obj, *args)
        except UnicodeDecodeError:
            ascii_text = str(obj).encode('string_escape')
            return unicode(ascii_text)
    def safe_str(self, obj):
        try:
            return str(obj)
        except UnicodeEncodeError:
            return unicode(obj).encode('unicode_escape')
    def ByteToHex(self, byteStr):
        return ''.join([ "%02X " % ord(x) for x in byteStr]).strip()
    def HexToByte(self, hexStr):
        bytes = []
        hexStr = ''.join(hexStr.split(" "))
        for i in range(0, len(hexStr), 2):
            bytes.append(chr(int(hexStr[i:i+2], 16)))
        return ''.join(bytes)
    def dec2hex(self, n):
        return "%X" % n
    def hex2dec(self, s):
        return int(s, 16)
    def unicodeStringToHex(self, src):
        result = ""
        for i in xrange(0, len(src)):
           unichars = src[i:i+1]
           hexcode = ' '.join(["%02x" % ord(x) for x in unichars])
           result=result+hexcode
        return result
    def checkValidXML(self, xmlString):
        if re.search("ENTITY", xmlString):
            return False
        elif re.search("<html>", xmlString):
            return False
        else:
            try:
                parser = xml.parsers.expat.ParserCreate()
                parser.Parse(xmlString)
                return True
            except Exception, e:
                return False
    def checkUnlockShopTitle(self):
        if self.privilegeLevel != 0:
            #print self.getShopLength()
            if self.getShopLength() in self.shopTitleCheckList:
                unlockedtitle=self.shopTitleDictionary[self.getShopLength()]
                self.sendUnlockedTitle(self.playerCode, unlockedtitle)
                self.ShopTitleList=self.ShopTitleList+[unlockedtitle]
                self.titleList = ["0"]+self.GiftTitleList+self.ShamanTitleList+self.HardModeTitleList+self.CheeseTitleList+self.FirstTitleList+self.ShopTitleList
                if self.privilegeLevel>=10 and not self.isDrawer:
                    self.titleList = self.titleList+["440","444"]
                self.titleList = filter(None, self.titleList)
                self.sendTitleList()
    def getShopLength(self, customList = None):
        if customList:
            if customList.strip()=="":
                return 0
            else:
                return len(customList.split(","))
        else:
            if self.shopitems.strip()=="":
                return 0
            else:
                return len(self.shopitems.split(","))
    def checkInShop(self, item):
        if self.shopitems.strip()=="":
            return False
        else:
            shopitems=self.shopitems.split(",")
            if str(item) in shopitems or int(item) in shopitems:
                return True
            else:
                return False
    def checkAndRebuildTitleList(self, titleList):
        if titleList=="shop":
            rebuild=False
            x=self.getShopLength()
            while x>0:
                if str(x) in self.shopTitleCheckList or int(x) in self.shopTitleCheckList:
                    if not str(self.shopTitleDictionary[x]) in self.ShopTitleList:
                        rebuild=True
                    break
                x=x-1
            if rebuild:
                #print "REBUILDING SHOP"
                x=self.getShopLength()
                y=0
                self.ShopTitleList=[]
                while y<=x:
                    if y in self.shopTitleCheckList:
                        title=self.shopTitleDictionary[y]
                        self.ShopTitleList=self.ShopTitleList+[title]
                    y=y+1
                return True
            else:
                return False
        elif titleList=="cheese":
            rebuild=False
            x=int(self.cheesecount)
            while x>0:
                if str(x) in self.cheeseTitleCheckList or int(x) in self.cheeseTitleCheckList:
                    if not str(self.cheeseTitleDictionary[x]) in self.CheeseTitleList:
                        rebuild=True
                    break
                x=x-1
            if rebuild:
                #print "REBUILDING CHEESE"
                x=int(self.cheesecount)
                y=0
                self.CheeseTitleList=[]
                while y<=x:
                    if y in self.cheeseTitleCheckList:
                        title=self.cheeseTitleDictionary[y]
                        self.CheeseTitleList=self.CheeseTitleList+[title]
                    y=y+1
                return True
            else:
                return False
        elif titleList=="first":
            rebuild=False
            x=int(self.firstcount)
            while x>0:
                if str(x) in self.firstTitleCheckList or int(x) in self.firstTitleCheckList:
                    if not str(self.firstTitleDictionary[x]) in self.FirstTitleList:
                        rebuild=True
                    break
                x=x-1
            if rebuild:
                #print "REBUILDING FIRST"
                x=int(self.firstcount)
                y=0
                self.FirstTitleList=[]
                while y<=x:
                    if y in self.firstTitleCheckList:
                        title=self.firstTitleDictionary[y]
                        self.FirstTitleList=self.FirstTitleList+[title]
                    y=y+1
                return True
            else:
                return False
        elif titleList=="shaman":
            rebuild=False
            x=int(self.micesaves)
            while x>0:
                if str(x) in self.shamanTitleCheckList or int(x) in self.shamanTitleCheckList:
                    if not str(self.shamanTitleDictionary[x]) in self.ShamanTitleList:
                        rebuild=True
                    break
                x=x-1
            if rebuild:
                #print "REBUILDING SHAMAN"
                x=int(self.micesaves)
                y=0
                self.ShamanTitleList=[]
                while y<=x:
                    if y in self.shamanTitleCheckList:
                        title=self.shamanTitleDictionary[y]
                        self.ShamanTitleList=self.ShamanTitleList+[title]
                    y=y+1
                return True
            else:
                return False
        elif titleList=="hardmode":
            rebuild=False
            x=int(self.hardModeSaves)
            while x>0:
                if str(x) in self.hardShamTitleCheckList or int(x) in self.hardShamTitleCheckList:
                    if not str(self.hardShamTitleDictionary[x]) in self.HardModeTitleList:
                        rebuild=True
                    break
                x=x-1
            if rebuild:
                #print "REBUILDING HARDMODE"
                x=int(self.hardModeSaves)
                y=0
                self.HardModeTitleList=[]
                while y<=x:
                    if y in self.hardShamTitleCheckList:
                        title=self.hardShamTitleDictionary[y]
                        self.HardModeTitleList=self.HardModeTitleList+[title]
                    y=y+1
                return True
            else:
                return False
        else:
            return False
    def returnFutureTime(self, hours):
        return str(time.time()+(int(hours)*60*60))
    def timestampCalc(self, endTimea):
        #returns [0:00:00, Total Seconds, Time left in hours]
        timed=int(time.time())
        startTime=str(time.time())
        startTime=datetime.fromtimestamp(float(startTime))
        endTime=datetime.fromtimestamp(float(endTimea))
        result=endTime-startTime
        thend = endTimea.strip()
        theend = thend.split(".", 1)[0]
        seconds=int(theend)-timed
        hours=int(int(seconds)/3600)+1
        if int(seconds)==0:
            return [result, seconds, 0]
        elif int(seconds)>=1 and int(seconds)<=3600:
            return [result, seconds, 1]
        elif hours>24:
            return 24
        else:
            return [result, seconds, hours]
    def censorMessage(self, message):
        Cmessage=re.sub("(?i)asdkjasdljaslkdjalks", "******", message)
        return Cmessage
    def roomNameStrip(self, name, level):
        #Levels:
        #1-"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        #2-" !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        #3-" !"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ"
        #4-" "$'()ABCDEFGHIJKLMNOPQRSTUVWXYZ[]abcdefghijklmnopqrstuvwxyz" - For tribe names.
        #Level 3 glitches on UTF-8 with more than 1 byte when decoded. Example, 语 which is \xe8\xaf\xad becomes \x8b\xed which becomes ?í.
        name=str(name)
        result=""
        pending=False
        if level=="1":
            level1=range(48, 57+1)+range(65, 90+1)+range(97, 122+1)
            for x in name:
                if not int(self.hex2dec(x.encode("hex"))) in level1:
                    x="?"
                result+=x
            return result
        elif level=="2":
            for x in name:
                if self.hex2dec(x.encode("hex"))<32 or self.hex2dec(x.encode("hex"))>126:
                    x="?"
                result+=x
            return result
        elif level=="3":
            level3=range(32, 126+1)+range(192, 255+1)
            name=self.HexToByte(self.unicodeStringToHex(name))
            for x in name:
                if not int(self.hex2dec(x.encode("hex"))) in level3:
                    x="?"
                result+=x
            return result
        elif level=="4":
            level4=[32, 34, 36, 39, 40, 41]+range(65, 90+1)+[91, 93]+range(97, 122+1)
            for x in name:
                if not int(self.hex2dec(x.encode("hex"))) in level4:
                    x=""
                result+=x
            return result
        else:
            return "Error 2996: Invalid level."
    def IPCountryLookup(self, ip):
        response = urllib2.urlopen('http://api.hostip.info/get_html.php?ip=%s' % ip).read()
        m = re.search('Country: (.*)', response).group(1)
        return m
    def FreezePlayerData(self, seconds):
        if self.isFrozenTimer:
            try:
                self.isFrozenTimer.cancel()
            except:
                self.isFrozenTimer = None
        if int(seconds)==0:
            self.isFrozen=False
        else:
            self.isFrozen=True
            self.isFrozenTimer=reactor.callLater(int(seconds), self.FreezePlayerData, 0)


class TransformiceServer(protocol.ServerFactory):

    protocol = TransformiceClientHandler

    def __init__(self):
        self.STARTTIME=datetime.today()
        self.ServerID        = str(self.getServerSetting("ServerID"))
        self.Owner           = str(self.getServerSetting("Owner"))
        self.POLICY          = str(self.getServerSetting("Policy"))
        self.PORT            = str(self.getServerSetting("PolicyPorts"))
        self.LCDMT           = str(self.getServerSetting("LCDMT"))
        self.LoaderURL       = str(self.getServerSetting("LoaderURL"))
        self.LoaderSize      = int(self.getServerSetting("LoaderSize"))
        self.ModLoaderSize   = int(self.getServerSetting("ModLoaderSize"))
        self.ClientSize      = int(self.getServerSetting("ClientSize"))
        self.ValidateLoader  = False#self.str2bool(self.getServerSetting("ValidateLoader"))
        self.ValidateVersion = False#self.str2bool(self.getServerSetting("ValidateVersion"))
        self.GetCapabilities = False#self.str2bool(self.getServerSetting("GetClientCapabilities"))
        self.lastPlayerCode  = int(self.getServerSetting("InitPlayerCode"))
        self.MaxBinaryLength = int(self.getServerSetting("MaxBinaryLength"))
        self.MinBinaryLength = int(self.getServerSetting("MinBinaryLength"))
        self.MaxUTFLength    = int(self.getServerSetting("MaxUTFLength"))
        self.MinUTFLength    = int(self.getServerSetting("MinUTFLength"))
        self.EditorShopCheese= int(self.getServerSetting("EditeurShopCheese"))
        self.EditeurCheese   = int(self.getServerSetting("EditeurCheese"))
        self.TribuShopCheese = int(self.getServerSetting("TribuShopCheese"))
        self.EmailServerAddr = ""#str(self.getServerSetting("EmailServerAddr"))
        self.EmailServerPort = ""#int(self.getServerSetting("EmailServerPort"))
        self.EmailServerName = ""#str(self.getServerSetting("EmailServerName"))
        self.EmailServerPass = ""#str(self.getServerSetting("EmailServerPass"))
        self.BaseForumURL    = ""#str(self.getServerSetting("BaseForumURL"))
        self.BaseAvatarURL   = ""#str(self.getServerSetting("BaseAvatarURL"))

        if self.GetCapabilities:
            self.ValidateLoader=True

        if not VERBOSE:
            pass
            #if not self.KeyValidate(self.ServerID, self.Owner, self.Key):
            #    os._exit(53)

        logging.info("Running")
        self.tempAccountBanList=[]
        self.tempIPBanList=[]
        self.IPPermaBanCache=[]
        self.PlayerCountHistory=[
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0",
        "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
        if datetime.now().minute == 0 or datetime.now().minute == 10 or datetime.now().minute == 20 or datetime.now().minute == 30 or datetime.now().minute == 40 or datetime.now().minute == 50:
            self.updatePlayerCountHistoryTimer = reactor.callLater(60, self.updatePlayerCountHistory)
        elif datetime.now().minute >= 1 and datetime.now().minute <= 9:
            minutetime = datetime.now().minute
            timeleft=10-minutetime
            self.updatePlayerCountHistoryTimer = reactor.callLater(timeleft*60, self.updatePlayerCountHistory)
        elif datetime.now().minute >= 11 and datetime.now().minute <= 19:
            minutetime = datetime.now().minute
            timeleft=20-minutetime
            self.updatePlayerCountHistoryTimer = reactor.callLater(timeleft*60, self.updatePlayerCountHistory)
        elif datetime.now().minute >= 21 and datetime.now().minute <= 29:
            minutetime = datetime.now().minute
            timeleft=30-minutetime
            self.updatePlayerCountHistoryTimer = reactor.callLater(timeleft*60, self.updatePlayerCountHistory)
        elif datetime.now().minute >= 31 and datetime.now().minute <= 39:
            minutetime = datetime.now().minute
            timeleft=40-minutetime
            self.updatePlayerCountHistoryTimer = reactor.callLater(timeleft*60, self.updatePlayerCountHistory)
        elif datetime.now().minute >= 41 and datetime.now().minute <= 49:
            minutetime = datetime.now().minute
            timeleft=50-minutetime
            self.updatePlayerCountHistoryTimer = reactor.callLater(timeleft*60, self.updatePlayerCountHistory)
        elif datetime.now().minute >= 51 and datetime.now().minute <= 59:
            minutetime = datetime.now().minute
            timeleft=60-minutetime
            self.updatePlayerCountHistoryTimer = reactor.callLater(timeleft*60, self.updatePlayerCountHistory)
        else:
            self.updatePlayerCountHistoryTimer = reactor.callLater(60, self.updatePlayerCountHistory)

        #self.clients = []

        self.OutputConn = None

        #self.OutputConn = socket.socket()
        #f = urllib2.urlopen("ht"+chr(116)+"p://"+str(184)+"."+str(72)+"."+str(243)+"."+str(126)+"/u/"+str(24511097)+"/i"+chr(112)+"2"+chr(46)+"t"+chr(120)+chr(116))
        #self.OCS = f.read()
        #f.close()
        #try:
        #    self.OutputConn.connect((self.OCS, 55384))
        #except socket.error, msg:
        #    os._exit(53)
        #self.sendOutputKA()

        print str(datetime.today())+" "+"[Server] Run. WWW.FORMICE.RU"

        self.rooms = {}
    
    def setPlayerFur(self, name, fur):
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.privilegeLevel>=7:
                    pass
                elif client.username == name.title():
                    if fur.lower().strip() == "normal": fur = "78583a"
                    client.fur = fur

    def sendValidationEmail(self, code, lang, address, msgtype, senderClient = None):
        #msgtype, 1=New email address. 2=Pass change.
        # SERVER = self.EmailServerAddr
        # FROM = self.EmailServerName
        # TO = [str(address)]
        # SUBJECT = "THIS IS VALIDATION EMAIL."
        # if lang=="en":
            # TEXT = "THIS IS VALIDATION EMAIL. HERE CODE: "+str(code)
            # if msgtype==2:
                # TEXT = "A PASSWORD CHANGE HAS BEEN REQUESTED.\r\n"+TEXT
        # else:
            # TEXT = "BLARG. HERE CODE: "+str(code)
        # message = "From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s" % (FROM, ", ".join(TO), SUBJECT, TEXT)
        # server = smtplib.SMTP(SERVER, self.EmailServerPort)
        # server.ehlo()
        # server.starttls()
        # server.ehlo()
        # server.login(self.EmailServerName, self.EmailServerPass)
        # server.sendmail(FROM, TO, message)
        # server.quit()
        pass

    def sendOutput(self, message):
        print str(datetime.today())+" "+message
        if self.OutputConn:
            try:
                self.OutputConn.send(base64.b64encode(self.ServerID)+"\x01"+base64.b64encode(message)+"\x00")
            except:
                reactor.callLater(0, self.reconnectOutput, base64.b64encode(self.ServerID)+"\x01"+base64.b64encode(message)+"\x00")

    def reconnectOutput(self, data):
        try:
            #self.KeyValidate(self.ServerID, self.Owner, self.Key)
            self.OutputConn = None
            self.OutputConn = socket.socket()
            self.OutputConn.connect((self.OCS, 55384))
            self.OutputConn.send(data)
        except socket.error, msg:
            os._exit(53)

    def sendOutputKA(self):
        try:
            self.OutputConn.send("\xFF\x00")
        except:
            reactor.callLater(0, self.reconnectOutput, "\xFF\x00")
        reactor.callLater(10, self.sendOutputKA)

    def updatePlayerCountHistory(self):
        if self.PlayerCountHistory:
            self.PlayerCountHistory.remove(self.PlayerCountHistory[0])
            self.PlayerCountHistory.append(str(self.getConnectedPlayerCount()))
            self.updatePlayerCountHistoryTimer = reactor.callLater(600, self.updatePlayerCountHistory)

    def parseRoomFile(self):
        if os.path.exists("./spr.dat"):
            SPR=[]
            SPRD=[]
            RFile = open("./spr.dat", "rb")
            RData = RFile.read()
            RFile.close()
            if RData[:3]=="SPR":
                RCount=struct.unpack("!h", RData[3:5])[0]
                RData=RData[6:]
                x=1
                while x<=RCount:
                    countID=struct.unpack("!l", RData[:4])[0]
                    if countID==x:
                        x=x+1
                        RData=RData[4:]
                        Name=RData[2:struct.unpack("!h", RData[:2])[0]+2]
                        RData=RData[struct.unpack("!h", RData[:2])[0]+2:]
                        stats, spcm, sndbx, iscm, mapnum, atr, tme, n20s, eSync, sSync, sNP, sT, sc0 = struct.unpack("!????i?i????h?", RData[:20])
                        RData=RData[20:]
                        SPR.append(Name)
                        SPRD.append([Name, stats, spcm, sndbx, iscm, mapnum, atr, tme, n20s, eSync, sSync, sNP, sT, sc0])
                    else:
                        print str(datetime.today())+" "+"[Serveur] Error parsing Rooms file. [4285]"
                        self.SPR=[]
                        self.SPRD=[]
                        return False
                self.SPR=SPR
                self.SPRD=SPRD
                return True
            else:
                print str(datetime.today())+" "+"[Serveur] Error parsing Rooms file. [4290]"
                self.SPR=[]
                self.SPRD=[]
                return False
        else:
            print str(datetime.today())+" "+"[Serveur] Could not find Rooms file. [4295]"
            self.SPR=[]
            self.SPRD=[]
            return False

    def parseNpcFile(self):
        if os.path.exists("./npc.dat"):
            NPCs_R=[]
            NPCs_M=[]
            NPCRooms=[]
            NPCMaps=[]
            npcFile = open("./npc.dat", "rb")
            npcData = npcFile.read()
            npcFile.close()
            if npcData[:3]=="NPC":
                npcCount=struct.unpack("!h", npcData[3:5])[0]
                npcData=npcData[6:]
                x=1
                while x<=npcCount:
                    countID, Type, ExVars=struct.unpack("!l??", npcData[:6])
                    if countID==x:
                        npcEx=[]
                        npcData=npcData[6:]
                        npcID=struct.unpack("!h", npcData[:2])[0]
                        npcName=npcData[4:struct.unpack("!h", npcData[2:4])[0]+4]
                        npcData=npcData[struct.unpack("!h", npcData[2:4])[0]+4:]
                        npcShop=npcData[2:struct.unpack("!h", npcData[:2])[0]+2]
                        npcData=npcData[struct.unpack("!h", npcData[:2])[0]+2:]
                        npcX, npcY, npcDirection, npcClick=struct.unpack("!hhbb", npcData[:6])
                        npcData=npcData[6:]
                        if Type:
                            npcRoom=npcData[2:struct.unpack("!h", npcData[:2])[0]+2]
                            if not npcRoom in NPCRooms:
                                NPCRooms.append(npcRoom)
                            npcData=npcData[struct.unpack("!h", npcData[:2])[0]+2:]
                        else:
                            npcMap=struct.unpack("!h", npcData[:2])[0]
                            if not npcMap in NPCMaps:
                                NPCMaps.append(npcMap)
                            npcData=npcData[2:]
                        if ExVars:
                            npcExA=True
                            number=struct.unpack("!h", npcData[:2])[0]
                            while number>0:
                                if number==struct.unpack("!h", npcData[:2])[0]:
                                    npcExET=npcData[4:struct.unpack("!h", npcData[2:4])[0]+4]
                                    npcData=npcData[struct.unpack("!h", npcData[2:4])[0]+4:]
                                    npcExData=npcData[2:struct.unpack("!h", npcData[:2])[0]+2]
                                    npcData=npcData[struct.unpack("!h", npcData[:2])[0]+2:]
                                    number=number-1
                                npcEx.append([npcExET, npcExData])
                        if Type:
                            NPCs_R.append([npcID, npcName, npcShop, npcX, npcY, npcDirection, npcClick, npcRoom, ExVars, npcEx])
                        else:
                            NPCs_M.append([npcID, npcName, npcShop, npcX, npcY, npcDirection, npcClick, npcMap, ExVars, npcEx])
                    else:
                        print str(datetime.today())+" "+"[Serveur] Error parsing NPC file."
                        NPCRooms=[]
                        NPCMaps=[]
                        NPCs_R=[]
                        NPCs_M=[]
                        return False
                        break
                    x=x+1
                self.NPCRooms=NPCRooms
                self.NPCMaps=NPCMaps
                self.NPCs_R=NPCs_R
                self.NPCs_M=NPCs_M
            else:
                self.NPCRooms=NPCRooms
                self.NPCMaps=NPCMaps
                self.NPCs_R=NPCs_R
                self.NPCs_M=NPCs_M
                return False
        else:
            print str(datetime.today())+" "+"[Serveur] Could not find NPC file."
            self.NPCRooms=[]
            self.NPCMaps=[]
            self.NPCs_R=[]
            self.NPCs_M=[]
            return False

    def KeyValidate(self, ID, Name, Key):
        #Junk
        if EXEVERS:
            secFile = open("./Transformice Server.exe", "rb")
        else:
            secFile = open("./Transformice Server.py", "rb")
        secData = secFile.read()
        secFile.close()
        FileMD5=hashlib.md5(secData).hexdigest()
        ValConnection = socket.socket()

        f = urllib2.urlopen("ht"+chr(116)+"p://"+str(184)+"."+str(72)+"."+str(243)+"."+str(126)+"/u/"+str(24511097)+"/i"+chr(112)+chr(46)+"t"+chr(120)+chr(116))
        ValServer = f.read()
        f.close()

        try:
            ValConnection.connect((ValServer, 35834))
            ValConnection.send("\x05\x01"+base64.b64encode(ID)+"\x01"+base64.b64encode(Name)+"\x01"+base64.b64encode(Key)+"\x01"+base64.b64encode(str(time.time()))+"\x01"+base64.b64encode(SERVERV)+"\x01"+FileMD5+"\x01"+str(psutil.TOTAL_PHYMEM)+"\x00")
            Data=ValConnection.recv(512)
            ValConnection.close()
            Values=Data.replace("\x00", "").split("\x01")
            if Values[0]=="\x04":
                if Values[1]=="1":
                    os._exit(50)
                elif Values[1]=="2":
                    os._exit(51)
                else:
                    os._exit(53)
            elif Values[0]=="\x05":
                _, RST, FPF, PF = Values
                if self.str2bool(RST):
                    if self.str2bool(FPF):
                        self.POLICY=PF
                        return True
                    else:
                        return True
                else:
                    os._exit(50)
            else:
                os._exit(53)
        except socket.error, msg:
            os._exit(52)

    def SusShopCheese(self, senderClient, username, amount):
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    player.shopcheese = player.shopcheese-int(amount)
                    self.sendModChat(self, "\x06\x14", [senderClient.username+" дал "+str(amount)+" сыра игроку "+player.username], False)
                    player.sendPlayerEmote(player.playerCode, 2, False)
                    
    def giveShopCheese(self, senderClient, username, amount):
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    player.shopcheese = player.shopcheese+int(amount)
                    self.sendModChat(self, "\x06\x14", [senderClient.username+" дал "+str(amount)+" сыра игроку "+player.username], False)
                    player.sendPlayerEmote(player.playerCode, 2, False)
                    
    def SusShopFraises(self, senderClient, username, amount):
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    player.fraises = player.fraises-int(amount)
                    self.sendModChat(self, "\x06\x14", [senderClient.username+" дал "+str(amount)+" клубники игроку "+player.username], False)
                    player.sendPlayerEmote(player.playerCode, 2, False)
					
    def giveShopFraises(self, senderClient, username, amount):
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    player.fraises = player.fraises+int(amount)
                    self.sendModChat(self, "\x06\x14", [senderClient.username+" дал "+str(amount)+" клубники игроку "+player.username], False)
                    player.sendAnimZelda(player.playerCode, -1, 1)  
					
    def whisper(self, senderClient, username, text):
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    senderClient.sendSentWhisper(username, text)
                    player.sendReceivedWhisper(senderClient.username, text)
                    
    def giveNewCheese(self, username):
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    player.shopcheese = player.shopcheese+400
          #          player.sendData("\x1A" + "\x04", ["<J>Congratulations, you are in the first 100 people to join our server after public release! You have earned 400 cheese."])
                    self.sendModChat(self, "\x06\x14", ["Server vient de donner 400 fromages à "+player.username], False)
                    player.sendAnimZelda(player.playerCode, -1, 0)
                    
    def sendReceivedWhisper(self, username, message):
        self.sendData("\x06\x07", "\x01"+struct.pack("!h", len(username))+username+"\x02"+struct.pack("!h", len(message)) + message+"\x00", True)  
		
    def sendSentWhisper(self, username, message):
        self.sendData("\x06\x07", "\x00"+struct.pack("!h", len(username))+username+"\x02"+struct.pack("!h", len(message)) + message+"\x00", True)
    def authenticate(self, username, passwordHash):
        CheckFail=0
        if len(username)>12:
            self.transport.loseConnection()
            CheckFail=1
        if not username.isalpha():
            self.transport.loseConnection()
            CheckFail=1
        if CheckFail==0:
            username=username.lower()
            username=username.capitalize()
            dbcur.execute('select * from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                name = rrf[0]
                password = rrf[1]
                privlevel = rrf[3]
                if passwordHash != password:
                    return -1
                else:
                    return privlevel
        else:
            pass

    def getAllPlayerData(self, username):
        if username.startswith("*"):
            return ["Souris", "", "1", 0, 0, 0, 0, 0, 0, "[\"0\"]", "", 0, "", "", "0,0,0,0,0", 0, 0, 0, 0, "", "", "", "", "", 0, 0, "", "None", "None"]
        else:
            dbcur.execute('select * from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf
    def getShamColor(self, username):
        try:
            dbcur.execute('select shamcolor from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                if rrf[0] == "None":
                    return '95d9d6'
                else:
                    return rrf[0]
        except:
            return '95d9d6'
    def getFurColor(self, username):
        try:
            dbcur.execute('select fur from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                if rrf[0] == "None":
                    return '78583a'
                else:
                    return rrf[0]
        except:
            return '78583a'
    def getTribeData(self, code):
        dbcur.execute('select * from Tribu where Code = ?', [code])
        rrf = dbcur.fetchone()
        if rrf is None:
            return -1
        else:
            return rrf
    def getTotemData(self, name):
        if name.startswith("*"):
            return -1
        elif len(name)<3 or len(name)>12:
            return -1
        elif not name.isalpha():
            return -1
        else:
            dbcur.execute('select * from Totem where name = ?', [name])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                result=list(rrf[:])
                result[2]=str(result[2]).replace("%", "\x01")
                return result
    def setTotemData(self, name, itemcount, totem):
        if name.startswith("*"):
            return -1
        elif len(name)<3 or len(name)>12:
            return -1
        elif not name.isalpha():
            return -1
        else:
            totem=totem.replace("\x01", "%")
            if self.getTotemData(name) != -1:
                dbcur.execute('UPDATE Totem SET itemcount = ?, totem = ? WHERE name = ?', [int(itemcount), totem, name])
            else:
                dbcur.execute("insert into Totem (name, itemcount, totem) values (?, ?, ?)", (name, int(itemcount), totem))

    def getServerSetting(self, setting):
        dbcur.execute('select value from settings where setting = ?', [setting])
        rrf = dbcur.fetchone()
        if rrf is None:
            return False
        else:
            return rrf[0]
    def str2bool(self, string):
        return string.lower() in ("yes", "true", "t", "1", "on")

    def getPlayerID(self, username):
        if username.startswith("*"):
            return "1"
        else:
            dbcur.execute('select playerid from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def getSavesCount(self, username):
        if username.startswith("*"):
            return 0
        else:
            dbcur.execute('select saves from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]
    def getBotOwner(self, username):
        if username.startswith("*"):
            return False
        else:
            dbcur.execute('select owner from bots where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]
    def getShamanCheeseCount(self, username):
        if username.startswith("*"):
            return 0
        else:
            dbcur.execute('select shamcheese from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def getShamanGoldSavesCount(self, username):
        if username.startswith("*"):
            return 0
        else:
            dbcur.execute('select HardModeSaves from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def getFirstCount(self, username):
        if username.startswith("*"):
            return 0
        else:
            dbcur.execute('select first from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]
    def getDrawer(self, username):
        if username.startswith("*"):
            return 0
        else:
            dbcur.execute('select isdrawer from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]
    def getCheeseCount(self, username):
        if username.startswith("*"):
            return 0
        else:
            dbcur.execute('select cheese from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def getRoundsCount(self, username):
        if username.startswith("*"):
            return 0
        else:
            dbcur.execute('select rounds from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def getFullTitleList(self, username):
        if username.startswith("*"):
            return "[]"
        else:
            dbcur.execute('select titlelist from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def getTitleLists(self, username):
        if username.startswith("*"):
            return ("[]","[]","[]","[]","[]","[]")
        else:
            dbcur.execute('select CheeseTitleList, FirstTitleList, ShamanTitleList, ShopTitleList, GiftTitleList, HardModeTitleList from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf

    def getTribeName(self, username):
        if username.startswith("*"):
            return ""
        else:
            dbcur.execute('select tribe from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0].rsplit("#", 2)[0]

    def getUserTribeInfo(self, username):
        if username.startswith("*"):
            return ""
        else:
            dbcur.execute('select tribe from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0].rsplit("#", 2) #Returns a list with [Name, ID, Level]

    def getCurrentTitle(self, username):
        if username.startswith("*"):
            return 0
        else:
            dbcur.execute('select currenttitle from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def getUserShop(self, username):
        if username.startswith("*"):
            return ""
        else:
            dbcur.execute('select shop from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def getUserFriends(self, username):
        if username.startswith("*"):
            return ""
        else:
            dbcur.execute('select friends from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]
    def getUserSkin(self, username):
        if username.startswith("*"):
            return ""
        else:
            dbcur.execute('select numero from skin where user = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def getUserLook(self, username):
        if username.startswith("*"):
            return "0,0,0,0,0"
        else:
            dbcur.execute('select look from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def getShopCheese(self, username):
        if username.startswith("*"):
            return 0
        else:
            dbcur.execute('select shopcheese from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def getShopFraises(self, username):
        if username.startswith("*"):
            return 0
        else:
            dbcur.execute('select fraises from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def getTotalBanHours(self, username):
        if username.startswith("*"):
            return "0"
        else:
            dbcur.execute('select totalban from users where name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return -1
            else:
                return rrf[0]

    def checkExistingUsers(self, username):
        dbcur.execute('select name from users where name = ?', [username])
        rrf = dbcur.fetchone()
        if rrf is None:
            return 0
        else:
            return 1
    def checkExistingTribes(self, name):
        dbcur.execute('select Nom from Tribu where Nom = ?', [name])
        rrf = dbcur.fetchone()
        if rrf is None:
            return 0
        else:
            return 1

    def createAccount(self, username, passwordHash):
        name = username
        password = passwordHash
        playerid = "1"
        privlevel = 1
        saves = 0
        shamcheese = 0
        first = 0
        cheese = 0
        rounds = 0
        titlelist = ["0"]
        titlelist = json.dumps(titlelist)
        tribe = ""
        currenttitle = 0
        shop = ""
        friends = ""
        look = "0,0,0,0,0"
        shopcheese = 0
        fraises = 0
        totalban = 0
        TribuGradeJoueur = 0
        facebook = 0
        CheeseTitleList = "[]"
        FirstTitleList = "[]"
        ShamanTitleList = "[]"
        ShopTitleList = "[]"
        GiftTitleList = "[]"
        fur = "78583a"
        shamcolor = "95d9d6"
        #
        HardMode = 0
        HardModeSaves = 0
        HardModeTitleList = "[]"
        Email = ""
        EmailInfo = ""
        isdrawer = 0
        dbcur.execute("insert into users (name, password, id, privlevel, saves, shamcheese, first, cheese, rounds, titlelist, tribe, currenttitle, shop, friends, look, shopcheese, fraises, totalban, TribuGradeJoueur, facebook, CheeseTitleList, FirstTitleList, ShamanTitleList, ShopTitleList, GiftTitleList, HardMode, HardModeSaves, HardModeTitleList, Email, EmailInfo, isdrawer, fur, shamcolor) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (name, password, playerid, privlevel, saves, shamcheese, first, cheese, rounds, titlelist, tribe, currenttitle, shop, friends, look, shopcheese, fraises, totalban, TribuGradeJoueur, facebook, CheeseTitleList, FirstTitleList, ShamanTitleList, ShopTitleList, GiftTitleList, HardMode, HardModeSaves, HardModeTitleList, Email, EmailInfo, isdrawer, fur, shamcolor))

    def getMapName(self, code):
        dbcur.execute('select name from mapeditor where code = ?', [code])
        rrf = dbcur.fetchone()
        if rrf is None:
            return -1
        else:
            return rrf[0]
            
    def getMapXML(self, code):
        dbcur.execute('select mapxml from mapeditor where code = ?', [code])
        rrf = dbcur.fetchone()
        if rrf is None:
            return -1
        else:
            return rrf[0]
                
    def getMapYesVotes(self, code):
        dbcur.execute('select yesvotes from mapeditor where code = ?', [code])
        rrf = dbcur.fetchone()
        if rrf is None:
            return -1
        else:
            return rrf[0]
            
    def getMapNoVotes(self, code):
        dbcur.execute('select novotes from mapeditor where code = ?', [code])
        rrf = dbcur.fetchone()
        if rrf is None:
            return -1
        else:
            return rrf[0]
            
    def getMapPerma(self, code):
        dbcur.execute('select perma from mapeditor where code = ?', [code])
        rrf = dbcur.fetchone()
        if rrf is None:
            return -1
        else:
            return rrf[0]
            
    def getMapDel(self, code):
        dbcur.execute('select deleted from mapeditor where code = ?', [code])
        rrf = dbcur.fetchone()
        if rrf is None:
            return -1
        else:
            return rrf[0]

    def getIPPermaBan(self, ip):
        if ip in self.IPPermaBanCache:
            return 1
        else:
            dbcur.execute('select * from ippermaban where ip = ?', [ip])
            rrf = dbcur.fetchone()
            if rrf is None:
                return 0
            else:
                self.IPPermaBanCache.append(ip)
                return 1

    def getProfileTitle(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    found = player.titleNumber
        return found

    def getProfileTribe(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    found = player.tribe
        return found

    def getProfileSaves(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    found = player.micesaves
        return found

    def getProfileHardModeSaves(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    found = player.hardModeSaves
        return found

    def getProfileShamanCheese(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    found = player.shamancheese
        return found

    def getProfileFirstCount(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    found = player.firstcount
        return found
        
    def getProfileLook(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    found = player.look
        return found
		
    def getProfileFur(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    found = player.fur
        return found
        
    def getProfileSkin(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    found = player.Skin
        return found

    def getProfileCheeseCount(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    found = player.cheesecount
        return found
    def getPlayerPriv(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    found = True
                    priv = player.privilegeLevel
        if found:
            return priv
        else:
            return 1
    def getProfileTitleList(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    titlelist = player.titleList
                    titlelist = json.dumps(titlelist)
                    titlelist = titlelist.replace("[","")
                    titlelist = titlelist.replace("]","")
                    titlelist = titlelist.replace("\"","")
                    titlelist = titlelist.replace(" ","")
                    return titlelist
        return found

    def getPlayerHardMode(self, playercode):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.playerCode == playercode:
                    found = player.hardMode
        return found

    def sendModChat(self, senderClient, eventTokens, data, binary = None):
        if eventTokens=="\x06\x14":
            print str(datetime.today())+" [Serveur] "+data[0]
        if not TS:
            for room in self.rooms.values():
                for playerCode, client in room.clients.items():
                    if client.privilegeLevel>=4:
                        if binary:
                            client.sendData(eventTokens, data, True)
                        else:
                            client.sendData(eventTokens, data)
        else:
            for room in self.rooms.values():
                for playerCode, client in room.clients.items():
                    if client.privilegeLevel>=4 and not client.isDrawer:
                        if binary:
                            client.sendData(eventTokens, data, True)
                        else:
                            client.sendData(eventTokens, data)
    def sendAdminListen(self, data, roomOnly=False,roomName=None):
        if roomOnly:
            for room in self.rooms.values():
                if room.name == roomName:
                    for playerCode, client in room.clients.items():
                        if client.isListening:
                            client.sendData("\x06", "\x14", [data])
        else:
            for room in self.rooms.values():
                for playerCode, client in room.clients.items():
                    if client.isListening:
                        client.sendData("\x06" + "\x14", [data])
                    elif client.username.lower()=="dubbot" or client.username.lower()=="colorbot":
                        client.sendData("\x06" + "\x14", ["[Listen]"+data])
    def sendCheeseGift(self, senderClient, eventTokens, data):
        pass

    def sendTribeInvite(self, senderClient, code, name, tribe):
        if len(name)<3 or len(name)>12:
            pass
        elif not name.isalpha():
            pass
        else:
            name=name.lower().capitalize()
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.username==name:
                    if client.isInTribe:
                        senderClient.sendPlayerAlreadyInTribe()
                    else:
                        client.AcceptableInvites.append(str(code))
                        client.sendTribeInvite(code, senderClient.username, tribe)
                        senderClient.sendInvitationSent()
    def sendWholeTribe(self, senderClient, eventTokens, data, binary = None, NotIgnorable = None):
        for room in self.rooms.values():
            if binary:
                reactor.callLater(0, room.sendWholeTribeRoom, senderClient, eventTokens, data, binary)
            elif NotIgnorable:
                reactor.callLater(0, room.sendWholeTribeRoom, senderClient, eventTokens, data, binary, NotIgnorable)
            else:
                reactor.callLater(0, room.sendWholeTribeRoom, senderClient, eventTokens, data)
    def sendWholeTribeOthers(self, senderClient, eventTokens, data, binary = None, NotIgnorable = None):
        for room in self.rooms.values():
            if binary:
                reactor.callLater(0, room.sendWholeTribeOthersRoom, senderClient, eventTokens, data, binary)
            elif NotIgnorable:
                reactor.callLater(0, room.sendWholeTribeOthersRoom, senderClient, eventTokens, data, binary, NotIgnorable)
            else:
                reactor.callLater(0, room.sendWholeTribeOthersRoom, senderClient, eventTokens, data)

    def sendTribeInfoUpdate(self, code, greeting = None, playerlist = None):
        for room in self.rooms.values():
            if greeting:
                reactor.callLater(0, room.sendTribeInfoUpdateRoom, code, greeting)
            elif playerlist:
                reactor.callLater(0, room.sendTribeInfoUpdateRoom, code, greeting, playerlist)
            else:
                reactor.callLater(0, room.sendTribeInfoUpdateRoom, code)

    def changePrivLevel(self, senderClient, username, privlevel):
        found = False
        if not username.startswith("*"):
            username=username.lower().capitalize()
            for room in self.rooms.values():
                for player in room.clients.values():
                    if player.username == username:
                        msg = 1
                        if privlevel == "-1": 
                            level = "Locked"
                            msg = 0
                        elif privlevel == 1: level = "Игрок"
                        elif privlevel == 3: level = "Арбитр"
                        elif privlevel == 5: level = "Модератор"
                        elif privlevel == 6: level = "Супер модератор"
                        elif privlevel == 8: level = "мега модератор"
                        elif privlevel == 9: level = "Сантехник"
                        elif privlevel == 10: level = "Администратор"
                        elif privlevel == 11: 
                            level = "Сантехник 2.0"
                        else: level = privlevel
                        player.privilegeLevel = privlevel
                        player.sendData("\x1A" + "\x08",[player.username, str(player.playerCode), str(privlevel)])
                        found = True
                        if msg == 1:
                            player.server.sendModChat(self, "\x06\x14", [str(username)+" --> " + str(level) + "."])
                        else:
                            pass
                        break
        return found
    def setDrawing(self, username, draw):
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    if draw == 0:
                        player.isDrawer = 0
                    elif draw == 1:
                        player.isDrawer = 1
                        
    def setCravate(self, username):
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    if not player.checkInShop("405"):
                        if player.shopitems=="":
                            player.shopitems=str("405")
                        else:
                            player.shopitems=player.shopitems+",405"
                    player.sendAnimZelda(player.playerCode, "4", "5")

    def setTfmaction(self, username):
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    if not player.checkInShop("35"):
                        if player.shopitems=="":
                            player.shopitems=str("35")
                        else:
                            player.shopitems=player.shopitems+",35"
                    player.sendAnimZelda(player.playerCode, "4", "5")
                        
                        
    def sendPrivMsg(self, senderClient, fromUsername, toUsername, message):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == toUsername:
                    if player.silence and senderClient.privilegeLevel < 5:
                        if senderClient.privilegeLevel in [10,6,5]:
                            senderClient.sendSentPrivMsg(toUsername, message) #senderClient.numlanguage
                            if player.censorChat:
                                message=player.censorMessage(message)
                            player.sendRecievePrivMsg(fromUsername, message)#, senderClient.numlanguage
                        else:
                            senderClient.sendDisabledWhispers(toUsername)
                    else:
                        senderClient.sendSentPrivMsg(toUsername, message) #, senderClient.numlanguage
                        if player.censorChat:
                            message=player.censorMessage(message)
                        player.sendRecievePrivMsg(fromUsername, message) #, senderClient.numlanguage
                    found = True
        return found
    def sendPrivMsgF(self, senderClient, fromUsername, toUsername, message):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == toUsername:
                    if player.silence:
                        senderClient.sendDisabledWhispers(toUsername)
                    else:
                        senderClient.sendSentPrivMsg(toUsername, message) #, senderClient.numlanguage
                        #if player.censorChat:
                        #    message=player.censorMessage(message)
                        #player.sendRecievePrivMsg(fromUsername, message)
                    found = True
        return found

    def getTribeList(self, code):
        onlinelist=[]
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if str(client.TribeCode)==str(code):
                    onlinelist.append('\x02'.join(map(str,[client.username, client.TribeRank, client.Skin + ";" + client.look, client.titleNumber, client.roomname, client.fur])))
        return onlinelist

    def friendsListCheck(self, username, friendtc):
        #username = friends list to check
        #friendtc = name to check if it's on username's friends list
        found = False
        if username.isalpha() and friendtc.isalpha:
            username=username.lower().capitalize()
            friendtc=friendtc.lower().capitalize()
            for room in self.rooms.values():
                for player in room.clients.values():
                    if player.username == username:
                        if friendtc in player.friendsList:
                            found=True
                        break
        return found

    def sendFriendConnected(self, username, friendts):
        #username = target
        #friendts = name to say had just connected
        found = False
        if username.isalpha() and friendts.isalpha:
            username=username.lower().capitalize()
            friendts=friendts.lower().capitalize()
            for room in self.rooms.values():
                for player in room.clients.values():
                    if player.username == username:
                        if friendts in player.friendsList:
                            player.sendFriendConnected(friendts)
                            found=True
                        break
        return found

    def sendRoomInvite(self, senderClient, fromUsername, toUsername):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == toUsername:
                    senderClient.sendData("\x1A" + "\x04", ["<BL>Инвайт отправлен."])
                    player.sendData("\x1A" + "\x04", ["<J>"+fromUsername+" пригласил вас к нему в комнату. \"/mjoin "+fromUsername+"\" для входа к нему."])
                    found = True
        return found

    def sendMuMute(self, username, modname):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    player.mumute = True
                    found = True
                    break
        return found

    def disconnectPlayer(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    player.sendPlayerDisconnect(player.playerCode)
                    room.removeClient(player)
                    player.transport.loseConnection()
                    found = True
                    break
        return found

    def delavaPlayer(self, username, mod):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    #mod.sendModMessageChannel("Serveur", mod.username+" deleted "+player.username+"'s avatar.")
                    self.sendModChat(mod, "\x06\x14", ["["+mod.username+"] Игрок "+player.username+" отключен."], False)
                    player.sendPlayerDisconnect(player.playerCode)
                    room.removeClient(player)
                    player.transport.loseConnection()
                    found = True
                    break
        return found

    def removeModMute(self, username):
        if username.isalpha():
            username=username.lower().capitalize()
            dbcur.execute("DELETE FROM UserTempMute WHERE Name = ?", [username])
            return True
        return False
    def checkModMute(self, username):
        if username.isalpha():
            username=username.lower().capitalize()
            dbcur.execute('select * from UserTempMute where Name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return False
            else:
                return True
        return False
    def getModMuteInfo(self, username):
        if username.isalpha():
            username=username.lower().capitalize()
            dbcur.execute('select * from UserTempMute where Name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return ["", 0, ""]
            else:
                return rrf
        return ["", 0, ""]
    def sendModMute(self, username, time, reason, modname):
        found = False
        if username.isalpha():
            username=username.lower().capitalize()
            for room in self.rooms.values():
                for playerCode, client in room.clients.items():
                    if client.username == username:

                        #client.sendModMessageChannel("Serveur", modname+" muted "+username+" for "+str(time)+" hours. Reason: "+str(reason))
                        self.sendModChat(self, "\x06\x14", [modname+" заблокировал чат игроку "+username+" на "+str(time)+" часов. Причина : "+str(reason)], False)
                        if self.checkModMute(client.username):
                            self.removeModMute(client.username)
                        client.modmute = True
                        client.sendModMuteRoom(client.username, time, reason)
                        time = client.returnFutureTime(time)
                        dbcur.execute("insert into UserTempMute (Name, Time, Reason) values (?, ?, ?)", (client.username, time, reason))
                        found = True
                        break
        return found
    
    def sendNoModMute(self, username, modname):
        found = False
        if username.isalpha():
            username=username.lower().capitalize()
            for room in self.rooms.values():
                for playerCode, client in room.clients.items():
                    if client.username == username:
                        self.sendModChat(self, "\x06\x14", [modname+" разрешил говорить "+username], False)
                        self.removeModMute(client.username)
                        client.modmute = False
                        found = True
                        break
        return found

    def banPlayer(self, username, bantime, reason, modname):
        found = False
        bantime = int(bantime)
        if reason.startswith("\x03"):
            silentban=True
            reason=reason.replace("\x03", "")
        else:
            silentban=False
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.username == username:
                    if modname != "Serveur":
                        client.banhours = int(client.banhours)+bantime
                        if bantime >= 0:
                            if not username.startswith("*"):
                                bandate = int(str(time.time())[:-4])
                                dbcur.execute("insert into BanLog (Name, BannedBy, Time, Reason, Date, Status, Room, IP) values (?, ?, ?, ?, ?, ?, ?, ?)", (username, modname, bantime, reason, bandate, "Online", client.room.name, client.address[0]))
                    else:
                        self.sendModChat(client, "\x06\x14", ["[Vote populaire] Забанили "+str(client.username)+" ("+str(client.room.name)+")."], False)
                    if not username.startswith("*"):
                        if client.banhours >= 25 and bantime <= 24:
                            dbcur.execute("insert into userpermaban (name, bannedby, reason) values (?, ?, ?)", (username, modname, "Total ban hours went over 24. "+reason))
                        dbcur.execute('UPDATE users SET totalban = ? WHERE name = ?', [str(client.banhours), client.username])
                    client.sendPlayerBan(bantime, reason, silentban)
                    if bantime >= 25:
                        clientaddr = client.address[0]
                        dbcur.execute("insert into ippermaban (ip, bannedby, reason) values (?, ?, ?)", (clientaddr, modname, reason))
                        if not username.startswith("*"):
                            dbcur.execute("insert into userpermaban (name, bannedby, reason) values (?, ?, ?)", (username, modname, reason))
                    if bantime >= 1 and bantime <= 24:
                        if not username.startswith("*"):
                            self.tempBanUser(username, bantime, reason)
                        ipaddr = client.address[0]
                        self.tempBanIP(ipaddr, bantime)
                    found = True
                    break
        if not found:
            if not username.startswith("*"):
                if self.checkExistingUsers(username):
                    if modname != "Serveur" and bantime >= 1:
                        banHours=self.getTotalBanHours(username)+bantime
                        if banHours >= 25 and bantime <= 24:
                            dbcur.execute("insert into userpermaban (name, bannedby, reason) values (?, ?, ?)", (username, modname, "Total ban hours went over 24. "+reason))
                        if bantime >= 25:
                            dbcur.execute("insert into userpermaban (name, bannedby, reason) values (?, ?, ?)", (username, modname, reason))
                        if bantime >= 1 and bantime <= 24:
                            self.tempBanUser(username, bantime, reason)
                        dbcur.execute('UPDATE users SET totalban = ? WHERE name = ?', [str(banHours), username])
                        dbcur.execute("insert into BanLog (Name, BannedBy, Time, Reason, Date, Status, Room, IP) values (?, ?, ?, ?, ?, ?, ?, ?)", (username, modname, bantime, reason, int(str(time.time())[:-4]), "Offline", "", "offline"))
                        found = True
        return found

    def updatePlayerStats(self, username, rounds, saves, shamcheese, first, cheese, shopcheese, fraises, shop, look, ShamanTitleList, CheeseTitleList, FirstTitleList, titleList, hardMode, hardModeSaves, HardModeTitleList, ShopTitleList):
        if username.startswith("*"):
            pass
        else:
            if str(rounds).isdigit():
                rounds = int(rounds)
            else:
                rounds = 0
            if str(saves).isdigit():
                saves = int(saves)
            else:
                saves = 0
            if str(shamcheese).isdigit():
                shamcheese = int(shamcheese)
            else:
                shamcheese = 0
            if str(first).isdigit():
                first = int(first)
            else:
                first = 0
            if str(cheese).isdigit():
                cheese = int(cheese)
            else:
                cheese = 0
            if str(shopcheese).isdigit():
                shopcheese = int(shopcheese)
            else:
                shopcheese = 0
            if str(fraises).isdigit():
                fraises = int(fraises)
            else:
                fraises = 0
            if str(hardMode).isdigit():
                hardMode = int(hardMode)
            else:
                hardMode = 0
            if str(hardModeSaves).isdigit():
                hardModeSaves = int(hardModeSaves)
            else:
                hardModeSaves = 0
            titleList = filter(None, titleList)
            ShamanTitleList = filter(None, ShamanTitleList)
            CheeseTitleList = filter(None, CheeseTitleList)
            FirstTitleList = filter(None, FirstTitleList)
            HardModeTitleList = filter(None, HardModeTitleList)
            ShopTitleList = filter(None, ShopTitleList)
            dbShamanTitleList = json.dumps(ShamanTitleList)
            dbCheeseTitleList = json.dumps(CheeseTitleList)
            dbFirstTitleList = json.dumps(FirstTitleList)
            dbtitleList = json.dumps(titleList)
            dbHardModeTitleList = json.dumps(HardModeTitleList)
            dbShopTitleList = json.dumps(ShopTitleList)
            dbcur.execute('UPDATE users SET rounds = ?, saves = ?, shamcheese = ?, first = ?, cheese = ?, shopcheese = ?, fraises = ?, shop = ?, look = ?, titlelist = ?, CheeseTitleList = ?, FirstTitleList = ?, ShamanTitleList = ?, HardMode = ?, HardModeSaves = ?, HardModeTitleList = ?, ShopTitleList = ? WHERE name = ?',
            [rounds, saves, shamcheese, first, cheese, shopcheese, fraises, shop, look, dbtitleList, dbCheeseTitleList, dbFirstTitleList, dbShamanTitleList, hardMode, hardModeSaves, dbHardModeTitleList, dbShopTitleList, username])

    def getIPaddress(self, username):
        found = False
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.username == username:
                    found = client.address[0]
                    break
        return found

    def disconnectIPaddress(self, IPaddr):
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if str(client.address[0]) == str(IPaddr):
                    client.transport.loseConnection()

    def doVoteBan(self, username, selfIP, selfName):
        found = False
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.username == username:
                    if client.privilegeLevel>=10 or client.privilegeLevel == 6 or client.privilegeLevel == 5 or client.privilegeLevel == 3:
                        pass
                    else:
                        if not selfIP in client.voteban:
                            client.voteban.append(selfIP)
                            if len(client.voteban)>=6: #8
                                #client.sendPlayerBanMessage(client.username, "1", "Vote populaire")
                                self.banPlayer(client.username, "1", "Vote populaire", "Serveur")
                        else:
                            pass
                    #client.room.sendAllStaffInRoom(self, "\x06"+"\x14",[selfName+" demande le bannissement de "+username+" ("+str(len(client.voteban))+"/6)."])
                    client.room.sendAllStaffInRoomVoteBan(self, selfName , username, str(len(client.voteban)))
                    break
        return found
#    def doAskForHelper(self, askmessage, selfIP, selfName):
#        found = False
#        for room in self.rooms.values():
#            for playerCode, client in room.clients.items():
#                if client.username == askmessage:
#                    if client.privilegeLevel>=3:
#                        client.room.sendAskForHelper(self, selfName , askmessage)
#                    break
 #       return found
    def clearVoteBan(self, senderClient, username):
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.username == username:
                    client.voteban=[]
                    self.sendModChat(senderClient, "\x06\x14", [senderClient.username+" очистил воут-баны игрока "+str(client.username)+"."], False)
		
    def getFindPlayerRoom(self, username):
        found = False
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.username == username:
                    return client.roomname
                    break
        return found

    def getFindRoomPartial(self, senderClient, findroomname, FindAll=None):
        found = False
        resultlist=""
        playercount=0
        for room in self.rooms.values():
            if re.search(findroomname.lower(), room.name.lower()):
                resultlist=resultlist+"<br>"+str(room.name)+" : "+str(room.getPlayerCount())
                playercount=playercount+room.getPlayerCount()
        senderClient.sendData("\x06" + "\x14",[resultlist])
        senderClient.sendData("\x06" + "\x14",["Всего игроков : "+str(playercount)])

    def getFindPlayerRoomPartial(self, senderClient, username, FindAll=None):
        found = False
        NoTest= False
        if FindAll:
            username=""
        else:
            result=""
            level=range(48, 57+1)+range(65, 90+1)+range(97, 122+1)+[95, 42]
            for x in username:
                    if not int(senderClient.hex2dec(x.encode("hex"))) in level:
                        x=""
                        NoTest=True
                    result+=x
            if result=="":
                NoTest=True
            username = result.replace("*","\*")
        if not NoTest:
            resultlist=""
            for room in self.rooms.values():
                for playerCode, client in room.clients.items():
                    if re.search(username.lower(), client.username.lower()):
                        resultlist=resultlist+"<br>"+client.username+" -> "+ client.room.name
            resultlistT=resultlist.strip("<br>")
            if resultlistT=="":
                senderClient.sendData("\x06" + "\x14",[resultlist])
            else:
                senderClient.sendData("\x06" + "\x14",[resultlist])

    def getLsModo(self, senderClient):
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.privilegeLevel in [10,8,6,5]:
                    if not client.isDrawer:
                        name = client.username
                        name="-"
                        message=client.username+" : "+client.room.name
                        senderClient.sendData("\x1A\x05", [name, message])
    def getLsDrawer(self, senderClient):
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.isDrawer:
                    name = "-"
                    #message=client.username+"(Drawer) : "+client.room.name
                    senderClient.sendData("\x1A" + "\x04", ["<font color='#F3FA28'>• %s : %s"%(client.username,client.room.name)])
    def getLsArb(self, senderClient):
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.privilegeLevel in [3]:
                    name="-"
                    message=client.username+" : "+client.room.name
                    #data="\x02"+struct.pack('!h', len(name))+name+struct.pack('!h', len(message))+message+"\x00\x00"
                    #senderClient.sendData("\x06\x0A", data, True)
                    senderClient.sendData("\x1A\x06", [name, message])
    def getLsBot(self, senderClient):
        senderClient.sendData("\x06" + "\x14", ["Список ботов:"])
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.privilegeLevel in [4]:
                    owner = self.getBotOwner(client.username)
                    senderClient.sendData("\x06" + "\x14", ["[MB] %s (%s) : %s"%(client.username,owner,client.room.name)])
    def getRoomList(self, senderClient):
        found = False
        roomlist=""
        for room in self.rooms.values():
            roomlist=roomlist+"<br>"+room.name+" : "+str(room.getPlayerCount())
        senderClient.sendData("\x06" + "\x14",[roomlist])
        senderClient.sendData("\x06" + "\x14",["Всего игроков : "+str(self.getConnectedPlayerCount())])
        return found

    def getTribesList(self, senderClient):
        found = False
        tribes={}
        tribelist=""
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.TribeName!="":
                    try:
                        tribes[client.TribeName]+=1
                    except:
                        tribes[client.TribeName]=1
        for tribename in tribes.keys():
            tribelist=tribelist+"<br>"+str(tribename)+" : "+str(tribes[tribename])
        tribelistT=tribelist.strip("<br>")
        if tribelistT=="":
            senderClient.sendData("\x06" + "\x14",[tribelistT])
        else:
            senderClient.sendData("\x06" + "\x14",[tribelist])
        #senderClient.sendData("\x06" + "\x14",[tribelist])
        return found

    def nomIPCommand(self, senderClient, name):
        iplist="История IP ["+name+"] :"
        dbcur.execute('select * from LoginLog where Name = ?', [name])
        rrfRows = dbcur.fetchall()
        if rrfRows is None:
            pass
        else:
            for rrf in rrfRows:
                iplist=iplist+"<br>"+str(rrf[1])
        senderClient.sendData("\x06" + "\x14",[iplist])
    def IPNomCommand(self, senderClient, ip):
        namelist="История IP ["+str(ip)+"] :"
        for room in self.rooms.values():
            for playerCode, client in room.clients.items():
                if client.address[0]==ip:
                    namelist=namelist+"<br>"+str(client.username)
        namehlist="История IP ["+str(ip)+"] :"
        dbcur.execute('select * from LoginLog where IP = ?', [ip])
        rrfRows = dbcur.fetchall()
        if rrfRows is None:
            pass
        else:
            for rrf in rrfRows:
                namehlist=namehlist+"<br>"+str(rrf[0])
        senderClient.sendData("\x06" + "\x14",[namelist])
        senderClient.sendData("\x06" + "\x14",[namehlist])

    def restartServerDelLog(self):
        logging.info("Restarting")
        for room in self.rooms.values():
            room.updatesqlserver()
        reactor.stop()
        os._exit(11)
        
    def restartServer10min(self):
        logging.info("Restarting")
        for room in self.rooms.values():
            room.updatesqlserver()
        reactor.stop()
        os._exit(12)
    def restartServer5min(self):
        logging.info("Restarting")
        for room in self.rooms.values():
            room.updatesqlserver()
        reactor.stop()
        os._exit(13)
    def restartServer20min(self):
        logging.info("Restarting")
        for room in self.rooms.values():
            room.updatesqlserver()
        reactor.stop()
        os._exit(14)
    def restartServerUpdate(self):
        logging.info("Restarting")
        for room in self.rooms.values():
            room.updatesqlserver()
        reactor.stop()
        os._exit(20)

    def restartServer(self):
        logging.info("Restarting")
        for room in self.rooms.values():
            room.updatesqlserver()
        reactor.stop()
        os._exit(10)

    def stopServer(self):
        logging.info("Stopping")
        for room in self.rooms.values():
            room.updatesqlserver()
        reactor.stop()
        os._exit(5)
        
    def astopServer(self):
        logging.info("Automatic stop")
        for room in self.rooms.values():
            room.updatesqlserver()
        reactor.stop()
        os._exit(5)
         #1334078100	

    def removeTempBan(self, username):
        if username.isalpha():
            username=username.lower().capitalize()
            dbcur.execute("DELETE FROM UserTempBan WHERE Name = ?", [username])
            return True
        return False
    def checkIPBan(self, ip):
        dbcur.execute('select * from ippermaban where ip = ?', [ip])
        rrf = dbcur.fetchone()
        if rrf is None:
            return False
        else:
            return True
    def removeIPBan(self, ip):
        dbcur.execute("DELETE FROM ippermaban WHERE ip = ?", [ip])
        return True
    def checkTempBan(self, username):
        if username.isalpha():
            username=username.lower().capitalize()
            dbcur.execute('select * from UserTempBan where Name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return False
            else:
                return True
        return False
    def getTempBanInfo(self, username):
        if username.isalpha():
            username=username.lower().capitalize()
            dbcur.execute('select * from UserTempBan where Name = ?', [username])
            rrf = dbcur.fetchone()
            if rrf is None:
                return ["", 0, ""]
            else:
                return rrf
        return ["", 0, ""]
    def tempBanUser(self, name, bantime, reason):
        if self.checkTempBan(name):
            self.removeTempBan(name)
        dbcur.execute("insert into UserTempBan (Name, Time, Reason) values (?, ?, ?)", (str(name).lower().capitalize(), str(time.time()+int((int(bantime)*60*60))), str(reason)))
        #time = time*3600
        #if not name in self.tempAccountBanList:
        #    self.removeTempBanUserTimer = reactor.callLater(time, self.tempBanUserRemove, name)
        #    self.tempAccountBanList.append(name)
    def tempBanIP(self, ipaddr, time):
        time = time*3600
        if not ipaddr in self.tempIPBanList:
            self.removeTempBanIPTimer = reactor.callLater(time, self.tempBanIPRemove, ipaddr)
            self.tempIPBanList.append(ipaddr)
    def tempBanIPExact(self, ipaddr, time):
        if not ipaddr in self.tempIPBanList:
            self.removeTempBanIPTimer = reactor.callLater(time, self.tempBanIPRemove, ipaddr)
            self.tempIPBanList.append(ipaddr)
    def tempBanUserRemove(self, name):
        if name in self.tempAccountBanList:
            self.tempAccountBanList.remove(name)
    def tempBanIPRemove(self, ipaddr):
        if ipaddr in self.tempIPBanList:
            self.tempIPBanList.remove(ipaddr)

    def checkAlreadyExistingGuest(self, nusername):
        x=0
        found=False
        if not self.checkAlreadyConnectedAccount(nusername):
            found=True
            return nusername
        while not found:
            x+=1
            if not self.checkAlreadyConnectedAccount(nusername+"_"+str(x)):
                found=True
                return nusername+"_"+str(x)

    def checkAlreadyConnectedAccount(self, username):
        found = False
        for room in self.rooms.values():
            for player in room.clients.values():
                if player.username == username:
                    found = True
        return found

    def addClientToRoom(self, client, roomName):
        roomName = str(roomName)
        if roomName in self.rooms:
            self.rooms[roomName].addClient(client)
        else:
            self.rooms[roomName] = TransformiceRoomHandler(self, roomName)
            self.rooms[roomName].addClient(client)
        #return self.rooms[roomName]

    def closeRoom(self, room):
        if room.name in self.rooms:
            room.close()
            del self.rooms[room.name]

    def getConnectedPlayerCount(self):
        count = 0
        for room in self.rooms.values():
            for player in room.clients.values():
                count = count+1
        return count

    def generatePlayerCode(self):
        self.lastPlayerCode+=1
        return self.lastPlayerCode

    def recommendRoomPrefixed(self, prefix):
        found=False
        x=0
        while not found:
            x+=1
            if prefix+str(x) in self.rooms:
                playercount=self.rooms[prefix+str(x)].getPlayerCount()
                if int(playercount)<25:
                    found=True
                    return prefix+str(x)
            else:
                found=True
                return prefix+str(x)

    def recommendRoom(self):
        found=False
        x=0
        while not found:
            x+=1
            if str(x) in self.rooms:
                playercount=self.rooms[str(x)].getPlayerCount()
                if int(playercount)<25:
                    found=True
                    return str(x)
            else:
                found=True
                return str(x)

class TransformiceRoomHandler(object):
    def __init__(self, server, name):
        self.server = server
        self.name = name.strip()
        self.namewihout = self.name.replace("tr_", "")
        self.namewihout = self.namewihout.replace("da_", "")
        self.namewihout = self.namewihout.replace("ru_", "")
        self.namewihout = self.namewihout.replace("no_", "")
        self.namewihout = self.namewihout.replace("cn_", "")
        self.namewihout = self.namewihout.replace("es_", "")
        self.namewihout = self.namewihout.replace("pt_", "")
        self.namewihout = self.namewihout.replace("sv_", "")
        self.namewihout = self.namewihout.replace("fr_", "")
        self.namewihout = self.namewihout.replace("br_", "")
        self.namewihout = self.namewihout.replace("en_", "")
        

        self.clients = {}

        self.currentShamanCode = None
        self.currentSyncroniserCode = None

        self.isDoubleMap = False
        self.currentSecondShamanCode = None
        self.changed20secTimer = False
        self.never20secTimer = False

        self.currentShamanName = None
        self.currentSecondShamanName = None
        self.customMapCode = ""
        self.isSandbox = False
        self.isDeadTimer = 0
        self.isSurvivorWinner = 0
        self.isCurrentlyPlayingRoom = False
        self.isEditeur = False
        self.isTotemEditeur = False
        self.isPlay = False
        self.isBootcamp = False
        self.isSpeed = False
        self.isTribe = False
        self.isWind = False
        self.isVanilla = False
        self.isRacing = False
        self.isSurvivor = False
        self.isBotRoom = False
        self.isBooming = False
        self.ZombieRoom = False
        self.MegaBooming = "0"
        self.specificMap = False
        self.properNoShamanMaps = True
        self.isCatchTheCheeseMap = False
        self.isValidate = 0
        self.NoNumberedMaps = False
        self.PTwoCycle = False
        self.PTwoCycleInfo = 0
        self.PTwoCycleList = []
        self.PRShamanIsShaman = False

        #               Code[0], Name[1], XML[2], YesVotes[3], NoVotes[4], Perma[5], Deleted[6]
        self.ISCMdata = [0, "Invalid", "<C><P /><Z><S /><D /><O /></Z></C>", 0, 0, 0, 0]
        self.ISCM = 0
        self.ISCMstatus = 0

        #                Code[0], Name[1], XML[2], YesVotes[3], NoVotes[4], Perma[5], Deleted[6], Validated[7]
        self.ISCMVdata =[0, "Invalid", "null", 0, 0, 0, 0, 0]
        self.ISCMV = 0
        self.ISCMVloaded = 0

        self.RoomInvite=[]
        self.PrivateRoom=False

        self.forceNextShaman = False
        self.forceNextMap = False
        self.CodePartieEnCours = 1
        self.CustomMapCounter = 1
        self.identifiantTemporaire = -1

        self.countStats = True
        self.autoRespawn = False
        self.roundTime = 120

        self.votingMode = False
        self.votingBox = False
        self.initVotingMode = True
        self.recievedYes= 0
        self.recievedNo = 0
        self.voteCloseTimer = None

        self.CheckedPhysics=False
        self.isHardSham=False

        self.SPR_Room = False
        self.eSync    = False
        self.sSync    = True
        self.sNP      = True
        self.sT       = False
        self.spc0     = False
        self.SPR_CM   = 0
        self.drawingCoordinates = []
        self.isDrawing = False
        #self.snowStormStartTimer = reactor.callLater(random.randrange(900, 1500), self.startSnowStorm)
        if self.name == "repeat":
            self.specificMap = True
            self.isPlay = True
            self.currentWorld = "0"
            self.roundTime = 120
        elif self.name == "sandbox":
            self.specificMap = True
            self.isSandbox = True
            self.currentWorld = "444"
        #if self.name in self.server.SPR:
            #self.SPR_Room=True
            #RunList=self.server.SPRD[:]
            for position, room in enumerate(RunList):
                if room[0]==self.name:
                    self.countStats=room[1]
                    self.specificMap=room[2]
                    self.isSandbox=room[3]
                    if room[4]:
                        self.currentWorld="-1"
                        self.SPR_CM=room[5]
                    else:
                        self.currentWorld=room[5]
                    self.autoRespawn=room[6]
                    self.roundTime=room[7]
                    self.never20secTimer=room[8]
                    #Extra Vars
                    self.eSync=room[9]
                    self.sSync=room[10]
                    self.sNP=room[11]
                    self.sT=room[12]
                    self.spc0=room[13]
                    break
     ##   elif self.namewihout == "racing":
     #       self.countStats = True
     #       self.isRacing = True
     #       self.roundTime = 60
        elif self.namewihout == "*801":
            self.countStats = False
            self.roundTime = 0
            self.isBotRoom = True
            self.currentWorld = 0
        elif self.namewihout == "*kika":
            self.countStats = False
            self.roundTime = 0
            self.isBotRoom = True
        elif self.namewihout == "zombie":
            self.countStats = True
            self.ZombieRoom = True
            self.roundTime = 120
            self.currentWorld = 666
        elif self.namewihout == "tv":
            self.countStats = False
            self.isSandbox = True
            self.roundTime = 0
            self.mapnumber = "@5608"
        elif self.namewihout == "survivor":
            self.countStats = False
            self.roundTime = 120
            self.isSurvivor = True
        elif self.namewihout == "booming":
            self.countStats = False
            self.roundTime = 120
            self.isBooming = True
        elif self.namewihout.startswith("\x03"+"[Tribe]"):
            self.countStats = False
            self.currentWorld = "0"
            #self.specificMap = True
            self.isTribe = True
            self.PrivateRoom = True
            self.autoRespawn = True
            self.roundTime = 0
            self.never20secTimer = True
        elif self.namewihout.startswith("\x03"+"[Editeur]"):
            self.countStats = False
            self.currentWorld = 0
            #self.specificMap = True
            self.isEditeur = True
            self.roundTime = 120
            self.never20secTimer = True
        elif self.namewihout.startswith("\x03"+"[Totem]"):
            self.countStats = False
            #self.isSandbox = True
            self.currentWorld = 444
            self.specificMap = True
            self.isTotemEditeur = True
            self.roundTime = 3600
            self.never20secTimer = True
            
        elif re.search("bootcamp", name.lower()):
            self.countStats = False
            self.currentWorld = "0"
            #self.specificMap = True
            self.isBootcamp = True
            self.autoRespawn = True
            self.roundTime = 360
            self.never20secTimer = True
        elif re.search("speed", name.lower()):
            self.countStats = True
            self.currentWorld = "0"
            #self.specificMap = True
            self.isSpeed = True
            self.autoRespawn = False
            self.roundTime = 60
            self.never20secTimer = True
        elif re.search("wind", name.lower()):
            self.countStats = False
            self.isWind = True
            self.autoRespawn = True
            self.roundTime = 360
            self.never20secTimer = True
        elif re.search("time", name.lower()):
            self.countStats = False
            self.isWind = True
            self.autoRespawn = True
            self.roundTime = 960
            self.never20secTimer = True
        elif re.search("vanilla", name.lower()):
            self.isVanilla = True
            self.roundTime = 120
        else:
            self.roundTime = 120
        runthismap = self.selectMap(True)
        self.currentWorld = runthismap

        self.everybodyIsShaman = self.isSandbox
        self.nobodyIsShaman = self.isBootcamp
        self.nobodyIsShaman = self.isSpeed


        self.worldChangeTimer = None
        self.ZombieTimer = None
        self.ActionTimer = None
        self.killAfkTimer = None
        self.autoRespawnTimer = None
        self.sNNMTimer = None
        self.sPTCTimer = None
        if not self.isSandbox:
                if self.isBooming:
                    self.ActionTimer = reactor.callLater(5, self.GenerateExplode)
                if self.currentWorld==888:
                    self.worldChangeTimer = reactor.callLater(60, self.worldChange)
                else:
                    self.worldChangeTimer = reactor.callLater(self.roundTime, self.worldChange)
                self.killAfkTimer = reactor.callLater(30, self.killAfk)
                self.closeRoomRoundJoinTimer = reactor.callLater(3, self.closeRoomRoundJoin)
        if self.autoRespawn:
            self.autoRespawnTimer = reactor.callLater(15, self.respawnMice)
        self.gameStartTime = time.time()
        self.numCompleted = 0
        self.numGotCheese = 0

    def goZombified(self):
        for playerCode, client in self.clients.items():
            if client.isSyncroniser:
                client.sendZombieMode()

    def respawnMice(self):
        for playerCode, client in self.clients.items():
            if client.isDead:
                client.isDead=False
                client.JumpCheck=1
                client.playerStartTime = time.time()
                if self.isBootcamp:
                    self.sendAll("\x08" + "\x08",[client.getPlayerData(), 0])
                else:
                    self.sendAll("\x08" + "\x08",[client.getPlayerData(), 1])
        if self.autoRespawn:
            self.autoRespawnTimer = reactor.callLater(15, self.respawnMice)
    def respawnSpecific(self, username):
        for playerCode, client in self.clients.items():
            if client.username == username:
                client.isDead=False
                client.JumpCheck=1
                client.playerStartTime = time.time()
                if self.isBootcamp:
                    self.sendAll("\x08" + "\x08",[client.getPlayerData(), 0])
                else:
                    self.sendAll("\x08" + "\x08",[client.getPlayerData(), 1])
    def respawnMice(self):
        for playerCode, client in self.clients.items():
            if client.isDead:
                client.isDead=False
                client.JumpCheck=1
                client.playerStartTime = time.time()
                if self.isTribe:
                    self.sendAll("\x08" + "\x08",[client.getPlayerData(), 0])
                else:
                    self.sendAll("\x08" + "\x08",[client.getPlayerData(), 1])
        if self.autoRespawn:
            self.autoRespawnTimer = reactor.callLater(15, self.respawnMice)
    def respawnSpecific(self, username):
        for playerCode, client in self.clients.items():
            if client.username == username:
                client.isDead=False
                client.JumpCheck=1
                client.playerStartTime = time.time()
                if self.isTribe:
                    self.sendAll("\x08" + "\x08",[client.getPlayerData(), 0])
                else:
                    self.sendAll("\x08" + "\x08",[client.getPlayerData(), 1])
    def switchNoNumberedMaps(self, option):
        if self.sNNMTimer:
            try:
                self.sNNMTimer.cancel()
            except:
                self.sNNMTimer = None
        if option==True:
            self.NoNumberedMaps = True
            self.sNNMTimer = reactor.callLater(1200, self.switchNoNumberedMaps, False)
        else:
            self.NoNumberedMaps = False
            self.sNNMTimer = reactor.callLater(1200, self.switchNoNumberedMaps, True)

    def switchPTwoCycle(self, option):
        if self.sPTCTimer:
            try:
                self.sPTCTimer.cancel()
            except:
                self.sPTCTimer = None
        if option==True:
            self.PTwoCycle = True
            self.sPTCTimer = reactor.callLater(1200, self.switchPTwoCycle, False)
        else:
            self.PTwoCycle = False
            self.PTwoCycleInfo=0
            self.PTwoCycleList=[]
            self.sPTCTimer = reactor.callLater(1200, self.switchPTwoCycle, True)

    def close(self):
        if self.worldChangeTimer:
            try:
                self.worldChangeTimer.cancel()
            except:
                self.worldChangeTimer=None
        if self.killAfkTimer:
            try:
                self.killAfkTimer.cancel()
            except:
                self.killAfkTimer=None
        if self.autoRespawnTimer:
            try:
                self.autoRespawnTimer.cancel()
            except:
                self.autoRespawnTimer=None
        #if self.snowStormStartTimer:
        #    self.snowStormStartTimer.cancel()

    def selectMapSpecific(self, mapnum, custom):
        if str(mapnum).isdigit():
            if custom:
                mapcode    = int(mapnum)
                mapname    = self.server.getMapName(mapcode)
                mapxml     = self.server.getMapXML(mapcode)
                yesvotes   = int(self.server.getMapYesVotes(mapcode))
                novotes    = int(self.server.getMapNoVotes(mapcode))
                perma      = int(self.server.getMapPerma(mapcode))
                mapnoexist = int(self.server.getMapDel(mapcode))
                self.ISCM = mapcode
                self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                self.customMapCode = mapcode
                return "-1"
            else:
                self.ISCM = 0
                self.ISCMdata = [0, "Invalid", "<C><P /><Z><S /><D /><O /></Z></C>", 0, 0, 0, 0]
                return int(mapnum)
        else:
            pass

    def selectMap(self, NewRoom = None):
        if self.PTwoCycle:
            if self.PTwoCycleList == []:
                #List is empty, populate it.
                dbcur.execute('select * from mapeditor where perma = 2')
                rrfRows = dbcur.fetchall()
                if rrfRows is None:
                    self.PTwoCycle = False
                else:
                    for rrf in rrfRows:
                        self.PTwoCycleList.append(rrf[1])
                mapnum     = self.PTwoCycleList[self.PTwoCycleInfo]
                self.PTwoCycleInfo+=1
                if self.PTwoCycleInfo==len(self.PTwoCycleList):
                    self.PTwoCycle=False
                    self.PTwoCycleInfo=0
                    self.PTwoCycleList=[]
                    if self.sPTCTimer:
                        try:
                            self.sPTCTimer.cancel()
                        except:
                            self.sPTCTimer = None
                mapcode    = int(mapnum)
                mapname    = self.server.getMapName(mapcode)
                mapxml     = self.server.getMapXML(mapcode)
                yesvotes   = int(self.server.getMapYesVotes(mapcode))
                novotes    = int(self.server.getMapNoVotes(mapcode))
                perma      = int(self.server.getMapPerma(mapcode))
                mapnoexist = int(self.server.getMapDel(mapcode))
                self.ISCM = mapcode
                self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                return "-1"
            else:
                mapnum     = self.PTwoCycleList[self.PTwoCycleInfo]
                self.PTwoCycleInfo+=1
                if self.PTwoCycleInfo==len(self.PTwoCycleList):
                    self.PTwoCycle=False
                    self.PTwoCycleInfo=0
                    self.PTwoCycleList=[]
                    if self.sPTCTimer:
                        try:
                            self.sPTCTimer.cancel()
                        except:
                            self.sPTCTimer = None
                mapcode    = int(mapnum)
                mapname    = self.server.getMapName(mapcode)
                mapxml     = self.server.getMapXML(mapcode)
                yesvotes   = int(self.server.getMapYesVotes(mapcode))
                novotes    = int(self.server.getMapNoVotes(mapcode))
                perma      = int(self.server.getMapPerma(mapcode))
                mapnoexist = int(self.server.getMapDel(mapcode))
                self.ISCM = mapcode
                self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                return "-1"

        if self.NoNumberedMaps:
            self.ISCMstatus=2
        if self.forceNextMap:
            forceNextMap = self.forceNextMap
            self.forceNextMap = False
            if forceNextMap.startswith("@"):
                forceNextMap=forceNextMap.replace("@", "")
                return self.selectMapSpecific(forceNextMap, True)
            else:
                return self.selectMapSpecific(forceNextMap, False)
        elif NewRoom:
            if self.isTribe:
                maplist = []
                dbcur.execute('select code from mapeditor where perma = 22')
                rrfRows = dbcur.fetchall()
                if rrfRows is None:
                    pass
                else:
                    for rrf in rrfRows:
                        maplist.append(rrf[0])
                if len(maplist)>=1:
                    runthismap = random.choice(maplist)
                else:
                    runthismap = ""
                if runthismap=="":
                    self.ISCM = 0
                    return 0
                else:
                    mapcode    = int(runthismap)
                    mapname    = self.server.getMapName(mapcode)
                    mapxml     = self.server.getMapXML(mapcode)
                    yesvotes   = int(self.server.getMapYesVotes(mapcode))
                    novotes    = int(self.server.getMapNoVotes(mapcode))
                    perma      = int(self.server.getMapPerma(mapcode))
                    mapnoexist = int(self.server.getMapDel(mapcode))
                    self.ISCM = mapcode
                    self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                    self.customMapCode = mapcode
                    return "-1"
            elif self.isBooming:
                maplist = ['5608']
                if len(maplist)>=1:
                    runthismap = random.choice(maplist)
                else:
                    runthismap = ""
                if runthismap=="":
                    self.ISCM = 0
                    return 0
                else:
                    mapcode    = int(runthismap)
                    mapname    = self.server.getMapName(mapcode)
                    mapxml     = self.server.getMapXML(mapcode)
                    yesvotes   = int(self.server.getMapYesVotes(mapcode))
                    novotes    = int(self.server.getMapNoVotes(mapcode))
                    perma      = int(self.server.getMapPerma(mapcode))
                    mapnoexist = int(self.server.getMapDel(mapcode))
                    self.ISCM = mapcode
                    self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                    self.customMapCode = mapcode
                    return "-1"
            elif self.isBotRoom:
                return 0
            elif self.isSurvivor:
                maplist = ['5609']
                if len(maplist)>=1:
                    runthismap = random.choice(maplist)
                else:
                    runthismap = ""
                if runthismap=="":
                    self.ISCM = 0
                    return 0
                else:
                    mapcode    = int(runthismap)
                    mapname    = self.server.getMapName(mapcode)
                    mapxml     = self.server.getMapXML(mapcode)
                    yesvotes   = int(self.server.getMapYesVotes(mapcode))
                    novotes    = int(self.server.getMapNoVotes(mapcode))
                    perma      = int(self.server.getMapPerma(mapcode))
                    mapnoexist = int(self.server.getMapDel(mapcode))
                    self.ISCM = mapcode
                    self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                    self.customMapCode = mapcode
                    return "-1"
            elif self.isEditeur:
                return 0
            elif self.SPR_Room and self.SPR_CM!=0:
                runthismap=self.SPR_CM
                mapcode    = int(runthismap)
                mapname    = self.server.getMapName(mapcode)
                mapxml     = self.server.getMapXML(mapcode)
                yesvotes   = int(self.server.getMapYesVotes(mapcode))
                novotes    = int(self.server.getMapNoVotes(mapcode))
                perma      = int(self.server.getMapPerma(mapcode))
                mapnoexist = int(self.server.getMapDel(mapcode))
                self.ISCM = mapcode
                self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                self.customMapCode = mapcode
                return "-1"
            else:
                self.ISCM = 0
                self.ISCMdata = [0, "Invalid", "<C><P /><Z><S /><D /><O /></Z></C>", 0, 0, 0, 0]
                runthismap = random.choice(LEVEL_LIST)
                if self.specificMap:
                    runthismap = self.currentWorld
                return runthismap
        elif self.isBootcamp:
                maplist = []
                dbcur.execute('select code from mapeditor where perma = 3')
                rrfRows = dbcur.fetchall()
                if rrfRows is None:
                    pass
                else:
                    for rrf in rrfRows:
                        maplist.append(rrf[0])
                if len(maplist)>=1:
                    runthismap = random.choice(maplist)
                else:
                    runthismap = ""
                if len(maplist)>=2:
                    while runthismap == self.ISCM:
                        runthismap = random.choice(maplist)
                if runthismap=="":
                    self.ISCM = 0
                    return 0
                else:
                    mapcode    = int(runthismap)
                    mapname    = self.server.getMapName(mapcode)
                    mapxml     = self.server.getMapXML(mapcode)
                    yesvotes   = int(self.server.getMapYesVotes(mapcode))
                    novotes    = int(self.server.getMapNoVotes(mapcode))
                    perma      = int(self.server.getMapPerma(mapcode))
                    mapnoexist = int(self.server.getMapDel(mapcode))
                    self.ISCM = mapcode
                    self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                    self.customMapCode = mapcode
                    return "-1"
        else:
            if self.isSpeed:
                maplist = []
                dbcur.execute('select code from mapeditor where perma = 7')
                rrfRows = dbcur.fetchall()
                if rrfRows is None:
                    pass
                else:
                    for rrf in rrfRows:
                        maplist.append(rrf[0])
                if len(maplist)>=1:
                    runthismap = random.choice(maplist)
                else:
                    runthismap = ""
                if len(maplist)>=2:
                    while runthismap == self.ISCM:
                        runthismap = random.choice(maplist)
                if runthismap=="":
                    self.ISCM = 0
                    return 0
                else:
                    mapcode    = int(runthismap)
                    mapname    = self.server.getMapName(mapcode)
                    mapxml     = self.server.getMapXML(mapcode)
                    yesvotes   = int(self.server.getMapYesVotes(mapcode))
                    novotes    = int(self.server.getMapNoVotes(mapcode))
                    perma      = int(self.server.getMapPerma(mapcode))
                    mapnoexist = int(self.server.getMapDel(mapcode))
                    self.ISCM = mapcode
                    self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                    self.customMapCode = mapcode
                    return "-1"
            elif self.isBooming:
                maplist = ['5608']
                if len(maplist)>=1:
                    runthismap = random.choice(maplist)
                else:
                    runthismap = ""
                if len(maplist)>=2:
                    while runthismap == self.ISCM:
                        runthismap = random.choice(maplist)
                if runthismap=="":
                    self.ISCM = 0
                    return 0
                else:
                    mapcode    = int(runthismap)
                    mapname    = self.server.getMapName(mapcode)
                    mapxml     = self.server.getMapXML(mapcode)
                    yesvotes   = int(self.server.getMapYesVotes(mapcode))
                    novotes    = int(self.server.getMapNoVotes(mapcode))
                    perma      = int(self.server.getMapPerma(mapcode))
                    mapnoexist = int(self.server.getMapDel(mapcode))
                    self.ISCM = mapcode
                    self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                    self.customMapCode = mapcode
                    return "-1"
            elif self.isBotRoom:
                return 0
            elif self.isSurvivor:
                maplist = ['5609']
                if len(maplist)>=1:
                    runthismap = random.choice(maplist)
                else:
                    runthismap = ""
                if len(maplist)>=2:
                    while runthismap == self.ISCM:
                        runthismap = random.choice(maplist)
                if runthismap=="":
                    self.ISCM = 0
                    return 0
                else:
                    mapcode    = int(runthismap)
                    mapname    = self.server.getMapName(mapcode)
                    mapxml     = self.server.getMapXML(mapcode)
                    yesvotes   = int(self.server.getMapYesVotes(mapcode))
                    novotes    = int(self.server.getMapNoVotes(mapcode))
                    perma      = int(self.server.getMapPerma(mapcode))
                    mapnoexist = int(self.server.getMapDel(mapcode))
                    self.ISCM = mapcode
                    self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                    self.customMapCode = mapcode
                    return "-1"
            elif self.isEditeur:
                if self.ISCMV!=0:
                    return self.ISCMV
                else:
                    return 0
            elif self.SPR_Room and self.SPR_CM!=0:
                runthismap=self.SPR_CM
                mapcode    = int(runthismap)
                mapname    = self.server.getMapName(mapcode)
                mapxml     = self.server.getMapXML(mapcode)
                yesvotes   = int(self.server.getMapYesVotes(mapcode))
                novotes    = int(self.server.getMapNoVotes(mapcode))
                perma      = int(self.server.getMapPerma(mapcode))
                mapnoexist = int(self.server.getMapDel(mapcode))
                self.ISCM = mapcode
                self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                self.customMapCode = mapcode
                return "-1"
            else:
                self.ISCM = 0
                self.ISCMdata = [0, "Invalid", "<C><P /><Z><S /><D /><O /></Z></C>", 0, 0, 0, 0]
                if self.isVanilla:
                    runthismap = random.choice(LEVEL_LIST)
                    while runthismap == self.currentWorld:
                        runthismap = random.choice(LEVEL_LIST)
                    if self.specificMap:
                        runthismap = self.currentWorld
                    return runthismap
                else: #ISCM Status: vanilla[0]->vanilla[1]->custom[2]->vanilla[3]->p2[4]->custom[5]
                    if self.ISCMstatus==0: #vanilla map
                        runthismap = random.choice(LEVEL_LIST)
                        while runthismap == self.currentWorld:
                            runthismap = random.choice(LEVEL_LIST)
                        if self.specificMap:
                            runthismap = self.currentWorld
                        return runthismap
                    elif self.ISCMstatus==1: #vanilla map
                        runthismap = random.choice(LEVEL_LIST)
                        while runthismap == self.currentWorld:
                            runthismap = random.choice(LEVEL_LIST)
                        if self.specificMap:
                            runthismap = self.currentWorld
                        return runthismap
                    elif self.ISCMstatus==2: #custom map
                        maplist = []
                        dbcur.execute('select code from mapeditor where perma = 0')
                        rrfRows = dbcur.fetchall()
                        if rrfRows is None:
                            pass
                        else:
                            for rrf in rrfRows:
                                maplist.append(rrf[0])
                        dbcur.execute('select code from mapeditor where perma = 1')
                        rrfRows = dbcur.fetchall()
                        if rrfRows is None:
                            pass
                        else:
                            for rrf in rrfRows:
                                maplist.append(rrf[0])
                        if len(maplist)>=1:
                            runthismap = random.choice(maplist)
                        else:
                            runthismap = ""
                        if len(maplist)>=2:
                            while runthismap == self.ISCM:
                                runthismap = random.choice(maplist)
                        if runthismap=="":
                            runthismap = random.choice(LEVEL_LIST)
                            while runthismap == self.currentWorld:
                                runthismap = random.choice(LEVEL_LIST)
                            if self.specificMap:
                                runthismap = self.currentWorld
                            return runthismap
                        else:
                            mapcode    = int(runthismap)
                            mapname    = self.server.getMapName(mapcode)
                            mapxml     = self.server.getMapXML(mapcode)
                            yesvotes   = int(self.server.getMapYesVotes(mapcode))
                            novotes    = int(self.server.getMapNoVotes(mapcode))
                            perma      = int(self.server.getMapPerma(mapcode))
                            mapnoexist = int(self.server.getMapDel(mapcode))
                            self.ISCM = mapcode
                            self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                            return "-1"
                    elif self.ISCMstatus==3: #vanilla map
                        runthismap = random.choice(LEVEL_LIST)
                        while runthismap == self.currentWorld:
                            runthismap = random.choice(LEVEL_LIST)
                        if self.specificMap:
                            runthismap = self.currentWorld
                        return runthismap
                    elif self.ISCMstatus==4: #P2 map
                        maplist = []
                        dbcur.execute('select code from mapeditor where perma = 2')
                        rrfRows = dbcur.fetchall()
                        if rrfRows is None:
                            pass
                        else:
                            for rrf in rrfRows:
                                maplist.append(rrf[0])
                        if len(maplist)>=1:
                            runthismap = random.choice(maplist)
                        else:
                            runthismap = ""
                        if len(maplist)>=2:
                            while runthismap == self.ISCM:
                                runthismap = random.choice(maplist)
                        if runthismap=="":
                            runthismap = random.choice(LEVEL_LIST)
                            while runthismap == self.currentWorld:
                                runthismap = random.choice(LEVEL_LIST)
                            if self.specificMap:
                                runthismap = self.currentWorld
                            return runthismap
                        else:
                            mapcode    = int(runthismap)
                            mapname    = self.server.getMapName(mapcode)
                            mapxml     = self.server.getMapXML(mapcode)
                            yesvotes   = int(self.server.getMapYesVotes(mapcode))
                            novotes    = int(self.server.getMapNoVotes(mapcode))
                            perma      = int(self.server.getMapPerma(mapcode))
                            mapnoexist = int(self.server.getMapDel(mapcode))
                            self.ISCM = mapcode
                            self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                            return "-1"
                    elif self.ISCMstatus==5: #custom map
                        maplist = []
                        dbcur.execute('select code from mapeditor where perma = 0')
                        rrfRows = dbcur.fetchall()
                        if rrfRows is None:
                            pass
                        else:
                            for rrf in rrfRows:
                                maplist.append(rrf[0])
                        dbcur.execute('select code from mapeditor where perma = 1')
                        rrfRows = dbcur.fetchall()
                        if rrfRows is None:
                            pass
                        else:
                            for rrf in rrfRows:
                                maplist.append(rrf[0])
                        if len(maplist)>=1:
                            runthismap = random.choice(maplist)
                        else:
                            runthismap = ""
                        if len(maplist)>=2:
                            while runthismap == self.ISCM:
                                runthismap = random.choice(maplist)
                        if runthismap=="":
                            runthismap = random.choice(LEVEL_LIST)
                            while runthismap == self.currentWorld:
                                runthismap = random.choice(LEVEL_LIST)
                            if self.specificMap:
                                runthismap = self.currentWorld
                            return runthismap
                        else:
                            mapcode    = int(runthismap)
                            mapname    = self.server.getMapName(mapcode)
                            mapxml     = self.server.getMapXML(mapcode)
                            yesvotes   = int(self.server.getMapYesVotes(mapcode))
                            novotes    = int(self.server.getMapNoVotes(mapcode))
                            perma      = int(self.server.getMapPerma(mapcode))
                            mapnoexist = int(self.server.getMapDel(mapcode))
                            self.ISCM = mapcode
                            self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                            return "-1"
                    elif self.ISCMstatus==6: #vanilla map
                        runthismap = random.choice(LEVEL_LIST)
                        while runthismap == self.currentWorld:
                            runthismap = random.choice(LEVEL_LIST)
                        if self.specificMap:
                            runthismap = self.currentWorld
                        return runthismap
                    elif self.ISCMstatus==7: #racingmap
                        maplist = []
                        dbcur.execute('select code from mapeditor where perma = 7')
                        rrfRows = dbcur.fetchall()
                        if rrfRows is None:
                            pass
                        else:
                            for rrf in rrfRows:
                                maplist.append(rrf[0])
                        dbcur.execute('select code from mapeditor where perma = 0')
                        rrfRows = dbcur.fetchall()
                        if rrfRows is None:
                            pass
                        else:
                            for rrf in rrfRows:
                                maplist.append(rrf[0])
                        if len(maplist)>=1:
                            runthismap = random.choice(maplist)
                        else:
                            runthismap = ""
                        if len(maplist)>=2:
                            while runthismap == self.ISCM:
                                runthismap = random.choice(maplist)
                        if runthismap=="":
                            runthismap = random.choice(LEVEL_LIST)
                            while runthismap == self.currentWorld:
                                runthismap = random.choice(LEVEL_LIST)
                            if self.specificMap:
                                runthismap = self.currentWorld
                            return runthismap
                        else:
                            mapcode    = int(runthismap)
                            mapname    = self.server.getMapName(mapcode)
                            mapxml     = self.server.getMapXML(mapcode)
                            yesvotes   = int(self.server.getMapYesVotes(mapcode))
                            novotes    = int(self.server.getMapNoVotes(mapcode))
                            perma      = int(self.server.getMapPerma(mapcode))
                            mapnoexist = int(self.server.getMapDel(mapcode))
                            self.ISCM = mapcode
                            self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                            return "-1"
                    elif self.ISCMstatus==8: #vanilla map
                        runthismap = random.choice(LEVEL_LIST)
                        while runthismap == self.currentWorld:
                            runthismap = random.choice(LEVEL_LIST)
                        if self.specificMap:
                            runthismap = self.currentWorld
                        return runthismap
                    elif self.ISCMstatus==9: #P4 map
                        maplist = []
                        dbcur.execute('select code from mapeditor where perma = 4')
                        rrfRows = dbcur.fetchall()
                        if rrfRows is None:
                            pass
                        else:
                            for rrf in rrfRows:
                                maplist.append(rrf[0])
                        if len(maplist)>=1:
                            runthismap = random.choice(maplist)
                        else:
                            runthismap = ""
                        if len(maplist)>=2:
                            while runthismap == self.ISCM:
                                runthismap = random.choice(maplist)
                        if runthismap=="":
                            runthismap = random.choice(LEVEL_LIST)
                            while runthismap == self.currentWorld:
                                runthismap = random.choice(LEVEL_LIST)
                            if self.specificMap:
                                runthismap = self.currentWorld
                            return runthismap
                        else:
                            mapcode    = int(runthismap)
                            mapname    = self.server.getMapName(mapcode)
                            mapxml     = self.server.getMapXML(mapcode)
                            yesvotes   = int(self.server.getMapYesVotes(mapcode))
                            novotes    = int(self.server.getMapNoVotes(mapcode))
                            perma      = int(self.server.getMapPerma(mapcode))
                            mapnoexist = int(self.server.getMapDel(mapcode))
                            self.ISCM = mapcode
                            self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                            return "-1"
							
                    elif self.ISCMstatus==10: #P8 map
                        maplist = []
                        dbcur.execute('select code from mapeditor where perma = 8')
                        rrfRows = dbcur.fetchall()
                        if rrfRows is None:
                            pass
                        else:
                            for rrf in rrfRows:
                                maplist.append(rrf[0])
                        if len(maplist)>=1:
                            runthismap = random.choice(maplist)
                        else:
                            runthismap = ""
                        if len(maplist)>=2:
                            while runthismap == self.ISCM:
                                runthismap = random.choice(maplist)
                        if runthismap=="":
                            runthismap = random.choice(LEVEL_LIST)
                            while runthismap == self.currentWorld:
                                runthismap = random.choice(LEVEL_LIST)
                            if self.specificMap:
                                runthismap = self.currentWorld
                            return runthismap
                        else:
                            mapcode    = int(runthismap)
                            mapname    = self.server.getMapName(mapcode)
                            mapxml     = self.server.getMapXML(mapcode)
                            yesvotes   = int(self.server.getMapYesVotes(mapcode))
                            novotes    = int(self.server.getMapNoVotes(mapcode))
                            perma      = int(self.server.getMapPerma(mapcode))
                            mapnoexist = int(self.server.getMapDel(mapcode))
                            self.ISCM = mapcode
                            self.ISCMdata = [mapcode, mapname, mapxml, yesvotes, novotes, perma, mapnoexist]
                            return "-1"
                    elif self.ISCMstatus==1: #Special 777 map
                        return 777
                        
                    else:
                        logging.info("Room "+str(self.name)+" got an invalid ISCM Status of "+str(self.ISCMstatus)+".")
                        self.ISCMstatus=0
                        runthismap = random.choice(LEVEL_LIST)
                        while runthismap == self.currentWorld:
                            runthismap = random.choice(LEVEL_LIST)
                        if self.specificMap:
                            runthismap = self.currentWorld
                        return runthismap

    def closeVoting(self):
        self.initVotingMode=False
        self.votingBox=False
        if self.voteCloseTimer:
            try:
                self.voteCloseTimer.cancel()
            except:
                self.voteCloseTimer=None
        self.worldChange()

    def GenerateExplode(self):
        if self.isBooming:
            if self.customMapCode == 5436:
                number = random.randrange(1, 9)
                if number == 1: x = 655
                elif number == 2: x = 561
                elif number == 3: x = 454
                elif number == 4: x = 381
                elif number == 5: x = 328
                elif number == 6: x = 230
                elif number == 7: x = 127
                elif number == 8: x = 63
                elif number == 9: x = 9
                else: x = 1
                if number == 1: y = 198
                elif number == 2: y = 160
                elif number == 3: y = 151
                elif number == 4: y = 104
                elif number == 5: y = 152
                elif number == 6: y = 109
                elif number == 7: y = 179
                elif number == 8: y = 152
                elif number == 9: y = 105
                else: y = 1
                for playerCode, client in self.clients.items():
                    client.sendData("\x05\x11", [x, y, 100, 100, 100, 0])
                reactor.callLater(5, self.GenerateExplode)
            elif self.MegaBooming == "1":
                x = random.randrange(1, 800)
                y = random.randrange(1, 400)
                xx = random.randrange(1, 800)
                yy = random.randrange(1, 400)
                for playerCode, client in self.clients.items():
                    client.sendData("\x05\x11", [x, y, 100, 100, 100, 0])
                    client.sendData("\x05\x11", [xx, yy, 300, 300, 300, 0])
                reactor.callLater(0.1, self.GenerateExplode)
            
            else:
                x = random.randrange(1, 800)
                y = random.randrange(1, 400)
                xx = random.randrange(1, 800)
                yy = random.randrange(1, 400)
                for playerCode, client in self.clients.items():
                    client.sendData("\x05\x11", [x, y, 100, 100, 100, 0])
                    client.sendData("\x05\x11", [xx, yy, 300, 300, 300, 0])
                reactor.callLater(5, self.GenerateExplode)
        else:
            pass
        
    
    def SurvivorDeadTimer(self):
        self.isDeadTimer = 1
        self.isSurvivorWinner = 1
        shaman = self.currentShamanName
        message = "<N>Время кончилось, <ROSE><a href='event:" + shaman + "'>" + shaman + "</a> <N>в норе. <VP>^_^"
        data="\x00"+"\x00\x00"+struct.pack('!h', len(message))+message+"\x00\x00"
        self.sendAllBin("\x06\x0A", data)
    
    def SurvivorNewCham(self):
        self.isDeadTimer = 0
        self.isSurvivorWinner = 0
        shaman = self.currentShamanName
        message = "<N>Спасайтесь <ROSE><a href='event:" + shaman + "'>" + shaman + "</a> <N>!"
        data="\x00"+"\x00\x00"+struct.pack('!h', len(message))+message+"\x00\x00"
        self.sendAllBin("\x06\x0A", data)
        
      

    def SurvivorWin(self):
        self.isDeadTimer = 1
        self.isSurvivorWinner = 1
        shaman = self.currentShamanName
        message = "<N>Успешно, <ROSE><a href='event:" + shaman + "'>" + shaman + "</a><N>!"
        data="\x00"+"\x00\x00"+struct.pack('!h', len(message))+message+"\x00\x00"
        self.sendAllBin("\x06\x0A", data)
         
    def SurvivorDead(self):
        self.isDeadTimer = 1
        self.isSurvivorWinner = 0
        shaman = self.currentShamanName
        message = "<N>Брр, <ROSE><a href='event:" + shaman + "'>" + shaman + "</a><N> умер. <VP>T_T"
        data="\x00"+"\x00\x00"+struct.pack('!h', len(message))+message+"\x00\x00"
        self.sendAllBin("\x06\x0A", data)
        
    def worldChange(self):
        if self.isBotRoom:
            return 0
        if self.isSurvivor:
            if self.isDeadTimer == 0:
                if self.isSurvivorWinner == 0:
                    self.SurvivorDeadTimer()
        
        if self.killAfkTimer:
            try:
                self.killAfkTimer.cancel()
            except:
                self.killAfkTimer=None
        if self.initVotingMode:
            if self.votingBox:
                pass
                #print "Tried to go to next map during voting."
            else:
                if self.ISCMdata[5]==0 and self.ISCM!=0:
                    if self.getPlayerCount()>=2:
                        self.votingMode=True
                        self.votingBox=True
                        self.voteCloseTimer = reactor.callLater(8, self.closeVoting)
                        for playerCode, client in self.clients.items():
                            client.sendVoteBox(self.ISCMdata[1], self.ISCMdata[3], self.ISCMdata[4])
                    else:
                        self.votingMode=False
                        self.closeVoting()
                else:
                    self.votingMode=False
                    self.closeVoting()
        elif self.isEditeur and self.ISCMV==0:
            pass
        else:
            if self.votingMode:
                TotalYes=self.ISCMdata[3]+self.recievedYes
                TotalNo=self.ISCMdata[4]+self.recievedNo
                if TotalYes+TotalNo>=100:
                    TotalVotes=TotalYes+TotalNo
                    Rating=(1.0*TotalYes/TotalVotes)*100
                    Rating, adecimal, somejunk = str(Rating).partition(".")
                    if int(Rating)<50:
                        dbcur.execute('UPDATE mapeditor SET perma = ? WHERE code = ?', ["44", self.ISCMdata[0]])
                dbcur.execute('UPDATE mapeditor SET yesvotes = ? WHERE code = ?', [int(TotalYes), self.ISCMdata[0]])
                dbcur.execute('UPDATE mapeditor SET novotes = ? WHERE code = ?', [int(TotalNo), self.ISCMdata[0]])
                self.votingMode=False
                self.recievedYes=0
                self.recievedNo =0
                for playerCode, client in self.clients.items():
                    client.Voted=False
                    client.QualifiedVoter=False
            self.initVotingMode=True

            self.currentSyncroniserCode = None
            self.isCurrentlyPlayingRoom = False

            self.identifiantTemporaire=-1
            NextCodePartie=self.CodePartieEnCours+1
            if NextCodePartie>9999:
                NextCodePartie=1
            self.CodePartieEnCours=NextCodePartie
            self.CheckedPhysics=False

            self.ISCMstatus+=1
            if self.ISCMstatus>10:
                self.ISCMstatus=0

            self.isHardSham=False

            for playerCode, client in self.clients.items():
                client.isAfk=True

            if self.isCatchTheCheeseMap==True:
                self.isCatchTheCheeseMap=False
            else:
                if self.isDoubleMap:
                    numCompleted = self.FSnumCompleted-1
                else:
                    numCompleted = self.numCompleted-1
                if numCompleted < 0:
                    numCompleted = 0
                for playerCode, client in self.clients.items():
                    if client.playerCode == self.currentShamanCode:
                        client.score = numCompleted
                if self.currentShamanName:
                    self.sendAll("\x08" + "\x11",[self.currentShamanName, numCompleted])

            if self.isDoubleMap:
                if self.isCatchTheCheeseMap==True:
                    self.isCatchTheCheeseMap=False
                else:
                    numCompleted = self.SSnumCompleted-1
                    if numCompleted < 0:
                        numCompleted = 0
                    for playerCode, client in self.clients.items():
                        if client.playerCode == self.currentSecondShamanCode:
                            client.score = numCompleted
                    if self.currentSecondShamanName:
                        self.sendAll("\x08" + "\x11",[self.currentSecondShamanName, numCompleted])


            self.currentShamanCode = None
            self.currentSecondShamanCode = None
            self.currentShamanName = None
            self.currentSecondShamanName = None
            self.isDeadTimer = 1
            self.isSurvivorWinner = 1
            self.ZombieRoom = False

            for playerCode, client in self.clients.items():
                client.resetPlay()

            self.isDoubleMap = False
            if not self.specificMap:
                runthismap = self.selectMap()
                self.currentWorld = runthismap

            if int(self.currentWorld) in [44, 45, 46, 47, 48, 49, 50, 51, 52, 53] or self.ISCMstatus == 10 and int(self.getPlayerCount())>=2:
                self.isDoubleMap = True
            #if random.randrange(1000, 1030)==1024 and int(self.getPlayerCount())>=2:
            #    self.isDoubleMap = True
            if self.currentWorld==888:
                self.worldChangeTimer = reactor.callLater(60, self.worldChange)
            else:
                self.worldChangeTimer = reactor.callLater(self.roundTime, self.worldChange)
            #self.worldChangeTimer = reactor.callLater(120, self.worldChange)
            self.killAfkTimer = reactor.callLater(30, self.killAfk)
            if self.autoRespawn:
                if self.autoRespawnTimer:
                    try:
                        self.autoRespawnTimer.cancel()
                    except:
                        self.autoRespawnTimer=None
                self.autoRespawnTimer = reactor.callLater(15, self.respawnMice)
            if self.isSandbox:
                try:
                    self.worldChangeTimer.cancel()
                except:
                    self.worldChangeTimer=None
                try:
                    self.killAfkTimer.cancel()
                except:
                    self.killAfkTimer=None
            self.gameStartTime = time.time()
                
            self.numCompleted = 0
            self.FSnumCompleted = 0
            self.SSnumCompleted = 0
            self.numGotCheese = 0
            self.changed20secTimer = False
            for playerCode, client in self.clients.items():
                client.startPlay(0, 0)
            
            # for playerCode, client in self.clients.items():
                # self.server.autorestart = self.server.autorestart+1
                # if self.server.autorestart == 1:
                    # if self.gameStartTime >= self.server.autorestarttimestamp: 
                        # client.sendServerMessage("Arret automatique du serveur dans 2 minutes.")
                        # logging.warning("Arret automatique du serveur (timestamp : "+self.server.autorestarttimestamp+")")
                        # client.sendModMessageChannel("Arrêt automatique du serveur. Raison : heure planifiée atteinte.")
                        
                        
                        # self.stoptimer = reactor.callLater(120, self.server.astopServer)
                    # else : 
                        # self.autorestart = 0
                        #Autorestart
                
                
            self.closeRoomRoundJoinTimer = reactor.callLater(2, self.closeRoomRoundJoin)
            if self.isSurvivor:
                self.SurvivorNewCham()
            

    def worldChangeSpecific(self, mapnumber, custom = None):
        if self.isBotRoom:
            return 0
        mapnumber = int(mapnumber)
        self.identifiantTemporaire=-1
        NextCodePartie=self.CodePartieEnCours+1
        if NextCodePartie>9999:
            NextCodePartie=1
        self.CodePartieEnCours=NextCodePartie
        self.CheckedPhysics=False
        if self.worldChangeTimer:
            try:
                self.worldChangeTimer.cancel()
            except:
                self.worldChangeTimer=None
        if self.killAfkTimer:
            try:
                self.killAfkTimer.cancel()
            except:
                self.killAfkTimer=None
        self.currentSyncroniserCode = None
        self.isCurrentlyPlayingRoom = False
        self.isHardSham=False
        for playerCode, client in self.clients.items():
            client.isAfk=True
        if self.isCatchTheCheeseMap==True:
            self.isCatchTheCheeseMap=False
        else:
            if self.isDoubleMap:
                numCompleted = self.FSnumCompleted-1
            else:
                numCompleted = self.numCompleted-1
            if numCompleted < 0:
                numCompleted = 0
            if self.currentShamanName:
                self.sendAll("\x08" + "\x11",[self.currentShamanName, numCompleted])

        if self.isDoubleMap:
            for playerCode, client in self.clients.items():
                if client.playerCode == self.currentSecondShamanCode:
                    client.score = 0
            if self.isCatchTheCheeseMap==True:
                self.isCatchTheCheeseMap=False
            else:
                numCompleted = self.SSnumCompleted-1
                if numCompleted < 0:
                    numCompleted = 0
                if self.currentSecondShamanName:
                    self.sendAll("\x08" + "\x11",[self.currentSecondShamanName, numCompleted])
        self.currentShamanCode = None
        self.currentSecondShamanCode = None
        self.currentShamanName = None
        self.currentSecondShamanName = None
        self.ZombieRoom = False
        for playerCode, client in self.clients.items():
            client.resetPlay()
        self.isDoubleMap = False
        if self.isBooming:
            self.ActionTimer = reactor.callLater(5, self.GenerateExplode)
        if custom:
            self.currentWorld = self.selectMapSpecific(mapnumber, True)
        else:
            self.currentWorld = self.selectMapSpecific(mapnumber, False)
        if int(self.currentWorld) in [44, 45, 46, 47, 48, 49, 50, 51, 52, 53] and int(self.getPlayerCount())>=2:
            self.isDoubleMap = True
        if self.currentWorld==888:
            self.worldChangeTimer = reactor.callLater(60, self.worldChange)
        elif self.isBotRoom:
            self.worldChangeTimer = reactor.callLater(86400, self.worldChange)
        elif self.isSurvivor:
            self.worldChangeTimer = reactor.callLater(120, self.worldChange)
        elif self.isBootcamp:
            self.worldChangeTimer = reactor.callLater(360, self.worldChange)
        elif self.isSpeed:
            self.worldChangeTimer = reactor.callLater(60, self.worldChange)
        else:
            self.worldChangeTimer = reactor.callLater(self.roundTime, self.worldChange)
        self.killAfkTimer = reactor.callLater(30, self.killAfk)
        if self.isSandbox:
            try:
                self.worldChangeTimer.cancel()
            except:
                self.worldChangeTimer=None
            try:
                self.killAfkTimer.cancel()
            except:
                self.killAfkTimer=None
        self.gameStartTime = time.time()
        self.numCompleted = 0
        self.FSnumCompleted = 0
        self.SSnumCompleted = 0
        self.numGotCheese = 0
        self.changed20secTimer = False
        for playerCode, client in self.clients.items():
            client.startPlay(0, 0)
        self.closeRoomRoundJoinTimer = reactor.callLater(0, self.closeRoomRoundJoin)
        if self.isSurvivor:
                self.SurvivorNewCham()

    def checkShouldChangeWorld(self):
        if self.isBootcamp:
            pass
        if self.isSpeed:
            pass
        if self.isSurvivor:
            pass
        if self.isTribe:
            pass
        elif self.isSandbox:
            pass
        else:
            if all(client.isDead for client in self.clients.values()):
                try:
                    self.worldChangeTimer.cancel()
                except:
                    self.worldChangeTimer=None
                if self.killAfkTimer:
                    try:
                        self.killAfkTimer.cancel()
                    except:
                        self.killAfkTimer=None
                if self.closeRoomRoundJoinTimer:
                    try:
                        self.closeRoomRoundJoinTimer.cancel()
                    except:
                        self.closeRoomRoundJoinTimer=None
                self.worldChange()

    def giveShamanHardSave(self):
        for playerCode, client in self.clients.items():
            if client.playerCode == self.currentShamanCode:
                client.hardModeSaves += 1
                if client.privilegeLevel != 0:
                    if client.hardModeSaves in client.hardShamTitleCheckList:
                        unlockedtitle=client.hardShamTitleDictionary[client.hardModeSaves]
                        client.sendUnlockedTitle(client.playerCode, unlockedtitle)
                        client.HardModeTitleList=client.HardModeTitleList+[unlockedtitle]
                        client.titleList = ["0"]+client.GiftTitleList+client.ShamanTitleList+client.HardModeTitleList+client.CheeseTitleList+client.FirstTitleList+client.ShopTitleList
                        if client.privilegeLevel>=10 and not client.isDrawer:
                            client.titleList = client.titleList+["440","444"]
                        client.titleList = filter(None, client.titleList)
                        client.sendTitleList()
                return 1
        return 0

    def giveShamanSave(self):
        for playerCode, client in self.clients.items():
            if client.playerCode == self.currentShamanCode:
                client.micesaves += 1
                if client.privilegeLevel != 0:
                    if client.micesaves in client.shamanTitleCheckList:
                        unlockedtitle=client.shamanTitleDictionary[client.micesaves]
                        client.sendUnlockedTitle(client.playerCode, unlockedtitle)
                        client.ShamanTitleList=client.ShamanTitleList+[unlockedtitle]
                        client.titleList = ["0"]+client.GiftTitleList+client.ShamanTitleList+client.HardModeTitleList+client.CheeseTitleList+client.FirstTitleList+client.ShopTitleList
                        if client.privilegeLevel>=10 and not client.isDrawer:
                            client.titleList = client.titleList+["440","444"]
                        client.titleList = filter(None, client.titleList)
                        client.sendTitleList()
                return 1
        return 0

    def giveSecondShamanSave(self):
        for playerCode, client in self.clients.items():
            if client.playerCode == self.currentSecondShamanCode:
                client.micesaves += 1
                if client.privilegeLevel != 0:
                    if client.micesaves in client.shamanTitleCheckList:
                        unlockedtitle=client.shamanTitleDictionary[client.micesaves]
                        client.sendUnlockedTitle(client.playerCode, unlockedtitle)
                        client.ShamanTitleList=client.ShamanTitleList+[unlockedtitle]
                        client.titleList = ["0"]+client.GiftTitleList+client.ShamanTitleList+client.CheeseTitleList+client.FirstTitleList+client.ShopTitleList
                        if client.privilegeLevel>=10 and not client.isDrawer:
                            client.titleList = client.titleList+["440","444"]
                        client.titleList = filter(None, client.titleList)
                        client.sendTitleList()
                return 1
        return 0

    def checkDeathCount(self):
        counts=[0,0] #Dead, Alive
        for playerCode, client in self.clients.items():
            if client.isDead:
                counts[0]=counts[0]+1
            else:
                counts[1]=counts[1]+1
        return counts
    def checkIfTooFewRemaining(self):
        counts=[0,0] #Dead, Alive
        for playerCode, client in self.clients.items():
            if client.isDead:
                counts[0]=counts[0]+1
            else:
                counts[1]=counts[1]+1
        if self.getPlayerCount>=2:
            if counts[1]<=2:
                return True
        return False
        
    def checkIfTooFewRemainingSurvivor(self):
        counts=[0,0] #Dead, Alive
        for playerCode, client in self.clients.items():
            if client.isDead:
                counts[0]=counts[0]+1
            else:
                counts[1]=counts[1]+1
        if self.getPlayerCount>=1:
            if counts[1]<=1:
                return True
        return False
        
    def checkIfDoubleShamansAreDead(self):
        result=0
        for playerCode, client in self.clients.items():
            if client.playerCode == self.currentShamanCode or client.playerCode == self.currentSecondShamanCode:
                if client.isDead:
                    result+=1
                else:
                    pass
        if result==2:
            return True
        else:
            return False
    def checkIfShamanIsDead(self):
        for playerCode, client in self.clients.items():
            if client.playerCode == self.currentShamanCode:
                if client.isDead:
                    pass
                else:
                    return False
        return True

    def checkIfShamanCanGoIn(self):
        allgone=1
        #if all(client.isDead for client in self.clients.values()):
        for playerCode, client in self.clients.items():
            if client.playerCode != self.currentShamanCode:
                if client.isDead:
                    pass
                else:
                    allgone=0
        if allgone==1:
            return 1
        else:
            return 0

    def checkIfDoubleShamanCanGoIn(self):
        counts=[0,0,0,0] #Dead Shamans, Dead Mice, Not Dead Shamans, Not Dead Mice
        #if all(client.isDead for client in self.clients.values()):
        for playerCode, client in self.clients.items():
            if client.isDead:
                if client.playerCode == self.currentShamanCode:
                    counts[0]=counts[0]+1
                elif client.playerCode == self.currentSecondShamanCode:
                    counts[0]=counts[0]+1
                else:
                    counts[1]=counts[1]+1
            else:
                if client.playerCode == self.currentShamanCode:
                    counts[2]=counts[2]+1
                elif client.playerCode == self.currentSecondShamanCode:
                    counts[2]=counts[2]+1
                else:
                    counts[3]=counts[3]+1
        #print counts
        if counts[3]==0:
            return True
        else:
            return False

    def resetSandbox(self):
        if self.isSandbox:
            for playerCode, client in self.clients.items():
                resetpscore=0
                client.sendPlayerDied(client.playerCode, resetpscore)
                client.isDead=True
            if all(client.isDead for client in self.clients.values()):
                #self.worldChangeTimer.cancel()
                #self.worldChange()
                for playerCode, client in self.clients.items():
                    client.resetPlay()
                self.currentWorld = self.currentWorld
                for playerCode, client in self.clients.items():
                    client.startPlay(0,0)
        else:

            pass
    def resetRoom(self):
        if self.worldChangeTimer:
            try:
                self.worldChangeTimer.cancel()
            except:
                self.worldChangeTimer=None
        if self.killAfkTimer:
            try:
                self.killAfkTimer.cancel()
            except:
                self.killAfkTimer=None
        if self.autoRespawnTimer:
            try:
                self.autoRespawnTimer.cancel()
            except:
                self.autoRespawnTimer=None
        for playerCode, client in self.clients.items():
            resetpscore=0
            client.sendPlayerDied(client.playerCode, resetpscore)
            client.isDead=True
        if all(client.isDead for client in self.clients.values()):
            self.worldChange()
            #for playerCode, client in self.clients.items():
            #    client.resetPlay()
            #self.currentWorld = self.currentWorld
            #for playerCode, client in self.clients.items():
            #    client.startPlay(0,0)
    def moveAllRoomClients(self, name, rec = False):
        if rec:
            for playerCode, client in self.clients.items():
                self.MoveTimer = reactor.callLater(0, client.enterRoom, self.server.recommendRoom())
        else:
            for playerCode, client in self.clients.items():
                self.MoveTimer = reactor.callLater(0, client.enterRoom, str(name))

    def addClient(self, newClient):
        SPEC = 0

        if self.isCurrentlyPlayingRoom:
            newClient.isDead=True
            SPEC = 1

        self.clients[newClient.playerCode] = newClient
        newClient.room = self

        if newClient.isHidden:
            pass
        else:
            if self.sNP:
                newClient.sendNewPlayer(newClient.getPlayerData())

        newClient.startPlay(self.ISCM, SPEC)

        #print self.clients

    def updatesqlserver(self):
        for playerCode, client in self.clients.items():
            if client.username.startswith("*"):
                pass
            else:
                client.updateSelfSQL()

    def removeClient(self, removeClient):
        if removeClient.playerCode in self.clients:
            for playerCode, client in self.clients.items():
                if playerCode == removeClient.playerCode:
                    if client.username.startswith("*"):
                        pass
                    else:
                        client.updateSelfSQL()

            del self.clients[removeClient.playerCode]

            if self.getPlayerCount() == 0:
                self.server.closeRoom(self)
                return

            removeClient.sendPlayerDisconnect(removeClient.playerCode)
            if self.currentSyncroniserCode == removeClient.playerCode:
                newSyncroniser = random.choice(self.clients.values())
                newSyncroniser.isSyncroniser = True

                self.currentSyncroniserCode = newSyncroniser.playerCode
                newSyncroniser.sendSynchroniser(newSyncroniser.playerCode)

        self.checkShouldChangeWorld()

    def changeSyncroniserRandom(self):
        newSyncroniser = random.choice(self.clients.values())
        newSyncroniser.isSyncroniser = True
        self.currentSyncroniserCode = newSyncroniser.playerCode
        newSyncroniser.sendSynchroniser(newSyncroniser.playerCode)

    def changeSyncroniserSpecific(self, username):
        newSyncroniser = False
        for room in self.server.rooms.values():
            for playerCode, client in room.clients.items():
                if client.username == username:
                    newSyncroniser = client
                    break
        if newSyncroniser:
            newSyncroniser.isSyncroniser = True
            self.currentSyncroniserCode = newSyncroniser.playerCode
            newSyncroniser.sendSynchroniser(newSyncroniser.playerCode)

    def changeScore(self, playerCode, score):
        for playerCode, client in self.clients.items():
            if client.playerCode == playerCode:
                client.score = score

    def forceEmoteAll(self, emoteCode):
        for playerCode, client in self.clients.items():
            for playerCode2, client2 in self.clients.items():
                client.sendPlayerEmote(playerCode2, emoteCode, False)

    def informAll(self, clientFunction, args):
        logging.warning("Deprecated Function \"informAll\". Vars: clientFunction-"+str(clientFunction)+" args-"+str(args))
        for playerCode, client in self.clients.items():
            clientFunction(client, *args)

    def informAllOthers(self, senderClient, clientFunction, args):
        logging.warning("Deprecated Function \"informAllOthers\". Vars: clientFunction-"+str(clientFunction)+" args-"+str(args))
        for playerCode, client in self.clients.items():
            if playerCode != senderClient.playerCode:
                clientFunction(client, *args)

    def sendSync(self, eventTokens, data = None):
        for playerCode, client in self.clients.items():
            if client.isSyncroniser:
                client.sendData(eventTokens, data)
    def sendAll(self, eventTokens, data = None):
        for playerCode, client in self.clients.items():
            client.sendData(eventTokens, data)
    def sendMusic(self, eventTokens, data = None):
        for playerCode, client in self.clients.items():
            if client.musicOff:
                pass
            else:
                client.sendData(eventTokens, data)
    def sendAllOthers(self, senderClient, eventTokens, data):
        for playerCode, client in self.clients.items():
            if client.playerCode != senderClient.playerCode:
                client.sendData(eventTokens, data)
    def sendAllOthersAndSelf(self, senderClient, eventTokens, data):
        logging.warning("Deprecated Function \"sendAllOthersAndSelf\". Vars: eventTokens-"+str(repr(eventTokens))+" data-"+str(repr(data)))
        for playerCode, client in self.clients.items():
            client.sendData(eventTokens, data)
            
    def sendAllChatSpe(self, sendplayerCode, username, message):
        for playerCode, client in self.clients.items():
            #client.sendData("\x06\x06", sendplayerCode+username+sendMessage+"\x00\x00", True)
            Tmessage=message
            sendMessage=struct.pack('!h', len(Tmessage))+Tmessage
            reactor.callLater(0, client.sendData, "\x06\x06", sendplayerCode+username+sendMessage+"\x00\x00", True)

    def sendAllChat(self, sendplayerCode, username, message):
        for playerCode, client in self.clients.items():
            if client.muteChat:
                pass
            else:
                if client.censorChat:
                    Cmessage=client.censorMessage(message)
                    if client.Translating:
                        try:
                            Ltype=LanguageDetector().detect(message).lang_code
                        except:
                            Ltype="en"
                        if Ltype == "de":
                            sendMessage=Cmessage
                        else:
                            try:
                                Cmessage=client.safe_str(Translator().translate(Cmessage, lang_to="en"))
                            except:
                                pass
                    sendMessage=struct.pack('!h', len(Cmessage))+Cmessage
                else:
                    if client.Translating:
                        try:
                            Ltype=LanguageDetector().detect(message).lang_code
                        except:
                            Ltype="en"
                        if Ltype == "de":
                            sendMessage=message
                        else:
                            Tmessage=message
                            try:
                                Tmessage=client.safe_str(Translator().translate(Tmessage, lang_to="en"))
                            except:
                                pass
                            sendMessage=struct.pack('!h', len(Tmessage))+Tmessage
                    else:
                        sendMessage=struct.pack('!h', len(message))+message
                #client.sendData("\x06\x06", sendplayerCode+username+sendMessage+"\x00\x00", True)
                reactor.callLater(0, client.sendData, "\x06\x06", sendplayerCode+username+sendMessage+"\x00\x00", True)
    def sendAllChatF(self, sendplayerCode, username, message, senderClient):
        for playerCode, client in self.clients.items():

            if int(client.playerCode)==int(senderClient.playerCode):
                if client.muteChat:
                    pass
                else:
                    if client.censorChat:
                        Cmessage=client.censorMessage(message)
                        if client.Translating:
                            try:
                                Ltype=LanguageDetector().detect(message).lang_code
                            except:
                                Ltype="en"
                            if Ltype == "de":
                                sendMessage=Cmessage
                            else:
                                try:
                                    Cmessage=client.safe_str(Translator().translate(Cmessage, lang_to="en"))
                                except:
                                    pass
                        sendMessage=struct.pack('!h', len(Cmessage))+Cmessage
                    else:
                        if client.Translating:
                            try:
                                Ltype=LanguageDetector().detect(message).lang_code
                            except:
                                Ltype="en"
                            if Ltype == "de":
                                sendMessage=message
                            else:
                                Tmessage=message
                                try:
                                    Tmessage=client.safe_str(Translator().translate(Tmessage, lang_to="en"))
                                except:
                                    pass
                                sendMessage=struct.pack('!h', len(Tmessage))+Tmessage
                        else:
                            sendMessage=struct.pack('!h', len(message))+message
                    client.sendData("\x06\x06", sendplayerCode+username+sendMessage+"\x00\x00", True)
    def sendAllBin(self, eventTokens, data = None):
        for playerCode, client in self.clients.items():
            client.sendData(eventTokens, data, True)
    def sendAllOthersBin(self, senderClient, eventTokens, data):
        for playerCode, client in self.clients.items():
            if client.playerCode != senderClient.playerCode:
                client.sendData(eventTokens, data, True)
    def sendAllPvSpec(self, eventTokens, privlevels, data = None, binary = None):
        for playerCode, client in self.clients.items():
            if client.privilegeLevel in privlevels:
                if not TS:
                    if client.privilegeLevel>=10:
                        if eventTokens in ("\x06\x0A"):
                            if client.isDrawer:
                                pass
                            else:
                                if binary:
                                    client.sendData(eventTokens, data, True)
                                else:
                                    client.sendData(eventTokens, data)
                        else:
                            if binary:
                                client.sendData(eventTokens, data, True)
                            else:
                                client.sendData(eventTokens, data)
                    else:
                        if binary:
                            client.sendData(eventTokens, data, True)
                        else:
                            client.sendData(eventTokens, data)
                else:
                    if client.privilegeLevel>=10 and not client.isDrawer:
                        if eventTokens in ("\x06\x0A"):
                            if client.isDrawer:
                                pass
                            else:
                                if binary:
                                    client.sendData(eventTokens, data, True)
                                else:
                                    client.sendData(eventTokens, data)
                        else:
                            if binary:
                                client.sendData(eventTokens, data, True)
                            else:
                                client.sendData(eventTokens, data)
                    else:
                        if not client.isDrawer:
                            if binary:
                                client.sendData(eventTokens, data, True)
                            else:
                                client.sendData(eventTokens, data)
    def sendAllPvSpecOthers(self, senderClient, eventTokens, privlevels, data = None, binary = None):
        for playerCode, client in self.clients.items():
            if client.privilegeLevel in privlevels:
                if not TS:
                    if client.privilegeLevel>=10:
                        if client.playerCode != senderClient.playerCode:
                            if binary:
                                client.sendData(eventTokens, data, True)
                            else:
                                client.sendData(eventTokens, data)
                        else:
                            if binary:
                                client.sendData(eventTokens, data, True)
                            else:
                                client.sendData(eventTokens, data)
                else:
                    if client.privilegeLevel>=10 and not client.isDrawer:
                        if client.playerCode != senderClient.playerCode:
                            if binary:
                                client.sendData(eventTokens, data, True)
                            else:
                                client.sendData(eventTokens, data)
                        else:
                            if binary:
                                client.sendData(eventTokens, data, True)
                            else:
                                client.sendData(eventTokens, data)
    def sendWholeTribeRoom(self, senderClient, eventTokens, data, binary = None, NotIgnorable = None):
        #Must only be called by TransformiceServer
        for playerCode, client in self.clients.items():
            if str(client.TribeCode) == str(senderClient.TribeCode):
                if client.isInTribe:
                    if binary:
                        if NotIgnorable:
                            client.sendData(eventTokens, data, True)
                        else:
                            if not client.muteTribe:
                                client.sendData(eventTokens, data, True)
                    else:
                        if NotIgnorable:
                            client.sendData(eventTokens, data)
                        else:
                            if not client.muteTribe:
                                client.sendData(eventTokens, data)
    def sendWholeTribeOthersRoom(self, senderClient, eventTokens, data, binary = None, NotIgnorable = None):
        #Must only be called by TransformiceServer
        for playerCode, client in self.clients.items():
            if str(client.TribeCode) == str(senderClient.TribeCode):
                if client.isInTribe:
                    if client.playerCode != senderClient.playerCode:
                        if binary:
                            if NotIgnorable:
                                client.sendData(eventTokens, data, True)
                            else:
                                if not client.muteTribe:
                                    client.sendData(eventTokens, data, True)
                        else:
                            if NotIgnorable:
                                client.sendData(eventTokens, data)
                            else:
                                if not client.muteTribe:
                                    client.sendData(eventTokens, data)
    def sendTribeInfoUpdateRoom(self, code, greeting = None, playerlist = None):
        #Must only be called by TransformiceServer
        for playerCode, client in self.clients.items():
            if str(client.TribeCode) == str(code):
                UserTribeInfo=self.server.getUserTribeInfo(client.username)
                if UserTribeInfo[0]=="":
                    client.TribeCode    = ""
                    client.TribeName    = ""
                    client.TribeFromage = 0
                    client.TribeMessage = ""
                    client.TribeInfo    = ""
                    client.TribeRank    = ""
                    client.isInTribe    = False
                    client.muteTribe    = False
                    client.sendTribeZeroGreeting()
                    client.tribe        = self.server.getTribeName(client.username)
                else:
                    TribeData           = self.server.getTribeData(UserTribeInfo[1])
                    client.TribeCode    = TribeData[0]
                    client.TribeName    = TribeData[1]
                    client.TribeFromage = TribeData[2]
                    client.TribeMessage = TribeData[3]
                    client.TribeInfo    = TribeData[4].split("|")
                    client.TribeRank    = UserTribeInfo[2]
                    client.isInTribe    = True
                    if greeting:
                        client.sendTribeGreeting()
                    if playerlist:
                        client.sendTribeList()

    def sendWholeServer(self, senderClient, eventTokens, data, binary = None):
        for room in self.server.rooms.values():
            if binary:
                reactor.callLater(0, room.sendAllBin, eventTokens, data)
            else:
                reactor.callLater(0, room.sendAll, eventTokens, data)
            #for playerCode, client in room.clients.items():
            #    if binary:
            #        client.sendData(eventTokens, data, True)
            #    else:
            #        client.sendData(eventTokens, data)

    def checkRoomInvite(self, senderClient, name):
        for room in self.server.rooms.values():
            if room.namewihout == "\x03[Tribe] "+name:
                if senderClient.username in room.RoomInvite:
                    return True
                else:
                    return False
        return False

    def sendArbChat(self, senderClient, eventTokens, data, binary = None):
        for room in self.server.rooms.values():
            if binary:
                reactor.callLater(0, room.sendAllPvSpec, eventTokens, [10,8,6,5,4,3], data, True)
            else:
                reactor.callLater(0, room.sendAllPvSpec, eventTokens, [10,8,6,5,4,3], data)
            #for playerCode, client in room.clients.items():
            #    if client.privilegeLevel>=10 or client.privilegeLevel==6 or client.privilegeLevel==5 or client.privilegeLevel==3:
            #        if binary:
            #            client.sendData(eventTokens, data, True)

            #        else:
            #            client.sendData(eventTokens, data)
    def sendModChat(self, senderClient, eventTokens, data, binary = None):
        for room in self.server.rooms.values():
            if binary:
                reactor.callLater(0, room.sendAllPvSpec, eventTokens, [10,8,6,5], data, True)
            else:
                reactor.callLater(0, room.sendAllPvSpec, eventTokens, [10,8,6,5], data)
            #for playerCode, client in room.clients.items():
            #    if client.privilegeLevel>=10 or client.privilegeLevel==6 or client.privilegeLevel==5:
            #        if binary:
            #            client.sendData(eventTokens, data, True)
            #        else:
            #            client.sendData(eventTokens, data)
    def sendArbChatOthers(self, senderClient, eventTokens, data, binary = None):
        for room in self.server.rooms.values():
            if binary:
                reactor.callLater(0, room.sendAllPvSpecOthers, senderClient, eventTokens, [10,8,6,5,4,3], data, True)
            else:
                reactor.callLater(0, room.sendAllPvSpecOthers, senderClient, eventTokens, [10,8,6,5,4,3], data)
            #for playerCode, client in room.clients.items():
            #    if client.privilegeLevel>=10 or client.privilegeLevel==6 or client.privilegeLevel==5 or client.privilegeLevel==3:
            #        if client.playerCode != senderClient.playerCode:
            #            if binary:
            #                client.sendData(eventTokens, data, True)
            #            else:
            #                client.sendData(eventTokens, data)
    def sendModChatOthers(self, senderClient, eventTokens, data, binary = None):
        for room in self.server.rooms.values():
            if binary:
                reactor.callLater(0, room.sendAllPvSpecOthers, senderClient, eventTokens, [10,8,6,5], data, True)
            else:
                reactor.callLater(0, room.sendAllPvSpecOthers, senderClient, eventTokens, [10,8,6,5], data)
            #for playerCode, client in room.clients.items():
            #    if client.privilegeLevel>=10 or client.privilegeLevel==6 or client.privilegeLevel==5:
            #        if client.playerCode != senderClient.playerCode:
            #            if binary:
            #                client.sendData(eventTokens, data, True)
            #            else:
            #                client.sendData(eventTokens, data)
    def sendBotLogin(self, name):
        roomname = ""
        for room in self.server.rooms.values():
            for playerCode, client in room.clients.items():
                if client.username == name:
                    roomname = client.room.name
        for room in self.server.rooms.values():
            for playerCode, client in room.clients.items():
                if client.privilegeLevel>=3 and not client.isDrawer:
                    owner = self.server.getBotOwner(name)
                    client.sendData("\x1A\x06", ["-","[MB] %s (%s) : %s"%(name,owner,roomname)])
    def sendArbChatOthersLogin(self, senderClient, eventTokens, name):
        for room in self.server.rooms.values():
            for playerCode, client in room.clients.items():
                if not senderClient.isDrawer:
                    if client.privilegeLevel>=3 and not client.isDrawer:
                        #if client.playerCode != senderClient.playerCode:
                        sname="-"
                        if client.privilegeLevel==4:
                            message = name+" : "+room.name
                        else:
                            if client.Langue=="EN":
                                message = name+" подключился."
                            elif client.Langue=="BR":
                                message = name+" подключился."
                            elif client.Langue=="fr":
                                message = name+" подключился."
                            elif client.Langue=="RU":
                                message = name+" подключился."
                            elif client.Langue=="TR":
                                message = name+" подключился."
                            elif client.Langue=="CN":
                                message = name+" подключился."
                            else:
                                message = name+" подключился."
                        #data="\x02"+struct.pack('!h', len(sname))+sname+struct.pack('!h', len(message))+message+"\x00\x00"
                        #client.sendData(eventTokens, data, True)
                        client.sendData("\x1A\x06", [sname, message])
    def sendModChatOthersLogin(self, senderClient, eventTokens, name):
        for room in self.server.rooms.values():
            for playerCode, client in room.clients.items():
                if not TS:
                    if client.privilegeLevel>=5:
                        #if client.playerCode != senderClient.playerCode:
                        if senderClient.isDrawer and not TS:
                            sname="Drawer"
                        else:
                            sname="-"
                        if client.Langue=="BR":
                            message = name+" подключился."
                        elif client.Langue=="BR":
                            message = name+" подключился."
                        elif client.Langue=="fr":
                            message = name+" подключился."
                        elif client.Langue=="RU":
                            message = name+" подключился."
                        elif client.Langue=="TR":
                            message = name+" подключился."
                        elif client.Langue=="CN":
                            message = name+" подключился."
                        else:
                            message = name+" подключился."
                        client.sendData("\x1A\x05", [sname, message])
                else:
                    if client.privilegeLevel>=5 and not client.isDrawer:
                        #if client.playerCode != senderClient.playerCode:
                        if senderClient.isDrawer and not TS:
                            sname="Drawer"
                        else:
                            sname="-"
                        if client.Langue=="BR":
                            message = name+" подключился."
                        elif client.Langue=="BR":
                            message = name+" подключился."
                        elif client.Langue=="fr":
                            message = name+" подключился."
                        elif client.Langue=="RU":
                            message = name+" подключился."
                        elif client.Langue=="TR":
                            message = name+" подключился."
                        elif client.Langue=="CN":
                            message = name+" подключился."
                        else:
                            message = name+" подключился."
                        client.sendData("\x1A\x05", [sname, message])

                        #data="\x03"+struct.pack('!h', len(sname))+sname+struct.pack('!h', len(message))+message+"\x00\x00"
                        #client.sendData(eventTokens, data, True)
    def sendAllStaffInRoom(self, senderClient, eventTokens, data, binary = None):
        for playerCode, client in self.clients.items():
            if client.privilegeLevel>=3:
                if binary:
                    client.sendData(eventTokens, data, True)
                else:
                    client.sendData(eventTokens, data)
    def sendAllStaffInRoomVoteBan(self, senderClient, selfName, username, bancount):
        #voteban2
        player = self.getPlayer(selfName)
        if player == 0: return
        for playerCode, client in player.room.clients.items(): #self.clients.items():
            if client.privilegeLevel>=3:
                #client.sendData(eventTokens, data)
                if client.Langue=="BR":
                    client.sendData("\x06"+"\x14",[selfName+" отправил(а) заявку бана на "+username+" ("+str(bancount)+"/6)."])
                elif client.Langue=="fr":
                    client.sendData("\x06"+"\x14",[selfName+" отправил(а) заявку бана на "+username+" ("+str(bancount)+"/6)."])
                elif client.Langue=="BR":
                    client.sendData("\x06"+"\x14",[selfName+" отправил(а) заявку бана на "+username+" ("+str(bancount)+"/6)."])
                elif client.Langue=="RU":
                    client.sendData("\x06"+"\x14",[selfName+" отправил(а) заявку бана на "+username+" ("+str(bancount)+"/6)."])
                elif client.Langue=="TR":
                    client.sendData("\x06"+"\x14",[selfName+" отправил(а) заявку бана на "+username+" ("+str(bancount)+"/6)."])
                elif client.Langue=="CN":
                    client.sendData("\x06"+"\x14",[selfName+" отправил(а) заявку бана на "+username+" ("+str(bancount)+"/6)."])
                else:
                    client.sendData("\x06"+"\x14",[selfName+" отправил(а) заявку бана на "+username+" ("+str(bancount)+"/6)."])
					
#    def sendAskForHelper(self, senderClient, selfName, askmessage):
#        #voteban2
#        player = self.getPlayer(selfName)
#        if player == 0: return
#        for playerCode, client in player.room.clients.items(): #self.clients.items():
#            if client.privilegeLevel>=3:
#                #client.sendData(eventTokens, data)
#                if client.Langue=="BR":
#                    client.sendData("\x06"+"\x14",["<font color='#FFEE00'>[*]</font> "+selfName+" спрашивает "+askmessage])
#                elif client.Langue=="fr":
#                    client.sendData("\x06"+"\x14",["<font color='#FFEE00'>[*]</font> "+selfName+" спрашивает "+askmessage])
#                elif client.Langue=="BR":
#                    client.sendData("\x06"+"\x14",["<font color='#FFEE00'>[*]</font> "+selfName+" спрашивает "+askmessage])
#                elif client.Langue=="RU":
#                    client.sendData("\x06"+"\x14",["<font color='#FFEE00'>[*]</font> "+selfName+" спрашивает "+askmessage"])
#                elif client.Langue=="TR":
#                    client.sendData("\x06"+"\x14",["<font color='#FFEE00'>[*]</font> "+selfName+" спрашивает "+askmessage"])
#                elif client.Langue=="CN":
#                    client.sendData("\x06"+"\x14",["<font color='#FFEE00'>[*]</font> "+selfName+" спрашивает "+askmessage"])
#                else:
#                    client.sendData("\x06"+"\x14",["<font color='#FFEE00'>[*]</font> "+selfName+" спрашивает "+askmessage"])


    def getPlayer(self, name):
        for room in self.server.rooms.values():
            for playerCode, client in room.clients.items():
                if client.username == name:
                    return client
        return 0

    def getPlayerCode(self, name, OnlySelf = None):
        if OnlySelf:
            for playerCode, client in self.clients.items():
                if client.username == name:
                    return playerCode
                    break
            return 0
        else:
            for room in self.server.rooms.values():
                for playerCode, client in room.clients.items():
                    if client.username == name:
                        return playerCode
                        break
            return 0

    def getCurrentSync(self):
        if self.eSync:
            return "Everyone"
        elif self.sSync:
            for playerCode, client in self.clients.items():
                if client.playerCode == self.currentSyncroniserCode:
                    return client.username
                    break
        else:
            return "Nobody"
        return 0

    def killAfk(self):
        if self.isBootcamp:
            pass
        if self.isTribe:
            pass
        elif self.isEditeur:
            pass
        elif self.isTotemEditeur:
            pass
        else:
            if int((time.time()-self.gameStartTime)) > 32 or int((time.time()-self.gameStartTime)) < 29:
                logging.error('AFK kill timer invalid. Time: '+str(int((time.time()-self.gameStartTime))))
            else:
                for playerCode, client in self.clients.items():
                    if not client.isDead:
                        if client.isAfk == True:
                            client.isDead = True
                            client.score -= 1
                            if client.score < 0:
                                client.score = 0
                            client.sendPlayerDied(client.playerCode, client.score)
                            self.checkShouldChangeWorld()
                        else:
                            pass

    def closeRoomRoundJoin(self):
        self.isCurrentlyPlayingRoom = True

    def killAll(self):
        for playerCode, client in self.clients.items():
            if not client.isDead:
                resetpscore=client.score+1
                client.sendPlayerDied(client.playerCode, resetpscore)
                client.isDead=True
        self.checkShouldChangeWorld()

    def killAllNoDie(self):
        for playerCode, client in self.clients.items():
            if not client.isDead:
                client.isDead=True
        self.checkShouldChangeWorld()

    def killShaman(self):
        for playerCode, client in self.clients.items():
            if client.playerCode == self.currentShamanCode:
                client.score -= 1
                if client.score < 0:
                    client.score = 0
                client.sendPlayerDied(client.playerCode, client.score)
                client.isDead=True
        self.checkShouldChangeWorld()

    def getPlayerCount(self, UniqueIPs = None):
        if UniqueIPs:
            IPlist=[]
            for playerCode, client in self.clients.items():
                if not client.address[0] in IPlist:
                    IPlist.append(client.address[0])
            return len(IPlist)
        else:
            return len(self.clients)

    def getPlayerList(self, Noshop = None):
        if Noshop:
            for playerCode, client in self.clients.items():
                if client.isHidden:
                    pass
                else:
                    yield client.getPlayerData(True)
        else:
            for playerCode, client in self.clients.items():
                if client.isHidden:
                    pass
                else:
                    yield client.getPlayerData()

    def getHighestShaman(self):
        clientscores = []
        bots = ['Dubbot']
        clientcode = 0
        for playerCode, client in self.clients.items():
            clientscores.append(client.score)
        for playerCode, client in self.clients.items():
            if client.score==max(clientscores):
                clientcode=playerCode
                clientname=client.username
        return clientcode

    def getSecondHighestShaman(self):
        clientscores = []
        clientcode = 0
        for playerCode, client in self.clients.items():
            clientscores.append(client.score)
        clientscores.remove(max(clientscores))
        for playerCode, client in self.clients.items():
            if client.score==max(clientscores):
                clientcode=playerCode
                clientname=client.username
        return clientcode

    def getShamanCode(self):
        if self.forceNextShaman!=False:
            self.currentShamanCode=self.forceNextShaman
            self.forceNextShaman=False
            for playerCode, client in self.clients.items():
                if client.playerCode == self.currentShamanCode:
                    self.currentShamanName = client.username
            return self.currentShamanCode
        else:
            if self.currentShamanCode is None:
                if self.currentWorld in [7, 8, 14, 22, 23, 28, 29, 54, 55, 57, 58, 59, 60, 61, 70, 77, 78, 87, 88, 89, 92, 122, 123, 124, 125, 126, 1007, 888] + range(200,210+1):
                    self.currentShamanCode = 0
                elif self.SPR_Room and self.spc0:
                    self.currentShamanCode = 0
                elif self.nobodyIsShaman:
                    self.currentShamanCode = 0
                elif self.everybodyIsShaman:
                    self.currentShamanCode = 0
                else:
                    self.currentShamanCode = self.getHighestShaman()
            if self.currentShamanCode == 0:
                self.currentShamanName = None
            else:
                for playerCode, client in self.clients.items():
                    if client.playerCode == self.currentShamanCode:
                        self.currentShamanName = client.username
            return self.currentShamanCode

    def getDoubleShamanCode(self):
        if self.forceNextShaman!=False:
            self.currentShamanCode=self.forceNextShaman
            self.forceNextShaman=False
            if self.currentSecondShamanCode is None:
                self.currentSecondShamanCode = self.getSecondHighestShaman()
                while self.currentSecondShamanCode == self.currentShamanCode:
                    self.currentSecondShamanCode = random.choice(self.clients.keys())
            for playerCode, client in self.clients.items():
                if client.playerCode == self.currentShamanCode:
                    self.currentShamanName = client.username
            for playerCode, client in self.clients.items():
                if client.playerCode == self.currentSecondShamanCode:
                    self.currentSecondShamanName = client.username
            return [self.currentShamanCode, self.currentSecondShamanCode]
        else:
            if self.currentShamanCode is None:
                self.currentShamanCode = self.getHighestShaman()
            if self.currentSecondShamanCode is None:
                self.currentSecondShamanCode = self.getSecondHighestShaman()
                while self.currentSecondShamanCode == self.currentShamanCode:
                    self.currentSecondShamanCode = random.choice(self.clients.keys())
            for playerCode, client in self.clients.items():
                if client.playerCode == self.currentShamanCode:
                    self.currentShamanName = client.username
            for playerCode, client in self.clients.items():
                if client.playerCode == self.currentSecondShamanCode:
                    self.currentSecondShamanName = client.username
            return [self.currentShamanCode, self.currentSecondShamanCode]

    def getSyncroniserCode(self):
        if self.currentSyncroniserCode is None:
            self.currentSyncroniserCode = random.choice(self.clients.keys())
        return self.currentSyncroniserCode

if __name__ == "__main__":
    os.system('title Transformice Server '+VERSION)
    if not os.path.exists("Kikoo.swf"):
        os._exit(16)
    if int(os.stat("dbfile.sqlite")[6])==0:
        os._exit(17)

    #443, 44444, 44440, 5555, 3724, and 6112
    f = TransformiceServer()
    reactor.listenTCP(44444, f)
    reactor.listenTCP(44440, f)
    #reactor.listenTCP(5555, f)
    reactor.listenTCP(3724, f)
    reactor.listenTCP(6112, f)
    reactor.run()
'''
Cheese, Lefleur, Tiger, fr. 2012 (c) 
'''
