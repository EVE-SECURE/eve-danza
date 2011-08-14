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

	STATE_IDLESPACE = 0
	STATE_UNLOADSTATION = 1
	STATE_IDLESTATION = 2
	STATE_READYSTATION = 3
	STATE_UNDOCKED = 4
	STATE_WARPINGTOBELT = 5
	STATE_IDLEBELT = 6
	STATE_APPROACHINGROCKS = 7
	STATE_MININGROCKS = 8
	STATE_DOCKINGSTATION = 9
	LOCATION_BELT = 10
	LOCATION_STATION = 11
	LOCATION_SPACE = 12
	STR = [ "Idle in space",
			"Unloading in station",
			"Idle in station",
			"Ready in station",
			"Undocked from station",
			"Warping to a belt",
			"Idle in belt",
			"Approaching asteroid",
			"Mining asteroid",
			"Docking to station",
			"Asteroid belt",
			"Station",
			"Space"
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
	def Sleep(duration = 5000):
		try:
			blue.pyos.synchro.Sleep(duration)
		except:
			msg('we are in the main thread!')

	@safetycheck
	def Report():
		# this is all crap
		overview = sm.GetService('window').GetWindow('OverView')
		uicore.registry.SetFocus(overview.sr.scroll)
		scrollnodes = overview.sr.scroll.GetNodes()
		if scrollnodes is None:
			msg('None!')
		msg('scroll contains %d nodes' % len(scrollnodes))

		targetsvc = sm.GetService('target')
		cmdsvc = sm.GetService('cmd')
		count = 0
		for each in scrollnodes:
			slimItem = each.slimItem()
			overview.sr.scroll.SelectNode(each)
			if count > 2:
				break
			targetsvc.TryLockTarget(slimItem.itemID)
			blue.pyos.synchro.Sleep(500)
			count += 1
		blue.pyos.synchro.Sleep(1500)
		cmdsvc.CmdActivateHighPowerSlot1()
		blue.pyos.synchro.Sleep(500)
		targetsvc.SelectPrevTarget()
		cmdsvc.CmdActivateHighPowerSlot2()

	@safetycheck
	def FindStation():
		stationID = None
		ballpark = sm.GetService('michelle').GetBallpark()
		for itemID in ballpark.balls.keys():
			if ballpark is None:
			    break
			if itemID == eve.session.shipid:
			    continue
			slimItem = ballpark.GetInvItem(itemID)
			#ball = ballpark.GetBall(itemID)
			if not slimItem:
			    continue
			if slimItem.groupID == const.groupStation:
				stationID = itemID
		return stationID


	"""
##   		slimItem = node.slimItem()
##			if slimItem:

##				typeinfo = cfg.invtypes.Get(slimItem.typeID)
##				entryname = hint = uix.GetSlimItemName(slimItem)
##				msg('%s (%s)' % (entryname, typeinfo))
	"""

	@safetycheck
	def GetCargo():
		windows = sm.GetService('window').GetWindows()
		cargo = None
		for each in windows:
			if each.__guid__ in ('form.DockedCargoView', 'form.InflightCargoView'):
				cargo = each
		return cargo
		#cargo.sr.scroll.SelectAll()

	@safetycheck
	def GetHangar():
		windows = sm.GetService('window').GetWindows()
		hangar = None
		for each in windows:
			if each.__guid__ == 'form.ItemHangar':
				hangar = each
		return hangar
		"""
		for entry in hangar.sr.scroll.GetNodes():
			name = entry.name
			qty = entry.rec.stacksize
			msg('%s (%s)' % (name, qty))
			blue.pyos.synchro.Sleep(1000)
		"""

	@safetycheck
	def DockUp():
		try:
			stationID = FindStation()
			menusvc = sm.GetService('menu')
			menusvc.Dock(stationID)
		except:
			pass

	@safetycheck
	def GetLocation():
		locationname = None
		if session.stationid:
			locationname = cfg.evelocations.Get(session.stationid2).name
		elif session.shipid:
	 		validNearBy = [const.groupAsteroidBelt,
	         const.groupMoon,
	         const.groupPlanet,
	         const.groupWarpGate,
	         const.groupStargate]
	   		ballPark = sm.GetService('michelle').GetBallpark()
			myBall = ballPark.GetBall(eve.session.shipid)
	        if not ballPark:
	            return
	        lst = []
	        for (ballID, ball,) in ballPark.balls.iteritems():
	            slimItem = ballPark.GetInvItem(ballID)
	            if slimItem and slimItem.groupID in validNearBy:
                 	if myBall:
	                    dist = trinity.TriVector(ball.x - myBall.x, ball.y - myBall.y, ball.z - myBall.z).Length()
	                    lst.append((dist, slimItem))
	                else:
	                    lst.append((ball.surfaceDist, slimItem))

			lst.sort()
			if lst:
			    location = lst[0][1]
			if slimItem:
				typeinfo = cfg.invtypes.Get(location.typeID)
				locationname = uix.GetSlimItemName(location)
				itemID = location.itemID
				typeID = location.typeID
				if not locationname:
					locationname = typeinfo.Group().name
		"""
		elif session.shipid:
			location = sm.GetService('neocom').GetNearestBall()
			if not location is None:
				locationname = location.name
		"""
		msg('nearest is: %s' % locationname)

	@safetycheck
	def WarpRandomBelt():
		if session.shipid:
			ballPark = sm.GetService('michelle').GetBallpark()
			myBall = ballPark.GetBall(eve.session.shipid)
			if not ballPark:
			    return
			belts = []
			for (ballID, ball,) in ballPark.balls.iteritems():
			    slimItem = ballPark.GetInvItem(ballID)
			    if slimItem and (slimItem.groupID == const.groupAsteroidBelt):
					belts.append(ballID)
			msg('belts found: %d' % len(belts))
		randomidx = random.randrange(1, len(belts)) - 1
		destination = belts[randomidx]
		sm.GetService('menu').WarpToItem(destination, 0)


	@safetycheck
	def CreateIt(*args):
		#create an instance of something
		bottomline = sm.GetService('neocom').bottomline
		if bottomline and hasattr(bottomline, "alive") and bottomline.alive:
			msg('Miner Service already running!')
		else:
			sm.GetService('neocom').bottomline = MinerService()

	@safetycheck
	def DestroyIt(*args):
		#destroy an instance of something
		if sm.GetService('neocom').bottomline == None:
			msg('Miner Service not running!')
			return
		if hasattr(sm.GetService('neocom').bottomline, 'alive'):
			sm.GetService('neocom').bottomline.CleanUp()
		del sm.GetService('neocom').bottomline
		sm.GetService('neocom').bottomline = None
		msg('Miner Service killed!')

	@safetycheck
	def ToggleIt(*args):
		bottomline = sm.GetService('neocom').bottomline
		if bottomline and hasattr(bottomline, 'alive') and bottomline.alive:
			if bottomline.pane:
				bottomline.Close()
			else:
				bottomline.Open()

	class MinerService(service.Service):
		__guid__ = 'svc.MinerService'
		__servicename__ = 'MinerService'
		__displayname__ = 'Miner Service'
		# some constants

		def __init__(self):
			service.Service.__init__(self)
			sm.GetService('gameui').Say('Miner Service started')
			self.StartUp()
  			self.alive = base.AutoTimer(1000, self.Update)

		def StartUp(self):
			self.pane = None
			self.belts = []
			self.modulesTargets = []
			self.updateSkip = 0
			self.state = None
			self.location = None
			self.UpdateState()
			self.UpdateLocation()

		def InitPane(self):
			self.pane = Dash(parent=uicore.layer.abovemain, name='Dash')
			self.UpdatePane()

		def UpdatePane(self):
			if self.pane == None:
				return
			locationname = "Unknown"
			statename = "Unknown"
			if not self.location is None:
				locationname = STR[self.location]
			if not self.state is None:
				statename = STR[self.state]
			self.pane.ShowMsg(locationname, statename)

		def Update(self):
			if self.updateSkip:
				self.updateSkip -= 1
				return
			self.UpdateState()
			self.UpdateLocation()
			self.UpdatePane()

		def UpdateState(self):
			self.state = STATE_IDLESTATION

		def UpdateLocation(self):
			self.location = LOCATION_STATION

		def Open(self):
			if self.pane == None:
				self.InitPane()

		def Close(self):
			if self.pane:
				self.pane.Close()
				del self.pane
				self.pane = None

		def IsInWarp(self):
			if session.shipid and hasattr(uicore.layer.shipui, 'ball'):
				return (uicore.layer.shipui.ball.mode == destiny.DSTBALL_WARP)
			else:
				return False

		def CleanUp(self):
			if self.alive:
				del self.alive
			self.alive = None
			self.belts = None
			self.modulesTargets = None
			self.updateSkip = None
			self.state = None
			self.location = None
			self.Close()

	class Dash(uicls.Container):
			__guid__ = 'uicls.Dash'

			def ApplyAttributes(self, attributes):
				self.scope = 'station_inflight'
				self.message = None
				self.message2 = None
				uicls.Container.ApplyAttributes(self, attributes)

			def Prepare_Text_(self):
				self.message = uicls.Label(text='', parent=self, left=0, top=4, autowidth=False, width=200, fontsize=12, state=uiconst.UI_DISABLED)
				self.message2 = uicls.Label(text='', parent=self, left=0, top=16, autowidth=False, width=200, fontsize=12, state=uiconst.UI_DISABLED)

			def Prepare_Underlay_(self):
			    border = uicls.Frame(parent=self, frameConst=uiconst.FRAME_BORDER1_CORNER1, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25))
			    frame = uicls.Frame(parent=self, color=(0.0, 0.0, 0.0, 0.75), frameConst=uiconst.FRAME_FILLED_CORNER1, state=uiconst.UI_DISABLED)

			def ShowMsg(self, location, state):
			    if self.message is None:
			        self.Prepare_Text_()
			        self.Prepare_Underlay_()
				self.message.text = '<center>Location: ' + location
				self.message2.text = '<center>State: ' + state
				self.SetAlign(uiconst.CENTERTOP)
				self.SetSize(200, 32)
				offset = sm.GetService('window').GetCameraLeftOffset(self.width, align=uiconst.CENTERTOP, left=0)
				self.SetPosition(offset, 5)
				self.state = uiconst.UI_DISABLED
				uiutil.SetOrder(self, 0)

	@safetycheck
	def Action(*args):
		# arbitrary action definition!
		bottomline = sm.GetService('neocom').bottomline
		if bottomline == None:
			msg('Miner Service not running!')
			return
		if hasattr(bottomline, 'alive'):
			# here comes the action!
			warping = bottomline.IsInWarp()
			if warping:
				msg('in warp')
			else:
				msg('not in warp')


	try:
		#uthread.new(Report)
		#cargo = GetCargo()
		#hangar = GetHangar()
		#if cargo and hangar:
		#	hangar.OnDropDataWithIdx(cargo.sr.scroll.GetNodes())
		#shipui = uicore.layer.shipui
		#slot1 = shipui.sr.slotsByOrder.get((0, 0), None)
		#slot2 = shipui.sr.slotsByOrder.get((0, 1), None)
		#msg('slot1 state: %s, slot2 state: %s' % (slot1.sr.module.def_effect.isActive, slot2.sr.module.def_effect.isActive))

		#uthread.new(DockUp)
		#uthread.new(WarpRandomBelt)
		#uthread.new(GetLocation)
		neocomwnd = sm.GetService('neocom').main
		btn = uix.GetBigButton(32, neocomwnd, top=800)
		btn.OnClick = CreateIt
		btn.hint = "Start Miner service"
		btn.sr.icon.LoadIcon('11_01')
		createBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=833)
		btn.OnClick = DestroyIt
		btn.hint = "Kill Miner service"
		btn.sr.icon.LoadIcon('11_02')
		destroyBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=866)
		btn.OnClick = ToggleIt
		btn.hint = "Toggle Dash"
		btn.sr.icon.LoadIcon('11_03')
		actionBtn = btn

	except:
  		msg('failed doing something')

except:
	pass