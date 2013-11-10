from __future__ import division

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from subprocess import Popen, STDOUT, PIPE
import sys

class OpenMCEngine(QObject):
  def __init__(self, parent=None):
    QObject.__init__(self,parent=parent)
    self.outputlog = "output.log"
    
  def run(self,params,stencil):
    self.make_inputs(stencil)
    self.execute(params)

  def run_plot(self,stencil):
    self.make_inputs(stencil)
    proc = Popen(['openmc','--plot','tmpdir/minicore_inputs'])
    proc.wait()
    self.process_geometry_plot()
  def make_inputs(self,stencil):
      geotemp = 'tmpdir/minicore_inputs/geometry.template'
      geofile = 'tmpdir/minicore_inputs/geometry.xml'
      with open(geotemp,'r') as fh:
          lines = fh.read().splitlines()
      rowbegin = 7697 # where does core lattice start
      nlines = 5
      colbegin = 7
      for i in range(nlines):
          aline = lines[rowbegin + i] # extract line
          sline = aline.split() # split line by spaces

          # check for corner indents in row
          if i == 0 or i == nlines - 1:
              for j in range(3):
                  sline[colbegin + j + 1] = self.map_core(stencil[i][j+1])
          else:
              for j in range(5):
                  sline[colbegin + j] = self.map_core(stencil[i][j])

          # replace the line
          newstr = ''
          for item in sline:
              newstr += '{0} '.format(item)
          lines[rowbegin + i] = newstr
          print newstr
          # rewrite file
          with open(geofile,'w') as fh:
              for aline in lines:
                  fh.write(aline + '\n')

  def map_core(self,guid):
      if guid == 1:
          return str(144) # 1.6% No BAs
      if guid == 2:
          return str(180) # 2.4% No BAs
      if guid == 3:
          return str(184) # 2.4% 12 BAs
      if guid == 4:
          return str(196) # 3.1% No BAs
      if guid == 5:
          return str(200) # 3.1% 20 BAs

  def execute(self,params):
#   timer = QTimer(self)
#   QObject.connect(timer, SIGNAL("timeout()"), self.parse_output)
#   timer.start(10)
#   for i in range(10000000): pass
#   timer.stop()
    
    # run openmc here with subprocess, piping output to self.outputlog
#   fh = open('output.log','w')
    proc = Popen(['openmc','tmpdir/minicore_inputs'])
#   fh.close()

  def parse_output(self):
    # parse output here and fire signal with new datapoints for plotting
    # populate data dictionary from the output
    data = {}
    data['shannon'] = 1.3
    data['keff'] = 1.0
    self.emit(SIGNAL("new plot data"),data)

  def process_geometry_plot(self):
      proc = Popen(['convert','tmpdir/minicore_inputs/1_slice.ppm','tmpdir/minicore_inputs/1_slice.png'])
