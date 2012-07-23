try:
	import service
	import uix
	import uiutil
	import uthread
	import xtriui
	import form
	import triui
	import util
	import sys
	import types
	import uicls
	import uiconst
	import functools
	import math
	import re
	import svc
	import destiny
	import menu
	from itertools import izip, imap
	from math import pi, cos, sin, sqrt
	from mapcommon import SYSTEMMAP_SCALE
	from traceback import format_exception
	import random
	import base
	import trinity
	import blue

	def safetycheck(func):
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except:
				try:
					print "exception in " + func.__name__
					(exc, e, tb,) = sys.exc_info()
					result2 = (''.join(format_exception(exc, e, tb)) + '\n').replace('\n', '<br>')
					sm.GetService('gameui').MessageBox(result2, "ProbeHelper Exception")
				except:
					pass
		return wrapper

	@safetycheck
	def msg(m = 'bad input'):
		try:
			sm.GetService('gameui').Say(m)
		except:
			pass


	@safetycheck
	def randomPause(fromtime = 0, totime = 1000):
		return random.randrange(fromtime, totime)

	class SteerService():
		__guid__ = 'svc.SteerService'
		__servicename__ = 'SteerService'
		__displayname__ = 'Steer Service'

		def __init__(self):
			#service.Service.__init__(self)
			sm.GetService('gameui').Say('Steer Service started')
			self.busy = 0
			self.accelconst = 0.25
			self.acceleration = { 'LEFT': 1, 'RIGHT': 1, 'UP': 1, 'DOWN': 1 }
  			self.alive = base.AutoTimer(99, self.Update)
			self.keyDown = {'LEFT': 0, 'RIGHT': 0, 'UP': 0, 'DOWN': 0 }

		def initPane(self):
			pass

		def Update(self):
			for key in self.keyDown.keys():
				self.keyDown[key] = 0
			ret = ''
			if uicore.uilib.Key(uiconst.VK_A):
				self.keyDown['LEFT'] = 1
				ret += 'A'
			if uicore.uilib.Key(uiconst.VK_S):
				self.keyDown['DOWN'] = 1
				ret += 'S'
			if uicore.uilib.Key(uiconst.VK_D):
				self.keyDown['RIGHT'] = 1
				ret += 'D'
			if uicore.uilib.Key(uiconst.VK_W):
				self.keyDown['UP'] = 1
				ret += 'W'
 			# skip if nothing is pressed or if we're busy
			if (not ret == "") and (not self.busy):
				#msg(ret)
				self.UpdateAcceleration()
				self.UpdateDirection()

		@safetycheck
		def UpdateAcceleration(self):
			self.busy = 1
			for key in self.keyDown.keys():
				if self.keyDown[key]:
					#increase acceleration per updated keyDown
					self.acceleration[key] += 1
				else:
					# lifting the key resets the acceleration
					self.acceleration[key] = 1
			self.busy = 0

		@safetycheck
		def UpdateDirection(self):
			self.busy = 1
 			bp = sm.GetService('michelle').GetBallpark()
			rbp = sm.GetService('michelle').GetRemotePark()
			if bp is None or rbp is None:
				self.busy = 0
				return
			ownBall = bp.GetBall(eve.session.shipid)
			x, y = 0.0, 0.0
			if self.keyDown['UP']:
				y += self.accelconst * self.acceleration['UP']
			elif self.keyDown['DOWN']:
				y -= self.accelconst * self.acceleration['DOWN']
			elif self.keyDown['LEFT']:
				x += self.accelconst * self.acceleration['LEFT']
			elif self.keyDown['RIGHT']:
				x -= self.accelconst * self.acceleration['RIGHT']
			d = trinity.TriVector(x, y, 1.0)
			if ownBall and rbp is not None:
				if not sm.GetService('autoPilot').GetState():
					currentDirection = ownBall.GetQuaternionAt(blue.os.GetTime())
					d.TransformQuaternion(currentDirection)
					rbp.GotoDirection(d.x, d.y, d.z)
			if rbp is not None:
				rbp.SetSpeedFraction(ownBall.speedFraction)
			self.busy = 0

		def CleanUp(self):
			del self.alive
			self.alive = None


	@safetycheck
	def CreateIt(*args):
		bottomline = sm.GetService('neocom').neocom.autoHideActive
		if bottomline and hasattr(bottomline, "alive") and bottomline.alive:
			msg('Steer Service already running!')
		else:
			sm.GetService('neocom').neocom.autoHideActive = SteerService()

	@safetycheck
	def DestroyIt(*args):
		if sm.GetService('neocom').neocom.autoHideActive == None:
			msg('LocalWatch Service not running!')
			return
		if hasattr(sm.GetService('neocom').neocom.autoHideActive, 'alive'):
			sm.GetService('neocom').neocom.autoHideActive.CleanUp()
		del sm.GetService('neocom').neocom.autoHideActive
		sm.GetService('neocom').neocom.autoHideActive = None
		msg('Steer Service killed!')

	try:

		neocomwnd = sm.GetService('neocom').neocom
		btn = uix.GetBigButton(32, neocomwnd, top=800)
		btn.OnClick = CreateIt
		btn.hint = "Start LocalWatch service"
		btn.sr.icon.LoadIcon('10_01')
		createBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=833)
		btn.OnClick = DestroyIt
		btn.hint = "Kill LocalWatch service"
		btn.sr.icon.LoadIcon('10_02')
		destroyBtn = btn

	except:
		msg('bad inject')

except:
	pass
