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
                    sm.GetService('gameui').MessageBox(result2, "Dscanner Exception") 
                except:
                    print "exception in safetycheck"
        return wrapper

    @safetycheck
    def GetGetGet(self, *args):
        (config, value,) = args
        self.dir_rangeinput.SetValue(value*14959800)

    form.Scanner.GetGetGet = GetGetGet

    @safetycheck
    def SetSetSet(self, *args):
        uthread.new(self.NewScan)

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

    form.Scanner.NewScan = NewScan

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
                else:
                    maxDist = settings.user.ui.Get('dir_scanrange')*1000
                    dist = maxDist
                    lastDist = None
                    try:
                        lastDist = self.distData[entryname]
                    except:
                        lastDist = maxDist
                    if dist > lastDist:
                        dist = lastDist
                    else:
                        self.distData[entryname] = dist
                    diststr = util.FmtDist(dist, maxdemicals=1)
                groupID = cfg.invtypes.Get(typeID).groupID
                if not (eve.session.role & (service.ROLE_GML | service.ROLE_WORLDMOD)):
                    if (groupID == const.groupCloud):
                        continue
                hint = entryname
                data = util.KeyVal()
                data.label = ('%s<t>%s<t>%s' % (entryname,
                 typeinfo.name,
                 diststr))
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
        old_apply_attributes(self, attributes)

        self.sr.destroyBtn.Close()
        self.distData = dict()

        dslider = uix.GetSlider('slider', self.sr.useoverview.parent.parent, 'scandist', 1, 14.4, 'Range', '', uiconst.TOPRIGHT, 150, 18, 0, 15, getvaluefunc=self.GetGetGet, endsliderfunc=self.SetSetSet, increments=(1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5,5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 12.5, 13, 13.5, 14, 14.4), underlay=0)

        self.dir_rangeinput = uicls.SinglelineEdit(name='edit2', parent=self.sr.useoverview.parent.parent, ints=(1, None), align=uiconst.TOPRIGHT, pos=(5, 36, 78, 0), maxLength=(len(str(sys.maxint))*2))
        self.dir_rangeinput.SetValue(settings.user.ui.Get('dir_scanrange', 1000))
        self.dir_rangeinput.OnReturn = self.DirectionSearch

    form.Scanner.ApplyAttributes = MyApplyAttributes

except:
    print "Dscanner broken."
