#-------------------------------------------------------------------------------
# Created:     01/05/2011
# Copyright:   (c) Admin 2011
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import struct

def main():
##"SPR"
##long  Number of rooms
##\x00  Pad Byte
##
##long  ID
##shrt  UTF length
##UTF   Name
##bool            self.countStats = False
##bool            self.specificMap = True
##bool            self.isSandbox = True
##bool	custommap
##int             self.currentWorld = "0"
##bool            self.autoRespawn = True
##int             self.roundTime = 0
##bool            self.never20secTimer = True
##bool	everyone is sync
##bool  send sync
##bool	sendnewplayer
##shrt  sendNewPlayerType #UNUSED
##bool	shamancode is 0

    data="SPR"
    data=data+struct.pack("!h", 5)+"\x00"
    #                         ul               ID  ul  name  stats   spcm sndbx iscm   map atr tme n20s  eSync  sSync  sNP    sT  sc0
    data=data+struct.pack("!lh3s????i?i????h?", 1, 3, "801", False, True, True, False, 0, True, 0, True, False, False, False, 0, True)
    data=data+struct.pack("!lh3s????i?i????h?", 2, 3, "mod", False, True, True, False, 801, True, 0, True, False, False, True, 0, True)
    data=data+struct.pack("!lh7s????i?i????h?", 3, 7, "ranking", False, True, False, True, 801, True, 0, True, False, True, False, 0, True)
    data=data+struct.pack("!lh3s????i?i????h?", 4, 3, "804", False, True, True, True, 121, True, 0, True, True, False, False, 0, True)
    data=data+struct.pack("!lh3s????i?i????h?", 5, 3, "805", False, True, True, True, 149, True, 0, True, True, False, False, 0, True)

    f=open('spr.dat', 'wb')
    f.write(data)
    f.close()

if __name__ == '__main__':
    main()
                                                                                                                                          