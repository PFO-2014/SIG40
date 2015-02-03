# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_selection_zone_reconciliation.ui'
#
# Created: Thu Aug 21 12:23:30 2014
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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(228, 311)
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 60, 201, 19))
        self.label.setObjectName(_fromUtf8("label"))
        self.rechercheParNom = QtGui.QLineEdit(Form)
        self.rechercheParNom.setEnabled(True)
        self.rechercheParNom.setGeometry(QtCore.QRect(20, 80, 201, 32))
        self.rechercheParNom.setText(_fromUtf8(""))
        self.rechercheParNom.setObjectName(_fromUtf8("rechercheParNom"))
        self.comboBox_listPGtables = QtGui.QComboBox(Form)
        self.comboBox_listPGtables.setGeometry(QtCore.QRect(20, 30, 201, 25))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(50)
        sizePolicy.setHeightForWidth(self.comboBox_listPGtables.sizePolicy().hasHeightForWidth())
        self.comboBox_listPGtables.setSizePolicy(sizePolicy)
        self.comboBox_listPGtables.setObjectName(_fromUtf8("comboBox_listPGtables"))
        self.buttonBox = QtGui.QDialogButtonBox(Form)
        self.buttonBox.setGeometry(QtCore.QRect(20, 240, 176, 27))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(20, 10, 201, 19))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.toolButtonPoly = QtGui.QToolButton(Form)
        self.toolButtonPoly.setGeometry(QtCore.QRect(60, 130, 101, 91))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/ourapp/ZRlogo")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.toolButtonPoly.setIcon(icon)
        self.toolButtonPoly.setIconSize(QtCore.QSize(64, 64))
        self.toolButtonPoly.setObjectName(_fromUtf8("toolButtonPoly"))
        self.pushButton_new = QtGui.QPushButton(Form)
        self.pushButton_new.setEnabled(False)
        self.pushButton_new.setGeometry(QtCore.QRect(60, 270, 87, 27))
        self.pushButton_new.setObjectName(_fromUtf8("pushButton_new"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Outil de selection géographique", None))
        self.label.setText(_translate("Form", "Commentaires Additionnels:", None))
        self.label_3.setText(_translate("Form", "Motifs Prédéfinis:", None))
        self.toolButtonPoly.setText(_translate("Form", "...", None))
        self.pushButton_new.setText(_translate("Form", "Nouvelle ZR", None))

import sig40.ressources.resources
