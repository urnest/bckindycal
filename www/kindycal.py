import sys
import cgi
import urllib
import calendar
import webapp2
import pq
import datetime
import uuid

from google.appengine.ext import ndb

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
            return webapp2.redirect('login.html?from=index.html')
        self.response.write(file('admin.html').read())
        self.response.set_cookie('kc-session',session.sid)
        pass
    pass

class staff(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            print 'not logged in as staff or admin'
            return webapp2.redirect('login.html?from=index.html')
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
        if self.request.get('password','')==getPassword('admin'):
            level='admin'
            pass
        if self.request.get('password','')==getPassword('staff'):
            level='staff'
            pass
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

def today(): return datetime.date.today()

class Terms(ndb.Model):
    numberOfTerms=ndb.IntegerProperty(indexed=False,repeated=False,default=4)
    # json [ {start:(year,month,day),end:(year,month,day)) ]
    terms=ndb.StringProperty(indexed=False,repeated=False)
    def getTerms(self):
        result=[ { 'start': datetime.date(*_['start']),
                   'end': datetime.date(*_['end']) } 
                 for _ in fromJson(self.terms)]
        t=today()
        while len(result)<self.numberOfTerms:
            result.append({'start':t,'end':t})
            pass
        return result
    def setTerms(self,terms):
        self.terms=toJson([ { 'start':(_['start'].year,
                                       _['start'].month,
                                       _['start'].day),
                              'end':  (_['end'].year,
                                       _['end'].month,
                                       _['end'].day) }
                            for _ in terms])
        pass
    def toJson(self):
        return toJson({
            'numberOfTerms':self.numberOfTerms,
            'terms': fromJson(self.terms)
            })

class get_terms(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            return response.write(toJson({'error':'not logged in'}))
        terms=Terms.query(ancestor=root_key).fetch(1)
        if len(terms)==0:
            terms=[Terms(numberOfTerms=4,terms=toJson([]))]
            pass
        return response.write(toJson(terms[0]))
    pass

class edit_terms(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if session.loginLevel!='admin':
            print 'not logged in as admin'
            return webapp2.redirect('login.html?from=index.html')
        terms=Terms.query(ancestor=root_key).fetch(1)
        if len(terms)==0:
            terms=[Terms(numberOfTerms=4,terms=toJson([]))]
            pass
        terms=terms[0]
        page=pq.loadFile('edit_terms.html')
        t_t=page.find(pq.hasClass('term')).remove().first()
        for i,term in enumerate(terms.getTerms()):
            t=t_t.clone()
            t.find(pq.hasClass('term-number')).text(str(i+1))
            t.find(pq.attrEquals('name','start')).attr('value','%s/%s/%s'%(
                        term['start'].day,
                        term['start'].month,
                        term['start'].year))
            t.find(pq.attrEquals('name','end')).attr('value','%s/%s/%s'%(
                        term['end'].day,
                        term['end'].month,
                        term['end'].year))
            t.appendTo(page.find(pq.hasClass('terms')))
            pass
        return self.response.write(unicode(page).encode('utf-8'))
    def post(self):
        #REVISIT
        pass


application = webapp2.WSGIApplication([
        ('/', index),
        ('/index.html', index),
        ('/login.html',login),
        ('/staff.html',staff),
        ('/admin.html',admin),
        ('/edit_terms.html',edit_terms),
], debug=True)
