#!/usr/bin/env python

import sys
import os.path

d=os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path.append(os.path.join(d,'www'))

import httplib
import urllib
import pq
from xn import inContext,firstLineOf
import sys
from pq import attrEquals,tagName
import random

l1=firstLineOf

import json
def toJson(x):
    return json.dumps(x,sort_keys=True,indent=4,separators=(',',': '))

def fromJson(x):
    return json.loads(x)

import types

def assert_equal(a,b):
    assert a==b,(a,b)
    pass
def assert_in(field,dictionary):
    assert field in dictionary,(field,dictionary)
    pass

class Scope:
    def __init__(self,description):
        self.description=description
        self.result_=None
        print '+ '+self.description
        pass
    def __del__(self):
        print '- '+self.description+' = '+repr(self.result_)
        pass
    def result(self,result):
        self.result_=result
        return result
    pass

def getSession(cookies):
    x=[_.strip() for _ in cookies.split(';') if _.startswith('kc-session=')]
    assert len(x)==1, (x,cookies)
    return x[0].split('=')[1]

class Staff:
    def __init__(self,server,staff_password):
        'login in to %(server)s/staff using password %(staff_password)s'
        try:
            self.c=httplib.HTTPConnection(server)
            self.c.set_debuglevel(1)
            self.c.request('GET','/staff_login.html')
            r=self.c.getresponse()
            page=pq.parse(r.read())
            assert len(page.find(tagName('input')).filter(attrEquals(
                        'name','password'))),(r,r.getheaders(),unicode(page))
            params=urllib.urlencode({
                    'password':staff_password
                    })
            self.c.request('POST','/staff_login.html',params)
            r=self.c.getresponse()
            assert r.status==302,(r.status,r.read())
            content=r.read()
            self.session=getSession(r.getheader('Set-Cookie'))
            assert not self.session is None, self.getheaders()
            self.headers={
                'Cookie':'kc-session=%s'%self.session
                }
            assert r.getheader('location')=='http://'+server+'/events.html', repr( (r,r.getheaders(),content) )
        except:
            raise inContext(l1(Staff.__init__.__doc__)%vars())
        pass
    def logout(self,headers={}):
        'logout %(self)s'
        scope=Scope(l1(Staff.logout.__doc__)%vars())
        try:
            headers['Cookie']='kc-session=%s'%self.session
            self.c.request('GET','/logout','',headers)
            r=self.c.getresponse()
            content=fromJson(r.read())
            assert content['result']=='OK',content
        except:
            raise inContext(scope.description)
        pass
    def get(self,url,params={},headers={}):
        'send HTTP GET to %(self)r page %(url)r with params %(params)r and headers %(headers)r'
        scope=Scope(l1(Staff.get.__doc__)%vars())
        try:
            assert url.startswith('/'),url
            headers['Cookie']='kc-session=%s'%self.session
            self.c.request('GET',url+'?'+urllib.urlencode(params),'',headers)
            return self.c.getresponse()
        except:
            raise inContext(scope.description)
        pass
    def post(self,url,params={},headers={}):
        'send HTTP POST to %(self)r page %(url)r with params %(params)r and headers %(headers)r'
        scope=Scope(l1(Staff.post.__doc__)%vars())
        try:
            assert url.startswith('/'),url
            headers['Cookie']='kc-session=%s'%self.session
            self.c.request('POST',url,urllib.urlencode(params),headers)
            return self.c.getresponse()
        except:
            raise inContext(scope.description)
        pass
    def postMulipartFormData(self,url,parts,headers={}):
        'post multipart/form-data to %(self)s url %(url)s'
        scope=Scope(l1(Staff.postMulipartFormData.__doc__)%vars())
        try:
            boundary='------------%08x%08x' % (random.randint(0,0xffffffff),random.randint(0,0xffffffff))
            while len([_ for _ in parts if boundary in _]):
                boundary='------------%08x%08x' % (random.randint(0,0xffffffff),random.randint(0,0xffffffff))
                pass
            body='\r\n'.join(['--'+boundary+'\r\n'+part for part in parts]+['--'+boundary+'--\r\n'])
            h=dict(headers.items())
            h['Content-Type']='multipart/form-data; boundary=%(boundary)s'%vars()
            h['Cookie']='kc-session=%s'%self.session
            self.c.request('POST',url,body,h)
            return self.c.getresponse()
        except:
            raise inContext(scope.description)
        pass

    def postFile(self,url,fieldName,fileName,mime_type,data,headers={}):
        'post file %(fileName)s of type %(mime_type)s as field %(fieldName)s to %(self)s url %(url)s'
        scope=Scope(l1(Staff.postFile.__doc__)%vars())
        try:
            lines=['Content-Disposition: form-data; name="%(fieldName)s"; filename="%(fileName)s"'%{
                    'fieldName':fieldName.replace(r'"',r'\"').encode('ascii'),
                    'fileName':fileName.replace(r'"',r'\"').encode('ascii')
                    },
                   'Content-Type: %(mime_type)s'%vars(),
                   '',
                   data]
            part='\r\n'.join(_ for _ in lines)
            return self.postMulipartFormData(url,[part],headers)
        except:
            raise inContext(scope.description)
        pass

    def uploadFile(self,fileName,mime_type,content,headers={}):
        'post %(fileName)s of type %(mime_type)s and given content to /uploaded_file, returning resulting id'
        scope=Scope(l1(Staff.__doc__)%vars())
        try:
            r=staff.postFile('/uploaded_file','filename',fileName,mime_type,content,headers)
            result=fromJson(r.read())
            assert 'result' in result, toJson(result).encode('utf8')
            assert 'id' in result['result']
            xxx=result['result']['id']
            assert type(xxx) is types.IntType, xxx
            assert xxx != 0, xxx
            return xxx
        except:
            raise inContext(scope.description)
        pass

    def verifyFileRefcount(self,uploadedFileId,expectedCount):
        'verify that %(self)s has %(expectedCount)s as uploaded_file %(uploadedFileId)s refcount'
        scope=Scope(l1(Staff.verifyFileRefcount.__doc__)%vars())
        try:
            r=self.get('/uploaded_file_refcount',{'id':uploadedFileId})
            assert r.status==200,r.status
            content=fromJson(r.read())
            assert 'refcount' in content,content
            assert content['refcount']==expectedCount,(content,expectedCount)
        except:
            raise inContext(scope.description)
        pass

    def verifyUploadedFile(self,uploadedFileId,mime_type,content):
        'verify that %(self)s uploaded_file %(uploadedFileId)s has type %(mime_type)s and content %(content)r'
        scope=Scope(l1(Staff.verifyUploadedFile.__doc__)%vars())
        try:
            r=staff.get('/uploaded_file',{'id':'%(uploadedFileId)s'%vars()})
            assert_equal(r.status,200)
            assert_equal(r.getheader('Content-Type'),'text/plain')
            assert_equal(r.read(),content)
        except:
            raise inContext(scope.description)
        pass
    def postJSON(self,url,params,headers={}):
        'post %(params)r as json encoded "params" to %(url)s'
        'return json-decode response'
        scope=Scope(l1(Staff.postJSON.__doc__)%vars())
        try:
            r=self.post(url,{'params':toJson(params)},headers)
            assert_equal(r.status,200)
            return scope.result(fromJson(r.read()))
        except:
            raise inContext(scope.description)
        pass
    def __str__(self):
        return 'Staff session %(session)r'%self.__dict__
    pass

server,staff_password=sys.argv[1:]

staff=Staff(server,staff_password)

xxx=staff.uploadFile('xxx.txt','text/plain','xxx\n')
staff.verifyFileRefcount(xxx,1)

r=staff.get('/uploaded_file',{'id':str(xxx)})
assert_equal(r.read(),'xxx\n')

yyy=staff.uploadFile('yyy.txt','text/plain','yyy\n')
staff.verifyFileRefcount(yyy,1)

r=staff.get('/uploaded_file',{'id':str(yyy)})
assert_equal(r.read(),'yyy\n')

assert xxx != yyy, (xxx,yyy)

assert_equal(staff.uploadFile('yyy2.txt','text/plain','yyy\n'),yyy)
staff.verifyFileRefcount(yyy,1)

prev_session=staff.session
staff.logout()
del staff

staff=Staff(server,staff_password)

assert prev_session!=staff.session, (prev_session,staff.session)

staff.verifyFileRefcount(xxx,0)
staff.verifyFileRefcount(yyy,0)

r=staff.get('/uploaded_file',{'id':str(yyy)})
assert_equal(r.status,404)
assert_equal(r.read(),'')

yyy3=staff.uploadFile('yyy3.txt','text/plain','yyy\n')
staff.verifyFileRefcount(yyy3,1)

assert_in('result',staff.postJSON('/event',{
            'id': 101,
            'groups': [0],
            'dates': [ { 'year':2016,'month':3,'day':13 } ],
            'name':{
                'text':'event 101',
                'colour':'#000000'
                },
            'description': {
                'html': 'event 101 <img src="uploaded_file?id=%(yyy3)s">'%vars()
                }
            }))

staff.verifyFileRefcount(yyy3,2)

mf1=staff.uploadFile('mf1.txt','text/plain','mf1\n')
staff.verifyFileRefcount(mf1,1)

mf2=staff.uploadFile('mf2.txt','text/plain','mf2\n')
staff.verifyFileRefcount(mf2,1)

assert_in('result',staff.postJSON('/maintenance_day',{
                'id':102,
                'name':'md1',
                'date':{'year':2016,'month':3,'day':23},
                'groups':[3],
                'description':{'html':'<a href="uploaded_file?id=%(mf1)s">mf1</a>'%vars()},
                'maxVolunteers':2,
                'volunteers':[{
                        'childs_name':'fred jr',
                        'parents_name':'fred',
                        'attended':True,
                        'note':'<a href="uploaded_file?id=%(mf2)s">mf2</a>'%vars()
                        }]
                }))

staff.verifyFileRefcount(yyy3,2)
staff.verifyFileRefcount(mf1,2)
staff.verifyFileRefcount(mf2,2)

prev_session=staff.session
staff.logout()

staff=Staff(server,staff_password)

assert prev_session!=staff.session, (prev_session,staff.session)

staff.verifyFileRefcount(yyy3,1)
staff.verifyFileRefcount(mf1,1)
staff.verifyFileRefcount(mf2,1)

staff.verifyUploadedFile(yyy3,'text/plain','yyy\n')
staff.verifyUploadedFile(mf1,'text/plain','mf1\n')
staff.verifyUploadedFile(mf2,'text/plain','mf2\n')

assert_in('result',staff.postJSON(
        '/maintenance_day',
        {
            'id':102,
            'name':'md1',
            'date':{'year':2016,'month':3,'day':23},
            'groups':[3],
            'description':{'html':'<a href="uploaded_file?id=%(mf1)s">mf1</a>'%vars()},
            'maxVolunteers':2,
            'volunteers':[{
                    'childs_name':'fred jr',
                    'parents_name':'fred',
                    'attended':True,
                    'note':'none'%vars()
                    }]
            }))
             
staff.verifyFileRefcount(yyy3,1)
staff.verifyFileRefcount(mf1,1)
staff.verifyFileRefcount(mf2,0)

staff.verifyUploadedFile(mf1,'text/plain','mf1\n')

rj1=staff.postJSON('/roster_job',{
        'id':0,
        'name':'Chicken Feeding',
        'per':'unit',
        'description':'chicken feeding as per <a href="uploaded_file?id=%(mf1)s">mf1.txt</a>'%vars(),
        'frequency':'as_required',
        'volunteers_required':3})['result']

staff.verifyFileRefcount(mf1,2)

assert_equal(fromJson(staff.get('/roster_job',{'id':rj1}).read())['result'],{
        'id':rj1,
        'name':'Chicken Feeding',
        'per':'unit',
        'description':'chicken feeding as per <a href="uploaded_file?id=%(mf1)s">mf1.txt</a>'%vars(),
        'frequency':'as_required',
        'volunteers_required':3})

mf3=staff.uploadFile('mf3.jpg','image/jpeg','mf3')
staff.verifyFileRefcount(mf3,1)

assert_in('result',staff.postJSON('/roster_job',{
        'id':rj1,
        'name':'Chicken Feeding',
        'per':'unit',
        'description':'chicken feeding as like <img src="uploaded_file?id=%(mf3)s">'%vars(),
        'frequency':'as_required',
        'volunteers_required':3}))

staff.verifyFileRefcount(yyy3,1)
staff.verifyFileRefcount(mf1,1)
staff.verifyFileRefcount(mf2,0)
staff.verifyFileRefcount(mf3,2)

assert_equal(staff.postJSON('/add_roster_job_volunteer',{
            'id':rj1,
            'groups':[1,2],
            'parents_name':'jock',
            'childs_name':'jock jr'})['result']['added'],True)

assert_in('result',staff.postJSON('/update_roster_job_volunteer',{
            'id':rj1,
            'groups':[1,2],
            'volunteer':{
                'childs_name':'jock jr',
                'parents_name':'jock',
                'attended':True,
                'note':''
                },
            'new_volunteer':{
                'childs_name':'jock jr',
                'parents_name':'jock',
                'attended':True,
                'note':'saw <img src="uploaded_file?id=%(mf3)s">'%vars()
                }}))

assert_equal(staff.postJSON('/add_roster_job_volunteer',{
            'id':rj1,
            'groups':[1,2],
            'parents_name':'fred',
            'childs_name':'fred jr'})['result']['added'],True)

assert_in('result',staff.postJSON('/update_roster_job_volunteer',{
            'id':rj1,
            'groups':[1,2],
            'volunteer':{
                'childs_name':'fred jr',
                'parents_name':'fred',
                'attended':True,
                'note':''
                },
            'new_volunteer':{
                'childs_name':'fred jr',
                'parents_name':'fred',
                'attended':True,
                'note':'saw <img src="uploaded_file?id=%(yyy3)s">'%vars()
                }}))

staff.verifyFileRefcount(yyy3,2)
staff.verifyFileRefcount(mf1,1)
staff.verifyFileRefcount(mf2,0)
staff.verifyFileRefcount(mf3,2)

assert_in('result',staff.postJSON('/delete_roster_job_volunteer',{
            'id':rj1,
            'groups':[1,2],
            'childs_name':'fred jr',
            }))

staff.verifyFileRefcount(yyy3,1)
staff.verifyFileRefcount(mf1,1)
staff.verifyFileRefcount(mf2,0)
staff.verifyFileRefcount(mf3,2)

assert_in('result',staff.postJSON('/roster_job',{
        'id':rj1,
        'name':'Chicken Feeding',
        'per':'unit',
        'description':'chicken feeding',
        'frequency':'as_required',
        'volunteers_required':3}))

staff.verifyFileRefcount(yyy3,1)
staff.verifyFileRefcount(mf1,1)
staff.verifyFileRefcount(mf2,0)
staff.verifyFileRefcount(mf3,2)

rj2=staff.postJSON('/roster_job',{
        'id':0,
        'name':'Chicken Feeding 3',
        'per':'unit',
        'description':'chicken feeding as per <a href="uploaded_file?id=%(mf3)s">mf3.txt</a>'%vars(),
        'frequency':'as_required',
        'volunteers_required':3})['result']

staff.verifyFileRefcount(yyy3,1)
staff.verifyFileRefcount(mf1,1)
staff.verifyFileRefcount(mf2,0)
staff.verifyFileRefcount(mf3,3)

assert_in('result',staff.postJSON('/delete_roster_job',{'id':rj1}))

staff.verifyFileRefcount(yyy3,1)
staff.verifyFileRefcount(mf1,1)
staff.verifyFileRefcount(mf2,0)
staff.verifyFileRefcount(mf3,2)

assert_in('result',staff.postJSON('/delete_maintenance_day',{'id':102}))
assert_in('result',staff.postJSON('/delete_roster_job',{'id':rj2}))

staff.verifyFileRefcount(yyy3,1)
staff.verifyFileRefcount(mf1,0)
staff.verifyFileRefcount(mf2,0)
staff.verifyFileRefcount(mf3,1)

assert_in('result',staff.postJSON('/delete_event',{'id':101}))

staff.verifyFileRefcount(yyy3,0)
staff.verifyFileRefcount(mf1,0)
staff.verifyFileRefcount(mf2,0)
staff.verifyFileRefcount(mf3,1)

staff.logout()
staff=Staff(server,staff_password)
staff.verifyFileRefcount(yyy3,0)
staff.verifyFileRefcount(mf1,0)
staff.verifyFileRefcount(mf2,0)
staff.verifyFileRefcount(mf3,0)
staff.logout()
