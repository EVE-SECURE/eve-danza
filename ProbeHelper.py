try:
    import uix
    import uiconst
    import form.Scanner
    from foo import Vector3
    import sys
    from traceback import format_exception


    try:
        old_apply_attributes
    except NameError:
        old_apply_attributes = form.Scanner.ApplyAttributes

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
        try:
            data = selected[0].result.data
        except:
            return
            
        if isinstance(data, float):
            data = selected[0].result.pos
        
        if not isinstance(data, Vector3):
            data = data.point
         
        scanSvc = sm.GetService("scanSvc")
        probeData = [(k,v) for (k,v) in scanSvc.GetProbeData().iteritems() if v.state == const.probeStateIdle]
        if len(probeData) == 0:
            return

        avg = sum( (v.destination for (k,v) in probeData), Vector3() ) / len(probeData)

        for (k,v) in probeData:
            destination = data + v.destination - avg
            scanSvc.SetProbeDestination(k, destination)
            
        self.UpdateProbeSpheres()

    form.Scanner.SendProbes = SendProbes

    @safetycheck
    def SaveLoadProbePositions(self, *args):
        scanSvc = sm.GetService("scanSvc")
        probeData = [(k,v) for (k,v) in scanSvc.GetProbeData().iteritems() if v.state == const.probeStateIdle]
        if len(probeData) == 0:
            return

        settingsName = 'ProbePositions2' if uicore.uilib.Key(uiconst.VK_CONTROL) else 'ProbePositions'

        if uicore.uilib.Key(uiconst.VK_SHIFT):
            settings.user.ui.Set(settingsName, [(v.destination, v.rangeStep) for (k,v) in probeData])
            return
        
        pos = settings.user.ui.Get(settingsName, [])
        if( pos == [] ):
            return
            
        for ((probekey, probevalue), (dest,rstep)) in zip(probeData, pos):
            scanSvc.SetProbeDestination(probekey, dest)
            scanSvc.SetProbeRangeStep(probekey, rstep)
        self.UpdateProbeSpheres()
            
    form.Scanner.SaveLoadProbePositions = SaveLoadProbePositions


    @safetycheck
    def MyApplyAttributes(self, attributes):
        old_apply_attributes(self, attributes)
        
        self.sr.destroyBtn.Close()
        btn = uix.GetBigButton(32, self.sr.systemTopParent, left=120)
        btn.OnClick = self.SaveLoadProbePositions
        btn.hint = "Load Probe Positions\nShift-Click to Save Probe Positions"
        btn.sr.icon.LoadIcon('44_03')
        self.sr.saveloadBtn = btn

        btn = uix.GetBigButton(32, self.sr.systemTopParent, left=164)
        btn.OnClick = self.ContractProbes
        btn.hint = "Shrink Probe Pattern"
        btn.sr.icon.LoadIcon('44_43')
        self.sr.contractBtn = btn
     
        btn = uix.GetBigButton(32, self.sr.systemTopParent, left=200)
        btn.OnClick = self.ExpandProbes
        btn.hint = "Expand Probe Pattern"
        btn.sr.icon.LoadIcon('44_44')
        self.sr.expandBtn = btn

        btn = uix.GetBigButton(32, self.sr.systemTopParent, left=244)
        btn.OnClick = self.SendProbes
        btn.hint = "Send Probes to Selected Result"
        btn.sr.icon.LoadIcon('44_59')
        self.sr.sendBtn = btn

    form.Scanner.ApplyAttributes = MyApplyAttributes

except:
    print "ProbeHelper broken."
