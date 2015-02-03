# -*- coding: utf-8 -*-
"""
/***************************************************************************
 sig40Dialog
                                 A QGIS plugin
 sig40
                             -------------------
        begin                : 2014-07-28
        git sha              : $Format:%H$
        copyright            : (C) 2014 by p
        email                : pierre.foicik@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from action.ProjectAction import GeoSelection
from action.ProjectAction import NewProjectAction
from action.ProjectAction import ConnectionParameters
from action.ProjectAction import ZRselection2
from global_mod import Global

import time
import shutil
import shelve
import sys

from ressources.resources import *
from ui.ui_main_window import Ui_MainWindow
from ui.ui_selection_zone_geo import Ui_Form
from ui.ui_start_tab_menu import Ui_TabWidget
from ui.ui_setConnectionParameter2 import Ui_Dialog as Ui_Form_connect
from ui.ui_selection_zone_reconciliation import Ui_Form as Ui_Form_ZR


from ProjectXL import ProjectXL


class OurZRSelectionReload(QWidget, Ui_Form_ZR, ZRselection2):

    '''
    This class generate a Object to initialize a "Zone de Reconciliation" dialog callable at anytime
    Inherit From QWidget - PyQT4
    Inherit from our custom class -Ui_Tabwidget that construct our custom Widget to select geographical area.
    '''

    def __init__(self):

        #======================================================================
        # QT Tab view constructor
        # Super Constuctor for our Tabulated Windows; NO PARENT
        #======================================================================
        super(OurZRSelectionReload, self).__init__()

        QWidget.__init__(self, None, Qt.WindowStaysOnTopHint)

        #Make reference to QGIS main objects
        self.mapinstance = QgsMapLayerRegistry.instance()
        self.qproject = QgsProject.instance()
        #Retrieve the project Path from the QgsProject instance

        project_path = self.qproject.homePath()
        #Rebuild the current folder path
        shelve_path = os.path.join(
            str(project_path), "current/shelf_PP.db")
        current_path = os.path.join(
            str(project_path), "current")
        tmp_path = os.path.join(
            str(project_path), "shelve.db")
         # Change directory
        #os.chdir(current_path)
        try:
            #======================================================================
            #Rebuild Oproject instance from shelf
            #======================================================================
            shelve_p = shelve.open(shelve_path,  writeback=True)
            self.oproject = shelve_p['object']
            Global.setOproject(self.oproject)
            #======================================================================
            # SetupUi from ui_Start_tab_menu
            # Build the windows apparence and layout
            #======================================================================
            self.setupUi(self)
            #======================================================================
            # Give Action to the pop-up windows
            #======================================================================
            self.setupAction_ZRselection2(Global.getOproject())
            self.loaded = True
        except:
            self.loaded = False
            QMessageBox.about(self, 'A Message from earth' , 
                         u'Pas de projet chargé - Veuilles créer/recharger un projet avant de définir une nouvelle ZR')

       

    # def browseDir(self):
    #     """
    #     Select a project directory within the OS filesystem
    #     """
    #     # Caption dirname in local variable
    #     filename = QFileDialog.getOpenFileName(self, "", "","*.qgs" )
    #     #======================================================================
    #     # Write Project Directory
    #     #======================================================================
    #     # directory name does not exist; empty string;...
    #     if filename=='':
    #         return
    #     else:
    #     	return filename 
        	

