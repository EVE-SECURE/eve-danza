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

# modules in cmd
def CmdActivateHighPowerSlot1(self, *args):
    self._cmdshipui(0, 0)

def _cmdshipui(self, sidx, gidx):
    shipui = uicore.layer.shipui
    if shipui.isopen:
        shipui.OnF(sidx, gidx)

# modules in shipui
def OnF(self, sidx, gidx):
    slot = self.sr.slotsByOrder.get((gidx, sidx), None)
    if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
        uthread.new(slot.sr.module.Click)
    else:
        uthread.new(eve.Message, 'Disabled')

# Overload in cmd
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

# Overload in shipui

def OnFKeyOverload(self, sidx, gidx):
    slot = self.sr.slotsByOrder.get((gidx, sidx), None)
    if slot and slot.sr.module and slot.sr.module.state == uiconst.UI_NORMAL:
        if hasattr(slot.sr.module, 'ToggleOverload'):
            uthread.new(slot.sr.module.ToggleOverload)
    else:
        uthread.new(eve.Message, 'Disabled')


# set speed + direciton
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