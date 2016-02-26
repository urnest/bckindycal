import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import pq
import json

from pq import hasClass, tagName, attrEquals

from xn import Xn,inContext,firstLineOf
l1=firstLineOf

def toJson(x):
    return json.dumps(x,sort_keys=True,indent=4,separators=(',',': '))

def fromJson(x):
    return json.loads(x)

import logging

def log(s):
    return logging.info(s)

class Scope:
    def __init__(self,description):
        self.description=description
        self.result_=None
        log('+ '+self.description)
        pass
    def __del__(self):
        log('- '+self.description+' = '+repr(self.result_))
        pass
    def result(self,result):
        self.result_=result
        return result
    pass



stalls={
#Art corresponds to a href="stall?stall_name=Art" in fair_index.html
'Art':{
        #name is the name for display
        'name':"Children's Art",
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Auction':{
        'name':'Auction',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Bar':{
        'name':'Drinks (Bar)',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Books':{
        'name':'Books',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'BBQ':{
        'name':'BBQ',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Cakes':{
        'name':'Cakes',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Coffee':{
        'name':'Coffee Shop',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Drinks':{
        'name':'Drinks (Soft)',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'FacePainting':{
        'name':'Face Painting',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Garden':{
        'name':'Plants and Herbs',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Gourmet':{
        'name':'Gourmet',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'LobaChoc':{
        'name':'Lob-a-Choc',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Rides':{
        'name':'Rides',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Lucky':{
        'name':'Lucky Bags',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'PreLoved':{
        'name':'Pre-loved Toys and Clothes',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Floss':{
        'name':'Fairy Floss',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Games':{
        'name':'Games',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'SweetTreats':{
        'name':'Sweets and Preserves',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'Raffle':{
        'name':'Wheelbarrow Raffle',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'SetupFri':{
        'name':'Setup Crew - Friday',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },
'SetupSat':{
        'name':'Setup Crew - Saturday',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },			
'SetupSun':{
        'name':'Pulldown Crew - Sunday',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },			
'SetupMon':{
        'name':'Pulldown Crew - Monday',
        'email':{
            'name':'',
            'address':'info@bardonkindy.com.au'
            }
        },								
}
stall_page_head="""
<div align="center">
          <div class="container">
            <h2 class="hd stall_name" style="text-transform:uppercase">Gourmet Stall</h2>
          </div> 
<div align="center" class="kindycal-py-stall">
<p><img class="stall_image" src="fair_images/stall-BBQ.jpg"></p>
<p style="text-align:center" class="stallconv">CONVENOR: <a class="stallconvac" href="/convenor_signup">VACANT</a></p>
</div>

<p class="hdsub"><pre width="90%" style="max-width:600px"class="roster_instructions">Please add your name to the roster. The more the merrier!
The official carnival open times are 10am-2pm, so earlier shifts are for set up and after 2pm time is for pack up.
Please note that email and phone numbers you enter will not appear on this roster, they are sent to the stall convenor and used for private communication only.
</pre></p>
<hr class="stallhd">
<h3 class="section-head">PRE-FAIR HELP</h3>
<p class="blue" width="90%" style="max-width:600px">Can you help with organising and preparing goods for the stall? &nbsp; <a class="add-prefair-helper helpros" href="add_prefair_helper"> ADD ME</a></p>
<p class="pre-fair-helper-names parent-only" width="90%" style="max-width:600px">Alan, John</p>
<p class="staff-only" width="90%" style="max-width:600px">
  <table align="center" class="non-admin pre-fair-helper-details pre-fair-helpers">
    <tr class="pre-fair-helper-detail">
      <td><a href="delete-pre-fair-helper"><i class="fa fa-trash-o"></i>&nbsp;</td>
      <td class="pre-fair-helper-name">Fred Glob</td>
      <td class="helper-top"><a href="mailto:fred@glob.com" class="pre-fair-helper-mailto-link">fred@glob.com</a></td>
      <td class="pre-fair-helper-note">I have a table you can borrow.</td>
    </tr>
  </table>
</p>
<br><br>
<hr class="stallhd">
<h3 class="section-head">ROSTER</h3>
<p class="kindycal-py-roster-el">NOTE: Your email address is only seen by stall convenors and not published on the roster.</p>
<p class="kindycal-py-noroster-el">No roster required.</p><br>
<table class="helper_table kindycal-py-roster-el">
 <tr class="table_headings">
	<td width=60 align=center class=hdoff>START</td>
	<td width=200 align=left class=hdred>&nbsp;</td>
	<td width=100 align=center class="hd helper-th">HELPER 1</td>
	<td width=100 align=center class="hd helper-th">HELPER 2</td>
	<td width=100 align=center class="hd helper-th">HELPER 3</td>
	<td width=100 align=center class="hd helper-th">HELPER 4</td>
	<td width=100 align=center class="hd helper-th">HELPER 5</td>
	<td width=100 align=center class="hd helper-th">HELPER 6</td>
	<td width=100 align=center class="hd helper-th">HELPER 7</td>
	<td width=100 align=center class="hd helper-th">HELPER 8</td>
	<td width=100 align=center class="hd helper-th">HELPER 9</td>
	<td width=100 align=center class="hd helper-th">HELPER 10</td></tr>
	<tr><td class="dkgry-background top-spacer" colspan="12"></td>
"""


headerror = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head>
<link href="fair_css/rssrc1.css" rel="stylesheet" type="text/css" media="all" />
</head>
<div align=center>
<h2 class="hd stall_name" style="text-transform:uppercase">Bardon Kindy Fair</h2>
<h4>ERROR</h4>
<div class="aq-box"><br/><br/>
<table class="helper_table">
<tr class="table_headings"><td class=recerr width=400 height=200 align=center><strong>
"""
tailerror = """\
"""

non_empty_cell="""<td align=center class="helpercell" style="height:54px">
<input type="hidden" class="helper-number">
<input type="hidden" class="hour">
<input type="hidden" class="stall-name">
<span class="admin-only"><a class="delete-fair-helper" href="delete_stall_helper"><i class="fa fa-trash-o"></i></a>
</span>%(name)s<span class="admin-only">%(contact)s</span></td>"""

empty_cell="""<td align="center" class="helpercell" style="height:54px">&nbsp;</td>"""

def getHr(hour):
    'turn hour, 0..23, into 12am..11pm'
    if hour == 0:
        return '12am'
    elif hour < 12:
        return '%sam'%hour
    elif hour == 12:
        return '12noon'
    else:
        return '%spm'%(hour-12)

def cell(names,phones,emails,i,hour,stall_name):
    'get name phone and email of ith person in list of names'
    '- return '' if there are less than i names in list'
    if i < len(names):
        name=str(names[i])
        contact=[]
        if i < len(phones) and len(phones[i]): contact.append(str(phones[i]))
        if i < len(emails) and len(emails[i]): contact.append(str(emails[i]))
        if len(contact):
            contact=' ('+', '.join(contact)+')'
        else:
            contact=''
            pass
        
        result=pq.parse(non_empty_cell%vars())
        inputs=result.find(pq.tagName('input'))
        inputs.filter(pq.hasClass('helper-number')).attr('value',str(i))
        inputs.filter(pq.hasClass('hour')).attr('value',str(hour))
        inputs.filter(pq.hasClass('stall-name')).attr('value',stall_name)
        return unicode(result).encode('utf-8')
    return empty_cell

def makeRow(table_cols,
            stall_name,
            hour,
            names,
            phones,
            emails,
            helpers_required,
            ask_for_email,
            ask_for_phone):
    assert helpers_required<=table_cols-2, (helpers_required,table_cols)
    result='<tr><td align=center class=bw><strong>%s</td>'%getHr(hour)
    if len(names)<helpers_required:
        email=''
        phone=''
        if ask_for_email:
            email='''
<input type="text" placeholder="Email" class="roster-email" name="email">'''
        if ask_for_phone:
            phone='''
<input type="text" placeholder="Mobile" class="roster-phone" name="phone">'''
        result=result+\
            '''<td class="sm roster-add"><form method="POST" action="add?hour=%(hour)s">
<input type="text" placeholder="Full Name" class="roster-name" name="name">%(email)s%(phone)s<input type="submit" value="ADD" class="add-me subscribe"></form></td>'''%vars()
    else:
        result=result+'''<td class="sm" align="left">&nbsp;&nbsp;SHIFT FULL</td>'''
    result=result+ \
      ''.join([ cell(names,phones,emails, i,hour,stall_name) \
                    for i in range(0,helpers_required) ])
    result=result+''.join(['<td class="grey-background" style="height:54px">&nbsp;</td>' for _ in range(helpers_required,table_cols-2)])
    result=result+'</tr><tr><td class="dkgrey-background" colspan="%(table_cols)s"></td></tr>\n'%vars()
    return result


stall_page_tail="""\
  </table><br><br>
          <div class="container">
            <p>Made a mistake? <span class="kindycal-py-roster-el">Need to change your shift? </span>Please contact the stall convenor or <a href="mailto:info@bardonkindy.com.au" class="gohome">email the office</a>.</p>  			
  			<p><a class="gohome" href="/fair.html">RETURN TO FAIR PAGE</a><br/><br/>
		  </div> 
        <div class="fair-only container" align=center>
          <br><br>
            <p><a href="stalladmin.html?stall_name=None"  class="jobros edit-stall-link">STALL ADMIN</a></p><br><br><br/><br/>
          </div>
  
  <p class=ft><strong><br><br><br/><br/>
"""

tailpledge="""\
  </table>
  </div><br/><br/>
  </p>&nbsp;</p></div>
"""

tailpledgedetails=tailpledge
tailcontainers=tailpledge

taillabel="""\
"""

def encodeEntities(s):
    return cgi.escape(s).encode('ascii', 'xmlcharrefreplace') 

DEFAULT_STALL_NAME = 'Art'


# We set a parent key on the 'OneHourOfHelp' object to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def stall_key(stall_name):
    """Constructs a Datastore key for a Stall entity with stall_name."""
    return ndb.Key('Stall', stall_name)

nextCodeKey=ndb.Key('nextCode','nextCode')

class OneHourOfHelp(ndb.Model):
    """Models an individual Stall 1 hour of help."""
    hour = ndb.IntegerProperty()
    names = ndb.StringProperty(indexed=False, repeated=True)
    emails = ndb.StringProperty(indexed=False, repeated=True)
    phones = ndb.StringProperty(indexed=False, repeated=True)

class StallPrefs(ndb.Model):
    '''Stall preferences'''
    roster_instructions=ndb.StringProperty(indexed=False,repeated=False)
    ask_for_email=ndb.BooleanProperty(indexed=False,repeated=False)
    ask_for_phone=ndb.BooleanProperty(indexed=False,repeated=False)
    #json { <hour> : <number-required> } #default number is 6
    helpers_required=ndb.StringProperty(indexed=False,repeated=False)
	
class StallConvenor(ndb.Model):
    '''Stall convenor'''
    name=ndb.StringProperty(indexed=False,repeated=False)
    email=ndb.StringProperty(indexed=False,repeated=False)
    phone=ndb.StringProperty(indexed=False,repeated=False)		

class StallPreFairHelper(ndb.Model):
    '''Stall convenor'''
    name=ndb.StringProperty(indexed=False,repeated=False)
    email=ndb.StringProperty(indexed=False,repeated=False)
    note=ndb.StringProperty(indexed=False,repeated=False)		

def default_helpers_required(hour):
    if hour < 9:
        return 0
    if hour < 15:
        return 4	
    return 0

Listofproducts= ["Biscotti","Butters / Curds","Chutney / Relish","Curry Paste","Dips","Drinks","Dry Items",
                 "Jam - Sweet","Jam - Savoury","Jelly",
                 "Kits","Marmalade","Preserved Goods",
                 "Sauce - Sweet","Sauce - Savoury","Other"]

def getHelperEmails(stall_name):
    entry_query = OneHourOfHelp.query(ancestor=stall_key(stall_name))
    entries = entry_query.fetch(10000)
    emails=[]
    for e in entries:
        emails.extend(e.emails)
        pass
    return set(emails)

def getHelperMobiles(stall_name):
    entry_query = OneHourOfHelp.query(ancestor=stall_key(stall_name))
    entries = entry_query.fetch(10000)
    mobiles=[]
    for e in entries:
        mobiles.extend(e.phones)
        pass
    return set(mobiles)

def getPrefs(stall_name):
    q=StallPrefs.query(ancestor=stall_key(stall_name))
    prefs=q.fetch(1)
    print 'prefs: %(prefs)r' %vars()
    if len(prefs):
        prefs=prefs[0]
        print 'prefs2: %(prefs)r' %vars()
    else:
        prefs = StallPrefs(parent=stall_key(stall_name))
        prefs.roster_instructions=''
        prefs.ask_for_email=False
        prefs.ask_for_phone=False
        prefs.helpers_required=toJson({})
        pass
    print 'prefs: %(prefs)r' %vars()
    return prefs

def getStallConvenor(stall_name):
    q=StallConvenor.query(ancestor=stall_key(stall_name))
    convs=q.fetch(1)
    print 'convs: %(convs)r' %vars()
    if len(convs):
        convs=convs[0]
        print 'convs2: %(convs)r' %vars()
    else:
        convs = StallConvenor(parent=stall_key(stall_name))
        convs.name=''
        convs.email=''
        convs.phone=''
        pass
    print 'convs: %(convs)r' %vars()
    return convs
	
def getStallPreFairHelpers(stall_name):
    q=StallPreFairHelper.query(ancestor=stall_key(stall_name))
    helpers=q.fetch(1000)
    result=[{ 'name':_.name,'email':_.email,'note':_.note} for _ in helpers]
    result.sort(lambda a,b: cmp(a['name'],b['name']))
    return result
	
def makeRosterContent(stall_name):
    print 'prefs'
    prefs=getPrefs(stall_name)
    helpers_required=fromJson(prefs.helpers_required)
    result=stall_page_head
    helpers_by_hour=[(hour,int(helpers_required.get(str(hour),default_helpers_required(hour)))) for hour in range(8,21)]
    table_cols=2+max([_[1] for _ in helpers_by_hour])
    while len(helpers_by_hour) and helpers_by_hour[-1][1]==0:
        helpers_by_hour=helpers_by_hour[0:-1]
        pass
    for hour, max_helpers in helpers_by_hour:
        # get OneHourOfHelp object for specified hour from datastore
        entry_query = OneHourOfHelp.query(OneHourOfHelp.hour == hour, ancestor=stall_key(stall_name))
        entries = entry_query.fetch(1)
        names=[]
        phones=[]
        emails=[]
        if len(entries):
            names=entries[0].names
            phones=entries[0].phones
            emails=entries[0].emails
            pass
        if max_helpers>0:
            result=result+makeRow(table_cols,
                                  stall_name,
                                  hour, 
                                  names,
                                  phones,
                                  emails,
                                  max_helpers,
                                  prefs.ask_for_email,
                                  prefs.ask_for_phone)
            pass
        pass
    result=result+stall_page_tail    
    content=pq.parse(result,'StallPage')
    #lop off empty table columns
    helper_table=content.find(hasClass('helper_table'))
    helper_table.find(hasClass("top-spacer"))\
                .attr('colspan',str(table_cols))
    ths=helper_table.find(hasClass('helper-th'))
    ths[table_cols-2:].remove()
    #suppress roster table and heading etc if there are no rows
    if len(helpers_by_hour)==0:
        content.find(hasClass('kindycal-py-roster-el')).remove()
    else:
        content.find(hasClass('kindycal-py-noroster-el')).addClass('kc-display-none')
        pass
    content.find(hasClass('stall_name')).text(stalls[stall_name]['name'])
    content.find(hasClass('stall_image')).attr('src','fair_images/roster-%(stall_name)s.jpg'%vars())
    content.find(hasClass('stall-convenor-name')).text(
        stalls[stall_name]['email']['name'])
    content.find(hasClass('roster_instructions')).text(
        prefs.roster_instructions)
    return content

class TooManyNames:
    pass

def addName(stall_name, hour, name, email, phone):
        entry_query = OneHourOfHelp.query(OneHourOfHelp.hour == hour, ancestor=stall_key(stall_name))
        entries = entry_query.fetch(1)
        if len(entries):
            entry=entries[0]
        else:
            entry = OneHourOfHelp(parent=stall_key(stall_name))
            entry.hour=hour
        prefs=getPrefs(stall_name)
        helpers_required=fromJson(prefs.helpers_required)
        helpers_this_hour=helpers_required.get(str(hour),default_helpers_required(hour))
        if len(entry.names)>=helpers_this_hour:
            raise TooManyNames()
        entry.names.append(name)
        entry.emails.append(email)
        entry.phones.append(phone)
        entry.put()

def deleteHelper(stall_name,hour,helper_number):
    'delete helper with index %(helper_number)s from hour %(hour)s from stall %(stall_name)s'
    scope=Scope(l1(deleteHelper.__doc__)%vars())
    try:
        entry_query = OneHourOfHelp.query(OneHourOfHelp.hour == hour, ancestor=stall_key(stall_name))
        entries = entry_query.fetch(1)
        if len(entries)==0:
            return scope.result('no such hour of help')
        entry=entries[0]
        del entry.names[helper_number]
        del entry.emails[helper_number]
        del entry.phones[helper_number]
        entry.put()
        return scope.result('entry now %(entry)s'%vars())
    except:
        raise inContext(scope.description)
    pass

def error(msg):
    'return url of error page with specified message'
    return 'error?'+urllib.urlencode({'msg':msg})

def errorPage(msg):
    result=headerror+\
        ('''ERROR: %s<br/><br/>(Use browser Back button to return to page)</td></tr></div>'''%encodeEntities(msg))+\
        tailerror
    page=pq.parse(result,'errorPage')
    return str(page)
        
class Error(webapp2.RequestHandler):
    def get(self):
        self.response.write(headerror)
        self.response.write('''ERROR: %s<br/><br/>(Use browser Back button to return to page)</td></tr>'''%encodeEntities(
            self.request.get('msg','')))
     
        self.response.write(tailerror)     

class ArtRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Art')
    pass

class AuctionRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Auction')
    pass

class BarRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Bar')
    pass

class BooksRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Books')
    pass

class BurgerServersRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=BBQ')
    pass

class BurgerBurnersRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=BBQCooks')
    pass

class CakesRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Cakes')
    pass

class CoffeeRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Coffee')
    pass

class DrinksRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Drinks')
    pass

class FacePaintingRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=FacePainting')
    pass

class GardenRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Garden')
    pass

class GamesRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Games')
    pass

class LobaChocRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=LobaChoc')
    pass

class RidesRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Rides')
    pass

class LuckyRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Lucky')
    pass

class PreLovedRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=PreLoved')
    pass

class FlossRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Floss')
    pass

class SweetTreatsRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=SweetTreats')
    pass

class RaffleRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=Raffle')
    pass

class SetupSatRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=SetupSat')
    pass

class SetupSunRedirect(webapp2.RequestHandler):
    def get(self):
        return self.redirect('stall?stall_name=SetupSun')
    pass

