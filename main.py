from math import pi, sin, cos, atan
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
import os
from panda3d.core import loadPrcFileData, LineSegs, NodePath, MeshDrawer, PointLight
import numpy as np

class Satellite(object):
	def __init__(self, radius, orbitalPosition):
		self.startPosition = orbitalPosition
		self.orbitPosition = orbitalPosition

	def setOrbitPosition(self, newPos):
		self.orbitPosition = newPos

class Orbit(object):
	def __init__(self, numSats, radius, polarAngle, tiltAngle = 90, orbitOffset = 0):
		self.polarAngle = polarAngle
		self.tiltAngle = tiltAngle
		self.radius = radius
		self.numSats = numSats
		self.render = render

		self.sats = []
		spacing =  np.deg2rad(360/numSats)
		for i in range(numSats):
			self.sats.append(Satellite(radius, spacing*i+orbitOffset))

	def getPolarAngle(self):
		return self.polarAngle

	def getSats(self):
		return self.sats

class Constellation():

	def __init__(self, numOrbits, satsPerOrbit, radius, tiltAngle=90):
		self.satsPerOrbit = satsPerOrbit

		#Define and fill the orbit array
		self.orbits = []
		spacing = float(360/numOrbits)
		for i in range(numOrbits):
			polarAngle = i*spacing
			orbitOffset = (np.deg2rad(360/satsPerOrbit)/numOrbits)*i
			self.orbits.append(Orbit(satsPerOrbit, radius, polarAngle, tiltAngle, orbitOffset))

	#def tickTime(self):
	#	pass

	def getSat(self, orbitNumber, satNumber):
		return self.orbits[orbitNumber].sats[satNumber]

class Panda_Frame(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		#Set background color of scene (dark purple)
		base.setBackgroundColor(0.1,0,0.2,1.0)

		#Define the globe model
		self.globe = self.loader.loadModel('models/Icosahedron.egg')

		# Reparent the model to render.
		self.globe.reparentTo(self.render)

		#Set color, scale, and position of globe
		self.globe.setScale(1,1,1)
		self.globe.setPos(0,0,0)
		self.globe.setColor(0.05,0.5,0.2,1.0)

		#Define the satellite constellation w/ properties
		numOrbits = 35
		satsPerOrbit = 50
		radius = 4
		tiltAngle = 45
		self.constellation = Constellation(numOrbits, satsPerOrbit, radius, tiltAngle)
		for orb in self.constellation.orbits:
			polarAngle = np.deg2rad(orb.polarAngle)
			tiltAngle = np.deg2rad(orb.tiltAngle)
			radius = orb.radius

			#DRAW THE SAT ORBIT PATHS
			ls = LineSegs()
			#set color of each sat path
			ls.setColor((0.3,0.3,0.3,1))
			#define number of vertices for circle drawings
			numSteps = 100
			angleStep = np.deg2rad(360/numSteps)
			for i in range(numSteps+1):
				(x,y,z) = self.getSpatialPosition(radius, polarAngle, tiltAngle, angleStep*i)
				ls.drawTo(x, y, z)
			satNode = NodePath(ls.create())
			satNode.reparentTo(self.render)

		#define and populate the graphics nodes that represent each satellite
		self.satNodes = []
		for (i, orb) in enumerate(self.constellation.orbits):
			self.satNodes.append([])
			for sat in orb.sats:
				satNode = self.loader.loadModel('models/Icosahedron.egg')
				satNode.reparentTo(self.render)
				satNode.setScale(0.005,0.005,0.005)
				satNode.setColor(1.0,1.0,1.0,1.0)
				self.satNodes[i].append(satNode)

		# Add the spinCameraTask procedure to the task manager.
		self.taskMgr.add(self.spinCameraTask, "SpinCameraTask")
		# Add the satTask procedure to the task manager. This is where the satellite positions are updated.
		self.taskMgr.add(self.updateSats, "satTask")

	# Define a procedure to move the camera.
	def spinCameraTask(self, task):
		cameraRadius = 20
		angleDegrees = task.time * 5
		angleRadians = angleDegrees * (pi / 180.0)
		self.camera.setPos(cameraRadius * sin(angleRadians), -cameraRadius * cos(angleRadians), 0)
		self.camera.setHpr(angleDegrees, 0, 0)
		return Task.cont

	def getSpatialPosition(self, radius, polarAngle, tiltAngle, orbitPos):
		xtemp = sin(orbitPos)*cos(tiltAngle)*radius
		ytemp = cos(orbitPos)*radius
		z = sin(orbitPos)*radius*sin(tiltAngle)
		x = xtemp*cos(polarAngle) - ytemp*sin(polarAngle)
		y = ytemp*cos(polarAngle) + xtemp*sin(polarAngle)
		return (x,y,z)

	def updateSats(self, task):
		angleDegrees = task.time * 0.1
		#DRAW EACH SATELLITE
		for (i, orb) in enumerate(self.constellation.orbits):
			for (j, sat) in enumerate(orb.sats):
				polarAngle = np.deg2rad(orb.polarAngle)
				tiltAngle = np.deg2rad(orb.tiltAngle)
				radius = orb.radius
				(x,y,z) = self.getSpatialPosition(radius, polarAngle, tiltAngle, sat.orbitPosition)
				self.satNodes[i][j].setPos(x,y,z)
				sat.setOrbitPosition(sat.startPosition+angleDegrees)
		return Task.cont

#define the window size and start the program
loadPrcFileData('', 'win-size 750 750')
app = Panda_Frame()
app.run()


#NOTES

#COULD BE USEFUL: https://telecomunicationsystems.wordpress.com/low-earth-orbit-leo/
