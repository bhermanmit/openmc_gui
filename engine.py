from __future__ import division

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import subprocess

class OpenMCEngine(QObject):
  def __init__(self, parent=None):
    QObject.__init__(self,parent=parent)
    self.outputlog = "output.log"
    
    
    
  def run(self,params,stencil):
    pass
    #self.make_inputs(stencil)
    #self.execute(params)
    
  def execute(self,params):
    timer = QTimer(self)
    QObject.connect(timer, SIGNAL("timeout()"), self.parse_output)
    timer.start(10)
    for i in range(10000000): pass
    timer.stop()
    
    # run openmc here with subprocess, piping output to self.outputlog
    
  def parse_output(self):
    # parse output here and fire signal with new datapoints for plotting
    # populate data dictionary from the output
    data = {}
    data['shannon'] = 1.3
    data['keff'] = 1.0
    self.emit(SIGNAL("new plot data"),data)
