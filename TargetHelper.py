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
	def MyStartup(self, slimItem):
		target_old_startup(self, slimItem)
		self.underlay = uicls.Frame(parent=self, color=(1.0, 1.0, 1.0, 0.25), frameConst=uiconst.FRAME_FILLED_CORNER1, state=uiconst.UI_DISABLED)

	try:
		target_old_startup
	except NameError:
		target_old_startup = xtriui.Target.Startup

	try:
		xtriui.Target.Startup = MyStartup
	except:
		msg('terrible things happened')

except:
	pass