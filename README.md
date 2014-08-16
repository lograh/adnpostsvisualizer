adnpostsvisualizer
==================

a toy for visualizing a user's ADN activity

Usage: python adnpostsvisualizer.py <options>

Default behaviour to note: 
  Attempts to use a local file for caching data (can be overridden with --nocache).
    This defaults to USERIDcache.json (can be changed with --cachefile) and will be created if it does not exist.
    If the cachefile does exist, it will be read in, parsed, and then clobbered with new data (regardless of success
    of parsing).
  Default output file is postscalendar.png (can be changed with --filename). This does not check for filename
    collisions on output. An existing file of the same name will be overwritten.

ToDo:
  - More error checking on passed/read arguments
  - More error checking in general, honestly
  - Fancier date range options.
  - Better type handling
  - Custom week start day
  
