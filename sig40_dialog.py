# -*- coding: utf-8 -*-
"""
/***************************************************************************
 sig40Dialog
                                 A QGIS plugin
 sig40
                             -------------------
        begin                : 2014-07-28
        git sha              : $Format:%H$
        copyright            : (C) 2014 by pierre foicik
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

from PyQt4 import QtGui, uic
from PyQt4 import QtGui
from PyQt4.Qt import QFrame, QGridLayout, QAction, QIcon
from PyQt4.QtCore import *
from PyQt4.QtGui import QTabWidget, QColor, QMainWindow, QFileDialog, QWidget, QDialog, QMessageBox

from qgis.core import *
from qgis.gui import *

from action.ProjectAction import GeoSelection
from action.ProjectAction import NewProjectAction
from action.ProjectAction import ConnectionParameters
from action.ProjectAction import ZRselection2
from action.ProjectAction import ZrDestroy
from action.ProjectAction import customStaticTools


from global_mod import Global
from ressources.resources import *

from ui.ui_main_window import Ui_MainWindow
from ui.ui_selection_zone_geo import Ui_Form
from ui.ui_start_tab_menu import Ui_TabWidget
from ui.ui_setConnectionParameter2 import Ui_Dialog as Ui_Form_connect
from ui.ui_supression_ZR import Ui_Dialog as Ui_Dialog_ZRdestroy

from ui.ui_selection_zone_reconciliation import Ui_Form as Ui_Form_ZR


from OProject import OProject
from ProjectXL import ProjectXL


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'sig40_dialog_base.ui'))

import sys

class sig40Dialog(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        """Constructor."""
        super(sig40Dialog, self).__init__(parent)
        QMainWindow.__init__(self, None)

        customStaticTools.centerOnScreen(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect

        # Instanciate a Oproject that will encapsulate all references and tools
        # for the session
        # Oproject instance will be shelved for persistance 

        #Reset all values
        try:
            Global.reset()
        except:
            pass

        Global.setMw(self)
        self.setEnabled(False)
        oproject = OProject()
        Global.setOproject(oproject)
        print Global.getOproject()

        projetXL = ProjectXL()
        Global.setprojectXL(projetXL)


        self.setupUi(self)
        self.setWindowTitle('ProjectXL Manager')
        #======================================================================
        # Create and add Child Widgets:
        # 1 - Tabulation
        #======================================================================
        self.our_tab_view = OurTabWiew(self)
        self.formLayout.addChildWidget(self.our_tab_view)

        #======================================================================
        # Give Action to the main windows
        #======================================================================
        self.setupAction_main()

        if Global.connectionstatus:
            self.connection_window = setConnectionParameters("Serveur SIG40: Choisir la base de donnée")
            self.connection_window.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.connection_window.show()


    def setupAction_main(self):
        """
        Give action to the main window
        Connect Signals -> Slots
        """

        self.connect(
            self.actionParam_tres_de_connexion, SIGNAL("triggered()"), self.setconnection)

    def setconnection(self):

        #======================================================================
        # Pop a connection parameters dialog
        #======================================================================

        self.connection_window = setConnectionParameters()
        self.connection_window.show()

class OurTabWiew(QTabWidget,  Ui_TabWidget, NewProjectAction):

    '''
    This class generate a QTab Widget
    Inherit From QtabWidget - PyQT4
    Inherit from our custom class -Ui_Tabwidget that construct our custom tabulated window.
    '''

    def __init__(self, parent):

        #======================================================================
        # QT Tab view constructor
        # Super Constuctor for our Tabulated Windows; CHILD of Top parent
        #======================================================================
        super(OurTabWiew, self).__init__(parent)
        #======================================================================
        # SetupUi from ui_Start_tab_menu
        # Build the windows apparence and layout
        #======================================================================
        self.parent = parent
        self.setupUi(self)
        self.timer = QTimer()
        # Retrieve System/USER value to be set and displayed
        self.editDirName.setText(os.path.expanduser("~"))
        self.timer.timeout.connect(self.updateInfo)
        self.timer.start(2000)

        #======================================================================
        # Give Action to the btnZoneCliente to allow window to pop-up
        # when clicked
        #======================================================================

        self.connect(
            self.btnZoneCliente, SIGNAL("clicked()"), self.selectZoneCliente)
        self.connect(
            self.btnZR, SIGNAL("clicked()"), self.selectZR)
        # Prepare variable to keep the selection window alive!
        self.selectionWindow = None

        #======================================================================
        # Give other button Action
        #======================================================================
        self.setupAction_newProject()
       

    def updateInfo(self):
        """
        Set Connection info
        """
        
        try:
            self.editUserName.setText(Global.getPG_connection().user)
            self.editIP.setText(Global.getPG_connection().IP)
            Global.getPG_connection()

            if Global.getPG_connection().con != None:
                self.editConnectionState.setText("Connection serveur OK")
                self.timer.stop()
                del self.timer
            else:
                self.editConnectionState.setText("Pas de Connection")
        except:
            pass
    # pop-up ZR area selection
    def selectZR(self):
        """
        Slot to pop a the ZR selection window
        """
        self.ZRWindow = OurZRSelection()
        self.ZRWindow.show()
        
        self.parent.close()
        self.close()

        pass

    # pop-up geoselection window
    def selectZoneCliente(self):
        """
        Slot to pop a the geographical selection window
        """
        self.selectionWindow = OurGeoSelection(self)
        try:
            if self.selectionWindow.error and Global.getPG_connection().con != None:
                #Simple cancel
                del self.selectionWindow
            elif self.selectionWindow.error:
                #print "pas de selection possible" 
                del self.selectionWindow
                QMessageBox.about(self, u"Base de donnée invalide",  "Suppression du projet en cours - Veuillez redéfinir un nouveau projet" )
                self.delProject()
                #It is required to redefine the connection parameters
                self.connection_window = setConnectionParameters("Connection Serveur: Choisir une base de donnée")
                self.connection_window.setWindowFlags(Qt.WindowStaysOnTopHint)
                self.connection_window.show()

            else:
                self.selectionWindow.show()
        except:
            #if self.selectionWindow.error doesn't exits, no error has been encountered
            self.selectionWindow.show()

class OurGeoSelection(QWidget, Ui_Form, GeoSelection):

    '''
    This class generate a QTab Widget
    Inherit From QWidget - PyQT4
    Inherit from our custom class -Ui_Tabwidget that construct our custom Widget to select geographical area.
    '''

    def __init__(self, parent):

        #======================================================================
        # QT Tab view constructor
        # Super Constuctor for our Tabulated Windows; NO PARENT
        #======================================================================
        super(OurGeoSelection, self).__init__()
        QWidget.__init__(self, None, Qt.WindowStaysOnTopHint)
        self.mapinstance = QgsMapLayerRegistry.instance()
        #Reference to the Tabulated window to allow field and button access 
        self.parent = parent
        #======================================================================
        # SetupUi from ui_Start_tab_menu
        # Build the windows apparence and layout
        #======================================================================
        self.setupUi(self)

        #======================================================================
        # Instanciate a Qgis map canvas and pass it to the windows
        #======================================================================
        self.map_canvas = QgsMapCanvas()
        self.map_canvas.setCanvasColor(QColor(255, 255, 255))
        self.gridLayout.addWidget(self.map_canvas)

        #======================================================================
        # Give Action to the pop-up windows
        #======================================================================
        a = self.setupAction_geoSelection()
        
        if not a:
            #print "Aucune couche importée return %s" %(a)
            self.error = True
           
class OurZRSelection(QWidget, Ui_Form_ZR, ZRselection2):

    '''
    This class generate a QTab Widget
    Inherit From QWidget - PyQT4
    Inherit from our custom class -Ui_Tabwidget that construct our custom Widget to select geographical area.
    '''

    def __init__(self):

        #======================================================================
        # QT Tab view constructor
        # Super Constuctor for our Tabulated Windows; NO PARENT
        #======================================================================
        super(OurZRSelection, self).__init__()
        # QWidget.__init__(self, None, Qt.WindowStaysOnTopHint)
        # self.mapinstance = QgsMapLayerRegistry.instance()
        #======================================================================
        # SetupUi from ui_Start_tab_menu
        # Build the windows apparence and layout
        #======================================================================
        self.setupUi(self)

     
        #======================================================================
        # Give Action to the pop-up windows
        #======================================================================
        self.setupAction_ZRselection2()

class setConnectionParameters(QWidget, Ui_Form_connect, ConnectionParameters):

    def __init__(self, errormess = "", parent =None):
        super(setConnectionParameters, self).__init__()
        QWidget.__init__(self, parent , Qt.WindowStaysOnTopHint)
        
        
        
        customStaticTools.centerOnScreen(self)
        self.setupUi(self)

        #Add a message bar to communicate with the user
        self.bar = QgsMessageBar()
        self.bar.adjustSize()
        #self.bar.setSizePolicy( QSizePolicy.Maximum, QSizePolicy.Expanding)
        self.gridLayout.addWidget(self.bar,0,0)

        #Give user some information about the default PG connection status
        if Global.connectionstatus:
            self.bar.pushMessage("OK",unicode(errormess, "utf-8"), level=QgsMessageBar.INFO)
        else: 
            unicoded_mess = "Paramètres invalides - Modifications requises - "+str(errormess)
            # unicoded_mess = u"Paramètres invalides - Modifications requises - "+unicode(errormess, "utf-8")


            # self.bar.pushMessage("",  unicode(errormess, "utf-8")
            #  , level=QgsMessageBar.CRITICAL)
            self.bar.pushMessage("",  errormess
             , level=QgsMessageBar.CRITICAL)
        # Retrieve System/USER value to be set and displayed
        try:
           
            self.editUserName.setText(Global.getUserName())
            self.editBDName.setText(Global.getBDname())
            self.editHostName.setText(Global.getHostName())
        except:
        
            self.editUserName.setText("")
            self.editBDName.setText("")
            self.editHostName.setText("")

        #======================================================================
        # Give Action to the connection parameters windows
        #======================================================================
        self.setupAction_connectionParameters()

class OurZRDestroyer(QDialog, Ui_Dialog_ZRdestroy, ZrDestroy ):
    """
    Class for ZR destruction
    Serve a fidlist -- list of indexed booleans to their fid index
    """
    def __init__(self, parent =None):
        super(OurZRDestroyer, self).__init__()
        QWidget.__init__(self, parent , Qt.WindowStaysOnTopHint)

        self.fidlist = []
        
        self.setupUi(self)

        self.setupAction_ZRdestroy()
