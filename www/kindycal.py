import sys
import cgi
import urllib
import calendar
import webapp2
import pq
import datetime
import uuid
import stuff

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
    nextFileId=ndb.IntegerProperty(indexed=False,default=1)
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
        for i in SessionFile.query(
            SessionFile.sid==x.sid,
            ancestor=root_key).fetch(100000):
            i.key.delete()
            pass
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
        self.response.write(file('index.html').read())
        self.response.set_cookie('kc-session',session.sid)
        pass
    pass

class admin_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if session.loginLevel!='admin':
            print 'not logged in as admin'
            return webapp2.redirect('admin_login.html?from=admin.html')
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
        'starts_with':StringType # 'mon-tue' or 'mon-wed'
    }]})

class Terms(ndb.Model):
    # data is json encoded terms_schema-conformant
    data=ndb.StringProperty(indexed=False,repeated=False)

def fetchTerms():
    '''fetch terms from db'''
    terms=Terms.query(ancestor=root_key).fetch(1)
    if len(terms)==0:
        result=None
    else:
        result=fromJson(terms[0].data)
        pass
    return result
    pass

class terms(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'You are not logged in.'}
        else:
            result=fetchTerms()
            pass
        return self.response.write(toJson({'result':result}))
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['admin','staff']:
                result={'error':'You are not logged in.'}
            else:
                data=fromJson(self.request.get('params'))
                assert not data is None
                terms_schema.validate(data)
                print 'save terms: '+toJson(data)
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
        print self.request.headers
        page=pq.loadFile('edit_terms.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('id','referer')).attr('value',self.request.headers['Referer'])
        self.response.write(unicode(page).encode('utf-8'))
    pass

groups_schema=jsonschema.Schema([
    {
        'name': StringType # eg 'Matt Mon-Wed'
    }])

class Groups(ndb.Model):
    # data is json encoded groups_schema-conformant
    data=ndb.StringProperty(indexed=False,repeated=False)
    pass

def fetchGroups():
    groups=Groups.query(ancestor=root_key).fetch(1)
    if len(groups)==0:
        result=None
    else:
        result=fromJson(groups[0].data)
        pass
    return result
    
class groups(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'you are not logged in'}
        else:
            result=fetchGroups()
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
        page=pq.loadFile('edit_groups.html')

        page.find(pq.tagName('input')).filter(pq.attrEquals('id','referer')).attr('value',self.request.headers['Referer'])
        self.response.write(unicode(page).encode('utf-8'))
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
        if fetchTerms() is None:
            print 'terms not defined'
            return webapp2.redirect('edit_terms.html')
        if fetchGroups() is None:
            print 'groups not defined'
            return webapp2.redirect('edit_groups.html')
        page=pq.loadFile('events.html')
        page.find(pq.hasClass('parent-only')).remove()
        if not session.loginLevel in ['admin']:
            page.find(pq.hasClass('admin-only')).remove()
            pass
        self.response.write(unicode(page).encode('utf-8'))
    pass


def formatDate(d):
    return '%(day)s/%(month)s/%(year)s'%d

class event_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin','staff','parent']:
            print 'not logged in'
            return webapp2.redirect('parent.html?from=events.html')
        id=int(self.request.get('id'))
        if session.loginLevel in ['admin','staff']:
            return webapp2.redirect('edit_event.html?id=%(id)s'%vars())
        event=Event.query(Event.id==id,
                          ancestor=root_key).fetch(1)
        event=fromJson(event[0].data)
        event_schema.validate(event)
        page=pq.loadFile('event.html')
        page.find(pq.hasClass('event-name')).text(event['name']['text'])
        groups=fetchGroups()
        print groups
        print event['groups']
        g=' + '.join([groups[_]['name'] for _ in event['groups']])
        page.find(pq.hasClass('groups')).text(g)
        d=', '.join([formatDate(_) for _ in event['dates']])
        page.find(pq.hasClass('dates')).text(d)
        page.find(pq.hasClass('event-description')).html(
            pq.parse(event['description']['html']))
        self.response.write(unicode(page).encode('utf-8'))
    pass



class groups_to_show(webapp2.RequestHandler):
    def get(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                raise xn.Exception('You are not logged in')
            try:
                result=fromJson(self.request.cookies.get('kc-groups-to-show','[0,1,2,3]'))
            except:
                raise inContext('get groups to show from kc-groups-to-show cookie')
            return self.response.write(toJson({'result':result}))
        except:
            self.response.write(toJson({'error':str(inContext('get groups_to_show'))}))
            pass
        pass
    def post(self):
        try:
            groups_to_show=fromJson(self.request.get('params','[0,1,2,3]'))
            jsonschema.Schema([IntType]).validate(groups_to_show)
            self.response.set_cookie('kc-groups-to-show',toJson(groups_to_show))
            result={}
        except:
            result={'error':str(inContext('save groups'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
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
        'dates' : [ {'year':IntType,'month':IntType,'day':IntType} ],
        'name' : {
            'text':StringType,
            'colour':StringType
            },
        'description' : {
            'html' : StringType
            }
        })

class Event(ndb.Model):
    # data is json encoded event_schema-conformant
    data=ndb.StringProperty(indexed=False,repeated=False)
    # id from data['id']
    id=ndb.IntegerProperty(indexed=True,repeated=False)
    # months of data['dates'], as yyyymm
    months=ndb.IntegerProperty(indexed=True,repeated=True)
    pass

class delete_event(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['staff','admin']:
                result={'error':'You are not logged in.'}
            else:
                data=fromJson(self.request.get('params'))
                assert not data is None
                for x in Event.query(Event.id==data['id'],ancestor=root_key).fetch(1): x.key.delete()
                self.response.write(toJson({'result':'OK'}))
                return
        except:
            result={'error':str(inContext('delete event'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

class event(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'You are not logged in.'}
        else:
            event=Event.query(Event.id==int(self.request.get('id')),
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
                event=Event(parent=root_key,
                            id=data['id'],
                            months=[_['year']*100+_['month'] \
                                    for _ in data['dates']],
                            data=toJson(data))
                for x in Event.query(Event.id==event.id,ancestor=root_key).fetch(1): x.key.delete()
                event.put()
                result=fromJson(event.data)
                event_schema.validate(result)
                result={'result':result}
                pass
            pass
        except:
            result={'error':str(inContext('save event'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

class PublicHolidayIdCounter(ndb.Model):
    """Counter to assign ids to PublicHolidays."""
    nextPublicHolidayId = ndb.IntegerProperty()

nextPublicHolidayIdKey=ndb.Key('nextPublicHolidayId','nextPublicHolidayId')

def nextPublicHolidayId():
    q=PublicHolidayIdCounter.query(ancestor=nextPublicHolidayIdKey)
    x=q.fetch(1)
    if len(x)==0:
        x=PublicHolidayIdCounter(parent=nextPublicHolidayIdKey)
        x.nextPublicHolidayId=100
    else:
        x=x[0]
    result=x.nextPublicHolidayId
    x.nextPublicHolidayId=x.nextPublicHolidayId+1
    x.put()
    return result


public_holiday_schema=jsonschema.Schema({
        'id': IntType, #0 for new PublicHoliday
        'dates' : [ {'year':IntType,'month':IntType,'day':IntType} ],
        'name' : {
            'text':StringType
            }
        })

class PublicHoliday(ndb.Model):
    # data is json encoded public_holiday_schema-conformant
    data=ndb.StringProperty(indexed=False,repeated=False)
    # id from data['id']
    id=ndb.IntegerProperty(indexed=True,repeated=False)
    # months of data['dates'], as yyyymm
    months=ndb.IntegerProperty(indexed=True,repeated=True)
    pass

class delete_public_holiday(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['staff','admin']:
                result={'error':'You are not logged in.'}
            else:
                data=fromJson(self.request.get('params'))
                assert not data is None
                for x in PublicHoliday.query(
                    PublicHoliday.id==data['id'],
                    ancestor=root_key).fetch(1): x.key.delete()
                self.response.write(toJson({'result':'OK'}))
                return
        except:
            result={'error':str(inContext('delete public_holiday'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

class public_holiday(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'You are not logged in.'}
        else:
            public_holiday=PublicHoliday.query(
                PublicHoliday.id==int(self.request.get('id')),
                ancestor=root_key).fetch(1)
            result=fromJson(public_holiday[0].data)
            public_holiday_schema.validate(result)
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
                public_holiday_schema.validate(data)
                if data['id']==0: data['id']=nextPublicHolidayId()
                public_holiday=PublicHoliday(parent=root_key,
                            id=data['id'],
                            months=[_['year']*100+_['month'] \
                                    for _ in data['dates']],
                            data=toJson(data))
                for x in PublicHoliday.query(PublicHoliday.id==public_holiday.id,ancestor=root_key).fetch(1): x.key.delete()
                public_holiday.put()
                result=fromJson(public_holiday.data)
                public_holiday_schema.validate(result)
                result={'result':result}
                pass
            pass
        except:
            result={'error':str(inContext('post public_holiday'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass


class MaintenanceDayIdCounter(ndb.Model):
    """Counter to assign ids to MaintenanceDays."""
    nextMaintenanceDayId = ndb.IntegerProperty()

nextMaintenanceDayIdKey=ndb.Key('nextMaintenanceDayId','nextMaintenanceDayId')

def nextMaintenanceDayId():
    q=MaintenanceDayIdCounter.query(ancestor=nextMaintenanceDayIdKey)
    x=q.fetch(1)
    if len(x)==0:
        x=MaintenanceDayIdCounter(parent=nextMaintenanceDayIdKey)
        x.nextMaintenanceDayId=100
    else:
        x=x[0]
    result=x.nextMaintenanceDayId
    x.nextMaintenanceDayId=x.nextMaintenanceDayId+1
    x.put()
    return result


maintenance_day_schema=jsonschema.Schema({
        'id': IntType, #0 for new MaintenanceDay
        'date' : {'year':IntType,'month':IntType,'day':IntType},
        'groups': [ IntType ],
        'description' : {
            'html' : StringType
            },
        'volunteers':[{
                'childs_name':StringType
                }]
        })

class MaintenanceDay(ndb.Model):
    # data is json encoded maintenance_day_schema-conformant
    data=ndb.StringProperty(indexed=False,repeated=False)
    # id from data['id']
    id=ndb.IntegerProperty(indexed=True,repeated=False)
    # month of data['date'], as yyyymm
    months=ndb.IntegerProperty(indexed=True,repeated=True)
    pass

class delete_maintenance_day(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['staff','admin']:
                result={'error':'You are not logged in.'}
            else:
                data=fromJson(self.request.get('params'))
                assert not data is None
                for x in MaintenanceDay.query(
                    MaintenanceDay.id==data['id'],
                    ancestor=root_key).fetch(1): x.key.delete()
                self.response.write(toJson({'result':'OK'}))
                return
        except:
            result={'error':str(inContext('delete maintenance_day'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

class maintenance_day(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'You are not logged in.'}
        else:
            maintenance_day=MaintenanceDay.query(
                MaintenanceDay.id==int(self.request.get('id')),
                ancestor=root_key).fetch(1)
            result=fromJson(maintenance_day[0].data)
            maintenance_day_schema.validate(result)
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
                maintenance_day_schema.validate(data)
                if data['id']==0: data['id']=nextMaintenanceDayId()
                maintenance_day=MaintenanceDay(parent=root_key,
                            id=data['id'],
                            months=[_['year']*100+_['month'] \
                                    for _ in [data['date']]],
                            data=toJson(data))
                for x in MaintenanceDay.query(MaintenanceDay.id==maintenance_day.id,ancestor=root_key).fetch(1): x.key.delete()
                maintenance_day.put()
                result=fromJson(maintenance_day.data)
                maintenance_day_schema.validate(result)
                result={'result':result}
                pass
            pass
        except:
            result={'error':str(inContext('post maintenance_day'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass


month_calendar_schema=jsonschema.Schema({
        'y':IntType,
        'm':IntType,
        'weeks':[
            {
                'term_week':jsonschema.OneOf(
                    {
                        'term':IntType, #>=1
                        'week':IntType #>=1
                    },
                    None),
                'days':[StringType], #egs '', '31'
            }
        ]
})

def dayName(n):
    if n:
        return str(n)
    return ''

class month_calendar(webapp2.RequestHandler):
    def get(self):
        'get month calendar'
        try:
            monthToShow=fromJson(self.request.get('params'))
            m=monthToShow['m']
            y=monthToShow['y']
            c=calendar.Calendar(6).monthdayscalendar(y,m)
            week_names=['' for _ in c]
            for ti,term in enumerate((fetchTerms() or {
                    'numberOfTerms':0,
                    'terms':[]})['terms']):
                week_names=[_[0] or _[1] for _ in
                            zip(week_names,
                                stuff.weekNames(
                                    (y,m),
                                    ti+1,
                                    datetime.date(
                                        term['start']['year'],
                                        term['start']['month'],
                                        term['start']['day']),
                                    datetime.date(
                                        term['end']['year'],
                                        term['end']['month'],
                                        term['end']['day'])))]
                

            result={'y':y,'m':m,
                    'weeks':[
                        {'term_week':_[0],
                         'days':[dayName(d) for d in _[1]]
                        }
                        for _ in zip(week_names,c)]
                    }
            month_calendar_schema.validate(result)
            self.response.write(toJson({'result':result}))
        except:
            self.response.write(toJson({'error':str(inContext('get month calendar'))}))
            pass
        pass
    pass

month_events_schema=jsonschema.Schema([event_schema])

class month_events(webapp2.RequestHandler):
    def get(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                y=int(self.request.get('y'))
                m=int(self.request.get('m'))
                print y*100+m
                events=[fromJson(_.data) for _ in
                        Event.query(Event.months==y*100+m,
                                    ancestor=root_key).fetch(10000)]
                print events
                month_events_schema.validate(events)
                self.response.write(toJson({'result':events}))
        except:
            self.response.write(toJson({'error':str(inContext('get month events'))}))
            pass
        pass
    pass

month_public_holidays_schema=jsonschema.Schema([public_holiday_schema])

class month_public_holidays(webapp2.RequestHandler):
    def get(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                y=int(self.request.get('y'))
                m=int(self.request.get('m'))
                print y*100+m
                public_holidays=[fromJson(_.data) for _ in
                        PublicHoliday.query(
                        PublicHoliday.months==y*100+m,
                        ancestor=root_key).fetch(10000)]
                print public_holidays
                month_public_holidays_schema.validate(public_holidays)
                self.response.write(toJson({'result':public_holidays}))
        except:
            self.response.write(toJson({'error':str(inContext('get month public_holidays'))}))
            pass
        pass
    pass

month_maintenance_days_schema=jsonschema.Schema([maintenance_day_schema])

class month_maintenance_days(webapp2.RequestHandler):
    def get(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                y=int(self.request.get('y'))
                m=int(self.request.get('m'))
                print y*100+m
                maintenance_days=[fromJson(_.data) for _ in
                        MaintenanceDay.query(
                        MaintenanceDay.months==y*100+m,
                        ancestor=root_key).fetch(10000)]
                print maintenance_days
                month_maintenance_days_schema.validate(maintenance_days)
                self.response.write(toJson({'result':maintenance_days}))
        except:
            self.response.write(toJson({'error':str(inContext('get month maintenance_days'))}))
            pass
        pass
    pass

class edit_event_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            print 'not logged in as staff or admin'
            return webapp2.redirect('staff_login.html')
        page=pq.loadFile('edit_event.html')
        page.find(pq.attrEquals('id','id')).attr('value',self.request.get('id','0'))
        self.response.write(unicode(page).encode('utf-8'))
    pass

class edit_public_holiday_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            print 'not logged in as staff or admin'
            return webapp2.redirect('staff_login.html')
        page=pq.loadFile('edit_public_holiday.html')
        page.find(pq.attrEquals('id','id')).attr('value',self.request.get('id','0'))
        self.response.write(unicode(page).encode('utf-8'))
    pass

class maintenance_day_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin','staff','parent']:
            print 'not logged in'
            return webapp2.redirect('parent.html')
        id=int(self.request.get('id'))
        if session.loginLevel in ['admin','staff']:
            return webapp2.redirect('edit_maintenance_day.html?id=%(id)s'%vars())
        maintenance_day=MaintenanceDay.query(MaintenanceDay.id==id,
                          ancestor=root_key).fetch(1)
        maintenance_day=fromJson(maintenance_day[0].data)
        maintenance_day_schema.validate(maintenance_day)
        page=pq.loadFile('maintenance_day.html')
        d=formatDate(maintenance_day['date'])
        page.find(pq.attrEquals('id','id')).attr('value',str(id))
        page.find(pq.hasClass('date')).text(d)
        page.find(pq.hasClass('maintenance-day-description')).html(
            pq.parse(maintenance_day['description']['html']))
        vrt=page.find(pq.hasClass('volunteer-row')).remove().first()
        for v in maintenance_day['volunteers']:
            vr=vrt.clone()
            vr.find(pq.hasClass('volunteer-child-name')).text(
                v['childs_name'])
            vr.appendTo(page.find(pq.hasClass('volunteers-table')))
            pass
        self.response.write(unicode(page).encode('utf-8'))
    pass


class edit_maintenance_day_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            print 'not logged in as staff or admin'
            return webapp2.redirect('staff_login.html')
        page=pq.loadFile('edit_maintenance_day.html')
        page.find(pq.attrEquals('id','id')).attr('value',self.request.get('id','0'))
        self.response.write(unicode(page).encode('utf-8'))
    pass

class add_maintenance_day_volunteer(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                assert self.request.get('id','')
                assert self.request.get('childs_name','')
                id=int(self.request.get('id'))
                childs_name=self.request.get('childs_name')
                maintenance_day=MaintenanceDay.query(
                    MaintenanceDay.id==id,
                    ancestor=root_key).fetch(1)[0]
                data=fromJson(maintenance_day.data)
                data['volunteers'].append({
                    'childs_name':childs_name
                    })
                maintenance_day_schema.validate(data)
                maintenance_day.data=toJson(data)
                maintenance_day.put()
                self.response.write(toJson({'result':toJson(data)}))
        except:
            self.response.write(toJson({'error':str(inContext('add maintenance day volunteer'))}))
            pass
        pass
    pass

class remember_month(webapp2.RequestHandler):
    def post(self):
        try:
            y=int(self.request.get('y'))
            m=int(self.request.get('m'))
            self.response.set_cookie('month-to-show',toJson({'y':y,'m':m}))
            self.response.write(toJson({'result':'OK'}))
        except:
            self.response.write(toJson({'error':str(inContext('remember month'))}))
            pass
        pass
    pass

class get_month_to_show(webapp2.RequestHandler):
    def get(self):
        t=today()
        result={'y':t.year,'m':t.month}
        if self.request.cookies.get('month-to-show',None):
            result=fromJson(self.request.cookies.get('month-to-show'))
            pass
        self.response.write(toJson({'result':result}))
        pass
    pass

class SessionFile(ndb.Model):
    sid=ndb.StringProperty(indexed=True)
    id=ndb.IntegerProperty(indexed=True)
    mime_type=ndb.StringProperty(indexed=False,repeated=False,default='') #eg image/jpeg
    data=ndb.BlobProperty(indexed=False,repeated=False)#file data
    pass

class session_file(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'You are not logged in.'}
            self.response.write(toJson(result))
        else:
            assert self.request.get('id')
            id=int(self.request.get('id'))
            f=SessionFile.query(
                SessionFile.sid==session.sid and SessionFile.id==id,
                ancestor=root_key).fetch(1)[0]
            self.response.headers['Content-Type'] = \
                f.mime_type.encode('ascii','ignore')
            self.response.write(f.data)
            pass
        pass
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['staff','admin']:
                result={'error':'You are not logged in.'}
            else:
                print self.request.POST.keys()
                data=self.request.get('filename')
                mime_type=self.request.POST['filename'].type
                id=session.nextFileId
                session.nextFileId=session.nextFileId+1
                session.put()
                f=SessionFile(parent=root_key,
                              sid=session.sid,
                              id=id,
                              mime_type=mime_type,
                              data=data)
                f.put()
                result={'result':{'id':id}}
                pass
            pass
        except:
            result={'error':str(inContext('post maintenance_day'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass



application = webapp2.WSGIApplication([
    ('/', index_page),
    ('/admin.html',admin_page),
    ('/admin_login.html',admin_login_page),
    ('/edit_terms.html',edit_terms_page),
    ('/edit_groups.html',edit_groups_page),
    ('/edit_event.html',edit_event_page),
    ('/edit_events.html',edit_events_page),
    ('/edit_maintenance_day.html',edit_maintenance_day_page),
    ('/edit_public_holiday.html',edit_public_holiday_page),
    ('/event.html',event_page),
    ('/events.html',events_page),
    ('/index.html', index_page),
    ('/login.html',login_page),
    ('/maintenance_day.html',maintenance_day_page),
    ('/staff.html',staff_page),
    ('/staff_login.html',staff_login_page),
    
    # following are not real pages, they are called by javascript files
    # to get and save data
    ('/add_maintenance_day_volunteer',add_maintenance_day_volunteer),
    ('/get_month_to_show',get_month_to_show),
    ('/groups',groups),
    ('/groups_to_show',groups_to_show),
    ('/terms',terms),
    ('/month_calendar',month_calendar),
    ('/month_events',month_events),
    ('/month_maintenance_days',month_maintenance_days),
    ('/month_public_holidays',month_public_holidays),
    ('/event',event),
    ('/maintenance_day',maintenance_day),
    ('/public_holiday',public_holiday),
    ('/delete_event',delete_event),
    ('/delete_maintenance_day',delete_maintenance_day),
    ('/delete_public_holiday',delete_public_holiday),
    ('/remember_month',remember_month),
    ('/session_file',session_file)
], debug=True)
