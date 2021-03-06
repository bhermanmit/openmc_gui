from __future__ import division

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from subprocess import Popen, STDOUT, PIPE
import sys
import statepoint
import glob
import time

class OpenMCEngine(QWidget):
  def __init__(self, parent=None):
    QWidget.__init__(self,parent=parent)
    self.outputlog = "output.log"
    self.currently_running = False
    
  def run(self,params,stencil):
    self.make_inputs(stencil)
    self.execute(params)

  def run_plot(self,stencil):
  
    self.make_inputs(stencil)

    worker = Worker(self,plot=True)
    
    self.progress = QProgressDialog("Processing Plot...","Cancel",0,100,self)
    self.progress.setWindowTitle("Processing Plot")
    self.progress.setMinimumDuration(0)
    self.progress.setWindowModality(Qt.WindowModal)
    self.connect(self.progress,SIGNAL("canceled()"),worker.cancel)
    self.connect(worker,SIGNAL("finished error"),self.progress,SLOT("cancel()"))
    self.connect(worker,SIGNAL("finished success"),self.progress,SLOT("cancel()"))
    self.progress.setValue(0)
    
    # if we make the progress bar persist as a member of the engine class, we
    # can call setValue on it to update the value it displays
    
    QObject.connect(worker,SIGNAL("finished success"),self.process_geometry_plot)
    worker.start()

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
    if self.currently_running: return
    self.currently_running = True
    worker = Worker(self)
    QObject.connect(worker,SIGNAL("finished success"),self.run_completed)
    worker.start()

  def run_completed(self):
    self.currently_running = False
    self.process_tallies()

#  def parse_output(self):
#    # parse output here and fire signal with new datapoints for plotting
#    # populate data dictionary from the output
#    data = {}
#    data['shannon'] = 1.3
#    data['keff'] = 1.0
#    self.emit(SIGNAL("new plot data"),data)

  def process_geometry_plot(self):
      proc = Popen(['convert','tmpdir/minicore_inputs/1_slice.ppm','tmpdir/minicore_inputs/1_slice.png'])
      proc.wait()
      self.emit(SIGNAL("new geometry plot"),'tmpdir/minicore_inputs/1_slice.png')

  def extract_mean(self, sp, tally_id, score_id):

      # extract results
      results = sp.extract_results(tally_id,score_id)

      # extract means and copy
      mean = results['mean'].copy()

      # reshape and integrate over energy
      mean = mean.reshape(results['bin_max'],order='F')
      mean = mean/mean.sum()*(mean > 1.e-8).sum()

      return mean

  def process_tallies(self):

      # get statepoint filename
      spfile = glob.glob('tmpdir/minicore_outputs/statepoint*')[0]

      # extract all means
      sp = statepoint.StatePoint(spfile)

      # plot
      sp.read_results()

      # extract distributions 
      nfiss = self.extract_mean(sp, 1, 'nu-fission')
      flux2 = self.extract_mean(sp, 2, 'flux')
      flux1 = self.extract_mean(sp, 3, 'flux')

      # write out data
      self.write_gnuplot_data(nfiss, flux1, flux2)

      # run gnuplot
      Popen(['gnuplot','tmpdir/minicore_outputs/nfiss.plot'])
      Popen(['gnuplot','tmpdir/minicore_outputs/flux1.plot'])
      Popen(['gnuplot','tmpdir/minicore_outputs/flux2.plot'])
      
      self.emit(SIGNAL("new output plots"),
                ["tmpdir/minicore_outputs/nfiss.png",
                 "tmpdir/minicore_outputs/flux1.png"])

  def write_gnuplot_data(self, nfiss, flux1, flux2):

    nfiss_str = ""
    for i in range(nfiss.shape[0]):
        for j in range(nfiss.shape[1]):
                nfiss_str += '{0} '.format(nfiss[i,j,0])
        nfiss_str += '\n'

    flux1_str = ""
    for i in range(flux1.shape[1]):
        for j in range(flux1.shape[2]):
                flux1_str += '{0} '.format(flux1[0,i,j,0])
        flux1_str += '\n'

    flux2_str = ""
    for i in range(flux2.shape[1]):
        for j in range(flux2.shape[2]):
                flux2_str += '{0} '.format(flux2[0,i,j,0])
        flux2_str += '\n'

    with open('tmpdir/minicore_outputs/nfiss.dat','w') as fh:
        fh.write(nfiss_str)
    with open('tmpdir/minicore_outputs/flux1.dat','w') as fh:
        fh.write(flux1_str)
    with open('tmpdir/minicore_outputs/flux2.dat','w') as fh:
        fh.write(flux2_str)

class Worker(QThread):

    def __init__(self,parent,plot=False):
        '''Parent must be defined to stop early garbage collection'''
        QThread.__init__(self,parent)
        self.plot = plot
        self.cancelled = False

    def run(self):
      try:
        if self.plot:
          proc = Popen(['mpiexec','-np','4','openmc','--plot','tmpdir/minicore_inputs'])
        else:
          proc = Popen(['mpiexec','-np','4','openmc','tmpdir/minicore_inputs'])

        while proc.poll() is None:
          if self.cancelled:
            proc.kill()
            self.emit(SIGNAL("finished error"))
            return
          time.sleep(0.1)

        self.emit(SIGNAL("finished success"))

      except OSError:
        print "Problem running OpenMC!  Is the exe in the path?"
        self.emit(SIGNAL("finished error"))
        
    def cancel(self):
      self.cancelled = True
