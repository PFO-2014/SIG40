# -*- coding: utf-8 -*-
"""
/***************************************************************************
 sig40
                                 A QGIS plugin
 sig40
                              -------------------
        begin                : 2014-07-28
        git sha              : $Format:%H$
        copyright            : (C) 2014 by pierre.foicik
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

from qgis.core import QgsApplication
from PyQt4.QtCore import *

from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
from PyQt4.QtGui import QApplication

import os.path
import sys

# Initialize Qt resources from file resources.py
import ressources.resources
# Import the code for the dialog
from sig40_dialog import sig40Dialog
from sig40_ZR_dialog import OurZRSelectionReload
from sig40_dialog import OurZRDestroyer
from sig40_reSync import reSyncDB
from sig40_Reload import OurReload
from global_mod import Global



class sig40:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0: 2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'sig40_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
	
	

        

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&sig40')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'sig40')
        self.toolbar.setObjectName(u'sig40')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('sig40', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the InaSAFE toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/ourapp/XLlogo_big'
        self.add_action(
            icon_path,
            text=self.tr(u'''Création d'un projet'''),
            callback=self.run,
            parent=self.iface.mainWindow())

        

        icon_path = ':/ourapp/reload'
        self.add_action(
            icon_path,
            text=self.tr(u'''Reprendre un projet'''),
            callback=self.reload,
            parent=self.iface.mainWindow())


        icon_path = ':/ourapp/ZRlogo'
        self.add_action(
            icon_path,
            text=self.tr(u'''Selection d'une ou plusieurs Zone de Reconciliation'''),
            callback=self.run2,
            parent=self.iface.mainWindow())

        icon_path = ':/ourapp/destructlogo'
        self.add_action(
            icon_path,
            text=self.tr(u'''Suppression d'une Zone de Reconciliation'''),
            callback=self.run3,
            parent=self.iface.mainWindow())


        icon_path = ':/ourapp/pgdb'
        self.add_action(
            icon_path,
            text=self.tr(u'''Reconciliation avec la Base de donnée'''),
            callback=self.run4,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&sig40'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""
        # Create the main dialog (after translation) and keep reference

        self.dlg = sig40Dialog()
        # show the dialog
        self.dlg.show()

        # self.dlg = sig40Dialog()
        # # show the dialog
        # self.dlg.show()

            #Run the dialog event loop
            #result = self.dlg.exec_()
        # See if OK was pressed
       # if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
        #    pass

    def run2(self):
        """Tool to create ZR for the current project"""
        # show the dialog
        self.ZRreload = OurZRSelectionReload()
        if self.ZRreload.loaded:
            self.ZRreload.show()
        else:
            #do nothing
            pass

    def run3(self):
        """Tool to delete ZR for the current project"""
        # show the dialog
        self.ZRDestroy = OurZRDestroyer()
        if self.ZRDestroy.loaded:
            self.ZRDestroy.show()
        else:
            #do nothing
            pass

        self.ZRDestroy.show()

    def run4(self):
        """Tool to reconciliate local SQLITE db with the PG database for
        the current project
        """
        # No dialog
        self.project = reSyncDB()
        #reSyncDB.test()
        #self.connectionPG = reSyncDB.connectTry()
        
        if self.project.loaded:
            self.project.reconciliate()
        else:
            #do nothing
            pass


    def reload(self):
        """Reload a previous XL project"""
        # show the dialog
        self.ZRreload = OurReload()
