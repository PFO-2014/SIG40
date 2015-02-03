# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_setConnectionParameter2.ui'
#
# Created: Thu Aug 21 11:40:10 2014
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(485, 318)
        self.gridLayoutWidget = QtGui.QWidget(Dialog)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 10, 461, 51))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.layoutWidget = QtGui.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(120, 120, 199, 27))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        self.editUserName = QtGui.QLineEdit(self.layoutWidget)
        self.editUserName.setText(_fromUtf8(""))
        self.editUserName.setObjectName(_fromUtf8("editUserName"))
        self.horizontalLayout_3.addWidget(self.editUserName)
        self.comboBox_listDB = QtGui.QComboBox(Dialog)
        self.comboBox_listDB.setGeometry(QtCore.QRect(230, 231, 78, 25))
        self.comboBox_listDB.setObjectName(_fromUtf8("comboBox_listDB"))
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(120, 231, 98, 27))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.layoutWidget_2 = QtGui.QWidget(Dialog)
        self.layoutWidget_2.setGeometry(QtCore.QRect(120, 90, 165, 27))
        self.layoutWidget_2.setObjectName(_fromUtf8("layoutWidget_2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_2 = QtGui.QLabel(self.layoutWidget_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.editHostName = QtGui.QLineEdit(self.layoutWidget_2)
        self.editHostName.setText(_fromUtf8(""))
        self.editHostName.setObjectName(_fromUtf8("editHostName"))
        self.horizontalLayout.addWidget(self.editHostName)
        self.layoutWidget_3 = QtGui.QWidget(Dialog)
        self.layoutWidget_3.setGeometry(QtCore.QRect(120, 170, 236, 29))
        self.layoutWidget_3.setObjectName(_fromUtf8("layoutWidget_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.layoutWidget_3)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_3 = QtGui.QLabel(self.layoutWidget_3)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_2.addWidget(self.label_3)
        self.editBDName = QtGui.QLineEdit(self.layoutWidget_3)
        self.editBDName.setText(_fromUtf8(""))
        self.editBDName.setObjectName(_fromUtf8("editBDName"))
        self.horizontalLayout_2.addWidget(self.editBDName)
        self.pushButton_Cancel = QtGui.QPushButton(Dialog)
        self.pushButton_Cancel.setEnabled(False)
        self.pushButton_Cancel.setGeometry(QtCore.QRect(270, 270, 101, 27))
        self.pushButton_Cancel.setObjectName(_fromUtf8("pushButton_Cancel"))
        self.pushButton_Valid = QtGui.QPushButton(Dialog)
        self.pushButton_Valid.setGeometry(QtCore.QRect(90, 270, 87, 27))
        self.pushButton_Valid.setObjectName(_fromUtf8("pushButton_Valid"))
        self.pushButton_Update = QtGui.QPushButton(Dialog)
        self.pushButton_Update.setEnabled(False)
        self.pushButton_Update.setGeometry(QtCore.QRect(180, 270, 87, 27))
        self.pushButton_Update.setObjectName(_fromUtf8("pushButton_Update"))
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(120, 211, 211, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.label_6 = QtGui.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(120, 150, 201, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtGui.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(120, 70, 201, 16))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName(_fromUtf8("label_7"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Paramètres de connection", None))
        self.label.setText(_translate("Dialog", "utilisateur", None))
        self.label_4.setText(_translate("Dialog", "Base de donnée", None))
        self.label_2.setText(_translate("Dialog", "hôte", None))
        self.label_3.setText(_translate("Dialog", "Base de donnée", None))
        self.pushButton_Cancel.setText(_translate("Dialog", "Annule edition", None))
        self.pushButton_Valid.setText(_translate("Dialog", "Continuer", None))
        self.pushButton_Update.setText(_translate("Dialog", "Mise à jour", None))
        self.label_5.setText(_translate("Dialog", "Bases de données disponibles:", None))
        self.label_6.setText(_translate("Dialog", "Base de donnée par défault:", None))
        self.label_7.setText(_translate("Dialog", "Identifiants de connection:", None))

