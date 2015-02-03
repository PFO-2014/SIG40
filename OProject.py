'''
Created on 10 juil. 2014
@author: pierre foicik
pierre.foicik@gmail.com
'''

import getpass
import os
#=========================================================================
# from qgis.core import QgsMapLayerRegistry, QgsProject
# from qgis.gui import QgsMapCanvas
#=========================================================================
import time


class OProject(object):

    '''
    This class is a object container that Records the Project configuration
    This Class provide a fully serializable object to build project persistance
    This Class is serialized throught the python shelve module

    NB: the shelve process should be a method of this object - NOT the CASE NOW!

    '''

    def __init__(self):
        '''
        Constructor
        '''

        # Boolean varaible to track reconciliation state
        # Any of this variable is set to false, project reconiliation will abort
        # and any changes on the server DB will be rolled-back
        self.desync = False
        self.synchronized = False
        self.synchronized_update = False
        self.synchronized_create = False
        self.synchronized_delete = False
        # Boolean in case data are rejected by the database (not compliant with type or constraint)
        self.dbrejected = False
        # Boolean in case no changes have been made to the dataset
        self.nochange = None
        # Boolean to mark presence of non-ZR referenced objects
        self.objectLost = False
        self._lostTable = {}
        # Dict to keep reference of DB error at writing time
        # Dictionnary format: {zr: error}
        self._errortable = {}
        # Number of modified object
        self.modificationcounter = 0
        # Numrec dictionnary - Key = localZRid
        self._numrecdict = {}
        #Build a report Dictionnary to build and track changes 
        self.reportDict = {}
        self.html_reportdict = None
        self.html_obliviondict = None
        self.html_reportdict = None

        self.project_name = None
        self.project_path = None
        self.currentProjectPath = None
        self.crs = None
        self.srid = None
        self.ZC = None
        self.user = None
        #give a temporary reference when creatin a new ZR
        self.tmpZR = None

        #The Table Dictionnary
        self.tableDict = None
        self.ZRtriggercount = 0

        #PG connection information persistance for the project
        self.username = None
        self.host = None
        self.port = None
        self.dbname = None
        self.passwd = None

        #Top level desynchronisation Dict encapsulation; key = ZRid
        self.globalDeSyncDict = {}
        #Top level synchronisation Dict encapsulation; key = ZRid
        self.globalSyncDict = {}
        #Prepare an empty "synchronisation's dictionnary" dedicated to UPDATE
        self.syncDict = {}
        #Top level synchronisation Dict encapsulation INSERTION; key = ZRid
        self.globalSyncDictINSERT = {}
        #Prepare an empty "synchronisation's dictionnary" dedicated to INSERTION
        self.syncDictINSERT = {}
        #Top level synchronisation Dict encapsulation DELETE; key = ZRid
        self.globalSyncDictDELETE = {}
        #Prepare an empty "synchronisation's dictionnary" dedicated to DELETE
        self.syncDictDELETE = {}
        # list of tuple [( tablename, geometry_column_name  )]
        self.tablelistgeom = None


    def reinitResync(self):
        """
        reinit all variable to pre-resync state
        to allow resync re-attempt
        """

        self.dbrejected = False
        self.desync = False
        self.synchronized = False
        self.synchronized_update = False
        self.synchronized_create = False
        self.synchronized_delete = False
        self.dbrejected = False
        self.nochange = None
        self.objectLost = False
        self._lostTable = {}
        self._errortable = {}
        self.modificationcounter = 0
        self._numrecdict = {}
        self.reportDict = {}
        self.html_reportdict = None
        self.html_obliviondict = None
        self.html_reportdict = None
        self.globalDeSyncDict = {}
        self.globalSyncDict = {}
        self.syncDict = {}
        self.globalSyncDictINSERT = {}
        self.syncDictINSERT = {}
        self.globalSyncDictDELETE = {}
        self.syncDictDELETE = {}


    def setCcrs(self,  crs):
        """
        Keep track of the crs
        """
        self.crs = crs
        self.srid = crs[5:]

    def getCcrs(self):
        """
        Retrieve crs as str
        """
        return self.crs

    def getSrid(self):
        """
        Retrieve srid as str
        """
        return self.srid

    def setTableListGeom(self, table_list_geom):
        '''
        keep track of the geometry table within the server DB
        '''
        self.tablelistgeom = table_list_geom

    def setCurrentProjectPath(self, current_proj_path):
        '''
        Path string to Project Folder ./current
        '''
        self.currentProjectPath = current_proj_path

    def setProjectPath(self, project_path):
        '''
        Path string to Project Folder
        '''
        self.project_path = project_path

    def setProjectName(self, project_name):
        '''
        project name
        '''
        self.project_name = project_name

    def setZC(self, zone_cliente):
        '''
        WKB representation of the client zone
        '''
        self.ZC = zone_cliente

    def setZR(self, zone_reconciliation):
        '''
        ZR is an objet that contain:
            - Purpose of the ZR (string)
            - List of table related to the ZR
            - User owner of this ZR
            - Date
        '''
        self.ZR.append(zone_reconciliation)
