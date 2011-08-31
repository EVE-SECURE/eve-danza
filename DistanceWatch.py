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
					sm.GetService('gameui').Say(result2)
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
	def SetReport(*args):
		form.Scanner.reportChannel = sm.GetService('focus').GetFocusChannel()
		msg('Report channel set!')

	@safetycheck
	def randomPause(fromtime = 0, totime = 1000):
		return random.randrange(fromtime, totime)

	@safetycheck
	def ReportLocal(*args):
		try:
			msg('Reporting local channel...')
			for channelID in sm.GetService('LSC').channels.keys():
				channel = sm.GetService('LSC').channels[channelID]
				if (channel.window and ((type(channel.channelID) is tuple) and (channel.channelID[0][0] == 'solarsystemid2'))):
					form.Scanner.localChannel = channel
			solarSystemID = form.Scanner.localChannel.channelID[0][1]
			solarSystemName = cfg.evelocations.Get(solarSystemID).name
			link = ('showinfo:5' + '//' + str(solarSystemID))
			form.Scanner.reportChannel.input.AddLink(solarSystemName, link)

			entries = form.Scanner.localChannel.window.userlist.GetNodes()
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
			msg('error')

	class MyService():
		__guid__ = 'svc.MyService'
		__servicename__ = 'MyService'
		__displayname__ = 'My Service'

		def __init__(self):
			sm.GetService('gameui').Say('DistanceWatch Service started')
			self.pane = None
			self.watch = []
			self.anchor = None

  			self.alive = base.AutoTimer(1000, self.Update)
			self.initPane()

		@safetycheck
		def initPane(self):
			self.pane = Dash(parent=uicore.layer.abovemain, name='LocalDash')
			self.pane.ShowMsg("Watching nothing right now!")

		@safetycheck
		def Update(self):
			if self.pane == None:
				return
			output = 'Distances to anchor object:\n'
   			ballPark = sm.GetService('michelle').GetBallpark()
			if self.anchor == None:
				self.pane.ShowMsg("No anchor!")
				return
			anchorBall = ballPark.GetBall(self.anchor)
			if anchorBall == None:
				return
			output += 'My distance to anchor: %s km\n' % (util.FmtAmt(anchorBall.surfaceDist/1000, showFraction=0))
			if len(self.watch) > 0:
	 			sortwatch = []
				for eachID in self.watch:
					eachBall = ballPark.GetBall(eachID)
					if eachBall == None:
						return
					dist = trinity.TriVector(eachBall.x - anchorBall.x, eachBall.y - anchorBall.y, eachBall.z - anchorBall.z).Length()
					sortwatch.append((dist, eachBall))
				sortwatch.sort()

				for (dist, eachBall) in sortwatch:
					slimItem = sm.GetService('michelle').GetItem(eachBall.id)
					if slimItem:
						entryname = uix.GetSlimItemName(slimItem)
					if not entryname:
						entryname = cfg.evelocations.Get(eachBall.id).name
					output += '%s: %s km\n' %(entryname, util.FmtAmt(dist/1000, showFraction=0))

			self.pane.ShowMsg(output)

		@safetycheck
		def AddAnchor(self):
			try:
				itemID = eve.LocalSvc("window").GetWindow("selecteditemview").itemIDs[0]
				self.anchor = itemID
				msg("added anchor!")
			except:
				msg("no target selected!")

		@safetycheck
		def AddToWatch(self):
			try:
				itemID = eve.LocalSvc("window").GetWindow("selecteditemview").itemIDs[0]
				self.watch.append(itemID)
				msg("added current target to watchlist!")
			except:
				msg("no target selected!")

		@safetycheck
		def ClearWatchList(self):
			if len(self.watch) > 0:
				self.watch = []
				msg("watchlist cleared")
			else:
				msg("nothing in watchlist!")

		def Open(self):
			if self.pane:
				return
			self.initPane()

		def Close(self):
			if self.pane:
				self.pane.Close()

		def CleanUp(self):
			self.pane.Close()
			del self.pane
			self.pane = None
			self.watch = []
			self.anchor = None
			del self.alive
			self.alive = None


	class Dash(uicls.Container):
			__guid__ = 'uicls.LocalDash'

			def ApplyAttributes(self, attributes):
				self.scope = 'station_inflight'
				self.message = None
				uicls.Container.ApplyAttributes(self, attributes)

			def Prepare_Text_(self):
				self.message = uicls.Label(text='', parent=self, left=0, top=4, autowidth=False, width=200, fontsize=12, state=uiconst.UI_DISABLED)

			def Prepare_Underlay_(self):
				border = uicls.Frame(parent=self, frameConst=uiconst.FRAME_BORDER1_CORNER1, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25))
				frame = uicls.Frame(parent=self, color=(0.0, 0.0, 0.0, 0.75), frameConst=uiconst.FRAME_FILLED_CORNER1, state=uiconst.UI_DISABLED)

			def ShowMsg(self, text1):
				if self.message is None:
					self.Prepare_Text_()
					self.Prepare_Underlay_()
				self.message.text = '<center><color=0xffffffff>' + text1
				self.SetAlign(uiconst.CENTERTOP)
				self.SetSize(200, 120)
				offset = sm.GetService('window').GetCameraLeftOffset(self.width, align=uiconst.CENTERTOP, left=0)
				self.SetPosition(offset, 5)
				self.state = uiconst.UI_DISABLED
				uiutil.SetOrder(self, 0)



	@safetycheck
	def CreateIt(*args):
		#create an instance of something
		bottomline = sm.GetService('neocom').bottomline
		if bottomline and hasattr(bottomline, "alive") and bottomline.alive:
			sm.GetService('neocom').bottomline.CleanUp()
			del sm.GetService('neocom').bottomline
			sm.GetService('neocom').bottomline = None
			msg('Killed DistanceWatch')
		else:
			sm.GetService('neocom').bottomline = MyService()

	@safetycheck
	def DestroyIt(*args):
		#destroy an instance of something
		if sm.GetService('neocom').bottomline == None:
			msg('DistanceWatch Service not running!')
			return
		if hasattr(sm.GetService('neocom').bottomline, 'alive'):
			sm.GetService('neocom').bottomline.CleanUp()
		del sm.GetService('neocom').bottomline
		sm.GetService('neocom').bottomline = None
		msg('DistanceWatch Service killed!')

	@safetycheck
	def ClearIt(*args):
		bottomline = sm.GetService('neocom').bottomline
		if bottomline and hasattr(bottomline, 'alive') and bottomline.alive:
			bottomline.ClearWatchList()

	@safetycheck
	def AddAnchor(*args):
		bottomline = sm.GetService('neocom').bottomline
		if bottomline and hasattr(bottomline, 'alive') and bottomline.alive:
			bottomline.AddAnchor()

	@safetycheck
	def AddToWatch(*args):
		bottomline = sm.GetService('neocom').bottomline
		if bottomline and hasattr(bottomline, 'alive') and bottomline.alive:
			bottomline.AddToWatch()

	@safetycheck
	def TryGetInvItem(itemID):
		if eve.session.shipid is None:
			return
		ship = eve.GetInventoryFromId(eve.session.shipid)
		if ship:
			for invItem in ship.List():
				if invItem.itemID == itemID:
					return invItem
	@safetycheck
	def GetItem(itemID):
		item = uix.GetBallparkRecord(itemID)
		if not item:
			item = TryGetInvItem(itemID)
		return item

	try:

		neocomwnd = sm.GetService('neocom').main
		btn = uix.GetBigButton(32, neocomwnd, top=800)
		btn.OnClick = CreateIt
		btn.hint = "Start DistanceWatch"
		btn.sr.icon.LoadIcon('11_01')
		createBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=833)
		btn.OnClick = ClearIt
		btn.hint = "Clear Watchlist"
		btn.sr.icon.LoadIcon('11_02')
		destroyBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=866)
		btn.OnClick = AddAnchor
		btn.hint = "Add Anchor"
		btn.sr.icon.LoadIcon('11_03')
		killBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=899)
		btn.OnClick = AddToWatch
		btn.hint = "Add To Watchlist"
		btn.sr.icon.LoadIcon('11_04')
		warnBtn = btn


	except:
		msg('bad inject')

except:
	pass
