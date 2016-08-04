# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ZRisk
                                 A QGIS plugin
 ZRisk plugin za procenu zemljotresnog rizika zgrada
                              -------------------
        begin                : 2016-08-02
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Dejan Dragojević, Nemanja Paunić 
        email                : paunicnemanja@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication

from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from z_risk_dialog import ZRiskDialog
import os.path

from qgis.core import *
from qgis.core import QgsMapLayerRegistry
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QVariant
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QObject
from PyQt4.QtGui import QDialogButtonBox, QDialog, QMessageBox, QPushButton
import time


class ZRisk:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ZRisk_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ZRiskDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&ZRisk')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ZRisk')
        self.toolbar.setObjectName(u'ZRisk')


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ZRisk', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ZRisk/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'ZRisk'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&ZRisk'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # return QgsLayer by it's name

    '''def getLayerByName(vectorLayerName):
        layer = None
        for lyr in self.iface.legendInterface().layers():
            if lyr.name() == vectorLayerName:
                layer = lyr
                break
        return layer'''
    
    # return list of names of layer's fields. Second parameter can contain types of needed fields
    # e.g. ['Integer','Real']
    '''def getAttributesListOfVectorLayer(layer, types=None):
        names = []

        for field in layer.pendingFields():
            if not types:
                names.append(field.name())
            else:
                if str(field.typeName()) in types:
                    names.append(field.name())
            return names'''



    def layerChanged(self):

        self.hazard=self.dlg.mMapLayerComboBoxHazard.currentLayer() 
        self.povredljivost=self.dlg.mMapLayerComboBoxPovredljivost.currentLayer() 
        self.zgrade=self.dlg.mMapLayerComboBoxZgrade.currentLayer() 

        self.dlg.mFieldComboBoxHPGA.clear()
        self.dlg.mFieldComboBoxZPGA.clear()
        self.dlg.mFieldComboBoxOstecenje.clear()
        self.dlg.mFieldComboBoxLJudi.clear()
        self.dlg.mFieldComboBoxStanari.clear()
        self.dlg.mFieldComboBoxKljudi.clear()
        self.dlg.mFieldComboBoxKpovred.clear()

        self.hPGA=self.dlg.mFieldComboBoxHPGA.setLayer(self.hazard) 
        self.zPGA=self.dlg.mFieldComboBoxZPGA.setLayer(self.zgrade)
        self.ostecenje=self.dlg.mFieldComboBoxOstecenje.setLayer(self.zgrade)
        self.ljudi=self.dlg.mFieldComboBoxLJudi.setLayer(self.zgrade)
        self.stanari=self.dlg.mFieldComboBoxStanari.setLayer(self.zgrade)
        self.kljudi=self.dlg.mFieldComboBoxKljudi.setLayer(self.zgrade)
        self.kpovred=self.dlg.mFieldComboBoxKpovred.setLayer(self.zgrade)
    def fieldChanged(self):

        self.hPGA=self.dlg.mFieldComboBoxHPGA.currentField()
        self.zPGA=self.dlg.mFieldComboBoxZPGA.currentField()
        self.ostecenje=self.dlg.mFieldComboBoxOstecenje.currentField()
        self.ljudi=self.dlg.mFieldComboBoxLJudi.currentField()
        self.stanari=self.dlg.mFieldComboBoxStanari.currentField()
        self.kljudi=self.dlg.mFieldComboBoxKljudi.currentField()
        self.kpovred=self.dlg.mFieldComboBoxKpovred.currentField()

    def sracunaj(self):

        if not len(QgsMapLayerRegistry.instance().mapLayers())==0:


            ##--Povredljivost u dic--#

            self.dicPovredljivost={}
            for field in self.povredljivost.pendingFields():
                vrednosti=[]
        
                for featureP in self.povredljivost.getFeatures():
            
                    vrednost=float(featureP.attribute(field.name()))
                    vrednosti+=[vrednost]
                #print vrednosti
                self.dicPovredljivost[field.name()]=vrednosti

            ##--Zaobilazenje Unije

            self.zgrade.startEditing()
            for feature in self.zgrade.getFeatures():
     
                for feat in self.hazard.getFeatures():
                    if type(feature[self.zPGA]) is type(NULL):
                        if feature.geometry().within(feat.geometry()) or feature.geometry().overlaps(feat.geometry()) :
                            feature[self.zPGA]=float(feat[self.hPGA])
                            self.zgrade.updateFeature(feature)
                    else:
                        break
            self.zgrade.commitChanges()
        
            ##--Pronalazenje PGA za krivu povredljivosti i krivu ostecenja--##

            count = int(self.zgrade.featureCount()) #progress bar inicijalizacija
            i=0 #progress bar brojac
            self.zgrade.startEditing()

            for feature in self.zgrade.getFeatures():
                brojStanara=feature.attribute(self.stanari)
                keyP=feature.attribute(self.kpovred) #test1
                keyH=feature.attribute(self.kljudi)
                #progress bar
                self.pb(i,count)
                i=i+1
                #
                keyAp='a'+keyP[-1] #t1
                keyAh='a'+keyH[-1]

                #print keyH
                #print 'a'+keyH[-1]
                pga=float(feature.attribute(self.zPGA))
                #QtGui.QMessageBox.critical(None, "Error", str(type(pga)))

                krivaP=self.dicPovredljivost[keyP] #t1
                krivaH=self.dicPovredljivost[keyH]

                krivaAp=self.dicPovredljivost[keyAp] #t1
                krivaAh=self.dicPovredljivost[keyAh]

                minIndex1h=NULL
                minIndex2h=NULL
    
                minIndex1p=NULL
                minIndex2p=NULL

                if pga in krivaAh:
                    indexH=krivaAh.index(pga)
                    valueH=krivaH[indexH]
                    valueAh=krivaAh[indexH]

                    feature[self.ljudi] = valueH*brojStanara
                    self.zgrade.updateFeature(feature)
        
                else:
                    #print 'nema'
                    minIndex1h=min(range(len(krivaAh)), key=lambda i: abs(krivaAh[i]-pga))
                    if pga>krivaAh[minIndex1h]:
                        minIndex2h=minIndex1h+1
            
            
                    else:
                        minIndex2h=minIndex1h
                        minIndex1h=minIndex2h-1 
                    ##--Interpolacija##
        
                    #princip slicnosti u pravouglom trouglu 
                    #odsecak hx nalazi se na stranici h
                    #odsecak ax nalazi se na stranici a
                    #iz slicnosti sledi
                    # a:ax=h:hx
                    # hx=ax*h/a
                    #ljudi=valueH1+px
    
                    valueA2h=krivaAh[minIndex2h]
                    valueA1h=krivaAh[minIndex1h]
                    valueH2=krivaH[minIndex2h]
                    valueH1=krivaH[minIndex1h]
                    a=valueA2h-valueA1h
                    h=valueH2-valueH1
                    ax=pga-valueA1h
                    hx=ax*h/a
                    ljud=valueH1+hx
    
                    #print ljudi
                    feature[self.ljudi] = ljud*brojStanara
                    self.zgrade.updateFeature(feature)

                if pga in krivaAp:
                    indexP=krivaAp.index(pga)
                    valueP=krivaP[indexP]
                    valueA=krivaAp[indexP]
        
                    #zapis u polje
                    feature[self.ostecenje] = valueP*100
                    self.zgrade.updateFeature(feature)
                else:
                    minIndex1p=min(range(len(krivaAp)), key=lambda i: abs(krivaAp[i]-pga))
        
                    if pga>krivaAp[minIndex1p]:
                        minIndex2p=minIndex1p+1
                    else:
                        minIndex2p=minIndex1p
                        minIndex1p=minIndex2p-1
            

        
                        ##--Interpolacija##
                        
                        #princip slicnosti u pravouglom trouglu 
                        #odsecak px nalazi se na stranici p
                        #odsecak ax nalazi se na stranici a
                        #iz slicnosti sledi
                        # a:ax=p:px
                        # px=ax*p/a
                        #ostecenje=valueP1+px
                        
                        valueA2p=krivaAp[minIndex2p]
                        valueA1p=krivaAp[minIndex1p]
                        valueP2=krivaP[minIndex2p]
                        valueP1=krivaP[minIndex1p]
            
                        a=valueA2p-valueA1p
                        p=valueP2-valueP1
                        ax=pga-valueA1p
                        px=ax*p/a
                        ost=valueP1+px
            
                        #zapis u polje
                        feature[self.ostecenje] = ost*100
                        #feature['ostecenje'] = 1.1111111
                        self.zgrade.updateFeature(feature)
                    pass
            self.zgrade.commitChanges()
                    
            
            QMessageBox.information( self.iface.mainWindow(),"Info", "Procena zemljotresnog rizika uspesno je sracunata.")
            self.pb(0,count)
            self.close()
        else:
            QtGui.QMessageBox.critical(None, "Error", 'Trenutno ne postoji ni jedan ucitan lejer!')
            return

    def close(self):
        self.dlg.close() 

    #definisanje progress bara
    def pb(self,i,count):
        progress=self.dlg.progressBar
        progress.setMaximum(100)
        percent = (i/float(count)) * 100
        progress.setValue(percent)                         
        
    def run(self):
        """Run method that performs all the real work"""


        self.hazard=self.dlg.mMapLayerComboBoxHazard.currentLayer() 
        self.povredljivost=self.dlg.mMapLayerComboBoxPovredljivost.currentLayer() 
        self.zgrade=self.dlg.mMapLayerComboBoxZgrade.currentLayer() 
        
        self.dlg.mFieldComboBoxHPGA.setLayer(self.hazard) 
        self.dlg.mFieldComboBoxZPGA.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxOstecenje.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxLJudi.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxStanari.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxKljudi.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxKpovred.setLayer(self.zgrade)

        self.hPGA=self.dlg.mFieldComboBoxHPGA.currentField()
        self.zPGA=self.dlg.mFieldComboBoxZPGA.currentField()
        self.ostecenje=self.dlg.mFieldComboBoxOstecenje.currentField()
        self.ljudi=self.dlg.mFieldComboBoxLJudi.currentField()
        self.stanari=self.dlg.mFieldComboBoxStanari.currentField()
        self.kljudi=self.dlg.mFieldComboBoxKljudi.currentField()
        self.kpovred=self.dlg.mFieldComboBoxKpovred.currentField()        

        QObject.connect(self.dlg.mMapLayerComboBoxHazard, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.layerChanged)
        QObject.connect(self.dlg.mMapLayerComboBoxPovredljivost, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.layerChanged)
        QObject.connect(self.dlg.mMapLayerComboBoxZgrade, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.layerChanged)
        QObject.connect(self.dlg.mMapLayerComboBoxZgrade, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.layerChanged)
        QObject.connect(self.dlg.mFieldComboBoxHPGA, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        QObject.connect(self.dlg.mFieldComboBoxZPGA, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        QObject.connect(self.dlg.mFieldComboBoxOstecenje, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        QObject.connect(self.dlg.mFieldComboBoxLJudi, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        QObject.connect(self.dlg.mFieldComboBoxStanari, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        QObject.connect(self.dlg.mFieldComboBoxKljudi, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        QObject.connect(self.dlg.mFieldComboBoxKpovred, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        #QObject.connect(self.dlg.button_box.button(QDialogButtonBox.Ok), QtCore.SIGNAL('clicked()'), self.sracunaj)
        QObject.connect(self.dlg.pushButtonOK, QtCore.SIGNAL('clicked()'), self.sracunaj)
        QObject.connect(self.dlg.pushButtonOdustani, QtCore.SIGNAL('clicked()'), self.close)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
