################################################################################
#
# Custom map for a Zenoss monitoring system.
# Copyright (C) 2011 Krasotin Artem
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
################################################################################

import os
import logging
import Globals
import xml.etree.ElementTree as etree
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ZenUtils.Utils import zenPath

_log = logging.getLogger('zen.ZenCustomMap')
_resDir = os.path.join(os.path.dirname(__file__), 'resources')

class ZenCustomMap(BrowserView):
    __call__ = ViewPageTemplateFile('./skins/ZenPacks.Darkemon.ZenCustomMap/viewZenCustomMap.pt')


class ZenCustomMapData(BrowserView):

    # Set a log file.
    import logging.handlers
    logFilename = zenPath('log', 'zenCustomMap.log')
    maxBytes = 10 * 1024
    backupCount = 3
    handler = logging.handlers.RotatingFileHandler(
        logFilename, maxBytes=maxBytes, backupCount=backupCount)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s","%Y-%m-%d %H:%M:%S"))
    _log.addHandler(handler)

    def __call__(self):
        action = self.request.form['action']

        if action == "get_config":

            mapId = self.request.form['map_id']
            self.request.response.write(self._getConfig("map",mapId))

        elif action == "get_mainconfig":

            self.request.response.write(self._getConfig("main"))

        elif action == "save_config":

            config = self.request.form['config']
            mapId = self.request.form['map_id']
            self.request.response.write(self._saveConfig("map",config,mapId))

        elif action == "save_mainconfig":

            config = self.request.form['config']
            self.request.response.write(self._saveConfig("main",config))

        elif action == "delete_map":

            mapId = self.request.form['map_id']
            self.request.response.write(self._deleteMap(mapId))

        elif action == "upload_background":

            image = self.request.form['Filedata']
            filename = self.request.form['filename']
            self._uploadImage("background", image, filename)

        elif action == "download_background":

            filename = self.request.form['filename']
            self.request.response.write(
                self._downloadImage("background", filename))

        elif action == "delete_background":

            filename = self.request.form['filename']
            self.request.response.write(
                self._deleteImage("background", filename))

        elif action == "upload_nodeimage":

            image = self.request.form['Filedata']
            filename = self.request.form['Filename']
            self._uploadImage("node",image,filename)

        elif action == "download_nodeimage":

            try:
                filename = self.request.form['filename']
            except:
                filename = None
            self.request.response.write(self._downloadImage("node", filename))

        elif action == "delete_nodeimage":

            filename = self.request.form['filename']
            self.request.response.write(self._deleteImage("node",filename))

        elif action == "get_devicelist":

            self.request.response.write(self._getDeviceList())

        elif action == "get_devicesevents":

            deviceList = self.request.form['devicelist']
            self.request.response.write(self._getDevicesEvents(deviceList))

        elif action == "get_testdata":

            self.request.response.write(self._getTestData())

    ##
    # Return map config.
    # If config map is not exist, then return default config
    # map with specified 'mapId'.
    #
    def _getConfig(self, confType, mapId=-1):
        if confType == "main":
            confPath = _resDir + "/xml/zenmap.xml"
        elif confType == "map":
            confPath = _resDir + "/xml/map"+str(mapId)+".xml"

        output = ""
        try:
            f = open(confPath, 'r')
            for line in f: output = output + line
            f.close()
        except:
            if confType == "map": return self._defaultMap(mapId)

        return output

    ##
    # Save on server map config.
    #
    def _saveConfig(self, confType, config, mapId=-1):
        if confType == "main":
            confPath = _resDir + "/xml/zenmap.xml"
        elif confType == "map":
            confPath = _resDir + "/xml/map"+mapId+".xml"

        try:
            os.remove(confPath)
        except:
            pass
        try:
            f = open(confPath, 'w')
            f.writelines(config)
            f.close()
            result = "1"
        except:
            result = "0"
        return result

    ##
    # Delete map config and his background.
    #
    def _deleteMap(self, mapId):
        confPath = _resDir + "/xml/map"+mapId+".xml"
        imgPath = _resDir + "/img/backgrounds/background"+str(mapId)+".img"
        try: os.remove(confPath)
        except: pass

        try: os.remove(imgPath)
        except: pass
        return ""

    ##
    # Return list of all devices.
    #
    def _getDeviceList(self):
        devices = self.context.zport.dmd.Devices.getSubDevices()

        data = {}
        for dev in devices:
            if data.has_key(dev.getDeviceClassPath()):
                devList = data[dev.getDeviceClassPath()]
            else:
                devList = []
            devData = {}
            devData['name'] = dev.name()
            devData['ip'] = dev.getManageIp()
            devList.append(devData)
            data[dev.getDeviceClassPath()] = devList


        root = etree.Element("classes")
        for k,v in data.items():
            devClass = etree.Element("class")
            devClass.set("path", k)
            for dev in v:
                devName = etree.Element("device")
                devName.text = dev['name']
                devName.set("ip", dev['ip'])
                devClass.append(devName)
            root.append(devClass)
        return etree.tostring(root)

    ##
    # Save image on server.
    #
    def _uploadImage(self, imgType, image, filename):
        if imgType == "background":
            imgPath = _resDir + "/img/backgrounds/"+filename
        elif imgType == "node":
            imgPath = _resDir + "/img/nodes/"+filename

        try:
            os.remove(imgPath)
        except:
            pass
        f = open(imgPath, 'w')
        f.writelines(image)
        f.close()
        return ""

    ##
    # Return image.
    #
    def _downloadImage(self, imgType, filename):
        """ Return the image.
            If imgType is 'node', then if filename not specified,
            return list of all name images.
        """

        if imgType == "background":
            imgPath = _resDir + "/img/backgrounds/"+filename
        elif imgType == "node":
            imgPath = _resDir + "/img/nodes/"

            if filename is None:
                root = etree.Element("images")
                for fname in os.listdir(imgPath):
                    imageNode = etree.Element("image")
                    imageNode.text = fname
                    root.append(imageNode)
                return etree.tostring(root)
            else: imgPath += filename

        image = ""
        try:
            f = open(imgPath, 'r')
            for line in f: image = image + line
            f.close()
        except:
            pass
        return image

    ##
    # Delete image from server.
    #
    def _deleteImage(self, imgType, filename):
        if imgType == "background":
            imgPath = _resDir + "/img/backgrounds/"+filename
        elif imgType == "node":
            imgPath = _resDir + "/img/nodes/"+filename

        try:
            os.remove(imgPath)
        except:
            pass
        return ""

    ##
    # Return events severity for specified devices.
    #
    def _getDevicesEvents(self, deviceList):

        def addElementToXML(xmlRoot, nodeId, sev, msg="", ip=None):
            if not ip is None:
                if self.context.zport.dmd.Devices.findDevice(ip) is None:
                    sev = 5
                    msg = "Device not found!"
            dev = etree.Element("device")
            dev.set("id", str(nodeId))
            dev.set("severity", str(sev))
            dev.text = str(msg)
            xmlRoot.append(dev)

        def getMaxEventSeverity(dev):
            maxSeverity = 0

            # if device
            if type(dev) == type(""):
                checkExistDevice(dev)
                eventsList = self.context.zport.dmd.ZenEventManager.\
                        getEventList(where="ipAddress='"+dev+"'")

                for e in eventsList:
                    if e.severity >= 3 and e.severity > maxSeverity:
                        maxSeverity = e.severity
                return maxSeverity

            # if list of devices
            if type(dev) == type({}):
                for devId, devIp in devList.items():
                    if self.context.zport.dmd.Devices.findDevice(devIp) is None:
                        return 5
                    else:
                        sev = getMaxEventSeverity(devIp)
                        if sev >= 3 and sev > maxSeverity:
                            maxSeverity = sev
                return maxSeverity

        def checkExistDevice(ip):
            r = self.context.zport.dmd.Devices.findDevice(ip)
            if r is None: return False
            else: True

        #
        # Main block.
        #
        try:    xml = etree.fromstring(deviceList)
        except: _log.error(str(deviceList))

        root = etree.Element("devices_events")
        for dev in xml:
            if dev.get("type") == "submap":
                devList = self._getMapsDevices(dev.text)
                if devList is None:
                    addElementToXML(root, dev.get("id"), 5, "Map not found!")
                else:
                    addElementToXML(root, dev.get("id"), getMaxEventSeverity(devList), "")
            else:
                addElementToXML(root, dev.get("id"), getMaxEventSeverity(dev.text), "", dev.text)

        return etree.tostring(root)

    ##
    # Create default map config.
    #
    def _defaultMap(self, mapId):
        root = etree.Element("map")

        child = etree.Element("uid") # Add 'map' child.
        child.text = str(mapId)
        root.append(child)

        child = etree.Element("x") # Add 'x' child.
        child.text = "0"
        root.append(child)

        child = etree.Element("y") # Add 'y' child.
        child.text = "0"
        root.append(child)

        child = etree.Element("zoom_index") # Add 'zoom_index' child.
        child.text = "3"
        root.append(child)

        child = etree.Element("line_width") # Add 'line_width' child.
        child.text = "1"
        root.append(child)

        child = etree.Element("line_color") # Add 'line_color' child.
        child.text = "0"
        root.append(child)

        child = etree.Element("refresh") # Add 'refresh' child.
        child.text = "300"
        root.append(child)

        child = etree.Element("back_image") # Add 'back_image' child.
        child.text = "false"
        root.append(child)

        child = etree.Element("nodes") # Add 'nodes' child.
        root.append(child)

        child = etree.Element("edges") # Add 'edges' child.
        root.append(child)

        return etree.tostring(root)

    ##
    # Get devices list of the map.
    # Type of devices is 'node' only.
    #
    def _getMapsDevices(self, mapId):
        # Check map.
        xmlMainConf = self._getConfig("main")
        xml = etree.fromstring(xmlMainConf)
        maps = xml.find("maps")
        mapExist = False
        for m in maps:
            uid = m.get("uid")
            if uid == mapId: mapExist = True
        if not mapExist: return None

        # Get device list.
        xmlMapConf = self._getConfig("map", mapId)
        xml = etree.fromstring(xmlMapConf)

        result = {}
        nodes = xml.find("nodes")
        for node in nodes:
            if node.find("type").text == "node":
                nodeId = node.get("id")
                nodeIp = node.find("ip").text
                result[nodeId] = nodeIp

        return result

    ##
    # For testing.
    #
    def _getTestData(self):
        return "1"
