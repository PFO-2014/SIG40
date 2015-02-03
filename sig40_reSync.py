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

from PyQt4.QtCore import *
from PyQt4.QtGui import *


import qgis

from qgis.core import *
from qgis.gui import *

from dbtools.OGeoDB import OQgis, PGDB_utils, LocalDB_utils
from action.ProjectAction import GeoSelection
from action.ProjectAction import NewProjectAction
from action.ProjectAction import ConnectionParameters
from action.ProjectAction import ZRselection2
from global_mod import Global

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

import re
import time
import datetime
import shutil
import shelve
import sys
import getpass
import os
import copy
import unicodedata


import psycopg2
import sqlite3
from pyspatialite import dbapi2 as db

import sys



class reSyncDB(object):

    '''
    This class run the resynchronisation between the local SQlite DB and the Master PG server
    '''

    def __init__(self):
        """
        Retrieve connection parameters from the shelve
        """
        
        
        
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
        
        
        
        #======================================================================
        #Rebuild Oproject instance from shelf
        #======================================================================
        try:
            shelve_p = shelve.open(shelve_path, writeback=True)
            self.oproject = shelve_p['object']

            Global.setOproject(self.oproject)

            #change directory
            os.chdir(current_path)
            # self.host = Global.getOproject().host
            # self.port = Global.getOproject().port
            # #self.dbname = "reine"
            # self.dbname = Global.getOproject().dbname
            # self.user = Global.getOproject().username
            # self.passwd = Global.getOproject().passwd
            self.loaded = True
        except:
             QMessageBox.about(None, 'A Message from earth' , 
                         u'Pas de projet chargé - Veuilles créer/recharger un projet avant de tenter une reconciliation')
             self.loaded = False
        


   
    def getNumrec(self, pg_connection, pg_cursor, _qgsfeature, idx, idx2):
        """
        Specific to the ZR table
        This method write the new ZR entry to the Serveur ZR table
        this method return the current value for a newly inserted entry within the ZR table
        """

        attrs_geom = _qgsfeature.geometry()
        geomAsWKT = attrs_geom.exportToWkt()

        ZRid = _qgsfeature.attributes()[idx]
        motif = _qgsfeature.attributes()[idx2]


        ##print geomAsWKT
       

        #=============================
        #Action globale
        #=============================
        #get a unique numrec and inscribe the selected feature to the ZR PG table
        #connection = reSyncDB.connectTry()
        # connection = PGDB_utils.staticConnection()

        # c = connection.cursor()
        PGDB_utils._exec_sql(pg_connection, 
        pg_cursor, "INSERT INTO "+ Global.zr_table_name +" (nature_operation, operateur, projet_qgis, geometrie) VALUES ( '"+motif+"', '"+ Global.getOproject().username+"', '"+ Global.getOproject().project_name +"' , ST_GeomFromText('"+str(geomAsWKT)+"',"+Global.getOproject().getSrid()+")) RETURNING numrec")

        try:
            numrec = pg_cursor.fetchall()[0][0]
            #keep track of local ZRid to Global numrec index
            #print "NUMREC: ",numrec
            Global.getOproject()._numrecdict[ZRid] = numrec
            return numrec
        except:
            pass
        # #print "NUMREC UNIQUE: ", numrec

        
    def trueDesync(self, pg_connection, pg_cursor, syncDict, table_name, indexobjet, LOCAL_date, SERVER_date):
        """
        This method build a list of modified field with comparaison with the PG database history tables
        Require transtyping to allow object field value comparaison as SQLITE support only a few type 
        - Int
        - Real 
        - Blob
        - Boolean that are not boolean

        Unicode string with special characters are Normalized to regular ascii


        """

        if LOCAL_date == None:
            LOCAL_date = 'IS NULL'


        #print "Out-of-Sync Resolution module"
        trueSync = True

        #Fetch the PGtable_actual and PGtable_history from the server
        #build the ordered selection attribute list 
        #attribute_table = Global.getOproject().tableDict[table_name][4]
        
        # #print table_name
        # #print syncDict.keys()

        attribute_table =  syncDict[table_name][1]
        listedate = []
        listegeom = []

        #Set index variable to avoid date comparaison
        for i,j in enumerate(attribute_table):
            if j in Global.listedate_nom :
                listedate.append(i)

            if j in Global.getOproject().tableDict[table_name][1]:
                listegeom.append(i)

        _primarykey = PGDB_utils.getPrimaryKey(pg_connection, table_name)

        #get the indentifiant index from actual table
        for i,j in enumerate(attribute_table):
            if j == 'identifiant':
                index_identifiant = i
                break
            else:
                continue
        
        _pkobject = syncDict[table_name][0][indexobjet][0]

        _identifiant = syncDict[table_name][0][indexobjet][index_identifiant]

        _table_name_history = "historique."+table_name+"_h"

        #print "     _pkobject         : ", _pkobject
        #print "     index_identifiant : ", index_identifiant
        #print "     _identifiant      : ", str(_identifiant)
        
        #print "     _primarykey       : ",_primarykey
        #print "     indexobjet        : ", indexobjet

        #print "     liste date        : ", listedate
        #print "     liste geom        : ", listegeom

        #==========================================================================
        #Build the historical object
        #prepare the selection string without _primary_key
        for item in attribute_table:
            if item != _primarykey:

                try:
                    if item ==  Global.getOproject().tableDict[table_name][1]:
                        item = "ST_AsText("+item+")"
                    _sql_attribute_h += ","+item
                    
                except:
                    if item ==  Global.getOproject().tableDict[table_name][1]:
                        item = "ST_AsText("+item+")"
                    _sql_attribute_h = item
                
        # #print "     _sql_attribute_h: ", _sql_attribute_h

        if LOCAL_date == 'IS NULL':
            _sqlstatement = "SELECT %s from %s WHERE identifiant = %s AND date_de_modification %s AND detruit = false " %(_sql_attribute_h, _table_name_history, """'"""+_identifiant+"""'""",  LOCAL_date )
        else:
            _sqlstatement = "SELECT %s from %s WHERE identifiant = %s AND date_de_modification =  '%s'  AND detruit = false " %(_sql_attribute_h, _table_name_history, """'"""+_identifiant+"""'""",  LOCAL_date )

        PGDB_utils._exec_sql(pg_connection, 
        pg_cursor, _sqlstatement)
        
        tmp = pg_cursor.fetchall()
        #tmp[0] is a tuple
        PGtable_history = list(tmp[0])
        PGtable_history.insert(0, long(_pkobject) )
        
        #==========================================================================


        #==========================================================================
        #Build the up-to-date object
        #Build the SQL selection string; make Primary Key the first item of the selection index
        for item in attribute_table:
            if item != _primarykey:
                try:
                    if item ==  Global.getOproject().tableDict[table_name][1]:
                            item = "ST_AsText("+item+")"
                    _sql_attribute += ","+item
                except:
                    if item ==   Global.getOproject().tableDict[table_name][1]:
                            item = "ST_AsText("+item+")"
                    _sql_attribute = item
        _sql_attribute = _primarykey+","+_sql_attribute
        

        

        _sqlstatement = "SELECT %s from %s WHERE %s = %s " %(_sql_attribute, table_name, _primarykey, _pkobject )

        PGDB_utils._exec_sql(pg_connection, 
        pg_cursor, _sqlstatement)


        #pg_cursor.fetchall()[0] is a tuple
        PGtable_actual = list(pg_cursor.fetchall()[0])
        #==========================================================================

        # for itemh in PGtable_history:
        #     #print "     PGtable_history: ", itemh, type(itemh)
        # for itemh in PGtable_actual:
        #     #print "     PGtable_actual: ", itemh, type(itemh)
        # for itemh in Global.getOproject().syncDict[table_name][0][indexobjet]:
        #     #print "     local: ", itemh, type(itemh)


        #build an attribute index from comparaison with relative history table @LOCAL_date
        # #print "build an attribute index from comparaison with relative history table @LOCAL_date"

        #for all fields of current object in syncDict
        for i,j in enumerate(syncDict[table_name][0][indexobjet]):
            #Compare values within PGtable_history and syncDict to build an index of changes
            #Field indexation is homogeneous ie:
            #   1. Cle primaire
            #   2. Geom
            #   [...] champs métiers/historique/[...]
            
            # WARNING homogeneous Datatype between PG/SQLITE; TRANSTYPING MANDATORY
               
            # # Do not compare raw WKT string; turn them into QgsGeometry object before
             
            try:
               
                # #print type(PGtable_history[i]), PGtable_history[i] , type(j), j

                #do not compare date
                if i in listedate:
                    # #print "     DATATYPE DATE; PASS!"
                    continue

                # Do not compare raw WKT string; turn them into QgsGeometry object before
                if i in listegeom:
                    if QgsGeometry.fromWkt(str(j)).equals(QgsGeometry.fromWkt(str(PGtable_history[i]))):
                        continue
                    else:
                        try:
                            index_history.append(i)
                            # #print "NOUVELLE ENTREE D'INDEX: ", index_history
                        except:
                            index_history = []
                            index_history.append(i)
                            # #print "NOUVELLE ENTREE D'INDEX: ", index_history
                        
                #----------------------------------------------------------------------------------------------
                #transtype to string or normalized string when possible
                if isinstance(PGtable_history[i], unicode):
                    history_string = unicodedata.normalize('NFKD', PGtable_history[i]).encode('ascii','ignore')
                elif isinstance(PGtable_history[i], bool):
                    if PGtable_history[i] == True:
                        history_string = 't'
                    else:
                        history_string = 'f'
                else:
                    history_string   = str(PGtable_history[i])

                if isinstance(j, unicode):
                    local_string   = unicodedata.normalize('NFKD', j).encode('ascii','ignore')
                elif isinstance(j, bool):
                    if j == True:
                        local_string = 't'
                    else:
                        local_string = 'f'
                else: 
                    local_string   = str(j)
                #----------------------------------------------------------------------------------------------
               
                if history_string == local_string:
                    # #print "EQUALS  ", history_string,   local_string 
                    continue
                else:
                    # #print "NOT EQUALS  ", history_string,   local_string

                    try:
                        index_history.append(i)
                        # #print "NOUVELLE ENTREE D'INDEX: ", index_history
                    except:
                        index_history = []
                        index_history.append(i)
                        # #print "NOUVELLE ENTREE D'INDEX: ", index_history
            except:
                continue
                

       
  

        #Build attribute index that map changes on server side
        # #print "Build attribute index that map changes on server side"
        #HOMOGENEOUS DATATYPE THANKS TO PSYCOPG
        for i,j in enumerate(PGtable_actual):
            
            try:
                # #print type(PGtable_history[i]), PGtable_history[i] , type(PGtable_actual[i]), PGtable_actual[i] 
                history_string = PGtable_history[i]
                actual_string  = PGtable_actual[i]

                if history_string ==  actual_string:
                    continue
                else:
                    try:
                        index_actual.append(i)
                    except:
                        index_actual = []
                        index_actual.append(i)
            except:
                pass

        #Compare index and build a collision index if so:
        try:
            for i,j in enumerate(index_actual):
                try: 
                    for k,l in enumerate(index_history):
                        # #print "index_actual: ", j, "index_history: ", l
                        if l == j:
                            #This is a true desynchronisation
                            trueSync = False
                            try:
                                index_collision.append(j)
                            except:
                                index_collision = []
                                index_collision.append(j)
                        else:
                            pass
                except:
                    pass
        except:
            pass


        # try:
        #     #print "index_actual    : ", index_actual
        #     #print "index_history   : ",index_history
        #     #print "index_collision : ", index_collision
        # except:
        #     pass

        
        # pass the corresponding case (true desync or false desync) to the syncDict
        if not trueSync:
            print "     TRUE DE-SYNC with collision @: ",  index_collision
            syncDict[table_name][0][indexobjet].append(index_collision)
            return trueSync
        else:
            print "     NOT TRUE DE-SYNC!"
            print index_history
            #pass the attribute index for update
            syncDict[table_name][0][indexobjet].append(copy.copy(index_history))

            # print syncDict[table_name][0][copuindexobjet]
            #print  trueSync
            return trueSync


    def referenceUpdatedObject(self,_sql_attribute, _geometry_column_name, _primarykey, key, pg_connection, pg_cursor, ZRid, tmp_fieldlist):
        """
        Reference all Objects that have been locally modified by user action
        Populate the corresponding reconciliation dictionnary
        (available @ Oproject.syncDict) 
        """
        #REQUEST AND BUILD A LISTING OF LOCAL MODIFICATION
        _sqlstatement = "SELECT %s" %(_sql_attribute)
        _sqlstatement = _sqlstatement +" FROM %s" %(key)
        _sqlstatement = _sqlstatement +" WHERE ZRlocal = %s AND userMod = 1 AND userAdd = 0 AND userDel = 0" %(str(ZRid))
        # #print " SQL Statement: referenceUpdatedObject ", _sqlstatement
       
        fieldlist = copy.copy(tmp_fieldlist)

        fieldlist.insert(0, _geometry_column_name )
        fieldlist.insert(0, _primarykey )
        # #print tmp_fieldlist
        # tmp_fieldlist.insert(0, _geometry_column_name )
        # tmp_fieldlist.insert(0, _primarykey )

        #OPEN A CONNECTION TO THE LOCAL SQLITE TABLE
        rt = LocalDB_utils.connect2LocalDb( key, Global.getOproject().currentProjectPath ) 
        LOCAL_cursor = rt[0]
        LOCAL_conn = rt[1]
        LocalDB_utils.SQLinjection(LOCAL_cursor, str(_sqlstatement), False)
        

        #APPEND AN ENTRY TO THE SYNCHRONISATION DICTIONNARY
        try:
            recon = LOCAL_cursor.fetchall()
            for index1,objet in enumerate(recon):
                objet = list(objet)
                #Prepare field for boolean Sync and trueSync
                for i in range(2):
                    objet.append(None)

                recon[index1]=objet

                if len(recon)>0:
                    Global.getOproject().syncDict[key]=[recon, fieldlist]


        except:
            pass
            #print "Fetching error: referenceUpdatedObject"

        # if  len(recon) != 0:    
            #print u" OBJET MiS A JOuR trouvé", Global.getOproject().syncDict[key]
        #CLOSE THE CONNECTION
        LOCAL_cursor.close()
        LOCAL_conn.close()
        
        # try:
        #     if len(Global.getOproject().syncDict[key][0]) > 0:
        #         #print u"La table %s présente un ou plusieurs objets à synchroniser" %(key)   

        #     # for it in Global.getOproject().syncDict[key][0]:
        #     #     for idx2, it2 in enumerate(Global.getOproject().syncDict[key][1]):

        #     #         #print "%s, %s" %(it2, str(it[idx2]))

        # except:
        #     #print u"La table %s ne présente aucun objet à synchroniser" %(key) 
       


    def referenceNewObject(self,_sql_attribute, _geometry_column_name, _primarykey, key, pg_connection, pg_cursor,ZRid, tmp_fieldlist ):
        """
        Reference all Object that have been Newly added loally by user action
        Populate the corresponding reconciliation dictionnary
        (available @ Oproject.syncDictINSERT) 
        """
        #REQUEST AND BUILD A LISTING OF LOCAL MODIFICATION
        _sqlstatement = "SELECT %s" %(_sql_attribute)
        _sqlstatement = _sqlstatement +" FROM %s" %(key)
        _sqlstatement = _sqlstatement +" WHERE ZRlocal = %s AND userAdd = 1 AND userDel IS NULL" %(str(ZRid))
        # #print " SQL Statement: referenceNewObject ", _sqlstatement
        fieldlist = copy.copy(tmp_fieldlist)

        fieldlist.insert(0, _geometry_column_name )
        fieldlist.insert(0, _primarykey )

        del tmp_fieldlist
        del _sql_attribute

        #OPEN A CONNECTION TO THE LOCAL SQLITE TABLE
        rt = LocalDB_utils.connect2LocalDb( key, Global.getOproject().currentProjectPath ) 
        LOCAL_cursor = rt[0]
        LOCAL_conn = rt[1]
        LocalDB_utils.SQLinjection(LOCAL_cursor, str(_sqlstatement), False)
        

        #APPEND AN ENTRY TO THE SYNCHRONISATION DICTIONNARY
        try:
            recon = LOCAL_cursor.fetchall()
            for index1,objet in enumerate(recon):
                objet = list(objet)
                #Prepare field for boolean Sync and trueSync
                for i in range(2):
                    objet.append(None)

                recon[index1]=objet

                if len(recon)>0:
                    Global.getOproject().syncDictINSERT[key]=[recon, fieldlist]

        except:
            #print "Fetching error: referenceNewObject"
            pass

        if len(recon) !=0:
            #print "Nouvel objet trouvé", Global.getOproject().syncDictINSERT[key]
            pass

        #CLOSE THE CONNECTION
        LOCAL_cursor.close()
        LOCAL_conn.close()
        
        # try:
        #     if len(Global.getOproject().syncDictINSERT[key][0]) > 0:
        #         #print u"La table %s présente un ou plusieurs NOUVEAUX objets à synchroniser" %(key)   
        # except:
        #     #print u"La table %s ne présente aucun NOUVEL objet à synchroniser" %(key) 
        

    def referenceDeletedObject(self, _sql_attribute, _primarykey, key, pg_connection, pg_cursor,ZRid, tmp_fieldlist ):
        """
        Reference all Object that have been deleted loally by user action
        Populate the corresponding reconciliation dictionnary
        (available @ Oproject.syncDictDELETE) 
        """

        #REQUEST AND BUILD A LISTING OF LOCAL MODIFICATION
        _sqlstatement = "SELECT %s" %(_sql_attribute)
        _sqlstatement = _sqlstatement +" FROM %s" %(key)
        _sqlstatement = _sqlstatement +" WHERE ZRlocal = %s AND userDel = 1" %(str(ZRid))
        # #print _sqlstatement
        fieldlist = copy.copy(tmp_fieldlist)

        fieldlist.insert(0, _primarykey )
        
        del tmp_fieldlist
        del _sql_attribute

        #OPEN A CONNECTION TO THE LOCAL SQLITE TABLE
        rt = LocalDB_utils.connect2LocalDb( key, Global.getOproject().currentProjectPath ) 
        LOCAL_cursor = rt[0]
        LOCAL_conn = rt[1]
        LocalDB_utils.SQLinjection(LOCAL_cursor, str(_sqlstatement), False)
        

        #APPEND AN ENTRY TO THE SYNCHRONISATION DICTIONNARY
        try:
            recon = LOCAL_cursor.fetchall()
            for index1,objet in enumerate(recon):
                objet = list(objet)
                #Prepare field for boolean Sync and trueSync
                for i in range(2):
                    objet.append(None)

                recon[index1]=objet

                if len(recon)>0:
                    Global.getOproject().syncDictDELETE[key]=[recon, fieldlist]
                    # #print Global.getOproject().syncDictDELETE[key]

        except:
            #print "Fetching error: referenceDeletedObject"
            pass

        if len(recon) !=0:
            #print "Objet détruit trouvé", Global.getOproject().syncDictDELETE[key]
            pass
        #CLOSE THE CONNECTION
        LOCAL_cursor.close()
        LOCAL_conn.close()
        
        # try:
        #     if len(Global.getOproject().syncDictINSERT[key][0]) > 0:
        #         #print u"La table %s présente un ou plusieurs objets à Supprimer" %(key)   
        # except:
        #     pass


    def processUpdate(self,syncDict, pg_connection, pg_cursor, numrec ):
        """
        Core algorithm to write/reject UPDATE to the PG Database
        """
        trueSync = True
        #print "process Update "
        #print "liste des table à traiter: " , syncDict.keys()
        for tablemod_name in syncDict.keys():
            
            for indexobjet,objet in  enumerate(syncDict[tablemod_name][0]):
                
               
                #retrieve primary key field
                _primarykey = syncDict[tablemod_name][1][0]
                _id = objet[0]
                _sqlstatement = "SELECT date_de_modification FROM %s WHERE %s = %s" %(tablemod_name, _primarykey, str(_id) ) 
                
                

                try:
                    PGDB_utils._exec_sql(pg_connection, 
                        pg_cursor, _sqlstatement)

                    SERVER_date = pg_cursor.fetchall()[0][0]
                    
                   
                    index_date = -1
                    for i,j in enumerate(syncDict[tablemod_name][1]):
                        if j =="date_de_modification":
                            index_date = i
                        else:
                            continue
                    
                    #===============================================================================
                    # FLAG sync/desync 
                    # Based on DATE comparaison (ISO string)
                    #===============================================================================
                    if index_date != -1:
                        LOCAL_date = objet[index_date]
                       
                        # "COMPARAISON DES DATES LOCALES/SERVEUR: ", str(LOCAL_date), str(SERVER_date)
                        # String comparaison - Test if one contains the others
                        


                        if str(SERVER_date).find(str(LOCAL_date)) != -1:

                            #update  sync and trueSync field in dictionnary
                            syncDict[tablemod_name][0][indexobjet][-1] = True
                            syncDict[tablemod_name][0][indexobjet][-2] = True
                            # trueSync = True

                        elif str(LOCAL_date).find(str(SERVER_date)) != -1:
                     
                            #update  sync and trueSync field in dictionnary
                            syncDict[tablemod_name][0][indexobjet][-1] = True
                            syncDict[tablemod_name][0][indexobjet][-2] = True
                            # trueSync = True
                          
                        else:
                            #Sync isFalse
                            syncDict[tablemod_name][0][indexobjet][-2] = False
                            #Check for true desynchronisation
                            checktrueSync = self.trueDesync(pg_connection, pg_cursor, syncDict, tablemod_name, indexobjet, LOCAL_date, SERVER_date)
                            #print "     trueSync: " , checktrueSync
                            syncDict[tablemod_name][0][indexobjet][-2] = checktrueSync
                            # syncDict[tablemod_name][0][indexobjet].append("trueSync")
                            trueSync = False
                            
                           
                            pass

                    else:
                        #print "     TABLES NON CONFORME"
                        pass
                    #===============================================================================
                    
                except:
                    #print "erreur processUpdate try/except 678-680"
                    qgis.utils.iface.messageBar().clearWidgets() 
                    pass
        
        #CASE PARTIAL SYNC: NON-COLLIDING MODIFICATION
        # print "DESYNCHRONISATION Management"
        # print "trueSync: ", trueSync
        # print "objet: ", syncDict[tablemod_name][0][indexobjet][0]
        # print syncDict[tablemod_name][0][indexobjet][-1]
        # print syncDict[tablemod_name][0][indexobjet][-2]
        # print syncDict[tablemod_name][0][indexobjet][-3]

        restart = False;

        for g in syncDict.keys(): 
                
            for h in range(0,len(syncDict[g][0])):

               
                #CASE NO-SYNC - COLLING MODIFICATION
                try:
                    if not syncDict[g][0][h][-2]:
                        for i in syncDict[g][0][h][-1]:
                            #print "Collision sur attribut %s dans table %s " %(syncDict[g][1][i], g)
                            Global.getOproject().desync = True
                except:
                    #print "CASE NO-SYNC - COLLIDING MODIFICATION - Projet déjà synchronisé"
                    pass


                #=============================================================================
                # #GESTION DE LA CONCURRENCE @WRITING TIME
                # # Make local reference to 'date_de_modification' 
                # # LOCAL_date is required to ensure sync at writing time
                # index_date = -1
                # for i,j in enumerate(syncDict[g][1]):

                #     if j =="date_de_modification":
                #         index_date = i
                #     else:
                #         continue
                # LOCAL_date = syncDict[g][0][h][index_date]
                #=============================================================================


                
                #CASE NOT TRUE DE-SYNC
                if not isinstance(syncDict[g][0][h][-1], bool) and syncDict[g][0][h][-2] and not trueSync:
                # if not isinstance(syncDict[g][0][h][-1], bool) and syncDict[g][0][h][-3] and syncDict[g][0][h][-3] ==  "trueSync":  
                    
                    #Reset+Create or Create VARIABLEBINDING Table to hold python variables to pass from SQLITE to PG
                    #This table is required to cast Python varaibles into SQL littals by type
                    #http://initd.org/psycopg/docs/usage.html

                    try:
                        del variablebinding
                        variablebinding = []
                    except:
                        variablebinding = []
                       

                    #synchronisation avec conflit Résolu: Mise à jour de l'objet"

                    # print "     DICTIO DES SYNCHRONISATIONS FINAL: %s " %(g), syncDict[g][0][h]
                    # print "     cle primaire recherche: %s " %(syncDict[g][0][h][0])
                    # print "     champ à mettre à jour dans table : %s " %(g)
                    print "     liste des chanps %s " %(syncDict[g][1])

                    for indexmod in syncDict[g][0][h][-1]:
                        # Do Not RESYNC IMMUTABLE FIELD! Numrec need to be processed idependantly
                        if str(syncDict[g][1][indexmod]) in list(Global.immutable_field):
                            print "fieldname Immutable: ", fieldname
                            continue

                        #print "     objet: %s   champ : %s (index:%s) nouvelle valeur = %s " %(syncDict[g][0][h][0], syncDict[g][1][indexmod], indexmod,syncDict[g][0][h][indexmod] )
                        
                        #build the update set string
                        try:
                            #field IS NOT geometry:
                            if str(syncDict[g][1][indexmod]) != Global.getOproject().tableDict[g][1] :
                                
                                _setstring += ","+str(syncDict[g][1][indexmod])+" = %s "
                                variablebinding.append(syncDict[g][0][h][indexmod])
                            
                            #Field IS geometry
                            else: 
                                _setstring += ","+str(syncDict[g][1][indexmod])+"= ST_GeomFromText( %s, %s )"
                                
                                variablebinding.append( syncDict[g][0][h][indexmod] )
                                variablebinding.append( int(Global.getOproject().srid ))
                        except:
                            #field IS NOT geometry:
                            if str(syncDict[g][1][indexmod]) != Global.getOproject().tableDict[g][1] :
                                
                                _setstring = str(syncDict[g][1][indexmod])+" = %s "
                                variablebinding.append(syncDict[g][0][h][indexmod])
                            
                            #Field IS geometry
                            else: 
                                # #print "6 fieldindex %d: fieldname %s = %s " %(fieldindex, str(fieldname), str(syncDict[g][0][h][fieldindex]))
                                _setstring = str(syncDict[g][1][indexmod])+"= ST_GeomFromText( %s, %s )"
                                
                                variablebinding.append( syncDict[g][0][h][indexmod] )
                                variablebinding.append( int(Global.getOproject().srid ))

                    #Complete the setstring with the Numrec Field
                    _setstring += ",numrec = %s"
                    variablebinding.append(numrec)

                    _primarykey = syncDict[g][1][0]
                    _valkey = syncDict[g][0][h][0]
                    # #print u"        _setstring", _setstring
                    # _sqlstatement = "UPDATE %s SET %s, numrec = %s WHERE %s = %s" %(g, _setstring ,str(numrec), _primarykey, _valkey  )

                   


                    _sqlstatement = "UPDATE %s SET %s WHERE %s = %s" %(g, _setstring , _primarykey, _valkey  )
                    print _sqlstatement

                    

                    del _setstring
                    try:
                        ##print sql
                        pg_cursor.execute(_sqlstatement,variablebinding)
                        
                        print pg_cursor.query
                        # pg_connection.commit()

                    except psycopg2.Error, e:
                        # do the rollback to avoid a "current transaction aborted, commands
                        # ignored" errors
                        pg_connection.rollback()
                        pg_connection_ZR.rollback()
                        
                        #print str(e)
                        qgis.utils.iface.messageBar().pushMessage("ATTENTION", str(e), level= QgsMessageBar.CRITICAL, duration = 20)
                        Global.getOproject().synchronized_update = False
                        Global.getOproject().dbrejected = True
                        return




                #CASE FULL-SYNC
                # elif syncDict[g][0][h][-2] and trueSync:
                elif syncDict[g][0][h][-2]:

                    # QMessageBox.critical(
                    #         None ,u"CASE FULL-SYNC", "833")

                #Reset+Create or Create VARIABLEBINDING Table to hold python variables to pass from SQLITE to PG
                #This table is required to cast Python varaibles into SQL littals by type
                #http://initd.org/psycopg/docs/usage.html

                    try:
                        del variablebinding
                        variablebinding = []
                    except:
                        variablebinding = []
                  
                    # synchronisation sans aucun conflit: Mise à jour de l'objet"
                    #build the update set string
                    
                    for fieldindex,fieldname in enumerate(syncDict[g][1]):
                        
                        # Do Not RESYNC IMMUTABLE FIELD! Numrec need to be processed idependantly
                        try:
                            if str(fieldname) in list(Global.immutable_field):
                                # #print "fieldname Immutable: ", fieldname
                                continue
                           
                            # make sure we are not updating a PG key and avoid transtyping (python/PG) error on "None type"
                            # if str(fieldname) != Global.getOproject().tableDict[g][1] and syncDict[g][0][h][fieldindex] != None:
                            #field IS NOT geometry:
                            if str(fieldname) != Global.getOproject().tableDict[g][1] :
                                
                                _setstring += ","+str(fieldname)+"= %s "
                                variablebinding.append(syncDict[g][0][h][fieldindex])

                            #Python/PG transtyping: "None Type" to "NULL" mandatory
                            # elif syncDict[g][0][h][fieldindex] == None:
                                
                            #Field IS geometry
                            else: 
                                _setstring += ","+str(fieldname)+"= ST_GeomFromText( %s, %s )"
                                
                                variablebinding.append( syncDict[g][0][h][fieldindex] )
                                variablebinding.append( int(Global.getOproject().srid ))

                        # Exception for set string formatting
                        except:
                            if str(fieldname) in list(Global.immutable_field):
                                continue

                            #field IS NOT geometry:
                            if str(fieldname) != Global.getOproject().tableDict[g][1] :
                                _setstring = str(fieldname)+"= %s "
                                variablebinding.append(syncDict[g][0][h][fieldindex])
                          
                            # Field IS geometry
                            else: 
                                _setstring = str(fieldname)+"= ST_GeomFromText( %s, %s )"
                                
                                variablebinding.append( syncDict[g][0][h][fieldindex] )
                                variablebinding.append( int(Global.getOproject().srid ))

                    
                    #Complete the setstring with the Numrec Field
                    _setstring += ",numrec = %s"
                    variablebinding.append(numrec)

                    _primarykey = syncDict[g][1][0]
                    _valkey = syncDict[g][0][h][0]

                    # #print u"        _setstring", _setstring
                    # _sqlstatement = "UPDATE %s SET %s, numrec = %s WHERE %s = %s" %(g, _setstring ,str(numrec), _primarykey, _valkey  )
                    
                    _sqlstatement = "UPDATE %s SET %s WHERE %s = %s" %(g, _setstring , _primarykey, _valkey  )

                    #=============================================================================
                    #GESTION DE LA CONCURRENCE
                    # _sqlstatement = """DO $$ DECLARE sync BOOLEAN; BEGIN
                       
                    #    sync = false;
                    #    IF (SELECT date_de_modification FROM %s WHERE %s = %s) = '%s' 
                    #     THEN sync = true;
                    #           UPDATE %s SET %s WHERE %s = %s; END IF;

                    #     DROP TABLE IF EXISTS _x;
                    #     CREATE TEMPORARY TABLE _x (test_sync boolean);
                    #     INSERT INTO _x (test_sync) VALUES ( sync );
                    #     END$$;
                    #     SELECT * FROM _x;
                    #     """%(g, _primarykey, _valkey, LOCAL_date ,g, _setstring , _primarykey, _valkey  )
                     #=============================================================================


                    del _setstring

                    try:
                        ##print sql
                        pg_cursor.execute(_sqlstatement,variablebinding)
                        #=============================================================================
                        # # GESTION DE LA CONCURRENCE
                        # tmp = list(pg_cursor.fetchall())
                        # restart = tmp[0][0]  

                        # #TEST Concurrent reconcilaition @writing time
                        # #TEST if the sync is kept during the reconciliation process at writing time 
                        # if not restart :
                        #     # Stop reconciliation process
                        #     # print "synchro annulée"
                        #     Global.getOproject().concurencyManagement = True
                        #     pg_connection.rollback()
                        #     pg_connection_ZR.rollback()
                        #     Global.getOproject().synchronized_update = False
                        #     QMessageBox.critical(
                        #         None ,u"Synchronisation annulée", """Concurrence inter-utilisateur lors de l'écriture.
                        #         \n La base n'est plas synchronisée 
                        #         \n Veuillez relancer la réconciliation""")
                        #     #QUIT
                        #     return
                        # else:
                        #     # print "succes"
                        #     pass
                        #=============================================================================

                    except psycopg2.Error, e:
                        # do the rollback to avoid a "current transaction aborted, commands
                        # ignored" errors
                        pg_connection.rollback()
                        #print str(e)
                        qgis.utils.iface.messageBar().pushMessage("ATTENTION", str(e), level= QgsMessageBar.CRITICAL, duration = 20)
                        Global.getOproject().dbrejected = True


                         #Keep reference to the error for reporting
                        Global.getOproject()._errortable[ZR] = str(tablemod_name)+" objet: "+str(syncDict[tablemod_name][0][h][0] ) +" / "+e[0]
                        QMessageBox.critical(
                            None ,u"Synchronisation annulée", """Un objet ne respecte pas une contrainte de la Base de donnee.
                                        \n %s"""%(e[0]))
                        Global.getOproject().synchronized_update = False
                        Global.getOproject().dbrejected = True

                else:
                    pass


    def processCreate(self,syncDict, pg_connection, pg_cursor, numrec, ZR ):
        """
        Core algorithm to write/reject CREATE to the PG Database
        """

        #print "process create "
        #print "liste des table à traiter: " , syncDict.keys()
        for tablemod_name in syncDict.keys():
            #print "TRAITEMENT CREATE TABLE %s" %(tablemod_name)
            for indexobjet,objet in  enumerate(syncDict[tablemod_name][0]):

                #Reset+Create or Create VARIABLEBINDING Table to hold python variables to pass from SQLITE to PG
                #This table is required to cast Python varaibles into SQL littals by type
                #http://initd.org/psycopg/docs/usage.html
                try:
                    del variablebinding
                    variablebinding = []
                    #print "variablebinding, " , variablebinding
                except:
                    variablebinding = []
                    #print "variablebinding, " , variablebinding

                #print u"        synchronisation sans aucun conflit: Mise à jour de l'objet"
                #build the update set string
                
                for fieldindex,fieldname in enumerate(syncDict[tablemod_name][1]):
                    
                    
                    # #print (fieldname, fieldindex, Global.getOproject().syncDict[g][0][h][fieldindex])
                    # Do Not RESYNC IMMUTABLE FIELD! Numrec need to be processed idependantly
                    try:
                        if str(fieldname) in list(Global.immutable_field):
                            # #print "fieldname Immutable: ", fieldname
                            continue
                       

                        #make sure we are not updating a PG key and avoid transtyping (python/PG) error on "None type"
                        # if str(fieldname) != Global.getOproject().tableDict[g][1] and syncDict[g][0][h][fieldindex] != None:
                        #field IS NOT geometry:
                        if str(fieldname) != Global.getOproject().tableDict[tablemod_name][1] :
                            
                            _setstring += ","+str(fieldname)
                            _valstring += " ,%s"
                            variablebinding.append(syncDict[tablemod_name][0][indexobjet][fieldindex])

                        
                        #Field IS geometry
                        else: 
                            _setstring += ","+str(fieldname)
                            _valstring += " ,ST_GeomFromText( %s, %s )"
                            variablebinding.append( syncDict[tablemod_name][0][indexobjet][fieldindex] )
                            variablebinding.append( int(Global.getOproject().srid ))

               
                    # Exception for set string formatting
                    except:
                        if str(fieldname) in list(Global.immutable_field):
                            continue

                        # if str(fieldname) != Global.getOproject().tableDict[g][1] and syncDict[g][0][h][fieldindex] != None:
                        #field IS NOT geometry:
                        if str(fieldname) != Global.getOproject().tableDict[tablemod_name][1] :

                            _setstring = "("+str(fieldname)
                            _valstring = "(%s"
                            variablebinding.append(syncDict[tablemod_name][0][indexobjet][fieldindex])
                      
                        # Field IS geometry
                        else: 
                            # #print "6 fieldindex %d: fieldname %s = %s " %(fieldindex, str(fieldname), str(syncDict[g][0][h][fieldindex]))
                            _setstring = "("+str(fieldname)
                            _valstring = "(ST_GeomFromText( %s, %s )"
                            variablebinding.append( syncDict[tablemod_name][0][indexobjet][fieldindex] )
                            variablebinding.append( int(Global.getOproject().srid ))

                            # _setstring = str(fieldname)+"= ST_GeomFromText('"+syncDict[g][0][h][fieldindex]+"')"
                
                #Complete the setstring with the Numrec Field
                _setstring += ",numrec )"
                _valstring += ",%s )"
                variablebinding.append(numrec)
                _sqlstatement = "INSERT INTO %s %s VALUES %s " %(tablemod_name, _setstring , _valstring )
                del _setstring
                del _valstring

                try:
                    ##print sql
                    pg_cursor.execute(_sqlstatement,variablebinding)
                    #print pg_cursor.query
                    # pg_connection.commit()

                except psycopg2.Error, e:
                    # do the rollback to avoid a "current transaction aborted, commands
                    # ignored" errors
                    pg_connection.rollback()

                    qgis.utils.iface.messageBar().pushMessage("ATTENTION", e[0], level= QgsMessageBar.CRITICAL, duration =20)

                    #Keep reference to the error for reporting
                    Global.getOproject()._errortable[ZR] = str(tablemod_name)+" objet: Nouvel objet / "+e[0]
                    QMessageBox.critical(
                    None ,u"Synchronisation annulée", """Un objet ne respecte pas une contrainte de la Base de donnee.
                    \n %s"""%(e[0]))
                    Global.getOproject().synchronized_update = False
                    Global.getOproject().dbrejected = True
                    return


    def processDelete(self,syncDict, pg_connection, pg_cursor, numrec ):
        """
        Core algorithm to write/reject DELETE to the PG Database
        """
        #print "process Delete "
        #print "liste des table à traiter: " , syncDict.keys()
        for tablemod_name in syncDict.keys():
            #print "TRAITEMENT DELETE TABLE %s" %(tablemod_name)
            for indexobjet,objet in  enumerate(syncDict[tablemod_name][0]):

                #Reset+Create or Create VARIABLEBINDING Table to hold python variables to pass from SQLITE to PG
                #This table is required to cast Python varaibles into SQL littals by type
                #http://initd.org/psycopg/docs/usage.html
                try:
                    del variablebinding
                    variablebinding = []
                    #print "variablebinding, " , variablebinding
                except:
                    variablebinding = []
                    #print "variablebinding, " , variablebinding

                #print u"        synchronisation sans aucun conflit: Mise à jour de l'objet"
                #build the update set string

                _setstring = 'detruit = %s  '
                variablebinding.append(True)
                
                #Complete the setstring with the Numrec Field
                _setstring += ",numrec = %s "
                variablebinding.append(numrec)

                _primarykey = syncDict[tablemod_name][1][0]
                _valkey = syncDict[tablemod_name][0][indexobjet][0]


                # do not try to reconciliate object that have been created then destroyed by user
                # during the session
                # Such Object lack a value for PRIMARY KEY
                if _valkey == None:
                    #print "false destruction"
                    continue

                             
                _sqlstatement = "UPDATE %s SET %s WHERE %s = %s " %(tablemod_name, _setstring , _primarykey, str(_valkey)  )
                #print u"        _sqlstatement", _sqlstatement
                del _setstring

                try:
                    ##print sql
                    pg_cursor.execute(_sqlstatement,variablebinding)
                    # pg_connection.commit()

                except psycopg2.Error, e:
                    # do the rollback to avoid a "current transaction aborted, commands
                    # ignored" errors
                    pg_connection.rollback()

                    qgis.utils.iface.messageBar().pushMessage("ATTENTION", e[0], level= QgsMessageBar.CRITICAL, duration = 20)

                    QMessageBox.critical(
                    None ,u"Synchronisation delete annulée", """Un objet ne respecte pas une contrainte de la Base de donnee.
                    \n %s"""%(e[0]))
                    Global.getOproject().synchronized_update = False
                    Global.getOproject().dbrejected = True
                    return


    def reconciliate(self):
        """
        Reconciliation core algorithm
        """
        # #print "=====================RECONCILIATION========================================"

        # #print "Global.synchronized, ", Global.getOproject().synchronized
        if Global.getOproject().synchronized:
            
            QMessageBox.about(
                    None ,u"Attention", u"""Projet déjà synchronisé avec le serveur. """)
            self.generateReport()
            return

       
        #set a local boolean to keep project status s
        Global.getOproject().nochange = None
        #Fetch ZR table
        vZRlayer = OQgis.selectAlayerByName('ZR')
        # init local variable
        numfeat = 0
        #print numfeat 

        try:
            #Check how may ZR have been described
            vZRlayer.selectAll()
            numfeat = vZRlayer.selectedFeatureCount()
            vZRlayer.invertSelection()
           
        except:
            pass

        #=============================================================================
        # Shield specific cases:
        # - Abort if no ZR 
        # - Abort if Layer is corrupt
        #=============================================================================
        try: 
            if vZRlayer == None or numfeat == 0:
                 #No ZR has been defined-> OUT!
                QMessageBox.warning(
                    None ,u"Attention", u"""Aucune ZR n'a été définie.\n 1. Veuillez préalablement ouvrir un projet  \n
                     2. Veuillez définir une ou plusieurs ZR avant de réconcilier les données""")
                del numfeat
                return

            if not vZRlayer.isValid():
                #No ZR has been defined-> OUT!
                QMessageBox.about(
                    None, u"Attention", u"""La table ZR semble corrompue. 
                    Veuillez supprimer la ou les ZR existantes puis re-définir une ou plusieurs ZR avant de retenter une réconciliation
                    avec le serveur""")
                del numfeat
                return
        except:
            del numfeat
            return
            pass

        #=============================================================================
        # CORE algo:
        # FOR each ZR
        #   FOR each TABLE
        #       FOR each Objet
        #=============================================================================
        iterator = vZRlayer.getFeatures()
        
        idx = vZRlayer.fieldNameIndex('indexZR')
        idx2 = vZRlayer.fieldNameIndex('description')

        #open a pg connection;
        pg_connection = PGDB_utils.staticConnection()
        pg_cursor = pg_connection.cursor()

        #open a specific pg connection for the ZR;
        pg_connection_ZR = PGDB_utils.staticConnection()
        #give a unique cursor for the ZR table processing
        zr_pg_cursor = pg_connection.cursor()

        #=============================
        #FOR EACH ZR
        #=============================
        for feat in iterator:

            # #print "TRAITEMENT ZR: ",  feat.attributes()[idx]

            #Get an unique index number - Provided by the PG server
            numrec = self.getNumrec(pg_connection_ZR, zr_pg_cursor, feat, idx, idx2)
            


            #Manage error
            if numrec == None:
                QMessageBox.about(
                None, "Projet %s" % (Global.getOproject().project_name), u"Rien à réconcilier")
                pg_connection_ZR.rollback()
                pg_connection_ZR.commit()
                return

            ZRid = feat.attributes()[idx]
            motif = feat.attributes()[idx2]

            #=============================================================================================================
            #For each table
            #
            #constitution du dictionnaire des objets modifiés par table
            #dict = {'id': [Date; attributs métiers; [liste des attributs modifiés]; bool Sync; bool trueSync; numrec ]}
            #=============================================================================================================

            for key in  Global.getOproject().tableDict.keys():


                # #print "     TRAITEMENT: ", key

                #fetch the PRIMARY KEY from the current table
                _primarykey = PGDB_utils.getPrimaryKey(pg_connection, key)
                # #print "PRIMARY KEY: ", _primarykey

                _geometry_column_name =  Global.getOproject().tableDict[key][1]
                # #print "GEOMETRY COLUMN NAME: ", _geometry_column_name
                attribute_table = copy.copy(Global.getOproject().tableDict[key][4])
                # #print attribute_table
                
                #======================================================================================
                # Prepare the selection String
                # Build the SQL selection string; make Primary Key the first item of the selection index
                # Geometry is second
                tmp_fieldlist = []
                for item in attribute_table:

                    if str(item) ==  str(_primarykey) or str(item) ==  str(_geometry_column_name):
                        continue
                    else:
                        if len(tmp_fieldlist) > 0 :
                            _sql_attribute += ","+item
                            tmp_fieldlist.append(item)
                        else:
                            _sql_attribute = item
                            tmp_fieldlist.append(item)

                # make Primary Key the first item of the selection index
                _sql_attribute =  _primarykey +",ST_AsText(GEOMETRY),"+ _sql_attribute 
                #======================================================================================
                
                #=====================================================================
                #REFERENCE UPDATED/MODIFIED OBJECTS"
                #build the current reconciliation table - Connection to local DB
                #=====================================================================
                
                self.referenceUpdatedObject(_sql_attribute, _geometry_column_name, _primarykey, key, pg_connection, pg_cursor,ZRid, tmp_fieldlist )
                
                #=====================================================================
                #REFERENCE NEWLY INSERTED OBJECTS"
                #build the corresponding reconciliation table - Connection to local DB
                #=====================================================================

                self.referenceNewObject(_sql_attribute, _geometry_column_name, _primarykey, key, pg_connection, pg_cursor,ZRid, tmp_fieldlist )

                #=====================================================================
                #REFERENCE DELETED OBJECTS"
                #build the corresponding reconciliation table - Connection to local DB
                #=====================================================================

                self.referenceDeletedObject(_sql_attribute, _primarykey, key, pg_connection, pg_cursor, ZRid, tmp_fieldlist )

                # #if all synchronisation dictionnary are empty, ZR is empty; RollBack the last ZR entry
                # if len(Global.getOproject().syncDict.keys()) == 0 and  len(Global.getOproject().syncDict.keys()) == 0 and len(Global.getOproject().syncDict.keys()) == 0:
                #     #rollback
                #     #print " there is a stupid empty ZR (%d) out-there" %(ZRid)
                #     pg_connection.rollback()
                # else:
                #     pg_connection.commit()


            if len(Global.getOproject().syncDict.keys()) != 0:    
                Global.getOproject().globalSyncDict[ZRid] = copy.copy(Global.getOproject().syncDict)
            if len(Global.getOproject().syncDictINSERT.keys()) != 0: 
                Global.getOproject().globalSyncDictINSERT[ZRid] = copy.copy(Global.getOproject().syncDictINSERT)
            if len(Global.getOproject().syncDictDELETE.keys()) != 0: 
                Global.getOproject().globalSyncDictDELETE[ZRid] = copy.copy(Global.getOproject().syncDictDELETE)

            Global.getOproject().syncDict = {}
            Global.getOproject().syncDictINSERT = {}
            Global.getOproject().syncDictDELETE = {}

            # try:
            #     #print Global.getOproject().globalSyncDict[ZRid]
            #     #print Global.getOproject().globalSyncDictINSERT[ZRid]
            #     #print Global.getOproject().globalSyncDictDELETE[ZRid]
            # except:
            #     #print "No changes"


        #==================================
        # SYCHRONISE UPDATED/MODIFIED OBJECT"
        #==================================
        if len(Global.getOproject().globalSyncDict.keys()) !=0:
            #print "il existe des objets dans le dict des updates"
            for ZRdictKey in Global.getOproject().globalSyncDict.keys():
                ZRdict = Global.getOproject().globalSyncDict[ZRdictKey]
                if len(ZRdict.keys()) != 0:
                    #print "il existe %s objets pour la ZR %s dans le dict des updates" %(str(len(ZRdict.keys())), str(ZRdictKey))
                    Global.getOproject().nochange = False
                    try:
                        # print "try processUpdate"
                        self.processUpdate(ZRdict, pg_connection, pg_cursor, numrec)
                        # print "     process Udpate"
                        #print " reSyncDB.processUpdate mené"
                        #Check global desync variable to assess if some object are truly out-of-sync 
                        if not Global.getOproject().desync:
                            # print "Synchronisation de l'objet mis à jour"
                            Global.getOproject().synchronized_update = True  
                        else:
                            #They are out-of-sync objects
                            # QMessageBox.warning(
                            # None ,u"erreur desync: ", u"1402")

                            Global.getOproject().synchronized_update = False
                    except:
                        # QMessageBox.warning(
                        #     None ,u"exception processUpdate: ", u"1408")
                        Global.getOproject().synchronized_update = False
                        pass
                        # pg_connection.rollback()
        else:
            Global.getOproject().synchronized_update = True
            if Global.getOproject().nochange == None:
                Global.getOproject().nochange = True
            pass
            #TODO pop Warning

        # QMessageBox.warning(
        #                     None ,u"CAS: ", u"""  Global.getOproject().desync : %s \n Global.getOproject().synchronized_delete  :%s  \n Global.getOproject().synchronized_create : %s \n Global.getOproject().synchronized_update : %s \n Global.getOproject().dbrejected : %s \n nochange %s """%(Global.getOproject().desync, Global.getOproject().synchronized_delete ,Global.getOproject().synchronized_create , Global.getOproject().synchronized_update ,Global.getOproject().dbrejected ,Global.getOproject().nochange ))


        #If no object are out-of-sync:
        if not Global.getOproject().desync:
            #==================================
            #SYCHRONISE CREATED OBJECT"
            #==================================
            if len(Global.getOproject().globalSyncDictINSERT.keys()) !=0:
                for ZRdictKey in Global.getOproject().globalSyncDictINSERT.keys():
                    # #print ZRdictKey
                    ZRdict = Global.getOproject().globalSyncDictINSERT[ZRdictKey]
                    if len(ZRdict.keys()) != 0:
                        Global.getOproject().nochange = False
                        try:
                            self.processCreate(ZRdict, pg_connection, pg_cursor, numrec, ZRdictKey )
                            Global.getOproject().synchronized_create = True
                        except:
                            Global.getOproject().synchronized_create = False
                            pass
                            # pg_connection.rollback()
            else:   
                Global.getOproject().synchronized_create = True
                if Global.getOproject().nochange == None:
                    Global.getOproject().nochange = True
                pass
                #TODO pop Warning

            #==================================
            #SYCHRONISE DELETED OBJECT"
            #==================================
            if len(Global.getOproject().globalSyncDictDELETE.keys()) !=0:
                for ZRdictKey in Global.getOproject().globalSyncDictDELETE.keys():
                    ZRdict = Global.getOproject().globalSyncDictDELETE[ZRdictKey]
                    # #print ZRdict
                    if len(ZRdict.keys()) != 0:
                        Global.getOproject().nochange = False
                        try:
                            self.processDelete(ZRdict, pg_connection, pg_cursor, numrec )
                            Global.getOproject().synchronized_delete = True
                        except:
                            Global.getOproject().synchronized_delete = False
                            pass
                            # pg_connection.rollback().rollback()
            else:
                Global.getOproject().synchronized_delete = True
                if Global.getOproject().nochange == None:
                    Global.getOproject().nochange = True
                pass
                #TODO pop Warning




 
            #transtype to boolean
            if Global.getOproject().nochange == None:
                    Global.getOproject().nochange = False
            #======================================================================
            # IF PROJECT IS IN-SYNC WITH NO ERROR
            # Commit all Changes to the SERVER database; mark project has completed
            #======================================================================



            # QMessageBox.warning(
            #                 None ,u"CAS: ", u"""  Global.getOproject().desync : %s \n Global.getOproject().synchronized_delete  :%s  \n Global.getOproject().synchronized_create : %s \n Global.getOproject().synchronized_update : %s \n Global.getOproject().dbrejected : %s \n nochange %s """%(Global.getOproject().desync, Global.getOproject().synchronized_delete ,Global.getOproject().synchronized_create , Global.getOproject().synchronized_update ,Global.getOproject().dbrejected ,Global.getOproject().nochange ))



            if (Global.getOproject().synchronized_delete and Global.getOproject().synchronized_create 
                and Global.getOproject().synchronized_update and not Global.getOproject().dbrejected and not Global.getOproject().nochange):
                #print "Cas 1"
                
                # QMessageBox.warning(
                #             None ,u"CAS: ", u"""    cas 1   """)

                Global.getOproject().synchronized = True 
                pg_connection.commit()
                #Shelve Oproject
                copy_oproject = copy.deepcopy(Global.getOproject())
                self.writeProjectShelf(copy_oproject)
                # QMessageBox.about(
                #         None ,u"Projet Completé", u"""L'ensemble des modification ont été inscrite au serveur SIG40.""")
                # reSyncDB.generateReport()
                # return

            elif (Global.getOproject().synchronized_delete and Global.getOproject().synchronized_create 
                and Global.getOproject().synchronized_update and not Global.getOproject().dbrejected and Global.getOproject().nochange):
                #print "Cas 2"
                # QMessageBox.warning(
                #             None ,u"CAS: ", u"""    cas 2   """)
                #Shelve Oproject
                copy_oproject = copy.deepcopy(Global.getOproject())
                self.writeProjectShelf(copy_oproject)
                # QMessageBox.warning(
                #         None ,u"Projet vide", u"""Aucunes modifications n'ont été détectées""")
                # reSyncDB.generateReport()
                # return

            #======================================================================
            # IF PROJECT IS DE-SYNC OR SHOWS ERROR
            # Send DATABASE in previous state
            # Stop RESYNC by RETURN
            #======================================================================
            elif Global.getOproject().dbrejected:
                #print "Cas 3"
                # QMessageBox.warning(
                #             None ,u"CAS: ", u"""    cas 3   """)
                
                #mark project as non-synchronized
                Global.getOproject().synchronized = False
                #keep reference that the sync has been rejected
                Global.getOproject().dbrejected = True

                pg_connection.rollback()
                pg_connection_ZR.rollback()
                pg_connection_ZR.commit()
                
                #Error management required here
                QMessageBox.critical(
                            None ,u"Attention", u"""Synchronisation Interrompue
                            \nIl existe néanmmoins des objets modifiés au sein du Projet""")
                
                
                self.generateReport()
                #reinit the Dbrejected variable to allow reconcialiation re-attempt
                Global.getOproject().reinitResync()

                #Shelve Oproject
                copy_oproject = copy.deepcopy(Global.getOproject())
                self.writeProjectShelf(copy_oproject)

                #quit reconciliation attemp NOW!
                return

            #======================================================================
            # IF PROJECT IS DE-SYNC 
            # Send DATABASE in previous state
            # Try to give direction to the user for project correction
            #======================================================================
            elif (not Global.getOproject().synchronized_delete or not Global.getOproject().synchronized_create
                 or not Global.getOproject().synchronized_update):
                #keep going
                #print "Cas 4"
                # QMessageBox.warning(
                #             None ,u"CAS: ", u"""    cas 4   """)
                pass




            #============================================================================================================
            #USER INFORMATION - Pop some warning when nothing has been Synced
            #============================================================================================================
            if Global.getOproject().nochange:
                #Nothing to or has been updated
                nbrobj = 0
                try:
                    pg_connection_ZR.rollback()
                    pg_connection_ZR.commit()
                    pg_connection_ZR.close()
                    pg_connection.close()
                except:
                    pass

                for i in QgsMapLayerRegistry.instance().mapLayers().keys():
                    #print i
                    tabname = QgsMapLayerRegistry.instance().mapLayer(i).name()
                    #print tabname
                    if tabname != 'ZR' and tabname != 'Zone_Cliente' and tabname in Global.getOproject().tableDict.keys():
                        #REQUEST AND BUILD A LISTING OF LOCAL MODIFICATION
                        # _sqlstatement = "SELECT * FROM  %s WHERE ZRlocal != 0 AND userMod = 1 " %(tabname)
                        _sqlstatement = "SELECT * FROM  %s WHERE userMod = 1 " %(tabname)

                        #OPEN A CONNECTION TO THE LOCAL SQLITE TABLE
                        rt = LocalDB_utils.connect2LocalDb( tabname, Global.getOproject().currentProjectPath ) 
                        LOCAL_cursor = rt[0]
                        LOCAL_conn = rt[1]
                        LocalDB_utils.SQLinjection(LOCAL_cursor, str(_sqlstatement), False)
                        
                        
                        #EVALUATE HOW MANY MODIFICATIONS WERE PENDING
                        try:
                            recon = LOCAL_cursor.fetchall()
                            nbrobj = len(recon) + nbrobj
                            
                        except:
                            pass

                if nbrobj != 0:
                    
              
                    QMessageBox.critical(
                            None ,u"Attention", u"""Aucune Mise à jour n'a été effectuée
                            \nIl existe néanmmoins %d objets modifiés au sein du Projet
                            \nVeuillez vérifier que les entités à mettre à jour ont bien été inclusent au sein de Zone de Reconciliation""" %(nbrobj)) 
                    self.generateReport()
                else:
                    try:
                        pg_connection_ZR.rollback()
                    except:
                        pass

                    QMessageBox.warning(
                            None ,u"Attention Projet vide", u"""Aucune Mise à jour n'a été effectuée
                            \nAucune modification n'a été apportée au projet
                            \nVeuillez d'abord éditer vos données avant d'effectuer une réconciliation avec le serveur """)
            
            #If nochange = FALSE
            else:
                #DBs are in-Sync and have been synchronized; all has been committed
                #print "################################################"
                #==================================================================
                #Check if there are object that have not been synced (out-of-ZR)
                #==================================================================
                #Local counter
                nbrobj = 0
                tmp_tab = []
                for i in QgsMapLayerRegistry.instance().mapLayers().keys():
                    tabname = QgsMapLayerRegistry.instance().mapLayer(i).name()
                    if tabname != 'ZR' and tabname != 'Zone_Cliente' and tabname in Global.getOproject().tableDict.keys():
                        _sqlstatement = "SELECT * FROM  %s WHERE ZRlocal IN (-999, -666, 0) AND  userMod = 1 " %(tabname)

                        #OPEN A CONNECTION TO THE LOCAL SQLITE TABLE
                        rt = LocalDB_utils.connect2LocalDb( tabname, Global.getOproject().currentProjectPath ) 
                        LOCAL_cursor = rt[0]
                        LOCAL_conn = rt[1]
                        LocalDB_utils.SQLinjection(LOCAL_cursor, str(_sqlstatement), False)
                        
                        
                        #EVALUATE HOW MANY MODIFICATIONS WERE PENDING
                        try:
                            recon = LOCAL_cursor.fetchall()
                           
                            # #print type(recon), len(recon)
                            #Feed the oblivion dictionnary
                            for i in range(len(recon)):
                                tmp_tab.append(recon[i][0])
                            if len(recon) !=0:
                                Global.getOproject()._lostTable[tabname] = copy.copy(tmp_tab)

                            tmp_tab = []
                            nbrobj = len(recon) + nbrobj
                        except:
                            pass
                # IF nbrobj is not null, then some objects are Lost.
                if nbrobj != 0:
                    # give Warning but keep syncing
                    Global.getOproject().objectLost = True
                   
                    QMessageBox.warning(
                            None ,u"Attention Objets oubliés", u"""Certains objets modifiés/crées pendant la session session n'ont pas été inclus dans une zone de reconciliation. 
                            \nLe projet va être synchronisé sans inclures ces modification dans la base de données""")
                
                else:
                    pass 
                    # QMessageBox.warning(
                    #         None ,u"SYNC OK", u"""nochange : %s, objet restant : %s  """ %(Global.getOproject().nochange, str(nbrobj)))
                
                #Generate Success report
                try:
                    pg_connection_ZR.commit()
                    pg_connection_ZR.close()
                    pg_connection.close()
                except:
                    pass


                self.generateReport()


        else:
            try:
                pg_connection_ZR.rollback()
                pg_connection_ZR.commit()
                pg_connection_ZR.close()
            except:
                pass

            pg_connection.rollback()
            pg_connection.close()
            #print "DESYNC BUILD REPORT"
            #DBs are out-of-Sync
            #All desynchronisation are referenced and indexed within the UPDATE syncDict
            #Stop reconciliation and issue error report

            if len(Global.getOproject().globalSyncDict.keys()) !=0:
            #for each ZR
                for ZRdictKey in Global.getOproject().globalSyncDict.keys():
                    ZRdict = Global.getOproject().globalSyncDict[ZRdictKey]

                    if len(ZRdict.keys()) != 0:
                        #for each table
                        for TABkey in ZRdict.keys():

                            #open a pg connection;
                            pg_connection = PGDB_utils.staticConnection()
                            pg_cursor = pg_connection.cursor()

                            #retrieve primary key
                            _primarykey = PGDB_utils.getPrimaryKey(pg_connection, TABkey)
                            
                            #for each object
                            for objects in ZRdict[TABkey][0]:
                                if not objects[-2]:
                                    for i in objects[-1]:
                                        # #print objects

                                        #===============================================================================
                                        # FETCH DESYNCHRONISATION VALUES AND INFO
                                        # Retrieve from server Operator name and nature_operation corresponding to 
                                        # The current numrec value for Objects.table_name
                                        # - Who? 
                                        # - Which project?
                                        #===============================================================================

                                       
                                        
                                        #Build sql sql that join reciliation and public table based on unique id (PK)
                                        _sqlstatement = "SELECT c.%s, c.numrec, h.operateur, h.nature_operation, h.projet_qgis FROM %s c LEFT JOIN historique.reconciliation h "  %(str(ZRdict[TABkey][1][i]), str(TABkey))
                                        _sqlstatement += "ON c.numrec = h.numrec WHERE c.%s = %s LIMIT 1" %(_primarykey, objects[0])
                                        
                                        try:
                                            PGDB_utils._exec_sql(pg_connection, 
                                                pg_cursor, _sqlstatement )
                                            # #print pg_cursor.query
                                        except:
                                            pass

                                        try:
                                            result = pg_cursor.fetchall()
                                            # #print result

                                            server_value = str(result[0][0])
                                            if server_value == "None":
                                                server_value = "sys admin"
                                            server_operator = str(result[0][2])
                                            if server_operator == "None":
                                                server_operator = "sys admin"
                                            server_operation = str(result[0][3])
                                            if server_operation== "None":
                                               server_operation = "sys admin" 
                                            server_project = str(result[0][4]) 
                                            if server_project== "None":
                                               server_project = "sys admin"

                                        except:
                                            # #print "Fetch error 1636"
                                            server_value = "erreur requête"
                                            # #print "serveurvalue : ", server_value
                                            server_operator = "erreur requête"
                                            # #print "serveurop : ", server_operator
                                            server_operation = "erreur requête"
                                            # #print "server_operation : ",  server_operation
                                            server_project = "erreur requête"
                                            # #print "server_project : ", server_project


                                        try:
                                            if str(objects[i]) == str(unicode(server_value)):
                                                #warn user that is trying to update something that has already been updated:
                                                _html_string_warning = "<br> <dd> &#8594; Vous essayez de mettre à jour un attribut qui porte déjà la valeur désirée </dd></p>"
                                        except:
                                            pass

                                        try:
                                            _html_string += "<p> <b>ZR %s - Table %s - Objet %s </b> - Collision sur attribut <b>%s</b> <br> <dd> &#8594; valeur locale: <b> %s </b> " %(str(ZRdictKey),str(TABkey),str(objects[0]),str(ZRdict[TABkey][1][i]), str(objects[i]) )
                                            _html_string += "<br>  &#8594; valeur serveur <b> %s </b> <br>  &#8594; operation réalisée par opérateur <b>%s</b>, <br> &#8594; projet <b>%s</b>, au motif <b>%s</b>  </dd>  " %(  str(server_value), str(server_operator),str(server_project),str(server_operation)  )

                                            try:
                                                _html_string += _html_string_warning
                                                del _html_string_warning
                                            except:
                                                 _html_string += "</p>"                       
                                            

                                        except:
                                            #print "new _html_string"
                                            try:
                                                _html_string = "<p> <b>ZR %s - Table %s - Objet %s </b> - Collision sur attribut <b>%s</b>  <br> <dd> &#8594; valeur locale: <b> %s </b>" %(str(ZRdictKey), str(TABkey),str(objects[0]), str(ZRdict[TABkey][1][i]), str(objects[i]))
                                                _html_string += " <br>  &#8594; valeur serveur <b> %s </b>  <br> &#8594; operation réalisée par opérateur <b>%s</b>,  <br> &#8594; projet <b>%s</b>, au motif <b>%s</b> </dd>  " %(  str(server_value), str(server_operator),str(server_project),str(server_operation) )
                                                # _html_string += " valeur serveur <b> %s </b> (opération réalisée par opérateur <b>%s</b>, projet <b>%s</b>, au motif <b>%s</b> </p> ) " %( server_value,server_operator,server_project,server_operation  )
                                            except UnicodeEncodeError:
                                                _html_string = "<p> <b>ZR %s - Table %s - Objet %s </b> - Collision sur attribut <b>%s</b>  <br> <dd> &#8594; valeur locale: <b> non disponible - erreur encodage </b>" %(str(ZRdictKey), str(TABkey),str(objects[0]), str(ZRdict[TABkey][1][i]))
                                                _html_string += " <br>  &#8594; valeur serveur <b> %s </b>  <br> &#8594; operation réalisée par opérateur <b>%s</b>,  <br> &#8594; projet <b>%s</b>, au motif <b>%s</b> </dd>  " %(  str(server_value), str(server_operator),str(server_project),str(server_operation) )
                                                # _html_string += " valeur serveur <b> %s </b> (opération réalisée par opérateur <b>%s</b>, projet <b>%s</b>, au motif <b>%s</b> </p> ) " %( server_value,server_operator,server_project,server_operation  )
                                            try:
                                                _html_string += _html_string_warning
                                                del _html_string_warning

                                            except:
                                                 _html_string += "</p>"                       
                                            

                                    
                                        # #print "ZR %s - Collision sur attribut %s (valeur locale %s) dans table %s " %(str(ZRdictKey),str(ZRdict[TABkey][1][i]), str(objects[i]), TABkey)
                pg_connection.close()
                # #print _html_string
                self.finalizeAndPublish(_html_string)
            else:
                #error in dict structure
                pass


    def writeProjectShelf(self,oproject):

        # Test if the shelf is already open/needs to be open
        _shelve = os.path.join(oproject.currentProjectPath, 'shelf_PP.db')
        shelve_project_parameters = shelve.open(_shelve)

        # Construct the shelve:
        try:
            shelve_project_parameters['object'] = oproject
            #===================================================================
            # shelve_project_parameters['general_info'] = {
            #     'project_name': self.project_name, 'project_path': self.project_path, 'project_date': self.creationDate, 'project_user': self.user}
            # shelve_project_parameters['geographic_info'] = {
            #     'ZC': self.ZC, 'ZR': self.ZR}
            #===================================================================
        finally:
            shelve_project_parameters.close()

        # #print "Project Shelved!"


    def generateReport(self,):

        #Build a report Dictionnary
        # reportDict = {}
        
        #report table structure: [ Status Global, StatutMaj, StatusAjout,
        #                          StatutSuppr , NbreMaj, NbreAjout, NbreSuppr ]
     
        if Global.getOproject().dbrejected == True:
            reporttable = [False,False,False,False,0,0,0]
        else:
            reporttable = [True,True,True,True,0,0,0]

        #Feed the report Dictionnary
     
        # QMessageBox.warning(
        #                     None ,u"Generate report", u"""Global.getOproject().dbrejected %s """ %(Global.getOproject().dbrejected))

        #=======================================================================
        # PROCESS OBJECT UPDATE
        #=======================================================================
        for ZRkey in range(1, Global.getOproject().ZRtriggercount + 1):
            layerDict = {}
            try:
                for TABkey in Global.getOproject().globalSyncDict[ZRkey].keys():
                    
                    ZRdict = Global.getOproject().globalSyncDict[ZRkey][TABkey]
                    
                    #pour chaque objets reconciliés de cette couche au sein de cette ZR
                    #retourn le nbre d'objet reconcilié
                    nbrObj = len(ZRdict[0])
                    # #print "UPDATE, ", ZRkey, TABkey, nbrObj
                    reporttable[4] = copy.copy(nbrObj)
                    
                    for i in range(0,nbrObj):
                        objet = ZRdict[0][i]
                        #Check if there are De-Sync Objects
                        if objet[-2] == True:
                            continue
                        else:
                           reporttable[1] = False
                           reporttable[0] = False

                    layerDict[TABkey] = copy.copy(reporttable)
                    #reset the container report table

                    if Global.getOproject().dbrejected:
                        reporttable = [False,False,False,False,0,0,0]
                    else:
                        reporttable = [True,True,True,True,0,0,0]
                    
                    #Pass the layerDict to the reportDict top container
                    Global.getOproject().reportDict[ZRkey] = copy.copy(layerDict)
                    # #print  reportDict[ZRkey] 
                    
            except:
                pass

        #=======================================================================
        # PROCESS OBJECT CREATE
        #=======================================================================
            try: 
                for TABkey in Global.getOproject().globalSyncDictINSERT[ZRkey].keys():
                    ZRdict = Global.getOproject().globalSyncDictINSERT[ZRkey][TABkey]
                    
                    #pour chaque objets reconciliés de cette couche au sein de cette ZR
                    #retourn le nbre d'objet reconcilié
                    nbrObj = len(ZRdict[0])
                    # #print "CREATE, ", ZRkey, TABkey, nbrObj
                    for i in range(0,nbrObj):
                        objet = ZRdict[0][i]
                        try:
                            Global.getOproject().reportDict[ZRkey][TABkey][5] = copy.copy(nbrObj)
                            #Check if there are De-Sync Objects
                            
                        
                        except:
                            reporttable[5] = copy.copy(nbrObj)
                            #Check if there are De-Sync Objects
                            
                            
                            layerDict[TABkey] = copy.copy(reporttable)
                            #reset the container report table
                            if Global.getOproject().dbrejected:
                                reporttable = [False,False,False,False,0,0,0]
                            else:
                                reporttable = [True,True,True,True,0,0,0]

                            #Pass the layerDict to the reportDict top container
                            Global.getOproject().reportDict[ZRkey] = copy.copy(layerDict)

            except:
                pass


        #=======================================================================
        # PROCESS OBJECT DELETE
        #=======================================================================
            try:
                for TABkey in Global.getOproject().globalSyncDictDELETE[ZRkey].keys():
                    ZRdict = Global.getOproject().globalSyncDictDELETE[ZRkey][TABkey]

                    # QMessageBox.warning(
                    #         None ,u"PROCESS OBJECT DELETE", u"""PROCESS OBJECT DELETE """)
       
       
                    #pour chaque objets reconciliés de cette couche au sein de cette ZR
                    #retourn le nbre d'objet supprimé
                    nbrObj = len(ZRdict[0])
                    # #print "DELETE, ", ZRkey, TABkey, nbrObj
                    for i in range(0,nbrObj):
                        objet = ZRdict[0][i]
                        try:
                            Global.getOproject().reportDict[ZRkey][TABkey][6] = copy.copy(nbrObj)
                            #Check if there are De-Sync Objects
                            
                        
                        except:
                            reporttable[6] = copy.copy(nbrObj)
                            #Check if there are De-Sync Objects
                            
                            
                            layerDict[TABkey] = copy.copy(reporttable)
                            #reset the container report table
                            if Global.getOproject().dbrejected:
                                reporttable = [False,False,False,False,0,0,0]
                            else:
                                reporttable = [True,True,True,True,0,0,0]

                            #Pass the layerDict to the reportDict top container
                            Global.getOproject().reportDict[ZRkey] = copy.copy(layerDict)
            except:
                pass

        # QMessageBox.warning(
        #                     None ,u"Global.getOproject().reportDict", u""" Global.getOproject().reportDict : %s """ %(Global.getOproject().reportDict))
       
        Global.getOproject().html_reportdict = self.dict_to_html_table(Global.getOproject().reportDict)
        

        if Global.getOproject().dbrejected:

            Global.getOproject().html_errordict =  self.dict_to_html_table_error(Global.getOproject()._errortable)
            self.finalizeAndPublish(Global.getOproject().html_reportdict, Global.getOproject().html_errordict )
            #self.sendMailReport()

        elif Global.getOproject().objectLost:

            Global.getOproject().html_obliviondict =  self.dict_to_html_table_oblivion(Global.getOproject()._lostTable)
            self.finalizeAndPublish(Global.getOproject().html_reportdict, Global.getOproject().html_obliviondict )
            #self.sendMailReport()

        else:
            # QMessageBox.warning(
            #                 None ,u"Global.getOproject().reportDict", u"""  %s """ %(Global.getOproject().html_reportdict))
  
            self.finalizeAndPublish(Global.getOproject().html_reportdict)
            #self.sendMailReport()


    def dict_to_html_table(self,in_dict):
        """
        Build an Html table to report the DB synchronisation report after sync attempt
        """
        container = []

        for zr,tabledict in in_dict.iteritems():
            
            #print zr,tabledict

            tbl_fmt = '''
            <table class="names">
                <caption><p style="color: #000000; font-size: 12pt" lang="fr" xml:lang="fr" ><b> Zone de R&eacute;conciliation Num&eacute;ro %s </b> </p></caption>
                    <tr>
                            <th>Couches</th>
                            <th>Statut</th>
                            <th>Objets <br /> mis &agrave; jour </th>
                            <th>Objets <br /> ajout&eacute;s </th>
                            <th>Objets <br /> supprim&eacute;s </th>
                        </tr>
                    {}
            </table>'''%(zr)

            row_fmt  = '''
              <tr>
                <td>{}</td>
                <td {}</td>
                <td{}</td>
                <td{}</td>
                <td{}</td>

              </tr>'''

            container.append(  tbl_fmt.format(''.join([row_fmt.format(k, #layer name
                                    """style="color: #66FF66; font-size: 12pt; font-weight: bold" >OK""" if v[0] else """style="color: #FF3333; font-size: 12pt; font-weight: bold" >Failed"""   ,#Sync status
                                    "> "+str(v[4]) if v[4] != 0 else ' style="background-color: #c1c1c1">'  , #number of object
                                    "> "+str(v[5]) if v[5] != 0 else ' style="background-color: #c1c1c1">'  ,
                                    "> "+str(v[6]) if v[6] != 0 else ' style="background-color: #c1c1c1">'  )
                                            for k,v in tabledict.iteritems()]))
                            )
        try:
            _tablehtml = container[0]
            for i in range(1,len(in_dict.keys()) ):
                _tablehtml += container[i]

            # #print _tablehtml
            return _tablehtml
        except:
            pass

    def dict_to_html_table_error(self,in_dict):
        """
        Build an Html table to report the DB writing errors after sync attempt
        """
        container = []
        #print "A"
        tbl_fmt = '''
            <table class="names">
                <caption><p style="color: #000000; font-size: 12pt" lang="fr" xml:lang="fr" ><b> Erreur de typage/contraintes non respect&eacute;es</b> </p></caption>
                    <tr>
                            <th>ZR</th>
                            <th>Message PostgreSQL</th>
                            
                        </tr>
                    {}
            </table>'''

        row_fmt  = '''
              <tr>
                <td>{}</td>
                <td {}</td>

              </tr>'''

        #print "b"
        #print in_dict.keys()
        for zr in in_dict.keys():
            
            #print zr

            container.append(  tbl_fmt.format(''.join([row_fmt.format(zrnum, #ZR Name
                                    "> "+_error )
                                            for zrnum,_error in in_dict.iteritems()]))
                            )
        try:
            _tablehtml = container[0]
            for i in range(1,len(in_dict.keys()) ):
                _tablehtml += container[i]

            # #print _tablehtml
            return _tablehtml
        except:
            pass

    def dict_to_html_table_oblivion(self,in_dict):
        """
        Build an Html table to report objet that are not ZR referenced 
        """
        container = []
        #print "A"
        tbl_fmt = '''
            <table class="names">
                <caption><p style="color: #000000; font-size: 12pt" lang="fr" xml:lang="fr" ><b> Objet modifi&eacute;s mais non ref&eacute;renc&eacute;s</b> </p></caption>
                    <tr>
                            <th>Table</th>
                            <th>Id</th>
                            
                        </tr>
                    {}
            </table>'''

        row_fmt  = '''
              <tr>
                <td>{}</td>
                <td {}</td>

              </tr>'''

        #print "b"
        #print in_dict.keys()
        for zr in in_dict.keys():
            
            #print zr

            container.append(  tbl_fmt.format(''.join([row_fmt.format(zrnum, #ZR Name
                                    "> "+', '.join(str(j) for j in _error) )
                                            for zrnum,_error in in_dict.iteritems()]))
                            )
        try:
            _tablehtml = container[0]
            for i in range(1,len(in_dict.keys()) ):
                _tablehtml += container[i]

            # #print _tablehtml
            return _tablehtml
        except:
            pass

    def finalizeAndPublish(self,_tablehtml, *args):
        import webbrowser
        import datetime


        #print "Global.getOproject().synchronized: ", Global.getOproject().synchronized
        #print "Global.getOproject().dbrejected: ", Global.getOproject().dbrejected
        #print "Global.getOproject().objectLost: ", Global.getOproject().objectLost


        f = open('rapport_de_reconciliation.html','w')
        plugin_path = os.path.dirname(os.path.realpath(__file__))


        if _tablehtml == None:
            status = 'finalisée sans aucune modification'
            _tablehtml = "Aucun objet modifié sur la base"
            image = os.path.join(
                plugin_path, "ressources","resources","questionmark.jpg")

        elif Global.getOproject().synchronized and not Global.getOproject().dbrejected and not Global.getOproject().objectLost:
            status = 'Finalisée'
            image = os.path.join(
                plugin_path, "ressources","resources","smile.jpg")

        elif not Global.getOproject().synchronized and not Global.getOproject().dbrejected and not Global.getOproject().objectLost:
            status = 'Abandonnée - Veuiller résoudre les conflits avant de poursuivre'
            image = os.path.join(
                plugin_path, "ressources","resources", "warning-icon-md.png")

        elif not Global.getOproject().synchronized and  Global.getOproject().dbrejected:
            status = 'Abandonnée - La base de donnée a rejeté les modifications - Veuillez vérifier le typage et/ou les valeurs des objets modifiés '
            image = os.path.join(
                plugin_path, "ressources","resources", "warning-icon-md.png")
            #Build a table to show errors

        elif  Global.getOproject().synchronized and Global.getOproject().objectLost:
            status = 'Partielle - Certains objets ne sont référencés dans aucune ZR '
            image = os.path.join(
                plugin_path, "ressources","resources", "warning-icon-md.png")
            #Build a table to show errors


        date = datetime.date.today().isoformat()
        

        


        message =""" <!doctype html>
        <head>
            <meta charset="utf-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
            <title>Rapport de reconciliation </title>
            <meta name="description" content="Rapport de reconciliation sig40Dialog."/>
            <meta name="plugin SIG40" content="Conseil Général des Landes"/>
            <meta name="GPL2" content="Based on PyQT, PyQGIS and other GPL python libraries"/>
        

            <style>
                    table, th, td {
                        border: 1px solid black;
                        border-collapse: collapse;
                       
                    }
                    th, td {
                        padding: 15px;
                    }
                    table.names th  {
                        background-color: #c1c1c1;
                    }           
                </style>

        </head>
        <body>
         
        <div class="row">
            <div class="large-12 columns">

                <h1>Rapport de Réconciliation: <small>Cette réconciliation est %s.</small></h1>
                <hr/>
            </div>
        </div>
         
         
        <div class="row">
         
            <div class="large-9 columns" role="content">
                <article>

                <h6>Généré par <a href="#">Qgis ProjectXL Plugin</a> le %s </h6>


                <div class="large-6 columns">
                    <img src="%s" width="400" />
                </div>
            </div>
                <p> % s </p>
                </article>
                <hr/>
        <div>"""%(status, date, image, _tablehtml)

        try:
            message +=  """<div class="row">
                <article>
                <h3>Complément d'information</h3>
                    <p> % s </p>
                </article>
                <hr/>
            <div>"""%(args[0])

        except:
            pass
         
        message+= """<footer class="row">
        <p> Fin de rapport </p> 
        </footer>

        </body>
        </html>""" 

        f.write(message)
        f.close()

        webbrowser.open_new('rapport_de_reconciliation.html')
            
    def sendMailReport(self):

       

        # Define these once; use them twice!
        strFrom = u"message automatique <pluginSig40@cg40.fr>"
        # strTo = 'pierre.foicik@cg40.fr'
        strTo = 'bal.sig@cg40.fr'

        # Create the root message and fill in the from, to, and subject headers
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = u'Rapport de reconciliation généré par utilisateur '+str(Global.getOproject().username)
        msgRoot['From'] = strFrom
        msgRoot['To'] = strTo
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        msgText = MIMEText('ce message doit comporter un rapport de reconciliation')
        msgAlternative.attach(msgText)


        f = open('rapport_de_reconciliation.html','rb')
        _mess = f.read()
        _mess = self.remove_img_tags(_mess)
        # We reference the image in the IMG SRC attribute by the ID we give it below
        msgText = MIMEText(_mess, 'html')

        msgAlternative.attach(msgText)

       
        # Send the email (SMTP, no authentication is required)
        import smtplib
        smtp = smtplib.SMTP()
        smtp.connect('172.17.1.15', 25)

        #Identify to ESMTP server.
        #Put SMTP connection in TLS mode and call ehlo again.

        smtp.sendmail(strFrom, strTo, msgRoot.as_string())
        smtp.quit()

    def remove_img_tags(self,data):
        p = re.compile(r'<img.*?/>')
        return p.sub('', data)
            

            
