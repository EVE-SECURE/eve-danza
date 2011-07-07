7/7/2011

This is the first version of the Eve Danza injection suite. Over time, I will update the included scripts and the injector. The current injector, lolpy, was created by wibiti from PublicDemands (thanks!).

The current scripts and their features:

ProbeHelperSE:
- Improved upon the original ProbeHelper by wibiti
- Averaged selection position (instead of going to first item on list)
- Save/load probe positions; shift click to save result location, and control click to save current probe position, left-click to send probes to the saved location
- Error reporting

Dscanner:
- Added slider to adjust d-scan range (from 1AU to 14.4AU, in .5 steps)
- Distance approximation; the script will save the last max distance for any given result, so that after scanning at various ranges the results have their distance approximated


TO-DO:

ProbeHelperSE:
- Send to celestials
- Save/load ignorelist
- Alternative scanning mode using 2 sets of 4 probes

Dscanner:
- "One-click" approximation by Quicksort (specific result) and Bucketsort (all results)
- Distance stored by itemID instead of entryname
- "One-click" celestial conescan
- Global storage for distance results
- Removing/reducing scan timeout duration

Injector:
- GUI support
- Simultaneous injection of multiple files
- Automated injection
- Better multi-client support


Email me for suggestion or bug report.