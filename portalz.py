import os

import webapp2
import jinja2
import json

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


class SubmitPortal(webapp2.RequestHandler):
    def post(self):
        content = json.loads(self.request.body)
        portal = Portal(
            guid=content.get('guid'),
            name=content.get('title'),
            location=ndb.GeoPt(int(content.get("latE6")) / 1000000., int(content.get("lngE6")) / 1000000.),
            image=content.get('image'),
            level=int(content.get('level')),
            resonators=int(content.get('resCount')),
            health=content.get('health'),
            team=content.get('team').lower(),
        )
        portal.put()
        self.response.headers.add('Access-Control-Allow-Origin', 'https://www.ingress.com')
        self.response.write(portal.guid)

    def options(self):
        self.response.headers.add('Access-Control-Allow-Origin', 'https://www.ingress.com')
        self.response.write("OK")


class SubmitDetails(webapp2.RequestHandler):
    def post(self):
        content = json.loads(self.request.body)
        portal = Portal(
            guid=content.get('guid'),
            name=content.get('title'),
            location=ndb.GeoPt(int(content.get("latE6")) / 1000000., int(content.get("lngE6")) / 1000000.),
            image=content.get('image'),
            level=int(content.get('level')),
            resonators=int(content.get('resCount')),
            owner=content.get('owner'),
            health=content.get('health'),
            team=content.get('team').lower(),
        )
        portal.put()
        self.response.headers.add('Access-Control-Allow-Origin', 'https://www.ingress.com')
        self.response.write(portal.guid)

    def options(self):
        self.response.headers.add('Access-Control-Allow-Origin', 'https://www.ingress.com')
        self.response.write("OK")


class Portal(ndb.Model):
    name        = ndb.StringProperty(indexed=True)
    guid        = ndb.StringProperty(indexed=True)
    image       = ndb.StringProperty(indexed=False)
    owner       = ndb.StringProperty(indexed=True)
    location    = ndb.GeoPtProperty()
    level       = ndb.IntegerProperty()
    health      = ndb.IntegerProperty()
    team        = ndb.StringProperty(indexed=True)
    resonators  = ndb.IntegerProperty()
    tags        = ndb.StringProperty(repeated=True)
    submitor    = ndb.UserProperty()
    submitted   = ndb.DateTimeProperty(auto_now_add=True)

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/submit_portal', SubmitPortal),
    ('/submit_details', SubmitDetails)
], debug=True)
