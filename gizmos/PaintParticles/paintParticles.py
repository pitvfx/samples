import nuke
import random

import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets


class PaintParticlesUI(QtWidgets.QWidget):
    currentIndex = None
    
    def __init__(self, node):
        QtWidgets.QWidget.__init__(self, parent=None)
        self.node = node
        self.setLayout(QtWidgets.QHBoxLayout())
        self.treeWidget = QtWidgets.QTreeWidget()
        self.pKnobs = (("pos", node.node('pPosSizeRotate')['pPos']), ("frame", node.node('pFrame1')['pFrame']), ("sprite", node.node('pSprite1')['pSprite']), ("size", node.node('pPosSizeRotate')['pSize']), ("rotate", node.node('pPosSizeRotate')['pRotate']))
        self.treeWidget.setHeaderLabels([k for k, v in self.pKnobs])
        self.treeWidget.currentItemChanged.connect(self.itemChanged)
        self.update()
        self.layout().addWidget(self.treeWidget)
        
    @staticmethod
    def mapValues(values):
        mapValues = ["{0} , {1}".format(*values[0])]
        mapValues.extend(map(str, values[1:]))
        return mapValues
    
    def update(self):
        self.treeWidget.clear()
        amount = int(self.node['amount'].value())
        items = []
        for i in range(amount):
            itemData = self.mapValues([v.getValueAt(i) for k, v in self.pKnobs])
            items.append(QtWidgets.QTreeWidgetItem(itemData))
        self.treeWidget.insertTopLevelItems(0, items)
        self.filterByFrames()
        
    def addItem(self, data):
        self.treeWidget.addTopLevelItem(QtWidgets.QTreeWidgetItem(self.mapValues(data)))
    
    def removeItem(self, index):
        self.treeWidget.invisibleRootItem().removeChild(self.getItemFromIndex(index))
    
    def getItemFromIndex(self, index):
        return self.treeWidget.invisibleRootItem().child(index)
      
    def updateItem(self, column, values):
        item = self.getItemFromIndex(int(self.node['point'].value()))
        if column == "pos":
            values = self.mapValues([values])[0]
            col = 0
        else:
            values = str(values)
            col = [k for k,v in self.pKnobs].index(column)
        item.setText(col, values)
    
    def itemChanged(self, item):
        if not item:
            self.currentIndex = None
        index = self.treeWidget.indexFromItem(item).row()
        self.currentIndex = index
        paintParticlesKnobChanged(self.node, self.node["qtWidget"])
        
    def filterByFrames(self, frame=None):
        frame = int(frame if frame != None else nuke.frame())
        root = self.treeWidget.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            start = int(float(item.text(1)))
            end = int(self.node['lifetime'].value()) + start
            check = frame < start or frame > end
            item.setHidden(check)
            
    def clear(self):
        self.treeWidget.clear()
    
    def makeUI(self):
        return self
    
    def updateValue(self):
        pass

class PaintParticlesToolbar(QtWidgets.QWidget):
    def __init__(self, node):
        QtWidgets.QWidget.__init__(self, parent=None)
        self.node = node
        self.setLayout(QtWidgets.QHBoxLayout())
        
        self.addModeBtn = QtWidgets.QPushButton(text="add")
        self.addModeBtn.setCheckable(True)
        self.addModeBtn.clicked.connect(lambda:self.modeChange("add"))
        
        self.selectModeBtn = QtWidgets.QPushButton(text="select")
        self.selectModeBtn.setCheckable(True)
        self.selectModeBtn.clicked.connect(lambda:self.modeChange("select"))
        
        self.deleteModeBtn = QtWidgets.QPushButton(text="delete")
        self.deleteModeBtn.setCheckable(True)
        self.deleteModeBtn.clicked.connect(lambda:self.modeChange("delete"))
        
        self.layout().addWidget(self.addModeBtn)
        self.layout().addWidget(self.selectModeBtn)
        self.layout().addWidget(self.deleteModeBtn)
        self.layout().addStretch()
        
    
    def modeChange(self, mode):
        if mode == "add":
            knob = self.addModeBtn
            otherKnobs = [self.selectModeBtn, self.deleteModeBtn]
        elif mode == "select":
            knob = self.selectModeBtn
            otherKnobs = [self.addModeBtn, self.deleteModeBtn]
        else:
            knob = self.deleteModeBtn
            otherKnobs = [self.addModeBtn, self.selectModeBtn]
        value = knob.isChecked()
        if value:
            [k.setChecked(False) for k in otherKnobs]
            self.node['pickMode'].setValue(mode)
        else:
            self.node['pickMode'].setValue('none')
    
    def makeUI(self):
        return self
    
    def updateValue(self):
        pass

class PaintParticles(object):
    def __init__(self, node):
        self.node = node
        self.qtWidget = node['qtWidget'].getObject()
        self.amountKnob = node.node('pIndex')['amount']
        self.amount = int(self.amountKnob.value())
        self.pKnobs = {"pos": node.node('pPosSizeRotate')['pPos'], "frame": node.node('pFrame1')['pFrame'], "sprite": node.node('pSprite1')['pSprite'], "size": node.node('pPosSizeRotate')['pSize'], "rotate": node.node('pPosSizeRotate')['pRotate']}
        self.pointKnob = node['point']
        self.curPoint = int(self.pointKnob.value())
        self.pickMode = node['pickMode'].value()
        self.sampleNode = node.node('pointSelect')
        
    def changeValues(self, values, knobname, index=None):
        index = index if index != None else self.curPoint
        if knobname == "pos":
            self.pKnobs["pos"].setValueAt(values[0], index, 0)
            self.pKnobs["pos"].setValueAt(values[1], index, 1)
        else:
            self.pKnobs[knobname].setValueAt(values, index)
    
    def setPoint(self, point):
        point = int(max(0, (min(self.amount, point))))
        self.curPoint = point
        self.pointKnob.setValue(point)
        for knobname, pKnob in self.pKnobs.items():
            self.node[knobname].setValue(pKnob.getValueAt(point))
        for node, knob in [("previewSprite", "previewId"), ("killPreview", "previewId")]:
            self.node.node(node)[knob].setValue(point)
    
    def addPoint(self, pos, frame=None, sprite=0, size=None, rotate=0):
        amount = self.amount
        self.changeValues(pos, "pos", amount)
        frame = frame if frame else nuke.frame()
        self.changeValues(frame, "frame", amount)
        self.changeValues(sprite, "sprite", amount)
        size = size if size else self.node['initSize'].value()
        self.changeValues(size, "size", amount)
        self.changeValues(rotate, "rotate", amount)
        self.setPoint(max(0, amount))
        self.amount += 1
        self.amountKnob.setValue(self.amount)
        self.qtWidget.addItem([pos, frame, sprite, size, rotate])
    
    def pointChanged(self):
        changedPoints = self.node['changedPoints'].value().split(' ') + [self.curPoint]
        self.node['changedPoints'].setValue(' '.join(set(map(str, changedPoints))))
             
    def removePoint(self, point=None):
        point = point if point else self.curPoint
        for knob in self.pKnobs.values():
            knob.removeKeyAt(point)
            script = knob.toScript()
            script = nuke.re.sub(" x\d+ ", " ", script)
            knob.fromScript(script)
        self.amount -= 1
        self.amountKnob.setValue(self.amount)
        self.curPoint = min(self.amount-1, self.curPoint)
        self.qtWidget.removeItem(point)
    
    def reset(self, amount=True):
        for knobname, knob in self.pKnobs.iteritems():
            if knobname == "pos":
                knob.fromScript("curve curve")
            else:
                knob.fromScript("curve")
        if amount:
            for knob in [self.amountKnob, self.pointKnob]:
                knob.setValue(0)
            self.amount = 0
            self.point = 0
            
    def sortByFrame(self):
        sortedValues = []
        for i in range(self.amount):
            sortedValues.append(dict([(knobname, knob.getValueAt(i)) for knobname, knob in self.pKnobs.iteritems()]))
        self.reset(False)
        
        sortedValues.sort(key=lambda x: x['frame'])
        for i, sortedValue in enumerate(sortedValues):
            for k, v in sortedValue.iteritems():
                self.changeValues(v, k, i)
                
    def skipPointForw(self):
        point = min(self.amount-1 , self.curPoint+1)
        self.setPoint(point)
        
    def skipPointBackw(self):
        point = max(0 , self.curPoint-1)
        self.setPoint(point)
            
    def randomDistribute(self):
        mode = self.node['randMode'].value()
        box = self.node['randDistriBox'].getValue()
        width, height = box[2]-box[0], box[3]-box[1]
        center = [box[0]+ width/2, box[1] + height/2]
        
        amount = int(self.node['randAmount'].value())
        
        frameRand = self.node['frameRand'].getValue()
        spriteRand = self.node['spriteRand'].getValue()
        sizeRand = self.node['sizeRand'].getValue()
        rotRand = self.node['rotRand'].getValue()
        
        random.seed(int(self.node['randSeed'].value()))
        
        circleRand = self.node['circleRand'].value()
        circleWidth = self.node['circleWidth'].value()
        
        for i in range(amount):
            if mode == "rectangle":
                pos = [(random.random()*2-1)*(width/2) + center[0],  (random.random()*2-1)*(height/2) + center[1]]
            elif mode == "in circle":
                pos = [random.random()*2-1, random.random()*2-1]
                pos = [p/random._cos(p) for p in pos]
                l = random._sqrt(pos[0]*pos[0] + pos[1]*pos[1])
                pos = [(p/l)  for p in pos]
                pos = [pos[0] * (width/2) * (random.random()**.5) + center[0], pos[1] * (height/2) * (random.random()**.5) + center[1]]
            else:
                angle =  ((i/float(amount)) + (random.random()-.5)*circleRand) * random._pi*2
                pos = [random._cos(angle) * (width/2) + center[0] + (random.random()*2-1)*circleWidth, random._sin(angle) * (height/2) + center[1] + (random.random()*2-1)*circleWidth]
            frame = random.randrange(*frameRand)
            sprite = random.randrange(*spriteRand)
            size = random.randrange(*sizeRand)
            rot = random.randrange(*rotRand)
            self.addPoint(pos, frame, sprite, size, rot)
        
    def knobChanged(self, knob):   
        if knob.name() == "sampler":
            if self.pickMode != 'none':
                box = knob.value()[4:]
                center = [box[0] + (box[2]-box[0])/2.0,box[1] + (box[3]-box[1])/2.0]
                if self.pickMode == 'add':
                    self.addPoint(center)
                else:
                    if self.sampleNode.sample('rgba.alpha', center[0], center[1]) > 0.0:
                        point = self.sampleNode.sample('rgba.red', center[0], center[1])
                        if self.pickMode == "select":
                            self.setPoint(int(point))
                        else:
                            self.removePoint(int(point))                            
        elif knob.name() == "reset":
            self.reset()
            self.qtWidget.clear()
        elif knob.name() == "backw":
            self.skipPointBackw()
        elif knob.name() == "forw":
            self.skipPointForw()
        elif knob.name() == "distribute":
            self.randomDistribute()
        elif knob.name() == "sort":
            self.sortByFrame()
            self.qtWidget.update()
        elif knob.name() == "removePoint":
            self.removePoint()
        elif knob.name() == "qtWidget":
            if self.qtWidget and self.qtWidget.currentIndex != None:
                self.setPoint(self.qtWidget.currentIndex)
        elif knob.name() in self.pKnobs.keys():
            self.changeValues(knob.value(), knob.name())
            if self.node.shown():
                self.pointChanged()
                if self.qtWidget:
                    self.qtWidget.updateItem(knob.name(), knob.value())

def beforeRender(writeNode):
    sprite = writeNode.knobs().get('sprite')
    if sprite:
        for pP in nuke.allNodes('PaintParticles'):
            pP['output'].setValue(sprite.value())    
           

def paintParticlesKnobChanged(node=None, knob=None):
    node = nuke.thisNode() if node is None else node
    knob = nuke.thisKnob() if knob is None else knob
    
    if knob.name() == "showDevKnobs":
        v = node['devKnobs'].visible()
        node['devKnobs'].setVisible(not v)
    else:
        PaintParticles(node).knobChanged(knob)
        

def paintParticlesOnCreate():
    node = nuke.thisNode()
    if nuke.INTERACTIVE:
        tb = node['toolbar']
        tb.setFlag(0x00000002)
        tb.setFlag(0x00000010)
    else:
        node['preview'].setValue(False)


def paintParticlesViewerFrameChanged():
    node = nuke.thisNode()
    knob = nuke.thisKnob()
    if knob.name() == "frame":
        for pP in nuke.allNodes('PaintParticles'):
            qtObj = pP['qtWidget'].getObject()
            if qtObj:
                qtObj.filterByFrames(knob.value())
        
        
nuke.addKnobChanged(paintParticlesKnobChanged, nodeClass='PaintParticles')
nuke.addOnCreate(paintParticlesOnCreate, nodeClass='PaintParticles')
nuke.addKnobChanged(paintParticlesViewerFrameChanged, nodeClass='Viewer')