'''
Created on 17 juil. 2014

@author: pierre foicik
pierre.foicik@gmail.com
'''

from pyspatialite import dbapi2 as db
from sig40.global_mod import Global


class OSqlite(object):

    '''
    This Class init a Locale SQlite/Spatialite DB required when building a XL project session
    This locale DB is owned by the local user
    This Class require importing:

    - pyspatialite info @ https://github.com/lokkju/pyspatialite
    - sqlite3

    '''

    def __init__(self, dbname="localDB"):
        '''
        Create a spatially enabled SQlite DB and write it to disk 
        One geometry column 'geom', type POLYGON
        Keyword arguments:
        dbname -- the database name; default to localDB
        '''
        # Build a
        # creating/connecting the test_db
        conn = db.connect(dbname + '.sqlite')

        # creating a Cursor
        cur = conn.cursor()

        # testing library versions
        rs = cur.execute('SELECT sqlite_version(), spatialite_version()')
        for row in rs:
            msg = "> SQLite v%s Spatialite v%s" % (row[0], row[1])
            print msg

        #======================================================================
        # sql = "CREATE TABLE '" + dbname + \
        #     "' (  id INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT )"
        # cur.execute(sql)
        #======================================================================

        # initializing Spatial MetaData
        # using v.2.4.0 this will automatically create
        # GEOMETRY_COLUMNS and SPATIAL_REF_SYS
        sql = 'SELECT InitSpatialMetadata()'
        cur.execute(sql)

        # creating a POINT table
        sql = 'CREATE TABLE ' + dbname + '('
        sql += 'id INTEGER NOT NULL PRIMARY KEY, '
        sql += 'indexZR INTEGER,'
        sql += 'description TEXT)'
        #sql += 'name TEXT NOT NULL)'
        cur.execute(sql)
        # creating a POINT Geometry column
        sql = "SELECT AddGeometryColumn('" + dbname + "',"
        sql += "'geom' ," + \
            str(Global.getOproject().getSrid()) + ", 'POLYGON', 'XY')"
        cur.execute(sql)

        # initializing Spatial MetaData, REQUIRE pyspatialite
        # using v.2.4.0 this will automatically create
        # GEOMETRY_COLUMNS and SPATIAL_REF_SYS
        sql = 'SELECT InitSpatialMetadata()'
        cur.execute(sql)

        sql = "SELECT AddGeometryColumn('" + \
            dbname + "', 'geom',-1, 'POLYGON', 'XY', 0);"

        conn.commit()
        conn.close()


    @staticmethod
    def CreateSpatialDB(dbname="localDB"):
        '''
        Create a spatially enabled SQlite DB and write it to disk 
        One geometry column 'geom', type POLYGON
        Keyword arguments:
        dbname -- the database name; default to localDB

        TODO: make this method generic as it create 
        a fix-format DB for now LocalDB, table LocalDB, field[id;index; description]

        '''
        # Build a
        # creating/connecting the test_db
        conn = db.connect(dbname + '.sqlite')

        # creating a Cursor
        cur = conn.cursor()

        # testing library versions
        rs = cur.execute('SELECT sqlite_version(), spatialite_version()')
        for row in rs:
            msg = "> SQLite v%s Spatialite v%s" % (row[0], row[1])
            print msg

        #======================================================================
        # sql = "CREATE TABLE '" + dbname + \
        #     "' (  id INTEGER NOT NULL  PRIMARY KEY AUTOINCREMENT )"
        # cur.execute(sql)
        #======================================================================

        # initializing Spatial MetaData
        # using v.2.4.0 this will automatically create
        # GEOMETRY_COLUMNS and SPATIAL_REF_SYS
        sql = 'SELECT InitSpatialMetadata()'
        cur.execute(sql)

        # creating a POINT table
        sql = 'CREATE TABLE ' + dbname + '('
        sql += 'id INTEGER NOT NULL PRIMARY KEY, '
        sql += 'indexZR INTEGER,'
        sql += 'description TEXT)'
        #sql += 'name TEXT NOT NULL)'
        cur.execute(sql)
        # creating a POINT Geometry column
        sql = "SELECT AddGeometryColumn('" + dbname + "',"
        sql += "'geom' ," + \
            str(Global.getOproject().getSrid()) + ", 'POLYGON', 'XY')"
        cur.execute(sql)

        # initializing Spatial MetaData, REQUIRE pyspatialite
        # using v.2.4.0 this will automatically create
        # GEOMETRY_COLUMNS and SPATIAL_REF_SYS
        sql = 'SELECT InitSpatialMetadata()'
        cur.execute(sql)

        sql = "SELECT AddGeometryColumn('" + \
            dbname + "', 'geom',-1, 'POLYGON', 'XY', 0);"

        conn.commit()
        conn.close()

    def addTable(self):
        pass
