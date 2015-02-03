# -*- coding: utf-8 -*-
"""
/***************************************************************************
 sig40
                                 A QGIS plugin
 sig40
                             -------------------
        begin                : 2014-07-28
        copyright            : (C) 2014 by pierre foicik
        email                : pierre.foicik@gmail.com
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
    """Load sig40 class from file sig40.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .sig40 import sig40
    return sig40(iface)
