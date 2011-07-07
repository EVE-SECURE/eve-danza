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
            return

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
    def MyApplyAttributes(self, attributes):
        old_apply_attributes(self, attributes)
        
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

    form.Scanner.ApplyAttributes = MyApplyAttributes

except:
    print "ProbeHelper broken."
