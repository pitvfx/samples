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

Now, select the Add mode and the picker form the viewer toolbar.
![image](https://github.com/pitvfx/samples/blob/d36881f35811016ee4ea21e64f993fac8a1c5699/src/img/pp02.PNG)

Add points by holding down alt and right clicking into the viewer, the current frame will be start frame.
You can also select and delete points by changing the selection mode to either select or delete in the viewer toolbar and then alt click on the point. 

Alternative you can create points by randomly creating distributing them.
Open the random group and change the distribution box to the size you want your particles be distributed in. Choose the distribution mode, rectangle, in circle and on circle.Change the rest of the random attributes and hit the distribute button.
![image](https://github.com/pitvfx/samples/blob/d36881f35811016ee4ea21e64f993fac8a1c5699/src/img/pp04.PNG)


You can change all attributes of a particle, by first selecting one, either in the viewer (see above), or from the selection panel.
![image](https://github.com/pitvfx/samples/blob/d36881f35811016ee4ea21e64f993fac8a1c5699/src/img/pp03.PNG)
