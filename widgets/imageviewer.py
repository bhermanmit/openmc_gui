from __future__ import division

from PyQt4.QtCore import *
from PyQt4.QtGui import *


class ImageViewer(QGraphicsView):

  def __init__(self,image_path=None, parent=None):
    QGraphicsView.__init__(self,parent)

    self.imagePath = image_path

    self.scene = QGraphicsScene(self)
    self.setScene(self.scene)
    
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    
    self.set_image(self.imagePath)
    
  def set_image(self, path):
    self.imagePath = path
    self.scene.clear()
    if self.imagePath:
      pm = QPixmap(self.imagePath)
      item = QGraphicsPixmapItem(pm)
      self.scene.addItem(item)
      self.fitInView(self.scene.sceneRect(),Qt.KeepAspectRatio)
  
  def resizeEvent(self, event):
    self.fitInView(self.scene.sceneRect(),Qt.KeepAspectRatio)
