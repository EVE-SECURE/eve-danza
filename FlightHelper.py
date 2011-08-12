try:
	import service
	import uix
	import uiutil
	import mathUtil
	import blue
	import appUtils
	import uthread
	import xtriui
	import form
	import triui
	import trinity
	import util
	import draw
	import sys
	import types
	import uicls
	import uiconst
	import time
	import stackless
	import functools
	import listentry
	import base
	import math
	import geo2
	import vivoxConstants
	import re
	import chat
	import moniker
	import svc
	import destiny
	import menu
	from itertools import izip, imap
	from math import pi, cos, sin, sqrt
	from foo import Vector3
	from mapcommon import SYSTEMMAP_SCALE
	from traceback import format_exception
	import state
	import random
	import spaceObject
	import blue
	import timecurves
	import copy

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

	@safetycheck
	def MyMove(direction):
		try:
		 	#bp = sm.GetService('michelle').GetBallpark()
			#rbp = sm.GetService('michelle').GetRemotePark()
			#if bp is None or rbp is None:
			#	return
			#ownBall = bp.GetBall(eve.session.shipid)
			if direction == const.MOVDIR_FORWARD:
	   			msg('up')
				d = trinity.TriVector(0.0, -1.0, 1.0)
			elif direction == const.MOVDIR_BACKWARD:
				msg('down')
				d = trinity.TriVector(0.0, 1.0, 1.0)
			elif direction == const.MOVDIR_LEFT:
				msg('left')
				d = trinity.TriVector(-1.0, 0.0, 1.0)
			elif direction == const.MOVDIR_RIGHT:
				msg('right')
				d = trinity.TriVector(1.0, 0.0, 1.0)
			#currentDirection = ownBall.GetQuaternionAt(blue.os.GetTime())
			#direction.TransformQuaternion(currentDirection)
			#rbp.GotoDirection(direction.x, direction.y, direction.z)
		except:
			msg('MyMove error')

	class MyService(service.Service):
		__guid__ = 'svc.SteerService'
		__servicename__ = 'SteerService'
		__displayname__ = 'Steer Service'

		def __init__(self):
			service.Service.__init__(self)
			sm.GetService('gameui').Say('Steer Service started')
			self.busy = False
  			self.alive = base.AutoTimer(100, self.Update)
			self.direction = {'LEFT': 0, 'RIGHT': 0, 'UP': 0, 'DOWN': 0 }

		def initPane(self):
			pass


		def Update(self):
			for key in self.direction.keys():
				self.direction[key] = 0
			ret = ''
			if uicore.uilib.Key(uiconst.VK_A):
				self.direction['LEFT'] = 1
				ret += 'A'
			if uicore.uilib.Key(uiconst.VK_S):
				self.direction['DOWN'] = 1
				ret += 'S'
			if uicore.uilib.Key(uiconst.VK_D):
				self.direction['RIGHT'] = 1
				ret += 'D'
			if uicore.uilib.Key(uiconst.VK_W):
				self.direction['UP'] = 1
				ret += 'W'
 			# skip if nothing is pressed or if we're busy
			if (not ret == "") and (not self.busy):
				msg(ret)
				self.UpdateDirection()

		def UpdateDirection(self):
			self.busy = True
 			bp = sm.GetService('michelle').GetBallpark()
			rbp = sm.GetService('michelle').GetRemotePark()
			if bp is None or rbp is None:
				return
			ownBall = bp.GetBall(eve.session.shipid)
			x, y = 0.0, 0.0
			if self.direction['UP']:
				y += 0.33
			elif self.direction['DOWN']:
				y += -0.33
			elif self.direction['LEFT']:
				x += 0.33
			elif self.direction['RIGHT']:
				x += -0.33
			d = trinity.TriVector(x, y, 1.0)
			if ownBall and rbp is not None:
				if not sm.GetService('autoPilot').GetState():
					# changing direction according to the button we have pressed down
					currentDirection = ownBall.GetQuaternionAt(blue.os.GetTime())
					d.TransformQuaternion(currentDirection)
					rbp.GotoDirection(d.x, d.y, d.z)
			if rbp is not None:
				rbp.SetSpeedFraction(ownBall.speedFraction)
			self.busy = False


		def Open(self):
			if self.pane:
				return
			self.initPane()

		def Close(self):
			self.Reset()

		def Reset(self):
			pass

		def CleanUp(self):
			del self.alive
			self.alive = None
			self.Reset()


	@safetycheck
	def CreateIt(*args):
		#create an instance of something
		bottomline = sm.GetService('neocom').bottomline
		if bottomline and hasattr(bottomline, "alive") and bottomline.alive:
			msg('LocalWatch Service already running!')
		else:
			sm.GetService('neocom').bottomline = MyService()

	@safetycheck
	def DestroyIt(*args):
		#destroy an instance of something
		if sm.GetService('neocom').bottomline == None:
			msg('LocalWatch Service not running!')
			return
		if hasattr(sm.GetService('neocom').bottomline, 'alive'):
			sm.GetService('neocom').bottomline.CleanUp()
		del sm.GetService('neocom').bottomline
		sm.GetService('neocom').bottomline = None
		msg('LocalWatch Service killed!')

	@safetycheck
	def ToggleIt(*args):
		bottomline = sm.GetService('neocom').bottomline
		if bottomline and hasattr(bottomline, 'alive') and bottomline.alive:
			if bottomline.pane:
				bottomline.Close()
			else:
				bottomline.Open()

	try:
		"""
		#DisableLog()
		#sm.GetService('cmd').OpenUIDebugger()

		#old_UpdateMovement = sm.GetService('cmd')._UpdateMovement
		#sm.GetService('mouseInput').OnDoubleClick = MyOnDoubleClick
		"""
		neocomwnd = sm.GetService('neocom').main
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

		btn = uix.GetBigButton(32, neocomwnd, top=866)
		btn.OnClick = ToggleIt
		btn.hint = "Show LocalDash"
		btn.sr.icon.LoadIcon('10_03')
		killBtn = btn


	except:
		msg('bad inject')

except:
	pass
