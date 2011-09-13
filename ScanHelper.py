try:
	import uix
	import uiutil
	import mathUtil
	import xtriui
	import uthread
	import form
	import blue
	import util
	import trinity
	import service
	import listentry
	import base
	import math
	import sys
	import geo2
	import maputils
	import copy
	from math import pi, cos, sin, sqrt
	from foo import Vector3
	from mapcommon import SYSTEMMAP_SCALE
	from traceback import format_exception
	import functools
	import uiconst
	import uicls
	import listentry
	import state

	try:
		Scanner_old_apply_attributes
	except NameError:
		Scanner_old_apply_attributes = form.Scanner.ApplyAttributes

	try:
		form.Scanner.distData = dict()
	except:
		sm.GetService('gameui').Say("bad syntax")

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
		ret = uix.NamePopup(mls.UI_CMD_ADD_TAB, mls.UI_INFLIGHT_TYPELABEL, maxLength=15)
		if not ret:
			return
		numTabs = 8
		tabsettings = settings.user.overview.Get('tabsettings', {})
		if (len(tabsettings) >= numTabs):
			eve.Message('TooManyTabs', {'numTabs': numTabs})
			return
		if (len(tabsettings) == 0):
			newKey = 0
		else:
			newKey = (max(tabsettings.keys()) + 1)
		oldtabsettings = tabsettings
		tabsettings[newKey] = {'name': ret['name'],
		 'overview': None,
		 'bracket': None}
		if self.destroyed:
			return
		self.OnOverviewTabChanged(tabsettings, oldtabsettings)

	form.OverView.AddTab = MyAddTab

	@safetycheck
	def ContractProbes(self, *args):
		scanSvc = sm.GetService("scanSvc")
		probeData = [(k,v) for (k,v) in scanSvc.GetProbeData().iteritems() if v.state == const.probeStateIdle]
		if len(probeData) == 0:
			return

		avg = sum( (v.destination for (k,v) in probeData), Vector3() ) / len(probeData)
		min_range = min( v.rangeStep for (k,v) in probeData )
		if (min_range <= 1):
			return

		for (k,v) in probeData:
			destination = (v.destination + avg)/2
			scanSvc.SetProbeDestination(k, destination)
			scanSvc.SetProbeRangeStep(k, v.rangeStep - 1)

		self.UpdateProbeSpheres()

	form.Scanner.ContractProbes = ContractProbes

	@safetycheck
	def ExpandProbes(self, *args):
		scanSvc = sm.GetService("scanSvc")
		probeData = [(k,v) for (k,v) in scanSvc.GetProbeData().iteritems() if v.state == const.probeStateIdle]
		if len(probeData) == 0:
			return

		avg = sum( (v.destination for (k,v) in probeData), Vector3() ) / len(probeData)
		max_range = max( v.rangeStep for (k,v) in probeData )
		if (max_range >= const.scanProbeNumberOfRangeSteps):
			return

		for (k,v) in probeData:
			destination = (2 * v.destination) - avg
			scanSvc.SetProbeDestination(k, destination)
			scanSvc.SetProbeRangeStep(k, v.rangeStep + 1)

		self.UpdateProbeSpheres()

	form.Scanner.ExpandProbes = ExpandProbes


	@safetycheck
	def SendProbes(self, *args):
		selected = self.sr.resultscroll.GetSelected()
		points = []
		target = Vector3(0,0,0)
		target2 = Vector3(0,0,0)
		try:
			itemid = eve.LocalSvc("window").GetWindow("selecteditemview").itemIDs[0]
			ball= eve.LocalSvc("michelle").GetBallpark().GetBall(itemid)
			target2= Vector3(ball.x,ball.y, ball.z)
		except:
			sm.GetService('gameui').Say("No active item, going to scan results")
		if selected:
			for sel in selected:
				data = sel.result.data

				if isinstance(data, float):
					data = sel.result.pos

				if not isinstance(data, Vector3):
					data = data.point

				points.append(data)
			csum = 0
			for p in points:
				target += p
			target /= len(points)

		if uicore.uilib.Key(uiconst.VK_SHIFT) or (not selected):
			target = target2

		scanSvc = sm.GetService("scanSvc")
		probeData = [(k,v) for (k,v) in scanSvc.GetProbeData().iteritems() if v.state == const.probeStateIdle]
		if len(probeData) == 0:
			return

		avg = sum( (v.destination for (k,v) in probeData), Vector3() ) / len(probeData)

		for (k,v) in probeData:
			destination = target + v.destination - avg
			scanSvc.SetProbeDestination(k, destination)

		self.UpdateProbeSpheres()

	form.Scanner.SendProbes = SendProbes

	@safetycheck
	def CustomPosition(self, *args):
		scanSvc = sm.GetService("scanSvc")
		probeData = [(k,v) for (k,v) in scanSvc.GetProbeData().iteritems() if v.state == const.probeStateIdle]
		if len(probeData) == 0:
			return
		avg = sum( (v.destination for (k,v) in probeData), Vector3() ) / len(probeData)
		probePos = [
			[0, 0, 0],
			[-4000, 0, 0],
			[4000, 0, 0],
			[0, 0, -4000],
			[0, 0, 4000],
			[0, -4000, 0],
			[0, 4000, 0],
			[0, 0, 0],
			]
		i = 0
		for (k,v) in probeData:
			destination = Vector3(probePos[i][0], probePos[i][1], probePos[i][2]) + avg
			scanSvc.SetProbeDestination(k, destination)
			i += 1
		self.UpdateProbeSpheres()

	form.Scanner.CustomPosition = CustomPosition

	@safetycheck
	def SaveLoadProbePositions(self, *args):
		scanSvc = sm.GetService("scanSvc")
		probeData = [(k,v) for (k,v) in scanSvc.GetProbeData().iteritems() if v.state == const.probeStateIdle]
		if len(probeData) == 0:
			return

		settingsName = 'ProbePositons2' if uicore.uilib.Key(uiconst.VK_CONTROL) else 'ProbePositions'

		if uicore.uilib.Key(uiconst.VK_SHIFT):
			settings.public.ui.Set(settingsName, [(v.destination, v.rangeStep) for (k,v) in probeData])
			return

		pos = settings.public.ui.Get(settingsName, [])
		if( pos == [] ):
			return

		for ((probekey, probevalue), (dest,rstep)) in zip(probeData, pos):
			scanSvc.SetProbeDestination(probekey, dest)
			scanSvc.SetProbeRangeStep(probekey, rstep)
		self.UpdateProbeSpheres()

	form.Scanner.SaveLoadProbePositions = SaveLoadProbePositions

	@safetycheck
	def GoToLocations(self, *args):
		selected = self.sr.resultscroll.GetSelected()
		scanSvc = sm.GetService("scanSvc")
		probeData = [(k,v) for (k,v) in scanSvc.GetProbeData().iteritems() if v.state == const.probeStateIdle]
		avg = sum( (v.destination for (k,v) in probeData), Vector3() ) / len(probeData)
		if len(probeData) == 0:
			return
		points = []
		try:
			for sel in selected:
				data = sel.result.data

				if isinstance(data, float):
					data = sel.result.pos

				if not isinstance(data, Vector3):
					data = data.point

				points.append(data)
			target = Vector3(0,0,0)
			csum = 0
			for p in points:
				target += p
			target /= len(points)
		except:
			stub = "stubmsg"

		if uicore.uilib.Key(uiconst.VK_SHIFT):
			settings.public.ui.Set("Locations%d"%(args[0]), target)
			return
		elif uicore.uilib.Key(uiconst.VK_CONTROL):
			settings.public.ui.Set("Locations%d"%(args[0]), avg)
			return
		else:
			target = settings.public.ui.Get("Locations%d"%(args[0]))

		for (k,v) in probeData:
			destination = target + v.destination - avg
			scanSvc.SetProbeDestination(k, destination)

		self.UpdateProbeSpheres()

	form.Scanner.GoToLocations = GoToLocations

	@safetycheck
	def GoToLocations1(self, *args):
		GoToLocations(self, 1, args)

	form.Scanner.GoToLocations1 = GoToLocations1

	@safetycheck
	def GoToLocations2(self, *args):
		GoToLocations(self, 2, args)

	form.Scanner.GoToLocations2 = GoToLocations2

	@safetycheck
	def GoToLocations3(self, *args):
		GoToLocations(self, 3, args)

	form.Scanner.GoToLocations3 = GoToLocations3

	@safetycheck
	def MyLoadResultList(self):
		if ((self is None) or self.destroyed):
			return
		scanSvc = sm.GetService('scanSvc')
		currentScan = scanSvc.GetCurrentScan()
		scanningProbes = scanSvc.GetScanningProbes()
		results = scanSvc.GetScanResults()
		if self.destroyed:
			return
		self.CleanupResultShapes()
		resultlist = []
		if (currentScan and (blue.os.TimeDiffInMs(currentScan.startTime) < currentScan.duration)):
			data = util.KeyVal()
			data.header = mls.UI_GENERIC_ANALYZING
			data.startTime = currentScan.startTime
			data.duration = currentScan.duration
			resultlist.append(listentry.Get('Progress', data=data))
		elif (scanningProbes and (session.shipid not in scanningProbes)):
			data = util.KeyVal()
			data.label = mls.UI_GENERIC_SCAN_WAITING_FOR_PROBES
			data.hideLines = 1
			resultlist.append(listentry.Get('Generic', data=data))
		elif results:
			bp = sm.GetService('michelle').GetBallpark(doWait=True)
			if (bp is None):
				return
			ego = bp.balls[bp.ego]
			myPos = Vector3(ego.x, ego.y, ego.z)
			for result in results:
				if (result.id in scanSvc.resultsIgnored):
					continue
				if ((self.currentFilter is not None) and (len(self.currentFilter) > 0)):
					if (result.certainty >= const.probeResultGood):
						if (result.groupID not in self.currentFilter):
							continue
					else:
						if (result.scanGroupID not in self.activeScanGroupInFilter):
							continue
				id = result.id
				probeID = result.probeID
				certainty = result.certainty
				typeID = result.Get('typeID', None)
				result.typeName = None
				result.groupName = None
				result.scanGroupName = self.scanGroups[result.scanGroupID]
				if (certainty >= const.probeResultGood):
					explorationSite = (result.groupID in (const.groupCosmicAnomaly, const.groupCosmicSignature))
					if explorationSite:
						result.groupName = self.GetExplorationSiteType(result.strengthAttributeID)
					else:
						result.groupName = cfg.invgroups.Get(result.groupID).name
					if (certainty >= const.probeResultInformative):
						if explorationSite:
							result.typeName = result.dungeonName
						else:
							result.typeName = cfg.invtypes.Get(typeID).name
				if isinstance(result.data, Vector3):
					dist = (result.data - myPos).Length()
					if result.groupName == None and result.groupID:
						result.groupName = cfg.invgroups.Get(result.groupID).name
				elif isinstance(result.data, float):
					dist = result.data
					certainty = min(0.9999, certainty)
				else:
					dist = (result.data.point - myPos).Length()
					certainty = min(0.9999, certainty)
					if result.groupName == None and result.groupID:
						result.groupName = cfg.invgroups.Get(result.groupID).name
				texts = [result.id,
				 result.scanGroupName,
				 (result.groupName or ''),
				 (result.typeName or ''),
				 (('%1.2f' % (min(1.0, certainty) * 100)) + '%'),
				 util.FmtDist(dist)]
				sortdata = [result.id,
				 result.scanGroupName,
				 (result.groupName or ''),
				 (result.typeName or ''),
				 (min(1.0, certainty) * 100),
				 dist]
				data = util.KeyVal()
				data.texts = texts
				data.sortData = sortdata
				data.columnID = 'probeResultGroupColumn'
				data.result = result
				data.GetMenu = self.ResultMenu
				resultlist.append(listentry.Get('ColumnLine', data=data))

			resultlist = listentry.SortColumnEntries(resultlist, 'probeResultGroupColumn')
			data = util.KeyVal()
			data.texts = [mls.UI_GENERIC_ID,
			 mls.UI_GENERIC_SCAN_GROUP,
			 mls.UI_GENERIC_GROUP,
			 mls.UI_GENERIC_TYPE,
			 mls.UI_GENERIC_SIGNALSTRENGTH,
			 mls.UI_GENERIC_DISTANCE]
			data.columnID = 'probeResultGroupColumn'
			data.editable = True
			data.showBottomLine = True
			data.selectable = False
			data.hilightable = False
			resultlist.insert(0, listentry.Get('ColumnLine', data=data))
			listentry.InitCustomTabstops(data.columnID, resultlist)
		if not resultlist:
			data = util.KeyVal()
			data.label = mls.UI_GENERIC_NO_SCAN_RESULT
			data.hideLines = 1
			resultlist.append(listentry.Get('Generic', data=data))
		resultlist.append(listentry.Get('Line', data=util.KeyVal(height=1)))
		self.sr.resultscroll.Load(contentList=resultlist)
		self.sr.resultscroll.ShowHint('')
		self.HighlightGoodResults()

	form.Scanner.LoadResultList = MyLoadResultList

	@safetycheck
	def Nuke(self, *args):
		self.SendProbes (*args)
		self.Analyze(*args)

	form.Scanner.Nuke = Nuke

	@safetycheck
	def FlushDistData(self, *args):
		form.Scanner.distData.clear()
		sm.GetService('gameui').Say("Distance data flushed")

	form.Scanner.FlushDistData = FlushDistData

	@safetycheck
	def GetGetGet(self, *args):
		(config, value,) = args
		self.dir_rangeinput.SetValue(value*14959800)
		if hasattr(self, 'dir_rangeinput2'):
			self.dir_rangeinput2.SetValue(value*14959800)

	form.Scanner.GetGetGet = GetGetGet

	@safetycheck
	def SetSetSet(self, *args):
		uthread.new(self.DirectionSearch)

	form.Scanner.SetSetSet = SetSetSet

	@safetycheck
	def NewScan(self, *args):
		if ((self is None) or (self.destroyed or self.busy)):
			return
		self.busy = True
		self.ShowLoad()
		self.scanresult = []
		if self.sr.useoverview.checked:
			filters = sm.GetService('tactical').GetValidGroups()
		camera = sm.GetService('sceneManager').GetRegisteredCamera(None, defaultOnActiveCamera=True)
		if not camera:
			self.busy = False
			self.HideLoad()
			raise RuntimeError('No camera found?!')
		rot = camera.rotationAroundParent
		vec = trinity.TriVector(0.0, 0.0, 1.0)
		vec.TransformQuaternion(rot)
		vec.Normalize()
		rnge = self.dir_rangeinput.GetValue()
		result = None
		try:
			result = sm.GetService('scanSvc').ConeScan(self.scanangle, (rnge * 1000), vec.x, vec.y, vec.z)
		except (UserError, RuntimeError), err:
			result = None
			self.busy = False
			self.HideLoad()
			#raise err
			return
		settings.user.ui.Set('dir_scanrange', rnge)
		if result:
			bp = sm.GetService('michelle').GetBallpark()
			if bp:
				for rec in result:
					if self.sr.useoverview.checked:
						if (rec.groupID not in filters):
							continue
					if (rec.id in bp.balls):
						self.scanresult.append([None,
						 bp.balls[rec.id],
						 rec])
					else:
						self.scanresult.append([None,
						 None,
						 rec])

		self.NewShowResult()
		self.busy = False
		self.HideLoad()

	form.Scanner.DirectionSearch = NewScan

	@safetycheck
	def NewShowResult(self, *args):
		self.listtype = 'location'
		scrolllist = []
		if (self.scanresult and len(self.scanresult)):
			myball = None
			ballpark = sm.GetService('michelle').GetBallpark()
			if ballpark:
				myball = ballpark.GetBall(eve.session.shipid)
			prime = []
			for result in self.scanresult:
				(slimItem, ball, celestialRec,) = result
				if ((not slimItem) and celestialRec):
					prime.append(celestialRec.id)

			if prime:
				cfg.evelocations.Prime(prime)
			sortdist = []
			for (slimItem, ball, celestialRec,) in self.scanresult:
				if ((self is None) or self.destroyed):
					return
				dist = 0
				if slimItem:
					typeinfo = cfg.invtypes.Get(slimItem.typeID)
					entryname = hint = uix.GetSlimItemName(slimItem)
					itemID = slimItem.itemID
					typeID = slimItem.typeID
					if not entryname:
						entryname = typeinfo.Group().name
				elif celestialRec:
					typeinfo = cfg.invtypes.Get(celestialRec.typeID)
					if (typeinfo.groupID == const.groupHarvestableCloud):
						entryname = hint = ('%s (%s)' % (mls.UI_GENERIC_HARVESTABLE_CLOUD, typeinfo.name))
					elif (typeinfo.categoryID == const.categoryAsteroid):
						entryname = hint = ('%s (%s)' % (mls.UI_GENERIC_ASTEROID, typeinfo.name))
					else:
						entryname = hint = cfg.evelocations.Get(celestialRec.id).name
					if not entryname:
						entryname = hint = typeinfo.name
					itemID = celestialRec.id
					typeID = celestialRec.typeID
				else:
					continue
				if (ball is not None):
					dist = ball.surfaceDist
					diststr = util.FmtDist(dist, maxdemicals=1)
					finaldiststr = diststr
				else:
					maxDist = settings.user.ui.Get('dir_scanrange')*1000
					dist = maxDist
					lastDist = None
					dictName = "%d" % itemID
					try:
						lastDist = form.Scanner.distData[dictName]
					except:
						lastDist = maxDist
					if dist > lastDist:
						dist = lastDist
					else:
						form.Scanner.distData[dictName] = dist
					diststr = util.FmtDist(dist, maxdemicals=1)
					finaldiststr = '~%s' % diststr
				groupID = cfg.invtypes.Get(typeID).groupID
				if not (eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD)):
					if (groupID == const.groupCloud):
						continue
				hint = entryname
				data = util.KeyVal()
				data.label = ('%s (%d)<t>%s<t>%s' % (entryname, (itemID%1000000000000),
				 typeinfo.name,
				 finaldiststr))
				data.Set(('sort_%s' % mls.UI_GENERIC_DISTANCESHORT), dist)
				data.columnID = 'directionalResultGroupColumn'
				data.result = result
				data.itemID = itemID
				data.typeID = typeID
				data.GetMenu = self.DirectionalResultMenu
				scrolllist.append(listentry.Get('Generic', data=data))
				blue.pyos.BeNice()

		if not len(scrolllist):
			data = util.KeyVal()
			data.label = mls.UI_GENERIC_SCAN_DIRECTIONAL_NORESULT
			data.hideLines = 1
			scrolllist.append(listentry.Get('Generic', data=data))
			headers = []
		else:
			headers = [mls.UI_GENERIC_NAME,
			 mls.UI_GENERIC_TYPE,
			 mls.UI_GENERIC_DISTANCESHORT]
		self.sr.dirscroll.Load(contentList=scrolllist, headers=headers)

	form.Scanner.NewShowResult = NewShowResult

	@safetycheck
	def MyApplyAttributes(self, attributes):
		Scanner_old_apply_attributes(self, attributes)

		self.sr.destroyBtn.Close()

		btn = uix.GetBigButton(32, self.sr.systemTopParent, left=108)
		btn.OnClick = self.SaveLoadProbePositions
		btn.hint = "SHIFT-CLICK TO SAVE PROBES, CLICK TO LOAD PROBES"
		btn.sr.icon.LoadIcon('44_03')
		self.sr.saveloadBtn = btn

		btn = uix.GetBigButton(32, self.sr.systemTopParent, left=152)
		btn.OnClick = self.ContractProbes
		btn.hint = "CONTRACT PROBES"
		btn.sr.icon.LoadIcon('44_43')
		self.sr.contractBtn = btn

		btn = uix.GetBigButton(32, self.sr.systemTopParent, left=184)
		btn.OnClick = self.ExpandProbes
		btn.hint = "EXPAND PROBES"
		btn.sr.icon.LoadIcon('44_44')
		self.sr.expandBtn = btn

		btn = uix.GetBigButton(32, self.sr.systemTopParent, left=228)
		btn.OnClick = self.SendProbes
		btn.hint = "SEND PROBES TO SELECTED RESULT"
		btn.sr.icon.LoadIcon('44_59')
		self.sr.sendBtn = btn

		btn = uix.GetBigButton(32, self.sr.systemTopParent, left=270)
		btn.OnClick = self.GoToLocations1
		btn.hint = "SEND/SAVE TO SLOT1"
		btn.sr.icon.LoadIcon('77_21')
		self.sr.GoTo1Btn = btn

		btn = uix.GetBigButton(32, self.sr.systemTopParent, left=302)
		btn.OnClick = self.GoToLocations2
		btn.hint = "SEND/SAVE TO SLOT2"
		btn.sr.icon.LoadIcon('77_21')
		self.sr.GoTo2Btn = btn

		btn = uix.GetBigButton(32, self.sr.systemTopParent, left=334)
		btn.OnClick = self.GoToLocations3
		btn.hint = "SEND/SAVE TO SLOT3"
		btn.sr.icon.LoadIcon('77_21')
		self.sr.GoTo3Btn = btn

		btn = uix.GetBigButton(32, self.sr.systemTopParent, left=367)
		btn.OnClick = self.CustomPosition
		btn.hint = "Custom Probe Config"
		btn.sr.icon.LoadIcon('77_21')
		self.sr.GoToXBtn = btn

		btn = uix.GetBigButton(40, self.sr.systemTopParent, left=400)
		btn.OnClick = self.Nuke
		btn.hint = "Evil!"
		btn.sr.icon.LoadIcon('44_59')
		self.sr.TwoInOneBtn = btn

		btn = uix.GetBigButton(32, self.sr.useoverview.parent.parent, left=250 )
		btn.OnClick = self.FlushDistData
		btn.hint = "Flush distance data"
		btn.sr.icon.LoadIcon('44_03')
		self.sr.flushBtn = btn

		dslider = uix.GetSlider('slider', self.sr.useoverview.parent.parent, 'scandist', 1, 14.4, 'Range', '', uiconst.TOPRIGHT, 150, 18, 0, 15, getvaluefunc=self.GetGetGet, endsliderfunc=self.SetSetSet, increments=(1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5,5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.4), underlay=0)

		self.dir_rangeinput2 = uicls.SinglelineEdit(name='edit2', parent=self.sr.useoverview.parent.parent, ints=(1, None), align=uiconst.TOPRIGHT, pos=(5, 36, 78, 0), maxLength=(len(str(sys.maxint))*2))
		self.dir_rangeinput2.SetValue(settings.user.ui.Get('dir_scanrange', 1000))
		self.dir_rangeinput2.OnReturn = self.DirectionSearch



	form.Scanner.ApplyAttributes = MyApplyAttributes


except:
	print "ProbeHelper broken."
