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

# Modified for Zenoss V4 and to recurse submaps more fully to propagate the event severity.
# Use of ip filed changed to be the path of the device to allow for IP address changes, either manual or DHCP.
# The us of 'ip' as the name for the id and in the xml files and for the flash plugin should be changed 
# to avoid confusion, but do not have the facilities to edit the flash plugin.  'ip' should be changed to
# 'primaryId'.
# R. Martin June 2011.

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
    maxBytes = 1024 * 1024
    backupCount = 3
    handler = logging.handlers.RotatingFileHandler(
        logFilename, maxBytes=maxBytes, backupCount=backupCount)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s","%Y-%m-%d %H:%M:%S"))
    _log.addHandler(handler)

    def __call__(self):
        action = self.request.form['action']
        #_log.info('Action: ' + action)
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
            events = self._getMapsEvents(deviceList)
            self.request.response.write(events)

        elif action == "get_testdata":

            self.request.response.write(self._getTestData())


    ##
    # Return map config.
    # If config map does not exist, then return default config
    # map with specified 'mapId'.
    #    
    def _getConfig(self, confType, mapId=-1):
        if confType == "main":
            confPath = os.path.join(_resDir, "xml", "zenmap.xml")
        elif confType == "map":
            confPath = os.path.join(_resDir, "xml", "map"+str(mapId)+".xml")
        try:
            tree = etree.parse(confPath)
        except IOError:
            if confType == "map": 
                return self._defaultMap(mapId)
        # Update the name from Zenoss for each node
        nodes = tree.find('nodes')
        if not nodes is None:
            for node in nodes: # iterfind is not available before 2.7
                if node.tag == 'node': # node in the sense of it being a device.
                    n = node.find('ip')
                    if not n is None:
                        primaryId = n.text
                        if primaryId:
                            try:
                                dev = self.context.zport.dmd.Devices.getObjByPath(primaryId)
                                name = dev.name()
                                nameTag = node.find('name')
                                nameTag.text = name
                            except:
                                pass
        return etree.tostring(tree.getroot())
        

    ##
    # Save on server map config.
    #
    def _saveConfig(self, confType, config, mapId=-1):
        if confType == "main":
            confPath = os.path.join(_resDir, "xml", "zenmap.xml")
        elif confType == "map":
            confPath = os.path.join(_resDir, "xml", "map"+str(mapId)+".xml")

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
        confPath = os.path.join(_resDir,"xml" , "map"+str(mapId)+".xml")
        imgPath =  os.path.join(_resDir, "img/backgrounds" , "background"+str(mapId)+".xml")        
        try: 
            os.remove(confPath)
        except:
            pass
        try:
            os.remove(imgPath)
        except:
            pass
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
            devData['primaryId'] = dev.getPrimaryId()
            devList.append(devData)
            data[dev.getDeviceClassPath()] = devList

        root = etree.Element("classes")
        for k,v in data.items():
            devClass = etree.Element("class")
            devClass.set("path", k)
            for dev in v:
                devName = etree.Element("device")
                devName.text = dev['name']
                # TODO Change 'ip' to primaryID when flash is changed
                devName.set("ip", dev['primaryId'])
                devClass.append(devName)
            root.append(devClass)
        return etree.tostring(root)

    ##
    # Save image on server.
    #
    def _uploadImage(self, imgType, image, filename):
        if imgType == "background":
            imgPath = os.path.join(_resDir, "img/backgrounds", filename)
        elif imgType == "node":
            imgPath = os.path.join(_resDir,"img/nodes", filename)
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
            imgPath = os.path.join(_resDir, "img/backgrounds", filename)
        elif imgType == "node":
            imgPath = os.path.join(_resDir,"img/nodes")
            if filename is None:
                root = etree.Element("images")
                for fname in os.listdir(imgPath):
                    imageNode = etree.Element("image")
                    imageNode.text = fname
                    root.append(imageNode)
                return etree.tostring(root)
            else:
                imgPath = os.path.join(imgPath, filename)
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
            imgPath = os.path.join(_resDir, "img/backgrounds", filename)
        elif imgType == "node":
            imgPath = os.path.join(_resDir,"img/nodes", filename)
        try:
            os.remove(imgPath)
        except:
            pass
        return ""
        
    
    ##
    # Return events for map, including submaps
    # Recurses as necessary
    #
    def _getMapsEvents(self, devList):
        # Go through the entries, and if a submap entry, recurse
        eventsEtree = etree.Element("devices_events")
        
        def addElementToXML(xmlRoot, nodeId, sev, msg="", primaryId=None):
            if primaryId:
                try:
                    self.context.zport.dmd.Devices.getObjByPath(primaryId)
                except NotFound as e:
                    sev = 5
                    msg = "Device not found!"
                    _log.error('_getMapsEvents did not find ' + primaryId)
            dev = etree.Element("device")
            dev.set("id", str(nodeId))
            dev.set("severity", str(sev))
            dev.text = str(msg)
            xmlRoot.append(dev)
        
        def getMaxEventSeverity(primaryId):
            maxSeverity = 5
            try:
                dev = self.context.zport.dmd.Devices.getObjByPath(primaryId)
            except NotFound:
                return maxSeverity
            # This is not available in Zenoss 3.  Works in 4.
            #maxSeverity = dev.getWorstEventSeverity()
            eventsSummary = dev.getEventSummary()
            for e in eventsSummary:
                severity, acked, count = e
                if count > 0:
                    break;
                else:
                    maxSeverity -= 1
            return maxSeverity
        
        # Protect against infinite recursion
        visitedMapIds = set()
        def getSubmap(mapId):
            if mapId in visitedMapIds:
                # Already been here and will have the worsecase of itself and its descendants
                return(0)
            visitedMapIds.add(mapId)
            xmlMapConf = self._getConfig("map", mapId)
            xml = etree.fromstring(xmlMapConf)
            maxSeverity = 0
            nodes = xml.find("nodes")
            if not nodes:
                return 0 # No nodes so OK, or should it be Maximum severity - or should it be a warning?            
            for node in nodes:
                if node.find("type").text == "node":
                    # TODO 'ip' needs to be changed to 'primaryId' when flash is changed.
                    nodePrimaryId = node.find("ip").text
                    severity = getMaxEventSeverity(nodePrimaryId)
                    maxSeverity = max(maxSeverity, severity)
                # recursive call for submaps
                if node.find("type").text == "submap":
                    submap_uid = node.find("submap_uid").text
                    severity = getSubmap(submap_uid)
                    maxSeverity = max(maxSeverity, severity)                    
            return maxSeverity
        
        try:    deviceEtree = etree.fromstring(devList)
        except: _log.error(str(devList))
          
        for dev in deviceEtree:
            devId = dev.get("id")
            if dev.get("type") == "submap":
                mapId = str(dev.text)
                severity = getSubmap(mapId)
                addElementToXML(eventsEtree, devId, severity, "")
            elif dev.get("type") == "node":
                # dev.text use to contain the ip address, now the primaryId
                maxSeverity = getMaxEventSeverity(dev.text)
                addElementToXML(eventsEtree, devId, maxSeverity, "")
            else:
                _log.error('Node type is not known: ' + str(dev.get("type")))
                
        return etree.tostring(eventsEtree)


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
        child.text = "30"
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
    # For testing.
    #
    def _getTestData(self):
        return "1"
