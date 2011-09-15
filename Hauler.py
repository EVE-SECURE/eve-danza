try:
	import destiny
	import service
	import uix
	import uiutil
	import mathUtil
	import blue
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
	import cStringIO
	import collections
	import os
	import inspect
	import util.Moniker


	RENS_STATION = 60004588
	RENS = 30002510
	HOME = 30002564
	HOME_STATION = 60004675
	HSTATE_IDLESPACE = 1
	HSTATE_IDLESTATION = 2
	HSTATE_AUTOPILOT = 3
	HSTATE_READYTOUNDOCK = 4
	HSTR = [ "Error",
			"Idling in space",
			"Idling in station",
			"Autopilot",
			"Ready to undock"
			]

	def safetycheck(func):
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except:
				try:
					print "exception in " + func.__name__
					(exc, e, tb,) = sys.exc_info()
					result2 = (''.join(format_exception(exc, e, tb)) + '\n').replace('\n', '<br>')
					sm.GetService('gameui').MessageBox(result2, "Hauler Exception")
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
	def Sleep(duration = 5000):
		try:
			blue.pyos.synchro.Sleep(duration)
		except:
			msg('we are in the main thread!')

	@safetycheck
	def CreateIt(*args):
		#create an instance of something
		hauler = sm.GetService('jukebox').playlist
		if hauler and hasattr(hauler, "alive") and hauler.alive:
			msg('Hauler Service already running!')
		else:
			sm.GetService('jukebox').playlist = HaulerService()

	@safetycheck
	def DestroyIt(*args):
		#destroy an instance of something
		if sm.GetService('jukebox').playlist == None:
			msg('Hauler Service not running!')
			return
		if hasattr(sm.GetService('jukebox').playlist, 'alive'):
			sm.GetService('jukebox').playlist.CleanUp()
		del sm.GetService('jukebox').playlist
		sm.GetService('jukebox').playlist = None
		msg('Hauler Service killed!')

	@safetycheck
	def FormatTimeAgo(theTime):
		if (theTime == None):
			theTime = blue.os.GetTime()
		delta = blue.os.GetTime() - theTime
		(hours, minutes, seconds,) = util.HoursMinsSecsFromSecs(util.SecsFromBlueTimeDelta(delta))
		days = 0
		if hours > 48:
			days = int(hours / 24)
			hours %= 24
		t = util.FormatTimeDelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
		if t is None:
			howLongAgo = mls.UI_GENERIC_RIGHTNOW
		else:
			howLongAgo = mls.UI_GENERIC_AGO_WITH_FORMAT % {'time': t}
		return howLongAgo

	class HaulerService():
		__guid__ = 'svc.HaulerService'
		__servicename__ = 'HaulerService'
		__displayname__ = 'Hauler Service'

		def __init__(self):
			sm.GetService('gameui').Say('Hauler Service started')
			self.StartUp()
  			self.alive = base.AutoTimer(1999, self.Update)

		@safetycheck
		def StartUp(self):
			self.state = None
			self.pane = None
			self.runCount = 0
			self.DoLock = 0

			self.InitPane()

		@safetycheck
		def InitPane(self):
			self.pane = Dash(parent=uicore.layer.abovemain, name='Dash')
			self.UpdatePane()

		@safetycheck
		def UpdatePane(self):
			if self.pane == None:
				return
			statename = "Unknown"
			if self.state:
				statename = HSTR[self.state]
			self.pane.ShowMsg(statename, self.runCount)

		@safetycheck
		def Update(self):
			self.UpdateState()
			self.UpdatePane()
			if not self.DoLock:
				self.DoSomething()

		@safetycheck
		def UpdateState(self):
			if sm.GetService('autoPilot').autopilot:
				self.state = HSTATE_AUTOPILOT
			else:
				if session.stationid:
					if self.state == HSTATE_READYTOUNDOCK:
						return
					else:
						self.state = HSTATE_IDLESTATION
				else:
					self.state = HSTATE_IDLESPACE

		@safetycheck
		def DoSomething(self):
			self.DoLock = 1
			try:
				if self.state == HSTATE_AUTOPILOT:
					# we should do nothing if we're in autopilot
					pass
				elif self.state == HSTATE_IDLESTATION:
					# we are idling in a station, find out which one it is, and do accordingly
					if session.stationid == HOME_STATION:
						# we should load up on goods and set ready to undock
						if self.IsCargoFull():
							self.state = HSTATE_READYTOUNDOCK
						else:
							self.LoadSomething()
							Sleep(1000)
					elif session.stationid == RENS_STATION:
						if self.IsCargoEmpty():
							self.state = HSTATE_READYTOUNDOCK
						else:
							Sleep(1000)
							self.Unload()
							Sleep(1000)
				elif self.state == HSTATE_IDLESPACE:
					if not self.IsInWarp():
						self.DockUp()
				elif self.state == HSTATE_READYTOUNDOCK:
					self.UndockAndSetAutopilot()
			except:
				msg('error in DoSomething')

			self.DoLock = 0

		@safetycheck
		def UndockAndSetAutopilot(self):
			try:
				Sleep(random.randrange(25000, 30000))
  				uicore.cmd.CmdExitStation()
				Sleep(random.randrange(15000, 18000))
				if session.solarsystemid == HOME:
  					sm.StartService('starmap').SetWaypoint(RENS)
					sm.GetService('autoPilot').SetOn()
				elif session.solarsystemid == RENS:
					sm.StartService('starmap').SetWaypoint(HOME)
					sm.GetService('autoPilot').SetOn()
			except:
				msg('error undocking')

		@safetycheck
		def DockUp(self):
			if session.solarsystemid == RENS:
				station = RENS_STATION
			elif session.solarsystemid == HOME:
				station = HOME_STATION
			else:
				msg('we cannot dock up, we are lost!')
			try:
				sm.GetService('menu').Dock(station)
			except:
				msg('cannot dock yet')

		@safetycheck
		def Unload(self):
			try:
				cargo = self.GetCargo()
				hangar = self.GetHangar()
				if cargo and hangar:
					cap = cargo.GetCapacity()
 					load = cap.used
					if load > 0:
 						self.runCount += 1
						hangar.OnDropDataWithIdx(cargo.sr.scroll.GetNodes())
			except:
				msg('cannot unload')

		@safetycheck
		def LoadSomething(self):
			try:
				cargo = self.GetCargo()
				hangar = self.GetHangar()
				self.ConfirmSetQuantity()
				minerals = []
				for node in hangar.sr.scroll.GetNodes():
					groupID = cfg.invtypes.Get(node.rec.typeID).groupID
					if groupID == const.groupVeldspar or groupID == const.groupScordite:
						minerals.append(node)
				uthread.new(cargo.OnDropDataWithIdx, [minerals.pop()])
				Sleep(1000)
				self.ConfirmSetQuantity()
			except:
				msg('cannot load more')

		@safetycheck
		def IsCargoFull(self):
			try:
				cargownd = self.GetCargo()
				if cargownd == None:
					return 0
				cap = cargownd.GetCapacity()
				(total, full,) = (cap.capacity, cap.used)
			   	if total:
					proportion = min(1.0, max(0.0, full / float(total)))
				else:
					proportion = 1.0
				if proportion > 0.95:
					return 1
				else:
					return 0
			except:
				msg('check cargo error')

		@safetycheck
		def IsCargoEmpty(self):
			try:
				cargownd = self.GetCargo()
				if cargownd == None:
					return 0
				cap = cargownd.GetCapacity()
				(total, full,) = (cap.capacity, cap.used)
			   	if total:
					proportion = min(1.0, max(0.0, full / float(total)))
				else:
					proportion = 1.0
				if proportion == 0:
					return 1
				else:
					return 0
			except:
				msg('check cargo error')


		@safetycheck
		def GetCargo(self):
			windows = sm.GetService('window').GetWindows()
			cargo = None
			for each in windows:
				if each.__guid__ in ('form.DockedCargoView', 'form.InflightCargoView'):
					cargo = each
			if cargo == None:
				sm.GetService('cmd').OpenCargoHoldOfActiveShip()
 				Sleep(1000)
			for each in windows:
				if each.__guid__ in ('form.DockedCargoView', 'form.InflightCargoView'):
					cargo = each
			return cargo

		@safetycheck
		def GetHangar(self):
			windows = sm.GetService('window').GetWindows()
			hangar = None
			for each in windows:
				if each.__guid__ == 'form.ItemHangar':
					hangar = each
			if hangar == None:
				sm.GetService('cmd').OpenHangarFloor()
 				Sleep(1000)
			for each in windows:
				if each.__guid__ == 'form.ItemHangar':
					hangar = each
			return hangar

		@safetycheck
		def ConfirmSetQuantity(self):
			try:
				windows = sm.GetService('window').GetWindows()
				confirm = None
				for each in windows:
					if each.name == 'Set Quantity':
						confirm = each
				if confirm:
					confirm.Confirm()
			except:
				msg('error in locating set quantity window')

		@safetycheck
		def IsInWarp(self):
			try:
				if session.shipid:
					if hasattr(uicore.layer, 'shipui') and hasattr(uicore.layer.shipui, 'ball'):
						return (uicore.layer.shipui.ball.mode == destiny.DSTBALL_WARP)
				else:
					return False
			except:
				msg('error in IsInWarp')
			return False

		@safetycheck
		def CleanUp(self):
			del self.alive
			self.alive = None
			self.pane.Close()
			self.pane = None

        class Dash(uicls.Container):
			__guid__ = 'uicls.Dash'

			def ApplyAttributes(self, attributes):
				self.scope = 'station_inflight'
				self.message = None
				self.message2 = None
				uicls.Container.ApplyAttributes(self, attributes)

			def Prepare_Text_(self):
				self.message = uicls.Label(text='', parent=self, left=0, top=4, autowidth=False, width=300, fontsize=12, state=uiconst.UI_DISABLED)
				self.message2 = uicls.Label(text='', parent=self, left=0, top=16, autowidth=False, width=300, fontsize=12, state=uiconst.UI_DISABLED)


			def Prepare_Underlay_(self):
				border = uicls.Frame(parent=self, frameConst=uiconst.FRAME_BORDER1_CORNER1, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.5))
				frame = uicls.Frame(parent=self, color=(0.0, 0.0, 0.0, 0.75), frameConst=uiconst.FRAME_FILLED_CORNER1, state=uiconst.UI_DISABLED)

			def ShowMsg(self, state, runCount):
				if self.message is None:
					self.Prepare_Text_()
					self.Prepare_Underlay_()
				self.message.text = '<center> State: <color=0xffffff00>%s' % state
				self.message2.text = '<center> Runs completed: <color=0xff38ff38>%d' % runCount
				self.SetAlign(uiconst.CENTERTOP)
				self.SetSize(300, 32)
				offset = sm.GetService('window').GetCameraLeftOffset(self.width, align=uiconst.CENTERTOP, left=0)
				self.SetPosition(offset, 5)
				self.state = uiconst.UI_DISABLED
				uiutil.SetOrder(self, 0)

	try:
		util.Moniker.WarpToStuffAutopilot = lambda s, x: s.WarpToStuff("item", x, minRange=0)

		neocomwnd = sm.GetService('neocom').main
		btn = uix.GetBigButton(32, neocomwnd, top=900)
		btn.OnClick = CreateIt
		btn.hint = "Start Hauler service"
		btn.sr.icon.LoadIcon('11_14')
		createBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=933)
		btn.OnClick = DestroyIt
		btn.hint = "Kill Hauler service"
		btn.sr.icon.LoadIcon('11_15')
		destroyBtn = btn

	except:
		msg('bad inject')

except:
	pass