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
			self.alive = base.AutoTimer(5000, self.Update)
			sm.GetService('gameui').Say('MyService inited')
			self.pane = None

		def initPane(self):
			self.pane = sm.GetService('window').GetWindow("Temp", create=1)
			self.pane.windowID = "TempWindow"
			btn = uix.GetBigButton(50, self.pane.sr.main, left=0)
			btn.OnClick = ReportLocal
			btn.hint = "Report Local"
			btn.sr.icon.LoadIcon('44_02')
			self.pane.sr.FocusBtn = btn

			btn = uix.GetBigButton(50, self.pane.sr.main, left=50)
			btn.OnClick = SetReport
			btn.hint = "Set Report Channel"
			btn.sr.icon.LoadIcon('44_01')
			self.pane.sr.Focus2Btn = btn

		def Update(self):
			# add kill check in the future
			pass

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

	@safetycheck
	def CreateIt(*args):
		#create an instance of something
		bottomline = sm.GetService('neocom').bottomline
		if bottomline and hasattr(bottomline, "alive") and bottomline.alive:
			msg('MyService already running!')
		else:
			sm.GetService('neocom').bottomline = MyService()

	@safetycheck
	def DestroyIt(*args):
		#destroy an instance of something
		del sm.GetService('neocom').bottomline
		sm.GetService('neocom').bottomline = None
		msg('MyService killed!')

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
		btn.hint = ""
		btn.sr.icon.LoadIcon('11_01')
		createBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=833)
		btn.OnClick = DestroyIt
		btn.hint = ""
		btn.sr.icon.LoadIcon('11_02')
		destroyBtn = btn

		btn = uix.GetBigButton(32, neocomwnd, top=866)
		btn.OnClick = ToggleIt
		btn.hint = ""
		btn.sr.icon.LoadIcon('11_03')
		killBtn = btn


	except:
		msg('bad inject')

except:
	pass
