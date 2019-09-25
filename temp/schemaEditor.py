#!/usr/bin/python3
import argparse
from datetime import datetime
from pymongo import MongoClient
from bson import json_util
import json
import time
from collections import OrderedDict
import sys

from PyQt5.QtWidgets import QWidget, QApplication, QFrame, QDesktopWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QComboBox

from ADB import ADB
from SmartWidget import SmartWidget


##
# \class This class allows users to edit mongodb schemas
#
class SchemaEditor( QWidget ):
    def __init__(self):
        uriMap = {}
        self.dbs = []
        self.dbase = None
        self.collection = None

    def init( self, uri ):
        print("Initializing")
        #URI Value
        self.adb = ADB(uri)

        super().__init__()

        #Determine screen settings
        geo         = self.frameGeometry()
        self.width  = QDesktopWidget().availableGeometry().width();
        self.height = QDesktopWidget().availableGeometry().height();

        #Define window par meters
        self.resize(self.width*.5, self.height*.5 )
        self.setWindowTitle("Aqueti Schema Editor")
        self.show()

        self.mainLayout = QVBoxLayout()

        #Create title
        self.titleLayout = QHBoxLayout()
        self.titleLayout.addStretch(1)
        title = QLabel()
        title.setText("Aqueti Schema Editor")
        self.titleLayout.addWidget(title)
        self.titleLayout.addStretch(1)
        self.mainLayout.addLayout( self.titleLayout )

        #create the selector layout (allow user to select database)
        self.dbFrame = QFrame()
 
        print("Add QFrame")
        self.dbFrame.setLayout(self.genDBSelectorWidget())
       
        print("Added QFrame")
        self.collFrame = QFrame()
        self.collFrame.setLayout( self.genCollSelectorWidget())

        selectorFrame = QFrame()
        selectorLayout = QHBoxLayout()
        selectorLayout.addWidget( self.dbFrame)
        selectorLayout.addWidget( self.collFrame)

        self.mainLayout.addLayout(selectorLayout)
        
#        self.dbLayout = self.dbSelectorWidget()
#        self.mainLayout.addLayout(self.dbLayout)
        #The middle section will have a scroll area
        scrollArea = QScrollArea()
        scrollWidget = QWidget()

        scrollArea.setWidget(scrollWidget)
        scrollArea.setWidgetResizable(True)

        scrollLayout = QVBoxLayout()
        scrollLayout.addWidget(scrollArea)
        #Create a middle section
        self.midLayout = QVBoxLayout()
        scrollWidget.setLayout(self.midLayout)
        self.mainLayout.addLayout( scrollLayout )

#        self.draw()

#        self.mainLayout.addStretch(1)

        #submitButton
        submitButton = QPushButton("Submit")
        submitButton.clicked.connect( lambda: self.submitButtonPressEvent())
        self.mainLayout.addWidget(submitButton)

        self.setLayout( self.mainLayout)
        print("Finishing init")

    ##
    # \brief draw all items in the window
    def draw( self ):
        #Remove all widgets from the current layout
        while self.midLayout.count():
             item = self.midLayout.takeAt(0)
             widget = item.widget()
             if widget is not None:
                  widget.deleteLater()
       
        
        collection = self.collCombo.currentText()

        try:
           schema = self.adb.getSchema(collection)
           value  = self.adb.getDocuments(collection,{"_id":"5d8a9ff62dfe4c08d5850aab"},1)
           value  = value[0]
        except:
            print("Failed to get information for the database")
            schema = None
            value = {}
            return
 
        print("SDF value:"+str(value))
        print("SDF schema:"+str(schema))
        s2 = {}
        s2["bsonType"] = "object"
        s2["properties"] = schema
        s2["properties"]["_id"]  = {"bsonType":"string"}
        print("S2: "+str(s2))
        smartWidget = SmartWidget().init("schema", value, s2 )
        self.midLayout.addWidget(smartWidget.frame)

        #Get the current schema, if any
#        info = QLabel()
#        info.setText(str(schema))
#        self.midLayout.addWidget(info)
        """
        scrollArea = QScrollArea()
        scrollWidget = QWidget()

        scrollWidget.setLayout(self.mainLayout)
        scrollArea.setWidget(scrollWidget)
        scrollArea.setWidgetResizable(True)

        lastLayout = QVBoxLayout()
        lastLayout.addWidget(scrollArea)

        self.setLayout( lastLayout)
        """

    def genCollSelectorWidget(self):
        self.dbase = self.dbCombo.currentText()
        print("Using :"+self.dbase)
        self.adb.setDatabase( self.dbase )

        #the database to use
        self.collLayout = QHBoxLayout()
        info = QLabel()
        info.setText("Collection")

        self.collCombo = QComboBox()
        self.collCombo.addItems( self.adb.getCollections())

        print("Getting collections for "+self.dbase)
        print("Collections:"+str(self.adb.getCollections()))

        submitButton = QPushButton("UpdateColl")
        submitButton.clicked.connect( lambda: self.updateCollButtonPressEvent())

        self.collLayout.addWidget(info)
        self.collLayout.addWidget(self.collCombo)
        self.collLayout.addWidget(submitButton)

        self.collLayout.addStretch(1)
        return self.collLayout

    ##
    # \brief Generate the database selector widget
    def genDBSelectorWidget(self):
        #the database to use
        self.dbLayout = QHBoxLayout()
        info = QLabel()
        info.setText("Database")

        self.dbCombo = QComboBox()
        self.dbCombo.addItems( self.adb.getDatabaseList())

        submitButton = QPushButton("UpdateDB")
        submitButton.clicked.connect( lambda: self.updateDBButtonPressEvent())
#        self.dbLayout.addWidget(submitButton)

        self.dbLayout.addWidget(info)
        self.dbLayout.addWidget(self.dbCombo)
        self.dbLayout.addWidget(submitButton)
#        self.dbLayout.addStretch(1)

        return self.dbLayout

    ##
    # \brief handles database updates
    def updateCollButtonPressEvent(self):
        value = self.collCombo.currentText()
        if self.collection == value:
            print("collections match")
        else:
            self.draw()
#        if self.collection != value:
#            self.collection= value
#            self.draw()

    ##
    # \brief handles database updates
    def updateDBButtonPressEvent(self):
        print("Updating db")
        value = self.dbCombo.currentText()
        if self.dbase == value:
            print("Databases match")
        else:
            print("Setting database to "+value )
            self.dbase = value
            self.adb.setDatabase( self.dbase )
            self.collCombo.clear()
            self.collCombo.addItems( self.adb.getCollections())

            self.draw()

    ##
    # \brief handless a submit button event
    def submitButtonPressEvent(self):
        print("Submission")
        self.close()



def main():
    dbase = "schemas"
    uri = "localhost:27017"

    parser = argparse.ArgumentParser(description="Database Script")
    parser.add_argument('-uri', action='store', dest='uri', help='URI of the mongodb system')
    parser.add_argument('-dbase', action='store', dest='dbase', help='database to reference')
    parser.add_argument('-test', action='store_true', dest='test', help='unit test')

    args=parser.parse_args()
    if args.uri:
        uri = args.uri

    if args.dbase:
        dbase =args.dbase

    app = QApplication( sys.argv )

    print("Creating scheme editor with URI: "+str(uri))
    window = SchemaEditor()
    window.init(uri)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
