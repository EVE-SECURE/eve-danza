LAST UPDATE: 7/31/2011

This is the Eve Danza injection suite. Over time, I will update the included scripts and the injector. Thanks to Wibiti for the injector and other help!

The current scripts and their features:

ScanHelper:
- Improved upon the original ProbeHelper by wibiti
- Averaging results on multiple selections (instead of going to the first)
- Save/load probe positions; shift click to save result location, and control click to save current probe position, left-click to send probes to the saved location
- Listing of ship types as soon as possible for combat scanner (hidden by default)
- Send probes to active item
- Added slider to adjust d-scan range (from 1AU to 14.4AU, in .5 steps)
- Distance approximation; the script will save the last max distance for any given result, so that after scanning at various ranges the results have their distance approximated
- Display of itemID in parenthesese behind item name

ActiveItemHelper:
- Added sliders for default orbit and keep range distance adjustment
- WatchWarpOff: shift-click to start watching balls; left-click again to disable
- GetNearbyItem: returns the item that is closest to the current active item

LocalWatch:
-"Set Report Channel" sets the default report channel
-"Report Local" reports the local hostiles with their names as links and their alliance name (or corp name, if not in an alliance)
- Currently capping local hostile count to a max of 50, and a max report of 15 (due to rather slow service call response in iterations)

Email me for suggestion or bug report.