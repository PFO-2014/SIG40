# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_start_tab_menu.ui'
#
# Created: Thu Aug 28 10:27:25 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_TabWidget(object):
    def setupUi(self, TabWidget):
        TabWidget.setObjectName(_fromUtf8("TabWidget"))
        TabWidget.resize(618, 477)
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.frame = QtGui.QFrame(self.tab_2)
        self.frame.setGeometry(QtCore.QRect(20, 10, 221, 431))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.splitter = QtGui.QSplitter(self.frame)
        self.splitter.setGeometry(QtCore.QRect(10, 10, 201, 161))
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.label = QtGui.QLabel(self.splitter)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setObjectName(_fromUtf8("label"))
        self.editProjectName = QtGui.QLineEdit(self.splitter)
        self.editProjectName.setText(_fromUtf8(""))
        self.editProjectName.setObjectName(_fromUtf8("editProjectName"))
        self.label_2 = QtGui.QLabel(self.splitter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.editDirName = QtGui.QLineEdit(self.splitter)
        self.editDirName.setObjectName(_fromUtf8("editDirName"))
        self.btnSelectPath = QtGui.QPushButton(self.splitter)
        self.btnSelectPath.setObjectName(_fromUtf8("btnSelectPath"))
        self.btnProjectValidation = QtGui.QPushButton(self.frame)
        self.btnProjectValidation.setEnabled(False)
        self.btnProjectValidation.setGeometry(QtCore.QRect(60, 180, 101, 27))
        self.btnProjectValidation.setObjectName(_fromUtf8("btnProjectValidation"))
        self.btnExtraction = QtGui.QPushButton(self.frame)
        self.btnExtraction.setEnabled(False)
        self.btnExtraction.setGeometry(QtCore.QRect(10, 280, 201, 35))
        self.btnExtraction.setObjectName(_fromUtf8("btnExtraction"))
        self.btnZoneCliente = QtGui.QPushButton(self.frame)
        self.btnZoneCliente.setEnabled(False)
        self.btnZoneCliente.setGeometry(QtCore.QRect(10, 240, 201, 35))
        self.btnZoneCliente.setAutoFillBackground(False)
        self.btnZoneCliente.setCheckable(False)
        self.btnZoneCliente.setObjectName(_fromUtf8("btnZoneCliente"))
        self.ImageSig40 = QtGui.QLabel(self.frame)
        self.ImageSig40.setGeometry(QtCore.QRect(10, 320, 191, 91))
        self.ImageSig40.setText(_fromUtf8(""))
        self.ImageSig40.setTextFormat(QtCore.Qt.AutoText)
        self.ImageSig40.setPixmap(QtGui.QPixmap(_fromUtf8(":/ourapp/XLogo")))
        self.ImageSig40.setScaledContents(True)
        self.ImageSig40.setWordWrap(False)
        self.ImageSig40.setObjectName(_fromUtf8("ImageSig40"))
        self.btnProjectSuppression = QtGui.QPushButton(self.frame)
        self.btnProjectSuppression.setEnabled(False)
        self.btnProjectSuppression.setGeometry(QtCore.QRect(60, 210, 101, 27))
        self.btnProjectSuppression.setObjectName(_fromUtf8("btnProjectSuppression"))
        self.frame_3 = QtGui.QFrame(self.tab_2)
        self.frame_3.setGeometry(QtCore.QRect(240, 10, 351, 431))
        self.frame_3.setMouseTracking(False)
        self.frame_3.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_3.setObjectName(_fromUtf8("frame_3"))
        self.label_3 = QtGui.QLabel(self.frame_3)
        self.label_3.setGeometry(QtCore.QRect(10, 10, 201, 19))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.label_3.setFont(font)
        self.label_3.setTextFormat(QtCore.Qt.RichText)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.editUserName = QtGui.QLineEdit(self.frame_3)
        self.editUserName.setEnabled(False)
        self.editUserName.setGeometry(QtCore.QRect(120, 40, 201, 32))
        self.editUserName.setText(_fromUtf8(""))
        self.editUserName.setObjectName(_fromUtf8("editUserName"))
        self.editIP = QtGui.QLineEdit(self.frame_3)
        self.editIP.setEnabled(False)
        self.editIP.setGeometry(QtCore.QRect(120, 80, 201, 32))
        self.editIP.setText(_fromUtf8(""))
        self.editIP.setObjectName(_fromUtf8("editIP"))
        self.label_4 = QtGui.QLabel(self.frame_3)
        self.label_4.setGeometry(QtCore.QRect(40, 50, 71, 19))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.label_4.setFont(font)
        self.label_4.setTextFormat(QtCore.Qt.RichText)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(self.frame_3)
        self.label_5.setGeometry(QtCore.QRect(40, 90, 71, 19))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.label_5.setFont(font)
        self.label_5.setTextFormat(QtCore.Qt.RichText)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.editConnectionState = QtGui.QLineEdit(self.frame_3)
        self.editConnectionState.setEnabled(False)
        self.editConnectionState.setGeometry(QtCore.QRect(120, 120, 201, 32))
        self.editConnectionState.setText(_fromUtf8(""))
        self.editConnectionState.setObjectName(_fromUtf8("editConnectionState"))
        self.label_6 = QtGui.QLabel(self.frame_3)
        self.label_6.setGeometry(QtCore.QRect(10, 130, 101, 20))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        self.label_6.setFont(font)
        self.label_6.setTextFormat(QtCore.Qt.RichText)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.btnZR = QtGui.QPushButton(self.frame_3)
        self.btnZR.setEnabled(False)
        self.btnZR.setGeometry(QtCore.QRect(70, 170, 201, 35))
        self.btnZR.setAutoFillBackground(False)
        self.btnZR.setCheckable(False)
        self.btnZR.setObjectName(_fromUtf8("btnZR"))
        TabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        TabWidget.addTab(self.tab, _fromUtf8(""))

        self.retranslateUi(TabWidget)
        TabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(TabWidget)

    def retranslateUi(self, TabWidget):
        TabWidget.setWindowTitle(_translate("TabWidget", "TabWidget", None))
        self.label.setText(_translate("TabWidget", "1. Selectionner Nom du Projet", None))
        self.label_2.setText(_translate("TabWidget", "2. Selectionner Répertoire Projet", None))
        self.editDirName.setText(_translate("TabWidget", "/home/pierre/Bureau", None))
        self.btnSelectPath.setText(_translate("TabWidget", "Selection Répertoire Projet", None))
        self.btnProjectValidation.setText(_translate("TabWidget", "3. Valide Projet", None))
        self.btnExtraction.setText(_translate("TabWidget", "5. Extraction", None))
        self.btnZoneCliente.setText(_translate("TabWidget", "4. Dessiner Zone Cliente", None))
        self.btnProjectSuppression.setText(_translate("TabWidget", "Supprime Projet", None))
        self.label_3.setText(_translate("TabWidget", "INFORMATIONS CONNECTION", None))
        self.label_4.setText(_translate("TabWidget", "Utilisateur", None))
        self.label_5.setText(_translate("TabWidget", "Adresse IP", None))
        self.label_6.setText(_translate("TabWidget", "Etat Connection", None))
        self.btnZR.setText(_translate("TabWidget", "5. Selection Zone Reconciliation", None))
        TabWidget.setTabText(TabWidget.indexOf(self.tab_2), _translate("TabWidget", "Nouveau Projet", None))
        TabWidget.setTabText(TabWidget.indexOf(self.tab), _translate("TabWidget", "VIDE", None))

import sig40.ressources.resources
