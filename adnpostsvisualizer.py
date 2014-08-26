########  Uses quite a few libraries, some third party. I didn't check these in any way
########  My version of Python is 2.7.5. I have no idea what this does on any other version
######## 
########  started on the ADN community hack day 9Aug2014 by @lograh
########     anyone is welcome to use and modify as they see fit, just don't claim your modifications are mine
########     Given it is my first Python project, I'd highly recommend modifying it. :)
#########################################
#### KNOWN ISSUES :
# if desiredweeks runs back past a user's first post this crashes
# very easy to break if you pass it something clearly not valid, like setting maxshade to "happy happy joy joy" or somesuch
#
#########################################
# uses requests for the http getting and parsing 
# uses datetime/dateutil for the time manipulation
# uses Pillow to get PIL for image creation and manipulation
# uses argparse for command line argument support
# uses json to handle data parsing and cache file read/write
# uses numpy for standard deviation calculation
# used math at one point, but I think I've removed that since. may be safe to delete that? :)
# uses threading for multithread support
# uses pickle for the argfile support (can't json or iterate a Namespace)

import requests
from datetime import timedelta, datetime, tzinfo
from dateutil import parser
from PIL import Image, ImageDraw, ImageFont
import json
import argparse
import math
import numpy
import threading
import pickle

threads = []

def not_negative(string):
      value = int(string)
      if value < 0 :
        msg = "%r is less than 0" % string
        raise argparse.ArgumentTypeError(msg)
      return value

class writecache (threading.Thread):
  def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
  def run(self):
    if args.verbose or args.lessverbose :
      print "Starting " + self.name
    self.datatowrite = []
    if args.mincache :
      if args.verbose or args.lessverbose :
        print('mincache on, trimming data')
      self.indexes = ['created_at','num_stars','num_replies','num_reposts','id','entities']
      for self.x in range(len(timestamps)) :
        self.tempdata={}
        for self.y in self.indexes :
          self.tempdata[self.y]=timestamps[self.x][self.y]
        self.tempdata['user']={'username': timestamps[self.x]['user']['username']}
        self.datatowrite.append(self.tempdata)
        if args.verbose :
          print(self.datatowrite[self.x])
    else :
      if args.verbose or args.lessverbose :
        print('mincache off')
      for self.x in range(len(timestamps)) :
        self.datatowrite.append(timestamps[self.x])
    if args.verbose or args.lessverbose :
      print('writing new cache')
    self.f = open(args.cachefile, 'w+b')
    self.f.seek(0)
    json.dump(self.datatowrite, self.f)
    self.f.close()
    if args.verbose or args.lessverbose :
      print('Wrote ' + str(len(self.datatowrite)))
      print('Exiting ' + self.name)

################################## Parse command line args
argparser = argparse.ArgumentParser(description='Makes a picture of blocks of colour. At a minimum, you need to pass a userid (or an argfile containing one).', epilog='Uses cachefile named USERIDcache.json (will be created if missing) in current working directory')
argparser.add_argument('-id', '--userid', nargs='?', metavar='Num', default='-1', help='ID of user to get posts from')
argparser.add_argument('-f', '--filename', nargs='?', metavar='string', default='postschart.png', help='output chart filename')
argparser.add_argument('-wk', '--desiredweeks', type=not_negative, metavar='Num', nargs='?', default='5', help='number of weeks to chart')
argparser.add_argument('-dw', '--daywidth', type=not_negative, metavar='Num', nargs='?', default='10', help='width of a day in the week (7 of these plus the legend and months define height of chart)')
argparser.add_argument('-ww', '--weekwidth', type=not_negative, nargs='?', metavar='Num', default='0', help='width of a single week')
argparser.add_argument('-ch', '--chartheight', metavar='Num', nargs='?', default='default', help='total height of chart (may cause daywidth to shrink)')
argparser.add_argument('-cw', '--chartwidth', type=not_negative, metavar='Num', nargs='?', default='0', help='total width of chart (may be longer for legend, may cause weekwidth to shrink)')
argparser.add_argument('-bd', '--boundary', type=not_negative, metavar='Num', nargs='?', default=1, help='boundary around days (double this between days/weeks)')
argparser.add_argument('-bk', '--boundaryshade', nargs='?', metavar='string', default='white', help='colour for the boundaries')
argparser.add_argument('-mf', '--monthfontfile', nargs='?', metavar='string', default='none', help='fontfile for the month text ("none" to turn off months)')
argparser.add_argument('-lf', '--legendfontfile', nargs='?', metavar='string', default='default', help='fontfile for the legend text (defaults to monthfontfile, "none" to turn off legends)')
argparser.add_argument('-mpts', '--monthtextpoints', type=not_negative, nargs='?', metavar='Num', default='13', help='point size for the month text (defaults to 13)')
argparser.add_argument('-lpts', '--legendtextpoints', type=not_negative, nargs='?', metavar='Num', default='12', help='point size for the legend text (defaults to 12)')
argparser.add_argument('-mc', '--monthtextcolour', nargs='?', metavar='string', default='black', help='colour for month text (defaults to black)')
argparser.add_argument('-lc', '--legendtextcolour', nargs='?', metavar='string', default='default', help='colour for legend text (defaults to monthtextcolour')
argparser.add_argument('-nf', '--namefontfile', nargs='?', metavar='string', default='default', help='fontfile for the name text (defaults to monthfontfile, "none" to turn off name)')
argparser.add_argument('-nc', '--nametextcolour', nargs='?', metavar='string', default='default', help='colour for name text (defaults to monthtextcolour')
argparser.add_argument('-npts', '--nametextpoints', type=not_negative, nargs='?', metavar='Num', default='12', help='point size for the name text (defaults to 12)')
argparser.add_argument('-nptf', '--nametextfudge', type=not_negative, nargs='?', metavar='Num', default='0', help='some text types just need extra padding for ascend/descenders')
argparser.add_argument('-lptf', '--legendtextfudge', type=not_negative, nargs='?', metavar='Num', default='0', help='some text types just need extra padding for ascend/descenders')
argparser.add_argument('-mptf', '--monthtextfudge', type=not_negative, nargs='?', metavar='Num', default='0', help='some text types just need extra padding for ascend/descenders')
argparser.add_argument('-no', '--noposts', nargs='?', metavar='string', default='#fcf6f4', help='colour for days without any posts')
argparser.add_argument('-gd', '--gradients', type=not_negative, metavar='Num', nargs='?', default='5', help='how many steps of colour')
argparser.add_argument('-gt', '--gradienttype', nargs='?', metavar='string', default='linear', help='style of gradient calculation (may override --gradients)')
argparser.add_argument('-min', '--minshade', nargs='?', metavar='"#rrggbb"', default='#f0ccc6', help='colour for days with min posts')
argparser.add_argument('-max', '--maxshade', nargs='?', metavar='"#rrggbb"', default='#cc5139', help='colour for days with max posts')
argparser.add_argument('--shades', nargs='?', metavar='list', default='default', help='list of the colours (in order) to use for days with posts')
argparser.add_argument('--halign', nargs='?', metavar='string', default='default', help='horizontal alignment on canvas')
argparser.add_argument('--valign', nargs='?', metavar='string', default='default', help='vertical alignment on canvas')
argparser.add_argument('-mo', '--monthseparator', nargs='?', metavar='string', default='default', help='colour for bars between months (defaults to boundaryshade)')
argparser.add_argument('-v1', '--verbose',  help='verbose output (not read from argfile)', action="store_true")
argparser.add_argument('-v0', '--lessverbose',  help='less verbose output (not read from argfile)', action="store_true")
argparser.add_argument('--cachefile', nargs='?', metavar='string', default='default', help='filename for cache')
argparser.add_argument('--mincache',  help='reduce cache usage (not read from argfile)', action="store_true")
argparser.add_argument('--nocache',  help='disable all cache usage (not read from argfile)', action="store_true")
argparser.add_argument('--offline',  help='offline mode (not read from argfile)', action="store_true")
argparser.add_argument('--auth_field', nargs='?', metavar='string', default='0', help='auth token header name')  #  turns out auth tokens aren't needed for just reading public posts
argparser.add_argument('--auth_value', nargs='?', metavar='string', default='0', help='auth token header value') #  I'm leaving them in for now, might expand this script to other stuff
argparser.add_argument('--argfile', nargs='?', metavar='string', default='default', help='filename for loading/saving arguments (will be merged, command set (not default) arguments have priority)')
argparser.add_argument('--resetargfile', help='wipe argfile and replace with whatever is from the command line (not read from argfile)', action="store_true")

args = argparser.parse_args()

#######################################  argfile work
if args.argfile != 'default' :
  if args.verbose or args.lessverbose :
    print('************************ reading in argfile')
  f = open(args.argfile, 'a+b')
  f.seek(0)
  tmpargs = []
  try:
    tmpargs = pickle.load(f)
  except:
    print('pickle hates loading from an empty file')
  f.close()
  try :
    parseargfile = len(tmpargs)
  except :
    parseargfile = 1
  if args.resetargfile == False and parseargfile != 0 :    ### if resetargfile is false, then run through args reading in argfile over default command lines
    if args.userid =='-1' :
      try : tmpargs.userid 
      except : 1
      else : args.userid = tmpargs.userid
    if args.filename == 'postschart.png' :
      try : tmpargs.filename
      except : 1
      else : args.filename = tmpargs.filename
    if args.desiredweeks == 5  :
      try : tmpargs.desiredweeks
      except : 1
      else : args.desiredweeks = tmpargs.desiredweeks
    if args.daywidth == 10  :
      try : tmpargs.daywidth
      except : 1
      else : args.daywidth = tmpargs.daywidth
    if args.chartheight =='default' :
      try : tmpargs.chartheight
      except : 1
      else : args.chartheight = tmpargs.chartheight
    if args.weekwidth == 0 :
      try : tmpargs.weekwidth
      except : 1
      else : args.weekwidth = tmpargs.weekwidth
    if args.chartwidth == 0 :
      try : tmpargs.chartwidth
      except : 1
      else : args.chartwidth = tmpargs.chartwidth
    if args.boundary == 1 :
      try : tmpargs.boundary
      except : 1
      else : args.boundary = tmpargs.boundary
    if args.boundaryshade == 'white'  :
      try : tmpargs.boundaryshade
      except : 1
      else : args.boundaryshade = tmpargs.boundaryshade
    if args.monthfontfile =='none'  :
      try : tmpargs.monthfontfile
      except : 1
      else : args.monthfontfile = tmpargs.monthfontfile
    if args.legendfontfile =='default'  :
      try : tmpargs.legendfontfile                    #####   this whole try: foo / except:1 / else: baz=foo pattern is the best I could find
      except : 1                 ##########################    the problem is python throws an exception if the a nonexistent foo is ever used 
      else : args.legendfontfile = tmpargs.legendfontfile #    Annoying it takes so many lines, but it is what it is.
    if args.monthtextpoints == 13 :
      try : tmpargs.monthtextpoints
      except : 1
      else : args.monthtextpoints = tmpargs.monthtextpoints
    if args.legendtextpoints == 12  :
      try : tmpargs.legendtextpoints
      except : 1
      else : args.legendtextpoints = tmpargs.legendtextpoints
    if args.monthtextcolour =='black' :
      try : tmpargs.monthtextcolour
      except : 1
      else : args.monthtextcolour = tmpargs.monthtextcolour
    if args.legendtextcolour == 'default' :
      try : tmpargs.legendtextcolour
      except : 1
      else : args.legendtextcolour = tmpargs.legendtextcolour
    if args.namefontfile =='default'  :
      try : tmpargs.namefontfile
      except : 1
      else : args.namefontfile = tmpargs.namefontfile
    if args.nametextcolour =='default' :
      try : tmpargs.nametextcolour
      except : 1
      else : args.nametextcolour = tmpargs.nametextcolour
    if args.nametextpoints == 12  :
      try : tmpargs.nametextpoints
      except : 1
      else : args.nametextpoints = tmpargs.nametextpoints
    if args.noposts =='#fcf6f4'  :
      try : tmpargs.noposts 
      except : 1
      else : args.noposts = tmpargs.noposts
    if args.gradients == 5 :
      try : tmpargs.gradients
      except : 1
      else : args.gradients = tmpargs.gradients
    if args.gradienttype == 'linear'  :
      try : tmpargs.gradienttype
      except : 1
      else : args.gradienttype = tmpargs.gradienttype
    if args.minshade =='#f0ccc6'  :
      try : tmpargs.minshade
      except : 1
      else : args.minshade = tmpargs.minshade
    if args.maxshade =='#cc5139'  :
      try : tmpargs.maxshade
      except : 1
      else : args.maxshade = tmpargs.maxshade
    if args.shades =='default'  :
      try : tmpargs.shades
      except : 1
      else : args.shades = tmpargs.shades
    if args.monthseparator =='default'  :
      try : tmpargs.monthseparator
      except : 1
      else : args.monthseparator = tmpargs.monthseparator   
    if args.auth_field =='0' :
      try : tmpargs.auth_field
      except : 1
      else :args.auth_field = tmpargs.auth_field 
    if args.auth_value =='0'  :
      try : tmpargs.auth_value
      except : 1
      else : args.auth_value = tmpargs.auth_value
    if args.cachefile == 'default' :
      try : tmpargs.cachefile
      except : 1
      else :  args.cachefile = tmpargs.cachefile
    if args.nametextfudge ==0 :
      try : tmpargs.nametextfudge
      except : 1
      else :args.nametextfudge = tmpargs.nametextfudge 
    if args.legendtextfudge ==0 :
      try : tmpargs.legendtextfudge
      except : 1
      else :args.legendtextfudge = tmpargs.legendtextfudge
    if args.monthtextfudge ==0 :
      try : tmpargs.monthtextfudge
      except : 1
      else :args.monthtextfudge = tmpargs.monthtextfudge
    if args.valign == 'default' :
      try : tmpargs.valign
      except : 1
      else :args.valign = tmpargs.valign
    if args.halign == 'default' :
      try : tmpargs.halign
      except : 1
      else :args.halign = tmpargs.halign
  if args.verbose or args.lessverbose :
    print('************************ writing out argfile')
  f = open(args.argfile, 'w+b')
  f.seek(0)
  pickle.dump(args, f)
  f.close()

headers = {}
headers[args.auth_field] = args.auth_value
nomonths = False
nolegends = False
noname = False

####### assigning overrides
if args.monthseparator == 'default' :
  args.monthseparator = args.boundaryshade
if args.gradienttype == 'stdev' :
  args.gradients = 5
elif args.gradienttype == 'highlights' :
  args.gradients = 4
if args.chartheight != 'default' :
  if int(args.chartheight) < 0 :
    args.chartheight = 0
  else :
    args.chartheight = int(args.chartheight)
if args.legendfontfile == 'default' :
  args.legendfontfile = args.monthfontfile
if args.namefontfile == 'default' :
  args.namefontfile = args.monthfontfile
if args.monthfontfile == 'none' :
  nomonths = True
if args.legendfontfile =='none' :
  nolegends = True
if args.namefontfile == 'none' :
  noname = True
if args.legendtextcolour == 'default' :
  args.legendtextcolour = args.monthtextcolour
if args.nametextcolour == 'default' :
  args.nametextcolour = args.monthtextcolour
if args.shades != 'default' :
  args.shades = json.loads(args.shades)
if args.cachefile == 'default' :
  args.cachefile = args.userid+"cache.json"

if args.verbose or args.lessverbose :
  print(args)
  print(headers)

####### setting up
duration = timedelta(weeks=args.desiredweeks)
sevendays = timedelta(days=7)
oneday = timedelta(days=1)
lasttime = datetime.utcnow()
endtime = lasttime - duration
timestamps = []
payload = { 'count': '200'}
indivpost = {}

#######################################  cacheing
if args.nocache == False :
  if args.verbose or args.lessverbose :
    print('************************ reading in cache')
  f = open(args.cachefile, 'a+b')
  f.seek(0)
  try:
    timestamps = json.load(f)
  except:
    print('json hates loading from an empty file')
  f.close()

if args.verbose or args.lessverbose :
  print('data length ' + str(len(timestamps)))

#################### fill cache
if args.offline == False :
  if args.verbose or args.lessverbose :
    print('not offline, entering cache update')
  if len(timestamps) != 0 :
    r = requests.get('https://api.app.net/users/' + args.userid + '/posts', params=payload, headers=headers)
    if args.verbose or args.lessverbose :
      print('call for newer posts')
    list = r.json()['data']
    timestamps.reverse()
    newestid = timestamps[-1]['id']
    while list[-1]['id'] > newestid :
      payload = {'before_id': list[-1]['id'], 'count': '200'}
      r = requests.get('https://api.app.net/users/' + args.userid + '/posts', params=payload, headers=headers)
      if args.verbose :
        print('more calling for newer posts')
      tmplist = r.json()['data']
      for x in tmplist : list.append(x)
    list.reverse()
    for x in list :
      if x['id'] > newestid :
        timestamps.append(x)
        if args.verbose :
          print('post id ' + x['id'] + ' appended to data')
    timestamps.reverse()
    lasttime = parser.parse(timestamps[-1]['created_at'])
    lasttime = lasttime.replace(tzinfo=None)
    payload = {'before_id': timestamps[-1]['id'], 'count': '200'}
  while lasttime > endtime :
    if args.verbose or args.lessverbose :
      print('need to extend back more to cover the duration')
      print(lasttime)
      print('does not cover')
      print(endtime)
    r = requests.get('https://api.app.net/users/' + args.userid + '/posts', params=payload, headers=headers)
    if args.verbose or args.lessverbose :
      print('call for older posts')
    status = r.status_code
    if status != 200 :
      print('API return status not OK, breaking')
      break
    list = r.json()
    data = list['data']
    for x in data :
      timestamps.append(x)
      if args.verbose :
        print('post id ' + x['id'] + ' appended to data')
    tail = data.pop()
    lasttime = parser.parse(tail['created_at'])
    lasttime = lasttime.replace(tzinfo=None)
    endid=tail['id']
    payload = {'before_id': endid, 'count': '200'}

############ spin off writing the cache to a new thread, since it can take a while and nothing relies on it
if args.nocache == False :
  thread1 = writecache(1, "writecache")
  thread1.start()
  threads.append(thread1)

if args.verbose or args.lessverbose :
  print('data length ' + str(len(timestamps)))

############################ parsing
if args.verbose or args.lessverbose :
  print('************************ parsing out timestamps for posts')

####### convert the timestamps to datetime objects for counting
newtimestamps = []
for x in timestamps :
  if args.verbose :
    print(x)
  x = parser.parse(x['created_at'])
  if args.verbose :
    print(x)
  newtimestamps.append(x)


postsbyday = []
currentweek = []
maxposts = 0
minposts = 9999
daytotal = 0
dayiterator = 0
weekiterator = 0

if args.verbose :
  print('topping off current week with 0')

####### fill days that haven't happened yet this week with 0
if len(newtimestamps) != 0 :
  newtimestamps.reverse()
  working=newtimestamps.pop()
  workingday=working.weekday()
  dayiterator = working.date()
  if workingday < 6 :
    currentweek.append(((dayiterator+(6*oneday)).isoformat(), 0))
  if workingday < 5 :
    currentweek.append(((dayiterator+(5*oneday)).isoformat(), 0))
  if workingday < 4 :
    currentweek.append(((dayiterator+(4*oneday)).isoformat(), 0))
  if workingday < 3 :
    currentweek.append(((dayiterator+(3*oneday)).isoformat(), 0))
  if workingday < 2 :
    currentweek.append(((dayiterator+(2*oneday)).isoformat(), 0))
  if workingday < 1 :
    currentweek.append(((dayiterator+oneday).isoformat(), 0))
  daytotal = daytotal + 1

if args.verbose or args.lessverbose :
  print('************************ counting posts per day')

####### run through them counting how many on each day
while len(newtimestamps) > 0 :
  working = newtimestamps.pop()
  if args.verbose: 
    print(len(newtimestamps), working)
  workingday = working.date()
  if workingday == dayiterator :
    daytotal = daytotal + 1
  else :
    currentweek.append((dayiterator.isoformat(), daytotal))
    if maxposts < daytotal :
      maxposts = daytotal
    if daytotal < minposts :
      minposts = daytotal
    if args.verbose :
      print('date' + dayiterator.isoformat() + ' counted ' + str(daytotal) + ' posts. Max now ' + str(maxposts) + ' and Min now ' + str(minposts))
    daytotal = 1
    while dayiterator - oneday > workingday :
      if args.verbose :
        print('skipping a day')
      dayiterator = dayiterator - oneday
      if dayiterator.weekday() == 6 :
        postsbyday.append(currentweek)
        if args.verbose :
          print('new week detected.')
          print(currentweek)
          print('appended to count data')
        currentweek = []
      currentweek.append((dayiterator.isoformat(), 0))
    dayiterator = workingday
    if dayiterator.weekday() == 6 :
      postsbyday.append(currentweek)
      if args.verbose :
        print('new week detected.')
        print(currentweek)
        print('appended to count data')
      currentweek = []

if args.verbose or args.lessverbose :
  print('Max Posts ' + str(maxposts) + '. Min Posts ' + str(minposts) + '. Number of weeks ' + str(len(postsbyday)) + '.')



############################## find stars
stars = []
for x in timestamps :
  if args.verbose :
    print(x)
  stars.append(x['num_stars'])
if len(stars) != 0 :
  maxstars = max(stars)
else :
  maxstars = 0

################################### now build a chart based on what we got
if args.verbose or args.lessverbose :
  print('************************ building chart')

workingweek = 0
workingday = 0
vspace = 0
hspace = 0

###### set up the image canvas
if nolegends == False :
  legendfont = ImageFont.truetype(args.legendfontfile, args.legendtextpoints)
  legendtext = 'Max Posts/Day : ' + str(maxposts) + ' | Min Posts/Day : ' + str(minposts) + ' | Max stars : ' + str(maxstars)
  legendtxtsize = legendfont.getsize(legendtext)
  legendheight = legendtxtsize[1] + 2*args.boundary + args.legendtextfudge
else :
  legendtxtsize = [0,0]
  legendheight = 0

if args.chartwidth < legendtxtsize[0] + 2*args.boundary :
  args.chartwidth = legendtxtsize[0] + 2*args.boundary
else :
  hspace = args.chartwidth - legendtxtsize[0] - 2*args.boundary

if nomonths == False :
  monthfont = ImageFont.truetype(args.monthfontfile, args.monthtextpoints)
  monthname = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
  monthnamesize = monthfont.getsize(monthname)
  monthheight = monthnamesize[1] + 2*args.boundary + args.monthtextfudge
else :
  monthnamesize = [0,0]
  monthheight = 0

if noname == False :
  usernamefont = ImageFont.truetype(args.namefontfile, args.nametextpoints)
  usernametext = '@' + timestamps[-1]['user']['username']
  usernamesize = usernamefont.getsize(usernametext)
  usernameheight = usernamesize[0]+2*args.boundary     # intentionally using the 'wrong' ones, this gets flipped
  usernamewidth = usernamesize[1]+2*args.boundary + args.nametextfudge
else :
  usernameheight = 0
  usernamewidth = 0

if args.halign == 'default' :
  weekwidth = (args.chartwidth-usernamewidth) / args.desiredweeks
elif args.halign == 'center' :
  weekwidth = (args.chartwidth-2*usernamewidth) / args.desiredweeks
if args.weekwidth > weekwidth :
  args.weekwidth = weekwidth

if args.verbose or args.lessverbose :
  print('weekwidth calculated as ' + str(weekwidth) + ' = (' + str(args.chartwidth) + '-' + str(usernamewidth) +') /' + str(args.desiredweeks)  )

if args.verbose :
  print('adjusting heights')

if str(args.chartheight) != 'default' :
  if args.valign == 'center' :
    largetext = max([legendheight,monthheight])
    calculatedheight = (args.daywidth*7)+2*largetext
    if calculatedheight < args.chartheight :
      blocksorigin = [usernamewidth,(largetext + (args.chartheight-calculatedheight)/2)]
    else :
      blocksorigin = [usernamewidth,largetext]
  elif args.valign == 'default' :
    calculatedheight = (args.daywidth*7)+legendheight+monthheight
    blocksorigin = [usernamewidth,monthheight]
  if args.chartheight < calculatedheight :
    if args.valign == 'center' :
      weekheight = args.chartheight - 2*largetext
    elif args.valign == 'default' :
      weekheight = args.chartheight - legendheight - monthheight
    if weekheight/7 <= 1 :
      args.daywidth = 1
    else :
      args.daywidth = int(round(weekheight/7))
  if args.verbose :
    print('daywidth is now ' + str(args.daywidth))
else :
  if args.valign == 'center' :
    largetext = max([legendheight,monthheight])
    args.chartheight = (args.daywidth*7)+2*largetext
    blocksorigin = [usernamewidth,largetext]
  else :
    args.chartheight = (args.daywidth*7)+legendheight+monthheight
    blocksorigin = [usernamewidth,monthheight]

if usernameheight != 0 and args.chartheight < usernameheight :
  args.chartheight = usernameheight
  if args.valign == 'center' :
    blocksorigin = args.chartheight-largetext


chartimage = Image.new("RGB",(args.chartwidth, args.chartheight),args.boundaryshade)

if args.verbose or args.lessverbose :
  print('canvas generated with size ' + str(args.chartwidth) + ' x ' + str(args.chartheight))
  print('blocksorigin = ' + str(blocksorigin))

######  compute the gradient shades


maxshadeR = int(args.maxshade[1:3],16)
maxshadeG = int(args.maxshade[3:5],16)
maxshadeB = int(args.maxshade[5:7],16)
minshadeR = int(args.minshade[1:3],16)
minshadeG = int(args.minshade[3:5],16)
minshadeB = int(args.minshade[5:7],16)
shadedeltaR = int(round((maxshadeR-minshadeR)/args.gradients))
shadedeltaG = int(round((maxshadeG-minshadeG)/args.gradients))
shadedeltaB = int(round((maxshadeB-minshadeB)/args.gradients))

gradientranges = [[0, args.noposts]]
  
if args.gradienttype == 'stdev' :
  if args.verbose :
    print('calculating stdev based gradient')
  counts =[]
  for x in postsbyday :
    for y in x :
      counts.append(y[1])
  mean = numpy.mean(counts)
  stdev = numpy.std(counts)
  grad = []
  if mean - (2*stdev) <= 0 :
    if mean-stdev <= 0 :
      grad.append(mean/3)
      grad.append(mean - (mean/3))
    else :
      grad.append((mean-stdev) / 2)
      grad.append(mean - stdev)
  else :
    grad.append(mean - (2*stdev))
    grad.append(mean - stdev)
  grad.append(mean)
  if mean + (2*stdev) >= maxposts :
    if mean + stdev >= maxposts :
      grad.append(mean + (maxposts-mean)/3)
      grad.append(maxposts -  ((maxposts-mean)/3) )
    else :
      grad.append(mean + stdev)
      grad.append(mean + stdev + (maxposts-(mean+stdev))/2)
  else :
    grad.append(mean + stdev)
    grad.append(mean + (2*stdev))
  if args.verbose :
    print('mean ' + str(mean))
    print('stdev ' + str(stdev))
    print(grad)
  if args.shades == 'default' or len(args.shades) != args.gradients :
    for x in range(args.gradients-1) :
      tmpshadedeltaR = hex(minshadeR+(shadedeltaR*x)).replace('0x','')
      if len(tmpshadedeltaR) == 1 :
        tmpshadedeltaR = '0' + tmpshadedeltaR
      tmpshadedeltaG = hex(minshadeG+(shadedeltaG*x)).replace('0x','')
      if len(tmpshadedeltaG) == 1 :
        tmpshadedeltaG = '0' + tmpshadedeltaG
      tmpshadedeltaB = hex(minshadeB+(shadedeltaB*x)).replace('0x','')
      if len(tmpshadedeltaB) == 1 :
        tmpshadedeltaB = '0' + tmpshadedeltaB
      gradientranges.append([grad[x],'#' + tmpshadedeltaR + tmpshadedeltaG + tmpshadedeltaB ])
    gradientranges.append([grad[args.gradients-1],args.maxshade])
    gradientranges.append([maxposts+1, args.maxshade])
  else :
    for x in range(args.gradients-1) :
      gradientranges.append([grad[x],args.shades[x]])
    gradientranges.append([grad[args.gradients-1],args.shades[-1]])
    gradientranges.append([maxposts+1,args.shades[-1]])
elif args.gradienttype == 'highlights' :
  if args.verbose :
    print('calculating highlights type gradients')
  shadedeltaR = int(round((maxshadeR-minshadeR)/9))
  shadedeltaG = int(round((maxshadeG-minshadeG)/9))
  shadedeltaB = int(round((maxshadeB-minshadeB)/9))
  counts =[]
  grad = []
  for x in postsbyday :
    for y in x :
      counts.append(y[1])
  numberofdays = len(counts)
  numberofmax = counts.count(maxposts)
  numberofmin = counts.count(minposts)   
  mean = numpy.mean(counts[numberofmin+1:numberofdays-numberofmax])
  if args.shades == 'default' or len(args.shades) != args.gradients :
    gradientranges.append([minposts,args.minshade])
    tmpshadeR =  hex(minshadeR+(shadedeltaR*4)).replace('0x','')
    if len(tmpshadeR) == 1 :
      tmpshadeR = '0' + tmpshadeR
    tmpshadeG = hex(minshadeG+(shadedeltaG*4)).replace('0x','')
    if len(tmpshadeG) == 1 :
      tmpshadeG = '0' + tmpshadeG
    tmpshadeB = hex(minshadeB+(shadedeltaB*4)).replace('0x','')
    if len(tmpshadeB) == 1 :
      tmpshadeB = '0' + tmpshadeB
    gradientranges.append([minposts + (mean-minposts)/3,'#' + tmpshadeR + tmpshadeG + tmpshadeB])
    tmpshadeR =  hex(minshadeR+(shadedeltaR*5)).replace('0x','')
    if len(tmpshadeR) == 1 :
      tmpshadeR = '0' + tmpshadeR
    tmpshadeG = hex(minshadeG+(shadedeltaG*5)).replace('0x','')
    if len(tmpshadeG) == 1 :
      tmpshadeG = '0' + tmpshadeG
    tmpshadeB = hex(minshadeB+(shadedeltaB*5)).replace('0x','')
    if len(tmpshadeB) == 1 :
      tmpshadeB = '0' + tmpshadeB
    gradientranges.append([minposts + (mean-minposts)/3,'#' + tmpshadeR + tmpshadeG + tmpshadeB])
    gradientranges.append([maxposts-(maxposts-mean)/3,args.maxshade])
    gradientranges.append([maxposts+1, args.maxshade])
  else :
    gradientranges.append([minposts, args.shades[0]])
    gradientranges.append([minposts + (mean-minposts)/3, args.shades[1]])
    gradientranges.append([mean, args.shades[2]])
    gradientranges.append([maxposts-(maxposts-mean)/3, args.shades[3]])
    gradientranges.append([maxposts+1, args.shades[3]])
else :
  if args.verbose :
    print('calculating linear gradient')
  gradientposts = (maxposts - minposts) / args.gradients
  if args.shades == 'default' or len(args.shades) != args.gradients :
    for x in range(args.gradients -1) :
      tmpshadedeltaR = hex(minshadeR+(shadedeltaR*x)).replace('0x','')
      if len(tmpshadedeltaR) == 1 :
        tmpshadedeltaR = '0' + tmpshadedeltaR
      tmpshadedeltaG = hex(minshadeG+(shadedeltaG*x)).replace('0x','')
      if len(tmpshadedeltaG) == 1 :
        tmpshadedeltaG = '0' + tmpshadedeltaG
      tmpshadedeltaB = hex(minshadeB+(shadedeltaB*x)).replace('0x','')
      if len(tmpshadedeltaB) == 1 :
        tmpshadedeltaB = '0' + tmpshadedeltaB
      gradientranges.append([minposts+(gradientposts*x),'#' +  tmpshadedeltaR + tmpshadedeltaG + tmpshadedeltaB  ])
    gradientranges.append([minposts+(gradientposts*(args.gradients -1)),args.maxshade])
    gradientranges.append([maxposts+1, args.maxshade])
  else :
    for x in range(args.gradients -1) :
      gradientranges.append([minposts+(gradientposts*x),args.shades[x]])
    gradientranges.append([minposts+(gradientposts*(args.gradients-1)),args.shades[-1]])
    gradientranges.append([maxposts+1,args.shades[-1]])

if args.verbose or args.lessverbose :
  print('gradients calculated as :')
  print(gradientranges)

if args.verbose or args.lessverbose :
  print('trimming extra weeks from end')

####### Dump a few extra weeks that may have snuck in earlier
while len(postsbyday) > args.desiredweeks :
  trash = postsbyday.pop()
  if args.verbose :
    print(trash)
    print('dropped')

if args.verbose or args.lessverbose :
  print('assigning colours to days and building chart')

####### run through the days picking color blocks and adding to the chart
while len(postsbyday) > 0 :
  currentweek = postsbyday.pop()
  if args.verbose :
    print('working on week starting ' + str(currentweek[-1][0]))
  while len(currentweek) > 0 :
    currentday = currentweek.pop()
    value = currentday[1]
    if args.verbose :
      print(str(currentday[0]) + ' has count ' + str(value))
    for x in range(args.gradients+1) :
      if gradientranges[x][0] <= value < gradientranges[x+1][0] :
        value = gradientranges[x][1]
        if args.verbose :
          print('value changed to ' + value + ' based on bin ' + str(x))
    tempday = Image.new("RGB",(weekwidth-(2*args.boundary), args.daywidth-(2*args.boundary)),value)
    if args.verbose :
      print('day block made with size ' + str(weekwidth-(2*args.boundary)) + ' x ' + str(args.daywidth-(2*args.boundary)))
    chartimage.paste(tempday,((workingweek*weekwidth)+args.boundary+blocksorigin[0],(workingday*args.daywidth)+args.boundary+blocksorigin[1]))
    if args.verbose :
      print('day block pasted in calendar at position ' + str((workingweek*weekwidth)+blocksorigin[0]) + ' x ' + str((workingday*args.daywidth)+blocksorigin[1]))
    if args.verbose :
      print('testing for end of month')
      print(currentday)
    if parser.parse(currentday[0]).month != (parser.parse(currentday[0])+sevendays).month and workingweek != args.desiredweeks - 1 :
      if args.verbose :
        print('last week of month, adding separator to right')
      if workingday == 0 :
        monthseparatorline = Image.new("RGB",((2*args.boundary), args.daywidth-args.boundary),args.monthseparator)
        chartimage.paste(monthseparatorline,(((workingweek+1)*weekwidth)-args.boundary+blocksorigin[0],(workingday*args.daywidth)+args.boundary+blocksorigin[1]))
      else :
        monthseparatorline = Image.new("RGB",((2*args.boundary), args.daywidth),args.monthseparator)
        chartimage.paste(monthseparatorline,(((workingweek+1)*weekwidth)-args.boundary+blocksorigin[0],(workingday*args.daywidth)-args.boundary+blocksorigin[1]))
    if parser.parse(currentday[0]).month != (parser.parse(currentday[0])+oneday).month and workingday != 6 :
      if args.verbose :
        print('last day of month, adding separator below')
      if workingweek == 0 :
        monthseparatorline = Image.new("RGB",(weekwidth,(2*args.boundary)),args.monthseparator)
        chartimage.paste(monthseparatorline,(((workingweek)*weekwidth)+args.boundary+blocksorigin[0],(((workingday+1)*args.daywidth)-args.boundary+blocksorigin[1])))
      else :
        monthseparatorline = Image.new("RGB",(weekwidth+(2*args.boundary),(2*args.boundary)),args.monthseparator)
        chartimage.paste(monthseparatorline,(((workingweek)*weekwidth)-args.boundary+blocksorigin[0],(((workingday+1)*args.daywidth)-args.boundary+blocksorigin[1])))
    if ( parser.parse(currentday[0]).month != (parser.parse(currentday[0])-oneday).month ) and nomonths == False :
      if args.verbose :
        print('first day of the month, adding month name at top')
      monthname = parser.parse(currentday[0]).strftime('%b')
      monthnamesize = monthfont.getsize(monthname)
      monthnamesize = (monthnamesize[0] + 2*args.boundary, monthnamesize[1] + 2*args.boundary)
      tempmonth = Image.new('RGB', monthnamesize, args.boundaryshade)
      if args.verbose :
        print('month name canvas made with size ' + str(monthnamesize[0]) + ' x ' + str(monthnamesize[1]))
      draw = ImageDraw.Draw(tempmonth)
      draw.text((args.boundary, args.boundary),monthname, font=monthfont, fill=args.monthtextcolour)
      chartimage.paste(tempmonth, ((workingweek*weekwidth)+args.boundary+blocksorigin[0], args.boundary))
      if args.verbose :
        print('month ' + monthname + ' pasted at position ' + str((workingweek*weekwidth)+args.boundary+blocksorigin[0]) + ' x ' + str(args.boundary))
    workingday = workingday + 1
    if workingday == 7 :
      workingday = 0
      workingweek = workingweek + 1
      if args.verbose :
        print('seven days, incremented week')

if args.verbose or args.lessverbose :
  print('adding on legends')
###### add legends
if nolegends :
  if args.verbose or args.lessverbose :
    print('legends off, skipping')
else :
  legendtxtsize = (legendtxtsize[0] + 2*args.boundary, legendtxtsize[1] + 2*args.boundary)
  im = Image.new('RGB', legendtxtsize, args.boundaryshade)
  if args.verbose :
    print('legend image made with size ' + str(legendtxtsize[0]) + ' x ' + str(legendtxtsize[1]))
  draw = ImageDraw.Draw(im)
  draw.text((args.boundary, args.boundary), legendtext, font=legendfont, fill=args.legendtextcolour)
  chartimage.paste(im, (args.boundary+usernamewidth, args.chartheight-legendtxtsize[1]-args.boundary))
  if args.verbose :
    print('legend pasted in at position ' + str(args.boundary+usernamewidth) + ' x ' + str(args.chartheight-legendtxtsize[1]-args.boundary))

if noname == False :
  if args.verbose or args.lessverbose :
    print('adding name')
  usernamesize = (usernamesize[0] + 2*args.boundary, usernamesize[1] + 2*args.boundary)
  usernameim = Image.new('RGB', usernamesize, args.boundaryshade)
  if args.verbose :
    print('username canvase made with size ' + str(usernamesize[0]) + ' x ' + str(usernamesize[1]))
  draw = ImageDraw.Draw(usernameim)
  draw.text((args.boundary,args.boundary), usernametext, font=usernamefont, fill=args.nametextcolour)
  usernameim = usernameim.rotate(90)
  if args.valign == 'default' :
    chartimage.paste(usernameim, (args.boundary,args.chartheight-usernameheight))
  elif args.valign == 'center' :
    chartimage.paste(usernameim, (args.boundary,(args.chartheight-usernameheight)/2))
  if args.verbose :
    print('username pasted in at postition ' + str(args.boundary) + ' x ' + str(args.chartheight-usernameheight))

if args.verbose or args.lessverbose :
  print('************************ saving final image ' + args.filename)
  
chartimage.save(args.filename)

if args.verbose or args.lessverbose :
  print('waiting for threads to finish')
for t in threads :
  t.join()