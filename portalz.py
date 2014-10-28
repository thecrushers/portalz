import os

import webapp2
import jinja2

from google.appengine.ext import ndb
from google.appengine.api import users

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)


class MainPage(webapp2.RequestHandler):
    def get(self):
        # Checks for active Google account session
        user = users.get_current_user()

        if user:
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('Hello, World!')
        else:
            self.redirect(users.create_login_url(self.request.uri))


class Portal(ndb.Model):
    name        = ndb.StringProperty(indexed=True)
    description = ndb.TextProperty()
    owner_uid   = ndb.StringProperty(indexed=True)
    owner_name  = ndb.StringProperty(indexed=True)
    location    = ndb.GeoPtProperty()
    tags        = ndb.StringProperty(repeated=True)
    captured    = ndb.DateTimeProperty(auto_now_add=False)
    submitted   = ndb.DateTimeProperty(auto_now_add=True)

application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
