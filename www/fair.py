import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2
import pq
import json

from pq import hasClass, tagName, attrEquals

def toJson(x):
    return json.dumps(x,sort_keys=True,indent=4,separators=(',',': '))

def fromJson(x):
    return json.loads(x)


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
' class="job"Burners':{
        'name':'BBQ - Cooks',
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
<div align=center>
          <div class="container">
            <h2 class="hd stall_name" style="text-transform:uppercase">Gourmet Stall</h2>
          </div> 


<h2 class="section-head">ROSTER</h2>
<p class="hdsub"><pre class="roster_instructions">Please add your name to the roster. The more the merrier!
The official carnival open times are 10am-2pm, so earlier shifts are for set up and after 2pm time is for pack up.
Please note that email and phone numbers you enter will not appear on this roster, they are sent to the stall convenor and used for private communication only.
</pre></p>
<table class="helper_table">
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

non_empty_cell="""<td align=center class="helpercell" style="height:54px">%(name)s<span class="admin-only">%(contact)s</span></td>"""
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

def cell(names,phones,emails, i):
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
        return non_empty_cell%vars()
    return empty_cell

def makeRow(table_cols,
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
      ''.join([ cell(names,phones,emails, i) \
                    for i in range(0,helpers_required) ])
    result=result+''.join(['<td class="grey-background" style="height:54px">&nbsp;</td>' for _ in range(helpers_required,table_cols-2)])
    result=result+'</tr><tr><td class="dkgrey-background" colspan="%(table_cols)s"></td></tr>\n'%vars()
    return result


stall_page_tail="""\
  </table><br><br>
          <div class="container">
            <p>Made a mistake? Need to change your shift? Please contact the stall convenor or <a href="mailto:info@bardonkindy.com.au" class="gohome">email the office</a>.</p>  			
  			<p><a class="gohome" href="/fair.html">RETURN TO FAIR PAGE</a><br/><br/><br/><br/>
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



def default_helpers_required(hour):
    if hour < 16:
        return 4
    return 0

class StallPage(webapp2.RequestHandler):
    def get(self):
        stall_name = self.request.get(
            'stall_name',
            self.request.cookies.get('stall_name',
                                     DEFAULT_STALL_NAME))
        self.response.set_cookie('stall_name',stall_name)
        content=makeRosterContent(stall_name)
        page=pq.loadFile('fair_index.html')
        main=page.find(tagName('main'))
        section_template=main.find(tagName('section')).find(attrEquals('id','info'))
        roster_section=section_template.clone()
        roster_section.attr('id','roster')
        roster_section.html(content)
        main.html(roster_section)
        #stall page never shows admin stuff
        page.find(hasClass('admin-only')).remove()
        page.find(hasClass('staff-only')).remove()
        self.response.write(unicode(page).encode('utf-8'))

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
    content.find(hasClass('stall_name')).text(stalls[stall_name]['name'])
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

def error(msg):
    'return url of error page with specified message'
    return 'error?'+urllib.urlencode({'msg':msg})

def errorPage(msg):
    result=headerror+\
        ('''ERROR: %s<br/><br/>(Use browser Back button to return to page)</td></tr></div>'''%encodeEntities(msg))+\
        tailerror
    page=pq.parse(result,'errorPage')
    return str(page)
        
class AddName(webapp2.RequestHandler):

    def post(self):
        stall_name = self.request.cookies.get('stall_name')
        hour = int(self.request.get('hour'))
        name = self.request.get('name')
        email = self.request.get('email',None)
        phone = self.request.get('phone',None)
        if name=='':
            self.redirect(error('Please enter your name before pressing Add'))
            return
        if not self.request.get('email') is None and email=='':
            self.redirect(error('Please enter your email before pressing Add'))
            return
        if not self.request.get('phone') is None and phone=='':
            self.redirect(error('Please enter your mobile before pressing Add'))
            return
        try:
            ndb.transaction(lambda: addName(stall_name,hour,name,email or '',phone or ''))
            self.redirect('stall')
        except TooManyNames:
            self.redirect(error('The shift is full. Too many names have been entered already. Please enter your name into another shift start time'))
            return
        except TransactionFailedError:
            self.redirect(error('Please try again; Someone else put their name in at the same time'))

class Error(webapp2.RequestHandler):
    def get(self):
        self.response.write(headerror)
        self.response.write('''ERROR: %s<br/><br/>(Use browser Back button to return to page)</td></tr>'''%encodeEntities(
            self.request.get('msg','')))
     
        self.response.write(tailerror)     


class stalladmin(webapp2.RequestHandler):
    def get(self):
        stall_name = self.request.get(
            'stall_name',
            self.request.cookies.get('stall_name', None))
        if stall_name is None:
            return webapp2.redirect('fair.html')
        self.response.set_cookie('stall_name',stall_name)
        page=pq.loadFile('stall_admin.html')
        page.find(hasClass('stall_name')).text(stalls[stall_name]['name'])
        page.find(hasClass('stall_specific')).addClass('suppress')
        page.find(hasClass('stall_specific')).find(hasClass(stall_name))\
          .removeClass('suppress')
        q=StallPrefs.query(ancestor=stall_key(stall_name))
        prefs=q.fetch(1)
        if len(prefs):
            page.find(hasClass('roster_instructions')).text(
                str(prefs[0].roster_instructions))
            if prefs[0].ask_for_email:
                page.find(pq.attrEquals('name','ask_for_email')).attr('checked','checked')
                pass
            if prefs[0].ask_for_phone:
                page.find(pq.attrEquals('name','ask_for_phone')).attr('checked','checked')
                pass
            helpers_required=fromJson(str(prefs[0].helpers_required))
        else:
            helpers_required={}
            pass
        helpers_by_hour=[(hour,int(helpers_required.get(str(hour),default_helpers_required(hour)))) for hour in range(8,21)]
        for hour,number_required in helpers_by_hour:
            page.find(pq.attrEquals('name','helpers_'+str(hour)))\
                .find(pq.attrEquals('value',str(number_required)))\
                .attr('checked','checked')
            pass
        roster_section=page.find(tagName('section'))\
                           .filter(attrEquals('id','roster'))
        roster_div=pq.parse('<div style="display:inline-block"></div>',
                            'roster_div')
        roster_div.appendTo(roster_section)
        roster_table=makeRosterContent(stall_name).find(
            hasClass('helper_table'))
        trs=roster_table.find(tagName('tr'))
        for i in range(0,len(trs)):
            tds=trs[i:i+1].find(tagName('td'))
            trs[i:i+1].html(tds[0:1])
            tds[2:].appendTo(trs[i:i+1])
            pass
        roster_table.appendTo(roster_div)
        page.find(tagName('section')).filter(attrEquals('id','emails'))\
            .find(tagName('textarea')).text(
                ' '.join([_ for _ in getHelperEmails(stall_name) if _.strip()]))
        page.find(tagName('section')).filter(attrEquals('id','mobiles'))\
            .find(tagName('textarea')).text(
                ' '.join([_ for _ in getHelperMobiles(stall_name) if _.strip()]))
        page.find(hasClass('non-admin-only')).remove()
        page.find(hasClass('stall-specific')).addClass('suppress')
        page.find(hasClass('stall-specific'))\
            .filter(hasClass(stall_name)).removeClass('suppress')
        self.response.write(unicode(page).encode('utf-8'))

class adminsave(webapp2.RequestHandler):
    def post(self):
        stall_name = self.request.get(
            'stall_name',
            self.request.cookies.get('stall_name', None))
        if stall_name is None:
            return webapp2.redirect('fair_index.html')
        roster_instructions=self.request.get('roster_instructions')
        ask_for_email=self.request.get('ask_for_email',False)!=False
        ask_for_phone=self.request.get('ask_for_phone',False)!=False
        print ask_for_email
        print ask_for_phone
        helpers_required={}
        for hour in range(8,21):
            number=self.request.get('helpers_'+str(hour),default_helpers_required(hour))
            helpers_required[str(hour)]=number
        q=StallPrefs.query(ancestor=stall_key(stall_name))
        prefs=q.fetch(1)
        if len(prefs):
            entry=prefs[0]
        else:
            entry = StallPrefs(parent=stall_key(stall_name))
        entry.roster_instructions=str(roster_instructions)
        entry.helpers_required=toJson(helpers_required)
        entry.ask_for_email=ask_for_email
        entry.ask_for_phone=ask_for_phone
        entry.put()            
        self.redirect('stalladmin')

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

