try:
	import const
	import form
	import uix
	import util
	import xtriui
	import uiutil
	import uiconst
	import blue
	import base
	import sys
	from traceback import format_exception
	import functools
	import localization
	import localizationUtil

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
					print "exception in safetycheck"
		return wrapper

	@safetycheck
	def MyAddTab(self):
		ret = uiutil.NamePopup(localization.GetByLabel('UI/Overview/AddTab'), localization.GetByLabel('UI/Overview/TypeInLabel'), maxLength=15)
		if not ret:
			return
		numTabs = 10
		tabsettings = settings.user.overview.Get('tabsettings', {})
		if len(tabsettings) >= numTabs:
			eve.Message('TooManyTabs', {'numTabs': numTabs})
			return
		if len(tabsettings) == 0:
			newKey = 0
		else:
			newKey = max(tabsettings.keys()) + 1
		oldtabsettings = tabsettings
		tabsettings[newKey] = {'name': ret,
		 'overview': None,
		 'bracket': None}
		if self.destroyed:
			return
		self.OnOverviewTabChanged(tabsettings, oldtabsettings)

	form.OverView.AddTab = MyAddTab

except:
	pass