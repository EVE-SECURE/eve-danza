try:
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


	try:
		ActiveItem_old_apply_attributes
	except NameError:
		ActiveItem_old_apply_attributes = form.ActiveItem.ApplyAttributes

 	try:
		old_remove_ball = sm.GetService('michelle').GetBallpark().RemoveBall

		form.ActiveItem.ballsToTheWall = list()

	except:
		sm.GetService('gameui').Say("exception1")

	def safetycheck(func):
		def wrapper(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except:
				try:
					print "exception in " + func.__name__
					(exc, e, tb,) = sys.exc_info()
					result2 = (''.join(format_exception(exc, e, tb)) + '\n').replace('\n', '<br>')
					sm.GetService('gameui').MessageBox(result2, "Caught Exception")
				except:
					print "exception in safetycheck"
		return wrapper

	@safetycheck
	def msg(m = 'bad input'):
		try:
			sm.GetService('gameui').Say(m)
		except:
			pass

	@safetycheck
	def GetNearbyItem(self, *args):
		currItem = eve.LocalSvc("window").GetWindow("selecteditemview").itemIDs[0]
		bp = eve.LocalSvc("michelle").GetBallpark()
		currBall = bp.GetBall(currItem)
		shortestDist = currBall.surfaceDist
		nearbyItem = currItem
		nearbyBall = None
		entryname = None
		for itemID in bp.balls.keys():
			if bp is None:
				break
			if (itemID == eve.session.shipid):
				continue
			if (itemID == currItem):
				continue
##			"""
##			slimItem = uix.GetBallparkRecord(itemID)
##			invItem = self.TryGetInvItem(itemID)
##			if slimItem:
##				categoryID = cfg.invtypes.Get(slimItem.typeID).categoryID
##				groupID = cfg.invtypes.Get(slimItem.typeID).groupID
##			elif invItem:
##				typeOb = cfg.invtypes.Get(invItem.typeID)
##				groupID = typeOb.groupID
##				categoryID = typeOb.categoryID
##			if not ((categoryID == const.categoryAsteroid) or ((groupID in (const.groupAsteroidBelt,
##				 const.groupPlanet,
##				 const.groupMoon,
##				 const.groupSun,
##				 const.groupHarvestableCloud,
##				 const.groupSecondarySun)) )):
##				continue
##			"""
			itemBall = bp.GetBall(itemID)
			proximity = abs(currBall.surfaceDist - itemBall.surfaceDist)
			if proximity < shortestDist:
				shortestDist = proximity
				nearbyItem = itemID
				nearbyBall = itemBall
		slimItem = sm.GetService('michelle').GetItem(nearbyItem)
		if slimItem:
			entryname = uix.GetSlimItemName(slimItem)
		if not entryname:
			entryname = cfg.evelocations.Get(nearbyItem).name
		realdiststr = None
		try:
			nearbyPos = Vector3(nearbyBall.x, nearbyBall.y, nearbyBall.z)
			currPos = Vector3(currBall.x, currBall.y, currBall.z)
			realDist = (nearbyPos - currPos).Length()
			realdiststr = util.FmtDist(realDist, maxdemicals=1)
		except:
			pass
		if not realdiststr:
			realdiststr = ''

		sm.GetService('gameui').Say('Nearby Item is: %s, Distance is: %s' % (entryname, realdiststr, ))

	form.ActiveItem.GetNearbyItem = GetNearbyItem

	@safetycheck
	def MyRemoveBall(self, ball, *args):
		form.ActiveItem.ballsToTheWall.append(ball)
		return

	form.ActiveItem.MyRemoveBall = MyRemoveBall


	@safetycheck
	def WatchWarpOff(self, *args):
		if uicore.uilib.Key(uiconst.VK_SHIFT):
			sm.GetService('michelle').GetBallpark().RemoveBall = self.MyRemoveBall
			sm.GetService('gameui').Say('Changed RemoveBall to my own')
			return

		sm.GetService('michelle').GetBallpark().RemoveBall = old_remove_ball

		for ball in form.ActiveItem.ballsToTheWall:
			sm.GetService('michelle').GetBallpark().RemoveBall(ball)
		form.ActiveItem.ballsToTheWall = list()

		form.OverView.UpdateAll
		sm.GetService('gameui').Say('Reverted back to normal RemoveBall')

	form.ActiveItem.WatchWarpOff = WatchWarpOff

	@safetycheck
	def OrbitGet(self, *args):
		(config, value,) = args
		settings.user.ui.Set('defaultOrbitDist', value)
		msg('Set default orbit distance to %dm' % int(value))
		sm.ScatterEvent('OnDistSettingsChange')

	form.ActiveItem.OrbitGet = OrbitGet

	@safetycheck
	def OrbitSet(self, *args):
	    return

	form.ActiveItem.OrbitSet = OrbitSet

	@safetycheck
	def KeepRangeGet(self, *args):
		(config, value,) = args
		settings.user.ui.Set('defaultKeepAtRangeDist', value)
		msg('Set default keep range distance to %dm' % int(value))
		sm.ScatterEvent('OnDistSettingsChange')

	form.ActiveItem.KeepRangeGet = KeepRangeGet

	@safetycheck
	def KeepRangeSet(self, *args):
	    return

	form.ActiveItem.KeepRangeSet = KeepRangeSet

	@safetycheck
	def MyApplyAttributes(self, attributes):
		ActiveItem_old_apply_attributes(self, attributes)

		btn = uix.GetBigButton(32, sm.GetService('window').GetWindow('selecteditemview'), left=315, top=20)
		btn.OnClick = self.WatchWarpOff
		btn.hint = "Watch!"
		btn.sr.icon.LoadIcon('44_03')
		self.sr.WatchBtn = btn

		btn = uix.GetBigButton(32, sm.GetService('window').GetWindow('selecteditemview'), left=315, top=55)
		btn.OnClick = self.GetNearbyItem
		btn.hint = "Show nearby item"
		btn.sr.icon.LoadIcon('77_21')
		self.sr.nearbyBtn = btn

		orbitslider = uix.GetSlider('slider', sm.GetService('window').GetWindow('selecteditemview'), 'orbitdist', 500, 30000, 'Orbit Distance', '', uiconst.BOTTOMLEFT, 150, 15, 5, 0, getvaluefunc=self.OrbitGet, endsliderfunc=self.OrbitSet, increments=(500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000, 20000, 21000, 22000, 23000, 24000, 25000, 26000, 27000, 28000, 29000, 30000), underlay=0)
		self.sr.orbitslider = orbitslider

		rangeslider = uix.GetSlider('slider', sm.GetService('window').GetWindow('selecteditemview'), 'keeprangedist', 500, 100000, 'Keep Range Distance', '', uiconst.BOTTOMLEFT, 150, 15, 160, 0, getvaluefunc=self.KeepRangeGet, endsliderfunc=self.KeepRangeSet, increments=(500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000, 20000, 21000, 22000, 23000, 24000, 25000, 26000, 27000, 28000, 29000, 30000, 35000, 40000, 50000, 60000, 70000, 80000, 90000, 100000), underlay=0)
		self.sr.rangeslider = rangeslider



	form.ActiveItem.ApplyAttributes = MyApplyAttributes

	try:
		wnd = sm.GetService('window').GetWindow('selecteditemview', decoClass=form.ActiveItem)
		if wnd:
			wnd.SelfDestruct()
		if session.solarsystemid:
			sm.GetService('tactical').InitSelectedItem()
	except:
		msg('bad inject')

except:
	pass
