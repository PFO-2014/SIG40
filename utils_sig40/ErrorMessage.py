# -*- coding: utf-8 -*-

'''
Created on 29 juil. 2014

@author: pierre
'''

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QSize
from PyQt4.QtGui import QMessageBox, QDialog, QPixmap, QPushButton, QLineEdit,  QWidget, QSizePolicy
from sig40.global_mod import Global
from qgis.core import *
from qgis.gui import *


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class errorMessage(QDialog):

    """
    Container window to report raised error
    """

    def __init__(self, mess):

        super(errorMessage, self).__init__()

        msgBox = QMessageBox()
        msgBox.setWindowTitle("Erreur")
        msgBox.setText(mess)
        tmp = QPixmap(":/ourapp/warning")
        icon = QPixmap(tmp.scaled(QSize(32, 32)))
        print icon.size()
        msgBox.setIconPixmap(icon)
        msgBox.addButton(
            QPushButton('continue'), QMessageBox.NoRole)

        ret = msgBox.exec_()

        if ret == True:
            return





class errorConnection(QDialog):

    """
    Dialog to correct connection parameters
    """

    def __init__(self, parent=None):

        super(errorConnection, self).__init__(parent)

        self.Buser = False
        self.Bhost = False
        self.Bdb = False
        
        self.setupUi(self)
        self.setupAction()
        r = self.exec_()

    def setupAction(self):
        
        self.connect(
            self.lineEdit, QtCore.SIGNAL("textEdited(QString)"), self.user)
        self.connect(
            self.lineEdit_2, QtCore.SIGNAL("textEdited(QString)"), self.host)
        self.connect(
            self.lineEdit_3, QtCore.SIGNAL("textEdited(QString)"), self.db)
        
    def user(self):
        self.Buser = True
    def host(self):
        self.Bhost = True
    def db(self):
        self.Bdb = True
        
    def valid(self):
        if self.Buser*self.Bhost*self.Bdb == True:
            print self.Buser*self.Bhost*self.Bdb
            #Reset the connection
            self.accept()
            print self.Buser*self.Bhost*self.Bdb
            
            Global.BDname = str(self.lineEdit_3.text())
            Global.HostName = str(self.lineEdit_2.text())
            Global.userName = str(self.lineEdit.text())
  
        else:
            print self.Buser*self.Bhost*self.Bdb
            QMessageBox.about(
            self, "Renseignement Incomplet" , "Veuillez completer tous les champs")     
    
        
    
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(259, 143)
        self.pushButton = QtGui.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(10, 110, 87, 27))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.widget = QtGui.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(10, 10, 100, 91))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_2.addWidget(self.label_2)
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_2.addWidget(self.label_3)
        self.widget1 = QtGui.QWidget(Dialog)
        self.widget1.setGeometry(QtCore.QRect(120, 10, 131, 89))
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.verticalLayout = QtGui.QVBoxLayout(self.widget1)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lineEdit = QtGui.QLineEdit(self.widget1)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.verticalLayout.addWidget(self.lineEdit)
        self.lineEdit_2 = QtGui.QLineEdit(self.widget1)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.verticalLayout.addWidget(self.lineEdit_2)
        self.lineEdit_3 = QtGui.QLineEdit(self.widget1)
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.verticalLayout.addWidget(self.lineEdit_3)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.valid)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle( QtGui.QApplication.translate("Dialog", "Connection Manuelle", None))
        self.label.setText( QtGui.QApplication.translate("Dialog", "Utilisateur", None))
        self.label_2.setText( QtGui.QApplication.translate("Dialog", "Host", None))
        self.label_3.setText( QtGui.QApplication.translate("Dialog", _fromUtf8("Base de donnée"), None))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "Valider", None))
