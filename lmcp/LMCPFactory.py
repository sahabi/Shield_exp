import struct
import LMCPObject
import xml.dom.minidom

import afrl.cmasi
import afrl.cmasi.perceive


HEADER_SIZE = 8  # don't modify this
CHECKSUM_SIZE = 4 # don't modify this
LMCP_CONTROL_STR = 0x4c4d4350

class LMCPFactory:
    def __init__(self):
        self.series_enums = {}
        from afrl.cmasi import SeriesEnum
        self.addSeries(SeriesEnum)
        from afrl.cmasi.perceive import SeriesEnum
        self.addSeries(SeriesEnum)


    def addSeries(self, series):
        if not series.SERIES_NAME_ID in self.series_enums.keys():
            self.series_enums[series.SERIES_NAME_ID] = series

    def getObject(self, buffer):
        #print len(buffer)
        if len(buffer) < HEADER_SIZE:
            print("getObject() : buffer too small for message")
            return None
        type_ = getLMCPType(buffer)
        series = getLMCPSeries(buffer)
        version = getLMCPVersion(buffer)
        obj = self.createObject(series, version, type_)
        if obj != None:
           obj.unpack(buffer, HEADER_SIZE + 15)
        return obj

    def getObjFromStream(self, fileobj):
        """
        reads an LMCP object from a file source, such as a socket (or file on the disk)
        """
        header = fileobj.read(HEADER_SIZE)
        msgSize = getSize(header)
        msgBody = fileobj.read(msgSize + CHECKSUM_SIZE)
        if  validate(header + msgBody) != True:
            print("LMCPFactory : bad checksum. ")
            return None
        return self.getObject(header + msgBody)

    def createObject(self, series_id, version, object_type):
        if series_id in self.series_enums.keys():
            series_enum = self.series_enums[series_id]

            if series_enum.SERIES_VERSION == version:
                return series_enum.SeriesEnum().getInstance(object_type)


        return None

    def createObjectByName(self, name):
        """
        Returns a new LMCP object based on its name
        """
        return None

    def unpackFromXMLNode(self, domNode):
        """
        Reads in an XML node, unpacks objects, adds them to a list and
        returns the list
        """
        objs = []
        for e in domNode.childNodes:
            if e.nodeType == xml.dom.Node.ELEMENT_NODE:
                obj = self.createObjectByName(e.localName)
                if obj != None:
                    obj.unpackFromXMLNode(e, self)
                    objs.append(obj)
        return objs

    def createObjectFromNode(self, xmlNode):
        return None

    def unpackFromXMLString(self, xmlStr):
        """
        Reads in an XML string, unpacks objects, adds them to a list and
        returns the list
        """
        doc = xml.dom.minidom.parseString(xmlStr)
        return self.unpackFromXMLNode(doc.documentElement)

    def unpackFromXMLFile(self, file):
        """
        Reads in an XML document, unpacks objects, adds them to a list and
        returns the list
        """
        doc = xml.dom.minidom.parse(file)
        return self.unpackFromXMLNode(doc.documentElement)

internalFactory = LMCPFactory()

def packMessage(lmcpObject, calcChecksum):
    """
    packs a buffer (string) object and returns it
    """

    if lmcpObject == None:
        return None
    # pack the header
    hdr_buffer = []
    obj_buffer = []
    cks_buffer = []
    total_buffer = []
    hdr_buffer.append(struct.pack(">I", LMCP_CONTROL_STR))
    obj_tmp = lmcpObject.pack()
    obj_buffer.append(struct.pack(">B", lmcpObject != None))
    obj_buffer.append(struct.pack(">q", lmcpObject.SERIES_NAME_ID))
    obj_buffer.append(struct.pack(">I", lmcpObject.LMCP_TYPE))
    obj_buffer.append(struct.pack(">H", lmcpObject.SERIES_VERSION))
    obj_buffer.append(obj_tmp)
    hdr_buffer.append(struct.pack(">I", len("".join(obj_buffer))))
    total_buffer.extend(hdr_buffer)
    total_buffer.extend(obj_buffer)

    #pack the checksum
    if calcChecksum:
        total_buffer.append(struct.pack(">I", calculateChecksum("".join(total_buffer), 0)))
    else:
        total_buffer.append(struct.pack(">I", 0))

    return "".join(total_buffer)

def getSize(buffer):
    return struct.unpack_from(">I", buffer, 4)[0]

def getLMCPValidObject(buffer):
    return struct.unpack_from(">B", buffer, 8)[0]

def getLMCPSeries(buffer):
    return struct.unpack_from(">q", buffer, 9)[0]

def getLMCPType(buffer):
    return struct.unpack_from(">I", buffer, 17)[0]

def getLMCPVersion(buffer):
    return struct.unpack_from(">H", buffer, 21)[0]

def calculateChecksum(buffer, offset):
    """
    Calculates the checksum.  This should be called after pack().
    The checksum sums all bytes in the packet between 0 and
    buf.limit() - CHECKSUM_SIZE.
    """
    sum = 0
    for x in range(len(buffer)-offset):
        sum += struct.unpack_from("b", buffer, x)[0] & 0xFF
    return sum

def validate(buffer):
    """
    checks the bytebuffer's checksum value against the calculated checksum
    returns true if the calculated and stored values match, or if the buffer value is
    zero (indicating that checksum was not calculated.  This method rewinds the buffer and
    returns it to LIMIT - 4 bytes (start position of checksum)
    """
    cs = struct.unpack_from(">I", buffer, len(buffer)-5)[0]
    if cs == 0:
        return True
    else:
        return cs == calculateChecksum(buffer, 5)


