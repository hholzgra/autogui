#!/usr/bin/env python3

"""based on the PyQt4 port of the tools/settingseditor example from Qt v4.x"""


import sys
import os
import collections

from PyQt4 import QtCore, QtGui

from pprint import pprint

from configure   import ConfigureSettings

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.settingsTree = SettingsTree()
        self.setCentralWidget(self.settingsTree)

        self.createActions()
        self.createMenus()

        self.setWindowTitle("Configure Option Editor")
        self.resize(800, 600)
        self.move(100, 100)

    def openSettings(self):
        settings = ConfigureSettings()
        self.configureFile = QtGui.QFileDialog.getOpenFileName(self, "Pick configure file", ".", "configure")
        settings.readConfigureHelp(self.configureFile)

        self.setSettingsObject(settings)
        
    def about(self):
        QtGui.QMessageBox.about(self, "About Configure Option Editor",
                "<b>Configure Option Editor</b> provides<br> a GUI interface to 'configure' scripts")

    def createActions(self):
        self.openSettingsAct = QtGui.QAction("&Get Configure Options...",
                self, shortcut="Ctrl+O", triggered=self.openSettings)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                triggered=QtGui.qApp.aboutQt)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openSettingsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.optionsMenu = self.menuBar().addMenu("&Options")

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

    def setSettingsObject(self, settings):
        self.settingsTree.setSettingsObject(settings)

        self.setWindowTitle("%s - Configure Option Editor" % settings.getName())




class SettingsTree(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        super(SettingsTree, self).__init__(parent)

        self.setItemDelegate(VariantDelegate(self))

        self.setHeaderLabels(("Option", "Value"))
        self.header().setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.header().setResizeMode(1, QtGui.QHeaderView.Stretch)

        self.settings = None

    def setSettingsObject(self, settings):
        self.settings = settings
        self.clear()

        if self.settings is not None:
            self.settings.setParent(self)
            self.refresh()

    def sizeHint(self):
        return QtCore.QSize(800, 600)

    def refresh(self):
        if self.settings is None:
            return

        # The signal might not be connected.
        try:
            self.itemChanged.disconnect(self.updateSetting)
        except:
            pass

        self.updateChildItems(None)

        self.itemChanged.connect(self.updateSetting)

    def event(self, event):
        return super(SettingsTree, self).event(event)

    def updateSetting(self, item):
        key = item.text(0)
        ancestor = item.parent()

        while ancestor:
            key = ancestor.text(0) + '/' + key
            ancestor = ancestor.parent()

        self.settings.setValue(key, item.data(1, QtCore.Qt.UserRole))

    def updateChildItems(self, parent):
        for group in self.settings.childGroups():
            child = self.createItem(group, parent)

            self.settings.beginGroup(group)
            self.updateChildItems(child)
            self.settings.endGroup()

        for key in self.settings.childKeys():
            child = self.createItem(key, parent)

            # set tooltip if a description exists
            description = self.settings.getDescription(key)
            if description is not None:
                child.setToolTip(0, description)

            value = self.settings.value(key)

            child.setText(1, value)
            child.setData(1, QtCore.Qt.UserRole, value)

    def createItem(self, text, parent):

        if parent is not None:
            item = QtGui.QTreeWidgetItem(parent)
        else:
            item = QtGui.QTreeWidgetItem(self)

        item.setText(0, text)

        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        return item







class VariantDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        super(VariantDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if index.column() == 1:
            value = index.model().data(index, QtCore.Qt.UserRole)
            if value is None:
                myOption = QtGui.QStyleOptionViewItem(option)
                myOption.state &= ~QtGui.QStyle.State_Enabled
                super(VariantDelegate, self).paint(painter, myOption, index)
                return

        super(VariantDelegate, self).paint(painter, option, index)

    def createEditor(self, parent, option, index):
        if index.column() != 1:
            return None

        originalValue = index.model().data(index, QtCore.Qt.UserRole)
        if originalValue is None:
            return None

        lineEdit = QtGui.QLineEdit(parent)
        lineEdit.setFrame(False)

        return lineEdit

    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.UserRole)
        if editor is not None:
            editor.setText(value)

    def setModelData(self, editor, model, index):
        if not editor.isModified():
            return

        text = editor.text()

        model.setData(index, text, QtCore.Qt.DisplayRole)
        model.setData(index, text, QtCore.Qt.UserRole)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

