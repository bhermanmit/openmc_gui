from __future__ import division

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class AssemblyControls(QWidget):
  def __init__(self,parent=None):
    QWidget.__init__(self,parent)
    
    # Parameter dict, sent out in the run signal
    self.params = {}
    
    # can create any number of other widget e.g. buttons, slides, labels, and
    # add them to a layout here
    self.run_button = QPushButton("Run OpenMC")
    self.run_button2 = QPushButton("Plot Geometry")
    layout = QVBoxLayout()
    layout.addWidget(self.run_button)
    layout.addWidget(self.run_button2)
    self.setLayout(layout)
    
    QObject.connect(self.run_button, SIGNAL("clicked()"), self.fire_run_signal)
    QObject.connect(self.run_button2, SIGNAL("clicked()"), self.fire_run_signal_plot)
    
  def fire_run_signal(self):
    # populate the params dictionary here to send info from this widget out with
    # the signal
    self.emit(SIGNAL("run openmc"),self.params)

  def fire_run_signal_plot(self):
    self.emit(SIGNAL("run openmc plot"))
