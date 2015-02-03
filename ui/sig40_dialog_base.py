# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sig40_dialog_base.ui'
#
# Created: Mon Jul 28 14:28:40 2014
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

class Ui_sig40DialogBase(object):
    def setupUi(self, sig40DialogBase):
        sig40DialogBase.setObjectName(_fromUtf8("sig40DialogBase"))
        sig40DialogBase.resize(400, 300)
        self.button_box = QtGui.QDialogButtonBox(sig40DialogBase)
        self.button_box.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))

        self.retranslateUi(sig40DialogBase)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), sig40DialogBase.accept)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), sig40DialogBase.reject)
        QtCore.QMetaObject.connectSlotsByName(sig40DialogBase)

    def retranslateUi(self, sig40DialogBase):
        sig40DialogBase.setWindowTitle(_translate("sig40DialogBase", "sig40", None))

