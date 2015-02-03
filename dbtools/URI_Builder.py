# -*- coding: utf-8 -*-

'''
Created on 4 juil. 2014
@author: pierre foicik
pierre.foicik@gmail.com
'''
import getpass
from qgis.core import QgsDataSourceURI
from sig40.global_mod import Global
from sig40.utils_sig40.ErrorMessage import errorMessage


class URI_Builder(object):

    '''
    This Class build an URI required by the QgsVectorLayer(uri, name, provider) to make a connection on a PG database
    User is defaulted to getpass.getuser() ( equivalent to os.getlogin() - work for both linux and windows platforms)
    '''

    # def __init__(self, host="localhost", port="5432", bd="stage",
    # user=getpass.getuser(), schema="public", table="epci",
    # champ="geometrie", *args):

    def __init__(self, table, host=Global.getHostName(), port="5432", bd=Global.getBDname(), user=getpass.getuser(), password="", schema="public",  *args):
        '''
        Build an URI
        Set a connection 
        Set a DB path to a specific Schema->Tabel->Field
        Keyword Parameters:
        One parameter required, table name
        args[0] for SQL injection, str expected
        '''
        try:
            asql = args[0]
        except:
            asql = ''
            pass

        self.uri = QgsDataSourceURI()


        # print Global.getPG_connection().tableListWithGeomDict.keys()
        try:

            self.uri.setConnection(host, port, bd, user, password)
            self.champgeom = Global.getPG_connection().tableListWithGeomDict[
                str(table)][1]
            self.uri.setDataSource(schema, table, self.champgeom, asql)

        except KeyError, e :
            mess = unicode("Selection d'une table invalide: %s , veuillez vérifier les paramètres de connection et/ou la table selectionnnée" %(e), 'utf-8')
            errorMessage(mess)
            



        

        

        

    def getUri(self):
        '''
        Return a connection
        '''
        return self.uri

    def getDBpath(self):
        '''
        Return a DBpath
        '''
        return self.uri.uri()

    @staticmethod
    def static_testing_uri():
        host = "localhost"
        port = "5432"
        bd = "stage"
        user = getpass.getuser()
        schema = "public"
        table = "epci"
        champ = "geometrie"
        polygone = "POLYGON((355900 6330300, 455900 6330300,455900 6230300,355900 6230300, 355900 6330300  ))"
        asql = "ST_WITHIN(ST_CENTROID(geometrie), ST_GeomFromText('POLYGON((355900 6430300, 455900 6430300,455900 6230300,355900 6230300, 355900 6430300  ))', 2154) )"

        uri = QgsDataSourceURI()
        uri.setDataSource(schema, table, champ, asql)
        uri.setConnection(host, port, bd, user, "")
        return uri.uri()
