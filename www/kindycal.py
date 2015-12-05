import sys
import cgi
import urllib
import calendar
import webapp2

from google.appengine.ext import ndb

class index(webapp2.RequestHandler):
    def get(self):
        self.response.write(file('index.html').read())
        pass
    pass

application = webapp2.WSGIApplication([
        ('/', index),
], debug=True)
