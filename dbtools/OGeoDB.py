# -*- coding: utf-8 -*-
'''
Created on 17 juil. 2014
This module contains all tools required to interact with the database including:
- Browsing DB Metadata
- Performing SELECT/DELETE/UPDATE/....
- Error management
- ...
@author: pierre foicik
pierre.foicik@gmail.com
'''


from PyQt4 import QtCore
from PyQt4.QtCore import *

import qgis

import sys
import getpass
import os
import time
import psycopg2
import sqlite3
from pyspatialite import dbapi2 as db

from qgis.gui import QgsMapCanvas
from qgis.core import QgsDataSourceURI, QgsVectorLayer, QgsVectorFileWriter, QgsMapLayerRegistry, QgsMessageLog
from qgis.gui import QgsMapCanvasLayer, QgsMessageBar
from PyQt4.QtGui import (QProgressBar, QMessageBox)


from sig40.utils_sig40.ErrorMessage import errorMessage, errorConnection
from sig40.global_mod import Global




class DbError(Exception):

    def __init__(self, error):
        # save error. funny that the variables are in utf8, not
        self.msg = unicode(error.args[0], 'utf-8')
        self.a = error.args[0]
        if hasattr(error, "cursor") and hasattr(error.cursor, "query"):
            self.query = unicode(error.cursor.query, 'utf-8')
        else:
            self.query = None

    def __str__(self):
        if self.query is None:
            return self.msg.encode('utf-8')
        return self.msg.encode('utf-8') + "\nQuery:\n" + self.query.encode('utf-8')


class TableAttribute:

    """
    not in use yet
    """

    def __init__(self, row):
        self.num, self.name, self.data_type, self.char_max_len, self.modifier, self.notnull, self.hasdefault, self.default = row



class OQgis:

    """
    This Class contains all PyQGIS based function
    """
    @staticmethod
    def setTableEditType(vector_layer):
        """
        Set the predefined field values within the tables
        - immutable
        - calendar
        Set all table field to immutable if user is not allow to modified the table
        """
        try:
            # print "CHECK RIGHT"
            # print "CHECK RIGHT for user %s " %(Global.getOproject().username)
            #Check 

            _sql_statement = """SELECT has_table_privilege('%s', '%s', 'UPDATE, INSERT')""" %(Global.getOproject().username, str(vector_layer.name()) )
            print _sql_statement

            connection = PGDB_utils.staticConnection()
            cursor = connection.cursor()
            cursor.execute(_sql_statement)
            b =  cursor.fetchall()[0][0]


            if b:
                #this layer has some right
                # print "layer : ", vector_layer.name(), "has right to ", Global.getOproject().username
                pass
            else:
                print "layer : ", vector_layer.name(), "has NO right to ", Global.getOproject().username
                #then this layer is entirely immutable; no reconciliation will be attempted
                field_names = [field.name() for field in vector_layer.pendingFields() ]

                field_index = [vector_layer.fieldNameIndex(field) for field in field_names ]
                for f in field_index:
                    vector_layer.setEditType(f, QgsVectorLayer.Immutable)
                #Done - All field immutable
                return


            # #======================================================================================
            # # Not vlaid in case of privileges gestion throught role group
            # # Kept for further reference
            # #======================================================================================
            # _sql_statement = """select *"""
            # _sql_statement += """ from INFORMATION_SCHEMA.table_privileges"""
            # _sql_statement += """ WHERE table_name = '%s' AND grantee = (Select * from session_user) AND table_schema = 'public' and privilege_type IN ('INSERT')""" %(vector_layer.name())
        
            # # print _sql_statement
            # connection = PGDB_utils.staticConnection()
            # cursor = connection.cursor()
            # cursor.execute(_sql_statement)
            # items = list(cursor.fetchall())
            # # print items

            # if len(items) !=0:
            #     #this layer has some right
            #     pass
                
            # else:
            #     #then this layer is entirely immutable; no reconciliation will be attempted
                
            #     field_names = [field.name() for field in vector_layer.pendingFields() ]

            #     field_index = [vector_layer.fieldNameIndex(field) for field in field_names ]
            #     for f in field_index:
            #         vector_layer.setEditType(f, QgsVectorLayer.Immutable)

        except:
            print "TROUBLE TROUBLE"
            pass



        try:
            #set immutable field
            for field in Global.immutable_field:
                try:
                    #get field index
                    field_index = vector_layer.fieldNameIndex(field)
                    if field_index != -1:
                        # print "Layer %s, Field %s,  Field Index %s" %(str(vector_layer.name()), str(field), str(field_index))
                        #set the widget
                        vector_layer.setEditType(field_index, QgsVectorLayer.Immutable)
                except:
                    pass

            #set Calendar field
            for field in Global.calendar_field:
                try:
                    #get field index
                    field_index = vector_layer.fieldNameIndex(field)
                    if field_index != -1:
                        # print "Field Index Calendar %s" %(str(field_index))
                        #set the widget
                        vector_layer.setEditType(field_index, QgsVectorLayer.Calendar)
                        #Config the widget behaviour for Qgis > 2.2 !!!! only
                        vector_layer.setEditorWidgetV2Config(field_index, Global.calendar_field_config)
                        print vector_layer.editorWidgetV2Config(field_index)
                except:
                    pass

            # #for QGIS > 2.2
            # #set ValueMap field
            for field in Global.source_donnee_field:
                try:
                    #get field index
                    field_index = vector_layer.fieldNameIndex(field)
                    if field_index != -1:
                        print "Field Index ValueMap %s" %(str(field_index))
                        #set the widget
                        vector_layer.setEditType(field_index, QgsVectorLayer.ValueMap)
                        #Config the widget behaviour
                        vector_layer.setEditorWidgetV2Config(field_index, Global.source_donnee_field_config)
                except:
                    pass


        except:
            pass
            # print "ERROR setTableEditType"

    def getUri(self, table_list,schema, *args):
        """
        Build an URI -- PyQGIS.core.QgsDataSourceURI() -- to allow layer extraction as defined by the PyQGIS API
        keyword parameter:
        table -- a list of table, typed string 'tablename'
        *args -- optional argument, WKB or WKT object to build a spatially constrained sql request over our DB 
        Return:
        urilist -- A python list of all URI
        """

        #======================================================================
        # if it doesn't exist any ZC
        # if not Global.getOproject().ZC:
        #======================================================================

        #If *args is passed
        # thenrecord the session ZC to global variables

        # initialize empt uri list
        urilist = []
        #SET THE SQL WHERE CLAUSE
        try:
            Global.getOproject().setZC(str(args[0]))
            polygone = str(Global.getOproject().ZC)
            # QMessageBox.about(
            #      None, u"polygone" , str(polygone))
        except:
            Global.getOproject().setZC("")

        # retrieve layers
        for item in table_list:


            try:

                geom = str(item[1])

                # QMessageBox.about(
                #      None, u"Item" , str(item[0])+" "+str(item[1]))

                asql = "ST_INTERSECTS(" + geom + \
                    " , ST_GeomFromText('" + polygone + "', 2154) ) AND detruit = false"
                # HERE NEED TO SPECIFY the asql variable = WKB or WKT string
                # else, no spatial selection is attempted
               
            except:
                asql = ""

            uri = QgsDataSourceURI()
            uri.setConnection(
                self.host, str(self.port), self.dbname, self.user, self.passwd)
            uri.setDataSource(schema, item[0], item[1], asql)

            urilist.append(uri)
            # QMessageBox.about(
            #          None, u"Uri "+str(item[0])  , str(uri.uri()))

        return urilist

        #======================================================================
        # ZC already defined elsewhere
        # else:
        #     print "ZC already recorded"
        #     return
        #======================================================================

    def VectorlayerListBuilder(self, uri_list):
        """ 
        Build a list of QgsVectorLayer
        tables required to embed at least one geometry column 
        """

        layer_list = []

        if uri_list == None:
            # TODO generate empty layer
            return

        for item in uri_list:

            vlayer = QgsVectorLayer(
                item.uri(), str(item.table()), Global.dataProvider())
            self.setDisplayField(vlayer)
            layer_list.append(vlayer)
            # QgsMapLayerRegistry.instance().addMapLayer(vlayer)

           
        _available_layers = '\n '.join( "%s: %s "% (vl.name(), vl.isValid()) for vl in layer_list )
        QMessageBox.about(
                 None, u"Couches disponible" , _available_layers )

        return layer_list

    def WriteVectorLayer2Sqlite(self, layer):
        """
        1. write a QgsVectorLayer to a sqlite file DB
        2. Check for layer.featureCount() and keep track of this number within the project tableListWithGeom Dictionnary
        Abandonned - 3. Doesn't output a file if featurecount() is null
        Abandonned - 4. Remove entry for tableListWithGeomDict if featurecount() is null
        5. Write ONLY if checkState = .TRUE.

        # Write a SQLITE/SPATIALITE FILE
        # create an instance of vector file writer, which will create the vector file.
        # Arguments:
        # 1. QgsVectorLayer to write
        # 2. path to new file (will fail if exists already)
        # 3. encoding of the attributes
        # 4. layer's spatial reference (instance of
        #    QgsCoordinateReferenceSystem) - optional
        # 5. driver name for the output file
        # return static WriterError

        """



        # Check the check state for the layer, set @ geoselection  
        if Global.getPG_connection().tableListWithGeomDict[str(layer.name())][5]:
            error = QgsVectorFileWriter.writeAsVectorFormat(layer, layer.name() + ".sqlite",
                                                        "utf-8", None, "SQLite", False, None ,["SPATIALITE=YES",])
          
            


            if error == QgsVectorFileWriter.NoError:
                pass
                # print "success!"
       
            # #discard  empty layer -- Empty layer mean no SELECT was allowed at extraction time
            # #===============================================================================
            #     Global.getPG_connection().tableListWithGeomDict[str(layer.name())][
            #        3] = int(layer.featureCount())
            #     if int(layer.featureCount()) != 0:
            #         print Global.getPG_connection().tableListWithGeomDict[str(layer.name())]
        
            #         error = QgsVectorFileWriter.writeAsVectorFormat(layer, layer.name() + ".sqlite",
            #                                                     "utf-8", None, "SQLite")
            #         if error == QgsVectorFileWriter.NoError:
            #             print "success!"
            #     else:
            #         #Remove the empty layer from the layer dictionnary
            #         del Global.getPG_connection().tableListWithGeomDict[str(layer.name())]



            #         #no output
            #         pass
            #===============================================================================
        #discard Unselected layer
        else:
            #Remove layer from the layer dictionnary
            del Global.getPG_connection().tableListWithGeomDict[str(layer.name())]
            # print "layer %s has been discarded by user" %(str(layer.name()))
            #no output
            pass

    def registerLocalLayers(self):
        """
        this class register all local copies of the SIG40 db extract
        Import the "OGR style" SQlite DB file extracted from the SIG40 DB to the Map Layer Registry
        """
           
        # Load and register all Layer using the QgsVectorLayer Class while
        # reading the list
        canvas = QgsMapCanvas()

        #Set a specfic progress bar for each layer
        # qgis.utils.iface.messageBar().clearWidgets() 

        # try:
        #     self.progressMessageBar.layout().removeWidget(self.progress)
        #     self.progressMessageBar.clearWidgets() 
        # except:
        #     pass


        #tble_list = Global.getOproject().tablelistgeom
        tble_list = Global.getPG_connection().tableListWithGeom


        # #first start/set a progress bar
        # self.progressMessageBar = qgis.utils.iface.messageBar().createMessage("Chargement en cours...")
        # self.progress = QProgressBar()
        # self.progress.setMaximum(100)
        # self.progress.setTextVisible (True) 
        # self.progressMessageBar.layout().addWidget(self.progress)
        # qgis.utils.iface.messageBar().pushWidget(self.progressMessageBar, qgis.utils.iface.messageBar().INFO)
     


        #first start/set a progress bar
        # self.progressMessageBar = qgis.utils.iface.messageBar()
        # self.progressMessageBar.pushMessage("Progress", level= QgsMessageBar.INFO)
        # self.progress = QProgressBar()
        # self.progress.setMaximum(100) 
        # self.progressMessageBar.pushWidget(self.progress)


        #Count all selected feature
        # count = len(tble_list)
        # i = 0



        # Retrieve the Table List discovered from the SIG40 DB
        for key in Global.getPG_connection().tableListWithGeomDict.keys():
        #for i in tble_list:
            #Pass non-selected table
           
            if Global.getPG_connection().tableListWithGeomDict[key][5]:
           
                # load sqlite
                # strip tablename
                tablename = key
                geom_name = Global.getPG_connection().tableListWithGeomDict[key][1]
    
                # Load the Sqlite file as a regular vector layer supported by the
                # OGR library
                # vlayerpath = os.path.join(
                #     Global.getOproject().currentProjectPath, tablename + ".sqlite")
                # vlayer = QgsVectorLayer(vlayerpath, tablename, "ogr")

                vlayerpath = os.path.join(
                     Global.getOproject().currentProjectPath, tablename + ".sqlite")
                
                uri = QgsDataSourceURI()
                uri.setDatabase(vlayerpath)
                schema = ''
                table = tablename
                uri.setDataSource(schema, table, 'GEOMETRY')

                display_name = tablename
                vlayer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')
                

    
                if vlayer.isValid():
                    # print "sqllayer succesfully loaded - adding to mapinstance"
                    QgsMapLayerRegistry.instance().addMapLayer(vlayer)
                    canvas_layer = QgsMapCanvasLayer(vlayer)
                    canvas = QgsMapCanvas()
                    canvas.setLayerSet([canvas_layer])
                    
                    #update the progress bar
                    # i = i + 1
                    # percent = (i/float(count)) * 100
                    # self.progress.setValue(percent)
                    # time.sleep(1)

                    try:
                        #INSTALL the Table Field Widgets
                        # print "SET FIELD CONTROL %s" %(vlayer.name())
                        OQgis.setTableEditType(vlayer)
                    except:
                        pass
                        # print "ARRGH"


                else:
                    pass
                    # print "sqllayer failed to load!"

    
        canvas.zoomToFullExtent()
        # Global.getOproject().map_canvas.show()

        #Clear the previous message bar
        # qgis.utils.iface.messageBar().clearWidgets()
        
    def setDisplayField(self, vlayer):
        """ensure that column identifiant is the primary display field to be used in the identify results dialog
        Keyword param:
        - vlayer -- A QgsVectorLayer
        """

        vlayer.setDisplayField("identifiant")

    @staticmethod
    def selectAlayerByName(name):
        """select a layer by its name"""

        layers = QgsMapLayerRegistry.instance().mapLayers().keys()
        for layer in layers:
            layername = QgsMapLayerRegistry.instance().mapLayer(layer).name()
            if layername != name:
                continue
            else:
                return QgsMapLayerRegistry.instance().mapLayer(layer)
                


class LocalDB_utils(object):

    """
    This Class gives utility to set-up the local DB generated for this projet.
    It is exclusive to Sqlite DB - no DB genericity here
    It includes:
    - Implant triggers to keep track of changes within the Sqlite Files
    - Set-up SQLITE Autorization Callback
    """
    @staticmethod
    def connect2LocalDb(_dbname,_dbpath):
        """
        Set a connection and a cursor for a local SQLITE DB
        Keyword Parameter:
        _dbname -- str the table name
        Return:
        An SQL cursor
        """
        
        # print "LocalDB_utils  atttempt connection to SQLITE"
        fullpath = os.path.join(_dbpath, _dbname + ".sqlite")
        # give a connection a cursor and execution
        conn = sqlite3.connect(fullpath)
        c = conn.cursor()
       
        return [c, conn]
        
    @staticmethod
    def SQLinjection(cursor, _sqlstatement, result = False):
        """
        Execute a SQL code
        result = False, no return
        result = True, return an iterator if performinf SELECT operations
        """
        cursor.execute(_sqlstatement)
        
        if result:
            items = cursor.fetchall()
            return items
        
    def AddField(self,_dbpath, _dbname, _field, _type):
        """
        Add a field to a SQLITE DB
        TODO : type should be an enumerator
        """
        
        fullpath = os.path.join(_dbpath, _dbname + ".sqlite")

        # give a connection a cursor and execution
        conn = sqlite3.connect(fullpath)
        c = conn.cursor()
        ex = c.execute
        
        ex("ALTER TABLE "+ _dbname +" ADD COLUMN "+ _field +" "+ _type )

        conn.close()
        
    def Trigger_UserMod(self, _dbpath, _dbname):
        """add a boolean field that set to .True. whenever a row is modified"""

        fullpath = os.path.join(_dbpath, _dbname + ".sqlite")

        # give a connection a cursor and execution
        conn = sqlite3.connect(fullpath)
        c = conn.cursor()
        ex = c.execute

        tbname = ex(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name !='geometry_columns' AND name != 'spatial_ref_sys' ").fetchall()

        # implant trigger if not existing
        if len(ex("SELECT name FROM sqlite_master WHERE type='table' AND name='userMod'").fetchall()) == 0:

            ex(
                "ALTER TABLE " + _dbname + " ADD COLUMN userMod integer default 0")
            # ex(
            #     "CREATE TRIGGER userMod_trig AFTER UPDATE ON " + _dbname + " BEGIN UPDATE " + _dbname + " SET userMod = 1, ZRnew = 0 WHERE rowid = new.rowid; END;")
            ex(
                "CREATE TRIGGER userMod_trig AFTER UPDATE ON " + _dbname + " BEGIN UPDATE " + _dbname + " SET userMod = new.ZRnew % 2, ZRnew = old.ZRnew  WHERE rowid = new.rowid AND new.ZRlocal != -999; END;")

        conn.close()

    def Trigger_UserMod2(self, _dbpath, _dbname):
        """add a boolean field that set to .True. whenever a row is modified"""

        fullpath = os.path.join(_dbpath, _dbname + ".sqlite")

        # give a connection a cursor and execution
        conn = sqlite3.connect(fullpath)
        c = conn.cursor()
        ex = c.execute

        tbname = ex(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name !='geometry_columns' AND name != 'spatial_ref_sys' ").fetchall()

       
        ex(
            "CREATE TRIGGER userMod2_trig AFTER UPDATE ON " + _dbname + " BEGIN UPDATE " + _dbname + " SET userMod = new.ZRnew %2, ZRnew = 1 WHERE rowid = new.rowid AND new.ZRlocal = -999 ; END;")

        conn.close()

    def Trigger_UserAdd(self, _dbpath, _dbname):
        """add a boolean field that set to .True. whenever a row is added"""

        fullpath = os.path.join(_dbpath, _dbname + ".sqlite")

       # give a connection a cursor and execution
        conn = sqlite3.connect(fullpath)
        c = conn.cursor()
        ex = c.execute

        # implant trigger if not existing
        if len(ex("SELECT name FROM sqlite_master WHERE type='table' AND name='userAdd'").fetchall()) == 0:

            c.execute("ALTER TABLE " + _dbname +
                      " ADD COLUMN userAdd integer default 0")
            c.execute(
                "CREATE TRIGGER userAdd_trig AFTER INSERT ON " + _dbname + " BEGIN UPDATE " + _dbname + " SET userAdd = 1  WHERE rowid = new.rowid; END;")

        conn.close()

    # def Trigger_UserDel(self, _dbpath, _dbname):
    #     """add a boolean field that set to .True. whenever a row is added"""

    #     fullpath = os.path.join(_dbpath, _dbname + ".sqlite")

    #     # give a connection a cursor and execution
    #     conn = sqlite3.connect(fullpath)
    #     c = conn.cursor()
    #     ex = c.execute

    #     # build a pre-sql string that contains all columns field from the table
    #     # first initialize the string
    #     _columnstring = Global.getPG_connection().tableListWithGeomDict[
    #         _dbname][4][0]

    #     for j in range(1, len(Global.getPG_connection().tableListWithGeomDict[_dbname][4])):
    #         if Global.getPG_connection().tableListWithGeomDict[_dbname][4][j] != Global.getPG_connection().tableListWithGeomDict[_dbname][1]:
    #             # print j, Global.getPG_connection().tableListWithGeomDict[_dbname][4][j]
    #             _columnstring += ", " + \
    #                 Global.getPG_connection().tableListWithGeomDict[
    #                     _dbname][4][j]
        

    #     # implant trigger if not existing
    #     if len(ex("SELECT name FROM sqlite_master WHERE type='table' AND name='userDel'").fetchall()) == 0:
    #         # Add required column to track changes associate when trigger
    #         # execution
    #         c.execute("ALTER TABLE " + _dbname +
    #                   " ADD COLUMN userDel integer default 0")
    #         c.execute("ALTER TABLE " + _dbname +
    #                   " ADD COLUMN original_pk integer")
    #         c.execute(
    #             "CREATE TRIGGER userDel_trig BEFORE DELETE ON " + _dbname + "  BEGIN INSERT INTO " +
    #             _dbname + " ( " + _columnstring + ", userDel, original_pk, ZRlocal ) SELECT " + _columnstring + ",1, old.pk, old.ZRlocal FROM  " + _dbname + "  WHERE rowid = old.rowid ; UPDATE " + _dbname + " SET userDel =1 WHERE rowid = old.rowid; END;")
    #     conn.commit()
    #     conn.close()

    def Trigger_UserDel(self, _dbpath, _dbname):
        """add a boolean field that set to .True. whenever a row is added"""

        fullpath = os.path.join(_dbpath, _dbname + ".sqlite")

        # give a connection a cursor and execution
        conn = sqlite3.connect(fullpath)
        c = conn.cursor()
        ex = c.execute

        # build a pre-sql string that contains all columns field from the table
        # first initialize the string
        _columnstring = Global.getPG_connection().tableListWithGeomDict[
            _dbname][4][0]

        for j in range(1, len(Global.getPG_connection().tableListWithGeomDict[_dbname][4])):
            if Global.getPG_connection().tableListWithGeomDict[_dbname][4][j] != Global.getPG_connection().tableListWithGeomDict[_dbname][1]:
                # print j, Global.getPG_connection().tableListWithGeomDict[_dbname][4][j]
                _columnstring += ", " + \
                    Global.getPG_connection().tableListWithGeomDict[
                        _dbname][4][j]
        

        # implant trigger if not existing
        if len(ex("SELECT name FROM sqlite_master WHERE type='table' AND name='userDel'").fetchall()) == 0:
            # Add required column to track changes associate when trigger
            # execution
            c.execute("ALTER TABLE " + _dbname +
                      " ADD COLUMN userDel integer default 0")
            c.execute("ALTER TABLE " + _dbname +
                      " ADD COLUMN original_pk integer")
            c.execute(
                "CREATE TRIGGER userDel_trig BEFORE DELETE ON " + _dbname + " WHEN old.ZRlocal <0  BEGIN SELECT RAISE(ABORT, 'Inclure objet à supprimer dans une Zone de réconcilation avant de le supprimer!!'); END;")
            
            c.execute(
                "CREATE TRIGGER userDelprotected_trig BEFORE DELETE ON   " + _dbname + " WHEN old.ZRlocal > 0 BEGIN INSERT INTO " + _dbname + " ( " + _columnstring + ", userDel, original_pk, ZRlocal )  SELECT " + _columnstring + ",1, old.pk, old.ZRlocal FROM  " + _dbname + "  WHERE rowid = old.rowid ; UPDATE " + _dbname + " SET userDel =1 WHERE rowid = old.rowid;  END;")
        conn.commit()
        conn.close()


    # def Trigger_UserDel_protected(self, _dbpath, _dbname):
    #     """
    #     SQLITE Trigger on DELETE Transaction that check if the object is referenced within a ZR
    #     """

    #     fullpath = os.path.join(_dbpath, _dbname + ".sqlite")

    #     # give a connection a cursor and execution
    #     conn = sqlite3.connect(fullpath)
    #     c = conn.cursor()
    #     ex = c.execute

    #     # build a pre-sql string that contains all columns field from the table
    #     # first initialize the string
    #     _columnstring = Global.getPG_connection().tableListWithGeomDict[
    #         _dbname][4][0]

    #     for j in range(1, len(Global.getPG_connection().tableListWithGeomDict[_dbname][4])):
    #         if Global.getPG_connection().tableListWithGeomDict[_dbname][4][j] != Global.getPG_connection().tableListWithGeomDict[_dbname][1]:
    #             # print j, Global.getPG_connection().tableListWithGeomDict[_dbname][4][j]
    #             _columnstring += ", " + \
    #                 Global.getPG_connection().tableListWithGeomDict[
    #                     _dbname][4][j]
        

    #     # implant trigger if not existing
    #     if len(ex("SELECT name FROM sqlite_master WHERE type='table' AND name='userDel'").fetchall()) == 0:
    #         # Add required column to track changes associate when trigger
    #         # execution
    #         c.execute("ALTER TABLE " + _dbname +
    #                   " ADD COLUMN userDel integer default 0")
    #         c.execute("ALTER TABLE " + _dbname +
    #                   " ADD COLUMN original_pk integer")
    #         c.execute(
    #             """CREATE TRIGGER userDelprotected_trig BEFORE DELETE ON   " + _dbname + 
    #             " WHEN old.ZRlocal > 0
    #                 BEGIN
    #                  INSERT INTO " + _dbname + " ( " + _columnstring + ", userDel, original_pk, ZRlocal ) 
    #                     SELECT " + _columnstring + ",1, old.pk, old.ZRlocal FROM  " + _dbname + "  
    #                         WHERE rowid = old.rowid ; UPDATE " + _dbname + " SET userDel =1 WHERE rowid = old.rowid; 

    #              END;""")
    #     conn.commit()
    #     conn.close()


    def Trigger_PK(self, _dbpath, _dbname):
        """
        add a trigger that will ensure distributig new unique primary values to database addition
        Unique ID set to new.rowid + last_values from Server side
        Need to substract last_value 

        Custom Generated and homogeneous with server DB primary keys algo:

        LAST_VALUE(server) + NEW.ROWID(local count) - ORIGINAL_IMPORTED_FEATURES_COUNT(server)

        All values accesible through the OGeoDB  tableListWithGeom Dictionnary


        """

        fullpath = os.path.join(_dbpath, _dbname + ".sqlite")

        # give a connection a cursor and execution
        conn = sqlite3.connect(fullpath)
        c = conn.cursor()
        ex = c.execute("SELECT * FROM " + _dbname)

        # Retrieve LAST_VALUE from corresponding table sequence at import time
        last_value = Global.getPG_connection().tableListWithGeomDict[
            _dbname][2]
        # Retrieve the feature count at import time
        original_feature_count = Global.getPG_connection().tableListWithGeomDict[
            _dbname][3]

        # implant trigger if not existing
        set = False
        for tuple in ex.description:
            if tuple[0] == "pk":
                set = True
                break

        if set:

            c.execute(
                "CREATE TRIGGER Trigger_PK AFTER INSERT ON " + _dbname + " BEGIN UPDATE " + _dbname + " SET pk = " + str(last_value) + "  + new.rowid - " + str(original_feature_count) + "  WHERE rowid = new.rowid; END;")
        else:

            c.execute(
                "ALTER TABLE " + _dbname + " ADD COLUMN pk integer DEFAULT -1")
            c.execute(
                "CREATE TRIGGER Trigger_PK AFTER INSERT ON " + _dbname + " BEGIN UPDATE " + _dbname + " SET pk = " + str(last_value) + "  + new.rowid - " + str(original_feature_count) + " WHERE rowid = new.rowid; END;")

        conn.close()

    def install_authorizer_function(self, _dbpath, _dbname):
        """
        NOT TESTED - ABANDONED, PREFER TRIGGER APPROACH
        Install a user defined function that 
        """
        fullpath = os.path.join(_dbpath, _dbname + ".sqlite")

        # give a connection a cursor and execution
        conn = sqlite3.connect(fullpath)
        c = conn.cursor()

        conn.create_function("check_authorzation", 5, self.authorizer_func)
        conn.close()
        
class PGDB_utils(object):
    """
    static toolbox for PG request
    """

    @staticmethod
    def staticConnection():
        """
        Require a Global instance
        """
       
        try:
                        
            con_str = "host='%s' port=%s dbname='%s' user='%s'" %( Global.getOproject().host, Global.getOproject().port, Global.getOproject().dbname, Global.getOproject().username )

            connection = psycopg2.connect(con_str)

            Global.connectionstatus = True
            

            return connection

        except psycopg2.OperationalError, e:

            Global.connectionstatus = False
            qgis.utils.iface.messageBar().pushMessage("ATTENTION", str(e), level= QgsMessageBar.CRITICAL, duration =5)


    @staticmethod
    def getPrimaryKey(connection, tablename):
        """
        Fetch the primary key column name for a given table
        Use information schemas:
            - information_schema.table_constraints
            - information_schema.key_column_usage
        """

        cursor = connection.cursor()


        _sqlstatement = "SELECT kcu.column_name"
        _sqlstatement = _sqlstatement +" FROM information_schema.key_column_usage kcu"
        _sqlstatement = _sqlstatement +" LEFT JOIN information_schema.table_constraints tc"
        _sqlstatement = _sqlstatement + " ON kcu.constraint_name = tc.constraint_name"
        _sqlstatement = _sqlstatement + " WHERE kcu.table_name = '%s' AND tc.constraint_type = 'PRIMARY KEY'" %(tablename)

        #print _sqlstatement

        PGDB_utils._exec_sql(connection, cursor, _sqlstatement)

        #return the Primary key column name
        return cursor.fetchall()[0][0]



    @staticmethod
    def _exec_sql(connection, cursor, sql):
        """sql injection with error management"""
        try:
            #print sql

            cursor.execute(sql)
            connection.commit()

        except psycopg2.Error, e:
            # do the rollback to avoid a "current transaction aborted, commands
            # ignored" errors
            connection.rollback()
            # print str(e)
            qgis.utils.iface.messageBar().pushMessage("ATTENTION", str(e), level= QgsMessageBar.CRITICAL)
            #raise DbError(e)

class OGeoDB(OQgis, LocalDB_utils):

    """
    This Class contains all the tools required to perform initial DB operation:
    - connection
    - selection
    - modification

    auto discover attributes from information schema an system catalog

    """


    def __init__(self, user=getpass.getuser(), dbname=Global.getBDname(), passwd="", host=Global.getHostName(), port=Global.getPort()):
        # def __init__(self, user='postgres', dbname='postgres', passwd="",Global.getBDname()
        # host='localhost', port=5432):
        """
        This class provide a connection over a POSQLgreSQL database
        Raise a DBerror if connection parameters are rejected
        """

        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.IP = self.get_ip_address()
        self.passwd = passwd
        
        #keep reference to the current user
        Global.setUserName(user)

        self.connectTry()

        if Global.connectionstatus:  


            self.databaselist = []
                                
            # Save an available database list
            self.listDb()

            #Keep Connection references for the Project
            Global.getOproject().username = self.user
            Global.getOproject().host = self.host
            Global.getOproject().dbname = self.dbname
            Global.getOproject().port = self.port
            Global.getOproject().passwd= self.passwd

            


    def connectTry(self):
       
        try:
            self.con = psycopg2.connect(self.con_info())
            Global.connectionstatus = True
            try:
                qgis.utils.iface.messageBar().clearWidgets()
            finally:
                qgis.utils.iface.messageBar().pushMessage("OK", "Connection serveur valide, session de creation de projet ouverte", level= QgsMessageBar.INFO, duration = 5)

        except psycopg2.OperationalError, e:

            from sig40.sig40_dialog import setConnectionParameters
            from sig40.action.ProjectAction import ConnectionParameters

            #s = "Impossible d'obtenir une connection sur le serveur, vérifier les paramètres de connection: "+ '\n'
            #s = "Impossible d'obtenir une connection sur le serveur, vérifier les paramètres de connection: "
            #errorMessage(str(s)+str(e))
            Global.connectionstatus = False
            #qgis.utils.iface.messageBar().pushMessage("WARNING", str(s)+str(e), level= QgsMessageBar.CRITICAL)
            
            #======================================================================
            # Pop a connection parameters dialog - To Validate/Change connection parameters
            #======================================================================
            #errorConnection()
            
            self.connection_window = setConnectionParameters(str(e))
            self.connection_window.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.connection_window.show()

            self.host = Global.HostName
            self.dbname = Global.BDname
            self.user = Global.userName
            
            #self.connectTry()
            
    def reinit(self, user=Global.getUserName(), dbname=Global.getBDname(), passwd="", host=Global.getHostName(), port=5432):
        """
        reinit a OGeoDb object
        """
        # print "reinit connection"

        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.IP = self.get_ip_address()
        self.passwd = passwd
        


        self.connectTry()

        if  Global.connectionstatus:


            try:
                try:
                    qgis.utils.iface.messageBar().clearWidgets()
                finally:
                    qgis.utils.iface.messageBar().pushMessage("OK", "Connection serveur valide, session de creation de projet ouverte", level= QgsMessageBar.INFO, duration = 5)

                self.databaselist = []
                self.tableListWithGeom = []
                self.tableListWithGeomDict = {}

                #reference sources
                self.tableListWithGeom_source = []
                self.tableListWithGeomDict_source = {}

                # Save an available database list
                self.listDb()

                #Keep Connection references for the Project
                Global.getOproject().username = self.user
                Global.getOproject().host = self.host
                Global.getOproject().dbname = self.dbname
                Global.getOproject().port = self.port
                Global.getOproject().passwd= self.passwd
                    
                
                #===================================================
                #Retrieve User Tables
                #===================================================
                # a counter to ensure that the cursor will be unique
                self.last_cursor_id = 0
                # Build a global list table from the postgresql information schema
                self.tableList = self.list_tables()
                # check if spatial extension is available
               
                if self.check_geometry_columns_table(self.dbname):
                # Build a list of table with geometry from the postgresql info
                # schema
                    try:
                        ret = self.listTablesWithGeom()
                        self.tableListWithGeom = ret[0]
                        self.tableListWithGeomDict = ret[1]

                        _mess = "connection Base de donnée %s!" %(self.dbname)

                    except:
                        pass

                #===================================================
                #Retrieve Sources Tables if available
                #===================================================
                # Build a global list table from the postgresql information schema
                self.tableList_source = self.list_tables("""'source'""")
                # check if spatial extension is available
                
                if self.check_geometry_columns_table(self.dbname):
                    # Build a list of table with geometry from the postgresql info
                    # schema
                    try:
                        ret = self.listTablesWithGeom("""'source'""")
                        self.tableListWithGeom_source = ret[0]
                        self.tableListWithGeomDict_source = ret[1]
                    except:
                        pass


            except:
                Global.connectionstatus = False
                _mess = "Impossible de charger les tables; veuillez vérifier la connection. La base de donnée sélectionnée (%s) n'est peut-être pas valide pour ce projet" %(self.dbname)

        else:
            Global.connectionstatus = False
            _mess = "Impossible de charger les tables; veuillez vérifier la connection. La base de donnée sélectionnée (%s) n'est peut-être pas valide pour ce projet" %(self.dbname)


        #======================================================================
        # Pop a connection parameters dialog - To Validate/Change connection 
        # parameters
        #======================================================================
        
        from sig40.sig40_dialog import setConnectionParameters
        from sig40.action.ProjectAction import ConnectionParameters
        
        try:
            type(_mess)
        except:
            if Global.connectionstatus:
                _mess = "connection OK"
            else:
                _mess = "connection refusée"

        self.connection_window = setConnectionParameters(_mess)
        self.connection_window.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.connection_window.show()

        try:
            # Build and Store the table uri's -- 'PUBLIC'
            self.tableUri = []
            self.geometryTableUriBuilder(self.tableListWithGeom, self.tableUri)
            # Build and Store the table uri's -- 'SOURCE'
            self.tableUri_source = []
            self.geometryTableUriBuilder(self.tableListWithGeom, self.tableUri_source)
        except:
            pass

    def con_info(self):
        """Build the connection parameter string as required by psycopg2.connect"""
        con_str = ''
        if self.host:
            con_str += "host='%s' " % self.host
        if self.port:
            con_str += "port=%d " % self.port
        if self.dbname:
            con_str += "dbname='%s' " % self.dbname
        if self.user:
            con_str += "user='%s' " % self.user
        if self.passwd:
            con_str += "password='%s' " % self.passwd

        return con_str

    def check_geometry_columns_table(self, table):
        """
        Check if a table:
        - has geometry
        - is selectable
        keyword arg:
        table -- string, table name
        return:
        bool True if both condition True
        bool False for any other cases
        """
        c = self.con.cursor()
        self._exec_sql(
            c, "SELECT relname FROM pg_class WHERE relname = 'geometry_columns' AND pg_class.relkind IN ('v', 'r')")

        return (len(c.fetchall()) != 0)

    def get_table_privileges(self, table, schema=None):
        """ table privileges: (select, insert, update, delete) """
        sql = "SELECT has_table_privilege('" + table + \
            "', 'SELECT'), has_table_privilege('" + table + "', 'INSERT'), has_table_privilege('" + \
            table + \
            "', 'UPDATE'), has_table_privilege('" + table + "', 'DELETE')"
        c = self.con.cursor()
        self._exec_sql(c, sql)
        # This SQL query return only one row
        return c.fetchone()

    def get_table_sequence(self, table, schema=None):
        """Retrieve the current avilable table sequence"""
        pass

    def list_schemas(self):
        """
                get list of schemas in tuples: (oid, name, owner, perms)
        """
        c = self.con.cursor()
        sql = "SELECT oid, nspname, pg_get_userbyid(nspowner), nspacl FROM pg_namespace WHERE nspname !~ '^pg_' AND nspname != 'information_schema'"
        self._exec_sql(c, sql)

        schema_cmp = lambda x, y: -1 if x[1] < y[1] else 1

        return sorted(c.fetchall(), cmp=schema_cmp)

    def listDb(self):
        """
        return the available database list installed on the server from sys. catalogue
        """
        c = self.con.cursor()

        sql = """SELECT datname FROM pg_database WHERE datistemplate = false; """

        self._exec_sql(c, sql)
        l = c.fetchall()

        for i in range(0, len(l)):
            self.databaselist.append(l[i][0])

    def list_tables(self, schema=u"""'public'"""):
        """
                get list of tables from default to public schema
                return a list of table
        """
        c = self.con.cursor()

        sql = """SELECT table_name FROM information_schema.tables WHERE table_name NOT LIKE """+"""'%_h'"""+""" AND table_type = 'BASE TABLE' AND table_schema = %s AND table_name NOT IN ('spatial_ref_sys') """ %(schema)
        # print "SQL list tables: ", sql
        self._exec_sql(c, sql)
        l = c.fetchall()
        items = []
        for i in range(0, len(l)):
            items.append(l[i][0])
        return items

    def listTablesWithGeom(self, schema=u"""'public'"""):
        """
            get list of tables from default to public schema
            Filter out non-spatial table ie: no geometry columns discovered
            return a list of table [ ( STR name, STR geometry_name, INT last_value, INT count(imported rows)= -1, List(STR)column_name ) ]
            set thetableListWithGeom dcitionnary
        """
        c = self.con.cursor()

        #sql = """SELECT f_table_name, f_geometry_column  FROM geometry_columns """
        sql = """SELECT f_table_name, f_geometry_column, getseq(f_table_name) FROM geometry_columns WHERE f_table_name NOT LIKE """+"""'%_h'"""+""" AND f_table_schema="""+schema

        self._exec_sql(c, sql)
        items = c.fetchall()
        tablelistgeom = []
        tableListWithGeomDict = {}

        # print "ITEMS %s: " %(schema), items

        try:
            # for i in range(0, len(items)):
            if Global.DBreduxBool:
                for i in range(0, 2):
                    # print "ATTENTION SET REDUIT"
                    # print items[i][0]
                    tablelistgeom.append((items[i][0], items[i][1], items[i][2]))
                    # Add a key and value to the table dictionnary
                    tableListWithGeomDict[items[i][0]] = [
                        items[i][0], items[i][1], items[i][2], -1]

                    c2 = self.con.cursor()
                    sql2 = """SELECT column_name FROM information_schema.columns WHERE  table_name = '""" + \
                        items[i][0] + """'"""
                    self._exec_sql(c2, sql2)
                    items2 = c2.fetchall()
                    columnlist = []
                    for j in range(0, len(items2)):
                        columnlist.append(items2[j][0])

                    # add columnlist to the dictionnary
                    tableListWithGeomDict[items[i][0]].append(columnlist)

            else:
                for i in range(0, len(items)):
                    tablelistgeom.append((items[i][0], items[i][1], items[i][2]))
                    # Add a key and value to the table dictionnary
                    tableListWithGeomDict[items[i][0]] = [
                        items[i][0], items[i][1], items[i][2], -1]

                    c2 = self.con.cursor()
                    sql2 = """SELECT column_name FROM information_schema.columns WHERE  table_name = '""" + \
                        items[i][0] + """'"""
                    self._exec_sql(c2, sql2)
                    items2 = c2.fetchall()
                    columnlist = []
                    for j in range(0, len(items2)):
                        columnlist.append(items2[j][0])
                    
                    # add columnlist to the dictionnary
                    tableListWithGeomDict[items[i][0]].append(columnlist)

                #self.tableListWithGeom = tablelistgeom

            return (tablelistgeom, tableListWithGeomDict )
        
        except:
            pass
            # print "no table with geom in schema %s" %(schema) 

    def geometryTableUriBuilder(self, tableList, tableUri, schema="public"):
        """
            Build a Qgsuirlist from the table name and it's corresponding geometry column
            keyword param:
            tableList -- [tuples ( tablename, geomtry_column_name )]
            schema -- defaulted to "public'
        """

        commonparameters = QgsDataSourceURI()
        commonparameters.setConnection(
            self.host, str(self.port), self.dbname, self.user, self.passwd)
        for item in tableList:
            uri = commonparameters
            uri.setDataSource(schema, item[0], item[1])
            # append to the uri list
            tableUri.append(uri)
            #self.tableUri.append(uri)

    def _exec_sql(self, cursor, sql):
        """sql injection with error management"""
        try:
            cursor.execute(sql)
        except psycopg2.Error, e:
            # do the rollback to avoid a "current transaction aborted, commands
            # ignored" errors
            self.con.rollback()
            errorMessage(str(e))
            #raise DbError(e)


    def get_ip_address(self):
        """
        Adapted from http://ubuntuforums.org/showthread.php?t=1215042
        Had to use a QProcess for windows implementation since Stdout is manage as a Qgis object
        Consulte and parse network. routing table
        """
        import socket
        # 3: Use OS specific command
        import subprocess
        import platform
        ipaddr = ''
        os_str = platform.system().upper()
        try:
            if os_str == 'LINUX':

                # Linux:
                arg = 'ip route list'
                p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE)
                data = p.communicate()
                sdata = data[0].split()
                ipaddr = sdata[sdata.index('src') + 1]
                #netdev = sdata[ sdata.index('dev')+1 ]
                #print('Can used Method 3: ' + ipaddr)
                return ipaddr

            elif os_str == 'WINDOWS':
                # Windows:
                arg = 'route print 0.0.0.0'
       

                process = QProcess()
                process.start(arg)
                process.waitForFinished();
                returnedstring = str(process.readAllStandardOutput())
                # print returnedstring
                process.close();
                sdata = returnedstring.split()
                # print sdata

                while len(sdata) > 0:
                    if sdata.pop(0) == 'Adr.':
                        if sdata[0] == 'interface':
                            ipaddr = sdata[5]
                            break
                #print('Can used Method 4: ' + ipaddr)
                return ipaddr
        except:
            return "Adresse IP inconnue"

