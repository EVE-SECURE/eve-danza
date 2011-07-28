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

	try:
		form.Scanner.localChannel = None
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

	@safetycheck
	def DoIt(*args):
		try:
			count = 0
			while(count<10):
				blue.pyos.synchro.Sleep(5000)
				count = (count + 1)
				sm.GetService('gameui').Say('We have looped %g times' % count)
		except:
			sm.GetService('gameui').Say('error!')

	@safetycheck
	def factorial():
		c = 100
		T = 1
		for i in xrange(1, c):
			T *= i
		return T

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

	@safetycheck
	def ReportFocus(*args):
		try:
			form.Scanner.reportChannel = sm.GetService('focus').GetFocusChannel()
			if form.Scanner.localChannel == None:
				msg('wtfwtfwtf')
			entries = form.Scanner.localChannel.userlist.GetNodes()

			for entry in entries:
				link = ((('showinfo:' + str(entry.info.typeID)) + '//') + str(entry.charID))
				form.Scanner.reportChannel.input.AddLink(entry.info.name, link)

		except:
			msg('error2')

	try:
		pane = sm.GetService('window').GetWindow("New", create=1)
		pane.windowID = "TestWindow"
		btn = uix.GetBigButton(32, pane.sr.main, left=10)
		btn.OnClick = GetLocal
		btn.hint = "GetLocal"
		btn.sr.icon.LoadIcon('44_03')
		pane.sr.FocusBtn = btn

		btn = uix.GetBigButton(32, pane.sr.main, left=42)
		btn.OnClick = ReportFocus
		btn.hint = "ReportFocus"
		btn.sr.icon.LoadIcon('44_04')
		pane.sr.Focus2Btn = btn
	except:
		sm.GetService('gameui').Say('didn\'t work!')

except:
	print "Error"
