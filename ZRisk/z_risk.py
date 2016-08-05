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
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant, QObject
from PyQt4.QtGui import QAction, QApplication, QIcon, QDialogButtonBox, QDialog, QMessageBox, QPushButton
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from z_risk_dialog import ZRiskDialog
import os.path
from qgis.core import *
from qgis.core import QgsMapLayerRegistry
from qgis.gui import QgsFieldProxyModel, QgsMapLayerProxyModel
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

        #Definisanje signala i slotova:

        #Detektovanje da li su lejeri u ulaznim poljima promenjeni
        QObject.connect(self.dlg.mMapLayerComboBoxHazard, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.layerChanged)
        QObject.connect(self.dlg.mMapLayerComboBoxPovredljivost, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.layerChanged)
        QObject.connect(self.dlg.mMapLayerComboBoxZgrade, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.layerChanged)
        
        #Detektovanje promena u ulalaznim poljima:
        QObject.connect(self.dlg.mFieldComboBoxHPGA, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        QObject.connect(self.dlg.mFieldComboBoxZPGA, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        QObject.connect(self.dlg.mFieldComboBoxOstecenje, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        QObject.connect(self.dlg.mFieldComboBoxLJudi, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        QObject.connect(self.dlg.mFieldComboBoxStanari, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        QObject.connect(self.dlg.mFieldComboBoxKljudi, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        QObject.connect(self.dlg.mFieldComboBoxKpovred, QtCore.SIGNAL("fieldChanged(const QString &)"), self.fieldChanged)
        
        #Glavni signal i dugme OK
        QObject.connect(self.dlg.pushButtonOK, QtCore.SIGNAL('clicked()'), self.sracunaj)
        #Dugme Odustani
        QObject.connect(self.dlg.pushButtonOdustani, QtCore.SIGNAL('clicked()'), self.close)
        #Detektovanje promene da li se raspolaze PGA podacima
        QObject.connect(self.dlg.radioButton, QtCore.SIGNAL('clicked()'), self.kliknuto)



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


    #Metod za slotove sa lejerima
    #Dogodila se promena   
    def layerChanged(self):

        #Postavi trenutne lejere
        self.hazard=self.dlg.mMapLayerComboBoxHazard.currentLayer() 
        self.povredljivost=self.dlg.mMapLayerComboBoxPovredljivost.currentLayer() 
        self.zgrade=self.dlg.mMapLayerComboBoxZgrade.currentLayer() 

        #Izbrisi vrednosti iz trenutnih polja za atribute
        self.dlg.mFieldComboBoxHPGA.clear()
        self.dlg.mFieldComboBoxZPGA.clear()
        self.dlg.mFieldComboBoxOstecenje.clear()
        self.dlg.mFieldComboBoxLJudi.clear()
        self.dlg.mFieldComboBoxStanari.clear()
        self.dlg.mFieldComboBoxKljudi.clear()
        self.dlg.mFieldComboBoxKpovred.clear()

        #Upisi atribute novih lejera
        self.dlg.mFieldComboBoxHPGA.setLayer(self.hazard) 
        self.dlg.mFieldComboBoxZPGA.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxOstecenje.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxLJudi.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxStanari.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxKljudi.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxKpovred.setLayer(self.zgrade)


    # Metod za slotove sa poljima
    # Dogodila se promena
    def fieldChanged(self):
        # Postavi trenutna vrednosti za ulazna polja
        
        self.hPGA=self.dlg.mFieldComboBoxHPGA.currentField()            #atribut PGA u hazardima
        self.zPGA=self.dlg.mFieldComboBoxZPGA.currentField()            #atribut PGA u zgradama        
        self.ostecenje=self.dlg.mFieldComboBoxOstecenje.currentField()  #atribut Ostecenje u zgradama
        self.ljudi=self.dlg.mFieldComboBoxLJudi.currentField()          #atribut Ljudi u zgradama
        self.stanari=self.dlg.mFieldComboBoxStanari.currentField()      #atribut br.stanara u zgradama
        self.kljudi=self.dlg.mFieldComboBoxKljudi.currentField()        #atribut kriva povredlj. za ljude
        self.kpovred=self.dlg.mFieldComboBoxKpovred.currentField()      #atribut kriva povredlj. za zgrade



    def sracunaj(self):
        ##--Povredljivost u dic--#
        self.dicPovredljivost={}
        for field in self.povredljivost.pendingFields(): #Izlistava zaglavlja (a1,p1,h1...)
            vrednosti=[]
        
            for featureP in self.povredljivost.getFeatures(): #Prolazi kroz redove [a1, p1...hn]
        
                vrednost=float(featureP.attribute(field.name())) #Dodaje u listu vrednosti
                vrednosti+=[vrednost] #Na kraju ciklusa ovo je su svre vrednosti jedne kolone

            
            self.dicPovredljivost[field.name()]=vrednosti # Kljuc je naziv zaglavlja, vrednost kolona
        #QgsMessageLog.logMessage(str(self.dicPovredljivost))


        ##--Prepisivanje vrednosti PGA iz lejera Hazard u lejer zgrade

        if self.st==False: #Indikator o aktivnosti radioButton-a #False je ukoliko nije cekirano
                            # Ako je cekirano, ovaj blok se preskace
            self.zgrade.startEditing() # Postavljamo lejer zgrade da bude aktivan za upis
            for feature in self.zgrade.getFeatures():
                for feat in self.hazard.getFeatures():
                    # Proverava da li se zgrada cela ili delom nalazi u hazardu
                    if feature.geometry().within(feat.geometry()) or feature.geometry().overlaps(feat.geometry()) :
                        feature[self.zPGA]=feat[self.hPGA]
                        self.zgrade.updateFeature(feature) #Upisivanje vrednosti pga u zgrade.PGA
                        #QgsMessageLog.logMessage(str(feature[self.zPGA]))  
            self.zgrade.commitChanges() #Cuvanje promena u lejeru zgrade
            #QgsMessageLog.logMessage('Vrednost PGA')
        

        ##--Pronalazenje PGA za krivu povredljivosti ljdui i krivu ostecenja--##

        #progress bar inicijalizacija
        count = int(self.zgrade.featureCount())
        i=0 #progress bar brojac


        self.zgrade.startEditing() #Lejer zgrade je aktivan za upis
        # Za svaki red:
        for feature in self.zgrade.getFeatures():

            brojStanara=feature.attribute(self.stanari) #  br.stanara
            keyP=feature.attribute(self.kpovred)        #  naziv krive pov. za zgrade P ('p1'...'pn')
            keyH=feature.attribute(self.kljudi)         #  indeks krive pov. za ljude H ('h1'...'an')
            #progress bar
            self.pb(i,count)
            i=i+1
            #################
            keyAp='a'+keyP[-1] # vraca string naziva odgovarajuce vrednosti krive A('a1', 'a2', 'an')
            keyAh='a'+keyH[-1] # vraca string naziva odgovarajuce vrednosti krive A('a1', 'a2', 'an')

            pga=float(feature.attribute(self.zPGA)) #float vrednost pga iz lejera zgrade
            #QgsMessageLog.logMessage(str(pga))


            krivaP=self.dicPovredljivost[keyP] #Vrednost krive p za datu zgradu
            krivaH=self.dicPovredljivost[keyH] #Vrednost krive h za datu zgradu

            krivaAp=self.dicPovredljivost[keyAp] #Kriva povredljivosti A za krivu P
            krivaAh=self.dicPovredljivost[keyAh] #Kriva povredljivosti A za krivu H


            #Inicijalizacija polja za susedne indekse iz krive A za krivu H
            minIndex1h=NULL
            minIndex2h=NULL
        
            #Inicijalizacija polja za susedne indekse iz krive A za krivu P
            minIndex1p=NULL
            minIndex2p=NULL

            # proverava da li se pga vrednost nalazi u tablicnim vrednostima krive Ah

            if pga in krivaAh:
                #ukoliko se nalazi
                indexH=krivaAh.index(pga)
                valueH=krivaH[indexH]
                valueAh=krivaAh[indexH]
                feature[self.ljudi] = valueH*brojStanara #tablicnu vrednost pomnozenu brojem stanra
                self.zgrade.updateFeature(feature)#upisuje u polje za gubitak ljudi 
                
            else:
                #ukoliko se ne nalazi

                #odredjuje indeks najblize tablicne vrednosti iz Ah
                minIndex1h=min(range(len(krivaAh)), key=lambda i: abs(krivaAh[i]-pga))
                if pga>krivaAh[minIndex1h]: #ukoliko je pga veca od najblize tablicne
                    minIndex2h=minIndex1h+1 #pronalazi sledeci veci tablicni indeks
                else:
                    # Ukoliko je manja, menja indeksima mesta
                    minIndex2h=minIndex1h  
                    minIndex1h=minIndex2h-1 

                ##--Interpolacija##
        
                #princip slicnosti u pravouglom trouglu 
                #odsecak hx nalazi se na stranici h
                #odsecak ax nalazi se na stranici a
                #iz slicnosti sledi
                #a:ax=h:hx
                #hx=ax*h/a
                #ljud=valueH1+px
        
                valueA2h=krivaAh[minIndex2h]
                valueA1h=krivaAh[minIndex1h]
                valueH2=krivaH[minIndex2h]
                valueH1=krivaH[minIndex1h]
                a=valueA2h-valueA1h
                h=valueH2-valueH1
                ax=pga-valueA1h
                hx=ax*h/a
                ljud=valueH1+hx #interpolovana vrednost krive povredljivosti za ljude
    
                feature[self.ljudi] = ljud*brojStanara #interpolovanu vrednost mnozi brojem stanara
                self.zgrade.updateFeature(feature) # izvrsava upisivanje u lejer

            # proverava da li se pga vrednost nalazi u tablicnim vrednostima krive Ap
            if pga in krivaAp:
                #ukoliko se nalazi
                indexP=krivaAp.index(pga)
                valueP=krivaP[indexP]
                valueA=krivaAp[indexP]
        
                #zapis u polje
                feature[self.ostecenje] = valueP*100 #tablicnu vrednost pretvara u procente
                #feature[self.ostecenje] = 111
                self.zgrade.updateFeature(feature) # izvrsava upisivanje u lejer
            else:
                #ukoliko se ne nalazi
                #odredjuje indeks najblize tablicne vrednosti iz Ap
                minIndex1p=min(range(len(krivaAp)), key=lambda i: abs(krivaAp[i]-pga))
                
                #ako je vrednost pga veca od tablicne
                if pga>krivaAp[minIndex1p]: 
                    minIndex2p=minIndex1p+1 #pronalazi sledeci veci tablicni indeks
                else:
                    minIndex2p=minIndex1p   #menja indeksima mesta
                    minIndex1p=minIndex2p-1
        
                ##--Interpolacija##
                #princip slicnosti u pravouglom trouglu 
                #odsecak px nalazi se na stranici p
                #odsecak ax nalazi se na stranici a
                #iz slicnosti sledi
                # a:ax=p:px
                # px=ax*p/a
                #ost=valueP1+px
                
                valueA2p=krivaAp[minIndex2p]
                valueA1p=krivaAp[minIndex1p]
                valueP2=krivaP[minIndex2p]
                valueP1=krivaP[minIndex1p]
                
                a=valueA2p-valueA1p
                p=valueP2-valueP1
                ax=pga-valueA1p
                px=ax*p/a
                ost=valueP1+px #interpolovana vrednost krive povredljivosti za zgrade
                
                #zapis u polje
                feature[self.ostecenje] = ost*100 #interpolovanu vrednost pretvara u procente
                #feature[self.ostecenje] = 999
                self.zgrade.updateFeature(feature) #izvrsava upisivanje u lejer  
        
                
        #Cuvanje upisanih vrednosti       
        self.zgrade.commitChanges()
        #Zatvaranje dijaloga
        self.close()
        #Dijalog obavestenje da su vrednosti ostecenja zgrada i gubitka ljudi uspesno sracunati
        QMessageBox.information( self.iface.mainWindow(),"Info", 
                                "Vrednosti ostecenja i gubitka ljudi uspesno su sracunate.")
          
    #Metod za zatvaranje dijaloga plugina     
    def close(self):
        self.dlg.close() 

    #definisanje progress bara
    def pb(self,i,count):
        progress=self.dlg.progressBar
        progress.setMaximum(100)
        percent = (i/float(count)) * 100
        progress.setValue(percent)  

    # Slot funkcija za registrovanje promene nad radioButton-om
    def kliknuto(self):
        self.st=self.dlg.radioButton.isChecked()
        #QgsMessageLog.logMessage(str(self.st))                     
        
    def run(self):
        #QgsMessageLog.logMessage('pokrenuo sam se')
        """Run method that performs all the real work"""
        
        #Setovanje filtera za lejere:
        self.dlg.mMapLayerComboBoxHazard.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.dlg.mMapLayerComboBoxPovredljivost.setFilters(QgsMapLayerProxyModel.NoGeometry)
        self.dlg.mMapLayerComboBoxZgrade.setFilters(QgsMapLayerProxyModel.PolygonLayer)

        #Setovanje filtera za atribute lejera:
        self.dlg.mFieldComboBoxHPGA.setFilters(QgsFieldProxyModel.Numeric)
        self.dlg.mFieldComboBoxZPGA.setFilters(QgsFieldProxyModel.Numeric)
        self.dlg.mFieldComboBoxOstecenje.setFilters(QgsFieldProxyModel.Numeric)
        self.dlg.mFieldComboBoxLJudi.setFilters(QgsFieldProxyModel.Numeric)
        self.dlg.mFieldComboBoxStanari.setFilters(QgsFieldProxyModel.Numeric)
        self.dlg.mFieldComboBoxKljudi.setFilters(QgsFieldProxyModel.String)
        self.dlg.mFieldComboBoxKpovred.setFilters(QgsFieldProxyModel.String)
        #Inicijalno popunjavanje lejera
        self.hazard=self.dlg.mMapLayerComboBoxHazard.currentLayer()
        self.povredljivost=self.dlg.mMapLayerComboBoxPovredljivost.currentLayer()  
        self.zgrade=self.dlg.mMapLayerComboBoxZgrade.currentLayer() 
        
        #Prikazivanje atributa inicijalnih lejera
        self.dlg.mFieldComboBoxHPGA.setLayer(self.hazard) 
        self.dlg.mFieldComboBoxZPGA.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxOstecenje.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxLJudi.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxStanari.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxKljudi.setLayer(self.zgrade)
        self.dlg.mFieldComboBoxKpovred.setLayer(self.zgrade)

        #inicijalne lejeri smesteni u promenljive
        self.hPGA=self.dlg.mFieldComboBoxHPGA.currentField()
        self.zPGA=self.dlg.mFieldComboBoxZPGA.currentField()
        self.ostecenje=self.dlg.mFieldComboBoxOstecenje.currentField()
        self.ljudi=self.dlg.mFieldComboBoxLJudi.currentField()
        self.stanari=self.dlg.mFieldComboBoxStanari.currentField()
        self.kljudi=self.dlg.mFieldComboBoxKljudi.currentField()
        self.kpovred=self.dlg.mFieldComboBoxKpovred.currentField()
        self.st=self.dlg.radioButton.isChecked() #inicijalni status (False)
        #QgsMessageLog.logMessage('status je:')
        #QgsMessageLog.logMessage(str(self.st))
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
