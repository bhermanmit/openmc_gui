#!/usr/bin/env python

from __future__ import division

import sys
import os
import platform
import copy

import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import widgets
import engine

__version__ = "0.0.1"

class MainWindow(QMainWindow):

    def __init__(self, parallel=False, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowTitle("OpenMC Demonstration GUI")

        self.engine = engine.OpenMCEngine()

        # Add menu items

        self.menubar = QMenuBar(self)

        self.menuFile = QMenu("&File",self.menubar)
        self.actionSaveImg = QAction("Save Core &Image",self)
        self.connect(self.actionSaveImg, SIGNAL("triggered()"), self.save_img)
        self.actionExit = QAction("E&xit",self)
        self.connect(self.actionExit, SIGNAL("triggered()"), self.close)
        self.menuFile.addActions([self.actionSaveImg,self.actionExit])
        self.menuFile.insertSeparator(self.actionExit)

        self.menuHelp = QMenu("&Help",self.menubar)
        self.actionAbout = QAction("&About",self)
        self.connect(self.actionAbout, SIGNAL("triggered()"), self.about)
        self.menuHelp.addActions([self.actionAbout])

        self.menubar.addActions([self.menuFile.menuAction(),
                                 self.menuHelp.menuAction()])
        self.setMenuBar(self.menubar)

        # Instantiate widgets

        self.coreDisplay = widgets.CoreDisplay(None)
        self.plotShannon = widgets.PlotWidget()
        self.plotKeff = widgets.PlotWidget()
        self.powerDist = widgets.PlotWidget()
        self.logView = widgets.LogWatcher(self.engine.outputlog)
        self.assemblyControls = widgets.AssemblyControls()

        # Setup widget layouts

        rightLayout = QHBoxLayout()
        tabsPlot = QTabWidget()
        tabsPlot.addTab(self.plotKeff, "K effective")
        tabsPlot.addTab(self.plotShannon, "Shannon Entropy")
        tabsPlot.addTab(self.powerDist, "Power Distribution")

        outerHorSplit = QSplitter()
        leftVertSplit = QSplitter()
        rightVertSplit = QSplitter()
        leftVertSplit.setOrientation(Qt.Vertical)
        rightVertSplit.setOrientation(Qt.Vertical)

        self.coreDisplay.setMinimumSize(400,400)
        leftVertSplit.addWidget(self.coreDisplay)
        leftVertSplit.addWidget(self.assemblyControls)

        rightVertSplit.addWidget(tabsPlot)
        rightVertSplit.addWidget(self.logView)

        outerHorSplit.addWidget(leftVertSplit)
        outerHorSplit.addWidget(rightVertSplit)
        self.setCentralWidget(outerHorSplit)
        
        self.connect(self.assemblyControls,SIGNAL("run openmc"),self.run_openmc)
        self.connect(self.assemblyControls,SIGNAL("run openmc plot"),self.run_openmc_plot)
        
        self.connect(self.engine,SIGNAL("new output data"),self.update_plots)

    def run_openmc(self,params):
    
      self.plotShannon.clear()
      self.plotKeff.clear()
    
      stencil = self.coreDisplay.stencil
      self.engine.run(params,stencil)

    def run_openmc_plot(self):
      stencil = self.coreDisplay.stencil
      self.engine.run_plot(stencil)

    def update_plots(self,data):
      self.plotKeff.add_point(data['keff'])
      self.plotShannon.add_point(data['shannon'])

    def save_img(self):
      filename = QFileDialog.getSaveFileName(self, "Save Core Image", "./",
                                               "PNG Files (*.png)")
      if filename:
        if not str(filename[-4:]).lower() == '.png':
          filename = str(filename) + ".png"
        self.coreDisplay.save_image(filename)

    def about(self):
        QMessageBox.about(self, "About OpenMC Demonstration GUI",
                          """<b>OpenMC Demonstration GUI</b> v %s
                          <p>Copyright &copy; 2013 Nick Horelik, Bryan Herman
                          All Rights Reserved.
                          <p>Python %s -- Qt %s -- PyQt %s on %s""" %
                          (__version__, platform.python_version(),
                           QT_VERSION_STR, PYQT_VERSION_STR, platform.system()))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()
