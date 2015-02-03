# -*- coding: utf-8 -*-

'''
SIG40 Plugin
Created on 11 juil. 2014

Contains All QT Signals to Slots 
Contains All Required Project Action:

    -Build project
    -Save project
    -Select from DB
    -Save to SQLITE
    -Select ZR
    
@author: pierre foicik
pierre.foicik@gmail.com
'''

import qgis
from qgis.core import *
from qgis.gui import *

from PyQt4.QtCore import SIGNAL, QSize, QObject

try:
    from PyQt4.QtCore import QStringList
except ImportError:
    QStringList = list
from PyQt4.QtGui import (QColor,  QFileDialog, QMessageBox, QPushButton, QDialog,
                         QPixmap, QInputDialog, QCheckBox, QWidget, QTableWidget,
                         QTableWidgetItem, QVBoxLayout, QCursor, QColor, QMouseEvent,
                         QProgressBar, QDesktopWidget, QApplication)
from PyQt4.QtCore import Qt, QFileInfo 

from __builtin__ import list
import copy
import os
import time
import unicodedata
import shelve
import shutil

from sig40.utils_sig40.ErrorMessage import errorMessage
from sig40.dbtools.OGeoDB import LocalDB_utils, OQgis
from sig40.OProject import OProject
from sig40.dbtools.OSqlite import OSqlite
from sig40.ProjectXL import ProjectXL
from sig40.dbtools.URI_Builder import URI_Builder
from sig40.global_mod import Global
from sig40.utils_sig40.polygon4qgis import ORectangle
from sig40.ressources.resources import *

from threading import Thread

import sys


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

class customStaticTools(object):
    """"
    Static toolbox
    """
    @staticmethod
    def centerOnScreen(window):
        '''
        centerOnScreen()
        Centers the window on the screen.
        '''
        resolution = QDesktopWidget().screenGeometry()
        # print resolution
        window.move((resolution.width() / 2) - (window.frameSize().width() / 2),
                      (resolution.height() / 2) - (window.frameSize().height() / 2))


class YesNo(QDialog):

    def __init__(self, path, window, mess):
        super(YesNo, self).__init__()

        msgBox = QMessageBox()
        msgBox.setText(mess)
        tmp = QPixmap(":/ourapp/warning")
        icon = QPixmap(tmp.scaled(QSize(32,32)))
        # print icon.size()
        msgBox.setIconPixmap(icon)
        msgBox.addButton(
            QPushButton('OUI'), QMessageBox.YesRole)
        msgBox.addButton(QPushButton('NON'), QMessageBox.NoRole)


        self.centerOnScreen(msgBox)
        msgBox.setWindowTitle('Suppression de projet')

        ret = msgBox.exec_()

        if ret == False:

            # print "delete dir '%s'" % (path)
            # print path
            os.chdir(os.path.expanduser("~"))

            shutil.rmtree(path)
            # print "reset editProjectName"
            try:
                window.editProjectName.setText("")

                # Give action to the extraction button
                
                window.btnExtraction.setEnabled(False)
                window.btnZoneCliente.setEnabled(False)
                window.btnProjectSuppression.setEnabled(False)
                

                # Remove action to the project Button and Qline edit
                window.btnProjectValidation.setEnabled(True)
                window.btnSelectPath.setEnabled(True)

                window.editDirName.setEnabled(True)
                window.editProjectName.setEnabled(True)

            except:
                window.parent.editProjectName.setText("")
                # Give action to the extraction button
                
                window.parent.btnExtraction.setEnabled(False)
                window.parent.btnZoneCliente.setEnabled(False)
                window.parent.btnProjectSuppression.setEnabled(False)
                

                # Remove action to the project Button and Qline edit
                window.parent.btnProjectValidation.setEnabled(True)
                window.parent.btnSelectPath.setEnabled(True)

                window.parent.editDirName.setEnabled(True)
                window.parent.editProjectName.setEnabled(True)

            #"del python object"
            del Global.oproject
            Global.delPG_connection()
            #print "rebuild python Object 1"
            oproject = OProject()
            Global.setOproject(oproject)

            #print "rebuild python Object 2"
            projetXL = ProjectXL()
            Global.setprojectXL(projetXL)
            
        if ret == True:
            return

    def centerOnScreen(self, messbox):
        '''
        centerOnScreen()
        Centers the window on the screen.
        '''
        resolution = QDesktopWidget().screenGeometry()
        # print resolution
        messbox.move((resolution.width() / 2) - (messbox.frameSize().width() / 2),
                      (resolution.height() / 2) - (messbox.frameSize().height() / 2))


class NewProjectAction(object):

    '''
    this class encapsulate all software/user interaction required to build a Projet
    '''

    #-------------------------------------------------------------------------
    #-------------------------ALL CONNECTION DEFINED HEREAFTER----------------
    #-------------------------------------------------------------------------

    def setupAction_newProject(self, *args):
        """
        Give action to the tabulated window
        Connect Signals -> Slots
        """
        if args:
            self.projectXL = args[0]

        #======================================================================
        # Project Tab  (path; date; general info)
        #======================================================================
        self.connect(
            self.btnSelectPath, SIGNAL("clicked()"), self.browseDir)
        self.connect(
            self.editProjectName, SIGNAL("textEdited(QString)"), self.setProjectName)
        self.connect(
            self.btnProjectValidation, SIGNAL("clicked()"), self.writeProjectToFSI)
        self.connect(
            self.btnExtraction, SIGNAL("clicked()"), self.ExtractData)
        self.connect(
            self.btnProjectSuppression, SIGNAL("clicked()"), self.delProject)
        

    #-------------------------------------------------------------------------
    #-------------------------ALL SLOT ARE DEFINE BELOW-----------------------
    #-------------------------------------------------------------------------
    
    def writeProjectShelf(self, oproject):

        # Test if the shelf is already open/needs to be open

        shelve_project_parameters = shelve.open('shelf_PP.db')

        # Construct the shelve:
        try:
            shelve_project_parameters['object'] = oproject
          
        finally:
            shelve_project_parameters.close()

        # print "Project Shelved!"
    
    def delProject(self):
        """
        Delete the project being build (remove directories)
        YesNo Class execute the deletion
        """

        # print "delete start"
        fullpath = os.path.join(
            str(self.editDirName.text()), str(self.editProjectName.text()))
        # Pop a YesNo cofirmation message
        messtxt = "Suppression du projet? ACTION IRREVERSIBLE!!"
        mess = YesNo(fullpath, self,messtxt)
        mess.show()

        #Empty the QgsProject instance from residual
        qproject = QgsProject.instance()
        qproject.clear()

        #Clear the previous message bar
        qgis.utils.iface.messageBar().clearWidgets()
        self.readyMessageBar = qgis.utils.iface.messageBar()
        self.readyMessageBar.pushMessage("PROJET SUPPRIME", u"Le projet en cours a été supprimé du système - En attente d'une création de projet", level= QgsMessageBar.WARNING, duration=10)


    def browseDir(self):
        """
        Select a project directory within the OS filesystem
        """
        # Caption dirname in local variable
        dirname = QFileDialog.getExistingDirectory(self)
        #======================================================================
        # Write Project Directory
        #======================================================================
        # directory name does not exist; empty string;...
        if dirname=='':
            return
        else:
            self.editDirName.setText(dirname)
        # update oproject
        # pass the project path to the oproject
        Global.getOproject().setProjectPath(str(self.editDirName.text()))
        # global_mod.oproject.setProjectPath(str(self.editDirName.text()))

    def setProjectName(self):
        """"
        Set a projet Name
        """
        # update oproject
        # pass the project name to the oproject
        try:
            Global.getOproject().setProjectName(str(self.editProjectName.text()))
            Global.setProjectName(str(self.editProjectName.text()))
            # Give action to the Project Validation Button
            self.btnProjectValidation.setEnabled(True)
        except:
            #Unauthorized char"
            QMessageBox.about(
                self, u"Caratère invalide", u"Le nom du projet ne peut-pas contenir de caractères accentués ou spéciaux")

            self.editProjectName.setText("")

    def writeProjectToFSI(self):
        """
        Write the project to the filesystem; create arborescence
        """
        # Build a generic/OS independant path
        # Transyping required from QString to regular python String
        path = os.path.join(
            str(self.editDirName.text()), str(self.editProjectName.text()))

        if os.path.exists(path):
            #Need to choose another name
            QMessageBox.about(
                self, "Erreur", u"Le projet %s existe déjà, veuillez choisir un nouveau nom" %(Global.getOproject().project_name))
            self.editProjectName.setText("")

        else:

            path_archive = os.path.join(path, "archive")
            path_current = os.path.join(path, "current")
            Global.getOproject().setCurrentProjectPath(path_current)


            os.mkdir(path)
            os.mkdir(path_archive)
            os.mkdir(path_current)

            # Change directory
            os.chdir(path_current)
            
            # test saving QGIS project view
            # Make reference to the QGIS project view
            #qproject = Global.getOproject().qproject
            qproject = QgsProject.instance()
            path_proj = os.path.join(path, "XLproject.qgs")
            qproject.setFileName(path_proj)
            # Write Changes
            qproject.write()            
            QMessageBox.about(
                self, "Projet %s" % (Global.getOproject().project_name), "Ajouter un ZC et/ou lancer l'extraction pour completer le projet")

            # Give action to the extraction button
            self.btnExtraction.setEnabled(True)
            self.btnZoneCliente.setEnabled(True)
            self.btnProjectSuppression.setEnabled(True)

            # Remove action to the project Button and Qline edit
            self.btnProjectValidation.setEnabled(False)
            self.btnSelectPath.setEnabled(False)

            self.editDirName.setEnabled(False)
            self.editProjectName.setEnabled(False)


    def showCanvas(self):
        #print "SHOW CANVAS"
        self.map_canvas = QgsMapCanvas()
        self.map_canvas.setCanvasColor(QColor(255, 255, 255))
        self.gridLayout_2.addWidget(self.map_canvas)

        layer = QgsVectorLayer(
            URI_Builder.static_testing_uri(), "test", "postgres")
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        canvas_layer = QgsMapCanvasLayer(layer)
        self.map_canvas.setLayerSet([canvas_layer])


    def writeToLocalDB(self, *args):
        """
        Init the writing of local databases extracted from the Server
        Install Required Triggers and local Field
        Install mandatory ZR database
        """

        # Make reference to the current Project
        projectxl = Global.getProjectXL()

        # make reference to the tables name
        l = projectxl.postgres_connection.tableListWithGeom
        
        # pass the list of table to the PyQGIS URI builder
        # WARNING: THIS COPY THE ENTIRE EXTENT OF THE DATABASE.
        # SQL STATEMENT MUST BE INJECTED TO DEFINE THE SPATIAL EXTENT OF THE
        # REQUEST, IE THE "ZONE_CLIENTE"

        try:
            args
            pol = args[0].asWktPolygon()
            
            urilist = projectxl.postgres_connection.getUri(l,'public', pol)
            

        except:
            #Case the polygon is invalid 
            urilist = projectxl.postgres_connection.getUri(l, 'public')


        # Build a PyQGIS vector layer list from the URI list
        layerlist = projectxl.postgres_connection.VectorlayerListBuilder(
            urilist)
        
        #Create a ZR table - MANDATORY
        
        thread1 = Function_threader(OSqlite.CreateSpatialDB, "ZR")
        # zr = OSqlite("ZR")
        thread1.start()
        

        #Set a specfic progress bar for each layer
        qgis.utils.iface.messageBar().clearWidgets() 
        

        #first start/set a progress bar
        self.progressMessageBar = qgis.utils.iface.messageBar().createMessage("Writing to Local Database - Please Wait")
        
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setTextVisible (True) 
        self.progressMessageBar.layout().addWidget(self.progress)
        qgis.utils.iface.messageBar().pushWidget(self.progressMessageBar, qgis.utils.iface.messageBar().INFO)
        #self.progressMessageBar.pushWidget(self.progress)
        #Count all selected feature
        count =  len(layerlist)
        j = 0
        
        # Write VectorLayer to SQLITE file
        for i in range(0, len(layerlist)):

            #update the progress bar
            j = j + 1
            
            self.progressMessageBar.setText("processing: "+str(layerlist[i].name()))
            percent = (j/float(count)) * 100
            time.sleep(1)
            self.progress.setValue(percent)

            projectxl.postgres_connection.WriteVectorLayer2Sqlite(layerlist[i])
        try:
                qgis.utils.iface.messageBar().clearWidgets()
        except:
            pass
            
        # Set the SQLITE triggers
        for i in Global.getPG_connection().tableListWithGeomDict.keys():
            #If table have been selected for export
            if Global.getPG_connection().tableListWithGeomDict[i][5]:
                # Implant Triggers
                # retreive the DB name from the corresponding QgsVectorLayer
                tabname = str(i) 
                path = Global.getOproject().currentProjectPath

                # Install the trigger within the local SQLITE DB project files
                projectxl.postgres_connection.Trigger_UserMod(path, tabname)
                projectxl.postgres_connection.Trigger_UserMod2(path, tabname)

                projectxl.postgres_connection.Trigger_UserAdd(path, tabname)
                projectxl.postgres_connection.Trigger_PK(path, tabname)
                projectxl.postgres_connection.Trigger_UserDel(path, tabname)
                # projectxl.postgres_connection.Trigger_UserDel_protected(path, tabname)

                projectxl.postgres_connection.AddField(path, tabname, "ZRlocal", "integer default -1")
                projectxl.postgres_connection.AddField(path, tabname, "ZRnew", "integer default 1")


        #==========================================================
        #Copy sources
        #==========================================================
        # make reference to the tables name
        l = projectxl.postgres_connection.tableListWithGeom_source
        
        try:
            
            lenght = len(tableListWithGeom_source)

             
            # pass the list of table to the PyQGIS URI builder
            # WARNING: THIS COPY THE ENTIRE EXTENT OF THE DATABASE.
            # SQL STATEMENT MUST BE INJECTED TO DEFINE THE SPATIAL EXTENT OF THE
            # REQUEST, IE THE "ZONE_CLIENTE"

            try:
                args
                pol = args[0].asWktPolygon()
                urilist = projectxl.postgres_connection.getUri(l, 'source', pol)

            except:
                urilist = projectxl.postgres_connection.getUri(l, 'source')
                
            # Build a PyQGIS vector layer list from the URI list
            layerlist = projectxl.postgres_connection.VectorlayerListBuilder(
                urilist)
            
                       
            # Write VectorLayer to SQLITE file
            for i in range(0, len(layerlist)):
                projectxl.postgres_connection.WriteVectorLayer2Sqlite(layerlist[i])
                
            # NO SQLITE triggers for the sources
        except:
            # print "no sources to import"
            pass

        thread1.join()


    def ExtractData(self):
        '''
        Perform Data extraction from PG server
        Write to local SQLITE DB files
        Save Project
        '''
          
		

        # print Global.getOproject().ZC.asWktPolygon()
        if Global.getOproject().ZC != None:

            self.writeToLocalDB(Global.getOproject().ZC)

            # Make reference to the current Project
            projectxl = Global.getProjectXL()
            #Load the layer within QGIS
            self.progressMessageBar = qgis.utils.iface.messageBar().createMessage("Chargement en cours...")
            self.progress = QProgressBar()
            self.progress.setRange(0,0)
            self.progressMessageBar.layout().addWidget(self.progress)
            qgis.utils.iface.messageBar().pushWidget(self.progressMessageBar, qgis.utils.iface.messageBar().INFO)
         


            projectxl.postgres_connection.registerLocalLayers()

            try:
                qgis.utils.iface.messageBar().clearWidgets()
            except:
                pass
            
            self.readyMessageBar = qgis.utils.iface.messageBar()
            self.readyMessageBar.pushMessage("OK!", u"import complet - projet prêt", level= QgsMessageBar.INFO, duration=10)
        

            #Allow ZR selection 
            self.btnZR.setEnabled(True)
            #Disallow redefining the selection area - need to rebuild a project
            self.btnZoneCliente.setEnabled(False)
            #Disallow Extraction
            self.btnExtraction.setEnabled(False)
            
            #=======================================================================
            # shelve the Global parameters - Required to reload the project 
            #=======================================================================
            #Update critical attribute
            Global.getOproject().tableDict = Global.getPG_connection().tableListWithGeomDict
            
            copy_project = copy.deepcopy(Global.getOproject())
            
            self.writeProjectShelf(copy_project)
            
            # Make reference to the QGIS project view
            qproject = QgsProject.instance()
            #Set title
            try:
                qproject.setTitle(str(Global.getProjectName()))
            except:
                pass
            # Global.getOproject().writeProjectShelf()
            # Save the project
            qproject.write()

        else:
            #need to specify a ZC
            QMessageBox.about(
                self, u"Action requise" , u"Veuillez définir une Zone Cliente avant de réaliser l'extraction des données")
            return

    #-------------------------------------------------------------------------
    #-------------------------GETTERS - SETTERS-------------------------------
    #-------------------------------------------------------------------------

    def getProjectName(self):
        pass

    def getProjetPath(self):
        pass


class GeoSelection(object):

    '''
    this class encapsulate all software/user interaction required to perform a Geographical selection
    over the Project Database
    '''
    #-------------------------------------------------------------------------
    #-------------------------ALL CONNECTION DEFINED HEREAFTER----------------
    #-------------------------------------------------------------------------

    def setupAction_geoSelection(self, *args):
        """
        Give action to the geoselection Window
        Connect Signals -> Slots
        """
        #======================================================================
        # Action: Accept; discard; Browse...
        #======================================================================
        # Signal sur ComboBox
        self.connect(
            self.comboBox_listPGtables, SIGNAL("currentIndexChanged(int)"), self.selectLayer)
        self.connect(
            self.toolButtonSelect, SIGNAL("clicked()"), self.geoSelect)
        self.connect(
            self.toolButtonDestruct, SIGNAL("clicked()"), self.geoDestruct)
        self.connect(
            self.toolButtonPoly, SIGNAL("clicked()"), self.geoPoly)
        self.connect(
            self.buttonBox, SIGNAL("accepted()"), self.completeSelect)
        self.connect(
            self.buttonBox, SIGNAL("rejected()"), self.abortSelect)
        
        #Destruction disabled
        self.toolButtonDestruct.setEnabled(False)
        
        #======================================================================
        # Populate ComboBox
        #======================================================================
        self.comboBox_listPGtables.clear()
        #self.comboBox_listPGtables.addItems(Global.getPG_connection().tableList)

        self.comboBox_listPGtables.addItems(Global.dict_form_pre.keys())
        self.comboBox_listPGtables.setCurrentIndex(Global.dict_form_pre.keys().index('--select--'))

        #======================================================================
        # Populate the tableWidget and give checkboxes
        #======================================================================
        
        numberRows = len(Global.getPG_connection().tableList)
        numberColumns = 1
        
        self.tableWidget.setRowCount(numberRows)
        self.tableWidget.setColumnCount(numberColumns)

        for rowNumber in range(numberRows):
            for columnNumber in range(numberColumns):
                item = QTableWidgetItem(Global.getPG_connection().tableList[rowNumber])
                item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                item.setCheckState(QtCore.Qt.Checked)
                
                self.tableWidget.setItem(rowNumber, columnNumber, item)
        
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels(['couches disponibles'])
        
        #=======================================================================
        # add a specific Boolean field to the tableDictionnary to keep CheckState
        # Defaulted to True
        #=======================================================================
        for key in  Global.getPG_connection().tableListWithGeomDict.keys():
            Global.getPG_connection().tableListWithGeomDict[key].append(True)
       
       
        #=======================================================================
        # Allow to select wich layer to be displayed to help to perform geoselection
        #=======================================================================
        ql = QStringList()
        #retrieve the previously fetched table list
        l = Global.getPG_connection().tableList
        #If tableList is empty, No geometry tables are available: EXIT!
        if len(l) == 0:
            QMessageBox.about(self, u"Base de donnée invalide",  u"Aucune donnée géographique disponible \nVeuillez redéfinir les paramètres de connection" )
            fullpath = os.path.join(
            str(self.parent.editDirName.text()), str(self.parent.editProjectName.text()))
            messtxt = "Suppression du projet? ACTION IRREVERSIBLE!!"
            mess = YesNo(fullpath, self,messtxt)
            
            self.close()
        else:
            #pass it to a QStringList to allow usage within a QInputDialog
            for item in l:
                ql.append(item)
            #Pass the QStringList to the QInputDialog
            table, ok = QInputDialog.getItem(self, unicode("Choix d'une couche à afficher", 'utf-8'), 
                unicode("Base de donnée '%s'"%(Global.BDname), 'utf-8'), ql )
       
            #=======================================================================
            # Build the corresponding URI
            #=======================================================================
            # QMessageBox.about(
            #     self, "parametres courant",  "user: %s, host: %s, DB: %s" % ( Global.getUserName(), Global.getHostName(),Global.getBDname() ) )

            if ok and table != "":
                #uri = URI_Builder(table)
                uri = URI_Builder(table,  Global.getHostName(), "5432", Global.getBDname(), Global.getUserName() )

                # QMessageBox.about(self, "URI courant",  uri.getDBpath() ) 

            #=======================================================================
            # Pass the URI Layer to the Canvas
            #=======================================================================
            

            try:

                self.add_postgis_layer(uri.getDBpath())
                self.map_canvas.zoomToFullExtent()
                return True
                   
            except:
                
                return False                                                                                

    #-------------------------------------------------------------------------
    #-------------------------ALL SLOT ARE DEFINE BELOW-----------------------
    #-------------------------------------------------------------------------
  
    def abortSelect(self):
        """
        Exit
        """
        try:
            #=======================================================================
            # Remove Selection Layer from Registry - Turn project into dirty state
            #=======================================================================
            self.remove_postgis_layer(self.layerId)
            #=======================================================================
            # clean project
            #=======================================================================
            # Make reference to the QGIS project view
            qproject = Global.getOproject().qproject
            # Global.getOproject().writeProjectShelf()
            # Save the project
            qproject.write()
            self.close()
        except:
            self.close()
        
    def completeSelect(self):
        """
        Check if a selection has been performed
        Set the checkState within the tableList Di
        ctionnary
        Load the ZC as a separate layer within the QgsMapregistry
        
        Set custom renderer for the ZC layer (opacity)
        
        Memory -> compose VectorLayer from attributes (QgsRectangle)-> Write to disk 
        -> reload and add to the QgsMapregistry for projet persistence
        
        """

        # Remove the layer that help to draw the selection box form the
        # registry
        e = u"Aucune zone n'a encore été sélectionnée"
        try:
            self.orectangle
            
            if Global.getOproject().ZC != None:
                self.remove_postgis_layer(self.layerId)
                # close the window
                self.close()
            else:
                QMessageBox.critical(
                    self ,u"Synchronisation annulée",e)
                # errorMessage(e)
        except:
            QMessageBox.critical(
                    self ,u"Synchronisation annulée",e)
                # errorMessage(e)
            return
            
        for rowNumber in range(self.tableWidget.rowCount()):
            #test the checkState of each QTableWidgetItem
            if self.tableWidget.item(rowNumber, 0).checkState() == 0:
                #if uncheck, get item Name
                #print str(self.tableWidget.item (rowNumber, 0).text())
                #set checkState to False in table dictionnary
                try:
                    Global.getPG_connection().tableListWithGeomDict[str(self.tableWidget.item (rowNumber, 0).text())][5] = False
                except:
                    # Key error: table does not have any geometry (not reference by the tableListWithGeomDict dictionnary )
                    pass

        
        
        #=======================================================================
        # Build the ZC layer from user selection
        #=======================================================================
        #set a memory layer, crs retrieved from last loaded layer
        
        mem_layer = QgsVectorLayer("POLYGON?crs="+Global.getOproject().getCcrs()+"&field=id:integer", "Zone_Cliente", "memory")
        #get memory layer provider
        pr = mem_layer.dataProvider()
        mem_layer.startEditing()
        #Prepare feature
        feat = QgsFeature()
        
        #set feature to the current selection rectangle
        feat.setAttributes([1]) #Dummy "1" attributes
        try:
            feat.setGeometry(QgsGeometry.fromRect(Global.getOproject().ZC))
        except:
            feat.setGeometry(QgsGeometry.fromPolygon(Global.getOproject().ZC.asPolygon()))
            Global.getOproject().ZC = Global.getOproject().ZC.exportToWkt()

        #add the feature
        pr.addFeatures([feat])
        #make sure the layer contains our new features
        mem_layer.updateExtents()
        mem_layer.commitChanges()

        


        #=======================================================================
        # Write and reload the vector for persistance
        #=======================================================================
        QgsVectorFileWriter.writeAsVectorFormat(mem_layer, str(mem_layer.name()) + ".sqlite",
                                                        "utf-8", None, "SQLite")
        

        vlayerpath = os.path.join(
                    Global.getOproject().currentProjectPath, str(mem_layer.name()) + ".sqlite")
        vlayer = QgsVectorLayer(vlayerpath, mem_layer.name(), "ogr")
    
              
        if vlayer.isValid():
            # print "sqllayer succesfully loaded - adding to mapinstance"
            #Global.getOproject().mapinstance.addMapLayer(vlayer)
            QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            
            
        #=======================================================================
        # set Custom Style for the ZC layer:
        #=======================================================================
            #get memory layer provider
            pr = vlayer.dataProvider()
            vlayer.startEditing()
            
            #Set the renderer
            myColour = QColor('#ffee00')
            myOpacity = 0.25
            #define the Single Symbol associated with the layer
            mySymbol1 = QgsSymbolV2.defaultSymbol(
               vlayer.geometryType())
            mySymbol1.setColor(myColour)
            mySymbol1.setAlpha(myOpacity)
            
            myRenderer = QgsSingleSymbolRendererV2(mySymbol1)
            vlayer.setRendererV2(myRenderer)

            vlayer.commitChanges()
            
    
            canvas_layer = QgsMapCanvasLayer(vlayer)
            canvas = QgsMapCanvas()
            canvas.setLayerSet([canvas_layer])
        else:
            # print "sqllayer failed to load!"
            pass

        #=======================================================================
        # Update view
        #=======================================================================
        canvas.zoomToFullExtent()
        #=======================================================================
        # Remove Selection Layer from Registry -- turn project to 'Dirty' state
        #=======================================================================
        self.remove_postgis_layer(self.layerId)
        
        #=======================================================================
        # clean project
        #=======================================================================
        # Make reference to the QGIS project view
        qproject = QgsProject.instance()
        # Save the project
        qproject.write()
            
    def geoDestruct(self):
        """
        This method reset the current selection rectangle
        """
        #Return if nothng has been set
        try:
            self.orectangle
        except NameError:
            return
        else:
            # suppress reference to the orectangle object
            del self.orectangle
            # get the current layer
            current_layer = self.getGeoSelectionMapCanvas().layer(0)
            # print current_layer.name()
            current_layer.removeSelection()
            #remove the rubber band
            self.getGeoSelectionMapCanvas().scene().removeItem(self.rubberband)

            #restart a selection session
            self.geoSelect()

    def geoPoly(self):
        # init the Map tool through the setMapTool public method
        # print type(self.getGeoSelectionMapCanvas())
        self.mytool = QgsMapToolSelectPolygon( self.getGeoSelectionMapCanvas() )
        
        self.getGeoSelectionMapCanvas().setMapTool(self.mytool)
        pass

    def geoSelect(self):
        """
        This method instaciate a QgsRectangle and his associated vertex list
        """
        try:
            self.orectangle
            # another rectangle has already been selected
            QMessageBox.about(
                self, "Attention - Action déjà en cours" , "Un rectangle a déjà été dessiné ou est déjà en cours de selection; Selectionner l'outil de remise à zéro sivous désirez redéfinir la zone de selection")
            return
        except:
            pass
            

        # Give a custom rectangle from polygon4Qgis
        self.orectangle = ORectangle()
        

        # Define a map tool of type QgsMapToolEmitPoint
        self.tool_clickPoint = QgsMapToolEmitPoint(
            self.getGeoSelectionMapCanvas())

        # init the Map tool through the setMapTool public method
        self.getGeoSelectionMapCanvas().setMapTool(self.tool_clickPoint)
        
        # connect the clicked signal the the rectangle construction
        self.tool_clickPoint.canvasClicked.connect(self.selectFromRectangle)

    def setRectangle(self, point, button):
        """
        This method Build a rectangle whenever two point have been selected over 
        the map canvas  
        """

        if (len(self.orectangle.pointList) < 2):
            # print "ajouter un point"
            self.orectangle.pointList.append(QgsPoint(point))
            # print len(self.orectangle.pointList)

        if (len(self.orectangle.pointList) == 2):
            
            #Remove the map tool action
            self.toolButtonSelect.setEnabled(False)
            self.toolButtonDestruct.setEnabled(True)
            
            self.getGeoSelectionMapCanvas().unsetMapTool(self.tool_clickPoint)
            
            self.orectangle.selection_rectangle = QgsRectangle(
                self.orectangle.pointList[0], self.orectangle.pointList[1])
            # print selection_rectangle.asWktCoordinates(),
            # print self.orectangle.selection_rectangle.width()               
            self.orectangle.pointList = list()
            # True = a polygon
            self.rubberband = QgsRubberBand(self.getGeoSelectionMapCanvas(), True)
            self.rubberband.setWidth(3)

            self.rubberband.setToGeometry(
                QgsGeometry.fromRect(self.orectangle.selection_rectangle), None)

            return self.orectangle.selection_rectangle

    def selectFromRectangle(self, point, button):
        """
        This method register the selection rectangle as an Oprojetc self.ZC
        for future reference
        Also make a selection over the current layer and highlight what have been selected
        """
        # define rectangle*

        select_rect = self.setRectangle(point, button)
        if (select_rect != None):
            
            # Store the selection rectangle as a
            Global.getOproject().ZC = select_rect

            # get the current layer
            current_layer = self.getGeoSelectionMapCanvas().layer(0)
            # print current_layer.name()
            current_layer.select(select_rect, True)
            # destruct QgsRectange used for selection
            del select_rect
            
    def selectLayer(self):
        # print "selected"
        # print self.comboBox_listPGtables.currentText()
        _wkt = Global.dict_form_pre[self.comboBox_listPGtables.currentText()]
        
        if _wkt == "":
            return

        self.geoSelect()
        self.getGeoSelectionMapCanvas().unsetMapTool(self.tool_clickPoint)

        # Store the selection rectangle as a
        select_rect = QgsGeometry.fromWkt(_wkt)
        

        Global.getOproject().ZC = select_rect
        # print Global.getOproject().ZC.asPolygon()


        

    def getGeoSelectionMapCanvas(self):
        return self.map_canvas

    def add_postgis_layer(self, uri_path):

        layer = QgsVectorLayer(
            uri_path, "layer_selection_geographique", "postgres")

        self.layerId = layer.id()
        Global.getOproject().dummyLayerId = layer.id()
        
        
        #keep the crs handy
        Global.getOproject().setCcrs(layer.crs().authid())
        
        
        
        self.ccrs = layer.crs().authid()
        self.mapinstance.addMapLayer(layer)
        canvas_layer = QgsMapCanvasLayer(layer)
        
        self.map_canvas.setLayerSet([canvas_layer])

    def remove_postgis_layer(self, layerID):

        self.mapinstance.removeMapLayer(layerID)
        pass
    

class ZRselection2(object):

    '''
    this class encapsulate all software/user interaction required to perform a ZR selection
    over the Extracted Project Database
    '''
    #-------------------------------------------------------------------------
    #-------------------------ALL CONNECTION DEFINED HEREAFTER----------------
    #-------------------------------------------------------------------------

    def setupAction_ZRselection2(self, *args):
        """
        Give action to the ZR Window
        Connect Signals -> Slots
        """
        

        #======================================================================
        # Action: Accept; discard; Browse...
        #======================================================================
        # Signal sur ComboBox
        self.connect(
            self.comboBox_listPGtables, SIGNAL("currentIndexChanged(int)"), self.selectLayer)
        self.connect(
            self.toolButtonPoly, SIGNAL("clicked()"), self.geoPoly)
        self.connect(
            self.buttonBox, SIGNAL("accepted()"), self.completeSelect)
        self.connect(
            self.buttonBox, SIGNAL("rejected()"), self.completeSelect)
        self.connect(
            self.rechercheParNom, SIGNAL("textEdited(QString)"), self.setMotifReconciliation)
        self.connect(
            self.pushButton_new, SIGNAL("clicked()"), self.newZR)
       

        
        #======================================================================
        # Populate ComboBox
        #======================================================================
        self.comboBox_listPGtables.clear()
        self.comboBox_listPGtables.addItems(Global.liste_motif)
        
        #Nothing has been changed yet!
        self.motifedited  = False  
        self.selectedmotif = False
       
    #-------------------------------------------------------------------------
    #-------------------------ALL SLOT ARE DEFINE BELOW-----------------------
    #-------------------------------------------------------------------------
    
    def newZR(self):
        """s
        give control if geopoly is not running
        """

        #refresh the map canvas;
        QgsMapLayerRegistry.instance().reloadAllLayers()
        qgis.utils.iface.mapCanvas().refresh()
        qgis.utils.iface.mapCanvas().zoomToFullExtent()
        
        self.toolButtonPoly.setEnabled(True)



    def setMotifReconciliation(self):
        """
        Allow to add a comment to the current ZR being build
        """
        #keep reference that a modification occured
        self.motifedited = True

    def abortSelect(self):
        """
        Exit
        """
        #=======================================================================
        # do nothing but close the windows
        #=======================================================================
         
        self.close()
        
    def completeSelect(self):
        """
        Save State and exit      
        """

        #=======================================================================
        # Update the shelve
        #=======================================================================

        copy_oproject = copy.deepcopy(Global.getOproject())
        self.writeProjectShelf(copy_oproject)

        #=======================================================================
        # clean project
        #=======================================================================
        #Get project reference
        qproject = QgsProject.instance()
        # Save the project
        qproject.write()

        self.close()
            
    def geoDestruct(self):
        """
        This method reset the current selection rectangle
        """
        #Return if nothng has been set
        try:
            self.orectangle
        except NameError:
            return
        else:
            # suppress reference to the orectangle object
            del self.orectangle
            # get the current layer
            current_layer = self.getGeoSelectionMapCanvas().layer(0)
            # print current_layer.name()
            current_layer.removeSelection()
            #remove the rubber band
            self.getGeoSelectionMapCanvas().scene().removeItem(self.rubberband)

            #restart a selection session
            self.geoSelect()


    def geoPoly(self):

        # init the Map tool through the setMapTool public method
        self.canvas = qgis.utils.iface.mapCanvas()
        #set oproject to dirty state

        try:

            vZRlayer = OQgis.selectAlayerByName('ZR')

            iterator = vZRlayer.getFeatures()
            idx = vZRlayer.fieldNameIndex('indexZR')
            index_ZR = 0                 
            for feat in iterator:
                        
                if feat.attributes()[idx] > index_ZR:
                    index_ZR = feat.attributes()[idx]
                else:
                    continue

            if Global.getOproject().ZRtriggercount < index_ZR:
                #correct to right value
                # print  Global.getOproject().ZRtriggercount , index_ZR
                Global.getOproject().ZRtriggercount = index_ZR

                    
                    
            else:
                # print "CLEAN!"
                pass

        except:
            #first ZR to be recorded
            pass 
      

        #remove control to avoid indexing error
        self.toolButtonPoly.setEnabled(False)
        self.pushButton_new.setEnabled(True)

       
        #Pass the right "motif" description for the current ZR
        if self.motifedited and not self.selectedmotif:
            _motif =  self.rechercheParNom.text()
        if self.motifedited and self.selectedmotif:
            #concatenation 
            _motif = self.rechercheParNom.text()+" / "+self.comboBox_listPGtables.currentText()
        if not self.motifedited and self.selectedmotif:
            _motif = self.comboBox_listPGtables.currentText()
        if not self.motifedited and not self.selectedmotif:
            _motif = "motif omis"


        self.mytool = QgsMapToolSelectPolygon( self.canvas, _motif )
        self.canvas.setMapTool(self.mytool)

        
        #Reset!
        self.motifedited  = False
        self.rechercheParNom.setText("")
        self.selectedmotif = False
        self.comboBox_listPGtables.setCurrentIndex (0)

        qgis.utils.iface.mapCanvas().refresh()

   
            
    def selectLayer(self):
        #keep reference that an item has been selected
        self.selectedmotif = True
        


    def writeProjectShelf(self, oproject):

        

        # Test if the shelf is already open/needs to be open
        os.chdir(oproject.currentProjectPath)
        shelve_project_parameters = shelve.open('shelf_PP.db', writeback=True)

        # Construct the shelve:
        #try:
        shelve_project_parameters['object'] = oproject
        
        #finally:
        shelve_project_parameters.close()

        # print "Project Shelved!"
        

class ConnectionParameters(object):
    '''
    this class encapsulate all software/user interaction required to set/accept connection parameters
    '''

    #-------------------------------------------------------------------------
    #-------------------------ALL CONNECTION DEFINED HEREAFTER----------------
    #-------------------------------------------------------------------------

    def setupAction_connectionParameters(self):
        
        
        #======================================================================
        # Populate ComboBox if connection has been granted!
        #======================================================================
        #try if connection exists
        try:            
            dblist = Global.getPG_connection().databaselist
            #keep reference for this instance
            connect_granted = True
            #add a dummy entry to the list
            if dblist[0] != "--Choix--":
                dblist.insert(0, "--Choix--")
            self.comboBox_listDB.clear()
            self.comboBox_listDB.addItems(
                                          dblist)
        except:
            #connection has been refused
            connect_granted = False
            #Update is mandatory
            self.pushButton_Valid.setEnabled(False)
            self.comboBox_listDB.setEnabled(False)

        try:
            if not Global.connectionstatus:
                self.pushButton_Valid.setEnabled(False)
        except:
            pass
        #======================================================================
        # Signal sur ComboBox
        #======================================================================
        self.connect(
            self.comboBox_listDB, SIGNAL("currentIndexChanged(int)"), self.selectDb)
        
        #======================================================================
        # Button action valid or Update connection parameters
        #======================================================================
        self.connect(
            self.pushButton_Valid, SIGNAL("clicked()"), self.accept)
        self.connect(
            self.pushButton_Update, SIGNAL("clicked()"), self.update2)
        self.connect(
            self.pushButton_Cancel, SIGNAL("clicked()"), self.accept)
        self.connect(
            self.editUserName, SIGNAL("textEdited(QString)"), self.edit)
        self.connect(
            self.editHostName, SIGNAL("textEdited(QString)"), self.edit)
        self.connect(
            self.editBDName, SIGNAL("textEdited(QString)"), self.edit)
        self.connect(
            self.editBDName, SIGNAL("textChanged(QString)"), self.edit)
      
        

    #-------------------------------------------------------------------------
    #-------------------------ALL SLOT ARE DEFINE BELOW-----------------------
    #-------------------------------------------------------------------------
    def selectDb(self):
        """
        Slot to allow selection within the db list
        index 0 is a dummy text value that cannot be selected
        """
        i = self.comboBox_listDB.currentIndex()
        if i !=0:
            self.editBDName.setText(self.comboBox_listDB.currentText())
            
    def accept(self):
        """
        Accept default connection parameter from "Global"
        """
        if Global.BDname != 'postgres':
            #give control to the main windows
            Global.getMw().setEnabled(True)
            #bring the main window on top of its parent window stack
            Global.getMw().raise_()
           
            self.close()
        else:
            QMessageBox.about(None, "Erreur", u"Veuillez choix une base de donnée valide dans la liste déroulante ci-dessous") 
        
    def update2(self):
        """
        Reinit Connection parameters
        Reinit the connection object
        """
        
        # Update global var
        Global.setUserName(str(self.editUserName.text()))
        Global.setBDname(str(self.editBDName.text()))
        Global.setHostName(str(self.editHostName.text()))

        #Re-init conection with updated values
        Global.getPG_connection().reinit(Global.getUserName(), Global.getBDname(),"", Global.getHostName(), 5432)
  
       
        try:
            dblist = Global.getPG_connection().databaselist
            #Enable the mainwindow
            #Global.getMw().setEnabled(True)
        except:
            pass



        self.close()
    
        
    def edit(self):
        self.pushButton_Update.setEnabled(True)
        #self.pushButton_Cancel.setEnabled(True)
        #Update is required if any edition has been done to avoid user confusion
        self.pushButton_Valid.setEnabled(False)
        

class QgsMapToolSelectPolygon(QgsMapToolEmitPoint):
    """
    Define a custom Map tool that Allow Polygonal Selection over a QgsMapCanvas and udpdate the selected database Field:
    column 'ZRlocal' set to the current ZR sequence number
    Write to Disk  
    !! Interface with SPATIALITE DB !!
    Install/Update specific spatial request triggers
    """
    
    trigger = QtCore.pyqtSignal()
    trigger2 = QtCore.pyqtSignal()



    def __init__(self,canvas, *args):
        """
        Keyword parameter:
        canvas -- qgis.gui.QgsMapCanvas
        """
        
        self.map_canvas = canvas
        self.widg = MyCustomWidget2()
        
        #check if there is a decritption passed for this Polygon
        if args:
            self.motif = unicodedata.normalize('NFKD', unicode(args[0])).encode('ascii','ignore')
            
            #pyspatialite no support for quote "'"
            self.motif = self.motif.replace("'"," ")
            # print self.motif


        super(QgsMapToolSelectPolygon, self).__init__( self.map_canvas)
        
        #Custom connector for custom signal - abandonned!
        #Kept for further reference
        # self.connect(
        #     self, SIGNAL("trigger()"), self.startMessage)
        # self.connect(
        #     self, SIGNAL("trigger2()"), self.endMessage)
        

        
        self.rubberBand = None;
        self.isEmittingPoint = False
        self.cursor = QCursor(QtCore.Qt.CrossCursor)
        self.FillColor = QColor(  254, 58, 29, 100 )
        self.BorderColor = QColor( 254, 58, 29, 100 )
     

    def startMessage(self):
        """
        Slot function to start QgsMessageBar as a thread 
        abandonned
        """

        t1 = Function_threader(self.processReferencement)
        t1.start()
        print "thread started"
        t1.join() 
        print "thread completed"

        # self.widg.start()
        # self.widg.show()
        # QApplication.processEvents()
        #  #Load the layer within QGIS
       

    def endMessage(self):
        """
        Slot function to end QgsMessageBar as a thread 
        abandonned
        """

        # self.widg.close()

        # self.readyMessageBar = qgis.utils.iface.messageBar()
        # self.readyMessageBar.pushMessage("Référencement Complet", u"Les Objets édités dans la ZR ont été correctement référencé pour reconciliation", level= QgsMessageBar.INFO, duration=10)


    def canvasPressEvent(self, _qMouseEvent):
        """
        Define Polygon selection behaviour from mouse Actions
        Add a ZR to the Corresponding Table; update the displayed layer
        Keyword parameter:
        _qMouseEvent -- PyQt4.QtGui QMouseEvent
        """
        

        #No selection has been set yet; construct the rubberband
        if self.rubberBand == None:
            #Instanciate a rubberBand; Attach it to the canvas
            #True -> QGis::Polygon
            self.isEmittingPoint = True
            self.rubberBand = QgsRubberBand(self.map_canvas, True)
            self.rubberBand.reset(QGis.Polygon)
            self.rubberBand.setColor(self.FillColor)
            #self.rubberBand.setBorderColor(self.setBorderColor)

            #Connect to the ZR DB to save the selection polygon
            rt  = LocalDB_utils.connect2LocalDb( "ZR", Global.getOproject().currentProjectPath ) 
            self.ZRcursor = rt[0]
            self.ZRconn = rt[1]
        #Define Left Button action
        if _qMouseEvent.button() == QtCore.Qt.LeftButton:
            
            self.rubberBand.addPoint( self.toMapCoordinates( _qMouseEvent.pos() ), True )
            self.rubberBand.show()
        #else = If Right click
        else:
            #close polygon if at least 3 point have been recorded

            if self.rubberBand.numberOfVertices() > 2:

               

                self.polygonGeom = QgsGeometry( self.rubberBand.asGeometry() )
                #make a temporary reference to the current ZR 
                # Global.getOproject().tmpZR = self.polygonGeom


                #Check if the Geometry intersect/overlap another ZR
                try:
                    #Try mandatory as ZR might not exist for the first pass at project creation
                    vZRlayer = OQgis.selectAlayerByName('ZR')
                    
                    iterator = vZRlayer.getFeatures()
                    idx = vZRlayer.fieldNameIndex('geom')
                    idx2 = vZRlayer.fieldNameIndex('indexZR')
                                        
                    for feat in iterator:
                        
                        attrs_geom = feat.attributes()[idx]
                        fid = feat.attributes()[idx2]
                        
                        if feat.geometry().intersects(self.polygonGeom):
                            #not authorized to draw intersectng ZR
                            QMessageBox.about(
                                None, "Erreur", u"La Zone dessinée  intersecte la Zone %s prééxistante, veuillez redefinir une nouvelle zone" %(fid))
                            #unset the polygon selectionmap tool
                            qgis.utils.iface.mapCanvas().unsetMapTool(self)  
                            self.rubberBand.reset(QGis.Polygon)
                            return
                        else:
                            continue
                except:
                    #Project creation; ZR has not been build to the project yet
                    pass
                
                
                #Update the trigger counter
                Global.getOproject().ZRtriggercount = Global.getOproject().ZRtriggercount + 1
                self.trigcount = Global.getOproject().ZRtriggercount
                _trigcount = str(self.trigcount)               
                #Write the polygon and it's descrption
                _sqlstatement = "INSERT INTO ZR (geom, description, indexZR) VALUES (GeomFromText('"+str(self.polygonGeom.exportToWkt())+"',"+Global.getOproject().getSrid()+"), '"+self.motif+"','"+_trigcount+"')"
                #_sqlstatement = u"INSERT INTO ZR (geom, description) VALUES (GeomFromText('%s',%s), '%s')" %(str(self.polygonGeom.exportToWkt()), str(Global.getOproject().getSrid()), str(self.motif))
                # print _sqlstatement
                LocalDB_utils.SQLinjection(self.ZRcursor, str(_sqlstatement), False)
                self.ZRconn.commit()
                self.ZRconn.close()

                # Emit a custom signal.
                # self.trigger.emit()
                # processReferencement as a thread - Abandonned not compatible with PyQGIS+PyQT
                # t1 = Function_threader(self.processReferencement)
                # t1.start()


                self.processReferencement()
                self.updateTableObject()
                self.checkZRlayer()

                #=======================================================================
                # Update the shelve
                #=======================================================================

                copy_oproject = copy.deepcopy(Global.getOproject())
                self.writeProjectShelf(copy_oproject)


    def writeProjectShelf(self, oproject):

        # Test if the shelf is already open/needs to be open

        shelve_project_parameters = shelve.open('shelf_PP.db')

        # Construct the shelve:
        try:
            shelve_project_parameters['object'] = oproject
        
        finally:
            shelve_project_parameters.close()

                          
    def processReferencement(self):
        """
        Update/install new triggers to the underlying local Sqlite DB
        - Complete/create the MoveOutOfZR_trig
        - Create additional MoveInsideZR_trig
        """

        for key in Global.getOproject().tableDict.keys():
                    
            rt2 = LocalDB_utils.connect2LocalDb( key, Global.getOproject().currentProjectPath ) 
            self.ZRcursor2 = rt2[0]
            self.ZRconn2 = rt2[1]
            
            geom1 = "GeomFromText('"+str(self.polygonGeom.exportToWkt())+"',"+Global.getOproject().getSrid()+")"
            geom2 = "new.GEOMETRY"

            

            #Tr if the MoveOutOf ZR trigger already exists
            _sqlstatement = "Select sql from sqlite_master WHERE type='trigger' and name='MoveOutOfZR_trig'"
            sqlcode_list = LocalDB_utils.SQLinjection(self.ZRcursor2, str(_sqlstatement), True)
            try:
                #if exists
                sqlcode = str(sqlcode_list[0][0])
               
                #Prepare String for concat. remove tailin "; END"
                old_sqlcode = sqlcode[:len(sqlcode)-5]
                #Add the new spatial request to the original trigger
                _additionalcode = " AND (NOT st_intersects("+str(geom1)+","+str(geom2)+") AND rowid = new.rowid); END;"
                new_sqlcode = old_sqlcode + _additionalcode 
                # print new_sqlcode
                #Drop previous trigger
                LocalDB_utils.SQLinjection(self.ZRcursor2, "DROP TRIGGER MoveOutOfZR_trig;",False)
                #Reimplant trigger
                LocalDB_utils.SQLinjection(self.ZRcursor2, str(new_sqlcode), False)
                self.ZRconn2.commit()

            except:
                _sqlstatement = "CREATE TRIGGER MoveOutOfZR_trig"
                _sqlstatement = _sqlstatement +" AFTER UPDATE ON "+key+" BEGIN UPDATE "+key+" SET userMod=1, ZRlocal = -666"
                _sqlstatement = _sqlstatement +" WHERE (NOT st_intersects("+str(geom1)+","+str(geom2)+")"
                _sqlstatement = _sqlstatement + " AND rowid = new.rowid); END;"
                # print key
                # print _sqlstatement
                LocalDB_utils.SQLinjection(self.ZRcursor2, str(_sqlstatement), False)
                self.ZRconn2.commit()
            #===========================================================
            # 3. Trigger when Object Modification - Check if Object has been moved INSIDE a ZR
            #===========================================================

            _sqlstatement = "CREATE TRIGGER MoveInsideZR_trig"+str(Global.getOproject().ZRtriggercount)
            _sqlstatement = _sqlstatement +" AFTER UPDATE ON "+key+" BEGIN UPDATE "+key+" SET ZRlocal = "+str(Global.getOproject().ZRtriggercount)
            #If the current feature geometry is not null
            _sqlstatement = _sqlstatement +" WHERE isEmpty("+geom2+") = 0 AND st_intersects("+str(geom1)+","+str(geom2)+")"
            _sqlstatement = _sqlstatement + " AND rowid = new.rowid; END;"
            
            # print _sqlstatement
            LocalDB_utils.SQLinjection(self.ZRcursor2, str(_sqlstatement), False)
            self.ZRconn2.commit()

            self.ZRcursor2.close()
            self.ZRconn2.close()
            
           
        #unset the polygon selectionmap tool
        qgis.utils.iface.mapCanvas().unsetMapTool(self)  

        try:
            vZRlayer = OQgis.selectAlayerByName('ZR')
            vZRlayer.triggerRepaint()
        except:
            pass

    def updateTableObject(self):
        """
        Check All object from All Layers if Inside the new ZR Polygon
        Required to load the underlying Spatialite DB to make use of 
        specificity of the spatialite data provider.
        """
        #===============================================================
        # Check All object from All Layers if Inside the new ZR Polygon
        # Required to load the underlying Spatialite DB to make use of 
        # specificity of the spatilaite data provider.
        #===============================================================
        #For all layer loaded within the map_canvas
        layers =  Global.getOproject().tableDict.keys()
        
        for layername in layers:
            #Set a specfic progress bar for each layer

            
            uri = QgsDataSourceURI()
            vlayerpath = os.path.join(Global.getOproject().currentProjectPath, 
                layername+".sqlite")
            uri.setDatabase(vlayerpath)
            schema = ''
            table = layername
            geom_column = 'GEOMETRY'
            uri.setDataSource(schema, table, geom_column)
            
            vlayer = QgsVectorLayer(uri.uri(),
                 layername, 'spatialite')

            
            
            caps = vlayer.dataProvider().capabilities()
            #if vlayer is capable of edition
            if caps & QgsVectorDataProvider.ChangeAttributeValues:
                

                #if it exists a ZRlocal Field
                if vlayer.fieldNameIndex('ZRlocal') != -1:


                    # print vlayer.name(), 'Update ZR'                          
                    #Perform spatial selection
                    vlayer.selectAll()

                  

                    #feature = QgsFeature()
                    for feature in vlayer.selectedFeatures():
                       

                        if feature.geometry() == None:
                            # print "geometry error!!!"
                            continue
                        
                        if feature.geometry().intersects(self.polygonGeom):
                            fid = feature.id()
                            #SET ZRlocal to the current ZR number
                            idx = vlayer.fieldNameIndex('ZRlocal')
                            idx2 = vlayer.fieldNameIndex('ZRnew')
                            
                            #check if feature has previously been modified
                            idx3 = vlayer.fieldNameIndex('userMod')
                            val = feature.attributes()[idx3]

                            #Decide wether to Update or not the ZRnew field (Variable required
                            #to control trigger execution withinthe local SQLite DB
                            if val == 1:
                                #the ZRnew field shoul be left unmodified to keep it referenced as a modified item by the userMod trigger 
                                attr ={idx:Global.getOproject().ZRtriggercount}
                            else:
                                #set both Fields if the features nevers has been modified by the user
                                attr ={idx:Global.getOproject().ZRtriggercount, idx2:2}


                            # print vlayer.dataProvider().name(), fid,idx,attr
                            vlayer.dataProvider().changeAttributeValues({fid:attr})
                            

                else:
                    # print vlayer.name(), 'NO UPDATE'  
                    pass
     

        #Finish the ZR polygon and reset Qgis rubberband
        self.rubberBand.reset(QGis.Polygon)
        #del self.rubberBand
        self.rubberBand = None
        # #discard polygon
        del self.polygonGeom



    def checkZRlayer(self):
        """
        Refresh the registry and mapcanvas
        Check if required to Load ZR layer within the project
        """

        # print "Check ZR layer"
        for key in QgsMapLayerRegistry.instance().mapLayers().keys():
            QgsMapLayerRegistry.instance().mapLayer(key).reload()
        
        qgis.utils.iface.mapCanvas().zoomToFullExtent()

        #test if ZR is already part of the map registry
        for key in QgsMapLayerRegistry.instance().mapLayers().keys():
            if QgsMapLayerRegistry.instance().mapLayer(key).name() == 'ZR':
                # Emit the signal.
                # self.trigger2.emit()
                return


        #ZR layer need to be added to the map registry 
        self.add2Registry()
        # Emit the custom end signal - abandonned
        # self.trigger2.emit()
        
    def canvasMoveEvent(self, _qMouseEvent):
        """
        Draw the rubberband when moving the mouse
        """
        if self.rubberBand == None:
            return
        if self.rubberBand.numberOfVertices() >= 2:
            self.rubberBand.removeLastPoint( 0 )
            self.rubberBand.addPoint( self.toMapCoordinates( _qMouseEvent.pos() ) )
    
    def poly(self):
        """
        return  polygon
        """
        if self.rubberBand != None:
            if self.rubberBand.numberOfVertices() > 2:
                return self.polygonGeom 
        else:
            return
        
    def add2Registry(self):
        """
        Add or refresh the map registry
        """
        
        #=======================================================================
        # Add to registry
        #=======================================================================1
        vlayerpath = os.path.join(
                    Global.getOproject().currentProjectPath, "ZR.sqlite")
        vlayer = QgsVectorLayer(vlayerpath, "ZR", "ogr")
    
              
        if vlayer.isValid():
            # print "sqllayer succesfully loaded - adding to mapinstance"
            QgsMapLayerRegistry.instance().addMapLayer(vlayer)
            #Global.getOproject().mapinstance.addMapLayer(vlayer)
            
            #=======================================================================
            # set Custom Style for the ZC layer:
            #=======================================================================
            #get memory layer provider
            pr = vlayer.dataProvider()
            vlayer.startEditing()
            #Set the renderer
            myColour = QColor('#ff6f00')
            myOpacity = 0.25
            #define the Single Symbol associated with the layer
            mySymbol1 = QgsSymbolV2.defaultSymbol(
               vlayer.geometryType())
            mySymbol1.setColor(myColour)
            mySymbol1.setAlpha(myOpacity)
            
            myRenderer = QgsSingleSymbolRendererV2(mySymbol1)
            vlayer.setRendererV2(myRenderer)
            vlayer.commitChanges()
            
    
            canvas_layer = QgsMapCanvasLayer(vlayer)
            canvas = QgsMapCanvas()
            canvas.setLayerSet([canvas_layer])
        else:
            # print "sqllayer failed to load!"
            pass
        
        # Make reference to the QGIS project view
        qproject = QgsProject.instance()
        # Save the project
        qproject.write()

    def showPoly(self):
        self.rubberBand.show()
                

class ZrDestroy(object):
    '''
    this class encapsulate all software/user interaction required to remove specific ZR from project
    All connected local database to the current project will be updated
    Object will be re-referenced regarding to the new ZR map
    Corresponding Database triggers will be removed
    '''
    #-------------------------------------------------------------------------
    #-------------------------ALL CONNECTION DEFINED HEREAFTER----------------
    #-------------------------------------------------------------------------

    def setupAction_ZRdestroy(self, *args):
        """
        Give action to the ZRdestroy Window
        Connect Signals -> Slots
        """
        #======================================================================
        # Action: Accept; discard; Browse...
        #======================================================================
        self.connect(
            self.pushButton_2, SIGNAL("clicked()"), self.completeSelect)
        self.connect(
            self.pushButton, SIGNAL("clicked()"), self.abortSelect)
        self.connect(
             self.tableWidget, SIGNAL("itemClicked(QTableWidgetItem*)"), self.handleItemClicked)
        #Keep next line for reference : New style for managing handler
        #self.tableWidget.itemClicked.connect(self.handleItemClicked)

        #Make reference to QGIS main objects
        self.mapinstance = QgsMapLayerRegistry.instance()
        self.qproject = QgsProject.instance()
        #Retrieve the project Path from the QgsProject instance
        try:
            project_path = self.qproject.homePath()
            #Rebuild the current folder path
            shelve_path = os.path.join(
                str(project_path), "current/shelf_PP.db")
            current_path = os.path.join(
                str(project_path), "current")
            tmp_path = os.path.join(
                str(project_path), "shelve.db")      

            #======================================================================
            #Rebuild Oproject instance from shelf
            #======================================================================
           
            shelve_p = shelve.open(shelve_path,  writeback=True)
            self.oproject = shelve_p['object']

            Global.setOproject(self.oproject)
            self.loaded = True

            #======================================================================
            # make local reference on the vector Layer
            #======================================================================
            layers = QgsMapLayerRegistry.instance().mapLayers().keys()
            for layer in layers:
                if QgsMapLayerRegistry.instance().mapLayer(layer).name() != 'ZR':
                    continue
                else:
                    #make temporary reference on the displayed ZR layer
                    self.ZRlayertmp = QgsMapLayerRegistry.instance().mapLayer(layer)
                    break


            #======================================================================
            # Populate the tableWidget and give checkboxes
            #======================================================================
            #Make reference to QGIS main objects
            self.mapinstance = QgsMapLayerRegistry.instance()
            self.qproject = QgsProject.instance()
            #Retrieve the project Path from the QgsProject instance

            project_path = self.qproject.homePath()
            #Rebuild the current folder path
            current_path = os.path.join(
                str(project_path), "current")

            ###########################################
            #make connection to the underlying database
            ###########################################
            uri = QgsDataSourceURI()
            vlayerpath = os.path.join(current_path, 
                            "ZR.sqlite")
            uri.setDatabase(vlayerpath)
            schema = ''
            table = 'ZR'
            geom_column = 'geom'
            uri.setDataSource(schema, table, geom_column)
                        
            vlayer = QgsVectorLayer(uri.uri(),
                    'ZR', 'spatialite')
            self.ZRlayer = vlayer
            self.ZRlayer.selectAll()
            numberRows = int(self.ZRlayer.selectedFeatureCount())
            self.ZRlayer.invertSelection()


            ###########################################
            #Count features (number of ZR)
            # numberRows = int(self.ZRlayer.featureCount())
            print numberRows
            if numberRows ==0:
                return
            ###########################################
            #set the fidlist;
            indexmax = -1 
            for feature in self.ZRlayer.getFeatures():
                if feature.id() > indexmax:
                    indexmax = feature.id()


            for i in range(indexmax):
                self.fidlist.append(False)

            ###########################################
            #Prepare an additional column for description
            ###########################################
            numberColumns = 3
            
            self.tableWidget.setRowCount(numberRows)
            self.tableWidget.setColumnCount(numberColumns)
            ###########################################
            #prepare value to be inserterted within the Qtablewidget
            ###########################################
            self.tab = []
            iterator = self.ZRlayer.getFeatures()
            idx = self.ZRlayer.fieldNameIndex('description')
            idx2 = vlayer.fieldNameIndex('indexZR')
                                        
            for feat in iterator:
                
                attrs = feat.attributes()[idx]
                fid = feat.attributes()[idx2]
                fid2 = int(feat.id())
                self.tab.append([fid2, fid, attrs])

            ###########################################
            #fill the table
            ###########################################
            for rowNumber in range(numberRows):
                for columnNumber in range(numberColumns):
                    item = QTableWidgetItem("{0}       ".format(self.tab[rowNumber][columnNumber]))
                    if columnNumber == 0:
                        item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
                        item.setCheckState(QtCore.Qt.Unchecked)

                    self.tableWidget.setItem(rowNumber, columnNumber, item)
                    
                    #self.tableWidget.setItem(rowNumber, columnNumber, item)
            ###########################################
            #reset table geometry
            ###########################################
            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.verticalHeader().setVisible(False)
            self.tableWidget.setHorizontalHeaderLabels([' ','index ZR', 'description'])
        except:
            self.loaded = False
        
        
        
    #-------------------------------------------------------------------------
    #-------------------------ALL SLOT ARE DEFINE BELOW-----------------------
    #-------------------------------------------------------------------------
    def handleItemClicked(self,item):
        """
        Slot/handler for Qtablewidget Signal "itemClicked"
        Test Check state of the underlying QTableWidgetItem
        Build a FID list of the selected features
        """
        try:
            #check for checkState and select/unselect feature
            if item.checkState() == QtCore.Qt.Checked:
                # print('"%s" Checked' % item.text())
                # print int(item.text())
                #selected the corresponding feature based on fid correspondance
                self.ZRlayertmp.select(int(item.text()))

                #-1 because there is no 0 index for fid
                # print int(item.text()) - 1, len(self.fidlist)
                self.fidlist[int(item.text()) - 1] = True
                # print self.fidlist

            else:
                #unselect feature
                self.ZRlayertmp.deselect(int(item.text()))
                #-1 because there is no 0 index for fid
                self.fidlist[int(item.text()) - 1] = False
                # print self.fidlist
        except:
            # print "pass"
            pass

    def completeSelect(self):
        """
        Suppress features based on the fidlist boolean index
        Act directly on the underlyng DB rather than on the loaded QgsVectorLayer
        - Delete Object
        - Update Triggers:
            remove corresponding ZRmoveIN_xxx trigger (see QgsMapToolSelectPolygon.canvasPressEvent )
        - Recalculate Wether DB object need to have their ZRlocal field updated
        """

        caps = self.ZRlayer.dataProvider().capabilities()
        #if vlayer is capable of edition
        if caps & QgsVectorDataProvider.ChangeAttributeValues:
            for i in range(len(self.fidlist)):
                #True means to be deleted
                if self.fidlist[i]:
                    # print i
                    self.ZRlayertmp.deselect(i+1)
                    res = self.ZRlayer.dataProvider().deleteFeatures([i+1])
                    # print res
                    #=====================
                    # Update Triggers
                    #=====================
                    #rebuild Trigger index from tab
                    for j in range(len(self.tab)):
                        # print "J",  self.tab[j][0], "i", i
                        if self.tab[j][0] -1 == i:
                            trigx = self.tab[j][1]
                            break
                        else:
                            continue
                    
                    # print "DROP Trigger"+str(trigx)
                    self.drop_trigger(trigx)
                    #=========================
                    # Re-idenx affected object
                    #=========================
                    self.reindexObject(trigx)


                    #refresh the map:
                    qgis.utils.iface.mapCanvas().zoomToFullExtent()

        self.close()
        
    def reindexObject(self, index):
        """
        Recalculate the proper ZRlocal field
        """
        for key in Global.getOproject().tableDict.keys():
                    
            rt2 = LocalDB_utils.connect2LocalDb( key, Global.getOproject().currentProjectPath ) 
            self.cursor = rt2[0]
            self.conn = rt2[1]


            _sqlstatement  = "UPDATE "+key+" SET ZRlocal = -999, ZRnew = 2 WHERE ZRlocal ="+str(index)+" AND userMod = 0"
            _sqlstatement2 = "UPDATE "+key+" SET ZRlocal = -999, ZRnew = 1 WHERE ZRlocal ="+str(index)+" AND userMod = 1"
            LocalDB_utils.SQLinjection(self.cursor, str(_sqlstatement), False)
            LocalDB_utils.SQLinjection(self.cursor, str(_sqlstatement2), False)

            self.conn.commit()
            self.cursor.close()
            self.conn.close()


    def drop_trigger(self, index):
        """"
        Drop trigger MoveInside for a specific ZR
        """
        for key in Global.getOproject().tableDict.keys():
                    
            rt2 = LocalDB_utils.connect2LocalDb( key, Global.getOproject().currentProjectPath ) 
            self.cursor = rt2[0]
            self.conn = rt2[1]
            
            _sqlstatement = "DROP TRIGGER MoveInsideZR_trig"+str(index)

            LocalDB_utils.SQLinjection(self.cursor, str(_sqlstatement), False)
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

        


    def abortSelect(self):
        #unselect everything that could have been selected
        try:
            if self.ZRlayertmp.selectedFeatureCount () != 0:
                for feature in self.ZRlayertmp.selectedFeatures():
                    self.ZRlayertmp.deselect(feature.id())
        except:
            #Do nothing
            pass
        self.close()
 

class Function_threader(Thread):
    """
    Thread a function with arguments!
    """
    def __init__(self, target, *args):
        self._target = target
        self._args = args

        Thread.__init__(self)
    
    def run(self):
        self._target(*self._args)


class MyCustomWidget(QWidget, QtCore.QThread):
    """
    abandonned
    QMessage bar as a thread
    kept for further reference
    """

    def __init__(self, parent=None):
        super(MyCustomWidget, self).__init__(parent)
        layout = QVBoxLayout(self)

        # Create a progress bar and a button and add them to the main layout
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0,0)
        layout.addWidget(self.progressBar)

    def run(self):
        self.show()


class MyCustomWidget2(QtCore.QThread):
    """
    abandonned
    QMessage bar as a thread
    kept for further reference
    """
  

    def run(self):
        self.progressMessageBar = qgis.utils.iface.messageBar().createMessage("Référencement en cours...")
        self.progress = QProgressBar()
        self.progress.setRange(0,0)
        self.progressMessageBar.layout().addWidget(self.progress)
        qgis.utils.iface.messageBar().pushWidget(self.progressMessageBar, qgis.utils.iface.messageBar().INFO)
         
