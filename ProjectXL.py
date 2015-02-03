'''
Created on 17 juil. 2014

@author: pierre foicik
pierre.foicik@gmail.com
'''

from dbtools.OGeoDB import OGeoDB
from OProject import OProject
#from dbtools.OSqlite import OSqlite


class ProjectXL(object):

    '''
    This Class prepare a XL project session owned by and customized for the local user

    - Build an appropriate File Tree 

    - Shelve custom metatada for project persitence, allow to start/end/reload a project session
    - Start a QGIS project serving allowed data out of the SIG40 DB

    '''

    def __init__(self):
        '''
        Constructor
        '''
        # Instanciate a OProject that will encapsulate all metadata for the
        # session being build
        self.postgres_connection = OGeoDB()


