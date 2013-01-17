#-------------------------------------------------------------------------------
# Created:     22/04/2011
# Copyright:   (c) Admin 2011
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import struct

def main():
##"NPC"
##[Number of NPCs (long)]
##[pad byte]
##[ID in file (long)]
##[Type (bool)]
##[ExVars (bool)]
##[Id (short)]
##[UTF len (short)]
##[Name UTF]
##[UTF len (short)]
##[ShopItems UTF]
##[X (short)]
##[Y (short)]
##[Direction (!b)]
##[Clickable (!b)]
##
##If Type is True (Room):
##[UTF len (short)]
##[Roomname UTF]
##
##If Type is False (Map):
##[Map (short)]
##
##If ExVars is False:
##End
##
##If ExVars is True:
##[Number (short)]
##[EventTokens len (short)]
##[EventTokens UTF]
##[Data len (short)]
##[Data UTF]

#        self.sendData("\x15" + "\x15", ["0", "Jingle", "21,0,3,4,3", "600", "335", "0", "0"])
#        if self.room.name=="801":
#            self.sendData("\x15" + "\x15", ["-1", "Papaille", "2,0,2,2,0", "400", "335", "0", "1"])
#            self.sendData("\x15" + "\x15", ["-2", "Elise", "10,0,1,0,1", "330", "335", "1", "0"])
#        if self.room.name=="ranking":
#            self.sendData("\x15" + "\x15", ["-1", "Hoste", "0,9,6,0,5", "93", "363", "1", "0"])
#            self.sendData("\x15" + "\x15", ["-2", "Brunodd", "0,0,0,0,6", "488", "175", "1", "0"])
#            self.sendData("\x15" + "\x15", ["-3", "Pride", "0,0,9,0,0", "581", "375", "0", "0"])
#        if self.room.name=="mod":
#            self.sendData("\x15" + "\x15", ["-1", "Modmj", "40,0,0,6,2", "93", "363", "1", "0"])
#            self.sendData("\x15" + "\x15", ["-2", "Sword", "47,0,9,4,2", "488", "175", "1", "0"])
#            self.sendData("\x15" + "\x15", ["-3", "Lorenzo", "0,8,0,0,5", "581", "375", "0", "0"])
#            self.sendData("\x15" + "\x15", ["-4", "Loved", "13,0,0,0,0", "330", "335", "1", "0"])
#            self.sendData("\x08" + "\x28", "\xFF\xFF\xFF\xFD", True)
#16 NPCs
        data="NPC"
        data=data+struct.pack("!h", 15)+"\x00"
        data=data+struct.pack("!l??hh", 1, False, False, 0, len("Rio"))+"Rio"+struct.pack("!h", len("1;87,14,0,0,0"))+"2;87,14,0,0,0"+struct.pack("!hhbb", 600, 335, 0, 0)+struct.pack("!h", 555)
        data=data+struct.pack("!l??hh", 2, False, False, 1, len("Pecheur"))+"Pecheur"+struct.pack("!h", len("1;62,5,0,4,0"))+"3;62,5,0,4,0"+struct.pack("!hhbb", 600, 335, 0, 0)+struct.pack("!h", 777)
        
        data=data+struct.pack("!l??hh", 3, True, False, -1, len("Papaille"))+"Papaille"+struct.pack("!h", len("2;2,0,2,2,0"))+"2;2,0,2,2,0"+struct.pack("!hhbb", 400, 335, 0, 1)+struct.pack("!h", len("*801"))+"*801"
        data=data+struct.pack("!l??hh", 4, True, False, -2, len("Elise"))+"Elise"+struct.pack("!h", len("3;10,0,1,0,1"))+"3;10,0,1,0,1"+struct.pack("!hhbb", 330, 335, 1, 0)+struct.pack("!h", len("*801"))+"*801"
        
        data=data+struct.pack("!l??hh", 5, True, False, -1, len("Kika"))+"Kika"+struct.pack("!h", len("2;61,1,0,0,5"))+"2;61,1,0,0,5"+struct.pack("!hhbb", 400, 335, 0, 0)+struct.pack("!h", len("*admin"))+"*admin"
        data=data+struct.pack("!l??hh", 6, True, False, -2, len("Shines"))+"Shines"+struct.pack("!h", len("2;63,11,7,7,0"))+"1;63,11,7,7,0"+struct.pack("!hhbb", 330, 335, 1, 0)+struct.pack("!h", len("*admin"))+"*admin"
        
        data=data+struct.pack("!l??hh", 7, True, False, -1, len("Kim"))+"Kim"+struct.pack("!h", len("1;65,0,1,0,4"))+"1;65,0,1,0,4"+struct.pack("!hhbb", 330, 335, 1, 0)+struct.pack("!h", len("*modo"))+"*modo"
        data=data+struct.pack("!l??hh", 8, True, False, -2, len("Woop"))+"Woop"+struct.pack("!h", len("1;66,8,0,0,5"))+"1;66,8,0,0,5"+struct.pack("!hhbb", 210, 335, 0, 0)+struct.pack("!h", len("*modo"))+"*modo"
        data=data+struct.pack("!l??hh", 9, True, False, -3, len("Happy"))+"Happy"+struct.pack("!h", len("1;12,5,0,0,0"))+"1;12,5,0,0,0"+struct.pack("!hhbb", 416, 335, 0, 0)+struct.pack("!h", len("*modo"))+"*modo"
        data=data+struct.pack("!l??hh", 10, True, False, -4, len("Stow"))+"Stow"+struct.pack("!h", len("1;0,0,0,0,5"))+"1;0,0,0,0,5"+struct.pack("!hhbb", 574, 335, 0, 0)+struct.pack("!h", len("*modo"))+"*modo"
        data=data+struct.pack("!l??hh", 11, True, False, -5, len("Kika"))+"Kika"+struct.pack("!h", len("2;61,1,0,0,5"))+"2;61,1,0,0,5"+struct.pack("!hhbb", 510, 150, 0, 2)+struct.pack("!h", len("*modo"))+"*modo"
        data=data+struct.pack("!l??hh", 12, True, False, -6, len("Shines"))+"Shines"+struct.pack("!h", len("1;63,11,7,7,0"))+"1;63,11,7,7,0"+struct.pack("!hhbb", 574, 150, 1, 0)+struct.pack("!h", len("*modo"))+"*modo"
        data=data+struct.pack("!l??hh", 13, True, False, -7, len("Baffbot"))+"Baffbot"+struct.pack("!h", len("1;35,0,0,5,0"))+"1;35,0,0,5,0"+struct.pack("!hhbb", 154, 335, 1, 0)+struct.pack("!h", len("*modo"))+"*modo"
        data=data+struct.pack("!l??hh", 14, True, False, -1, len("Kika"))+"Kika"+struct.pack("!h", len("1;72,0,0,5,0"))+"1;72,0,0,5,0"+struct.pack("!hhbb", 330, 335, 1, 1)+struct.pack("!h", len("*kika"))+"*kika"
        data=data+struct.pack("!l??hh", 15, True, False, -2, len("Shines"))+"Shines"+struct.pack("!h", len("1;46,0,5,5,0"))+"1;46,0,5,5,0"+struct.pack("!hhbb", 400, 335, 0, 1)+struct.pack("!h", len("*kika"))+"*kika"
		
        f=open('npc.dat', 'wb')
        f.write(data)
        f.close()

if __name__ == '__main__':
    main()
