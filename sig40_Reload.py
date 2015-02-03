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
from qgis.utils import *

from action.ProjectAction import GeoSelection
from action.ProjectAction import NewProjectAction
from action.ProjectAction import ConnectionParameters

from global_mod import Global
from ressources.resources import *

from ui.ui_main_window import Ui_MainWindow
from ui.ui_selection_zone_geo import Ui_Form
from ui.ui_start_tab_menu import Ui_TabWidget
from ui.ui_setConnectionParameter2 import Ui_Dialog as Ui_Form_connect
from ui.ui_selection_zone_reconciliation import Ui_Form as Ui_Form_ZR


from OProject import OProject
from ProjectXL import ProjectXL


class OurReload(QWidget):

    '''
    This class reload a project
    User browse directories to the desired path
    '''

    def __init__(self):

        

        


        #============================================================== ========
        # QT Widget constructor
        # Super Constuctor for our Qfiledialog; NO PARENT
        #======================================================================
        super(OurReload, self).__init__()
        

        # Give chance to abort reload
        self.load = True
        self.closeEvent()

        if self.load:

            qproject = QgsProject.instance()
            #first save and close all active session
            # Make reference to the QGIS project view
            #If a project is already loaded and Dirty first save
            if qproject: 	    
            	qproject.write()
            #Any other Cases (BLANK OR CLEAN), clear the project
            try:
                qproject.clear()
            except:
                pass
            #Reload the Project to clear 
            filename = self.browseDir()
            
            
            boold = qproject.read(QFileInfo(filename))


            mapinstance = QgsMapLayerRegistry.instance()
            canvas = iface.mapCanvas()

            canvas.zoomToFullExtent()


    def browseDir(self):
        """
        Select a project directory within the OS filesystem
        """
        # Caption dirname in local variable
        filename = QFileDialog.getOpenFileName(self, "", "","*.qgs" )
        #======================================================================
        # Write Project Directory
        #======================================================================
        # directory name does not exist; empty string;...
        if filename=='':
            return
        else:
        	return filename 
    
    def closeEvent(self):

        quit_msg = u"êtes-vous sur de vouloir recharger un projet?"
        reply = QMessageBox.question(self, 'Message', 
                         quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            pass
        else:
            self.load = False
           


