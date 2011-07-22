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
	from math import pi, cos, sin, sqrt
	from foo import Vector3
	from mapcommon import SYSTEMMAP_SCALE
	import functools
	import uiconst
	import uicls
	
	import listentry
	import state
	
	try:
		old_apply_attributes
	except NameError:
		old_apply_attributes = form.Scanner.ApplyAttributes
		
	try:
		old_remove_ball = sm.GetService('michelle').GetBallpark().RemoveBall

		form.Scanner.ballsToTheWall = list()
	except:
		sm.GetService('gameui').Say("exception1")
	try:
		localChannel = None
		for channelID in sm.GetService('LSC').channels.keys():
			channel = sm.GetService('LSC').channels[channelID]
			if (channel.window and ((type(channel.channelID) is tuple) and (channel.channelID[0][0] == 'solarsystemid2'))):
				localChannel = channel
	except:
		sm.GetService('gameui').Say("exception2")

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
	def UpdateCount():
		#sm.GetService('gameui').Say('Hostile count updated!')
		count = (blueCount, neutCount, orangeCount, redCount, )= GetHostileCount()
		sm.GetService('gameui').Say('Blue[%d] Neut[%d] Orange[%d] Red[%d]' % count)
		hostilecount = neutCount + orangeCount + redCount
		labeltext = ('HOSTILES [%d]' % hostilecount)
		hostileLabel.text = labeltext
		hostileLabel2.text = labeltext
		
	@safetycheck
	def GetHostileCount():
		'''
		localChannel = None
		for channelID in sm.GetService('LSC').channels.keys():
			channel = sm.GetService('LSC').channels[channelID]
			if (channel.window and ((type(channel.channelID) is tuple) and (channel.channelID[0][0] == 'solarsystemid2'))):
				localChannel = channel
		'''
		mlist = localChannel.memberList
		redCount = 0
		blueCount = 0
		orangeCount = 0
		neutCount = 0
		try:
			for charID in mlist.keys():
				standing = sm.GetService('standing').GetStanding(eve.session.charid, charID)
				if (standing >= 0.5):
					blueCount = blueCount + 1
				elif (standing < 0.5 and standing >= 0.0):
					neutCount = neutCount + 1
				elif (standing < 0.0 and standing > -1.0):
					orangeCount = orangeCount + 1
				else:
					redCount = redCount + 1
		except:
			sm.GetService('gameui').Say('oops')
		#sm.GetService('gameui').Say('Hostiles in local: %g' % (hostileCount, ))
		count = (blueCount, neutCount, orangeCount, redCount, )
		return count
		

	@safetycheck
	def MyUpdateCaption(self, startingup = 0, localEcho = 0):
		if self.channelInitialized:
			label = chat.GetDisplayName(self.channelID).split('\\')[-1]
			label.replace('conversation', 'conv.')
			label.replace('channel', 'ch.')
			memberCount = sm.GetService('LSC').GetMemberCount(self.channelID)
			if (memberCount != self.memberCount):
				self.memberCount = memberCount
			if ((type(self.channelID) == types.IntType) or (self.channelID[0] not in ('global', 'regionid', 'constellationid'))):
				if (self.memberCount > 2):
					label += (' [%d] [%d]' % (self.memberCount, form.Scanner.GetHostileCount(), ))
			self.SetCaption(label)
			

	'''
	try:
		form.LSCChannel.UpdateCaption = MyUpdateCaption
	except:
		sm.GetService('gameui').Say('uh-oh')
	'''
		
	@safetycheck
	def TryGetInvItem(self, itemID):
		if (eve.session.shipid is None):
			return 
		ship = eve.GetInventoryFromId(eve.session.shipid)
		if ship:
			for invItem in ship.List():
				if (invItem.itemID == itemID):
					return invItem
	
	form.Scanner.TryGetInvItem = TryGetInvItem
	
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
			'''
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
			'''
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
	
	form.Scanner.GetNearbyItem = GetNearbyItem

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
	def MyRemoveBall(ball, *args):
		form.Scanner.ballsToTheWall.append(ball)
		return
	
	@safetycheck
	def WatchWarpOff(self, *args):		
		if uicore.uilib.Key(uiconst.VK_SHIFT):
			sm.GetService('michelle').GetBallpark().RemoveBall = MyRemoveBall
			return

		elif uicore.uilib.Key(uiconst.VK_CONTROL):
			return
		
		sm.GetService('michelle').GetBallpark().RemoveBall = old_remove_ball
		for ball in form.Scanner.ballsToTheWall:
			sm.GetService('michelle').GetBallpark().RemoveBall(ball)
		form.Scanner.ballsToTheWall = list()
		form.OverView.UpdateAll	

		
	
	form.Scanner.WatchWarpOff = WatchWarpOff  
	
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
					if result.groupName == None:
						result.groupName = cfg.invgroups.Get(result.groupID).name
				elif isinstance(result.data, float):
					dist = result.data
					certainty = min(0.9999, certainty)
				else:
					dist = (result.data.point - myPos).Length()
					certainty = min(0.9999, certainty)
					if result.groupName == None:
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
	def MyApplyAttributes(self, attributes):
		old_apply_attributes(self, attributes)
		
		self.sr.destroyBtn.Close()
		
		wnd = sm.GetService('window').GetWindow('selecteditemview', decoClass=form.ActiveItem)
		if wnd:
			wnd.SelfDestruct()
		if session.solarsystemid:
			sm.GetService('tactical').InitSelectedItem()
		
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
		btn.hint = "SAVE/SEND TO LOCATION1"
		btn.sr.icon.LoadIcon('77_21')
		self.sr.GoToBtn = btn

		btn = uix.GetBigButton(32, self.sr.systemTopParent, left=302)
		btn.OnClick = self.GoToLocations2
		btn.hint = "SAVE/SEND TO LOCATION2"
		btn.sr.icon.LoadIcon('77_21')
		self.sr.GoToBtn = btn

		btn = uix.GetBigButton(32, self.sr.systemTopParent, left=334)
		btn.OnClick = self.GoToLocations3
		btn.hint = "SAVE/SEND TO LOCATION3"
		btn.sr.icon.LoadIcon('77_21')
		self.sr.GoToBtn = btn
		
		btn = uix.GetBigButton(32, eve.LocalSvc("window").GetWindow("selecteditemview"), left=315, top=20)
		btn.OnClick = self.WatchWarpOff
		btn.hint = "Watch!"
		btn.sr.icon.LoadIcon('44_03')
		self.sr.WatchBtn = btn
		
		btn = uix.GetBigButton(32, eve.LocalSvc("window").GetWindow("selecteditemview"), left=315, top=55)
		btn.OnClick = self.GetNearbyItem
		btn.hint = "Show nearby item"
		btn.sr.icon.LoadIcon('77_21')
		self.sr.nearbyBtn = btn



	form.Scanner.ApplyAttributes = MyApplyAttributes
	
	try:
		hostileLabel = uicls.Label(text='', parent=localChannel.window, left=90, top=3, fontsize=11, mousehilite=1, letterspace=1, state=uiconst.UI_NORMAL)
		hostileLabel2 = uicls.Label(text='', parent=localChannel.window, left=90, top=3, fontsize=11, mousehilite=1, letterspace=1, state=uiconst.UI_NORMAL)
		hostileLabel.OnClick = (UpdateCount, )
		hostileLabel.hint = "Click me!"
		hostileLabel.strong = 1
		hostileLabel2.OnClick = (UpdateCount, )
		hostileLabel2.hint = "Click me!"
		hostileLabel2.strong = 1
		UpdateCount()
	except:
		sm.GetService('gameui').Say("exception3")

except:
	print "ProbeHelper broken."
