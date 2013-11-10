from __future__ import division

from PyQt4.QtCore import *
from PyQt4.QtGui import *

L = 100 # default pixel width of assembly displays

class CoreDisplay(QGraphicsView):

    def __init__(self,parent=None):
        QGraphicsView.__init__(self,parent)
        
        self.stencil = [
            [0, 1, 2, 1, 0],
            [1, 3, 4, 3, 1],
            [2, 4, 5, 4, 2],
            [1, 3, 4, 3, 1],
            [0, 1, 2, 1, 0],
            ]
        
        self.scene = QGraphicsScene(self)
        self.scene.maxZ = 0
        self.setScene(self.scene)
        self.connect(self.scene, SIGNAL("selectionChanged()"), self.refresh)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.draw_core()

    def resizeEvent(self, event):
        self.fitInView(self.scene.sceneRect(),Qt.KeepAspectRatio)

    def refresh(self):
        try:
            for item in self.scene.items():
                if isinstance(item,AssemblyDisplay):
                    item.refresh()
        except RuntimeError: pass


    def draw_core(self):

        self.scene.clear()

        numRows = len(self.stencil)
        numCols = len(self.stencil[0])

        for r,row in enumerate(self.stencil):
            for c,assType in enumerate(row):
                if assType == 0: continue
                ass = AssemblyDisplay(r,c,assType,self,scene=self.scene)
                self.connect(ass.sigFire,SIGNAL("assemblySwapped"),
                             self.assembly_swap)

        m = 20 # pixel margin
        self.scene.setSceneRect(-m,-m,numCols*L+2*m,numRows*L+2*m)

        self.fitInView(self.scene.sceneRect(),Qt.KeepAspectRatio)


    def assembly_swap(self,toFrom):

      from_row = toFrom[0][0]
      from_col = toFrom[0][1]
      
      to_row = toFrom[1][0]
      to_col = toFrom[1][1]
      
      tmp = self.stencil[to_row][to_col]
      self.stencil[to_row][to_col] = self.stencil[from_row][from_col]
      self.stencil[from_row][from_col] = tmp
      
      self.draw_core()

    def save_image(self,fname):
      img = QImage(self.scene.width(),self.scene.height(),QImage.Format_ARGB32_Premultiplied)
      p = QPainter(img)
      self.scene.render(p)
      p.end()
      img.save(fname)

class AssemblyDisplay(QGraphicsItem):
    def __init__(self,r,c,type_,view,parent=None,scene=None):
        QGraphicsItem.__init__(self,parent,scene)

        self.loc = [r,c]
        self.type = type_
        self.view = view

        self.sigFire = SignalFire()

        self.set_coloring()

        self.draw_item()
        
        self.setFlags(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)


    def set_coloring(self):
    
        if self.type == 0:
          self.defaultColor = Qt.gray
#        elif self.type == 1:
#          self.defaultColor = Qt.blue
#        elif self.type == 2:
#          self.defaultColor = Qt.yellow
#        elif self.type == 3:
#          self.defaultColor = Qt.green
#        elif self.type == 4:
#          self.defaultColor = Qt.darkRed
#        elif self.type == 5:
#          self.defaultColor = Qt.red
        else:
          self.defaultColor = QColor(self.type/5*255,(5-self.type)/5*255,0)
#          self.defaultColor = Qt.white


    def draw_item(self):

        self.color = self.defaultColor
        self.path = QPainterPath()
        points = [(0,0),(0,L),(L,L),(L,0)]
        self.path.addPolygon(QPolygonF([QPointF(x,y) for x,y in points]))
        self.path.closeSubpath()
        self.make_labels()
        self.translate(self.loc[1]*L,self.loc[0]*L)

        s = self.get_scale()
        s = 1
        self.pixmap = QPixmap(L*s,L*s)
        self.pixpainter = QPainter(self.pixmap)
        rect = self.boundingRect()
        rect.translate(self.loc[1]*L,self.loc[0]*L)
        self.scene().render(self.pixpainter,QRectF(0,0,L*s,L*s),rect)


    def make_labels(self):
        id_ = QGraphicsTextItem(parent=self)

        f1 = "Type {0}".format(self.type)
        if self.type == 0:
          f1 = ""
          f2 = ""
          f3 = ""
        elif self.type == 1:
          f2 = "1.6%"
          f3 = "no ba"
        elif self.type == 2:
          f2 = "2.4%"
          f3 = "no ba"
        elif self.type == 3:
          f2 = "2.4%"
          f3 = "12 ba"
        elif self.type == 4:
          f2 = "3.1%"
          f3 = "no ba"
        elif self.type == 5:
          f2 = "3.1%"
          f3 = "no ba"
        else:
          f2 = ""
          f3 = ""
        f4 = ""
        f5 = ""
        f6 = ""
        
        
        text = '<p style="font-size:12px">'
        text += "<center>{0}<\center>".format(f1)
        text += "<center>{0}</center>".format(f2)
        text += "<center>{0}</center>".format(f3)
        text += "<center>{0}</center>".format(f4)
        text += "<center>{0}</center>".format(f5)
        text += "<center>{0}</center>".format(f6)
        text += '</p>'
        id_.setHtml(text)
        id_.setTextWidth(L)


    def get_scale(self):
        sy = self.view.height()/self.scene().height()
        sx =  self.view.width()/self.scene().width()
        return min([sx,sy])

    def boundingRect(self):
        return self.path.boundingRect()

    def shape(self):
        return self.path

    def paint(self, painter, option, widget=None):
        painter.setPen(Qt.black)
        painter.setBrush(QBrush(self.color))
        painter.drawPath(self.path)

    def refresh(self):
        if self.isSelected() and self.type != 0:
            self.color = Qt.red
        else:
            self.color = self.defaultColor
        self.update()

    def hoverLeaveEvent(self, event):
        self.refresh()

    def hoverEnterEvent(self, event):
        if self.type == 0: return
        self.color = Qt.darkGray
        self.update()

    def dragEnterEvent(self, event):
        if self.type == 0: return
        if event.mimeData().assembly == self: return
        self.color = Qt.magenta
        self.update()

    def dragLeaveEvent(self, event):
        if self.type == 0: return
        self.color = self.defaultColor
        self.update()

    def dropEvent(self, event):
        if self.type == 0: return
        from_ = event.mimeData().assembly.loc
        to = self.loc
        if from_ != to:
            self.sigFire.fireSwap(to,from_)

    def mousePressEvent(self, event):
        if self.type == 0: return
        for item in self.scene().selectedItems():
            item.setSelected(False)
        self.setSelected(True)

    def mouseMoveEvent(self, event):
        if self.type == 0: return
        drag = QDrag(event.widget())
        mime = QMimeData()
        mime.assembly = self
        drag.setMimeData(mime)
        s = self.get_scale()
        drag.setPixmap(self.pixmap.scaledToWidth(L*s))
        drag.setHotSpot(QPoint(event.pos().x()*s,event.pos().y()*s))
        drag.start()


class SignalFire(QObject):
    def __init__(self,parent=None):
        QObject.__init__(self,parent)
    def fireSwap(self,to,from_):
        self.emit(SIGNAL("assemblySwapped"),[from_,to])

