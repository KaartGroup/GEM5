
import os
import sys
from os import chdir
from os.path import join
import argparse
import json
import tempCSS
import subprocess
import logging
import re
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import *
from settings import *
from import_functions import *
from unuploaded_functions import *
from shape_select_widget import *
from list_functions import *
#----------------------MAIN WINDOW CLASS----------------------------

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("GEM - GUI Editor for Mapcss")
        ##----------------MAIN WINDOW VARIABLES---------------------
        self.importOldStyle=False
        self.output_file_dir = os.path.expanduser("~/Documents")
        self.filters = ""
        self.select_filters = "MAPCSS (*.mapcss)"
        self.currentEditors={}
        self.currentEditorsOrdered=[]
        self.selectedEditors=[]
        self.unup_node_size=0
        self.unup_line_width=0
        self.unup_line_color_text=''
        self.unup_line_color_ui=QColor(BLACK)
        self.unup_node_color_text=''
        self.unup_node_color_ui=QColor(BLACK)
 
        ##-----------------QICONS & QPIXMAPS--------------------------
        # self.kaartLogo='static/icons/kaart.png'
        # self.gemLogo='static/icons/GEM.png'
        # self.gemIcon  = QtGui.QIcon(self.gemLogo)    
        # self.kaartIcon  = QtGui.QIcon(self.kaartLogo)
        self.unup_shape=QPixmap(15,15)
        ##----------------GUI SETUP---------------------------------

        self.mainWidget=QWidget()
        self.mainWidgetLayout=QGridLayout()
        self.mainWidget.setLayout(self.mainWidgetLayout)
        self.setCentralWidget(self.mainWidget)


        ##----------------------CONTROLS WIDGET---------------------

        ##----------------------TEAM / FILE NAME BOX----------------

        self.controlsWidget=QGroupBox()

        self.controlsWidget.setTitle("Controls")
        self.controlsWidgetLayout=QGridLayout()
        self.controlsWidgetLayout.setSpacing(0)
        self.controlsWidget.setLayout(self.controlsWidgetLayout)
        self.mainWidgetLayout.addWidget(self.controlsWidget,0,0)

        self.teamNameBox = QGroupBox()

        self.teamNameBox.setTitle('Team Name')
        self.teamNameBoxLayout=QGridLayout()
        self.teamNameBoxLayout.setSpacing(0)
        self.teamNameBox.setLayout(self.teamNameBoxLayout)
        self.controlsWidgetLayout.addWidget(self.teamNameBox)

        self.teamNameField=QLineEdit()
        self.teamNameBoxLayout.addWidget(self.teamNameField,0,0)

        ##--------------------NON UPLOADED HIGHLIGHTS---------------

        self.notUploadedBox=QGroupBox()
        self.notUploadedBox.setTitle("Highlights for non-uploaded changes")
        self.notUploadedBoxLayout=QGridLayout()
        # self.notUploadedBoxLayout.addStretch(1)
        self.notUploadedBoxLayout.setSpacing(0)
        self.notUploadedBox.setLayout(self.notUploadedBoxLayout)
        self.controlsWidgetLayout.addWidget(self.notUploadedBox)

        self.unupLineColorButton=QPushButton()
        self.unupLineColorButton.setText('LINE COLOR')
        self.unupLineColorButton.clicked.connect(lambda:unup_linecolor_changed(self))
        self.notUploadedBoxLayout.addWidget(self.unupLineColorButton,0,0)

        self.unupLineColorPreview=QLabel()
        self.unupLineColorpix = QPixmap(15, 15)
        self.unupLineColorpix.fill(QColor(WHITE))
        self.unupLineColorPreview.setPixmap(self.unupLineColorpix)
        self.notUploadedBoxLayout.addWidget(self.unupLineColorPreview,0,1,Qt.AlignmentFlag.AlignCenter)

        self.unupLineWidthLabel=QLabel()
        self.unupLineWidthLabel.setText("Line Width")
        self.notUploadedBoxLayout.addWidget(self.unupLineWidthLabel,0,2)

        self.unupLineWidthSpinner=QSpinBox()
        self.unupLineWidthSpinner.setRange(1, 20)
        self.unupLineWidthSpinner.setValue(0)
        self.unupLineWidthSpinner.valueChanged.connect(lambda:unup_linewidth_changed(self,self.unupLineWidthSpinner.value()))
        self.notUploadedBoxLayout.addWidget(self.unupLineWidthSpinner,0,3)
        #---NODE SIZE)

        self.unupNodeColorButton=QPushButton()
        self.unupNodeColorButton.setText('NODE COLOR')
        self.unupNodeColorButton.clicked.connect(lambda:unup_nodecolor_changed(self))
        self.notUploadedBoxLayout.addWidget(self.unupNodeColorButton,1,0)

        self.unupNodeColorPreview=QLabel()
        self.unupNodeColorpix = QPixmap(15, 15)
        self.unupNodeColorpix.fill(QColor(WHITE))
        self.unupNodeColorPreview.setPixmap(self.unupNodeColorpix)
        self.notUploadedBoxLayout.addWidget(self.unupNodeColorPreview,1,1,Qt.AlignmentFlag.AlignCenter)

        self.unupNodeWidthLabel=QLabel()
        self.unupNodeWidthLabel.setText("Node Size")
        self.notUploadedBoxLayout.addWidget(self.unupNodeWidthLabel,1,2)

        self.unupNodeWidthSpinner=QSpinBox()
        self.unupNodeWidthSpinner.setRange(1, 20)
        self.unupNodeWidthSpinner.setValue(0)
        self.unupNodeWidthSpinner.valueChanged.connect(lambda:unup_nodesize_changed(self,self.unupNodeWidthSpinner.value()))
        self.notUploadedBoxLayout.addWidget(self.unupNodeWidthSpinner,1,3)
       
        # #---NODE SHAPE

        self.unupNodeShapeButton=QPushButton()
        self.unupNodeShapeButton.setText('NODE SHAPE')
        self.unupNodeShapeButton.clicked.connect(lambda:shapeSelectWidget(self,'unup'))
        self.notUploadedBoxLayout.addWidget(self.unupNodeShapeButton,2,0)

        self.unupNodeShapePreview=QLabel()
        self.unupNodeShapePix=QPixmap(15,15)
        self.unupNodeShapePreview.setPixmap(self.unupNodeShapePix)
        self.notUploadedBoxLayout.addWidget(self.unupNodeShapePreview,2,1,Qt.AlignmentFlag.AlignCenter)

        ##--------------------EDITOR HIGHLIGHT SETTINGS---------------

        self.editorSettingsBox=QGroupBox()
        self.editorSettingsBox.setTitle("Editor Highlights")
        self.editorSettingsBoxLayout=QGridLayout()

        self.editorSettingsBox.setLayout(self.editorSettingsBoxLayout)
        self.controlsWidgetLayout.addWidget(self.editorSettingsBox)

        #---EDITOR NAME

        self.editorNameLabel=QLabel()
        self.editorNameLabel.setText('Editor Name')
        self.editorSettingsBoxLayout.addWidget(self.editorNameLabel,0,0)

        self.editorNameField=QLineEdit()
        self.editorSettingsBoxLayout.addWidget(self.editorNameField,0,1,1,3)

        # #---EDITOR USERNAME

        self.editorUsernameLabel=QLabel()
        self.editorUsernameLabel.setText('OSM Username')
        self.editorSettingsBoxLayout.addWidget(self.editorUsernameLabel,1,0)

        self.editorUsernameField=QLineEdit()
        self.editorSettingsBoxLayout.addWidget(self.editorUsernameField,1,1,1,3)

        # #--ADD/CLEAR/EDIT EDITOR SETTINGS BUTTONS

        self.editorButtonWidget=QWidget()
        self.editorButtonLayout=QHBoxLayout()
        self.editorButtonLayout.setContentsMargins(0,0,0,0)
        self.editorButtonLayout.setSpacing(0)
        self.editorButtonWidget.setLayout(self.editorButtonLayout)
        self.editorSettingsBoxLayout.addWidget(self.editorButtonWidget,2,0,1,4)

        self.addEditorButton=QPushButton()
        self.addEditorButton.setText('ADD')
        self.addEditorButton.setMaximumWidth(80)
        self.editorButtonLayout.addWidget(self.addEditorButton)

        self.clearEditorButton=QPushButton()
        self.clearEditorButton.setText('CLEAR')
        self.clearEditorButton.setMaximumWidth(80)
        self.editorButtonLayout.addWidget(self.clearEditorButton)

        self.editEditorButton=QPushButton()
        self.editEditorButton.setText('EDIT')
        self.editEditorButton.setMaximumWidth(80)
        self.editorButtonLayout.addWidget(self.editEditorButton)


        # #--EDITOR LINE SETTINGS




        self.editorLineColorButton=QPushButton()
        self.editorLineColorButton.setText("LINE COLOR")      
        self.editorSettingsBoxLayout.addWidget(self.editorLineColorButton,3,0)


        self.editorNodeColorPreview=QLabel()
        self.editorNodeColorpix = QtGui.QPixmap(15, 15)
        self.editorNodeColorpix.fill(QColor(WHITE))
        self.editorNodeColorPreview.setPixmap(self.editorNodeColorpix)
        self.editorSettingsBoxLayout.addWidget(self.editorNodeColorPreview,3,1,Qt.AlignmentFlag.AlignCenter)

        self.editorLineWidthLabel=QLabel()
        self.editorLineWidthLabel.setText('LINE WIDTH:')  
        self.editorSettingsBoxLayout.addWidget(self.editorLineWidthLabel,3,2) 

        self.editorLineWidthSpinner=QSpinBox()
        self.editorLineWidthSpinner.setRange(1, 20)
        self.editorLineWidthSpinner.setValue(5)
        self.editorSettingsBoxLayout.addWidget(self.editorLineWidthSpinner,3,3)         

        # #---EDITOR NODE HIGHLIGHT SETTINGS

        self.editorNodeColorButton=QPushButton()
        self.editorNodeColorButton.setText('NODE COLOR')
        self.editorSettingsBoxLayout.addWidget(self.editorNodeColorButton,4,0)

        self.editorNodeColorPreview=QLabel()
        self.editorNodeColorpix = QtGui.QPixmap(15, 15)
        self.editorNodeColorpix.fill(QColor(WHITE))
        self.editorNodeColorPreview.setPixmap(self.editorNodeColorpix)
        self.editorSettingsBoxLayout.addWidget(self.editorNodeColorPreview,4,1,Qt.AlignmentFlag.AlignCenter)

        self.editorNodeWidthLabel=QLabel()
        self.editorNodeWidthLabel.setText('NODE WIDTH:')  
        self.editorSettingsBoxLayout.addWidget(self.editorNodeWidthLabel,4,2) 

        self.editorNodeWidthSpinner=QSpinBox()
        self.editorNodeWidthSpinner.setRange(1, 20)
        self.editorNodeWidthSpinner.setValue(10)
        self.editorSettingsBoxLayout.addWidget(self.editorNodeWidthSpinner,4,3)            

        # #---TOGGLE UID BUTTON

        self.toggleUIDLabel=QLabel()
        self.toggleUIDLabel.setText('Toggle UID:')
        self.editorSettingsBoxLayout.addWidget(self.toggleUIDLabel,5,2,Qt.AlignmentFlag.AlignCenter)

        self.toggleUIDCheckbox=QCheckBox()
        self.editorSettingsBoxLayout.addWidget(self.toggleUIDCheckbox,5,3,Qt.AlignmentFlag.AlignCenter)        
    
        # #---EDITOR NODE SHAPE SETTINGS

        self.editorNodeShapeSelectButton=QPushButton()
        self.editorNodeShapeSelectButton.setText('NODE SHAPE')
        self.editorSettingsBoxLayout.addWidget(self.editorNodeShapeSelectButton,5,0)

        self.editorNodeShapePreview = QLabel()
        self.editorNodeShapePix=QPixmap(15,15)
        self.editorNodeShapePreview.setPixmap(self.editorNodeShapePix)
        self.editorSettingsBoxLayout.addWidget(self.editorNodeShapePreview,5,1)

        # ##--------------------TIME SEARCH SETTINGS--------------------

        self.timeSearchBox=QGroupBox()
        self.timeSearchBox.setTitle("Time Search")
        self.timeSearchBoxLayout=QGridLayout()

        self.timeSearchBox.setLayout(self.timeSearchBoxLayout)
        self.controlsWidgetLayout.addWidget(self.timeSearchBox)

        #---OPEN CALENDAR WIDGET


        self.openCalendarButton=QPushButton()
        self.openCalendarButton.setText('OPEN CALENDAR')
        self.timeSearchBoxLayout.addWidget(self.openCalendarButton,0,0,1,2) 

        #---START DATE WIDGET


        self.startDateLabel=QLabel()
        self.startDateLabel.setText('Start Date:')   
        self.timeSearchBoxLayout.addWidget(self.startDateLabel,1,0)

        self.startDateField=QLineEdit()
        self.timeSearchBoxLayout.addWidget(self.startDateField,1,1)        

        #---END DATE WIDGET

        self.endDateLabel=QLabel()
        self.endDateLabel.setText('end Date:')   
        self.timeSearchBoxLayout.addWidget(self.endDateLabel,2,0)

        self.endDateField=QLineEdit()
        self.timeSearchBoxLayout.addWidget(self.endDateField,2,1)           

        # #---SET DATES BUTTONS WIDGET

        self.dateButtonsWidget=QWidget()
        self.dateButtonsWidgetLayout=QHBoxLayout()
        self.dateButtonsWidget.setLayout(self.dateButtonsWidgetLayout)



        self.setDatesButton=QPushButton()
        self.setDatesButton.setText('SET DATES')
        self.dateButtonsWidgetLayout.addWidget(self.setDatesButton)

        self.clearDatesButton=QPushButton()
        self.clearDatesButton.setText('CLEAR DATES')
        self.dateButtonsWidgetLayout.addWidget(self.clearDatesButton)

        self.timeSearchBoxLayout.addWidget(self.dateButtonsWidget,3,0,1,2)

        # #---TOGGLE TIME SEARCH WIDGET


        self.toggleTimeSearchLabel=QLabel()
        self.toggleTimeSearchLabel.setText("Toggle Time Search")
        self.timeSearchBoxLayout.addWidget(self.toggleTimeSearchLabel,4,0,Qt.AlignmentFlag.AlignCenter)

        self.toggleTimeSearchCheckbox=QCheckBox()
        self.timeSearchBoxLayout.addWidget(self.toggleTimeSearchCheckbox,4,1,Qt.AlignmentFlag.AlignCenter)


        ##----------------------TABLE WIDGET--------------------------

        self.tableWidget=QGroupBox()
        self.tableWidget.setTitle("Table")
        self.tableWidgetLayout=QVBoxLayout()


        #self.tableWidgetLayout.addStretch(0)
        self.tableWidgetLayout.setSpacing(0)
        self.tableWidgetLayout.setContentsMargins(0,0,0,0)


        self.tableWidget.setLayout(self.tableWidgetLayout)
        self.mainWidgetLayout.addWidget(self.tableWidget,0,1)

        self.editorTable=QTreeWidget()
        self.editorTable.clicked.connect(lambda:editor_list_clicked(self))
        self.editorTable.setColumnCount(4)
        self.editorTable.setHeaderLabels(['Name','OSM Username','Line','Node'])
        self.editorTable.setSizePolicy (QSizePolicy.Minimum, QSizePolicy.Minimum)
        
        self.editorTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tableWidgetLayout.addWidget(self.editorTable)

        self.tableControlsWidget=QWidget()
        self.tableControlsWidget.setFixedHeight(110)
        self.tableControlsWidgetLayout=QGridLayout()
 
        self.tableControlsWidget.setLayout(self.tableControlsWidgetLayout)
        self.tableWidgetLayout.addWidget(self.tableControlsWidget)


        # self.topTableButtonsWidget=QWidget()
        
        # self.topTableButtonsWidget.setMaximumHeight(40)
        # self.topTableButtonsWidgetLayout=QHBoxLayout()
        # self.topTableButtonsWidget.setLayout(self.topTableButtonsWidgetLayout)
        # self.tableControlsWidgetLayout.addWidget(self.topTableButtonsWidget)


        self.importButton=QPushButton()
        self.importButton.setText("IMPORT")
        self.importButton.clicked.connect(lambda:importCssFile(self))
        self.importButton.setFixedWidth(110)
        self.tableControlsWidgetLayout.addWidget(self.importButton,0,0)        


        self.removeEditorButton=QPushButton()
        self.removeEditorButton.setText("REMOVE")
        self.removeEditorButton.clicked.connect(lambda:remove_editors(self))
        self.removeEditorButton.setFixedWidth(110)
        self.tableControlsWidgetLayout.addWidget(self.removeEditorButton,0,1)


        self.moveUpButton=QPushButton()
        self.moveUpButton.setText("MOVE UP")
        self.moveUpButton.clicked.connect(lambda:move_up(self))
        self.moveUpButton.setFixedWidth(110)
        self.tableControlsWidgetLayout.addWidget(self.moveUpButton,0,2)

        self.restackButton=QPushButton()
        self.restackButton.setText("RESTACK")

        self.restackButton.setFixedWidth(110)
        self.tableControlsWidgetLayout.addWidget(self.restackButton,0,3)


        # self.bottomTableButtonsWidget=QWidget()
        # self.bottomTableButtonsWidget.setMaximumHeight(40)
        # self.bottomTableButtonsWidgetLayout=QHBoxLayout()
        # self.bottomTableButtonsWidget.setLayout(self.bottomTableButtonsWidgetLayout)
        # self.tableControlsWidgetLayout.addWidget(self.bottomTableButtonsWidget)
        # self.tableWidgetLayout.addWidget(self.tableControlsWidget)

        self.exportButton=QPushButton()
        self.exportButton.setText("EXPORT")
        self.exportButton.setFixedWidth(110)
        self.tableControlsWidgetLayout.addWidget(self.exportButton,1,0)        

        self.removeAllEditorsButton=QPushButton()
        self.removeAllEditorsButton.setText("REMOVE ALL") 
        self.removeAllEditorsButton.clicked.connect(lambda:remove_all_editors(self))  
        self.removeAllEditorsButton.setFixedWidth(110)
        self.tableControlsWidgetLayout.addWidget(self.removeAllEditorsButton,1,1)

        self.moveDownButton=QPushButton()
        self.moveDownButton.setText("MOVE DOWN")
        self.moveDownButton.clicked.connect(lambda:move_down(self))
        self.moveDownButton.setFixedWidth(110)
        self.tableControlsWidgetLayout.addWidget(self.moveDownButton,1,2)

        self.isolateButton=QPushButton()
        self.isolateButton.setText("ISOLATE")
        self.isolateButton.setFixedWidth(110)
        self.tableControlsWidgetLayout.addWidget(self.isolateButton,1,3)



























# close ewindow event---------------------------------
    def closeEvent(self, event):
        #save_settings(self)
        # if self.team_obj != self.loaded_team_obj:
        #     autosave_team_file(self)
        # self.deleteLater()
        try:
            print("CLOSE")
            # self.changeset_mode_widget.close()
        except Exception as e:
            print(str(e))
        self.close()
# main loop-------------------------------------------
def main(args):
        app = QApplication(args)
        main=MainWindow()
        main.show()
        sys.exit(app.exec_())

def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback) 
    sys.exit(1) 
sys.excepthook = exception_hook
# main loop init--------------------------------------
while  True:
    main(sys.argv)