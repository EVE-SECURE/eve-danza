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
	STATE_WARPING = 5
	STATE_IDLEBELT = 6
	STATE_ERROR = 7
	STATE_MINING = 8
	STATE_DOCKINGSTATION = 9
	LOCATION_BELT = 10
	LOCATION_STATIONDOCKED = 11
	LOCATION_STATIONUNDOCKED = 12
	LOCATION_SPACE = 13
	STR = [ "Idle in space",
			"Unloading in station",
			"Idle in station",
			"Ready in station",
			"Undocked from station",
			"Warping",
			"Idle in belt",
			"ERROR!",
			"Mining asteroid",
			"Docking to station",
			"Asteroid belt",
			"Station (docked)",
			"Station (undocked)",
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
			if location:
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
			self.balls = []
			self.station = None
			self.UpdateLocationLock = 0
			self.UpdateStateLock = 0
			self.MineLock = 0
			self.UndockLock = 0
			self.DoLock = 0
			self.pane = None
			self.belts = []
			self.modulesTargets = []
			self.updateSkip = 0
			self.state = None
			self.location = None
			self.UpdateState()
			self.UpdateLocation()
			self.InitPane()

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
			# we need to update location first to know where we are
			if not self.UpdateLocationLock:
 				uthread.new(self.UpdateLocation)
			# the state depends on the location
			if not self.UpdateStateLock:
				uthread.new(self.UpdateState)
			# updating the display of location and state
			self.UpdatePane()
			# the main update logic goes here
			# if we are idle at a belt, attempt to mine
			# the Mine() function should handle everything
			if not self.DoLock:
				self.DoSomething()

		@safetycheck
		def DoSomething(self):
			self.DoLock = 1
			if (self.state == STATE_IDLEBELT or self.state == STATE_MINING) and (not self.MineLock):
				uthread.new(self.Mine)
				if self.state == STATE_MINING:
					self.updateSkip += 2
  			elif (self.state == STATE_DOCKINGSTATION):
				uthread.new(self.DockUp)
				self.updateSkip += 1
			elif (self.state == STATE_UNLOADSTATION):
				uthread.new(self.Unload)
				self.updateSkip += 1
			elif (self.state == STATE_READYSTATION) and (not self.UndockLock):
				uthread.new(self.Undock)
				self.updateSkip += 10
			elif (self.state == STATE_UNDOCKED):
				uthread.new(self.WarpToBelt)
				self.updateSkip += 1
			elif (self.state == STATE_WARPING) and (self.location == LOCATION_BELT):
				pass
			elif (self.state == STATE_IDLESPACE):
				if self.location == LOCATION_BELT:
					self.state == STATE_MINING
				else:
					uthread.new(self.WarpToBelt)
			self.DoLock = 0


		@safetycheck
		def UpdateState(self):
			self.UpdateStateLock = 1
			# determine state from location and environment
			if self.location == LOCATION_STATIONDOCKED:
			# if we are docked, we are either unloading or idle
				cargownd = self.GetCargo()
				if cargownd == None:
					self.state = STATE_ERROR
					self.UpdateStateLock = 0
					return
				cargoloot = cargownd.sr.scroll.GetNodes()
 				# if our cargo is not yet emptied, we are in unloading
				if len(cargoloot) > 0:
					self.state = STATE_UNLOADSTATION
				# if our cargo is empty, and lasers are loaded, we're ready
				# ADD LASER CHECK LATER!
				else:
					self.state = STATE_READYSTATION
				# if we're in generic idle, we need to figure out which specific state we need to be in
				# ADD LATER!
			elif self.IsInWarp():
				self.state = STATE_WARPING
			elif self.location == LOCATION_STATIONUNDOCKED:
				cargownd = self.GetCargo()
				if cargownd == None:
					self.state == STATE_ERROR
					self.UpdateStateLock = 0
					return
				cap = cargownd.GetCapacity()
				(total, full,) = (cap.capacity, cap.used)
				if total:
					proportion = min(1.0, max(0.0, full / float(total)))
				else:
					proportion = 1.0
				# we're being lenient on the definition of "full" here
				if proportion > 0.8:
					self.state = STATE_DOCKINGSTATION
				else:
					self.state = STATE_UNDOCKED
			elif self.location == LOCATION_BELT:
				# if our cargo is full and we're at a belt, we must be docking up
				cargownd = self.GetCargo()
				if cargownd == None:
					self.state == STATE_ERROR
					self.UpdateStateLock = 0
					return
				cap = cargownd.GetCapacity()
				(total, full,) = (cap.capacity, cap.used)
				if total:
					proportion = min(1.0, max(0.0, full / float(total)))
				else:
					proportion = 1.0
				# we're being lenient on the definition of "full" here
				if proportion > 0.8:
					self.state = STATE_DOCKINGSTATION
				# if we're sitting at a belt, we can be idle or we can be mining
				elif self.ModulesActive():
					# we're mining, at least with one of the lasers
					self.state = STATE_MINING
				else:
					# we are in generic idle mode at a belt
					self.state = STATE_IDLEBELT
			else:
				self.state = STATE_IDLESPACE
			self.UpdateStateLock = 0

		@safetycheck
		def UpdateLocation(self):
			self.UpdateLocationLock = 1
			# we can be at 3 possible places: belt, space, and station
			# locate the closest ball in ballpark, determine what it is
			if session.stationid:
				self.location = LOCATION_STATIONDOCKED
			elif session.shipid:
				if len(self.balls) == 0:
			 		self.UpdateBalls()
					if len(self.balls) == 0:
						# something terribly wrong is happening
						self.UpdateLocationLock = 0
						return
		   		ballPark = sm.GetService('michelle').GetBallpark()
				if not ballPark:
					self.UpdateLocationLock = 0
					return
				myBall = ballPark.GetBall(eve.session.shipid)
				if not myBall:
					self.UpdateLocationLock = 0
					return
				mindist = 2147483647
				location = None
				for (ball, slimItem) in self.balls:
					dist = trinity.TriVector(ball.x - myBall.x, ball.y - myBall.y, ball.z - myBall.z).Length()
					if dist < mindist:
						mindist = dist
						location = slimItem
				if location:
					#check if we're warping, if so, we are technically in generic space
					if self.IsInWarp():
						self.location = LOCATION_SPACE
					# check if we're at an asteroid belt
					elif location.groupID == const.groupAsteroidBelt:
						self.location = LOCATION_BELT
					# if it isn't an asteroid belt, then we're in generic space
					elif location.groupID == const.groupStation:
						self.location = LOCATION_STATIONUNDOCKED
					else:
						self.location = LOCATION_SPACE

			self.UpdateLocationLock = 0

		@safetycheck
		def UpdateBalls(self):
			validNearBy = [const.groupAsteroidBelt,
					 const.groupMoon,
					 const.groupPlanet,
					 const.groupWarpGate,
					 const.groupStargate,
					 const.groupStation]
	   		ballPark = sm.GetService('michelle').GetBallpark()
			if not ballPark:
				return
			myBall = ballPark.GetBall(eve.session.shipid)
			if not myBall:
				return
			for (ballID, ball,) in ballPark.balls.iteritems():
				slimItem = ballPark.GetInvItem(ballID)
				if slimItem and slimItem.groupID in validNearBy:
					if (self.station == None) and (slimItem.groupID == const.groupStation):
						self.station = ballID
					self.balls.append((ball, slimItem))

		@safetycheck
		def Mine(self):
			self.MineLock = 1
			# we need to check if we have at least 3 targets in range
			overview = sm.GetService('window').GetWindow('OverView')
			scrollnodes = overview.sr.scroll.GetNodes()
			if scrollnodes is not None:
				if len(scrollnodes) < 10:
				# we need to warp to a better belt
					self.WarpToBelt()
					self.MineLock = 0
					return
				else:
					# we need to know if we're faraway and need to warp
					bp = sm.GetService('michelle').GetBallpark()
					myBall = bp.GetBall(session.shipid)
					nearNode = None
					for node in scrollnodes:
						nearNode = node
						break
					nearBall = bp.GetBall(nearNode.slimItem().itemID)
					dist = trinity.TriVector(nearBall.x - myBall.x, nearBall.y - myBall.y, nearBall.z - myBall.z).Length()
					if dist >= const.minWarpDistance:
						# we need to warp to the asteroid first
						try:
							sm.GetService('menu').WarpToItem(nearNode.slimItem().itemID, 0)
							Sleep(1000)
						except:
							msg('warp error')
						self.MineLock = 0
						return
					elif (dist <= const.minWarpDistance) and (dist > 15000):
						self.WarpToBelt()
						self.MineLock = 0
						return
					else:
						# we can mine now
						# first check to see if we have 3 targets
						targetsvc = sm.GetService('target')
						targets = targetsvc.GetTargets()
						if len(targets) < 3:
							# we need to acquire new targets until we have 3
							i = 0
							for node in scrollnodes:
									try:
										targetsvc.TryLockTarget(node.slimItem().itemID)
									except:
										pass
 									i += 1
									if i >= 3:
										break
						Sleep(random.randrange(2000,3000))
						# now we need to worry about activating all modules
						modulelist = []
	  					for i in xrange(0, 8):
							slot = uicore.layer.shipui.sr.slotsByOrder.get((0, i), None)
							if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
								if not slot.sr.module.def_effect.isActive:
							 		#we need to activate the module
									modulelist.append(slot.sr.module)
						for each in modulelist:
							try:
								each.Click()
								Sleep(random.randrange(1000, 1500))
								targetsvc.SelectNextTarget()
							except:
								pass
						self.MineLock = 0

		@safetycheck
		def WarpToBelt(self):
			# courtesy delay
			Sleep(1000)
			absvc = sm.GetService('addressbook')
			bookmarks = absvc.GetBookmarks()
			bms = list()
			for each in bookmarks.itervalues():
				if each.locationID == session.solarsystemid:
					bms.append(each)
			randomidx = random.randrange(0, 6)
			try:
				sm.GetService('menu').WarpToBookmark(bms[randomidx], 0.0, False)
			except:
				msg('error warping to belt')

		@safetycheck
		def DockUp(self):
			try:
				sm.GetService('menu').Dock(self.station)
			except:
				msg('error in dockup')
				self.updateSkip += 5

		@safetycheck
		def Undock(self):
			self.UndockLock = 1
			try:
				Sleep(random.randrange(30000, 35000))
  				uicore.cmd.CmdExitStation()
				Sleep(random.randrange(15000, 20000))
			except:
				msg('error in undock')
			self.UndockLock = 0

		@safetycheck
		def Unload(self):
			try:
				cargo = self.GetCargo()
				hangar = self.GetHangar()
				if cargo and hangar:
					hangar.OnDropDataWithIdx(cargo.sr.scroll.GetNodes())
			except:
				pass

		@safetycheck
		def ModulesActive(self):
			# iterate through the top x module slots and check if default effect is active
			# if any one of them is active, return True, else return False
			for i in xrange(0, 8):
				slot = uicore.layer.shipui.sr.slotsByOrder.get((0, i), None)
				if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
					if slot.sr.module.def_effect.isActive:
						return True
			return False

		@safetycheck
		def GetCargo(self):
			windows = sm.GetService('window').GetWindows()
			cargo = None
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
			return hangar

		def Open(self):
			if self.pane == None:
				self.InitPane()

		def Close(self):
			if self.pane:
				self.pane.Close()
				del self.pane
				self.pane = None

		def IsInWarp(self):
			if session.shipid:
				if hasattr(uicore.layer, 'shipui') and hasattr(uicore.layer.shipui, 'ball'):
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