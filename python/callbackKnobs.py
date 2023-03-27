import nuke, nukescripts

class showCallbackKnobsPanel(nukescripts.PythonPanel):
    def __init__(self, dictonary):
        nukescripts.PythonPanel.__init__(self, 'Callback Knobs Panel')
        self.setMinimumSize(700, 550)
        self.nodeKnob = nuke.Enumeration_Knob('node', 'node', [])
        self.subNodeKnob = nuke.Enumeration_Knob('subNodes', 'sub nodes', [])
        self.valueKnob = nuke.Multiline_Eval_String_Knob('values', 'values', '')
        self.defaultKnob = nuke.PyScript_Knob('default', 'default')
        self.resetKnob = nuke.PyScript_Knob('reset', 'reset')
        self.defaultKnob.setFlag(nuke.STARTLINE)
        self.resetKnob.clearFlag(nuke.STARTLINE)
        for k in (self.nodeKnob, self.subNodeKnob, self.valueKnob, self.defaultKnob, self.resetKnob):
                    self.addKnob(k)
        self.knobChangedDict = dictonary
        self.orgDict = dictonary
        
        self.nodeKnob.setValues(self.knobChangedDict.keys())

    def knobChanged(self, knob):
        node = self.nodeKnob.value()
        subNode = self.subNodeKnob.value()
        if knob is self.nodeKnob or knob.name()=='showPanel':
            subList = [key for key in self.knobChangedDict[node].keys() if key != 'values']
            subList.insert(0, 'None')
            self.subNodeKnob.setValues(subList)
            value = self.knobChangedDict[node]['values']
            self.valueKnob.setValue(value)
        if knob is self.subNodeKnob:
            value = ''
            if self.subNodeKnob.value() == 'None':
                value = self.knobChangedDict[self.nodeKnob.value()]['values']
            else:
                value = self.knobChangedDict[self.nodeKnob.value()][self.subNodeKnob.value()]['values']
            self.valueKnob.setValue(value)
        if knob is self.valueKnob:
            if subNode == 'None':
                self.knobChangedDict[node]['values'] = self.valueKnob.value()
            else:
                self.knobChangedDict[node][subNode]['values'] = self.valueKnob.value()
        if knob is self.resetKnob:
            value = ''
            if subNode == 'None':
                self.knobChangedDict[node]['values'] = self.orgDict[node]['values']
                value = self.orgDict[node]['values']
            else:
                self.knobChangedDict[node][subNode]['values'] = self.orgDict[node][subNode]['values'] 
                value = self.orgDict[node][subNode]['values']
            self.valueKnob.setValue(value)
        if knob is self.defaultKnob:
            default = "n = nuke.thisNode()\nk=nuke.thisKnob()\n\nif k.name() == '':\n    pass "
            if subNode == 'None':
                self.knobChangedDict[node]['values'] = default
            else:
                self.knobChangedDict[node][subNode]['values'] = default
            self.valueKnob.setValue(default)


def getDict(mode):
    d = {}
    for node in [node for node in nuke.selectedNodes() if node.Class() not in ('Viewer', 'Input', 'Output')]:
        if nuke.exists(node.name()+ '.' + mode):
            d[node.name()] = {'values': node[mode].value()}
            try:
                for subNode in [subNode for subNode in node.nodes() if subNode.Class() not in ('Viewer', 'Input', 'Output')]:
                    if nuke.exists('%s.%s.%s' % (node.name(), subNode.name(), mode)):
                        d[node.name()][subNode.name()] = {'values': subNode[mode].value()}
            except:
                pass
            return d

def callbackKnobsByUI(mode):
    if len(nuke.selectedNodes()):
        d = getDict(mode)
        panel = showCallbackKnobsPanel(d)
        if panel.showModalDialog():
            changedDict = panel.knobChangedDict
            for node in changedDict:
                values = changedDict[node]['values']
                toNode = nuke.toNode(node)
                toNode[mode].setValue(values)
                subList = [key for key in changedDict[node].keys() if key != 'values']
                for subNode in subList:
                    values = changedDict[node][subNode]['values']
                    toSubNode = nuke.toNode('%s.%s' % (node, subNode))
                    toSubNode[mode].setValue(values)
    else: 
        nuke.message('Please select node(s)!')