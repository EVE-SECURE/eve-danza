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

	STATE_IDLESPACE = 0
	STATE_UNLOADSTATION = 1
	STATE_IDLESTATION = 2
	STATE_READYSTATION = 3
	STATE_UNDOCKED = 4
	STATE_WARPING = 5
	STATE_IDLEBELT = 6
	STATE_HIBERNATE = 7
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
			"Hibernating...",
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
	def CreateIt(*args):
		#create an instance of something
		miner = sm.GetService('jukebox').playlists
		if miner and hasattr(miner, "alive") and miner.alive:
			msg('Miner Service already running!')
		else:
			sm.GetService('jukebox').playlists = MinerService()

	@safetycheck
	def DestroyIt(*args):
		#destroy an instance of something
		if sm.GetService('jukebox').playlists == None:
			msg('Miner Service not running!')
			return
		if hasattr(sm.GetService('jukebox').playlists, 'alive'):
			sm.GetService('jukebox').playlists.CleanUp()
		del sm.GetService('jukebox').playlists
		sm.GetService('jukebox').playlists = None
		msg('Miner Service killed!')

	@safetycheck
	def ToggleIt(*args):
		miner = sm.GetService('jukebox').playlists
		if miner and hasattr(miner, 'alive') and miner.alive:
			if miner.pane:
				miner.Close()
			else:
				miner.Open()

	@safetycheck
	def ClearIt(*args):
		miner = sm.GetService('jukebox').playlists
		if miner and hasattr(miner, 'alive') and miner.alive:
			miner.ClearStats()

	@safetycheck
	def FormatTimeAgo(theTime):
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

	@safetycheck
	def FormatTimeDelta(days = None, hours = None, minutes = None, seconds = None):
	    ret = []
	    if days:
	        ret.append('%s %s' % (days, uix.Plural(days, 'UI_GENERIC_DAY').lower()))
	    if hours:
	        ret.append('%s %s' % (hours, uix.Plural(hours, 'UI_GENERIC_HOUR').lower()))
	    if minutes:
	        ret.append('%s %s' % (minutes, uix.Plural(minutes, 'UI_GENERIC_MINUTE').lower()))
	    if seconds:
	        ret.append('%s %s' % (seconds, uix.Plural(seconds, 'UI_GENERIC_SECOND').lower()))
	    if ret:
	        return ', '.join(ret)
	    else:
	        return None

	class MinerService():
		__guid__ = 'svc.MinerService'
		__servicename__ = 'MinerService'
		__displayname__ = 'Miner Service'
		# some constants

		def __init__(self):
			#service.Service.__init__(self)
			sm.GetService('gameui').Say('Miner Service started')
			self.StartUp()
  			self.alive = base.AutoTimer(1000, self.Update)

		def StartUp(self):
			self.statsTime = 'unknown'
			self.runCount = 0
			self.avgTime = 0
			self.totalUnload = 0
			self.lastStart = None
			self.balls = []
			self.station = None
			self.UpdateLocationLock = 0
			self.UpdateStateLock = 0
			self.MineLock = 0
			self.UndockLock = 0
			self.DoLock = 0
			self.RefillLock = 0
			self.WarpLock = 0
			self.pane = None
			self.bmsToSkip = []
			self.currentBM = None
			self.modulesTargets = {}
			self.updateSkip = 0
			self.undockSafeFlag = 0
			self.state = None
			self.location = None

			self.LoadStats()
			self.UpdateLocation()
			self.UpdateState()
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
			self.pane.ShowMsg(locationname, statename, self.runCount, len(self.bmsToSkip), self.totalUnload, self.statsTime)

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
			if (self.state == STATE_HIBERNATE):
				if self.location == LOCATION_STATIONDOCKED:
					# we are doing nothing
					pass
				else:
					self.DockUp()
			elif (self.state == STATE_IDLEBELT or self.state == STATE_MINING) and (not self.MineLock):
				uthread.new(self.Mine)
				if self.state == STATE_MINING:
					self.updateSkip += 2
  			elif (self.state == STATE_DOCKINGSTATION):
				uthread.new(self.DockUp)
				self.updateSkip += 1
			elif (self.state == STATE_UNLOADSTATION):
				uthread.new(self.Unload)
				self.updateSkip += 2
			elif (self.state == STATE_IDLESTATION):
				if (not self.undockSafeFlag) and (not self.RefillLock):
					uthread.new(self.RefillCrystal)
					self.updateSkip += 6
			elif (self.state == STATE_READYSTATION) and (not self.UndockLock):
				uthread.new(self.Undock)
				self.updateSkip += 10
			elif (self.state == STATE_UNDOCKED):
				if (not self.UndockLock) and (not self.WarpLock):
					uthread.new(self.WarpToBelt)
					self.updateSkip += 2
			elif (self.state == STATE_WARPING) and (self.location == LOCATION_BELT):
				pass
			elif (self.state == STATE_IDLESPACE):
				if self.location == LOCATION_BELT:
					self.state == STATE_MINING
				elif not self.WarpLock:
					uthread.new(self.WarpToBelt)
				else:
					pass
			self.DoLock = 0


		@safetycheck
		def UpdateState(self):
			self.UpdateStateLock = 1
			if self.state == STATE_HIBERNATE:
				# we should not update state if we're hibernating
				pass
			# determine state from location and environment
			elif self.location == LOCATION_STATIONDOCKED:
			# if we are docked, we are either unloading or idle
				cargownd = self.GetCargo()
				if cargownd == None:
					self.UpdateStateLock = 0
					return
				cargoloot = cargownd.sr.scroll.GetNodes()
 				# if our cargo is not yet emptied, we are in unloading
				if len(cargoloot) > 0:
					self.state = STATE_UNLOADSTATION
				# if our cargo is empty, and lasers are loaded, we're idling and checking other things
				elif self.undockSafeFlag:
					self.state = STATE_READYSTATION
				else:
					self.state = STATE_IDLESTATION
			elif self.IsInWarp():
				self.state = STATE_WARPING
			elif self.location == LOCATION_STATIONUNDOCKED:
				cargownd = self.GetCargo()
				if cargownd == None:
					self.state == STATE_HIBERNATE
					self.UpdateStateLock = 0
					return
				cap = cargownd.GetCapacity()
				(total, full,) = (cap.capacity, cap.used)
				if total:
					proportion = min(1.0, max(0.0, full / float(total)))
				else:
					proportion = 1.0
				# we're being lenient on the definition of "full" here
				if proportion > 0.9:
					self.state = STATE_DOCKINGSTATION
				else:
					self.state = STATE_UNDOCKED
			elif self.location == LOCATION_BELT:
				# if our cargo is full and we're at a belt, we must be docking up
				cargownd = self.GetCargo()
				if cargownd == None:
					self.state == STATE_HIBERNATE
					self.UpdateStateLock = 0
					return
				cap = cargownd.GetCapacity()
				(total, full,) = (cap.capacity, cap.used)
				if total:
					proportion = min(1.0, max(0.0, full / float(total)))
				else:
					proportion = 1.0
				# we're being lenient on the definition of "full" here
				if proportion > 0.9:
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
				self.station = session.stationid
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
			overview = sm.GetService('window').GetWindow('OverView')
			scrollnodes = overview.sr.scroll.GetNodes()
			if scrollnodes is not None:
				targets = sm.GetService('target').GetTargets()
				if (len(scrollnodes)) < 6 and (len(targets) == 0):
				# we need to warp to a better belt, and tag this one bad
					if not self.WarpLock:
						if self.currentBM not in self.bmsToSkip:
							self.bmsToSkip.append(self.currentBM)
						msg('Bad belt, currently skipping %d' % len(self.bmsToSkip))
						self.SaveStats()
						Sleep(1000)
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
					if nearBall == None:
						self.MineLock = 0
						return
					dist = trinity.TriVector(nearBall.x - myBall.x, nearBall.y - myBall.y, nearBall.z - myBall.z).Length()
					if dist >= const.minWarpDistance:
						# we need to warp to the asteroid first
						try:
							sm.GetService('menu').WarpToItem(nearNode.slimItem().itemID, 2000)
							Sleep(10000)
						except:
							msg('warp error')
						self.MineLock = 0
						return
   					# we need to check if target is in range, if not, we should warp off
					elif (dist <= const.minWarpDistance) and (dist > 15000):
						if not self.WarpLock:
							self.WarpToBelt()
						self.MineLock = 0
						return
					else:
						# we can mine now
						# first check to see if we have 3 targets
						targetsvc = sm.GetService('target')
						targets = targetsvc.GetTargets()
						if len(targets) < 6:
   							overview = sm.GetService('window').GetWindow('OverView')
							scrollnodes = overview.sr.scroll.GetNodes()
							upto = min(len(scrollnodes), 6)
							# we need to acquire new targets until we have 3
							i = 0
							for node in scrollnodes:
									try:
										nodeBall = bp.GetBall(node.slimItem().itemID)
										dist = trinity.TriVector(nodeBall.x - myBall.x, nodeBall.y - myBall.y, nodeBall.z - myBall.z).Length()
										if dist < 20000:
											targetsvc.TryLockTarget(node.slimItem().itemID)
											if dist > 15000:
												sm.GetService('menu').Approach(node.slimItem().itemID, 1000)
									except:
										msg('error in targetting')
										Sleep(3000)
 									i += 1
									if i >= upto:
										break
									Sleep(250)
						Sleep(random.randrange(2000,3000))
						# now we need to worry about activating all modules
						if len(targetsvc.GetTargets()) >= 1:
							modulelist = []
							deactivate = []
		  					for i in xrange(0, 8):
								slot = uicore.layer.shipui.sr.slotsByOrder.get((0, i), None)
								if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
									if not slot.sr.module.def_effect.isActive:
								 		#we need to activate the module
										modulelist.append(slot.sr.module)
									else:
										try:
											if (not self.modulesTargets[slot.sr.module.id] == None) and (not self.modulesTargets[slot.sr.module.id] in targetsvc.GetTargets()):
												deactivate.append(slot.sr.module)
										except:
											msg('error finding modules')
							for each in modulelist:
								try:
									targetID = targetsvc.GetActiveTargetID()
									eachBall = sm.GetService('michelle').GetBallpark().GetBall(targetID)
									dist = trinity.TriVector(eachBall.x - myBall.x, eachBall.y - myBall.y, eachBall.z - myBall.z).Length()
									if dist < 15000:
										uthread.new(each.Click)
										Sleep(random.randrange(1000,1500))
										self.modulesTargets[each.id] = targetsvc.GetActiveTargetID()
									elif dist < 20000:
										sm.GetService('menu').Approach(targetID, 1000)
										Sleep(5000)
									else:
										if (not self.WarpLock):
											self.WarpToBelt()
											Sleep(10000)
											self.MineLock = 0
										return
									targetsvc.SelectNextTarget()
								except:
									msg('error in activating modules')
									Sleep(5000)
							for each in deactivate:
								try:
									uthread.new(each.Click)
									Sleep(random.randrange(200,800))
									self.modulesTargets[each.id] = None
								except:
									pass
						self.MineLock = 0


		@safetycheck
		def WarpToBelt(self):
			self.WarpLock = 1
			try:
				absvc = sm.GetService('addressbook')
				bookmarks = absvc.GetBookmarks()
				bmsAll = list()
				for each in bookmarks.itervalues():
					if each.locationID == session.solarsystemid:
						bmsAll.append(each)
				if len(self.bmsToSkip) >= len(bmsAll):
					msg('all belts are depleted!')
					self.state = STATE_HIBERNATE
					self.WarpLock = 0
					return

				bms = list()
				for each in bmsAll:
					if each.bookmarkID not in self.bmsToSkip:
						bms.append(each)
				# getting rid of the bms that we need to skip
				if len(bms) > 0:
					if len(bms) == 1:
						randomidx = 0
					else:
						randomidx = random.randrange(0, len(bms)-1)
					self.currentBM = bms[randomidx].bookmarkID
					sm.GetService('menu').WarpToBookmark(bms[randomidx], 0.0, False)
					Sleep(10000)
			except:
				msg('cannot warp to belt')
				Sleep(10000)

			self.WarpLock = 0

		@safetycheck
		def DockUp(self):
			try:
				sm.GetService('menu').Dock(self.station)
			except:
				msg('cannot dock yet')
				self.updateSkip += 5

		@safetycheck
		def Undock(self):
			self.UndockLock = 1
			try:
				Sleep(random.randrange(25000, 30000))
  				uicore.cmd.CmdExitStation()
				Sleep(random.randrange(15000, 18000))
 				self.runCount += 1
				self.SaveStats()
				self.undockSafeFlag = 0
			except:
				msg('cannot undock')
			self.UndockLock = 0

		@safetycheck
		def Unload(self):
			try:
				cargo = self.GetCargo()
				hangar = self.GetHangar()
				if cargo and hangar:
					cap = cargo.GetCapacity()
 					load = cap.used
					self.totalUnload += load
					self.SaveStats()
					hangar.OnDropDataWithIdx(cargo.sr.scroll.GetNodes())
			except:
				msg('cannot unload')

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
		def GetFitting(self):
			fitting = sm.GetService('window').GetWindow('fitting')
			if fitting == None:
				sm.GetService('window').GetWindow('fitting', decoClass=form.FittingWindow, create=1, maximize=1)
				Sleep(3000)
				fitting = sm.GetService('window').GetWindow('fitting')
			return fitting

		@safetycheck
		def RefillCrystal(self):
			self.RefillLock = 1
			try:
				hangar = self.GetHangar()
				fittingwnd = self.GetFitting()
				if hangar == None or fittingwnd == None:
					self.RefillLock = 0
					return
				# get empty mining laser slots
				empty = []
				for slot in fittingwnd.sr.fitting.slots.itervalues():
					if hasattr(slot, 'module') and (slot.module) and (slot.module.groupID == const.groupFrequencyMiningLaser):
						if slot.IsChargeEmpty():
							empty.append(slot)
				msg('%d empty lasers detected' % len(empty))
				if len(empty) > 0:
					Sleep(2000)
					# get crystal nodes from the item hangar
					crystals = []
					for node in hangar.sr.scroll.GetNodes():
						item = node.rec
						if empty[0].IsCharge(item.typeID):
							crystals.append(item)
					for slot in empty:
						item = crystals.pop()
						slot.shell.inventory.Add(item.itemID, item.locationID, qty=1, flag=slot.locationFlag)
						msg('loaded a crystal into slot%d' % slot.id)
						Sleep(3000)
				self.undockSafeFlag = 1
			except:
				msg('error in refilling crystals')
			self.RefillLock = 0

		@safetycheck
		def LoadStats(self):
			MinerStats = settings.public.ui.Get("MinerStats")
			if MinerStats == None:
				return
			self.runCount = MinerStats[0]
			self.bmsToSkip = MinerStats[1]
			self.totalUnload = MinerStats[2]
			self.lastStart = settings.public.ui.Get("MinerLastStart")

		@safetycheck
		def SaveStats(self):
			# we're packing the useful stats into one tuple to store in settings
			MinerStats = [self.runCount, self.bmsToSkip, self.totalUnload]
			settings.public.ui.Set("MinerStats", MinerStats)
			self.statsTime = FormatTimeAgo(self.lastStart)

		@safetycheck
		def ClearStats(self):
			self.LogToFile()
			self.runCount = 0
			self.bmsToSkip = list()
			self.totalUnload = 0
			settings.public.ui.Set("MinerStats", None)
			now = blue.os.GetTime()
			settings.public.ui.Set("MinerLastStart", now)
			self.lastStart = now
			self.UpdatePane()
			msg('Miner stats cleared!')

		@safetycheck
		def LogToFile(self):
			path = 'c:/Users/Public/'
			if not os.path.exists(path):
				os.makedirs(path)
	  		filename = 'logfile.txt'
			sio = cStringIO.StringIO()
			sio.write('\n')
			now = blue.os.GetTime()
			if self.lastStart == None:
				self.lastStart = now
			sessionInfo = '---Session from  %s  to  %s---\n' % (util.FmtDate(self.lastStart), util.FmtDate(now))
			sio.write(sessionInfo)
			durationText = FormatTimeAgo(self.lastStart)
			durationText = durationText[:-4]
			sio.write('Run duration:  %s\n' % durationText)
			sio.write('Runs completed:  %s\n' % self.runCount)
			sio.write('Number of belts depleted:  %s\n' % len(self.bmsToSkip))
			sio.write('Total ores mined:  %s m3\n' % self.totalUnload)
			sio.write('\n')
			with open(path+filename, 'a') as f:
				f.write(sio.getvalue())
			f.close()


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
			self.runCount = 0
			self.avgTime = 0
			self.totalUnload = 0
			self.lastStart = None
			self.balls = []
			self.station = None
			self.UpdateLocationLock = 0
			self.UpdateStateLock = 0
			self.MineLock = 0
			self.UndockLock = 0
			self.DoLock = 0
			self.RefillLock = 0
			self.WarpLock = 0
			self.pane = None
			self.bmsToSkip = []
			self.currentBM = None
			self.modulesTargets = {}
			self.updateSkip = 0
			self.undockSafeFlag = 0
			self.state = None
			self.location = None

	class Dash(uicls.Container):
			__guid__ = 'uicls.Dash'

			def ApplyAttributes(self, attributes):
				self.scope = 'station_inflight'
				self.message = None
				self.message2 = None
				self.message3 = None
				self.message4 = None
				self.message5 = None
				self.message6 = None
				uicls.Container.ApplyAttributes(self, attributes)

			def Prepare_Text_(self):
				self.message = uicls.Label(text='', parent=self, left=0, top=4, autowidth=False, width=400, fontsize=12, state=uiconst.UI_DISABLED)
				self.message2 = uicls.Label(text='', parent=self, left=0, top=16, autowidth=False, width=400, fontsize=12, state=uiconst.UI_DISABLED)
				self.message3 = uicls.Label(text='', parent=self, left=0, top=28, autowidth=False, width=400, fontsize=12, state=uiconst.UI_DISABLED)
				self.message4 = uicls.Label(text='', parent=self, left=0, top=40, autowidth=False, width=400, fontsize=12, state=uiconst.UI_DISABLED)
				self.message5 = uicls.Label(text='', parent=self, left=0, top=52, autowidth=False, width=400, fontsize=12, state=uiconst.UI_DISABLED)
				self.message6 = uicls.Label(text='', parent=self, left=0, top=70, autowidth=False, width=400, fontsize=12, state=uiconst.UI_DISABLED)

			def Prepare_Underlay_(self):
				border = uicls.Frame(parent=self, frameConst=uiconst.FRAME_BORDER1_CORNER1, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.5))
				frame = uicls.Frame(parent=self, color=(0.0, 0.0, 0.0, 0.75), frameConst=uiconst.FRAME_FILLED_CORNER1, state=uiconst.UI_DISABLED)

			def ShowMsg(self, location, state, runCount, skipNum, unloaded, statsTime):
				if self.message is None:
					self.Prepare_Text_()
					self.Prepare_Underlay_()
				self.message.text = '<left> Location: <color=0xffffff00>%s' % location
				self.message2.text = '<left> State: <color=0xff00ffff>%s' % state
				self.message3.text = '<right>Total Run Count: <color=0xff00ff37>%d ' % runCount
				self.message4.text = '<right>Number of belts currently being skipped: <color=0xff00ff37>%d ' % skipNum
				self.message5.text = '<right>Total Ores Mined: <color=0xff00ff37>%s m\xb3 ' % (util.FmtAmt(unloaded, showFraction=1))
				self.message6.text = '<center>Current stats logged from: %s' % statsTime
				self.SetAlign(uiconst.CENTERTOP)
				self.SetSize(400, 86)
				offset = sm.GetService('window').GetCameraLeftOffset(self.width, align=uiconst.CENTERTOP, left=0)
				self.SetPosition(offset, 5)
				self.state = uiconst.UI_DISABLED
				uiutil.SetOrder(self, 0)

	@safetycheck
	def Action(*args):
		# arbitrary action definition!
		miner = sm.GetService('jukebox').playlists
		if miner == None:
			msg('Miner Service not running!')
			return
		if hasattr(miner, 'alive'):
			# here comes the action!
			warping = miner.IsInWarp()
			if warping:
				msg('in warp')
			else:
				msg('not in warp')


	try:

		neocomwnd = sm.GetService('neocom').main
		btn = uix.GetBigButton(32, neocomwnd, top=800)
		btn.OnClick = CreateIt
		btn.hint = "Start Miner service"
		btn.sr.icon.LoadIcon('11_12')
		createBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=833)
		btn.OnClick = DestroyIt
		btn.hint = "Kill Miner service"
		btn.sr.icon.LoadIcon('11_13')
		destroyBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=866)
		btn.OnClick = ClearIt
		btn.hint = "Clear stats"
		btn.sr.icon.LoadIcon('11_14')
		actionBtn = btn

	except:
  		msg('failed doing something')

except:
	pass