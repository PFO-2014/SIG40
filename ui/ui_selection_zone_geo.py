# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_selection_zone_geo.ui'
#
# Created: Wed Aug 27 11:40:36 2014
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
        Form.resize(792, 454)
        self.frame = QtGui.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(260, 10, 491, 431))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.gridLayoutWidget = QtGui.QWidget(self.frame)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 40, 471, 381))
        self.gridLayoutWidget.setObjectName(_fromUtf8("gridLayoutWidget"))
        self.gridLayout = QtGui.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.toolButtonDestruct = QtGui.QToolButton(self.frame)
        self.toolButtonDestruct.setGeometry(QtCore.QRect(50, 10, 26, 23))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/ourapp/destructlogo")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.toolButtonDestruct.setIcon(icon)
        self.toolButtonDestruct.setObjectName(_fromUtf8("toolButtonDestruct"))
        self.toolButtonSelect = QtGui.QToolButton(self.frame)
        self.toolButtonSelect.setGeometry(QtCore.QRect(20, 10, 26, 23))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/ourapp/rectangle_icon")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.toolButtonSelect.setIcon(icon1)
        self.toolButtonSelect.setObjectName(_fromUtf8("toolButtonSelect"))
        self.toolButtonPoly = QtGui.QToolButton(self.frame)
        self.toolButtonPoly.setEnabled(False)
        self.toolButtonPoly.setGeometry(QtCore.QRect(80, 10, 26, 23))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/ourapp/ZRlogo")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.toolButtonPoly.setIcon(icon2)
        self.toolButtonPoly.setObjectName(_fromUtf8("toolButtonPoly"))
        self.comboBox_listPGtables = QtGui.QComboBox(Form)
        self.comboBox_listPGtables.setGeometry(QtCore.QRect(20, 30, 201, 25))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(50)
        sizePolicy.setVerticalStretch(50)
        sizePolicy.setHeightForWidth(self.comboBox_listPGtables.sizePolicy().hasHeightForWidth())
        self.comboBox_listPGtables.setSizePolicy(sizePolicy)
        self.comboBox_listPGtables.setObjectName(_fromUtf8("comboBox_listPGtables"))
        self.buttonBox = QtGui.QDialogButtonBox(Form)
        self.buttonBox.setGeometry(QtCore.QRect(20, 420, 176, 27))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(20, 10, 201, 19))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.tableWidget = QtGui.QTableWidget(Form)
        self.tableWidget.setGeometry(QtCore.QRect(10, 160, 231, 211))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.label_4 = QtGui.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(40, 120, 151, 31))
        self.label_4.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_4.setAutoFillBackground(True)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName(_fromUtf8("label_4"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Outil de selection géographique", None))
        self.toolButtonDestruct.setText(_translate("Form", "...", None))
        self.toolButtonSelect.setText(_translate("Form", "...", None))
        self.toolButtonPoly.setText(_translate("Form", "...", None))
        self.label_3.setText(_translate("Form", "Couche de selection :", None))
        self.label_4.setText(_translate("Form", "Selection des Couches à exporter:", None))

import sig40.ressources.resources
