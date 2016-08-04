# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ZRisk
                                 A QGIS plugin
 ZRisk plugin za procenu zemljotresnog rizika zgrada
                             -------------------
        begin                : 2016-08-02
        copyright            : (C) 2016 by Dejan Dragojević, Nemanja Paunić 
        email                : paunicnemanja@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ZRisk class from file ZRisk.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .z_risk import ZRisk
    return ZRisk(iface)
