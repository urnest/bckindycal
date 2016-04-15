import sys
import cgi
import urllib
import calendar
import webapp2
import pq
import datetime
import uuid
import stuff
import logging
import zlib

from pq import hasClass, tagName, attrEquals

from google.appengine.ext import ndb

from xn import Xn,inContext,firstLineOf

l1=firstLineOf

from types import IntType,StringType,FloatType,DictType,ListType,TupleType,ObjectType,BooleanType
import jsonschema

import json
def toJson(x):
    return json.dumps(x,sort_keys=True,indent=4,separators=(',',': '))

def fromJson(x):
    return json.loads(x)

#./fair.py
import fair

def addScriptToPageHead(script,page):
    pq.parse('<script type="text/javascript" src="%(script)s"></script>'%vars()).appendTo(page.find(pq.tagName('head')))
    pass
def makePageBodyInvisible(page):
    page.find(pq.tagName('body')).addClass('kc-invisible')
    pass

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


root_key=ndb.Key('KC', 'KC')

class Session(ndb.Model):
    sid=ndb.StringProperty(indexed=True)
    touched=ndb.DateTimeProperty(indexed=True,repeated=False,auto_now_add=True)
    # login levels are 'parent','staff','admin', or '' if not logged in
    loginLevel=ndb.StringProperty(indexed=False,repeated=False,default='')
    sessionFiles=ndb.IntegerProperty(indexed=False,repeated=True)
    pass

class Password(ndb.Model):
    loginLevel=ndb.StringProperty(indexed=True,repeated=False)
    password=ndb.StringProperty(indexed=False,repeated=False)
    pass

defaultPasswords={
    'admin':'10greenfrogs',#guru
    'staff':'password',
    'parent':'password',
    'fair':'fairyfloss',
}
loginLevelName={
    'admin':'GURU',
    'staff':'STAFF',
    'parent':'PARENT',
    'fair':'FAIR'
}

def getPassword(level):
    assert level in defaultPasswords.keys(),(level,defaultPasswords.keys())
    p=Password.query(Password.loginLevel==level,ancestor=root_key).fetch(1)
    if len(p):
        return p[0].password
    return defaultPasswords.get(level)

@ndb.transactional
def setPassword(level,new_password):
    'set %(level)s password to %(new_password)s'
    try:
        assert level in defaultPasswords.keys(),(level,defaultPasswords.keys())
        p=Password.query(Password.loginLevel==level,ancestor=root_key).fetch(1)
        if len(p)==0:
            p=[Password(parent=root_key,loginLevel=level,password='')]
            pass
        p[0].password=new_password
        p[0].put()
        log(l1(setPassword.__doc__)%vars())
    except:
        raise inContext(l1(setPassword.__doc__)%vars())
    pass

@ndb.transactional
def deleteSession(x):
    scope=Scope('delete session %(x)r'%vars())
    for id in x.sessionFiles:
        log('deref uploaded file %(id)s'%vars())
        deref_uploaded_file(id)
        pass
    x.key.delete()
    
def expireOldSessions():
    q=Session.query(
        Session.touched < datetime.datetime.now()-datetime.timedelta(days=1),
        ancestor=root_key)
    for x in q.fetch(10000):
        log('expire session %(x)s'%vars())
        deleteSession(x)
    pass

def getSession(id):
    expireOldSessions()
    log('get session %(id)s'%vars())
    if id=='':
        result=[]
    else:
        log('query session %(id)s'%vars())
        q=Session.query(Session.sid==str(id),ancestor=root_key)
        result=q.fetch(1)
        pass
    if not len(result):
        result=[Session(parent=root_key,
                        sid=uuid.uuid1().hex,
                        touched=datetime.datetime.now())]
        log('new session '+result[0].sid)
    else:
        log('existing session '+result[0].sid+ ' level '+result[0].loginLevel)
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

class indexrc_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        self.response.write(file('index-rc.html').read())
        self.response.set_cookie('kc-session',session.sid)
        pass
    pass

class admin_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if session.loginLevel!='admin':
            log('not logged in as admin')
            return webapp2.redirect('admin_login.html')
        page=pq.loadFile('admin.html')
        page.find(pq.hasClass('login-level-name')).text(
            loginLevelName[session.loginLevel])
        page.find(pq.hasClass('edit-fair-details-panel')).addClass('kc-display-none')
        addScriptToPageHead('admin.js',page)
        self.response.write(unicode(page).encode('utf-8'))
        pass
    pass

class staff_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            log('not logged in as staff or admin')
            return webapp2.redirect('staff_login.html?from=staff.html')
        page=pq.loadFile('admin.html')
        page.find(pq.hasClass('admin-only')).remove()
        page.find(pq.hasClass('login-level-name')).text(
            loginLevelName[session.loginLevel])
        page.find(pq.hasClass('edit-fair-details-panel')).addClass('kc-display-none')
        addScriptToPageHead('admin.js',page)
        self.response.write(unicode(page).encode('utf-8'))
        pass
    pass
	
class fair_admin_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin','fair']:
            log('not logged in as staff or admin')
            return webapp2.redirect('fair_login.html')
        page=pq.loadFile('admin.html')
        page.find(pq.hasClass('admin-only')).remove()
        page.find(pq.hasClass('staff-only')).remove()
        page.find(pq.hasClass('login-level-name')).text(
            loginLevelName[session.loginLevel])
        page.find(pq.hasClass('edit-fair-details-panel')).addClass('kc-display-none')
        addScriptToPageHead('admin.js',page)
        self.response.write(unicode(page).encode('utf-8'))
        pass
    pass

class login_page(webapp2.RequestHandler):
    def get(self):
        page=pq.loadFile('login.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.headers.get('Referer','events.html'))
        self.response.write(unicode(page).encode('utf-8'))
        pass
    def post(self):
        level=None
        session=getSession(self.request.cookies.get('kc-session',''))
        if self.request.get('password','')==getPassword('parent'):
            session.loginLevel='parent'
            log('session %(id)s now logged in to level %(loginLevel)s'%{
                    'id':session.sid,
                    'loginLevel':session.loginLevel
                    })
            session.put()
            from_=str(self.request.get('from'))
            if from_=='' or from_=='login.html':
                from_='events.html'
                pass
            result=webapp2.redirect(from_)
            result.set_cookie('kc-session',session.sid)
            return result
        page=pq.loadFile('login.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.get('from',''))
        page.find(pq.hasClass('login_failed')).text('Incorrect Password')
        self.response.write(unicode(page).encode('utf-8'))
        pass

links_schema=jsonschema.Schema(
    [
        {
            'title':StringType,
            'url':StringType,
            'description':StringType
        }
    ]
)

class Links(ndb.Model):
    data=ndb.StringProperty(indexed=False,repeated=False)
    pass

def populateLinksDb():
    scope=Scope('put default links page links into database')
    links=[
        {
            'title':'Kindy Portal',
            'url':'https://www.kindyportal.com.au',
            'description':'''Kindy Portal is an online portfolio resource, documenting each child's adventures at kindy. Requires a password - issued via email from class teachers.'''
            },
        {
            'title':'Bardon Kindy Website',
            'url':'http://www.bardonkindy.com.au',
            'description':'''Bardon Communittee Kindy's public website.'''
            }]
    links_schema.validate(links)
    x=Links(parent=root_key,data=toJson(links))
    x.put()
    return [x]

@ndb.transactional
def getLinksFromDb():
    try:
        x=Links.query(ancestor=root_key).fetch(1)
        if len(x)==0:
            x=populateLinksDb()
            pass
        result=fromJson(x[0].data)
        result.sort(lambda a,b: cmp(
                (a['title'].lower(),a['description'].lower(),a['url'].lower()),
                (b['title'].lower(),b['description'].lower(),b['url'].lower())))
        return result
    except:
        raise inContext('get links from database')
    pass

def replaceSampleLinksWithLinksFromDb(links_page):
    page=links_page
    links_div=page.find(pq.hasClass('kindycal-py-links'))
    link_t=links_div.find(pq.hasClass('kindycal-py-sample-link'))\
        .remove().first()
    link_t.removeClass('kinyycal-py-sample-link')
    link_t.addClass('kindycal-py-link')
    for link in getLinksFromDb():
        link_div=link_t.clone()
        link_div.find(pq.hasClass('kindycal-py-title')).text(link['title'])
        link_div.find(pq.hasClass('kindycal-py-url'))\
            .text(link['url'])\
            .attr('href',link['url'])
        link_div.find(pq.hasClass('kindycal-py-description'))\
            .text(link['description'])
        link_div.appendTo(links_div)
        pass
    pass

class links_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if session.loginLevel in ['staff','admin']:
            return webapp2.redirect('edit_links.html')
        if not session.loginLevel:
            log('not logged in')
            return webapp2.redirect('login.html')
        page=pq.loadFile('links.html')
        page.find(pq.hasClass('staff-only')).remove()
        page.find(pq.hasClass('admin-only')).remove()
        replaceSampleLinksWithLinksFromDb(page)
        self.response.write(unicode(page).encode('utf-8'))
        pass
    pass

class edit_links_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin','staff']:
            log('not logged in')
            return webapp2.redirect('staff_login.html')
        page=pq.loadFile('links.html')
        page.find(pq.hasClass('parent-only')).remove()
        if not session.loginLevel in ['staff','admin']:
            page.find(pq.hasClass('staff-only')).remove()
            pass
        if not session.loginLevel in ['admin']:
            page.find(pq.hasClass('admin-only')).remove()
            pass
        replaceSampleLinksWithLinksFromDb(page)
        page.find(pq.tagName('body')).addClass(session.loginLevel)
        addAdminNavButtonToPage(page,session.loginLevel)
        addScriptToPageHead('links.js',page)
        makePageBodyInvisible(page)
        self.response.write(unicode(page).encode('utf-8'))
    pass

@ndb.transactional
def deleteLink(title,url,description):
    'delete links page link %(title)s %(url)s %(description)r'
    scope=Scope(l1(deleteLink.__doc__)%vars())
    try:
        x=Links.query(ancestor=root_key).fetch(1)[0]
        links=fromJson(x.data)
        links=[_ for _ in links if not (_['title']==title and
                                        _['url']==url and
                                        _['description']==description)]
        x.data=toJson(links)
        x.put()
    except:
        raise inContext(scope.description)
    pass

class delete_link(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel in ['admin','staff']:
                log('not logged in')
                return webapp2.redirect('staff_login.html')
            deleteLink(**fromJson(self.request.get('params')))
            result={'result':'OK'}
        except:
            result={'error':str(inContext('delete link'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

@ndb.transactional
def addLink(title,url,description):
    'add link %(title)r to %(url)r description %(description)r'
    scope=Scope(l1(addLink.__doc__)%vars())
    try:
        x=Links.query(ancestor=root_key).fetch(1)[0]
        links=fromJson(x.data)
        links.append({
                'title':title,
                'url':url,
                'description':description
                })
        links_schema.validate(links)
        x.data=toJson(links)
        x.put()
    except:
        raise inContext(scope.description)
    pass
        
class add_link(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel in ['staff','admin']:
                result={'error':'You are not logged in.'}
            else:
                result={'result':addLink(**fromJson(self.request.get('params')))}
        except:
            result={'error':str(inContext('post add_link'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

class change_parent_password_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            log('not logged in as staff or admin')
            return webapp2.redirect('staff_login.html')
        page=pq.loadFile('change_parent_password.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.headers.get('Referer',session.loginLevel+'.html'))
        addScriptToPageHead('change_parent_password.js',page)
        self.response.write(unicode(page).encode('utf-8'))
        pass
    def post(self):
        level=None
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            log('not logged in as staff or admin')
            return webapp2.redirect('staff_login.html')
        page=pq.loadFile('change_parent_password.html')
        inputs=page.find(pq.tagName('input'))
        if self.request.get('new_password')=='':
            inputs.filter(pq.attrEquals('name','new_password')).addClass('kc-invalid-input')
        elif self.request.get('confirm_new_password')!=self.request.get('new_password'):
            page.find(pq.hasClass('login_failed')).text('passwords do not match')
        else:
            setPassword('parent',self.request.get('new_password'))
            from_=self.request.get('from')
            log('from input '+repr(from_))
            from_=from_ or session.loginLevel.encode('utf8')+'.html'
            log(repr(from_))
            return webapp2.redirect(from_.encode('utf-8'))
        self.response.write(unicode(page).encode('utf-8'))
        pass

class change_staff_password_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin']:
            log('not logged in as admin')
            return webapp2.redirect('admin_login.html')
        page=pq.loadFile('change_staff_password.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.headers.get('Referer',session.loginLevel+'.html'))
        addScriptToPageHead('change_staff_password.js',page)
        self.response.write(unicode(page).encode('utf-8'))
        pass
    def post(self):
        level=None
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin']:
            log('not logged in as admin')
            return webapp2.redirect('admin_login.html')
        page=pq.loadFile('change_staff_password.html')
        inputs=page.find(pq.tagName('input'))
        if self.request.get('new_password')=='':
            inputs.filter(pq.attrEquals('name','new_password')).addClass('kc-invalid-input')
        elif self.request.get('confirm_new_password')!=self.request.get('new_password'):
            page.find(pq.hasClass('login_failed')).text('passwords do not match')
        else:
            setPassword('staff',self.request.get('new_password'))
            from_=self.request.get('from')
            log('from input '+repr(from_))
            from_=from_ or session.loginLevel.encode('utf8')+'.html'
            log(repr(from_))
            return webapp2.redirect(from_.encode('utf-8'))
        self.response.write(unicode(page).encode('utf-8'))
        pass

class admin_login_page(webapp2.RequestHandler):
    def get(self):
        page=pq.loadFile('admin_login.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.headers.get('Referer','admin.html'))
        self.response.write(unicode(page).encode('utf-8'))
        pass
    def post(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if self.request.get('password','')==getPassword('admin'):
            session.loginLevel='admin'
            log('session %(id)s now logged in to level %(loginLevel)s'%{
                    'id':session.sid,
                    'loginLevel':session.loginLevel
                    })
            session.put()
            from_=str(self.request.get('from'))
            if from_=='' or from_=='admin_login.html':
                from_='admin.html'
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
        session=getSession(self.request.cookies.get('kc-session',''))
        if self.request.get('password','')==getPassword('staff'):
            session.loginLevel='staff'
            log('session %(id)s now logged in to level %(loginLevel)s'%{
                    'id':session.sid,
                    'loginLevel':session.loginLevel
                    })
            session.put()
            from_=str(self.request.get('from'))
            if from_=='' or from_=='staff_login.html':
                from_='events.html'
                pass
            result=webapp2.redirect(from_)
            result.set_cookie('kc-session',session.sid)
            return result
        page=pq.loadFile('staff_login.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.get('from',''))
        page.find(pq.hasClass('login_failed')).text('Incorrect Password')
        self.response.write(unicode(page).encode('utf-8'))
        pass

class fair_login_page(webapp2.RequestHandler):
    def get(self):
        page=pq.loadFile('fair_login.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','from')).attr('value',self.request.get('from',''))
        self.response.write(unicode(page).encode('utf-8'))
        pass
    def post(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if self.request.get('password','')==getPassword('fair'):
            session.loginLevel='fair'
            log('session %(id)s now logged in to level %(loginLevel)s'%{
                    'id':session.sid,
                    'loginLevel':session.loginLevel
                    })
            session.put()
            from_=str(self.request.get('from'))
            if from_=='' or from_=='fair_login.html':
                from_='fair_admin.html'
                pass
            result=webapp2.redirect(from_)
            result.set_cookie('kc-session',session.sid)
            return result
        page=pq.loadFile('fair_login.html')
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
                log('save terms: '+toJson(data))
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
            log('not logged in as staff or admin')
            return webapp2.redirect('staff_login.html?from=edit_terms.html')
        log(self.request.headers)
        page=pq.loadFile('edit_terms.html')
        page.find(pq.tagName('input')).filter(pq.attrEquals('id','referer')).attr('value',self.request.headers.get('Referer','staff.html'))
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
            log('not logged in as staff')
            return webapp2.redirect('staff_login.html?from=edit_groups.html')
        page=pq.loadFile('edit_groups.html')

        page.find(pq.tagName('input')).filter(pq.attrEquals('id','referer')).attr('value',self.request.headers.get('Referer','staff.html'))
        self.response.write(unicode(page).encode('utf-8'))
    pass


def addAdminNavButtonToPage(page,loginLevel):
    adminNavButton=page.find(pq.attrEquals('id','navigation')).find(
        pq.tagName('li')).first().clone()
    adminNavButton.find(pq.tagName('a')).text('ADMIN')
    if loginLevel=='admin':
        adminNavButton.find(pq.tagName('a')).attr('href','admin.html')
        pass
    if loginLevel=='staff':
        adminNavButton.find(pq.tagName('a')).attr('href','staff.html')
        pass
    if loginLevel=='fair':
        adminNavButton.find(pq.tagName('a')).attr('href','fair_admin.html')
        pass
    adminNavButton.addBefore(
        page.find(pq.attrEquals('id','navigation')).find(
            pq.tagName('li')).first())
    pass

class events_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if session.loginLevel in ['staff','admin']:
            return webapp2.redirect('edit_events.html')
        if not session.loginLevel:
            log('not logged in')
            return webapp2.redirect('login.html')
        page=pq.loadFile('events.html')
        page.find(pq.hasClass('staff-only')).remove()
        page.find(pq.hasClass('admin-only')).remove()
        if session.loginLevel in ['admin','staff']:
            addAdminNavButtonToPage(page,session.loginLevel)
            pass
        addScriptToPageHead('events.js',page)
        makePageBodyInvisible(page)
        self.response.write(unicode(page).encode('utf-8'))
    pass


class edit_events_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin','staff']:
            log('not logged in')
            return webapp2.redirect('staff_login.html')
        if fetchTerms() is None:
            log('terms not defined')
            return webapp2.redirect('edit_terms.html')
        if fetchGroups() is None:
            log('groups not defined')
            return webapp2.redirect('edit_groups.html')
        page=pq.loadFile('events.html')
        page.find(pq.hasClass('parent-only')).remove()
        if not session.loginLevel in ['staff','admin']:
            page.find(pq.hasClass('staff-only')).remove()
            pass
        if not session.loginLevel in ['admin']:
            page.find(pq.hasClass('admin-only')).remove()
            pass
        page.find(pq.tagName('body')).addClass(session.loginLevel)
        addAdminNavButtonToPage(page,session.loginLevel)
        addScriptToPageHead('events.js',page)
        makePageBodyInvisible(page)
        self.response.write(unicode(page).encode('utf-8'))
    pass


def formatDate(d):
    return '%(day)s/%(month)s/%(year)s'%d

class event_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            log('not logged in')
            return webapp2.redirect('events.html?from=events.html')
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
        log(groups)
        log(event['groups'])
        g=' + '.join([groups[_]['name'] for _ in event['groups']])
        page.find(pq.hasClass('groups')).text(g)
        d=', '.join([formatDate(_) for _ in event['dates']])
        page.find(pq.hasClass('mdate')).text(d)
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
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                raise xn.Exception('You are not logged in')
            dflt='[]'
            if session.loginLevel in ['staff','admin']:
                dflt='[0,1,2,3]'
                pass
            groups_to_show=fromJson(self.request.get('params',dflt))
            jsonschema.Schema([IntType]).validate(groups_to_show)
            self.response.set_cookie('kc-groups-to-show',toJson(groups_to_show))
            result={}
        except:
            result={'error':str(inContext('set groups to show in kc-groups-to-show cookie'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

class UploadedFileIdCounter(ndb.Model):
    """Counter to assign ids to UploadedFiles."""
    nextUploadedFileId = ndb.IntegerProperty()

@ndb.transactional
def nextUploadedFileId():
    q=UploadedFileIdCounter.query(ancestor=root_key)
    x=q.fetch(1)
    if len(x)==0:
        x=UploadedFileIdCounter(parent=root_key)
        x.nextUploadedFileId=100
    else:
        x=x[0]
    result=x.nextUploadedFileId
    x.nextUploadedFileId=x.nextUploadedFileId+1
    x.put()
    return result


class UploadedFile(ndb.Model):
    id=ndb.IntegerProperty(indexed=True)
    mime_type=ndb.StringProperty(indexed=False,repeated=False) #eg image/jpeg
    data=ndb.BlobProperty(indexed=False,repeated=False)#file data
    data_hash=ndb.IntegerProperty(indexed=True)
    ref_count=ndb.IntegerProperty(indexed=False)
    pass

@ndb.transactional
def saveFile(session,mime_type,data):
    'save file as an UploadedFile in session %(session)r, returning id'
    'post: session has a reference to id'
    try:
        h=zlib.adler32(data)
        c=[_ for _ in UploadedFile.query(UploadedFile.data_hash==h,
                                         ancestor=root_key).fetch(100000)
           if _.data==data and _.mime_type==mime_type]
        if len(c):
            assert len(c)==1,c
            c=c[0]
            if not c.id in session.sessionFiles:
                c.ref_count=c.ref_count+1
                session.sessionFiles.append(c.id)
                session.put()
                pass
        else:
            c=UploadedFile(parent=root_key,
                           id=nextUploadedFileId(),
                           data_hash=h,
                           mime_type=mime_type,
                           data=data,
                           ref_count=1)
            assert not c.id in session.sessionFiles
            session.sessionFiles.append(c.id)
            session.put()
            pass
        c.put()
        return c.id
    except:
        raise inContext(l1(saveFile.__doc__)%vars())
    pass

@ndb.transactional
def deref_uploaded_file(id):
    'dereference UploadedFile %(id)r'
    try:
        c=UploadedFile.query(UploadedFile.id==id,
                             ancestor=root_key).fetch(2)
        assert len(c)==1,c
        c=c[0]
        c.ref_count=c.ref_count-1
        if c.ref_count==0:
            c.key.delete()
        else:
            c.put()
            pass
    except:
        raise inContext(l1(deref_uploaded_file.__doc__)%vars())
    pass

@ndb.transactional
def ref_uploaded_file(id):
    'reference UploadedFile %(id)r'
    try:
        c=UploadedFile.query(UploadedFile.id==id,
                             ancestor=root_key).fetch(2)
        assert len(c)==1,c
        c=c[0]
        assert c.ref_count>0
        c.ref_count=c.ref_count+1
        c.put()
        pass
    except:
        raise inContext(l1(ref_uploaded_file.__doc__)%vars())
    pass

def updateUploadedFiles(oldFileIds,newFileIds):
    'update UploadedFiles for a page that had uploaded file ids %(oldFileIds)s and now has uploaded file ids %(newFileIds)s '
    'ie drop references to files that are no longer referenced, add new references'
    scope=Scope(l1(updateUploadedFiles.__doc__)%vars())
    try:
        o=set(oldFileIds)
        n=set(newFileIds)
        for id in n-o:
            ref_uploaded_file(id)
            pass
        for id in o-n:
            deref_uploaded_file(id)
            pass
    except:
        raise inContext(scope.description)
    pass

class uploaded_file(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'You are not logged in.'}
            self.response.write(toJson(result))
        else:
            assert self.request.get('id')
            id=int(self.request.get('id'))
            f=UploadedFile.query(
                UploadedFile.id==id,
                ancestor=root_key).fetch(1)
            if len(f)==0:
                return self.error(404)
            f=f[0]
            self.response.headers['Content-Type'] = \
                f.mime_type.encode('ascii','ignore')
            self.response.write(f.data)
            pass
        pass
    def post(self):
        'uploaded_file POST'
        scope=Scope(l1(uploaded_file.post.__doc__)%vars())
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['staff','admin']:
                result={'error':'You are not logged in.'}
            else:
                assert 'filename' in self.request.POST,self.request.POST
                mime_type=self.request.POST['filename'].type
                data=self.request.get('filename')
                id=saveFile(session,mime_type,data)
                result=scope.result({
                        'result':{
                            'id':id,
                            'originalFileName':self.request.POST['filename'].filename}})
                pass
            pass
        except:
            result=scope.result({'error':str(inContext(scope.description))})
            
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

class uploaded_file_refcount(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'You are not logged in.'}
            self.response.write(toJson(result))
        else:
            assert self.request.get('id')
            id=int(self.request.get('id'))
            f=UploadedFile.query(
                UploadedFile.id==id,
                ancestor=root_key).fetch(2)
            if len(f)==0:
                result=0
            else:
                assert len(f)==1, len(f)
                result=f[0].ref_count
                pass
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write(toJson({'refcount':result}))
            pass
        pass
    pass

class EventIdCounter(ndb.Model):
    """Counter to assign ids to events."""
    nextEventId = ndb.IntegerProperty()

nextEventIdKey=ndb.Key('nextEventId','nextEventId')

@ndb.transactional
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
        'hidden':BooleanType,
        'description' : {
            'html' : StringType
            }
        })

def fixOldEventData(data):
    if not 'hidden' in data:
        data['hidden']=False
        pass
    return True

class Event(ndb.Model):
    # data is json encoded event_schema-conformant
    data=ndb.StringProperty(indexed=False,repeated=False)
    # id from data['id']
    id=ndb.IntegerProperty(indexed=True,repeated=False)
    # months of data['dates'], as yyyymm
    months=ndb.IntegerProperty(indexed=True,repeated=True)
    pass

@ndb.transactional
def deleteEvent(id):
    'delete event with id %(id)s'
    scope=Scope(l1(deleteEvent.__doc__)%vars())
    try:
        for x in Event.query(Event.id==id,ancestor=root_key).fetch(1):
            xdata=fromJson(x.data)
            for f in getUploadedFileRefsFromHTML(xdata['description']['html']):
                deref_uploaded_file(f)
                pass
            x.key.delete()
    except:
        raise inContext(scope.description)
    pass

class delete_event(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['staff','admin']:
                result={'error':'You are not logged in.'}
            else:
                data=fromJson(self.request.get('params'))
                assert 'id' in data, data.keys()
                deleteEvent(data['id'])
                self.response.write(toJson({'result':'OK'}))
                return
        except:
            result={'error':str(inContext('delete event'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

@ndb.transactional
def createEvent(eventId,data):
    'create event from %(data)r'
    scope=Scope(l1(createEvent.__doc__)%vars())
    try:
        fixOldEventData(data)
        event_schema.validate(data)
        assert data['id']==0
        data['id']=eventId
        event=Event(parent=root_key,
                    id=data['id'],
                    months=[_['year']*100+_['month'] \
                                for _ in data['dates']],
                    data=toJson(data))
        event.put()
        updateUploadedFiles(
            [],
            getUploadedFileRefsFromHTML(
                data['description']['html']))
        return data
    except:
        raise inContext(scope.description)
    pass

@ndb.transactional
def updateEvent(data):
    'update event %(data)r'
    scope=Scope(l1(updateEvent.__doc__)%vars())
    try:
        event_schema.validate(data)
        assert not data['id']==0
        x=Event.query(Event.id==data['id'],ancestor=root_key).fetch(1)
        if not len(x):
            scope2=Scope('re-creating deleted event')
            event=Event(parent=root_key,
                        id=data['id'],
                        months=[_['year']*100+_['month'] \
                                    for _ in data['dates']],
                        data=toJson(data))
            event.put()
            updateUploadedFiles([],getUploadedFileRefsFromHTML(
                    data['description']['html']))
        else:
            scop2=Scope('updating event')
            event=x[0]
            updateUploadedFiles(
                getUploadedFileRefsFromHTML(
                    fromJson(event.data)['description']['html']),
                getUploadedFileRefsFromHTML(
                    data['description']['html']))
            event.data=toJson(data)
            event.months=[_['year']*100+_['month'] \
                              for _ in data['dates']]
            event.put()
            pass
        return data
    except:
        raise inContext(scope.description)
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
            fixOldEventData(result)
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
                fixOldEventData(data)
                event_schema.validate(data)
                if data['id']==0:
                    result=createEvent(nextEventId(),data)
                else:
                    result=updateEvent(data)
                    pass
                fixOldEventData(data)
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

@ndb.transactional
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

@ndb.transactional
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

volunteer_schema=jsonschema.Schema({
        'childs_name':StringType,
        'parents_name':StringType,
        'attended':BooleanType,
        'note':StringType,#html
        })

maintenance_day_schema=jsonschema.Schema({
        'id': IntType, #0 for new MaintenanceDay
        'name': StringType,
        'date' : {'year':IntType,'month':IntType,'day':IntType},
        'groups': [ IntType ],
        'description' : {
            'html' : StringType
            },
        'maxVolunteers': IntType,
        'volunteers':[volunteer_schema]
        })

class MaintenanceDay(ndb.Model):
    # data is json encoded maintenance_day_schema-conformant
    data=ndb.StringProperty(indexed=False,repeated=False)
    # id from data['id']
    id=ndb.IntegerProperty(indexed=True,repeated=False)
    # month of data['date'], as yyyymm
    months=ndb.IntegerProperty(indexed=True,repeated=True)
    pass

@ndb.transactional
def deleteMaintenanceDay(id):
    'delete maintenance day with id %(id)r'
    scope=Scope(l1(deleteMaintenanceDay.__doc__)%vars())
    try:
        for x in MaintenanceDay.query(MaintenanceDay.id==id,
                                      ancestor=root_key).fetch(1):
            xdata=fromJson(x.data)
            oldUploadedFileRefs=getUploadedFileRefsFromHTML(xdata['description']['html'])|\
                getVolunteeersUploadedFileRefs(xdata['volunteers'])
            updateUploadedFiles(oldUploadedFileRefs,[])
            x.key.delete()
            pass
    except:
        raise inContext(scope.description)
    pass

class delete_maintenance_day(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['staff','admin']:
                result={'error':'You are not logged in.'}
            else:
                data=fromJson(self.request.get('params'))
                assert not data is None,data
                assert 'id' in data,repr(data)
                deleteMaintenanceDay(data['id'])
                self.response.write(toJson({'result':'OK'}))
                return
        except:
            result={'error':str(inContext('delete maintenance_day'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

def getUploadedFileRefsFromHTML(html):
    'get set of UploadedFile ids referred to in %(html)r (as image sources or link targets)'
    try:
        page=pq.parse(html)
        i=[int(_.attr('src').split('=')[1]) for _ in page.find(pq.tagName('img'))
           if _.attr('src').startswith('uploaded_file?id=')]
        a=[int(_.attr('href').split('=')[1]) for _ in page.find(pq.tagName('a'))
           if _.attr('href').startswith('uploaded_file?id=')]
        return set(i+a)
    except:
        raise inContext(l1(getUploadedFileRefsFromHTML.__doc__)%vars())
    pass

volunteers_schema=jsonschema.Schema([volunteer_schema])
def getVolunteeersUploadedFileRefs(volunteers):
    volunteers_schema.validate(volunteers)
    result=set()
    for v in volunteers:
        result|=getUploadedFileRefsFromHTML(v.get('note',''))
        pass
    return result

@ndb.transactional
def updateMaintenanceDay(data):
    'insert/update maintenance day %(data)r'
    scope=Scope(l1(updateMaintenanceDay.__doc__)%vars())
    try:
        if not 'name' in data: data['name']='Maintenance Day 8am'
        if not 'maxVolunteers' in data: data['maxVolunteers']=25
        maintenance_day_schema.validate(data)
        maintenance_day=MaintenanceDay(parent=root_key,
                                       id=data['id'],
                                       months=[_['year']*100+_['month'] \
                                                   for _ in [data['date']]],
                                       data=toJson(data))
        oldUploadedFileRefs=set()
        for x in MaintenanceDay.query(MaintenanceDay.id==maintenance_day.id,
                                      ancestor=root_key).fetch(1):
            xdata=fromJson(x.data)
            oldUploadedFileRefs|=getUploadedFileRefsFromHTML(xdata['description']['html'])|\
                getVolunteeersUploadedFileRefs(xdata['volunteers'])
            x.key.delete()
            pass
        newUploadedFileRefs=getUploadedFileRefsFromHTML(data['description']['html'])|\
            getVolunteeersUploadedFileRefs(data['volunteers'])
        maintenance_day.put()
        updateUploadedFiles(oldUploadedFileRefs,newUploadedFileRefs)
        result=fromJson(maintenance_day.data)
        maintenance_day_schema.validate(result)
        return result
    except:
        raise inContext(scope.description)
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
            if not 'name' in result: result['name']='Maintenance Day 8am'
            if not 'maxVolunteers' in result: result['maxVolunteers']=25
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
                if data['id']==0: data['id']=nextMaintenanceDayId()
                result={'result':updateMaintenanceDay(data)}
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
                log(y*100+m)
                events=[fromJson(_.data) for _ in
                        Event.query(Event.months==y*100+m,
                                    ancestor=root_key).fetch(10000)]
                for event in events:
                    fixOldEventData(event)
                    pass
                if not session.loginLevel in ['staff','admin']:
                    events=[_ for _ in events if not _['hidden']]
                    pass
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
                log(y*100+m)
                public_holidays=[fromJson(_.data) for _ in
                        PublicHoliday.query(
                        PublicHoliday.months==y*100+m,
                        ancestor=root_key).fetch(10000)]
                log(public_holidays)
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
                log(y*100+m)
                maintenance_days=[fromJson(_.data) for _ in
                        MaintenanceDay.query(
                        MaintenanceDay.months==y*100+m,
                        ancestor=root_key).fetch(10000)]
                for data in maintenance_days:
                    if not 'name' in data: data['name']='Maintenance Day 8am'
                    if not 'maxVolunteers' in data: data['maxVolunteers']=25
                    pass
                log(maintenance_days)
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
            log('not logged in as staff or admin')
            return webapp2.redirect('staff_login.html')
        page=pq.loadFile('edit_event.html')
        page.find(pq.attrEquals('id','id')).attr('value',self.request.get('id','0'))
        addScriptToPageHead('edit_event.js',page)
        makePageBodyInvisible(page)
        self.response.write(unicode(page).encode('utf-8'))
    pass

class edit_public_holiday_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            log('not logged in as staff or admin')
            return webapp2.redirect('staff_login.html')
        page=pq.loadFile('edit_public_holiday.html')
        page.find(pq.attrEquals('id','id')).attr('value',self.request.get('id','0'))
        addScriptToPageHead('edit_public_holiday.js',page)
        makePageBodyInvisible(page)
        self.response.write(unicode(page).encode('utf-8'))
    pass

class maintenance_day_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            log('not logged in')
            return webapp2.redirect('events.html')
        id=int(self.request.get('id'))
        if session.loginLevel in ['admin','staff']:
            return webapp2.redirect('edit_maintenance_day.html?id=%(id)s'%vars())
        maintenance_day=MaintenanceDay.query(MaintenanceDay.id==id,
                          ancestor=root_key).fetch(1)
        maintenance_day=fromJson(maintenance_day[0].data)
        if not 'name' in maintenance_day: maintenance_day['name']='Maintenance Day 8am'
        if not 'maxVolunteers' in maintenance_day: maintenance_day['maxVolunteers']=25
        maintenance_day_schema.validate(maintenance_day)
        page=pq.loadFile('maintenance_day.html')
        page.find(pq.attrEquals('id','id')).attr('value',str(id))
        page.find(pq.attrEquals('id','max-volunteers')).attr('value',str(
            maintenance_day['maxVolunteers']))
        page.find(pq.hasClass('maintenance-day-name')).text(maintenance_day['name'])
        d=formatDate(maintenance_day['date'])
        page.find(pq.hasClass('mdate')).text(d)
        page.find(pq.hasClass('job-description')).html(
            pq.parse(maintenance_day['description']['html']))
        volunteer_table=page.find(pq.hasClass('volunteers-table'))
        vrt=volunteer_table.find(pq.hasClass('volunteer-row')).remove().first()
        if len(maintenance_day['volunteers'])>=maintenance_day['maxVolunteers']:
            full=pq.parse('(FULL)').replace(
                page.find(pq.tagName('a')).filter(pq.hasClass('add-volunteer')))
            pass
        for v in maintenance_day['volunteers']:
            vr=vrt.clone()
            vr.find(pq.hasClass('volunteer-child-name')).text(
                v['childs_name'])
            vr.find(pq.hasClass('volunteer-parent-name')).text(
                v['parents_name'])
            vr.appendTo(volunteer_table)
            pass
        vrt.attr('style',"display:none")
        vrt.addClass('vr-template')
        vrt.appendTo(volunteer_table)
        page.find(pq.tagName('form')).filter(pq.attrEquals('id','close')).attr(
            'action',self.request.headers.get('Referer','events.html'))
        self.response.write(unicode(page).encode('utf-8'))
    pass


class edit_maintenance_day_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            log('not logged in as staff or admin')
            return webapp2.redirect('staff_login.html')
        page=pq.loadFile('edit_maintenance_day.html')
        page.find(pq.attrEquals('id','id')).attr('value',self.request.get('id','0'))
        addScriptToPageHead('edit_maintenance_day.js',page)
        addAdminNavButtonToPage(page,session.loginLevel)
        makePageBodyInvisible(page)
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','referer')).attr('value',self.request.headers.get('Referer','roster.html'))
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
                assert self.request.get('parents_name','')
                id=int(self.request.get('id'))
                childs_name=self.request.get('childs_name')
                parents_name=self.request.get('parents_name')
                maintenance_day=MaintenanceDay.query(
                    MaintenanceDay.id==id,
                    ancestor=root_key).fetch(1)[0]
                data=fromJson(maintenance_day.data)
                if not 'name' in data: data['name']='Maintenance Day 8am'
                if not 'maxVolunteers' in data: data['maxVolunteers']=25
                data['volunteers'].append({
                    'childs_name':childs_name,
                    'parents_name':parents_name,
                    'attended':False,
                    'note':'',
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

add_prefair_helper_schema=jsonschema.Schema({
    'stall_name':StringType,
    'name':StringType,
    'email':StringType,
    'note':StringType
    })

class add_prefair_helper(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                params=fromJson(self.request.get('params'))
                add_prefair_helper_schema.validate(params)
                stall_name=params['stall_name']
                entry = fair.StallPreFairHelper(
                    parent=fair.stall_key(stall_name),
                    name=params['name'],
                    email=params['email'],
                    note=params['note'])
                entry.put()
                if session.loginLevel in ['staff','admin']:
                    result={
                        'result':{
                            'added':True,
                            'details':fair.getStallPreFairHelpers(stall_name)
                            }
                        }
                else:
                    result={
                        'result':{
                            'added':True,
                            'names':[_['name'] for _ in fair.getStallPreFairHelpers(stall_name)],
                            }
                        }
                    pass
                pass
        except:
            result={'error':str(inContext('add_prefair_helper'))}
            pass
        return self.response.write(toJson(result))
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

twyc_schema=jsonschema.Schema({
        'date' : {'year':IntType,'month':IntType,'day':IntType},
        'group': IntType,
        'parents':[StringType]
        })

def make_twyc_id(date,group):
    return date['year']*1000000+date['month']*10000+date['day']*100+group

class TWYC(ndb.Model):
    # yyyymmddgg ... where gg is data['group'], rest from data['date']
    id=ndb.IntegerProperty(indexed=True,repeated=False)
    # data is json encoded twyc_schema-conformant
    data=ndb.StringProperty(indexed=False,repeated=False)
    # month of data['date'], as yyyymm
    months=ndb.IntegerProperty(indexed=True,repeated=True)
    pass

add_delete_twyc_schema=jsonschema.Schema({
        'date' : {'year':IntType,'month':IntType,'day':IntType},
        'group': IntType,
        'parent': StringType
        })

@ndb.transactional
def delete_twyc_(data):
    'delete twyc %(data)r'
    try:
        log(l1(delete_twyc_.__doc__)%vars())
        add_delete_twyc_schema.validate(data)
        date=data['date']
        group=data['group']
        parent=data['parent']
        twycs=TWYC.query(TWYC.id==make_twyc_id(date,group),
                         ancestor=root_key).fetch(2)
        assert len(twycs)<2,twycs
        for twyc in twycs:
            d=fromJson(twyc.data)
            d['parents']=[_ for _ in d['parents'] if not _ == parent ]
            twyc_schema.validate(d)
            twyc.data=toJson(d)
            twyc.put()
            pass
        pass
    except:
        raise inContext(l1(delete_twyc_.__doc__)%vars())
    pass

class delete_twyc(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['staff','admin']:
                result={'error':'You are not logged in.'}
            else:
                delete_twyc_(fromJson(self.request.get('params')))
                result={'result':'OK'}
        except:
            result={'error':str(inContext('post delete_twyc'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

@ndb.transactional
def add_twyc_(data):
    'add twyc %(data)r'
    try:
        add_delete_twyc_schema.validate(data)
        date=data['date']
        group=data['group']
        parent=data['parent']
        twycs=TWYC.query(
            TWYC.id==make_twyc_id(date,group),ancestor=root_key).fetch(1)
        if not len(twycs):
            twycs.append(TWYC(
                    parent=root_key,
                    id=make_twyc_id(date,group),
                    data=toJson({
                        'date':date,
                        'group':group,
                        'parents':[]
                        }),
                    months=[ date['year']*100+date['month']]))
            pass
        twyc=twycs[0]
        d=fromJson(twyc.data)
        if not parent in d['parents']:
            if len(d['parents'])==1:
                return d['parents'][0]
            d['parents'].append(parent)
            pass
        twyc_schema.validate(d)
        twyc.data=toJson(d)
        twyc.put()
        return parent
    except:
        raise inContext(l1(add_twyc_.__doc__)%vars())
    pass

class add_twyc(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                result={'result':add_twyc_(fromJson(self.request.get('params')))}
        except:
            result={'error':str(inContext('post add_twyc'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

month_twycs_schema=jsonschema.Schema([twyc_schema])

class month_twycs(webapp2.RequestHandler):
    def get(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                y=int(self.request.get('y'))
                m=int(self.request.get('m'))
                log(y*100+m)
                twycs=[fromJson(_.data) for _ in
                        TWYC.query(TWYC.months==y*100+m,
                                   ancestor=root_key).fetch(10000)]
                log(twycs)
                month_twycs_schema.validate(twycs)
                self.response.write(toJson({'result':twycs}))
        except:
            self.response.write(toJson({'error':str(inContext('get month twycs'))}))
            pass
        pass
    pass

class twyc_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            log('not logged in')
            return webapp2.redirect('login.html')
        if session.loginLevel in ['staff','admin']:
            return webapp2.redirect('edit_twyc.html')
        page=pq.loadFile('twyc.html')
        page.find(pq.hasClass('staff-only')).remove()
        page.find(pq.hasClass('admin-only')).remove()
        if session.loginLevel in ['admin','staff']:
            addAdminNavButtonToPage(page,session.loginLevel)
            pass
        addScriptToPageHead('twyc.js',page)
        makePageBodyInvisible(page)
        self.response.write(unicode(page).encode('utf-8'))
    pass


class edit_twyc_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin','staff']:
            log('not logged in')
            return webapp2.redirect('staff.html?from=events.html')
        if fetchTerms() is None:
            log('terms not defined')
            return webapp2.redirect('edit_terms.html')
        if fetchGroups() is None:
            log('groups not defined')
            return webapp2.redirect('edit_groups.html')
        page=pq.loadFile('twyc.html')
        page.find(pq.hasClass('parent-only')).remove()
        if not session.loginLevel in ['staff','admin']:
            page.find(pq.hasClass('staff-only')).remove()
            pass
        if not session.loginLevel in ['admin']:
            page.find(pq.hasClass('admin-only')).remove()
            pass
        page.find(pq.tagName('body')).addClass(session.loginLevel)
        addAdminNavButtonToPage(page,session.loginLevel)
        addScriptToPageHead('twyc.js',page)
        makePageBodyInvisible(page)
        self.response.write(unicode(page).encode('utf-8'))
    pass

class redirect_to_events_page(webapp2.RequestHandler):
    def get(self):
        return webapp2.redirect('events.html')
    def post(self):
        return webapp2.redirect('events.html')
    pass

roster_job_instance_schema=jsonschema.Schema({
        'groups':[IntType], # eg [0,1] for unit 1 "per-unit" task
                            #    [0,1,2,3] for "kindy-wide" task
        'volunteers':[ volunteer_schema ]})

roster_job_schema=jsonschema.Schema({
        'id': IntType,
        'name': StringType,
        'per': jsonschema.OneOf('group','unit','kindy-wide'),
        'description': StringType,#html
        'frequency': jsonschema.OneOf('as_required',
                                      'week',
                                      'term',
                                      'year'),
        'volunteers_required': IntType,
        'instances':[roster_job_instance_schema]})

def getRosterJobUploadedFileRefs(data):
    'get ids of uploaded file refs from roster job data %(data)r'
    try:
        roster_job_schema.validate(data)
        result=getUploadedFileRefsFromHTML(data['description'])
        for i in data['instances']:
            result |= getVolunteeersUploadedFileRefs(i['volunteers'])
            pass
        return result
    except:
        raise inContext(l1(getRosterJobUploadedFileRefs.__doc__)%vars())
    pass

def updateRosterJobUploadedFileIds(oldData,newData):
    updateUploadedFiles(getRosterJobUploadedFileRefs(oldData),
                        getRosterJobUploadedFileRefs(newData))
    pass

class roster_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            log('not logged in')
            return webapp2.redirect('login.html')
        if session.loginLevel in ['staff','admin']:
            return webapp2.redirect('edit_roster.html')
        page=pq.loadFile('roster.html')
        page.find(pq.hasClass('staff-only')).remove()
        page.find(pq.hasClass('admin-only')).remove()
        if session.loginLevel in ['admin','staff']:
            addAdminNavButtonToPage(page,session.loginLevel)
            pass
        addScriptToPageHead('roster.js',page)
        makePageBodyInvisible(page)
        self.response.write(unicode(page).encode('utf-8'))
    pass


class edit_roster_job_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['staff','admin']:
            log('not logged in as staff or admin')
            return webapp2.redirect('staff_login.html')
        page=pq.loadFile('edit_roster_job.html')
        page.find(pq.attrEquals('id','id')).attr('value',self.request.get('id','0'))
        addScriptToPageHead('edit_roster_job.js',page)
        addAdminNavButtonToPage(page,session.loginLevel)
        makePageBodyInvisible(page)
        self.response.write(unicode(page).encode('utf-8'))
    pass

class RosterJobIdCounter(ndb.Model):
    """Counter to assign ids to Roster Jobs."""
    nextRosterJobId = ndb.IntegerProperty()

nextRosterJobIdKey=ndb.Key('nextRosterJobId','nextRosterJobId')

@ndb.transactional
def nextRosterJobId():
    q=RosterJobIdCounter.query(ancestor=root_key)
    x=q.fetch(1)
    if len(x)==0:
        x=RosterJobIdCounter(parent=root_key)
        x.nextRosterJobId=100
    else:
        x=x[0]
    result=x.nextRosterJobId
    x.nextRosterJobId=x.nextRosterJobId+1
    x.put()
    return result

class RosterJob(ndb.Model):
    # data is json encoded roster_job_schema-conformant
    data=ndb.StringProperty(indexed=False,repeated=False)
    # id from data['id']
    id=ndb.IntegerProperty(indexed=True,repeated=False)
    pass

def deleteRosterJob(id):
    'delete roster job with id %(id)r'
    scope=Scope(l1(deleteRosterJob.__doc__)%vars())
    try:
        for x in RosterJob.query(RosterJob.id==id,
                                 ancestor=root_key).fetch(1):
            updateUploadedFiles(getRosterJobUploadedFileRefs(fromJson(x.data)),[])
            x.key.delete()
            pass
    except:
        raise inContext(scope.description)
    pass

class delete_roster_job(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['staff','admin']:
                result={'error':'You are not logged in.'}
            else:
                data=fromJson(self.request.get('params'))
                assert not data is None
                assert 'id' in data,repr(data)
                deleteRosterJob(data['id'])
                self.response.write(toJson({'result':'OK'}))
                return
        except:
            result={'error':str(inContext('delete roster_job'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

@ndb.transactional
def updateRosterJob(json_data):
    'update roster job %(json_data)r keeping any existing volunteers'
    scope=Scope(l1(updateRosterJob.__doc__)%vars())
    try:
        data=fromJson(json_data)
        assert not 'instances' in data
        id=int(data['id'])
        if id>0:
            job=RosterJob.query(RosterJob.id==id,
                                ancestor=root_key).fetch(1)[0]
            xdata=fromJson(job.data)
            oldUploadedFileRefs=getRosterJobUploadedFileRefs(xdata)
            existing_instances=xdata['instances']
            jsonschema.Schema([roster_job_instance_schema]).validate(
                existing_instances)
        else:
            assert id==0
            id=nextRosterJobId()
            data['id']=id
            job=RosterJob(parent=root_key,id=id)
            existing_instances=[]
            oldUploadedFileRefs=set()
            pass
        new_data=dict(data.items()+[('instances',existing_instances)])
        roster_job_schema.validate(new_data)
        newUploadedFileRefs=getRosterJobUploadedFileRefs(new_data)
        job.data=toJson(new_data)
        job.put()
        updateUploadedFiles(oldUploadedFileRefs,newUploadedFileRefs)
        return new_data['id']
    except:
        raise inContext(l1(updateRosterJob.__doc__)%vars())
    pass

class roster_job(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'You are not logged in.'}
        else:
            roster_job=RosterJob.query(
                RosterJob.id==int(self.request.get('id')),
                ancestor=root_key).fetch(1)
            if len(roster_job)==0:
                return self.error(404)
            result=fromJson(roster_job[0].data)
            roster_job_schema.validate(result)
            del(result['instances'])
            pass
        return self.response.write(toJson({'result':result}))
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if session.loginLevel not in ['staff','admin']:
                result={'error':'You are not logged in.'}
            else:
                id_=updateRosterJob(self.request.get('params'))
                result={'result':id_}
                pass
            pass
        except:
            result={'error':str(inContext('post roster_job'))}
            pass
        return self.response.write(toJson(result).encode('utf-8'))
    pass

class roster_jobs(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            result={'error':'You are not logged in.'}
        else:
            roster_jobs=RosterJob.query(ancestor=root_key).fetch(10000)
            result={'result':[fromJson(_.data) for _ in roster_jobs]}
            pass
        return self.response.write(toJson(result))
    pass

class edit_roster_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin','staff']:
            log('not logged in')
            return webapp2.redirect('staff.html?from=events.html')
        if fetchTerms() is None:
            log('terms not defined')
            return webapp2.redirect('edit_terms.html')
        if fetchGroups() is None:
            log('groups not defined')
            return webapp2.redirect('edit_groups.html')
        page=pq.loadFile('roster.html')
        page.find(pq.hasClass('parent-only')).remove()
        if not session.loginLevel in ['staff','admin']:
            page.find(pq.hasClass('staff-only')).remove()
            pass
        if not session.loginLevel in ['admin']:
            page.find(pq.hasClass('admin-only')).remove()
            pass
        page.find(pq.tagName('body')).addClass(session.loginLevel)
        addAdminNavButtonToPage(page,session.loginLevel)
        addScriptToPageHead('roster.js',page)
        makePageBodyInvisible(page)
        self.response.write(unicode(page).encode('utf-8'))
    pass

@ndb.transactional
def addRosterJobVolunteer(id,groups,parents_name,childs_name):
    'add %(parents_name)r (parent of %(childs_name)r as groups %(groups)r volunteer for job %(id)s'
    scope=Scope(l1(addRosterJobVolunteer.__doc__)%vars())
    try:
        roster_job=RosterJob.query(
            RosterJob.id==id,
            ancestor=root_key).fetch(1)[0]
        data=fromJson(roster_job.data)
        instances=dict(
            [(tuple(_['groups']),_['volunteers']) for _ in data['instances']])
        log('groups %(groups)s'%vars())
        assert [ _ for _ in groups if 0<=_ and _<4 ]==groups, groups
        instance=instances.setdefault(tuple(groups),[])
        added=False
        if len(instance)>=data['volunteers_required']:
            log('already have %s volunteers of %s - cannot add more'%(
                    len(instance),data['volunteers_required']))
        elif len([_ for _ in instance 
                  if _['parents_name']==parents_name and _['childs_name']==childs_name]):
            log('%(parents_name)r is already in %(instance)r'%vars())
            added=True #in a sense
        else:
            instance.append({
                    'parents_name':parents_name,
                    'childs_name':childs_name,
                    'attended':False,
                    'note':''
                    })
            data['instances']=[ {'groups':list(_[0]),
                                 'volunteers':_[1]} for _ in instances.items() ]
            roster_job_schema.validate(data)
            roster_job.data=toJson(data)
            roster_job.put()
            added=True
            pass
        result={
            'added':added,
            'instances':data['instances']
            }
        return scope.result(result)
    except:
        raise inContext(l1(addRosterJobVolunteer.__doc__)%vars())
    pass

class add_roster_job_volunteer(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                params=fromJson(self.request.get('params'))
                result=addRosterJobVolunteer(**params)
                result={'result':result}
                pass
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext('add roster job volunteer'))}))
            pass
        pass
    pass

@ndb.transactional
def updateVolunteerAttended(id,groups,volunteer,new_attended):
    'record %(new_attended)s as attendance of %(volunteer)r as groups %(groups)r volunteer for job %(id)s'
    scope=Scope(l1(updateVolunteerAttended.__doc__)%vars())
    try:
        roster_job=RosterJob.query(
            RosterJob.id==id,
            ancestor=root_key).fetch(1)[0]
        data=fromJson(roster_job.data)
        instances=dict(
            [(tuple(_['groups']),_['volunteers']) for _ in data['instances']])
        log('groups %(groups)s'%vars())
        assert [ _ for _ in groups if 0<=_ and _<4 ]==groups, groups
        instance=instances.get(tuple(groups))
        indices=[_[0] for _ in enumerate(instance) 
                 if _[1]['childs_name']==volunteer['childs_name'] and
                    _[1]['parents_name']==volunteer['parents_name']]
        for i in indices:
            instance[i]['attended']=new_attended
            pass
        roster_job_schema.validate(data)
        roster_job.data=toJson(data)
        roster_job.put()
        result='OK'
        return scope.result(result)
    except:
        raise inContext(l1(updateVolunteerAttended.__doc__)%vars())
    pass

class update_roster_job_volunteer_attended(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                params=fromJson(self.request.get('params'))
                result=updateVolunteerAttended(**params)
                result={'result':result}
                pass
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext('update_volunteer_attended'))}))
            pass
        pass
    pass

@ndb.transactional
def updateVolunteer(id,groups,volunteer,new_volunteer):
    'update %(volunteer)s as a groups %(groups)r volunteer for job %(id)s to %(new_volunteer)s'
    scope=Scope(l1(updateVolunteer.__doc__)%vars())
    try:
        roster_job=RosterJob.query(
            RosterJob.id==id,
            ancestor=root_key).fetch(1)[0]
        data=fromJson(roster_job.data)
        log('data was %(data)r'%vars())
        oldUploadedFileRefs=getRosterJobUploadedFileRefs(data)
        instances=dict(
            [(tuple(_['groups']),_['volunteers']) for _ in data['instances']])
        log('groups %(groups)s'%vars())
        assert [ _ for _ in groups if 0<=_ and _<4 ]==groups, groups
        instance=instances.get(tuple(groups))
        log('selected instance %(instance)r'%vars())
        indices=[_[0] for _ in enumerate(instance) 
                 if _[1]['childs_name']==volunteer['childs_name'] and
                    _[1]['parents_name']==volunteer['parents_name']]
        log('matched indices %(indices)r'%vars())
        for i in indices:
            instance[i]=new_volunteer
            pass
        roster_job_schema.validate(data)
        roster_job.data=toJson(data)
        newUploadedFileRefs=getRosterJobUploadedFileRefs(data)
        roster_job.put()
        updateUploadedFiles(oldUploadedFileRefs,newUploadedFileRefs)
        return scope.result(data)
    except:
        raise inContext(l1(updateVolunteer.__doc__)%vars())
    pass

class update_roster_job_volunteer(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                params=fromJson(self.request.get('params'))
                result=updateVolunteer(**params)
                result={'result':result}
                pass
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext('update_volunteer'))}))
            pass
        pass
    pass

@ndb.transactional
def deleteRosterJobVolunteer(id,groups,childs_name):
    'delete parent of %(childs_name)r as groups %(groups)r volunteer for job %(id)s'
    scope=Scope(l1(deleteRosterJobVolunteer.__doc__)%vars())
    try:
        roster_job=RosterJob.query(
            RosterJob.id==id,
            ancestor=root_key).fetch(1)[0]
        data=fromJson(roster_job.data)
        oldUploadedFileRefs=getRosterJobUploadedFileRefs(data)
        instances=dict(
            [(tuple(_['groups']),_['volunteers']) for _ in data['instances']])
        log('groups %(groups)s'%vars())
        assert [ _ for _ in groups if 0<=_ and _<4 ]==groups, groups
        if tuple(groups) in instances:
            log('found groups instance')
            volunteers=instances.get(tuple(groups))
            childs_names=dict( (_[1]['childs_name'],_[0]) for _ in enumerate(volunteers))
            log('childs_names %(childs_names)r')
            if childs_name in childs_names:
                index=childs_names[childs_name]
                log('found childs_name (index %(index)s)'%vars())
                del(volunteers[index])
                roster_job_schema.validate(data)
                roster_job.data=toJson(data)
                newUploadedFileRefs=getRosterJobUploadedFileRefs(data)
                roster_job.put()
                updateUploadedFiles(oldUploadedFileRefs,newUploadedFileRefs)
                log('job now %(data)r'%vars())
                pass
            pass
        result=data['instances']
        return scope.result(result)
    except:
        raise inContext(scope.description)
    pass

class delete_roster_job_volunteer(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                params=fromJson(self.request.get('params'))
                result=deleteRosterJobVolunteer(**params)
                result={'result':result}
                pass
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext('delete_roster_job_volunteer'))}))
            pass
        pass
    pass

class get_edit_image_panel(webapp2.RequestHandler):
    def get(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                page=pq.loadFile('edit_image.html')
                result={'result':unicode(page).encode('utf-8')}
                pass
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext('get_edit_image_panel'))}))
            pass
        pass
    pass

all_maintenance_days_schema=jsonschema.Schema([
        maintenance_day_schema])

class all_maintenance_days(webapp2.RequestHandler):
    def get(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                result=[fromJson(_.data) for _ in MaintenanceDay.query(ancestor=root_key).fetch(1000)]
                cmpDate=lambda x, y: cmp( (x['year'],x['month'],x['day']),
                                          (y['year'],y['month'],y['day']))
                for data in result:
                    if not 'name' in data: data['name']='Maintenance Day 8am'
                    if not 'maxVolunteers' in data: data['maxVolunteers']=25
                    pass
                result.sort(lambda x,y: cmpDate(x['date'],y['date']))
                all_maintenance_days_schema.validate(result)
                result={'result':result}
                pass
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext('all_maintenance_days'))}))
            pass
        pass
    pass

convenor_signup_schema=jsonschema.Schema({
    'stall_name':StringType,
    'name':StringType,
    'email':StringType,
    'phone':StringType
    })
class convenor_signup(webapp2.RequestHandler):
    def post(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                params=fromJson(self.request.get('params'))
                convenor_signup_schema.validate(params)
                stall_name=params['stall_name']
                q=fair.StallConvenor.query(ancestor=fair.stall_key(stall_name))
                convenor=q.fetch(1)
                if len(convenor):
                    entry=convenor[0]
                else:
                    entry = fair.StallConvenor(
                        parent=fair.stall_key(stall_name),
                        name='',
                        email='',
                        phone='')
                    pass
                if entry.name != '':
                    added=False
                else:
                    entry.name=params['name']
                    entry.email=params['email']
                    entry.phone=params['phone']
                    entry.put()
                    added=True
                    pass
                result={
                    'result':{
                        'added':added,
                        'name':entry.name,
                        'email':entry.email,
                        'phone':entry.phone
                    }
                }
                pass
        except:
            result={
                'error':str(inContext('convenor_signup'))
            }
            pass
        return self.response.write(toJson(result))
    pass

def normaliseChildsName(x):
    y=x.split()
    z=[_[0].upper()+_[1:] for _ in y]
    return ' '.join(z)

class roster_bychild(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin','staff']:
            log('not logged in')
            return webapp2.redirect('staff.html?from=events.html')
        data={}
        x=[fromJson(_.data) for _ in MaintenanceDay.query(ancestor=root_key).fetch(1000)]
        for maintenance_day in x:
            if not 'name' in maintenance_day: maintenance_day['name']='Maintenance Day 8am'
            if not 'maxVolunteers' in maintenance_day: maintenance_day['maxVolunteers']=25
            for v in maintenance_day['volunteers']:
                data.setdefault(normaliseChildsName(v['childs_name']),[]).append(
                    (maintenance_day['name']+' '+formatDate(maintenance_day['date']),
                     v['parents_name'],
                     v['attended'],
                     v.get('note',''),
                     'edit_maintenance_day.html?id=%(id)s'%maintenance_day))
                pass
            pass
        x=[fromJson(_.data) for _ in RosterJob.query(ancestor=root_key).fetch(10000)]
        for roster_job in x:
            for instance in roster_job['instances']:
                for v in instance['volunteers']:
                    data.setdefault(normaliseChildsName(v['childs_name']),[]).append(
                        (roster_job['name'],
                         v['parents_name'],
                         v['attended'],
                         v.get('note',''),
                         'edit_roster_job.html?id=%(id)s'%roster_job))
                    pass
                pass
            pass
        data=data.items()
        data.sort()
        page=pq.loadFile('roster_bychild.html')
        table=page.find(pq.hasClass('roster-jobs-table'))
        rowt=table.find(pq.tagName('tr')).filter(pq.hasClass('jobs')).remove().first()
        for childs_name,jobs in data:
            log('%(childs_name)s %(jobs)r'%vars())
            t2=rowt.clone()
            t2.find(pq.hasClass('volunteer-child-name')).text(childs_name)
            for job_name,parents_name,attended,note,href in jobs:
                t2.find(pq.hasClass('name')).find(pq.tagName('a'))\
                    .text(job_name)\
                    .attr('href',href)
                t2.find(pq.hasClass('volunteer-parent-name'))\
                    .text(parents_name)
                if attended:
                    t2.find(pq.hasClass('volunteer-attended')).text('Y')
                else:
                    t2.find(pq.hasClass('volunteer-attended')).text('')
                    pass
                t2.find(pq.hasClass('volunteer-note')).html(pq.parse(note))
                t2.appendTo(table)
                t2=rowt.clone()
                t2.find(pq.hasClass('volunteer-child-name')).text('')
                pass
            pass
        self.response.write(unicode(page).encode('utf-8'))
        pass
    pass

class logout(webapp2.RequestHandler):
    def get(self):
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                result={'error':'You are not logged in.'}
            else:
                deleteSession(session)
                result={'result':'OK'}
                pass
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext('all_maintenance_days'))}))
            pass
        pass
    pass
            
class export_data(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin','staff']:
            log('not logged in')
            return webapp2.redirect('staff.html?from=events.html')
        terms=[fromJson(_.data) for _ in Terms.query(ancestor=root_key).fetch(100)]
        groups=[fromJson(_.data) for _ in Groups.query(ancestor=root_key).fetch(100)]
        nextEventId=(EventIdCounter.query(ancestor=nextEventIdKey).fetch(1)+
                     [EventIdCounter(parent=nextEventIdKey,
                                     nextEventId=1)])[0].nextEventId
        events=[{'data':fromJson(_.data),
                 'id':_.id,
                 'months':_.months} for _ in
                Event.query(ancestor=root_key).fetch(100000)]
        nextPublicHolidayId=(PublicHolidayIdCounter.query(ancestor=nextPublicHolidayIdKey).fetch(1)+
                             [PublicHolidayIdCounter(parent=nextPublicHolidayIdKey,
                                                     nextPublicHolidayId=1)])[0].nextPublicHolidayId
        publicHolidays=[{'data':fromJson(_.data),
                         'id':_.id,
                         'months':_.months} for _ in
                        PublicHoliday.query(ancestor=root_key).fetch(100000)]
        nextMaintenanceDayId=(MaintenanceDayIdCounter.query(ancestor=nextMaintenanceDayIdKey).fetch(1)+
                              [MaintenanceDayIdCounter(parent=nextMaintenanceDayIdKey,
                                                       nextMaintenanceDayId=1)])[0].nextMaintenanceDayId
        maintenanceDays=[{'data':fromJson(_.data),
                          'id':_.id,
                          'months':_.months} for _ in
                         MaintenanceDay.query(ancestor=root_key).fetch(100000)]

        twycs=[{'data':fromJson(_.data),
                 'id':_.id,
                 'months':_.months} for _ in
                TWYC.query(ancestor=root_key).fetch(100000)]
        roster_jobs=[fromJson(_.data) for _ in
                     RosterJob.query(ancestor=root_key).fetch(100000)]
        self.response.headers['Content-Type'] = 'text/json'
        self.response.write(toJson({
                'terms':terms,
                'groups':groups,
                'nextEventId':nextEventId,
                'events':events,
                'nextPublicHolidayId':nextPublicHolidayId,
                'publicHolidays':publicHolidays,
                'nextMaintenanceDayId':nextMaintenanceDayId,
                'maintenanceDays':maintenanceDays,
                'twycs':twycs,
                'roster_jobs':roster_jobs,
                }))
        pass
    pass

class import_data_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['admin']:
            log('not logged in')
            return webapp2.redirect('admin.html')
        page=pq.loadFile('import_data.html')
        self.response.write(unicode(page).encode('utf-8'))
        pass
    pass

class import_data(webapp2.RequestHandler):
    def post(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if session.loginLevel not in ['admin']:
            result={'error':'You are not logged in.'}
        else:
            log(self.request.POST.keys())
            data=fromJson(self.request.get('filename'))
            assert 'terms' in data, data.keys()
            assert 'groups' in data, data.keys()
            assert 'events' in data, data.keys()
            assert 'nextPublicHolidayId' in data, data.keys()
            assert 'publicHolidays' in data, data.keys()
            assert 'nextMaintenanceDayId' in data, data.keys()
            assert 'maintenanceDays' in data, data.keys()
            assert 'twycs' in data, data.keys()
            if len(data['terms']):
                for _ in Terms.query(ancestor=root_key).fetch(10): _.key.delete()
                for _ in data['terms']:
                    terms_schema.validate(_)
                    t=Terms(parent=root_key,
                            data=toJson(_))
                    t.put()
                    pass
                self.response.write('%s Terms<br>'%len(data['terms']))
                pass
            if len(data['groups']):
                for _ in Groups.query(ancestor=root_key).fetch(10): _.key.delete()
                for _ in data['groups']:
                    groups_schema.validate(_)
                    t=Groups(parent=root_key,
                             data=toJson(_))
                    t.put()
                    pass
                self.response.write('%s Groups<br>'%len(data['groups']))
                pass
            if 'nextEventId' in data:
                for _ in EventIdCounter.query(ancestor=nextEventIdKey).fetch(10): _.key.delete()
                t=EventIdCounter(parent=nextEventIdKey,
                                 nextEventId=data['nextEventId'])
                t.put()
                self.response.write('EventCounter<br>')
                pass
            if len(data['events']):
                for _ in Event.query(ancestor=root_key).fetch(100000): _.key.delete()
                for _ in data['events']:
                    fixOldEventData(data)
                    event_schema.validate(_['data'])
                    t=Event(parent=root_key,
                            data=toJson(_['data']),
                            id=_['id'],
                            months=_['months'])
                    t.put()
                    pass
                self.response.write('%s events<br>'%len(data['events']))
                pass
            if 'nextPublicHolidayId' in data:
                for _ in PublicHolidayIdCounter.query(ancestor=nextPublicHolidayIdKey).fetch(10): _.key.delete()
                t=PublicHolidayIdCounter(parent=nextPublicHolidayIdKey,
                                         nextPublicHolidayId=data['nextPublicHolidayId'])
                t.put()
                self.response.write('PublicHolidayIdCounter<br>')
                pass
            if len(data['publicHolidays']):
                for _ in PublicHoliday.query(ancestor=root_key).fetch(100000): _.key.delete()
                for _ in data['publicHolidays']:
                    public_holiday_schema.validate(_['data'])
                    t=PublicHoliday(parent=root_key,
                                    data=toJson(_['data']),
                                    id=_['id'],
                                    months=_['months'])
                    t.put()
                    pass
                self.response.write('%s PublicHolidayss<br>'%len(data['publicHolidays']))
                pass
            if 'nextMaintenanceDayId' in data:
                for _ in MaintenanceDayIdCounter.query(ancestor=nextMaintenanceDayIdKey).fetch(10): _.key.delete()
                t=MaintenanceDayIdCounter(parent=nextMaintenanceDayIdKey,
                                 nextMaintenanceDayId=data['nextMaintenanceDayId'])
                t.put()
                self.response.write('MaintenanceDayCounter<br>')
                pass
            if len(data['maintenanceDays']):
                for _ in MaintenanceDay.query(ancestor=root_key).fetch(100000): _.key.delete()
                for _ in data['maintenanceDays']:
                    maintenance_day_schema.validate(_['data'])
                    t=MaintenanceDay(parent=root_key,
                            data=toJson(_['data']),
                            id=_['id'],
                            months=_['months'])
                    t.put()
                    pass
                self.response.write('%s MaintenanceDays<br>'%len(data['maintenanceDays']))
                pass
            if len(data['twycs']):
                for _ in TWYC.query(ancestor=root_key).fetch(100000): _.key.delete()
                for _ in data['twycs']:
                    twyc_schema.validate(_['data'])
                    t=TWYC(parent=root_key,
                            data=toJson(_['data']),
                            id=_['id'],
                            months=_['months'])
                    t.put()
                    pass
                self.response.write('%s twycs<br>'%len(data['twycs']))
                pass
            if 'roster_jobs' in data:
                for _ in RosterJob.query(ancestor=root_key).fetch(100000): _.key.delete()
                for _ in data['roster_jobs']:
                    #handle old data format
                    if 'data' in _: _=_['data']
                    roster_job_schema.validate(_)
                    t=RosterJob(parent=root_key,
                                data=toJson(_),
                                id=_['id'])
                    t.put()
                    pass
                self.response.write('%s roster jobs<br>'%len(data['roster_jobs']))
                pass
            self.response.write('OK')
            pass
        pass
    pass

class FairPage(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            log('not logged in')
            return webapp2.redirect('login.html')
        page=pq.loadFile('fair.html')
        page.find(pq.hasClass('staff-only')).remove()
        page.find(pq.hasClass('admin-only')).remove()
        if session.loginLevel in ['admin','staff']:
            addAdminNavButtonToPage(page,session.loginLevel)
            pass
        stalls=page.find(pq.hasClass('stalls'))
        for stall in stalls.children().filter(pq.tagName('div')):
            stall=pq.Selection(stall)
            stallname=stall.find(pq.hasClass('jobros')).attr('href')[0]
	    if stallname.startswith('/'):
                stallname=stallname[1:]
            #pass stall name to fair.js via id
            stall.attr('id',stallname)
            conv=fair.getStallConvenor(stallname)
            a=stall.find(pq.hasClass('stallconv')).find(pq.tagName('a'))
            if conv.name:
                a.attr('href','mailto:'+conv.email)
                a.text(conv.name)
                a.removeClass('stallconvac')
	    else:
                log(stallname)
		a.attr('href','/convenor_signup?stall_name='+stallname)
		a.attr('title','Click to volunteer as Convenor')
                a.addClass('stallconvac')
                a.text('VACANT')
        addScriptToPageHead('fair.js',page)
        page=fair.adjustFairDetails(page)
        #makePageBodyInvisible(page)
        self.response.write(unicode(page).encode('utf-8'))
    pass

class edit_fair_details_page(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['fair','staff','admin']:
            log('not fair/staff/admin')
            return webapp2.redirect('fair_login.html')
        page=pq.loadFile('edit_fair_details.html')
        page=fair.adjustFairDetails(page)
        addAdminNavButtonToPage(page,session.loginLevel)
        addScriptToPageHead('edit_fair_details.js',page)
        page.find(pq.tagName('input')).filter(pq.attrEquals('name','referer')).attr('value',self.request.headers.get('Referer','admin.html'))
        self.response.write(unicode(page).encode('utf-8'))
    pass

prefair_helper_t='''<span class="prefair-helper"><input type="hidden" class="name"><li>
</span>'''

class fair_StallPage(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            log('not logged in')
            return webapp2.redirect('login.html')
        stall_name = self.request.get(
            'stall_name',
            self.request.cookies.get('stall_name',
                                     fair.DEFAULT_STALL_NAME))
        self.response.set_cookie('stall_name',stall_name)
        content=fair.makeRosterContent(stall_name)
        page=pq.loadFile('stall.html')
        main=page.find(pq.tagName('main'))
        section_template=main.find(pq.tagName('section')).find(pq.attrEquals('id','info'))
        roster_section=section_template.clone()
        roster_section.attr('id','roster')
        roster_section.html(content)
        main.html(roster_section)
        stall=page.find(pq.hasClass('kindycal-py-stall'))
        stallname=stall_name
	if stallname.startswith('/'):
            stallname=stallname[1:]
        #pass stall name to fair.js via id
        stall.attr('id',stallname)
        conv=fair.getStallConvenor(stallname)
        a=stall.find(pq.hasClass('stallconv')).find(pq.tagName('a'))
        if conv.name:
            a.attr('href','mailto:'+conv.email)
            a.text(conv.name)
            a.removeClass('stallconvac')
	else:
            log(stallname)
	    a.attr('href','/convenor_signup?stall_name='+stallname)
	    a.attr('title','Click to volunteer as Convenor')
            a.addClass('helpros')
            a.text('VACANT')
            pass
        preFairHelpers=fair.getStallPreFairHelpers(stallname)
        preFairHelpersElement=page.find(pq.hasClass('pre-fair-helper-names'))
        sep=pq.parse('')
        page.find(pq.hasClass('pre-fair-helper-names')).text(', '.join(
            [_['name'] for _ in preFairHelpers]))
        dt=page.find(pq.hasClass('pre-fair-helper-detail')).remove().first()
        preFairHelpersElement=page.find(pq.hasClass('pre-fair-helper-details'))
        for h in preFairHelpers:
            d=dt.clone()
            d.find(pq.hasClass('pre-fair-helper-name')).text(h['name'])
            d.find(pq.hasClass('pre-fair-helper-mailto-link'))\
                .attr('href','mailto:'+h['email'])\
                .text(h['email'])
            d.find(pq.hasClass('pre-fair-helper-note')).text(h['note'])
            d.appendTo(preFairHelpersElement)
            pass
        dt.addClass('kc-display-none').appendTo(preFairHelpersElement)
        if not session.loginLevel in ['admin']:
            page.find(pq.hasClass('admin-only')).remove()
            pass
        if not session.loginLevel in ['staff','admin']:
            page.find(pq.hasClass('staff-only')).remove()
            pass
        if not session.loginLevel in ['fair','staff','admin']:
            page.find(pq.hasClass('fair-only')).remove()
            pass
        if not session.loginLevel in ['parent','fair']:
            page.find(pq.hasClass('parent-only')).remove()
            pass
        page.find(pq.hasClass('edit-stall-link')).attr('href','stalladmin?stall_name=%(stallname)s'%vars())
        addScriptToPageHead('stall.js',page)
        self.response.write(unicode(page).encode('utf-8'))

class fair_AddName(webapp2.RequestHandler):
    def post(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel:
            log('not logged in')
            return webapp2.redirect('login.html')
        stall_name = self.request.cookies.get('stall_name')
        hour = int(self.request.get('hour'))
        name = self.request.get('name')
        email = self.request.get('email',None)
        phone = self.request.get('phone',None)
        if name=='':
            self.redirect(fair.error('Please enter your name'))
            return
        if not self.request.get('email') is None and email=='':
            self.redirect(fair.error('Please enter your email'))
            return
        if not self.request.get('phone') is None and phone=='':
            self.redirect(fair.error('Please enter your mobile'))
            return
        try:
            ndb.transaction(lambda: fair.addName(stall_name,hour,name,email or '',phone or ''))
            self.redirect('stall')
        except fair.TooManyNames:
            self.redirect(fair.error('The shift is full. Too many names have been entered already. Please enter your name into another shift start time'))
            return
        except TransactionFailedError:
            self.redirect(fair.error('Please try again; Someone else put their name in at the same time'))


class fair_stalladmin(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['fair','staff','admin']:
            log('not logged in')
            return webapp2.redirect('fair_login.html')
        stall_name = self.request.get(
            'stall_name',
            self.request.cookies.get('stall_name', None))
        if stall_name is None:
            return webapp2.redirect('fair.html')
        self.response.set_cookie('stall_name',stall_name)
        page=pq.loadFile('stall_admin.html')
        page.find(pq.hasClass('stall_name')).text(fair.getStalls()[stall_name]['name'])
        page.find(pq.hasClass('stall_specific')).addClass('suppress')
        page.find(pq.hasClass('stall_specific')).find(pq.hasClass(stall_name))\
          .removeClass('suppress')
        q=fair.StallPrefs.query(ancestor=fair.stall_key(stall_name))
        prefs=q.fetch(1)
        if len(prefs):
            page.find(pq.hasClass('roster_instructions')).text(
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
        helpers_by_hour=[(hour,int(helpers_required.get(str(hour),fair.default_helpers_required(hour)))) for hour in range(8,21)]
        for hour,number_required in helpers_by_hour:
            page.find(pq.attrEquals('name','helpers_'+str(hour)))\
                .find(pq.attrEquals('value',str(number_required)))\
                .attr('checked','checked')
            pass
        roster_section=page.find(pq.tagName('section'))\
                           .filter(pq.attrEquals('id','roster'))
        roster_div=pq.parse('<div style="display:inline-block"></div>',
                            'roster_div')
        roster_div.appendTo(roster_section)
        roster_table=fair.makeRosterContent(stall_name).find(
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
                ' '.join([_ for _ in fair.getHelperEmails(stall_name) if _.strip()]))
        page.find(tagName('section')).filter(attrEquals('id','mobiles'))\
            .find(tagName('textarea')).text(
                ' '.join([_ for _ in fair.getHelperMobiles(stall_name) if _.strip()]))
        page.find(hasClass('non-admin-only')).remove()
        page.find(hasClass('stall-specific')).addClass('suppress')
        page.find(hasClass('stall-specific'))\
            .filter(hasClass(stall_name)).removeClass('suppress')
        preFairHelpers=fair.getStallPreFairHelpers(stall_name)
        preFairHelpersTable=page.find(pq.hasClass('pre-fair-helpers'))
        rt=preFairHelpersTable.find(pq.tagName('tr')).remove().first()
        for helper in preFairHelpers:
            r=rt.clone()
            r.find(pq.hasClass('stall-name')).attr('value',stall_name)
            r.find(pq.hasClass('helper-name')).text(helper['name'])
            r.find(pq.hasClass('helper-email')).text(helper['email'])
            r.find(pq.hasClass('helper-email')).attr('href','mailto:'+helper['email'])
            r.find(pq.hasClass('helper-note')).text(helper['note'])
            r.appendTo(preFairHelpersTable)
            pass
        if len(preFairHelpers)>0:
            page.find(pq.hasClass('no-prefair-helpers-yet')).remove()
            pass
        if session.loginLevel in ['admin','staff', 'fair']:
            addAdminNavButtonToPage(page,session.loginLevel)
        addScriptToPageHead('stall_admin.js',page)
        self.response.write(unicode(page).encode('utf-8'))
        pass
    pass

class FairConvenorListPage(webapp2.RequestHandler):
    def get(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['fair','staff','admin']:
            log('not logged in')
            return webapp2.redirect('fair_login.html')
        page=pq.loadFile('fair_convenor_list.html')
        list=page.find(pq.hasClass('stall-convenor-list'))
        vacant=list.find(pq.hasClass('no-convenor-yet')).first()
        rt=list.find(pq.hasClass('stall-row')).remove().first()
        list.children().remove()
        stalls=fair.getStalls().items()
        stalls.sort(lambda x,y: cmp(x[1]['name'],y[1]['name']))
        for stall in stalls:
            stall_name=stall[0]
            display_name=stall[1]['name']
            conv=fair.getStallConvenor(stall_name)
            log('stall %(stall_name)s convenor %(conv)r'%vars())
            r=rt.clone()
            r.find(pq.hasClass('adm'))\
             .attr('href','stalladmin?stall_name=%(stall_name)s'%vars())\
             .find(pq.hasClass('stall-name')).text(display_name)
            if conv.name=='':
                log('vacant')
                vacant.clone().replace(r.find(pq.hasClass('convenor')))
                pass
            else:
                log('not vacant')
                r.find(pq.hasClass('convenor-name')).text(conv.name)
                r.find(pq.hasClass('convenor-email'))\
                 .text(conv.email)\
                 .attr('href','mailto:'+conv.email)
                r.find(pq.hasClass('convenor-phone')).text(conv.phone)
                pass
            r.appendTo(list)
            pass
        self.response.write(unicode(page).encode('utf-8'))
        pass
    pass

class fair_adminsave(webapp2.RequestHandler):
    def post(self):
        session=getSession(self.request.cookies.get('kc-session',''))
        if not session.loginLevel in ['fair','staff','admin']:
            log('not logged in')
            return webapp2.redirect('fair_login.html')
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
            number=self.request.get('helpers_'+str(hour),fair.default_helpers_required(hour))
            helpers_required[str(hour)]=number
        q=fair.StallPrefs.query(ancestor=fair.stall_key(stall_name))
        prefs=q.fetch(1)
        if len(prefs):
            entry=prefs[0]
        else:
            entry = fair.StallPrefs(parent=fair.stall_key(stall_name))
        entry.roster_instructions=str(roster_instructions)
        entry.helpers_required=toJson(helpers_required)
        entry.ask_for_email=ask_for_email
        entry.ask_for_phone=ask_for_phone
        entry.put()            
        self.redirect('stalladmin')

class delete_stall_helper(webapp2.RequestHandler):
    def post(self):
        'delete stall helper'
        scope=Scope(l1(delete_stall_helper.post.__doc__)%vars())
        try:
            schema=jsonschema.Schema({
                    'helper_number':IntType,
                    'hour':IntType,
                    'stall_name':StringType
                    })
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel in ['fair','staff','admin']:
                log('not logged in')
                return webapp2.redirect('fair_login.html')
            params=schema.validate(fromJson(self.request.get('params')))
            fair.deleteHelper(**params)
            result={'result':'OK'}
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext(scope.description))}))
            pass
        pass
    pass


class delete_prefair_helper(webapp2.RequestHandler):
    def post(self):
        'delete prefair helper'
        scope=Scope(l1(delete_prefair_helper.post.__doc__)%vars())
        try:
            schema=jsonschema.Schema({
                    'stall_name':StringType,
                    'helper_name':StringType,
                    'email':StringType,
                    })
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel in ['fair','staff','admin']:
                log('not logged in')
                return webapp2.redirect('fair_login.html')
            params=schema.validate(fromJson(self.request.get('params')))
            fair.deletePreFairHelper(**params)
            result={'result':'OK'}
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext(scope.description))}))
            pass
        pass
    pass

class fair_details(webapp2.RequestHandler):
    def post(self):
        'set fair details'
        scope=Scope(l1(fair_details.post.__doc__)%vars())
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel in ['fair','staff','admin']:
                raise xn.Xn('not logged in')
            params=fromJson(self.request.get('params'))
            fair.setFairDetails(
                getUploadedFileRefsFromHTML,
                updateUploadedFiles,
                params['dateAndTime'],
                params['email'],
                params['message'])
            result={'result':'OK'}
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext(scope.description))}))
            pass
        pass
    def get(self):
        'get fair details'
        scope=Scope(l1(fair_details.get.__doc__)%vars())
        try:
            session=getSession(self.request.cookies.get('kc-session',''))
            if not session.loginLevel:
                raise xn.Xn('not logged in')
            details=fair.getFairDetails()
            result={'result':{
                    'email':details.email,
                    'dateAndTime':details.date_and_time,
                    'message':details.message}
                    }
            self.response.write(toJson(result))
        except:
            self.response.write(toJson({'error':str(inContext(scope.description))}))
            pass
        pass
    pass
            
application = webapp2.WSGIApplication([
    ('/', redirect_to_events_page),
    ('/admin.html',admin_page),
    ('/guru',admin_page),
    ('/admin',admin_page),
    ('/admin_login.html',admin_login_page),
    ('/change_parent_password.html',change_parent_password_page),
    ('/change_staff_password.html',change_staff_password_page),
    ('/edit_terms.html',edit_terms_page),
    ('/edit_groups.html',edit_groups_page),
    ('/edit_event.html',edit_event_page),
    ('/edit_events.html',edit_events_page),
    ('/edit_links.html',edit_links_page),
    ('/edit_maintenance_day.html',edit_maintenance_day_page),
    ('/edit_public_holiday.html',edit_public_holiday_page),
    ('/edit_twyc.html',edit_twyc_page),
    ('/edit_roster.html',edit_roster_page),
    ('/edit_roster_job.html',edit_roster_job_page),
    ('/event.html',event_page),
    ('/events.html',events_page),
    ('/index.html', redirect_to_events_page),
    ('/login.html',login_page),
    ('/links.html',links_page),
    ('/parent',login_page),
    ('/maintenance_day.html',maintenance_day_page),
    ('/staff.html',staff_page),
    ('/staff',staff_page),
    ('/staff_login.html',staff_login_page),
    ('/fair_login.html',fair_login_page),
    ('/twyc.html',twyc_page),
    ('/roster.html',roster_page),
    ('/index-rc.html',indexrc_page),
    ('/import_data.html',import_data_page),
    
    # following are not real pages, they are called by javascript files
    # to get and save data
    ('/add_maintenance_day_volunteer',add_maintenance_day_volunteer),
    ('/add_roster_job_volunteer',add_roster_job_volunteer),
    ('/all_maintenance_days',all_maintenance_days),
    ('/convenor_signup',convenor_signup),
    ('/delete_roster_job',delete_roster_job),
    ('/delete_roster_job_volunteer',delete_roster_job_volunteer),
    ('/get_edit_image_panel',get_edit_image_panel),
    ('/get_month_to_show',get_month_to_show),
    ('/groups',groups),
    ('/groups_to_show',groups_to_show),
    ('/terms',terms),
    ('/add_link',add_link),
    ('/add_twyc',add_twyc),
    ('/delete_twyc',delete_twyc),
    ('/month_calendar',month_calendar),
    ('/month_events',month_events),
    ('/month_maintenance_days',month_maintenance_days),
    ('/month_public_holidays',month_public_holidays),
    ('/month_twycs',month_twycs),
    ('/event',event),
    ('/maintenance_day',maintenance_day),
    ('/public_holiday',public_holiday),
    ('/roster_job',roster_job),
    ('/roster_jobs',roster_jobs),
    ('/roster_bychild.html',roster_bychild),
    ('/delete_event',delete_event),
    ('/delete_maintenance_day',delete_maintenance_day),
    ('/delete_public_holiday',delete_public_holiday),
    ('/delete_link',delete_link),
    ('/remember_month',remember_month),
    ('/export_data.txt',export_data),
    ('/import_data',import_data),
    ('/update_roster_job_volunteer_attended',update_roster_job_volunteer_attended),
    ('/update_roster_job_volunteer',update_roster_job_volunteer),
    ('/uploaded_file',uploaded_file),
    ('/uploaded_file_refcount',uploaded_file_refcount),
    ('/logout',logout),
#fair stuff:
    ('/fair',FairPage),
    ('/fair.html',FairPage),
    ('/edit_fair_details.html',edit_fair_details_page),
    ('/fair_details',fair_details),
    ('/fair_convenor_list.html',FairConvenorListPage),
    ('/stalladmin', fair_stalladmin),
    ('/stalladmin.html', fair_stalladmin),
    ('/fair_admin.html', fair_admin_page),
    ('/adminsave', fair_adminsave),
    ('/stall', fair_StallPage),
    ('/stall.html', fair_StallPage),
    ('/add', fair_AddName),
    ('/error', fair.Error),
    ('/delete_stall_helper', delete_stall_helper),
    ('/add_prefair_helper',add_prefair_helper),
    ('/delete_prefair_helper', delete_prefair_helper),
#fair redirects, so can do /Art and get to stall?stall_name=Art
    ('/Art',fair.ArtRedirect),
    ('/Auction',fair.AuctionRedirect),
    ('/Bar',fair.BarRedirect),
    ('/Books',fair.BooksRedirect),
    ('/BBQ',fair.BurgerServersRedirect),
    ('/BBQCooks',fair.BurgerBurnersRedirect),
    ('/Cakes',fair.CakesRedirect),
    ('/Coffee',fair.CoffeeRedirect),
	('/Craft',fair.CraftRedirect),
    ('/Drinks',fair.DrinksRedirect),
    ('/FacePainting',fair.FacePaintingRedirect),
	('/Floss',fair.FlossRedirect),
    ('/Garden',fair.GardenRedirect),
	('/Games',fair.GamesRedirect),
	('/Info',fair.InfoRedirect),
    ('/LobaChoc',fair.LobaChocRedirect),    
    ('/Lucky',fair.LuckyRedirect),
	('/MC',fair.MCRedirect),
    ('/PreLoved',fair.PreLovedRedirect),    
    ('/SweetTreats',fair.SweetTreatsRedirect),
    ('/Raffle',fair.RaffleRedirect),
	('/Rides',fair.RidesRedirect),
    ('/SetupSat',fair.SetupSatRedirect),
    ('/SetupSun',fair.SetupSunRedirect),
    ('/art',fair.ArtRedirect),
    ('/auction',fair.AuctionRedirect),
    ('/bar',fair.BarRedirect),
    ('/books',fair.BooksRedirect),
    ('/bbq',fair.BurgerServersRedirect),
    ('/bbqcooks',fair.BurgerBurnersRedirect),
    ('/cakes',fair.CakesRedirect),
    ('/coffee',fair.CoffeeRedirect),
	('/craft',fair.CraftRedirect),
    ('/drinks',fair.DrinksRedirect),
    ('/facepainting',fair.FacePaintingRedirect),
    ('/garden',fair.GardenRedirect),
	('/games',fair.GamesRedirect),
	('/info',fair.InfoRedirect),
    ('/lobachoc',fair.LobaChocRedirect),
    ('/rides',fair.RidesRedirect),
    ('/lucky',fair.LuckyRedirect),
	('/mc',fair.MCRedirect),
	('/Mc',fair.MCRedirect),
    ('/preloved',fair.PreLovedRedirect),
    ('/floss',fair.FlossRedirect),
    ('/sweettreats',fair.SweetTreatsRedirect),
    ('/raffle',fair.RaffleRedirect),
    ('/setupsat',fair.SetupSatRedirect),
    ('/setupsun',fair.SetupSunRedirect),
], debug=True)
