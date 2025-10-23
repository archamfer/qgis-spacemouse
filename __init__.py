# -*- coding: utf-8 -*-
"""
SpaceMouse Navigation Plugin for QGIS
"""

def classFactory(iface):
    """Load SpaceMousePlugin class from file spacemouse_plugin.
    
    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .spacemouse_plugin import SpaceMousePlugin
    return SpaceMousePlugin(iface)
