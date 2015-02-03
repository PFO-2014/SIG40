
# -*- coding: utf-8 -*-

'''
Created on 24 juil. 2014

@author: pierre
'''

from __builtin__ import list
from qgis.core import QgsRectangle, QgsPoint, QgsGeometry
from qgis.gui import *


class ORectangle():

    """
    Give a rectangle
    """

    def __init__(self):
        '''
        Init QgsRectange, empty container
        '''

        # setup a basic rectangle selection tool
        self.pointList = list()
        self.selectionRectangle = QgsRectangle()

