import copy
import svc
import service
import uix
import uiconst
import form.Scanner
from foo import Vector3
from eve import eve
import sys

if (form.Scanner.ApplyAttributes.__func__.func_name is not 'ProbeHelperApplyAttributes'):
    old_apply_attributes = form.Scanner.ApplyAttributes

def ContractProbes(self, *args):
    probeData = sm.GetService("scanSvc").GetProbeData()
    if probeData == {}:
        return
    
    avg = Vector3( 0,0,0 )
    min_range = const.scanProbeNumberOfRangeSteps
    for key in probeData:
        min_range = min( min_range, probeData[key].rangeStep )
        avg = avg + probeData[key].destination
    if (min_range <= 1):
        return
    avg = avg / len(probeData)

    for key in probeData:
        destination = (probeData[key].destination + avg)/2
        sm.GetService("scanSvc").SetProbeDestination(key, destination)
        sm.GetService("scanSvc").SetProbeRangeStep(key, probeData[key].rangeStep - 1)
    self.UpdateProbeSpheres()

form.Scanner.ContractProbes = ContractProbes

def ScLoadIgnoreList(self, *args):
    sm.services["scanSvc"].resultsIgnored = copy.deepcopy(ignoreData[eve.session.solarsystemid])
    self.DoRefresh()
form.Scanner.ScLoadIgnoreList = ScLoadIgnoreList

def ScSaveIgnoreList(self, *args):
    ignoreData[eve.session.solarsystemid] = copy.deepcopy(sm.services["scanSvc"].resultsIgnored)  
form.Scanner.ScSaveIgnoreList = ScSaveIgnoreList

def ScLoadIgnoreList2(self, *args):
    sm.services["scanSvc"].resultsIgnored = copy.deepcopy(ignoreData[eve.session.solarsystemid])
    self.DoRefresh()
form.Scanner.ScLoadIgnoreList2 = ScLoadIgnoreList2

def ScSaveIgnoreList2(self, *args):
    ignoreData[eve.session.solarsystemid] = copy.deepcopy(sm.services["scanSvc"].resultsIgnored)  
form.Scanner.ScSaveIgnoreList2 = ScSaveIgnoreList2

def ExpandProbes(self, *args):
    probeData = sm.GetService("scanSvc").GetProbeData()
    if probeData == {}:
        return

    avg = Vector3( 0,0,0 )
    max_range = 1
    for key in probeData:
        max_range = max(max_range, probeData[key].rangeStep)
        avg = avg + probeData[key].destination
    if (max_range >= const.scanProbeNumberOfRangeSteps):
        return
    avg = avg / len(probeData)
    
    for key in probeData:
        destination = (2*probeData[key].destination) - avg
        sm.GetService("scanSvc").SetProbeDestination(key, destination)
        sm.GetService("scanSvc").SetProbeRangeStep(key, probeData[key].rangeStep + 1)
    self.UpdateProbeSpheres()

form.Scanner.ExpandProbes = ExpandProbes        
        
def SendProbes(self, *args):
    try:
        selected = self.sr.resultscroll.GetSelected()
        points = []
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

        probeData = sm.GetService("scanSvc").GetProbeData()
        if probeData == {}:
            return
        avg = Vector3( 0,0,0 )
        for key in probeData:
           avg = avg + probeData[key].destination
        avg = avg / len(probeData)

        for key in probeData:
            destination = target + probeData[key].destination - avg
            sm.GetService("scanSvc").SetProbeDestination(key, destination)

        self.UpdateProbeSpheres()
    except:
        print "SendProbes: an exception occured\n"
        print sys.exc_info()
        pass

form.Scanner.SendProbes = SendProbes

def SaveLoadProbePositions(self, *args):
    probeData = sm.GetService("scanSvc").GetProbeData()
    if probeData == {}:
        return

    avg = Vector3( 0,0,0 )
    for key in probeData:
       avg = avg + probeData[key].destination
    avg = avg / len(probeData)

    shift = uicore.uilib.Key(uiconst.VK_SHIFT)
    if( shift ):
        pos = []
        for key in probeData:
            pos.append( [probeData[key].destination - avg, probeData[key].rangeStep] )
        settings.public.ui.Set("ProbePositions%d"%(args[0]), pos)
        return
    
    pos = settings.public.ui.Get("ProbePositions%d"%(args[0]),[])
    if( pos == [] ):
        return
        
    i = 0
    for key in probeData:
        sm.GetService("scanSvc").SetProbeDestination(key, pos[i][0] + avg)
        sm.GetService("scanSvc").SetProbeRangeStep(key, pos[i][1])
        i = i + 1
        if( i >= len(pos) ):
            break
    self.UpdateProbeSpheres()

def SaveLoadProbePositions1(self, *args):
    SaveLoadProbePositions(self, 1, args)

def SaveLoadProbePositions2(self, *args):
    SaveLoadProbePositions(self, 2, args)

def SaveLoadProbePositions3(self, *args):
    SaveLoadProbePositions(self, 3, args)
        
form.Scanner.SaveLoadProbePositions = SaveLoadProbePositions
form.Scanner.SaveLoadProbePositions1 = SaveLoadProbePositions1
form.Scanner.SaveLoadProbePositions2 = SaveLoadProbePositions2
form.Scanner.SaveLoadProbePositions3 = SaveLoadProbePositions3

def ProbeHelperApplyAttributes(self, attributes):
    old_apply_attributes(self, attributes)
    
    self.sr.destroyBtn.Close()
    btn = uix.GetBigButton(32, self.sr.systemTopParent, left=120)
    btn.OnClick = self.SaveLoadProbePositions1
    btn.hint = "Saved probe positions 1: SHIFT-CLICK TO SAVE, CLICK TO LOAD"
    uix.MapSprite('44_60', btn.sr.icon)
    self.sr.saveloadBtn = btn

    btn = uix.GetBigButton(32, self.sr.systemTopParent, left=152)
    btn.OnClick = self.SaveLoadProbePositions2
    btn.hint = "Saved probe positions 2: SHIFT-CLICK TO SAVE, CLICK TO LOAD"
    uix.MapSprite('44_61', btn.sr.icon)
    self.sr.saveloadBtn2 = btn

    btn = uix.GetBigButton(32, self.sr.systemTopParent, left=184)
    btn.OnClick = self.SaveLoadProbePositions3
    btn.hint = "Saved probe positions 3: SHIFT-CLICK TO SAVE, CLICK TO LOAD"
    uix.MapSprite('44_62', btn.sr.icon)
    self.sr.saveloadBtn3 = btn

    btn = uix.GetBigButton(32, self.sr.systemTopParent, left=228)
    btn.OnClick = self.ContractProbes
    btn.hint = "CONTRACT PROBES"
    uix.MapSprite('44_43', btn.sr.icon)
    self.sr.contractBtn = btn
 
    btn = uix.GetBigButton(32, self.sr.systemTopParent, left=260)
    btn.OnClick = self.ExpandProbes
    btn.hint = "EXPAND PROBES"
    uix.MapSprite('44_44', btn.sr.icon)
    self.sr.expandBtn = btn

    btn = uix.GetBigButton(32, self.sr.systemTopParent, left=304)
    btn.OnClick = self.SendProbes
    btn.hint = "SEND PROBES TO SELECTED RESULT"
    uix.MapSprite('44_59', btn.sr.icon)
    self.sr.sendBtn = btn

    btn = uix.GetBigButton(32, self.sr.systemTopParent, left=352)
    btn.OnClick = self.ScSaveIgnoreList
    btn.hint = "SAVE IGNORE LIST"
    uix.MapSprite('77_21', btn.sr.icon)
    self.sr.saveignoreBtn = btn

    btn = uix.GetBigButton(32, self.sr.systemTopParent, left=384)
    btn.OnClick = self.ScLoadIgnoreList
    btn.hint = "LOAD IGNORE LIST"
    uix.MapSprite('44_47', btn.sr.icon)
    self.sr.loadignoreBtn = btn
	
    btn = uix.GetBigButton(32, self.sr.systemTopParent, left=416)
    btn.OnClick = self.ScSaveIgnoreList2
    btn.hint = "SAVE IGNORE LIST2"
    uix.MapSprite('77_21', btn.sr.icon)
    self.sr.saveignoreBtn = btn

    btn = uix.GetBigButton(32, self.sr.systemTopParent, left=448)
    btn.OnClick = self.ScLoadIgnoreList2
    btn.hint = "LOAD IGNORE LIST2"
    uix.MapSprite('44_47', btn.sr.icon)
    self.sr.loadignoreBtn = btn

form.Scanner.ApplyAttributes = ProbeHelperApplyAttributes

global ignoreData
ignoreData = dict()
ignoreData[eve.session.solarsystemid] = set()