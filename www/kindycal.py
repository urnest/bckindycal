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

class index(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            print 'not logged in'
            return webapp2.redirect('login.html?from=index.html')
        self.response.write(file('index.html').read())
        self.response.set_cookie('kc-session',session.sid)
        pass
    pass

class admin(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if session.loginLevel!='admin':
            print 'not logged in as admin'
            return webapp2.redirect('admin_login.html?from=index.html')
        self.response.write(file('admin.html').read())
        self.response.set_cookie('kc-session',session.sid)
        pass
    pass

class staff(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            print 'not logged in as staff or admin'
            return webapp2.redirect('staff_login.html?from=index.html')
        self.response.write(file('staff.html').read())
        self.response.set_cookie('kc-session',session.sid)
        pass
    pass

class login(webapp2.RequestHandler):
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

class admin_login(webapp2.RequestHandler):
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

class edit_terms(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            print 'not logged in as staff or admin'
            return webapp2.redirect('staff_login.html?from=edit_terms.html')
        return self.response.write(file('edit_terms.html').read())
    pass

groups_schema=[
    {
        'name': StringType, # eg 'Matt Mon-Wed'
        'terms' : [ {
                'daysOfFirstWeek' : [StringType], #eg ['Mon','Tue',"Wed']
                } ]
        }
    ]

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
            if session.loginLevel not in ['admin']:
                result={'need_login':'admin_login.html'}
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

class edit_groups(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin','staff']:
            print 'not logged in as staff'
            return webapp2.redirect('staff_login.html?from=edit_groups.html')
        return self.response.write(file('edit_groups.html').read())
    pass


application = webapp2.WSGIApplication([
        ('/', index),
        ('/admin.html',admin),
        ('/admin_login.html',admin_login),
        ('/edit_terms.html',edit_terms),
        ('/edit_groups.html',edit_groups),
        ('/groups',groups),
        ('/index.html', index),
        ('/login.html',login),
        ('/staff.html',staff),
        ('/staff_login.html',staff),
        ('/terms',terms),
], debug=True)
