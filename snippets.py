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