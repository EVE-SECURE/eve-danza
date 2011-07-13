try:
    import uix
    import uiconst
    import form.Scanner
    from foo import Vector3
    import sys
    from traceback import format_exception
    import copy
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
                    sm.GetService('gameui').MessageBox(result2, "OrbitHelper Exception") 
                except:
                    print "exception in safetycheck"
        return wrapper
		
    @safetycheck
    def GetGetGet(self, *args):
        (config, value,) = args
        settings.user.ui.Set('defaultOrbitDist', value)
        sm.ScatterEvent('OnDistSettingsChange')

    form.Scanner.GetGetGet = GetGetGet

    @safetycheck
    def SetSetSet(self, *args):
        return

    form.Scanner.SetSetSet = SetSetSet


    @safetycheck
    def MyApplyAttributes(self, attributes):
        old_apply_attributes(self, attributes)

        dslider = uix.GetSlider('slider', self.sr.useoverview.parent.parent, 'orbitdist', 500, 30000, 'Orbit', '', uiconst.TOPRIGHT, 150, 18, 0, 15, getvaluefunc=self.GetGetGet, endsliderfunc=self.SetSetSet, increments=(500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000, 20000, 21000, 22000, 23000, 24000, 25000, 26000, 27000, 28000, 29000, 30000), underlay=0)

    form.Scanner.ApplyAttributes = MyApplyAttributes

except:
    print "OrbitHelper broken."
