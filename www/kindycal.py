import sys
import cgi
import urllib
import calendar
import webapp2
import pq
import datetime
import uuid

from google.appengine.ext import ndb

from xn import Xn,inContext,firstLineOf

from types import IntType,StringType,FloatType,DictType,ListType,TupleType,ObjectType
import jsonschema

import json
def toJson(x):
    return json.dumps(x,sort_keys=True,indent=4,separators=(',',': '))

def fromJson(x):
    return json.loads(x)


root_key=ndb.Key('KC', 'KC')

class Session(ndb.Model):
    sid=ndb.StringProperty(indexed=True)
    touched=ndb.DateTimeProperty(indexed=True,repeated=False,auto_now_add=True)
    # login levels are 'parent','staff','admin', or '' if not logged in
    loginLevel=ndb.StringProperty(indexed=False,repeated=False,default='')
    pass

class Password(ndb.Model):
    loginLevel=ndb.StringProperty(indexed=True,repeated=False)
    password=ndb.StringProperty(indexed=False,repeated=False)
    pass

defaultPasswords={
    'admin':'10greenfrogs',
    'staff':'3blackbats',
    'parent':'88brownbears'
}

def getPassword(level):
    assert level in defaultPasswords.keys(),(level,defaultPasswords.keys())
    p=Password.query(Password.loginLevel==level,ancestor=root_key).fetch(1)
    if len(p):
        return p.password
    return defaultPasswords.get(level)

def expireOldSessions():
    q=Session.query(
        Session.touched < datetime.datetime.now()-datetime.timedelta(days=1),
        ancestor=root_key)
    for x in q.fetch(10000):
        print 'expire session %(x)s'%vars()
        x.key.delete()
    pass

def getSession(id):
    expireOldSessions()
    print 'get session %(id)s'%vars()
    if id=='':
        result=[]
    else:
        print 'query session %(id)s'%vars()
        q=Session.query(Session.sid==str(id),ancestor=root_key)
        result=q.fetch(1)
        pass
    if not len(result):
        result=[Session(parent=root_key,
                        sid=uuid.uuid1().hex,
                        touched=datetime.datetime.now())]
        print 'new session '+result[0].sid
    else:
        print 'existing session '+result[0].sid+ ' level '+result[0].loginLevel
        result[0].touched=datetime.datetime.now()
        pass
    result[0].put()
    return result[0]

class index_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            print 'not logged in'
            return webapp2.redirect('login.html?from=index.html')
        self.response.write(file('index.html').read())
        self.response.set_cookie('kc-session',session.sid)
        pass
    pass

class admin_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if session.loginLevel!='admin':
            print 'not logged in as admin'
            return webapp2.redirect('admin_login.html?from=index.html')
        self.response.write(file('admin.html').read())
        self.response.set_cookie('kc-session',session.sid)
        pass
    pass

class staff_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            print 'not logged in as staff or admin'
            return webapp2.redirect('staff_login.html?from=staff.html')
        self.response.write(file('staff.html').read())
        self.response.set_cookie('kc-session',session.sid)
        pass
    pass

class login_page(webapp2.RequestHandler):
    def get(self):
        page=pq.loadFile('login.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.get('from',''))
        self.response.write(unicode(page).encode('utf-8'))
        pass
    def post(self):
        level=None
        session=getSession(self.request.cookies.get('kc-session',''))
        if self.request.get('password','')==getPassword('parent'):
            level='parent'
            pass
        if level:
            session.loginLevel=level
            print 'session %(id)s now logged in to level %(loginLevel)s'%{
                'id':session.sid,
                'loginLevel':session.loginLevel
                }
            session.put()
            from_=str(self.request.get('from'))
            if from_=='':
                from_=level+'.html'
                pass
            result=webapp2.redirect(from_)
            result.set_cookie('kc-session',session.sid)
            return result
        page=pq.loadFile('login.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.get('from',''))
        page.find(pq.hasClass('login_failed')).text('Incorrect Password')
        self.response.write(unicode(page).encode('utf-8'))
        pass

class admin_login_page(webapp2.RequestHandler):
    def get(self):
        page=pq.loadFile('admin_login.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.get('from',''))
        self.response.write(unicode(page).encode('utf-8'))
        pass
    def post(self):
        level=None
        session=getSession(self.request.cookies.get('kc-session',''))
        if self.request.get('password','')==getPassword('admin'):
            level='admin'
            pass
        if level:
            session.loginLevel=level
            print 'session %(id)s now logged in to level %(loginLevel)s'%{
                'id':session.sid,
                'loginLevel':session.loginLevel
                }
            session.put()
            from_=str(self.request.get('from'))
            if from_=='':
                from_=level+'.html'
                pass
            result=webapp2.redirect(from_)
            result.set_cookie('kc-session',session.sid)
            return result
        page=pq.loadFile('admin_login.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.get('from',''))
        page.find(pq.hasClass('login_failed')).text('Incorrect Password')
        self.response.write(unicode(page).encode('utf-8'))
        pass

class staff_login_page(webapp2.RequestHandler):
    def get(self):
        page=pq.loadFile('staff_login.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.get('from',''))
        self.response.write(unicode(page).encode('utf-8'))
        pass
    def post(self):
        level=None
        session=getSession(self.request.cookies.get('kc-session',''))
        if self.request.get('password','')==getPassword('staff'):
            level='staff'
            pass
        if level:
            session.loginLevel=level
            print 'session %(id)s now logged in to level %(loginLevel)s'%{
                'id':session.sid,
                'loginLevel':session.loginLevel
                }
            session.put()
            from_=str(self.request.get('from'))
            if from_=='':
                from_=level+'.html'
                pass
            result=webapp2.redirect(from_)
            result.set_cookie('kc-session',session.sid)
            return result
        page=pq.loadFile('staff_login.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.get('from',''))
        page.find(pq.hasClass('login_failed')).text('Incorrect Password')
        self.response.write(unicode(page).encode('utf-8'))
        pass

def today(): return datetime.date.today()

terms_schema=jsonschema.Schema({
        'numberOfTerms':IntType,
        'terms':[{
                'start':{'year':IntType,'month':IntType,'day':IntType},
                'end':{'year':IntType,'month':IntType,'day':IntType},
                }]})

class Terms(ndb.Model):
    # data is json encoded terms_schema-conformant
    data=ndb.StringProperty(indexed=False,repeated=False)

class terms(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'You are not logged in.'}
        else:
            terms=Terms.query(ancestor=root_key).fetch(1)
            if len(terms)==0:
                result=None
            else:
                result=fromJson(terms[0].data)
                pass
            pass
        return self.response.write(toJson({'result':result}))
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['admin']:
                result={'error':'You are not logged in.'}
            else:
                data=fromJson(self.request.get('params'))
                assert not data is None
                terms_schema.validate(data)
                for x in Terms.query(ancestor=root_key).fetch(100000): x.key.delete()
                Terms(parent=root_key,
                      data=toJson(data)).put()
                result={}
                pass
            pass
        except:
            result={'error':str(inContext('save terms'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

class edit_terms_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            print 'not logged in as staff or admin'
            return webapp2.redirect('staff_login.html?from=edit_terms.html')
        return self.response.write(file('edit_terms.html').read())
    pass

groups_schema=jsonschema.Schema([
    {
        'name': StringType, # eg 'Matt Mon-Wed'
        'terms' : [ {
                'daysOfFirstWeek' : [StringType], #eg ['Mon','Tue',"Wed']
                } ]
        }
    ])

class Groups(ndb.Model):
    # data is json encoded groups_schema-conformant
    data=ndb.StringProperty(indexed=False,repeated=False)

class groups(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'you are not logged in'}
        else:
            groups=Groups.query(ancestor=root_key).fetch(1)
            if len(groups)==0:
                result=None
            else:
                result=fromJson(groups[0].data)
                pass
            pass
        return self.response.write(toJson({'result':result}))
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['admin','staff']:
                result={'error':'Not authorized'}
            else:
                data=fromJson(self.request.get('params'))
                assert not data is None
                groups_schema.validate(data)
                for x in Groups.query(ancestor=root_key).fetch(100000): x.key.delete()
                Groups(parent=root_key,
                      data=toJson(data)).put()
                result={}
                pass
            pass
        except:
            result={'error':str(inContext('save groups'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

class edit_groups_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin','staff']:
            print 'not logged in as staff'
            return webapp2.redirect('staff_login.html?from=edit_groups.html')
        return self.response.write(file('edit_groups.html').read())
    pass


class events_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin','staff','parent']:
            print 'not logged in'
            return webapp2.redirect('login.html?from=events.html')
        page=pq.loadFile('events.html')
        page.find(pq.hasClass('staff-only')).remove()
        page.find(pq.hasClass('admin-only')).remove()
        self.response.write(unicode(page).encode('utf-8'))
    pass


class edit_events_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin','staff']:
            print 'not logged in'
            return webapp2.redirect('staff.html?from=events.html')
        page=pq.loadFile('events.html')
        if not session.loginLevel in ['admin']:
            page.find(pq.hasClass('admin-only')).remove()
            pass
        self.response.write(unicode(page).encode('utf-8'))
    pass


class groups_to_show(webapp2.RequestHandler):
    def get(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                raise xn.Exception('You are not logged in')
            try:
                result=fromJson(self.request.cookies.get('kc-groups-to-show','[]'))
            except:
                raise inContext('get groups to show from kc-groups-to-show cookie')
            return self.response.write(toJson({'result':result}))
        except:
            self.response.write(toJson({'error':str(inContext('get groups_to_show'))}))
            pass
        pass
    def post(self):
        try:
            groups_to_show=fromJson(self.request.get('params','[]'))
            jsonschema.Schema([IntType]).validate(groups_to_show)
            self.response.set_cookie('kc-groups-to-show',toJson(groups_to_show))
            result={}
        except:
            result={'error':str(inContext('save groups'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

month_calendar_schema=jsonschema.Schema({
        'y':IntType,
        'm':IntType,
        'c':[ [ IntType ] ] # [week][dayOfWeek]=dayOfMonth||0
})

class month_calendar(webapp2.RequestHandler):
    def get(self):
        'get month calendar - see calendar.Calendar.monthdayscalendar'
        try:
            monthToShow=fromJson(self.request.get('params'))
            m=monthToShow['m']
            y=monthToShow['y']
            c=calendar.Calendar(6).monthdayscalendar(y,m)
            result={'y':y,'m':m,'c':c}
            month_calendar_schema.validate(result)
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext('get month calendar'))}))
            pass
        pass

term_weeks_schema=jsonschema.Schema({
    'month': { 'y': IntType, 'm': IntType },
    'weeks' : [ # week number, 0..4 or 0..5 or 0..6
        {
            'termIndex':IntType, # see terms_schema
            'weekNumber':IntType # 1.. (or 0 if not in a term)
        }
    ]
})
class term_weeks(webapp2.RequestHandler):
    def get(self):
        'get term weeks for a month'
        try:
            monthToShow=fromJson(self.request.get('params'))
            m=monthToShow['m']
            y=monthToShow['y']
            result={
                'month': monthToShow,
                'weeks':[
                    #REVISIT
                    { 'termIndex':0, 'weekNumber': 2 },
                    { 'termIndex':0, 'weekNumber': 3 },
                    { 'termIndex':0, 'weekNumber': 4 },
                    { 'termIndex':0, 'weekNumber': 5 },
                    { 'termIndex':0, 'weekNumber': 6 },
                    ]
                }
            term_weeks_schema.validate(result)
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext('get term weeks for a month'))}))
            pass
        pass

class EventIdCounter(ndb.Model):
    """Counter to assign ids to events."""
    nextEventId = ndb.IntegerProperty()

nextEventIdKey=ndb.Key('nextEventId','nextEventId')

def nextEventId():
    q=EventIdCounter.query(ancestor=nextEventIdKey)
    x=q.fetch(1)
    if len(x)==0:
        x=EventIdCounter(parent=nextEventIdKey)
        x.nextEventId=100
    else:
        x=x[0]
    result=x.nextEventId
    x.nextEventId=x.nextEventId+1
    x.put()
    return result


event_schema=jsonschema.Schema({
        'id': IntType, #0 for new event
        'groups': [ IntType ],
        'dates' : [ {year:IntType,month:IntType,Day:IntType} ],
        'name' : {
            'text':StringType,
            'colour':StringType
            },
        'description' : {
            html : StringType
            }
        })

class Event(ndb.Model):
    # data is json encoded event_schema-conformant
    data=ndb.StringProperty(indexed=False,repeated=False)
    # id from data['id']
    id=ndb.IntegerProperty(indexed=True,repeated=False)
    # dates from data['dates']
    dates=ndb.DateProperty(indexed=True,repeated=True)
    pass

class event(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'You are not logged in.'}
        else:
            event=Event.query(Event.id==self.request.get('id'),
                              ancestor=root_key).fetch(1)
            result=fromJson(event[0].data)
            event_schema.validate(result)
            pass
        return self.response.write(toJson({'result':result}))
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['staff','admin']:
                result={'error':'You are not logged in.'}
            else:
                data=fromJson(self.request.get('params'))
                assert not data is None
                event_schema.validate(data)
                if data['id']==0: data['id']=nextEventId()
                event=Event(id=data['id'],
                            dates=[datetime.date(_['y'],_['m'],_['d']) \
                                       for _ in data['dates']],
                            data=data)
                for x in Event.query(Event.id==event.id),ancestor=root_key).fetch(1): x.key.delete()
                event.put()
                result=event.data
                event_schema.validate(result)
                result={'result':result}
                pass
            pass
        except:
            result={'error':str(inContext('save terms'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

application = webapp2.WSGIApplication([
        ('/', index_page),
        ('/admin.html',admin_page),
        ('/admin_login.html',admin_login_page),
        ('/edit_terms.html',edit_terms_page),
        ('/edit_groups.html',edit_groups_page),
        ('/edit_events.html',edit_events_page),
        ('/events.html',events_page),
        ('/index.html', index_page),
        ('/login.html',login_page),
        ('/staff.html',staff_page),
        ('/staff_login.html',staff_login_page),

        # following are not real pages, they are called by javascript files
        # to get and save data
        ('/groups',groups),
        ('/groups_to_show',groups_to_show),
        ('/terms',terms),
        ('/month_calendar',month_calendar),
        ('/term_weeks',term_weeks),
        ('/event',event),
], debug=True)
