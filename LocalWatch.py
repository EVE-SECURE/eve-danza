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

	try:
		form.Scanner.localChannel = None
		form.Scanner.reportChannel = None
	except:
		msg('bad syntax')

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

	@safetycheck
	def DisableLog(*args):
		try:
			sm.LogMethodCall = DudLogger
			count = 0
			for each in sm.services.keys():
				KillLogInfo(sm.services[each])
				count += 1
			msg('disabled logging in %d services' % count)
		except:
			msg('error in DisableLog')

	@safetycheck
	def KillLogInfo(service):
		try:
			service.LogInfo = DudLogger
			service.LogMethodCall = DudLogger
		except:
			msg('error in KillLogInfo')

	@safetycheck
	def DudLogger(self, *args, **keywords):
		return

	@safetycheck
	def MapMoveButton(*args):
		try:
			msg('mapping...')
			sm.GetService('cmd')._UpdateMovement = MyMove
		except:
			msg('map error')

	@safetycheck
	def UnmapMoveButton(*args):
		try:
			msg('unmapping...')
			sm.GetService('cmd')._UpdateMovement = old_UpdateMovement
		except:
			msg('unmap error')

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
		__guid__ = 'svc.MyService'
		__servicename__ = 'MyService'
		__displayname__ = 'My Service'

		def __init__(self):
			service.Service.__init__(self)
			sm.GetService('gameui').Say('LocalWatch Service started')
			self.pane = None
			self.cache = {}
			self.hostilecount = -1
			self.busy = False
			self.localChannel = None
			self.warning = False
			# search for local channel window and save it
			# WARNING: currently we do not update this reference on session change, add it in later!
			for channelID in sm.GetService('LSC').channels.keys():
				channel = sm.GetService('LSC').channels[channelID]
				if (channel.window and ((type(channel.channelID) is tuple) and (channel.channelID[0][0] == 'solarsystemid2'))):
					self.localChannel = channel
  			self.alive = base.AutoTimer(1000, self.Update)

##			self.A_down = False
##			self.S_down= False
##			self.D_down= False
##			self.W_down= False

		def initPane(self):
			"""
			self.pane = sm.GetService('window').GetWindow("Temp", create=1)
			self.pane.windowID = "TempWindow"
			btn = uix.GetBigButton(50, self.pane.sr.main, left=0)
			btn.OnClick = ReportInfo
			btn.hint = "ReportInfo"
			btn.sr.icon.LoadIcon('44_02')
			self.pane.sr.FocusBtn = btn

			btn = uix.GetBigButton(50, self.pane.sr.main, left=50)
			btn.OnClick = TryWarpToSafe
			btn.hint = "TryWarpToSafe"
			btn.sr.icon.LoadIcon('44_01')
			self.pane.sr.Focus2Btn = btn
			"""
			self.pane = LocalDash(parent=uicore.layer.abovemain, name='LocalDash')
			self.pane.SetOpacity(0.5)
			#self.pane.ShowMsg("<color=0xff0037ff>BLUES</color> "+" <color=0xffff3700>REDS</color> "+" <color=0xffffffff>TOTAL</color>" + "<br>",
			#				"<color=0xff0037ff>0</color>    "+" <color=0xffff3700>0</color> "+"    <color=0xffffffff>0</color>")
			if self.hostilecount == -1 or self.busy:
				self.pane.ShowMsg("<color=0xffffffff>HOSTILES: " + "<color=0xffff3700>updating...</color>")
			else:
				self.pane.ShowMsg("<color=0xffffffff>HOSTILES: " + "<color=0xffff3700>%d</color>" % self.hostilecount)


		def Update(self):

			"""
			self.A_down = False
			self.S_down = False
			self.D_down = False
			self.W_down = False
			ret = 'Keys down: '
			if uicore.uilib.Key(uiconst.VK_A):
				self.A_down = True
				ret += ' A'
			if uicore.uilib.Key(uiconst.VK_S):
				self.S_down= True
				ret += ' S'
			if uicore.uilib.Key(uiconst.VK_D):
				self.D_down= True
				ret += ' D'
			if uicore.uilib.Key(uiconst.VK_W):
				self.W_down= True
				ret += ' W'
			msg(ret)
			"""
			if not self.busy:
				# safe to update hostile count since we're not busy
				self.hostilecount = self.GetHostileCount()
				# update pane only if we have it open
			if self.pane:
				self.pane.Close()
 				self.pane = LocalDash(parent=uicore.layer.abovemain, name='LocalDash')
				self.pane.SetOpacity(0.5)
				if self.hostilecount == -1 or self.busy:
					self.pane.ShowMsg("<color=0xffffffff>HOSTILES: " + "<color=0xffff3700>updating...</color>")
				else:
					self.pane.ShowMsg("<color=0xffffffff>HOSTILES: " + "<color=0xffff3700>%d</color>" % self.hostilecount)
			if self.warning and (self.hostilecount > 0):
				flash = WarningFlash(parent=uicore.layer.abovemain, name='WarningFlash')
				flash.Flash()

		def GetHostileCount(self):
			# set service status to busy to avoid lock
			self.busy = True
			if self.hostilecount == -1:
				self.hostilecount = 0
			count = 0
			mlist = copy.deepcopy(self.localChannel.memberList)
			for charID in mlist:
				# if it's myself, skip it
				if charID == session.charid:
					continue
				else:
					# check cache first
					if charID in self.cache.keys():
						if self.cache[charID] < 0.5:
							# increment counter if less than friendly
							count += 1
							#msg('hostiles: %d' % count)
					# charID not in cache, we need to find out the standing the hard way
					else:
						# figure out what ID to use for myself
						myStandingID = None
						if (eve.session.allianceid):
							myStandingID = eve.session.allianceid
						else:
							myStandingID = eve.session.corpid
						standing = sm.GetService('standing').GetStanding(myStandingID, charID)
						if (standing == 0.0):
							# neutral standing could mean charID is in our alliance or corp
							corpCharInfo = sm.GetService('corp').GetInfoWindowDataForChar(charID, 1)
							corpID = corpCharInfo.corpID
							allianceID = corpCharInfo.allianceID
							if (eve.session.corpid == corpID) or ((eve.session.allianceid != None) and (eve.session.allianceid == allianceID)):
								# charID is in our alliance or corp, mark friendly in cache and skip
								self.cache[charID] = 1.0
								continue
							else:
								# charID is not in our alliance or corp, better mark hostile in cache and increment count
								self.cache[charID] = standing
								count += 1
								#msg('hostiles: %d' % count)
						elif (standing < 0.5):
							# we found a new hostile, store in cache and increment counter
							self.cache[charID] = standing
							count += 1
							#msg('hostiles: %d' % count)
						else:
							# charID is in a friendly alliance/corp or tagged friendly by alliance, store in cache and skip
							self.cache[charID] = standing
							continue
			# we're done, no longer busy
			self.busy = False
			return count

		def Open(self):
			if self.pane:
				return
			self.initPane()

		def Close(self):
			self.Reset()

		def Reset(self):
			if self.pane:
				self.pane.Close()
				del self.pane
				self.pane = None

		def WarningOn(self):
			self.warning = True

		def WarningOff(self):
			self.warning = False

		def CleanUp(self):
			del self.alive
			self.alive = None
			self.Reset()

	class WarningFlash(uicls.Container):
			__guid__ = 'uicls.Warning'

			def ApplyAttributes(self, attributes):
				self.scope = 'station_inflight'
				self.frame = None
				uicls.Container.ApplyAttributes(self, attributes)

			def Flash(self, duration = 500):
				self.SetAlign(uiconst.CENTERTOP)
				self.SetSize(uicore.desktop.width, uicore.desktop.height)
				self.frame = uicls.Frame(parent=self, color=(1.0, 0.25, 0.25, 0.25), frameConst=uiconst.FRAME_FILLED_CORNER1, state=uiconst.UI_DISABLED)
				self.SetPosition(0, 0)
				self.state = uiconst.UI_DISABLED
				uiutil.SetOrder(self, 0)
				blue.pyos.synchro.Sleep(duration)
				self.Close()


	class LocalDash(uicls.Container):
			__guid__ = 'uicls.LocalDash'

			def ApplyAttributes(self, attributes):
				self.scope = 'station_inflight'
				self.message = None
				#self.message2 = None
				uicls.Container.ApplyAttributes(self, attributes)

			def Prepare_Text_(self):
				self.message = uicls.Label(text='', parent=self, left=0, top=4, autowidth=False, width=100, fontsize=12, state=uiconst.UI_DISABLED)
				#self.message2 = uicls.Label(text='', parent=self, left=0, top=16, autowidth=False, width=200, fontsize=12, state=uiconst.UI_DISABLED)

			def Prepare_Underlay_(self):
			    border = uicls.Frame(parent=self, frameConst=uiconst.FRAME_BORDER1_CORNER1, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25))
			    frame = uicls.Frame(parent=self, color=(0.0, 0.0, 0.0, 0.75), frameConst=uiconst.FRAME_FILLED_CORNER1, state=uiconst.UI_DISABLED)

			def ShowMsg(self, text1):
			    if self.message is None:
			        self.Prepare_Text_()
			        self.Prepare_Underlay_()
				self.message.text = '<center>' + text1
				#self.message2.text = '<center>' + text2
				self.SetAlign(uiconst.CENTERTOP)
				self.SetSize(100, 20)
				offset = sm.GetService('window').GetCameraLeftOffset(self.width, align=uiconst.CENTERTOP, left=0)
				self.SetPosition(offset, 5)
				self.state = uiconst.UI_DISABLED
				uiutil.SetOrder(self, 0)



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

	@safetycheck
	def WarnIt(*args):
		bottomline = sm.GetService('neocom').bottomline
		if bottomline and hasattr(bottomline, 'alive') and bottomline.alive:
			if bottomline.warning:
				bottomline.WarningOff()
				msg('Warning toggled OFF!')
			else:
				bottomline.WarningOn()
				msg('Warning toggled ON!')

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

	@safetycheck
	def ReportInfo(*args):
		absvc = sm.GetService('addressbook')
		bookmarks = absvc.GetBookmarks()
		bmsInSystem = list()
		for each in bookmarks.itervalues():
			if each.locationID == session.solarsystemid:
				bmsInSystem.append(each)
		msg('bmsInSystem length is: %d' % (len(bmsInSystem)))

	@safetycheck
	def TryWarpToSafe(*args):
		absvc = sm.GetService('addressbook')
		bookmarks = absvc.GetBookmarks()
		bms = list()
		for each in bookmarks.itervalues():
			if each.locationID == session.solarsystemid:
				bms.append(each)
		safeBM = None
		for bm in bms:
			memo = absvc.UnzipMemo(bm.memo)[0]
			if memo == 'safePoS':
				safeBM = bm
		if safeBM == None:
			msg('error finding safePoS')
			return
		if session.solarsystemid and session.shipid:
			bp = sm.GetService('michelle').GetRemotePark()
			if bp:
 	 			bp.WarpToStuff('bookmark', safeBM.bookmarkID, minRange=0.0, fleet=False)
		    	sm.StartService('space').WarpDestination(None, safeBM.bookmarkID, None)


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
		btn.sr.icon.LoadIcon('11_01')
		createBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=833)
		btn.OnClick = DestroyIt
		btn.hint = "Kill LocalWatch service"
		btn.sr.icon.LoadIcon('11_02')
		destroyBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=866)
		btn.OnClick = ToggleIt
		btn.hint = "Show LocalDash"
		btn.sr.icon.LoadIcon('11_03')
		killBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=899)
		btn.OnClick = WarnIt
		btn.hint = "Toggle flash warning"
		btn.sr.icon.LoadIcon('11_04')
		warnBtn = btn


	except:
		msg('bad inject')

except:
	pass
