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

class Scope:
    def __init__(self,description):
        self.description=description
        self.result=None
        print '+ '+self.description
        pass
    def __del__(self):
        print '- '+self.description+' = '+repr(self.result)
        pass
    def result(self,result):
        self.result=result
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
    
    def __str__(self):
        return 'Staff session %(session)r'%self.__dict__
    pass

server,staff_password=sys.argv[1:]

staff=Staff(server,staff_password)


r=staff.postFile('/uploaded_file','filename','xxx.txt','text/plain','xxx\n')

result=fromJson(r.read())

assert 'result' in result, toJson(result).encode('utf8')
assert 'id' in result['result']

xxx=result['result']['id']

assert type(xxx) is types.IntType, xxx
assert xxx != 0, xxx

r=staff.get('/uploaded_file',{'id':str(xxx)})
content=r.read()
assert content=='xxx\n'

r=staff.postFile('/uploaded_file','filename','yyy.txt','text/plain','yyy\n')

result=fromJson(r.read())

assert 'result' in result, toJson(result).encode('utf8')
assert 'id' in result['result']

yyy=result['result']['id']

assert type(yyy) is types.IntType, yyy
assert yyy != 0, yyy

r=staff.get('/uploaded_file',{'id':str(yyy)})
content=r.read()
assert content=='yyy\n'

assert xxx != yyy, (xxx,yyy)

r=staff.postFile('/uploaded_file','filename','yyy2.txt','text/plain','yyy\n')

result=fromJson(r.read())

assert 'result' in result, toJson(result).encode('utf8')
assert 'id' in result['result']

yyy2=result['result']['id']

assert type(yyy2) is types.IntType, yyy2
assert yyy2==yyy, (yyy2,yyy)

prev_session=staff.session
staff.logout()


staff=Staff(server,staff_password)

assert prev_session!=staff.session, (prev_session,staff.session)

r=staff.get('/uploaded_file',{'id':str(yyy)})
assert r.status==404, r.status
content=r.read()
assert content=='',content


r=staff.postFile('/uploaded_file','filename','yyy3.txt','text/plain','yyy\n')

result=fromJson(r.read())

assert 'result' in result, toJson(result).encode('utf8')
assert 'id' in result['result']

yyy3=result['result']['id']

assert type(yyy3) is types.IntType, yyy3
assert yyy3!=yyy, (yyy3,yyy)

