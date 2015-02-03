# -*- coding: utf-8 -*-

'''
Created on 15 juil. 2014
@author: pierre foicik
pierre.foicik@gmail.com
'''


from OProject import OProject

oproject = OProject()


class Global(object):

    '''
    Encapsulate Global variable and objects for project persistance
    Give Access to the oproject main object ---> Global.getOproject()
    Keep all Default variables:
    HostName should be the default IP adress for the remote PG server (localhost = LOCAL!)
    BDname should stay as postgres as long a the default postgres DB has been kept on the server


    '''
    

    oproject = oproject
    projectXL = None
    projectname = None
    PG_connection = None
    providerLib = "postgres"
    BDname = "postgres"
    defaultPort = 5432
    # Hostname is a STRING! ex="172.0.0.1" or "sig40"
    HostName = "localhost"
    userName = None
    dummyLayerId = None
    ZRtriggercount = 0
    connectionstatus = False
    projpath = None

    # window persistance
    mw = None
    cw = None

    #Reconciliation Table name; including schema
    zr_table_name = "historique.reconciliation"
    

    #Motif de reconciliation
    liste_motif = ["Motif Omis", "Motif 0", "Motif 1", "Motif 2", "Motif 3", "Motif 4", "Motif 5"]
    #Hold a shape that covers the entire 'canton' area
    env_canton = "POLYGON((334310 6273200, 334310 6397000, 474000 6397000, 474000 6273200, 334310 6273200)), 2154"
    dict_form_pre = {'--select--': "",'canton': env_canton}
    name_form_pre = ('--select--','canton')
    list_form_pre = ("", env_canton)

    # Work with Sample for the table from SIG40 for Dev.
    DBreduxBool = False


    #Datatype equivalence [PG,SQLITE]
    PGdataType = ['bigint', 'timestamp without time zone', 'boolean', 'character varying']
    SQLITEdatatype = ['long', 'unicode', 'unicode', 'unicode', 'unicode']  
    listedate_nom = ['date_d_actualite','date_de_creation', 'date_de_modification' , 'date_de_suppression' ]


    #Config Widget Attributes to predefined specific Table field values
    #Field are controlled and set @ OGeoDB.OQgis.setEditType
    immutable_field = ['date_de_creation','date_de_suppression', 'date_de_modification', 'detruit', 'identifiant', 'numrec', 'cle_primaire',
                        'userMod', 'userAdd', 'pk', 'userDel', 'original_pk', 'ZRlocal', 'ZRnew']
    calendar_field = ['date_d_actualite']
    source_donnee_field = ['source_de_la_geometrie']
    source_donnee_field_config = {u'Levé GPS':u'Levé GPS', u'Levé non GPS':u'Levé non GPS', u'PCI':u'PCI', u'BDOrtho':u'BDOrtho',
                                    u'BDTopo':u'BDTopo', u'BDCarto':u'BDCarto', u'Scan25':u'Scan25'}
    calendar_field_config = {u'display_format': u'yyyy-MM-dd HH:mm:ss', u'field_format': u'yyyy-MM-dd HH:mm:ss', u'calendar_popup': True}
    
    @staticmethod
    def reset():
        Global.oproject = oproject
        Global.projectXL = None
        Global.projectname = None
        Global.PG_connection = None
        Global.providerLib = "postgres"
        Global.BDname = "postgres"
        Global.defaultPort = 5432
        Global.HostName = "localhost"
        Global.userName = None
        Global.dummyLayerId = None
        Global.ZRtriggercount = 0
        Global.connectionstatus = False
        Global.projpath = None

        # window persistance
        Global.mw = None
        Global.cw = None


    @staticmethod
    def setProjectName(projectname):
        Global.projectname = projectname

    @staticmethod
    def getProjectName():
        return Global.projectname

    @staticmethod
    def delCw():
        Global.cw = None

    @staticmethod
    def setCw(cw):
        Global.cw = cw

    @staticmethod
    def getCw():
        return Global.cw

    @staticmethod
    def delMw():
        Global.mw = None

    @staticmethod
    def setMw(mw):
        Global.mw = mw

    @staticmethod
    def setPort(port):
        Global.defaultPort = port

    @staticmethod
    def getPort():
        return Global.defaultPort

    @staticmethod
    def getMw():
        return Global.mw

    @staticmethod
    def getUserName():
        return Global.userName

    @staticmethod
    def setUserName(name):
        Global.userName = name

    @staticmethod
    def setHostName(host):
        Global.HostName = host

    @staticmethod
    def getHostName():
        return Global.HostName

    @staticmethod
    def setBDname(bdname):
        Global.BDname = bdname

    @staticmethod
    def getBDname():
        return Global.BDname

    @staticmethod
    def setPG_connection(pgconnection):
        Global.PG_connection = pgconnection

    @staticmethod
    def getPG_connection2():
        return Global.PG_connection

    @staticmethod
    def getPG_connection():
        return Global.projectXL.postgres_connection

    @staticmethod
    def delPG_connection():
        del Global.projectXL.postgres_connection

    @staticmethod
    def getProjectXL():
        return Global.projectXL

    @staticmethod
    def setprojectXL(projectXL):
        Global.projectXL = projectXL

    @staticmethod
    def getOproject():
        return Global.oproject

    @staticmethod
    def setOproject(oproject):
        Global.oproject = oproject

    @staticmethod
    def dataProvider():
        return Global.providerLib
