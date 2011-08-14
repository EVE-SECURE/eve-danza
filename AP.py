try:
	import util.Moniker
	util.Moniker.WarpToStuffAutopilot = lambda s, x: s.WarpToStuff("item", x, minRange=0)
except:
	pass