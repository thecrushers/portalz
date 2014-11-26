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


ALLOWED_SUBMITTERS = ['bobfromnextdoor']


class MainPage(webapp2.RequestHandler):
    def get(self):
        # Checks for active Google account session
        user = users.get_current_user()
        if user:
            template = JINJA_ENVIRONMENT.get_template('templates/index.html')
            self.response.write(template.render())
        else:
            self.redirect(users.create_login_url(self.request.uri))


class PortalPage(webapp2.RequestHandler):
    def get(self):
        # Checks for active Google account session
        user = users.get_current_user()
        if user:
            guid = self.request.get('guid')
            data = Portal.query(Portal.guid == guid).order(-Portal.submitted).fetch()
            template_values = dict(base=data[0] if len(data) > 0 else None,
                                   data=data)
            template = JINJA_ENVIRONMENT.get_template('templates/portal_show.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))


class PortalListPage(webapp2.RequestHandler):
    def get(self):
        # Checks for active Google account session
        user = users.get_current_user()
        if user:
            num_portals = Portal.query().count()
            portals = list(Portal.query(projection=[Portal.guid], distinct=True).fetch(20))
            template_values = dict(num_portals=num_portals,
                                   portals=portals)
            template = JINJA_ENVIRONMENT.get_template('templates/portal_list.html')
            self.response.write(template.render(template_values))
        else:
            self.redirect(users.create_login_url(self.request.uri))


class SubmitDetails(webapp2.RequestHandler):
    def post(self):
        content = json.loads(self.request.body)
        if content.get('submitter') in ALLOWED_SUBMITTERS:
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
                submitter=content.get('submitter'),
            )
            portal.put()

        self.response.headers.add('Access-Control-Allow-Origin', 'https://www.ingress.com')
        self.response.write("OK")

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
    submitter   = ndb.StringProperty(indexed=True)
    submitted   = ndb.DateTimeProperty(auto_now_add=True)

application = webapp2.WSGIApplication([
    ('/',               MainPage),
    ('/submit_details', SubmitDetails),
    ('/portal',         PortalPage),
    ('/portals',        PortalListPage)
], debug=True)
