#-------------------------------------------------------------------------------
# Name:        Eve inject snippets
# Purpose:
#
# Author:      bc6
#
# Created:     08/08/2011
# Copyright:   (c) bc6 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

# UI debugger toggle
sm.GetService('cmd').OpenUIDebugger()

# #####################################################################################
# modules in svc.eveCmd
def CmdActivateHighPowerSlot1(self, *args):
    self._cmdshipui(0, 0)

def _cmdshipui(self, sidx, gidx):
    shipui = uicore.layer.shipui
    if shipui.isopen:
        shipui.OnF(sidx, gidx)

# modules in form.ShipUI
def OnF(self, sidx, gidx):
    slot = self.sr.slotsByOrder.get((gidx, sidx), None)
    if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
        uthread.new(slot.sr.module.Click)
    else:
        uthread.new(eve.Message, 'Disabled')

# Overload in svc.eveCmd
def CmdActivateHighPowerSlot1(self, *args):
	self._cmdshipui(0, 0)

def CmdOverloadHighPowerRack(self, *args):
    self._cmdoverloadrack('Hi')

def CmdOverloadMediumPowerRack(self, *args):
    self._cmdoverloadrack('Med')

def CmdOverloadLowPowerRack(self, *args):
    self._cmdoverloadrack('Lo')

def _cmdoverload(self, sidx, gidx):
    shipui = uicore.layer.shipui
    if shipui.isopen:
        shipui.OnFKeyOverload(sidx, gidx)

# Overload in form.ShipUI

def OnFKeyOverload(self, sidx, gidx):
    slot = self.sr.slotsByOrder.get((gidx, sidx), None)
    if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
        if hasattr(slot.sr.module, 'ToggleOverload'):
            uthread.new(slot.sr.module.ToggleOverload)
    else:
        uthread.new(eve.Message, 'Disabled')

# detect warping status
if self.ball.mode == destiny.DSTBALL_WARP:
	pass

# drop stuff in cargo inflight
def DropInCargo(self, dragObj, nodes):
	pass

# ###################################################################################
# set speed + direciton in svc.cmd
def CmdSetShipFullSpeed(self, *args):
    bp = sm.GetService('michelle').GetBallpark()
    rbp = sm.GetService('michelle').GetRemotePark()
    if bp is None or rbp is None:
        return
    ownBall = bp.GetBall(eve.session.shipid)
    if ownBall and rbp is not None and ownBall.mode == destiny.DSTBALL_STOP:
        if not sm.GetService('autoPilot').GetState():
            direction = trinity.TriVector(0.0, 0.0, 1.0)
            currentDirection = ownBall.GetQuaternionAt(blue.os.GetTime())
            direction.TransformQuaternion(currentDirection)
            rbp.GotoDirection(direction.x, direction.y, direction.z)
    if rbp is not None:
        rbp.SetSpeedFraction(1.0)
        sm.GetService('logger').AddText('%s %s' % (mls.UI_INFLIGHT_SPEEDCHANGEDTO, self._FormatSpeed(ownBall.maxVelocity)), 'notify')
        sm.GetService('gameui').Say('%s %s' % (mls.UI_INFLIGHT_SPEEDCHANGEDTO, self._FormatSpeed(ownBall.maxVelocity)))

# WASD keys for movements in svc.eveCmd
def CmdMoveForward(self, *args):
    return self._UpdateMovement(const.MOVDIR_FORWARD)

def CmdMoveBackward(self, *args):
    return self._UpdateMovement(const.MOVDIR_BACKWARD)

def CmdMoveLeft(self, *args):
    return self._UpdateMovement(const.MOVDIR_LEFT)

def CmdMoveRight(self, *args):
    return self._UpdateMovement(const.MOVDIR_RIGHT)

def _UpdateMovement(self, direction):
    if uicore.layer.charcontrol.isopen:
        sm.GetService('navigation').UpdateMovement(direction)
    return False

#approach gate with full speed:
park = sm.GetService('michelle').GetRemotePark()
park.SetSpeedFraction(1.0)
shipui = uicore.layer.shipui
if shipui.isopen:
    shipui.SetSpeed(1.0)
park.FollowBall(gateID, 0.0)
# #################################################################################
# svc.menu functions that are useful
def WarpToScanResult(self, scanResultID, minRange = None):
    self._WarpXToScanResult(scanResultID, minRange)
# check if in warp
checkWarpActive = ownBall and ownBall.mode == destiny.DSTBALL_WARP
# warp to bookmark
def WarpToBookmark(self, bookmark, warpRange = 20000.0, fleet = False):
    bp = sm.StartService('michelle').GetRemotePark()
    if bp:
        if getattr(bookmark, 'agentID', 0) and hasattr(bookmark, 'locationNumber'):
            referringAgentID = getattr(bookmark, 'referringAgentID', None)
            sm.StartService('agents').GetAgentMoniker(bookmark.agentID).WarpToLocation(bookmark.locationType, bookmark.locationNumber, warpRange, fleet, referringAgentID)
        else:
            bp.WarpToStuff('bookmark', bookmark.bookmarkID, minRange=warpRange, fleet=fleet)
            sm.StartService('space').WarpDestination(None, bookmark.bookmarkID, None)
# warp to item
def WarpToItem(self, id, warpRange = None):
    if id == session.shipid:
        return
    if warpRange is None:
        warprange = sm.GetService('menu').GetDefaultActionDistance('WarpTo')
    else:
        warprange = warpRange
    bp = sm.StartService('michelle').GetRemotePark()
    if bp is not None and sm.StartService('space').CanWarp(id):
        bp.WarpToStuff('item', id, minRange=warprange)
        sm.StartService('space').WarpDestination(id, None, None)
# warp/dock to station and cancel
def Dock(self, id):
    bp = sm.StartService('michelle').GetBallpark()
    if not bp:
        return
    station = bp.GetBall(id)
    if not station:
        return
    station.GetVectorAt(blue.os.GetTime())
    if station.surfaceDist >= const.minWarpDistance:
        self.WarpDock(id)
    else:
        eve.Message('OnDockingRequest')
        eve.Message('Command', {'command': mls.UI_INFLIGHT_REQUESTTODOCKAT % {'station': cfg.evelocations.Get(id).name}})
        paymentRequired = 0
        try:
            bp = sm.GetService('michelle').GetRemotePark()
            if bp is not None:
                self.LogNotice('Docking', id)
                if uicore.uilib.Key(uiconst.VK_CONTROL) and uicore.uilib.Key(uiconst.VK_SHIFT) and uicore.uilib.Key(uiconst.VK_MENU) and session.role & service.ROLE_GML:
                    success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.TurboDock, id)
                else:
                    success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.Dock, id, session.shipid)
        except UserError as e:
            if e.msg == 'DockingRequestDeniedPaymentRequired':
                sys.exc_clear()
                paymentRequired = e.args[1]['amount']
            else:
                raise
        except Exception as e:
            raise
        if paymentRequired:
            try:
                if eve.Message('AskPayDockingFee', {'cost': util.FmtAmt(paymentRequired)}, uiconst.YESNO) == uiconst.ID_YES:
                    bp = sm.GetService('michelle').GetRemotePark()
                    if bp is not None:
                        session.ResetSessionChangeTimer('Retrying with docking payment')
                        if uicore.uilib.Key(uiconst.VK_CONTROL) and session.role & service.ROLE_GML:
                            success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.TurboDock, id, paymentRequired)
                        else:
                            success = sm.GetService('sessionMgr').PerformSessionChange('dock', bp.Dock, id, session.shipid, paymentRequired)
            except Exception as e:
                raise
# undock from station
def ExitStation(self, invItem):
    uicore.cmd.CmdExitStation()
# cancel warp dock
def CancelWarpDock(self):
    self.warpDocking = False

# cargo related
def OpenCargo(self, id, *args):
    if getattr(self, '_openingCargo', 0):
        return
    self._openingCargo = 1
    uthread.new(self._OpenCargo, id)

def _OpenCargo(self, _id):
    if type(_id) != types.ListType:
        _id = [_id]
    for id in _id:
        try:
            if id == session.shipid:
                uicore.cmd.OpenCargoHoldOfActiveShip()
            else:
                slim = sm.GetService('michelle').GetItem(id)
                if slim and slim.groupID == const.groupWreck:
                    sm.StartService('window').OpenContainer(id, mls.UI_INFLIGHT_WRECK, hasCapacity=0, isWreck=True, windowPrefsID='lootCargoContainer')
                else:
                    sm.StartService('window').OpenContainer(id, mls.UI_INFLIGHT_FLOATINGCARGO, hasCapacity=1, windowPrefsID='lootCargoContainer')

        finally:
            self._openingCargo = 0

# launch drones
def LaunchDrones(self, invItems, *args):
    sm.GetService('godma').GetStateManager().SendDroneSettings()
    util.LaunchFromShip(invItems)
# jet
def Jettison(self, invItems):
    if eve.Message('ConfirmJettison', {}, uiconst.YESNO, suppress=uiconst.ID_YES) != uiconst.ID_YES:
        return
    ids = []
    for invItem in invItems:
        ids += [invItem.itemID]

    ship = sm.StartService('gameui').GetShipAccess()
    if ship:
        ship.Jettison(ids)
# drone engage
def EngageTarget(self, droneIDs):
    michelle = sm.StartService('michelle')
    requiresAttackConfirmation = False
    requiresAidConfirmation = False
    dronesRemoved = []
    for droneID in droneIDs:
        item = michelle.GetItem(droneID)
        if not item:
            dronesRemoved.append(droneID)
            continue
        for row in cfg.dgmtypeeffects.get(item.typeID, []):
            (effectID, isDefault,) = (row.effectID, row.isDefault)
            if isDefault:
                effect = cfg.dgmeffects.Get(effectID)
                if effect.isOffensive:
                    requiresAttackConfirmation = True
                    break
                elif effect.isAssistance:
                    requiresAidConfirmation = True
                    break

    for droneID in dronesRemoved:
        droneIDs.remove(droneID)

    if requiresAttackConfirmation and requiresAidConfirmation:
        raise UserError('DroneCommandEngageRequiresNoAmbiguity')
    targetID = sm.StartService('target').GetActiveTargetID()
    if targetID is None:
        raise UserError('DroneCommandRequiresActiveTarget')
    if requiresAidConfirmation and not sm.StartService('consider').DoAidConfirmations(targetID):
        return
    if requiresAttackConfirmation and not sm.StartService('consider').DoAttackConfirmations(targetID):
        return
    entity = moniker.GetEntityAccess()
    if entity:
        ret = entity.CmdEngage(droneIDs, targetID)
        self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')
        if droneIDs:
            name = sm.GetService('space').GetWarpDestinationName(targetID)
            eve.Message('Command', {'command': mls.UI_INFLIGHT_DRONESENGAGING % {'name': name}})

# more drone control
def ReturnAndOrbit(self, droneIDs):
    entity = moniker.GetEntityAccess()
    if entity:
        ret = entity.CmdReturnHome(droneIDs)
        self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')

def ReturnToDroneBay(self, droneIDs):
    entity = moniker.GetEntityAccess()
    if entity:
        ret = entity.CmdReturnBay(droneIDs)
        self.HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')

# action menu in svc.menu
def OnBtnparClicked(self, btnpar):
    sm.StartService('ui').StopBlink(btnpar)
    if btnpar.destroyed:
        uicore.layer.menu.Flush()
        return
    if btnpar.killsub and isinstance(btnpar.action[1], list):
        uthread.new(btnpar.action[1][0][2][0][0], btnpar.action[1][0][2][0][1][0])
        uicore.layer.menu.Flush()
        return
    if type(btnpar.action[1]) in types.StringTypes:
        sm.StartService('gameui').Say(btnpar.action[1])
    else:
        try:
            apply(*btnpar.action[1:])
        except Exception as e:
            log.LogError(e, 'Failed executing action:', btnpar.action)
            log.LogException()
            sys.exc_clear()
    uicore.layer.menu.Flush()

# ##################################
# svc.addressbook
# get bookmarks
def GetBookmarks(self, *args):
    return self.bms

# bookmark current location
def BookmarkCurrentLocation(self, *args):
    wnd = self.GetWnd()
    text = mls.UI_CMD_ADDBOOKMARK
    btn = wnd.sr.bookmarkbtns.GetBtnByLabel(text)
    btn.Disable()
    try:
        if not (session.stationid or session.shipid):
            eve.Message('HavetobeatstationOrinShip')
            return
        if session.stationid:
            stationinfo = sm.RemoteSvc('stationSvc').GetStation(session.stationid)
            self.BookmarkLocationPopup(session.stationid, stationinfo.stationTypeID, session.solarsystemid2)
        elif session.solarsystemid and session.shipid:
            bp = sm.GetService('michelle').GetBallpark()
            if bp is None:
                return
            slimItem = bp.GetInvItem(session.shipid)
            if slimItem is None:
                return
            self.BookmarkLocationPopup(session.shipid, slimItem.typeID, session.solarsystemid)

    finally:
        if wnd:
            text = mls.UI_CMD_ADDBOOKMARK
            btn = wnd.sr.bookmarkbtns.GetBtnByLabel(text)
            btn.Enable()
# the other bookmark functions are below this one in svc.addressbook

# ######################################################
# svc.gameui
# cargo window stuff
def KillCargoView(self, id_):
    for each in sm.GetService('window').GetWindows()[:]:
        if getattr(each, '__guid__', None) in ('form.DockedCargoView', 'form.InflightCargoView', 'form.LootCargoView', 'form.DroneBay', 'form.CorpHangar', 'form.ShipCorpHangars', 'form.CorpHangarArray', 'form.SpecialCargoBay', 'form.PlanetInventory') and getattr(each, 'itemID', None) == id_:
            if not each.destroyed:
                if hasattr(each, 'SelfDestruct'):
                    each.SelfDestruct()
                else:
                    each.CloseX()
################################################################
# form.OverView
# setting focus to the scroll
uicore.registry.SetFocus(self.sr.scroll)

# uicls.ScrollCore
# node functions
def ShowNodeIdx(self, idx, toTop = 1):
    if self.scrollingRange:
        node = self.GetNode(idx)
        fromTop = node.scroll_positionFromTop
        if fromTop is None:
            return
        if self._position > fromTop:
            portion = fromTop / float(self.scrollingRange)
            self.ScrollToProportion(portion)
        (clipperWidth, clipperHeight,) = self.GetContentParentSize()
        nodeHeight = self.GetNodeHeight(node, clipperWidth)
        if self._position + clipperHeight < fromTop + nodeHeight:
            portion = (fromTop - clipperHeight + nodeHeight) / float(self.scrollingRange)
            self.ScrollToProportion(portion)
def GetNodes(self, allowNone = False):
    ret = []
    for each in self.sr.nodes:
        if each.internalNodes:
            if allowNone:
                ret += each.internalNodes
            else:
                for internal in each.internalNodes:
                    if internal:
                        ret.append(internal)
        else:
            ret.append(each)
    return ret
def SetSelected(self, idx):
    node = self.GetNode(idx)
    if node:
        self.SelectNode(node)
    self.ReportSelectionChange()
    def SetSelected(self, idx):
        node = self.GetNode(idx)
        if node:
            self.SelectNode(node)
        self.ReportSelectionChange()
def SelectNode(self, node, multi = 0, subnode = None, checktoggle = 1):
	#see details in actual code
	pass

#########################
# hangar.py
# form.ItemHangar
def Add(self, itemID, sourceLocation, quantity, dividing = False):
    return self.GetShell().Add(itemID, sourceLocation, qty=quantity, flag=const.flagHangar)
# form.VirtualInvWindow

def OnContentDropData(self, dragObj, nodes):
    idx = None
    if self.viewMode == 'icons' and self.cols:
        (l, t,) = self.sr.scroll.GetAbsolutePosition()
        idx = self.cols * len(self.sr.scroll.sr.nodes) + (uicore.uilib.x - l) // (64 + colMargin)
    self.OnDropDataWithIdx(nodes, idx)

def OnDropData(self, dragObj, nodes):
    self.OnDropDataWithIdx(nodes)

def RefreshCapacity(self):
    cap = self.GetCapacity()
    if self.destroyed:
        return
    (total, full,) = (cap.capacity, cap.used)
    self.capacityText.text = '%s/%s m\xb3' % (util.FmtAmt(full, showFraction=1), util.FmtAmt(total, showFraction=1))
    if total:
        proportion = min(1.0, max(0.0, full / float(total)))
    else:
        proportion = 1.0
    self.sr.gauge.width = int(proportion * self.sr.gaugeParent.width)


###########################
# svc.window
def OpenCargo(self, id_, name, displayname = None, typeid = None):
    if eve.session.stationid:
        decoClass = form.DockedCargoView
    elif eve.session.solarsystemid:
        decoClass = form.InflightCargoView
    else:
        self.LogError('Not inflight or docked???')
        return
    self.LogInfo('OpenCargo', id_, name, displayname)
    wnd = self.GetWindow('shipCargo_%s' % id_, create=1, maximize=1, decoClass=decoClass, _id=id_, displayName=name)
    if wnd and id_ == eve.session.shipid:
        wnd.scope = 'station_inflight'

def OpenContainer(self, id_, name, displayname = None, typeid = None, hasCapacity = 0, locationFlag = None, nameLabel = 'loot', isWreck = False, windowPrefsID = None):
    wnd = self.GetWindow(nameLabel + '_%s' % id_, create=1, maximize=1, decoClass=form.LootCargoView, windowPrefsID=windowPrefsID, _id=id_, displayName=name, hasCapacity=hasCapacity, locationFlag=locationFlag, isWreck=isWreck)

def CloseContainer(self, id_):
    wnd = self.GetWindow('loot_%s' % id_)
    if wnd is not None and not wnd.destroyed:
        wnd.SelfDestruct()


##################################
# flash screen in spaceMgr.py
def FlashScreen(self, magnitude, duration = 0.5):
	pass

#####################################
#####################################
# AutoPilot's update call -
# This includes checking warp state,
# and a model for automated update calls
# as well as some other useful stuff

def Update(self):
    if self.autopilot == 0:
        self.KillTimer()
        return
    else:
        if self.ignoreTimerCycles > 0:
            self.ignoreTimerCycles = self.ignoreTimerCycles - 1
            return
        if not eve.session.IsItSafe():
            self.LogInfo('returning as it is not safe')
            return
        if not eve.session.rwlock.IsCool():
            self.LogInfo("returning as the session rwlock isn't cool")
            return
        starmapSvc = sm.GetService('starmap')
        waypoints = starmapSvc.GetWaypoints()
        destinationPath = starmapSvc.GetDestinationPath()
        if len(destinationPath) == 0:
            self.SetOff('  - %s' % mls.UI_INFLIGHT_NODESTPATHSET)
            return
        if destinationPath[0] == None:
            self.SetOff('  - %s' % mls.UI_INFLIGHT_NODESTPATHSET)
            return
        bp = sm.GetService('michelle').GetBallpark()
        if not bp:
            return
        if sm.GetService('jumpQueue').IsJumpQueued():
            return
        ship = bp.GetBall(eve.session.shipid)
        if ship is None:
            return
        if ship.mode == destiny.DSTBALL_WARP:
            return
        gateID = None
        gateItem = None
        for ballID in bp.balls.iterkeys():
            slimItem = bp.GetInvItem(ballID)
            if slimItem == None:
                continue
            if slimItem.groupID == const.groupStargate and destinationPath[0] in map(lambda x: x.locationID, slimItem.jumps):
                gateID = ballID
                gateItem = slimItem
                break

        if gateID is None:
            return
        theJump = None
        for jump in gateItem.jumps:
            if destinationPath[0] == jump.locationID:
                theJump = jump
                break

        if theJump is None:
            return
        gate = bp.GetBall(gateID)
        if gate is None:
            return
        jumpToSystem = sm.GetService('map').GetItem(theJump.locationID)
        shipGateDistance = bp.GetSurfaceDist(ship.id, gateID)
        if shipGateDistance < const.maxStargateJumpingDistance:
            if ship.isCloaked:
                return
            if eve.session.mutating:
                self.LogInfo('session is mutating')
                return
            if eve.session.changing:
                self.LogInfo('session is changing')
                return
            if bp.solarsystemID != eve.session.solarsystemid:
                self.LogInfo('bp.solarsystemid is not solarsystemid')
                return
            if sm.GetService('michelle').GetRemotePark()._Moniker__bindParams != eve.session.solarsystemid:
                self.LogInfo('remote park moniker bindparams is not solarsystemid')
                return
            try:
                self.LogNotice('Autopilot jumping from', gateID, 'to', theJump.toCelestialID, '(', jumpToSystem.itemName, ')')
                sm.GetService('sessionMgr').PerformSessionChange('autopilot', sm.GetService('michelle').GetRemotePark().StargateJump, gateID, theJump.toCelestialID, eve.session.shipid)
                eve.Message('AutoPilotJumping', {'what': jumpToSystem.itemName})
                self.ignoreTimerCycles = 5
            except UserError as e:
                if e.msg == 'SystemCheck_JumpFailed_Stuck':
                    self.SetOff()
                    raise
                elif e.msg.startswith('SystemCheck_JumpFailed_'):
                    eve.Message(e.msg, e.dict)
                elif e.msg == 'NotCloseEnoughToJump':
                    park = sm.GetService('michelle').GetRemotePark()
                    park.SetSpeedFraction(1.0)
                    shipui = uicore.layer.shipui
                    if shipui.isopen:
                        shipui.SetSpeed(1.0)
                    park.FollowBall(gateID, 0.0)
                    self.LogWarn("Autopilot: I thought I was close enough to jump, but I wasn't.")
                sys.exc_clear()
                self.LogError('Autopilot: jumping to ' + jumpToSystem.itemName + ' failed. Will try again')
                self.ignoreTimerCycles = 5
            except:
                sys.exc_clear()
                self.LogError('Autopilot: jumping to ' + jumpToSystem.itemName + ' failed. Will try again')
                self.ignoreTimerCycles = 5
            return
        if shipGateDistance < const.minWarpDistance:
            if ship.mode == destiny.DSTBALL_FOLLOW and ship.followId == gateID:
                return
            park = sm.GetService('michelle').GetRemotePark()
            park.SetSpeedFraction(1.0)
            shipui = uicore.layer.shipui
            if shipui.isopen:
                shipui.SetSpeed(1.0)
            park.FollowBall(gateID, 0.0)
            eve.Message('AutoPilotApproaching')
            self.LogInfo('Autopilot: approaching')
            self.ignoreTimerCycles = 2
            return
        try:
            sm.GetService('space').WarpDestination(gateID, None, None)
            sm.GetService('michelle').GetRemotePark().WarpToStuffAutopilot(gateID)
            eve.Message('AutoPilotWarpingTo', {'what': jumpToSystem.itemName})
            self.LogInfo('Autopilot: warping to gate')
            self.ignoreTimerCycles = 2
        except:
            sys.exc_clear()
            item = sm.GetService('godma').GetItem(session.shipid)
            if item.warpScrambleStatus > 0:
                self.SetOff('Autopilot cannot warp while warp scrambled.')
        return
###################################
# module interactions
# shipmodulebutton.py
def Click(self, ctrlRepeat = 0):
    if self.waitingForActiveTarget:
        sm.GetService('target').CancelTargetOrder(self)
        self.waitingForActiveTarget = 0
    elif self.def_effect is None:
        log.LogWarn('No default Effect available for this moduletypeID:', self.sr.moduleInfo.typeID)
    elif not self.online:
        if getattr(self, 'isMaster', None):
            eve.Message('ClickOffllineGroup')
        else:
            eve.Message('ClickOffllineModule')
    elif self.def_effect.isActive:
        self.DeactivateEffect(self.def_effect)
    elif not self.effect_activating:
        self.activationTimer = base.AutoTimer(500, self.ActivateEffectTimer)
        self.effect_activating = 1
        self.ActivateEffect(self.def_effect, ctrlRepeat=ctrlRepeat)
#########################################
# tactical.py
# toggling tactical layer display
def Init(self):
    if self.logme:
        self.LogInfo('Tactical::Init')
    if not self.inited:
        rm = []
        scene2 = sm.GetService('sceneManager').GetRegisteredScene2('default')
        if scene2 is None:
            return
        for each in scene2.objects:
            if each.name == 'TacticalMap':
                rm.append(each)

        for each in rm:
            scene2.objects.remove(each)

        self.arena = trinity.Load('res:/UI/Inflight/tactical/TacticalMap.red')
        self.arena.name = 'TacticalMap'
        self.usedCurveSets = []
        self.directionCurveSet = None
        self.updateDirectionTimer = None
        for child in self.arena.children:
            if child.name == 'connectors':
                self.connectors = child
            elif child.name == 'TargetingRange':
                self.TargetingRange = child
            elif child.name == 'OptimalRange':
                self.OptimalRange = child
            elif child.name == 'FalloffRange':
                self.FalloffRange = child
            elif child.name == 'circleLineSet':
                self.circles = child
            elif child.name == 'directionLineSet':
                self.direction = child

        self.InitDistanceCircles()
        self.InitDirectionLines()
        scene2.objects.append(self.arena)
        self.inited = True
        self.InitConnectors()
        self.UpdateTargetingRanges()

# init for directionlines
def InitDirectionLines(self):
    if self.direction is None:
        return
    self.direction.ClearLines()
    color = (0.2, 0.2, 0.2, 1.0)
    self.direction.AddLine((0.0, 0.0, 0.0), color, (1.0, 1.0, 1.0), color)
    self.direction.display = False
    self.direction.SubmitChanges()

# command service drone functions
def CmdDronesEngage(self, *args):
    drones = sm.GetService('michelle').GetDrones()
    if drones is None:
        return
    droneIDs = drones.keys()
    targetID = sm.GetService('target').GetActiveTargetID()
    entity = moniker.GetEntityAccess()
    if entity:
        sm.GetService('menu').EngageTarget(droneIDs)

def CmdDronesReturnAndOrbit(self, *args):
    drones = sm.GetService('michelle').GetDrones()
    if not drones:
        return
    droneIDs = drones.keys()
    targetID = sm.GetService('target').GetActiveTargetID()
    entity = moniker.GetEntityAccess()
    if entity:
        ret = entity.CmdReturnHome(droneIDs)
        sm.GetService('menu').HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')
        if droneIDs and targetID:
            eve.Message('Command', {'command': mls.UI_INFLIGHT_ALLDRONESRETURNINGANDORBITING})

def CmdDronesReturnToBay(self, *args):
    drones = sm.GetService('michelle').GetDrones()
    if not drones:
        return
    droneIDs = drones.keys()
    targetID = sm.GetService('target').GetActiveTargetID()
    entity = moniker.GetEntityAccess()
    if entity:
        ret = entity.CmdReturnBay(droneIDs)
        sm.GetService('menu').HandleMultipleCallError(droneIDs, ret, 'MultiDroneCmdResult')
        if droneIDs and targetID:
            eve.Message('Command', {'command': mls.UI_INFLIGHT_ALLDRONESRETURNINGTOBAY})

def OpenDroneBayOfActiveShip(self, *args):
    if eve.session.shipid and eve.session.stationid:
        uthread.new(self._EveCommandService__OpenDroneBayOfActiveShip_thread).context = 'cmd.OpenDroneBayOfActiveShip'

def __OpenDroneBayOfActiveShip_thread(self, *args):
    if eve.session.shipid and eve.session.stationid:
        name = cfg.evelocations.Get(eve.session.shipid).name
        sm.GetService('window').OpenDrones(eve.session.shipid, name, "%s's drone bay" % name)

def OpenCargoHoldOfActiveShip(self, *args):
    if eve.session.shipid:
        uthread.new(self._EveCommandService__OpenCargoHoldOfActiveShip_thread).context = 'cmd.OpenCargoHoldOfActiveShip'

#############################################
# base_fitting.py
# form.Fitting
def OnDropData(self, dragObj, nodes):
    for node in nodes:
        if node.Get('__guid__', None) in ('xtriui.InvItem', 'listentry.InvItem', 'listentry.InvFittingItem'):
            requiredSkills = sm.GetService('info').GetRequiredSkills(node.rec.typeID)
            for (skillID, level,) in requiredSkills:
                if getattr(sm.GetService('skills').HasSkill(skillID), 'skillLevel', 0) < level:
                    sm.GetService('tutorial').OpenTutorialSequence_Check(uix.skillfittingTutorial)
                    break


    sm.GetService('menu').TryFit([ node.rec for node in nodes ])
# form.Fitting's slots:
self.slots
# slot class:
def IsChargeEmpty(self):
    return self.charge is None

###################################################
# shipmodulebutton.py
# getting the duration of a module's activated effect
def DoActivateRampsThread(self):
    if not self or self.destroyed:
        return
    (startTime, durationInMilliseconds,) = self.GetDuration()
    if durationInMilliseconds <= 0:
        return
    self.ramp_active = True
    self.sr.ramps.state = uiconst.UI_DISABLED
    portionDone = blue.os.TimeDiffInMs(startTime) % durationInMilliseconds / durationInMilliseconds
    rampUpInit = min(1.0, max(0.0, portionDone * 2))
    rampDownInit = min(1.0, max(0.0, portionDone * 2 - 1.0))
    while self and not self.destroyed and self.ramp_active:
        (dummy, durationInMilliseconds,) = self.GetDuration()
        halfTheTime = durationInMilliseconds / 2.0
        funcs = [(self.SetRampUpValue, rampUpInit), (self.SetRampDownValue, rampDownInit)]
        rampUpInit = rampDownInit = 0.0
        for (i, (func, percent,),) in enumerate(funcs):
            init = percent
            if not self or self.destroyed:
                break
            if i == 0:
                self.sr.rightRamp.SetRotation(math.pi)
                self.sr.rightShadowRamp.SetRotation(math.pi)
                self.sr.leftRamp.SetRotation(math.pi)
                self.sr.leftShadowRamp.SetRotation(math.pi)
            else:
                self.sr.leftRamp.SetRotation(0)
                self.sr.leftShadowRamp.SetRotation(0)
                self.sr.rightRamp.SetRotation(math.pi)
                self.sr.rightShadowRamp.SetRotation(math.pi)
            while not self.destroyed:
                prePercent = percent
                try:
                    percent = min(blue.os.TimeDiffInMs(startTime) % halfTheTime / halfTheTime, 1.0)
                except:
                    percent = 1.0
                if prePercent > percent:
                    break
                curValue = mathUtil.Lerp(init, 1.0, percent)
                func(curValue)
                blue.pyos.synchro.Yield()
                if self and not self.destroyed and not self.ramp_active:
                    func(1.0)
                    break


        startTime += long(durationInMilliseconds * const.dgmTauConstant)
        if not self or self.destroyed or self.InLimboState():
            break
####################################
# some file io stuff from dataLog.py
# remember the imports
import cStringIO
import collections
import os
def GeneratePythonCode(self, path):
    files = []
    validPath = 'common'
    if validPath not in path:
        raise AxiomError('Script path is invalid: %s, it should contain %s' % (path, validPath))
    (helperClasses, standaloneClasses, enums,) = self.GetDefinitionElements()
    filename = os.path.join(path, 'modules', 'dust', 'dataLogSource.py')
    MARKER = '## MARKER ##'
    oldContents = open(filename, 'r').read()
    idxStart = oldContents.find(MARKER)
    if idxStart == -1:
        print 'Failed to find starting marker in %s' % filename
        return []
    idxEnd = oldContents.rfind(MARKER)
    if idxEnd == idxStart:
        print 'Failed to find two distinct markers in %s' % filename
        return []
    idxStart = oldContents.find('\n', idxStart) + 1
    idxEnd = oldContents.rfind('\n', 0, idxEnd) + 1
    sio = cStringIO.StringIO()
    sio.write(oldContents[:idxStart])
    sio.write('entryCategories = (\n')
    for eachClass in helperClasses:
        sio.write('    "%s",\n' % eachClass.className)

    sio.write(')\n')
    sio.write(oldContents[idxEnd:])
    sNew = sio.getvalue()
    if oldContents == sNew:
        print INFO_FILE_UNCHANGED.format(filename)
        return []
    codeGeneration.AutoCheckoutMagic(filename)
    try:
        f = open(filename, 'w')
    except IOError:
        print ERROR_CANT_OPEN_FILE.format(filename)
        return []
    f.write(sNew)
    f.close()
    files.append(filename)
    return files
############################
#########################################################
# setting waypoint for autopilot
# menusvc.py
def _MapMenu(self, itemID, unparsed = 0):
    mapItem = sm.StartService('map').GetItem(itemID)
    if mapItem is None:
        return []
    checkSolarsystem = mapItem.typeID == const.typeSolarSystem
    menuEntries = []
    if checkSolarsystem is True:
        waypoints = sm.StartService('starmap').GetWaypoints()
        (uni, regionID, constellationID, _sol, _item,) = sm.StartService('map').GetParentLocationID(itemID, gethierarchy=1)
        checkInWaypoints = itemID in waypoints
        menuEntries += [None]
        if checkSolarsystem:
            menuEntries += [[mls.UI_CMD_SETDESTINATION, sm.StartService('starmap').SetWaypoint, (itemID, 1)]]
            if checkInWaypoints:
                menuEntries += [[mls.UI_CMD_REMOVEWAYPOINT, sm.StartService('starmap').ClearWaypoints, (itemID,)]]
            else:
                menuEntries += [[mls.UI_CMD_ADDWAYPOINT, sm.StartService('starmap').SetWaypoint, (itemID,)]]
            menuEntries += [[mls.UI_CMD_BOOKMARKLOCATION, self.Bookmark, (itemID, const.typeSolarSystem, constellationID)]]
    if unparsed:
        return menuEntries
    return self.ParseMenu(menuEntries)


#############################################
# Figure this shit out later:
def FormatWnd(self, wnd, typeID, itemID = None, rec = None, parentID = None, historyData = None, headerOnly = 0, abstractinfo = None):
        try:
            if wnd is not None and not wnd.destroyed:
                wnd.ShowLoad()
            else:
                return
            self.loading = 1
            wnd.IsBusy = 1
            self.HideError(wnd)
            if wnd.top == uicore.desktop.height:
                wnd.Maximize()
            else:
                wnd.state = uiconst.UI_NORMAL
            wnd.sr.itemID = itemID
            wnd.sr.typeID = typeID
            wnd.sr.rec = rec
            wnd.sr.abstractinfo = abstractinfo
            wnd.sr.corpinfo = None
            wnd.sr.allianceinfo = None
            wnd.sr.factioninfo = None
            wnd.sr.warfactioninfo = None
            wnd.sr.stationinfo = None
            wnd.sr.plasticinfo = None
            wnd.sr.voucherinfo = None
            wnd.sr.itemname = None
            wnd.sr.variationbtm = None
            wnd.sr.corpID = None
            wnd.sr.allianceID = None
            wnd.sr.scroll.state = uiconst.UI_HIDDEN
            wnd.sr.notesedit.state = uiconst.UI_HIDDEN
            wnd.sr.descedit.state = uiconst.UI_HIDDEN
            setattr(wnd.sr, 'oldnotes', None)
            wnd.sr.maintabs = None
            self.ParseTabs(wnd)
            uix.Flush(wnd.sr.captionpush)
            uix.Flush(wnd.sr.captioncontainer)
            uix.Flush(wnd.sr.subinfolinkcontainer)
            uix.Flush(wnd.sr.therestcontainer)
            wnd.sr.subinfolinkcontainer.height = 0
            uiutil.FlushList(wnd.sr.subcontainer.children[:-3])
            self.GetWindowSettings(wnd, typeID, itemID)
            height = MINHEIGHTREGULAR
            if typeID == const.typeMedal:
                height = MINHEIGHTMEDAL
            wnd.SetMinSize([MINWIDTH, height])
            self.GetIcon(wnd, typeID, itemID)
            desc = self.GetNameAndDescription(wnd, typeID, itemID)
            bio = None
            if wnd.sr.isCharacter and itemID:
                if not headerOnly:
                    wnd.sr.dynamicTabs.append((mls.UI_GENERIC_NOTES, 'Notes'))
                corpid = None
                allianceid = None
                parallelCalls = []
                if util.IsNPC(itemID):
                    parallelCalls.append((ReturnNone, ()))
                    parallelCalls.append((ReturnNone, ()))
                else:
                    parallelCalls.append((sm.RemoteSvc('charMgr').GetPublicInfo3, (itemID,)))
                    parallelCalls.append((sm.GetService('corp').GetInfoWindowDataForChar, (itemID, 1)))
                if not util.IsNPC(itemID):
                    parallelCalls.append((sm.RemoteSvc('standing2').GetSecurityRating, (itemID,)))
                else:
                    parallelCalls.append((ReturnNone, ()))
                (charinfo, corpCharInfo, security,) = uthread.parallel(parallelCalls)
                if not util.IsNPC(itemID):
                    charinfo = charinfo[0]
                    bio = charinfo.description
                    corpAge = blue.os.GetTime() - charinfo.startDateTime
                    if getattr(charinfo, 'medal1GraphicID', None):
                        uicls.Icon(icon='ui_50_64_16', parent=wnd.sr.mainicon, left=70, top=80, size=64, align=uiconst.RELATIVE, idx=0)
                if corpCharInfo:
                    corpid = corpCharInfo.corpID
                    allianceid = corpCharInfo.allianceID
                    wnd.sr.corpID = corpid
                    wnd.sr.allianceID = allianceid
                    title = ''
                    if corpCharInfo.title:
                        title = corpCharInfo.title
                    for ix in xrange(1, 17):
                        titleText = getattr(corpCharInfo, 'title%s' % ix, None)
                        if titleText:
                            title = '%s%s%s' % (title, ['', ', '][(not not len(title))], titleText)

                    if len(title) > 0:
                        text = uicls.Label(text='%s: %s' % (mls.UI_GENERIC_TITLE, title), parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, fontsize=9, linespace=11, uppercase=1, letterspace=1)
                        if text.height > 405:
                            text.autoheight = 0
                            text.height = 405
                uicls.Container(name='push', parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, height=4, state=uiconst.UI_DISABLED)
                uicls.Line(parent=wnd.sr.captioncontainer, align=uiconst.TOTOP)
                if not util.IsNPC(itemID):
                    uicls.Line(parent=wnd.sr.therestcontainer, align=uiconst.TOTOP)
                    uicls.Container(name='push', parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, height=4)
                    uicls.Label(text='%s: %.1f' % (mls.UI_GENERIC_SECURITYSTATUS, security), parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, fontsize=9, linespace=9, uppercase=1, letterspace=1)
                    standing = sm.GetService('standing').GetStanding(eve.session.corpid, itemID)
                    if standing is not None:
                        uicls.Label(text='%s: %.1f' % (mls.UI_GENERIC_CORPSTANDING, standing), parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, fontsize=9, linespace=9, uppercase=1, letterspace=1)
                    if charinfo.bounty:
                        self.Wanted(wnd, charinfo.bounty)
                if wnd.sr.isCharacter and util.IsNPC(itemID):
                    agentInfo = sm.GetService('agents').GetAgentByID(itemID)
                    if agentInfo:
                        corpid = agentInfo.corporationID
                    else:
                        corpid = sm.RemoteSvc('corpmgr').GetCorporationIDForCharacter(itemID)
                if corpid:
                    uicls.Container(name='push', parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOTOP, height=4)
                    self.GetCorpLogo(corpid, parent=wnd.sr.subinfolinkcontainer, wnd=wnd)
                    wnd.sr.subinfolinkcontainer.height = 64
                    if not util.IsNPC(itemID) and corpid:
                        uicls.Container(name='push', parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOLEFT, width=4)
                        tickerName = cfg.corptickernames.Get(corpid).tickerName
                        uicls.Label(text=mls.UI_INFOWND_MEMBEROFCORP % {'corpName': cfg.eveowners.Get(corpid).name,
                         'tickerName': tickerName}, parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOALL, top=0, left=0, autowidth=False, autoheight=False)
                        uicls.Label(text=mls.UI_INFOWND_FORDAY % {'day': util.FmtTimeInterval(corpAge, 'day')}, parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOBOTTOM, left=4, autowidth=False, fontsize=9, linespace=9, uppercase=1, letterspace=1)
                        uthread.new(self.ShowRelationshipIcon, wnd, itemID, corpid, allianceid)
                    if not util.IsNPC(itemID) and allianceid:
                        uicls.Line(parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, idx=0)
                        uicls.Label(text=cfg.eveowners.Get(allianceid).name, parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, top=4, autowidth=False, fontsize=9, linespace=9, uppercase=1, letterspace=1, idx=1)
            elif wnd.sr.isShip and itemID or typeID and sm.GetService('godma').GetType(typeID).agentID:
                if itemID == eve.session.shipid:
                    otherCharID = eve.session.charid
                elif typeID and sm.GetService('godma').GetType(typeID).agentID:
                    otherCharID = sm.GetService('godma').GetType(typeID).agentID
                elif eve.session.solarsystemid is not None:
                    otherCharID = sm.GetService('michelle').GetCharIDFromShipID(itemID)
                else:
                    otherCharID = None
                if otherCharID:
                    btn = uix.GetBigButton(42, wnd.sr.subinfolinkcontainer, left=0, top=0, iconMargin=0)
                    btn.OnClick = (self._Info__PreFormatWnd,
                     wnd,
                     cfg.eveowners.Get(otherCharID).typeID,
                     otherCharID)
                    btn.hint = mls.UI_INFOWND_CLICKFORPILOTINFO
                    btn.sr.icon.LoadIconByTypeID(cfg.eveowners.Get(otherCharID).typeID, itemID=otherCharID, ignoreSize=True)
                    btn.sr.icon.SetAlign(uiconst.RELATIVE)
                    btn.sr.icon.SetSize(40, 40)
                    wnd.sr.subinfolinkcontainer.height = 42
            elif wnd.sr.abstractinfo is not None:
                if wnd.sr.isMedal or wnd.sr.isRibbon:
                    corpid = None
                    info = sm.GetService('medals').GetMedalDetails(itemID).info[0]
                    try:
                        corpid = info.ownerID
                    except:
                        sys.exc_clear()
                    if corpid:
                        uicls.Container(name='push', parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOTOP, height=4)
                        self.GetCorpLogo(corpid, parent=wnd.sr.subinfolinkcontainer, wnd=wnd)
                        wnd.sr.subinfolinkcontainer.height = 64
                        if corpid and not util.IsNPC(corpid):
                            uicls.Container(name='push', parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOLEFT, width=4)
                            tickerName = cfg.corptickernames.Get(corpid).tickerName
                            uicls.Label(text='%s %s [%s]' % (mls.UI_GENERIC_ISSUEDBY, cfg.eveowners.Get(corpid).name, tickerName), parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOALL, top=0, left=0, autoheight=False, autowidth=False)
                        uicls.Line(parent=wnd.sr.captioncontainer, align=uiconst.TOTOP)
                        uicls.Line(parent=wnd.sr.therestcontainer, align=uiconst.TOTOP)
                    uicls.Container(name='push', parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, height=4)
                    recipients = info.numberOfRecipients
                    txt = mls.UI_GENERIC_AWARDEDTIME % {'times': recipients}
                    uicls.Label(text=txt, parent=wnd.sr.therestcontainer, align=uiconst.TOTOP, autowidth=False, fontsize=9, linespace=9, uppercase=1, letterspace=1)
                elif getattr(wnd.sr.abstractinfo, 'categoryID', None) == const.categoryBlueprint:
                    wnd.sr.isBlueprint = True
            elif wnd.sr.isCorporation:
                parallelCalls = []
                if wnd.sr.corpinfo is None:
                    parallelCalls.append((sm.RemoteSvc('corpmgr').GetPublicInfo, (itemID,)))
                else:
                    parallelCalls.append((ReturnNone, ()))
                parallelCalls.append((sm.GetService('faction').GetFaction, (itemID,)))
                if wnd.sr.warfactioninfo is None:
                    parallelCalls.append((sm.GetService('facwar').GetCorporationWarFactionID, (itemID,)))
                else:
                    parallelCalls.append((ReturnNone, ()))
                (corpinfo, factionID, warFaction,) = uthread.parallel(parallelCalls)
                wnd.sr.corpinfo = wnd.sr.corpinfo or corpinfo
                allianceid = wnd.sr.corpinfo.allianceID
                uthread.new(self.ShowRelationshipIcon, wnd, None, itemID, allianceid)
                uicls.Label(text='%s: %s' % (mls.UI_INFOWND_HEADQUARTERS, cfg.evelocations.Get(wnd.sr.corpinfo.stationID).name), parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, autowidth=False, state=uiconst.UI_DISABLED)
                uicls.Container(name='push', parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, height=4)
                uicls.Line(parent=wnd.sr.captioncontainer, align=uiconst.TOTOP)
                self.RecalcCaptionContainer(wnd, wnd.sr.captioncontainer)
                memberDisp = None
                if factionID or warFaction:
                    faction = cfg.eveowners.Get(factionID) if factionID else cfg.eveowners.Get(warFaction)
                    logo = uiutil.GetLogoIcon(itemID=faction.ownerID, parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, hint=mls.UI_INFOWND_CLICKFORFACTIONINFO, OnClick=(self._Info__PreFormatWnd,
                     wnd,
                     faction.typeID,
                     faction.ownerID), size=64, ignoreSize=True)
                    wnd.sr.subinfolinkcontainer.height = 64
                    memberDisp = cfg.eveowners.Get(faction.ownerID).name
                if allianceid:
                    alliance = cfg.eveowners.Get(allianceid)
                    logo = uiutil.GetLogoIcon(itemID=allianceid, align=uiconst.TOLEFT, parent=wnd.sr.subinfolinkcontainer, OnClick=(self._Info__PreFormatWnd,
                     wnd,
                     alliance.typeID,
                     allianceid), hint=mls.UI_INFOWND_CLICKFORALLIANCEINFO, state=uiconst.UI_NORMAL, size=64, ignoreSize=True)
                    wnd.sr.subinfolinkcontainer.height = 64
                    memberDisp = cfg.eveowners.Get(allianceid).name
                if memberDisp is not None:
                    uicls.Container(name='push', parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOLEFT, width=4)
                    uicls.Label(text=mls.UI_INFOWND_MEMBEROFALLIANCE % {'allianceName': memberDisp}, parent=wnd.sr.subinfolinkcontainer, align=uiconst.TOALL, top=4, left=0, autowidth=False, autoheight=False)
            elif wnd.sr.isAlliance:
                if wnd.sr.allianceinfo is None:
                    wnd.sr.allianceinfo = sm.GetService('alliance').GetAlliance(itemID)
                uthread.new(self.ShowRelationshipIcon, wnd, None, None, itemID)
            elif wnd.sr.isFaction:
                if wnd.sr.factioninfo is None:
                    wnd.sr.factioninfo = sm.GetService('faction').GetFactionEx(itemID)
                uicls.Label(text='%s: %s' % (mls.UI_INFOWND_HEADQUARTERS, cfg.evelocations.Get(wnd.sr.factioninfo.solarSystemID).name), parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, autowidth=False, state=uiconst.UI_DISABLED)
                uicls.Container(name='push', parent=wnd.sr.captioncontainer, align=uiconst.TOTOP, height=4)
                uicls.Line(parent=wnd.sr.captioncontainer, align=uiconst.TOTOP)
                self.RecalcCaptionContainer(wnd, wnd.sr.captioncontainer)
            invtype = cfg.invtypes.Get(typeID)
            if invtype.groupID == const.groupWormhole:
                desc2 = ''
                slimItem = sm.StartService('michelle').GetItem(itemID)
                if slimItem:
                    desc += '<br>'
                    desc += getattr(mls, 'UI_INFOWND_WORMHOLE_DESTDESC_%s' % slimItem.otherSolarSystemClass)
                    maxStableMass = slimItem.maxStableMAss
                    if slimItem.wormholeAge >= 3:
                        desc2 += mls.UI_INFOWND_WORMHOLE_AGE4 + '<br>'
                    elif slimItem.wormholeAge >= 2:
                        desc2 += mls.UI_INFOWND_WORMHOLE_AGE3 + '<br>'
                    elif slimItem.wormholeAge >= 1:
                        desc2 += mls.UI_INFOWND_WORMHOLE_AGE2 + '<br>'
                    elif slimItem.wormholeAge >= 0:
                        desc2 += mls.UI_INFOWND_WORMHOLE_AGE1 + '<br>'
                    desc2 += '<br>'
                    if slimItem.wormholeSize < 0.5:
                        desc2 += mls.UI_INFOWND_WORMHOLE_REMAININGMASS3 + '<br>'
                    elif slimItem.wormholeSize < 1:
                        desc2 += mls.UI_INFOWND_WORMHOLE_REMAININGMASS2 + '<br>'
                    else:
                        desc2 += mls.UI_INFOWND_WORMHOLE_REMAININGMASS1 + '<br>'
                    if desc2:
                        desc += '<br><br><hr><br>' + desc2
            wnd.HideGoBack()
            wnd.HideGoForward()
            if not headerOnly:
                self.GetWndData(wnd, typeID, itemID, parentID=parentID)
                historyIdx = None
                if historyData is None:
                    if wnd.sr.historyIdx is not None:
                        wnd.sr.history = wnd.sr.history[:(wnd.sr.historyIdx + 1)]
                    history = (typeID,
                     itemID,
                     parentID,
                     len(wnd.sr.history),
                     rec,
                     abstractinfo)
                    wnd.sr.history.append(history)
                    wnd.sr.historyIdx = None
                else:
                    (_typeID, _itemID, _parentID, historyIdx, _rec, _abstractinfo,) = historyData
                    wnd.sr.historyIdx = historyIdx
                if len(wnd.sr.history) > 1:
                    if historyIdx != 0:
                        if historyIdx:
                            wnd.GoBack = (self.Browse, wnd.sr.history[(historyIdx - 1)], wnd)
                        else:
                            wnd.GoBack = (self.Browse, wnd.sr.history[-2], wnd)
                        wnd.ShowGoBack()
                    if historyIdx is not None and historyIdx != len(wnd.sr.history) - 1:
                        wnd.GoForward = (self.Browse, wnd.sr.history[(historyIdx + 1)], wnd)
                        wnd.ShowGoForward()
            else:
                desc = ''
                bio = None
            if wnd is None or wnd.destroyed:
                return
            tabgroup = []
            i = 0
            for (listtype, subtabs,) in wnd.sr.infotabs:
                items = wnd.sr.data[listtype]['items']
                tabname = wnd.sr.data[listtype]['name']
                if subtabs:
                    subtabgroup = []
                    for (sublisttype, subsubtabs,) in subtabs:
                        subitems = wnd.sr.data[sublisttype]['items']
                        subtabname = wnd.sr.data[sublisttype]['name']
                        if len(subitems):
                            subtabgroup.append([subtabname,
                             wnd.sr.scroll,
                             self,
                             (wnd, sublisttype, None)])

                    if subtabgroup:
                        _subtabs = uicls.TabGroup(name='%s_subtabs' % tabname.lower(), parent=wnd.sr.subcontainer, idx=0, tabs=subtabgroup, groupID='infowindow_%s' % sublisttype, autoselecttab=0)
                        tabgroup.append([tabname,
                         wnd.sr.scroll,
                         self,
                         (wnd,
                          'selectSubtab',
                          None,
                          _subtabs),
                         _subtabs])
                elif len(items):
                    tabgroup.append([tabname,
                     wnd.sr.scroll,
                     self,
                     (wnd, listtype, None)])

            for (listtype, funcName,) in wnd.sr.dynamicTabs:
                if listtype == mls.UI_GENERIC_NOTES:
                    tabgroup.append([listtype,
                     wnd.sr.notesedit,
                     self,
                     (wnd, listtype, funcName)])
                else:
                    tabgroup.append([listtype,
                     wnd.sr.scroll,
                     self,
                     (wnd, listtype, funcName)])

            widthRequirements = [MINWIDTH]
            if not headerOnly and wnd.sr.data['buttons']:
                btns = uicls.ButtonGroup(btns=wnd.sr.data['buttons'], parent=wnd.sr.subcontainer, idx=0, unisize=0)
                totalBtnWidth = 0
                for btn in btns.children[0].children:
                    totalBtnWidth += btn.width

                widthRequirements.append(totalBtnWidth)
            if desc:
                tabgroup.insert(0, [mls.UI_GENERIC_DESCRIPTION,
                 wnd.sr.descedit,
                 self,
                 (wnd,
                  'readOnlyText',
                  None,
                  desc)])
            if not util.IsNPC(itemID) and bio:
                tabgroup.insert(0, [mls.UI_GENERIC_BIO,
                 wnd.sr.descedit,
                 self,
                 (wnd,
                  'readOnlyText',
                  None,
                  bio)])
            if len(tabgroup):
                wnd.sr.maintabs = uicls.TabGroup(name='maintabs', parent=wnd.sr.subcontainer, idx=0, tabs=tabgroup, groupID='infowindow')
                widthRequirements.append(wnd.sr.maintabs.totalTabWidth + 16)
            if len(widthRequirements) > 1:
                height = MINHEIGHTREGULAR
                if typeID == const.typeMedal:
                    height = MINHEIGHTMEDAL
                wnd.SetMinSize([max(widthRequirements), height])
            self.lastActive = wnd
            self.RecalcCaptionContainer(wnd, wnd.sr.captioncontainer)
            self.RecalcTheRestContainer(wnd, wnd.sr.therestcontainer)
            wnd.sr.toparea.state = uiconst.UI_PICKCHILDREN
            if headerOnly:
                wnd.height = wnd.sr.toparea.parent.height
            wnd.HideLoad()
            wnd.ShowHeaderButtons(1)
            wnd.IsBusy = 0
            self.loading = 0
        except BadArgs as e:
            if not wnd.destroyed:
                wnd.HideLoad()
                wnd.ShowHeaderButtons(1)
                wnd.IsBusy = 0
                self.loading = 0
                self.ShowError(wnd, e.args)
            sys.exc_clear()
        except:
            if not wnd.destroyed:
                wnd.HideLoad()
                wnd.ShowHeaderButtons(1)
                wnd.IsBusy = 0
                self.loading = 0
                raise
            sys.exc_clear()