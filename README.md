# Samples

## python

### my3d.py

**description**
A small selection of helper functions working in 3d and with 3d geo in Nuke.

**animAxisFromVertex:**
select a vertex with animation and run. The resulting axis will follow the vertex.


**animAxisFromAlembicTransform:**
Select a ReadGeo with alembic cache file and run. Returns an Axis for each geo and animates it local_matrix with the alembic cache geo.


**axisFromAxis:**
Select one or more Axises and run. Selec a method in the panel and result will be an Axis based on the selection made. Works basically like the snap_menu, but with Axis than Vertexes.


**inverseAxis:**
Select an Axis and run. The result is the inverted Axis. Inverses the world_matrix!

## gizmos

### PaintParticles

**description**
Let's the user "paint" Particles in the viewer.

**installation**
Unpack both paintParticles.py and PaintParticles.gizmo into the .nuke folder and insert the following lines into the menu.py
        
        import paintParticles
        nuke.menu("Nodes").addCommand("PaintParticles/PaintParticles", nuke.nodes.PaintParticles)

**usage**
First, set the format, lifetime and intial size for your particles.

![image](src/img/pp01.png)



