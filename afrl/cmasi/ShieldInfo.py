#! /usr/bin/python

import struct
from lmcp import LMCPObject
#import xml.dom.minidom

#from lmcp import *
from afrl.cmasi import KeyValuePair


class ShieldInfo(LMCPObject.LMCPObject):

    def __init__(self):

        self.LMCP_TYPE = 63
        self.SERIES_NAME = "CMASI"
        #Series Name turned into a long for quick comparisons.
        self.SERIES_NAME_ID = 4849604199710720000
        self.SERIES_VERSION = 3

        #Define message fields
        self.UAVID = 0   #int64
        self.Label = ""   #string


    def pack(self):
        """
        Packs the object data and returns a string that contains all of the serialized
        members.
        """
        buffer = []
        buffer.extend(LMCPObject.LMCPObject.pack(self))
        buffer.append(struct.pack(">l", self.UAVID))   # changed from l to q
        buffer.append(struct.pack(">H", len(self.Label) ))
        if len(self.Label) > 0:
            buffer.append(struct.pack( `len(self.Label)` + "s", self.Label))

        return "".join(buffer)

    def unpack(self, buffer, _pos):
        """
        Unpacks data from a string buffer and sets class members
        """
        _pos = LMCPObject.LMCPObject.unpack(self, buffer, _pos)
        self.UAVID = struct.unpack_from(">q", buffer, _pos)[0] # changed from l to q
        _pos += 8
        _strlen = struct.unpack_from(">H", buffer, _pos )[0]
        _pos += 2
        if _strlen > 0:
            self.Label = struct.unpack_from( `_strlen` + "s", buffer, _pos )[0]
            _pos += _strlen
        else:
             self.Label = ""

        return _pos

    def get_UAVID(self):
        return self.UAVID

    def set_UAVID(self, value):
        self.UAVID = int( value )

    def get_Label(self):
        return self.Label


    def set_Label(self, value):
        self.Label = str( value )

    def toString(self):
        """
        Returns a string representation of all variables
        """
        buf = LMCPObject.LMCPObject.toString(self)
        buf += "From ShieldInfo:\n"
        buf +=    "UAVID = " + str( self.UAVID ) + "\n" 
        buf +=    "Label = " + str( self.Label ) + "\n" 

        return buf;

    def getLMCPType(self):
        return self.LMCP_TYPE

    def getSeriesName(self):
        return self.SERIES_NAME

    def getSeriesNameID(self):
        return self.SERIES_NAME_ID

    def getSeriesVersion(self):
        return self.SERIES_VERSION

    def toXMLStr(self, ws):
        str = ws + "<ShieldInfo>\n";
        #str +=LMCPObject.LMCPObject.toXMLMembersStr(self, ws + "  ")
        str += self.toXMLMembersStr(ws + "  ")
        str += ws + "</ShieldInfo>\n";
        return str

    def toXMLMembersStr(self, ws):
        buf = ""
        buf += LMCPObject.LMCPObject.toXMLMembersStr(self, ws)
        buf += ws + "<UAVID>" + str(self.UAVID) + "</UAVID>\n"
        buf += ws + "<Label>" + str(self.Label) + "</Label>\n"

        return buf
        
