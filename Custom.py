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
	import state
	import random
	import spaceObject
	import blue
	import timecurves

	try:
		form.Scanner.localChannel = None
		form.Scanner.localChannel2 = None
		form.Scanner.reportChannel = None
	except:
		msg('damn it')

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

	"""
	treading in dangerous waters!!!
	"""

	try:
		service.Service.LogMethodCall = service.Service.DudLogger
		service.Service.LogInfo = service.Service.DudLogger
		service.Service.LogWarn = service.Service.DudLogger
		service.Service.LogError = service.Service.DudLogger
		service.Service.LogNotice = service.Service.DudLogger
	except:
		msg('danger!!danger!!')


	@safetycheck
	def Report(*args):
		try:
			localChannel = None
			reportChannel = None
			reportStr = ''
			for channelID in sm.GetService('LSC').channels.keys():
				channel = sm.GetService('LSC').channels[channelID]
				"""
				if (channel.window and ((type(channel.channelID) is tuple) and (channel.channelID[0][0] == 'solarsystemid2'))):
					localChannel = channel
				elif (channel.window and (channel.channelID[0] == 'global')):
					reportChannel = channel
				if (channel.window and ((type(channel.channelID) is tuple) and (channel.channelID[0][0] == 'solarsystemid2'))):
				"""
				tempStr = 'Channel: %s' % channel.channelID
				reportStr = reportStr + tempStr + '\n'
				"""
				elif (channel.window and (channel.channeID[0] == 'corpid')):
					tempStr = 'Channel: %s' % channel.channelID
					reportStr = reportStr + tempStr + '\n'
				"""

			if (reportStr):
				sm.GetService('gameui').Say(reportStr)

			else:
				sm.GetService('gameui').Say('fuck')

		except:
			sm.GetService('gameui').Say('error3')

	@safetycheck
	def msg(m = 'bad input'):
		try:
			sm.GetService('gameui').Say(m)
		except:
			pass

	@safetycheck
	def GetLocal(*args):
		form.Scanner.localChannel = sm.GetService('focus').GetFocusChannel()
		msg('Local channel set!')
		blue.pyos.synchro.Sleep(randomPause(500,800))
		ReportLocal(*args)

	@safetycheck
	def SetReport(*args):
		form.Scanner.reportChannel = sm.GetService('focus').GetFocusChannel()
		msg('Report channel set!')

	@safetycheck
	def randomPause(fromtime = 0, totime = 1000):
		return random.randrange(fromtime, totime)

	@safetycheck
	def GetNearbyItem(*args):
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
			"""
			slimItem = uix.GetBallparkRecord(itemID)
			invItem = self.TryGetInvItem(itemID)
			if slimItem:
				categoryID = cfg.invtypes.Get(slimItem.typeID).categoryID
				groupID = cfg.invtypes.Get(slimItem.typeID).groupID
			elif invItem:
				typeOb = cfg.invtypes.Get(invItem.typeID)
				groupID = typeOb.groupID
				categoryID = typeOb.categoryID
			if not ((categoryID == const.categoryAsteroid) or ((groupID in (const.groupAsteroidBelt,
				 const.groupPlanet,
				 const.groupMoon,
				 const.groupSun,
				 const.groupHarvestableCloud,
				 const.groupSecondarySun)) )):
				continue
			"""
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

	@safetycheck
	def MyRemoveBall(ball, *args):
		if len(form.OverView.ballsToTheWall) > 20:
			return
		if form.OverView.ballsToTheWall:
			form.OverView.ballsToTheWall.append(ball)
		return


	@safetycheck
	def WatchWarpOff(*args):
		if uicore.uilib.Key(uiconst.VK_SHIFT):
			sm.GetService('michelle').GetBallpark().RemoveBall = MyRemoveBall
			sm.GetService('gameui').Say('Changed RemoveBall to my own')
			return

		sm.GetService('michelle').GetBallpark().RemoveBall = old_remove_ball
		for ball in form.OverView.ballsToTheWall:
			sm.GetService('michelle').GetBallpark().RemoveBall(ball)
		form.OverView.ballsToTheWall = list()
		form.OverView.UpdateAll
		sm.GetService('gameui').Say('Reverted back to normal RemoveBall')

	@safetycheck
	def ReportLocal(*args):
		try:
			msg('Reporting local channel...')
			for channelID in sm.GetService('LSC').channels.keys():
				channel = sm.GetService('LSC').channels[channelID]
				if (channel.window and ((type(channel.channelID) is tuple) and (channel.channelID[0][0] == 'solarsystemid2'))):
					form.Scanner.localChannel2 = channel
			solarSystemID = form.Scanner.localChannel2.channelID[0][1]
			solarSystemName = cfg.evelocations.Get(solarSystemID).name
			link = ('showinfo:5' + '//' + str(solarSystemID))
			form.Scanner.reportChannel.input.AddLink(solarSystemName, link)

			entries = form.Scanner.localChannel2.window.userlist.GetNodes()
			redCount = 0
			blueCount = 0
			orangeCount = 0
			neutCount = 0
			hostileList = list()
			count = 0

			for entry in entries:
				charID = entry.charID
				corpCharInfo = sm.GetService('corp').GetInfoWindowDataForChar(charID, 1)
				corpID = corpCharInfo.corpID
				allianceID = corpCharInfo.allianceID

				if (eve.session.charid == charID):
					continue
				myStandingID = None
				if (eve.session.allianceid):
					myStandingID = eve.session.allianceid
				else:
					myStandingID = eve.session.corpid
				standing = sm.GetService('standing').GetStanding(myStandingID, charID)
				if ((standing >= 0.5) or (eve.session.corpid == corpID) or ((eve.session.allianceid != None) and (eve.session.allianceid == allianceID))):
					blueCount += 1
				elif (standing < 0.5 and standing >= 0.0):
					neutCount += 1
					hostileList.append(entry)
					count += 1
					msg('hostiles detected %d' % count)
				elif (standing < 0.0 and standing > -1.0):
					orangeCount += 1
					hostileList.append(entry)
					count += 1
					msg('hostiles detected %d' % count)
				else:
					redCount = redCount + 1
					hostileList.append(entry)
					count += 1
					msg('hostiles detected %d' % count)
				if count >= 50:
					break

			blueText = '%d blues' % blueCount
			neutText = '%d neuts' % neutCount
			redText = '%d reds' % (redCount + orangeCount)
			solarSystemText = ': %s, %s, %s' % (blueText, neutText, redText)
			form.Scanner.reportChannel.input.InsertText('%s\r' % solarSystemText)
			form.Scanner.reportChannel.InputKeyUp()

			if len(hostileList) > 0:
				blue.pyos.synchro.Sleep(randomPause(1000,1500))
				iterNum = 0
				reportLimit = 15
				for entry in hostileList:
					iterNum += 1
					corpCharInfo = sm.GetService('corp').GetInfoWindowDataForChar(entry.charID, 1)
					corpID = corpCharInfo.corpID
					allianceID = corpCharInfo.allianceID
					if (iterNum % 3) == 1:
						form.Scanner.reportChannel.input.InsertText('|\r')
					link = ((('showinfo:' + str(entry.info.typeID)) + '//') + str(entry.charID))
					form.Scanner.reportChannel.input.AddLink(entry.info.name, link)
					ids = ''
					if allianceID:
						ids = cfg.eveowners.Get(allianceID).name
					else:
						ids = cfg.eveowners.Get(corpID).name
					form.Scanner.reportChannel.input.InsertText('-%s\r' % ids)
					if (iterNum == len(hostileList)) or (iterNum >= reportLimit):
						form.Scanner.reportChannel.input.InsertText('-(%d/%d)-'%(iterNum, len(hostileList)))
						form.Scanner.reportChannel.InputKeyUp()
						break
					if ((iterNum % 3) == 0):
						form.Scanner.reportChannel.InputKeyUp()
						blue.pyos.synchro.Sleep(randomPause(800,1100))

			msg('Local report done!')

		except:
			msg('error2')

	try:
		pane = sm.GetService('window').GetWindow("New", create=1)
		pane.windowID = "TestWindow"
		btn = uix.GetBigButton(50, pane.sr.main, left=0)
		btn.OnClick = ReportLocal
		btn.hint = "ReportLocal"
		btn.sr.icon.LoadIcon('44_02')
		pane.sr.FocusBtn = btn

		btn = uix.GetBigButton(50, pane.sr.main, left=50)
		btn.OnClick = SetReport
		btn.hint = "SetReport"
		btn.sr.icon.LoadIcon('44_01')
		pane.sr.Focus2Btn = btn

		"""
		btn = uix.GetBigButton(50, pane.sr.main, left=80)
		btn.OnClick = ReportLocal
		btn.hint = "ReportLocal"
		btn.sr.icon.LoadIcon('44_04')
		pane.sr.ReportBtn = btn
		"""

		btn = uix.GetBigButton(50, pane.sr.main, left=150)
		btn.OnClick = WatchWarpOff
		btn.hint = "Watch!"
		btn.sr.icon.LoadIcon('44_03')
		pane.sr.WatchBtn = btn

		btn = uix.GetBigButton(50, pane.sr.main, left=200)
		btn.OnClick = GetNearbyItem
		btn.hint = "Show nearby item"
		btn.sr.icon.LoadIcon('77_21')
		pane.sr.nearbyBtn = btn

	except:
		sm.GetService('gameui').Say('didn\'t work!')

except:
	print "Error"
