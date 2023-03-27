import nuke
import nukescripts
import math

def animAxisFromVertex():
    ct = nuke.nodes.CurveTool()
    axis = nuke.nodes.Axis3()
    axis["translate"].setAnimated()
    try:
        for f in nuke.root().frameRange():
            nuke.execute(ct, f, f)
            v = nukescripts.snap3d.anySelectedPoint()
            axis["translate"].setValueAt(v.x, f, 0)
            axis["translate"].setValueAt(v.y, f, 1)
            axis["translate"].setValueAt(v.z, f, 2)
    except:
        nuke.delete(axis)
        raise
    finally:
        nuke.delete(ct)

def animAxisFromAlembicTransform():
    node = nuke.selectedNode()
    geo_select = node.knobs().get("geo_select")
    scene_view = node.knobs().get("scene_view")
    if not (geo_select and scene_view):
        return
    geos = geo_select.getGeometry()
    ct = nuke.nodes.CurveTool()

    names = []
    try:
        for i, geoName in enumerate(scene_view.getSelectedItems()):
            name = geoName.split('/')[2]
            if name in names:
                continue
            names.append(name)
            axis = nuke.nodes.Axis3(name=name, useMatrix=True)
            axis['matrix'].setAnimated()
            geo = geos[i]
            for f in nuke.root().frameRange():
                nuke.execute(ct, f, f)
                m = geo.transform()
                m.transpose()
                for j in range(16):
                    axis['matrix'].setValueAt(m[j], f, j)
    except :
        raise
    finally:
        nuke.delete(ct)

def axisFromAxis():
    selAxis = [a for a in nuke.selectedNodes() if nuke.re.match(r"^Axis[\d]*$", a.Class())]
    if not selAxis:
        return
    vs = nukescripts.snap3d.VertexSelection()
    for i, axis in enumerate(selAxis):
        mat = axis["world_matrix"].getValue()
        vi = nukescripts.snap3d.VertexInfo(0, i, 1, nukescripts.snap3d._nukemath.Vector3(mat[3], mat[7], mat[11]))
        vs.add(vi)
    
    p = nuke.Panel("Snap Axis")
    values = {"position" : nukescripts.snap3d.translateToPointsVerified, "position rotate": nukescripts.snap3d.translateRotateToPointsVerified, "position rotate scale": nukescripts.snap3d.translateRotateScaleToPointsVerified}
    p.addEnumerationPulldown("snap mode", ' '.join('"{}"'.format(v) for v in values.keys()))
    if not p.show():
        return
    axis = nuke.nodes.Axis3()
    func = values[p.value("snap mode")]
    func(axis, vs)
    return axis

def inverseMatrix(matrix):
    rotMatr = nuke.math.Matrix4()
    rotMatr.makeIdentity()
    pos = []
    for i in range(12):
        if i % 4 == 3:
            pos.append(-matrix[i])
        else:
            rotMatr[i] = matrix[i]
    rotMatr.transpose()
    rotMatr = rotMatr.inverse()
    rot = [math.degrees(r) for r in rotMatr.rotationsYXZ()]
    return (pos, rot)
    
def inverseAxis(anim=False):
    inaxis = nuke.selectedNode()
    worldMatrix = inaxis.knobs().get("world_matrix")
    if not (worldMatrix and isinstance(worldMatrix, nuke.IArray_Knob) and worldMatrix.arraySize() == 16):
        return
    axis = nuke.nodes.Axis3(rot_order="YXZ", xform_order="TRS")
    transKnob = axis["translate"]
    rotKnob = axis["rotate"]
    if anim:
        transKnob.setAnimated()
        rotKnob.setAnimated()
        for f in nuke.root().frameRange():
            pos, rot = inverseMatrix(worldMatrix.getValueAt(f))
            for i in range(3):
                transKnob.setValueAt(pos[i], f, i)
                rotKnob.setValueAt(rot[i], f, i)
    else:
        pos, rot = inverseMatrix(worldMatrix.getValue())
        for i in range(3):
            transKnob.setValue(pos[i], i)
            rotKnob.setValue(rot[i], i)
    return axis
    