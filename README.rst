

==============================
ZenPacks.Darkemon.ZenCustomMap
==============================

.. contents::
   :depth: 3

This project is a Zenoss_ extension (ZenPack) that provides user definable maps and submaps of nodes.  The user can define and configure the maps, including custom background images and icons for different nodes and their positions.  Nodes and submaps can be linked with edges.

The greatest alarm severity is propagated up through any submaps.


Requirements & Dependencies
---------------------------
This ZenPack is known to be compatible with Zenoss versions 3.2 through 4.0.
Requires Flash Player version 10 or higher.


Installation
------------
You must first have, or install, Zenoss 3.2 or later. Tested with 3.2 and 4.1. You can download the free Core version of Zenoss from
http://community.zenoss.org/community/download .


Normal Installation (packaged egg)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Download the `Latest Package`_


Then copy it to your Zenoss server.  If there is a problem installing try removing "-py2.7" from the egg title and then run the following commands as the zenoss
user::

    zenpack --install <package.egg>
    zenoss restart


Developer Installation (link mode)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you wish to further develop and possibly contribute back you should clone
the git repository, then install the ZenPack in developer mode using the
following commands::

    git clone git://github.com/Darkemon/ZenPacks.Darkemon.ZenCustomMap
    zenpack --link --install ZenPacks.Darkemon.ZenCustomMap
    zenoss restart

See the `Zenpack Development Process`_

The sources of the Flash part are here http://code.google.com/p/zen-custom-map/


Screenshots
-----------
|Map 1|

.. _Zenoss: http://community.zenoss.org

.. _Latest Package: https://github.com/downloads/Darkemon/ZenPacks.Darkemon.ZenCustomMap/ZenPacks.Darkemon.ZenCustomMap-3.0-py2.7.egg

.. _Zenpack Development Process: http://community.zenoss.org/docs/DOC-8495

.. |Map 1| image:: https://github.com/Darkemon/ZenPacks.Darkemon.ZenCustomMap/raw/master/screenshots/common_view.png



