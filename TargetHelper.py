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
	def MyStartup(self, slimItem):
		target_old_startup(self, slimItem)
		self.underlay = uicls.Frame(parent=self, color=(1.0, 1.0, 1.0, 0.25), frameConst=uiconst.FRAME_FILLED_CORNER1, state=uiconst.UI_DISABLED)

	"""
	try:
		target_old_startup
	except NameError:
		target_old_startup = xtriui.Target.Startup

	try:
		xtriui.Target.Startup = MyStartup
	except:
		msg('terrible things happened')
	"""

	@safetycheck
	def Report():
		# do something
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


	try:
		#uthread.new(Report)
		cargo = GetCargo()
		hangar = GetHangar()
		if cargo and hangar:
			hangar.OnDropDataWithIdx(cargo.sr.scroll.GetNodes())

	except:
		msg('failed doing something')

except:
	pass