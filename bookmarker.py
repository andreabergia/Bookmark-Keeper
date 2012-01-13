import webapp2
import json

from google.appengine.ext import db
from google.appengine.api import users

class Link(db.Model):
    url = db.LinkProperty()
    user = db.UserProperty()


class List(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'application/json'

    user = users.get_current_user()
    assert(user)

    urls = []
    links = db.GqlQuery("SELECT * "
                        "FROM Link "
                        "WHERE user = :1",
                        user)
    for link in links:
        urls.append({"url" : link.url, "id" : str(link.key())})
    respJSON = json.dumps(urls)

    self.response.out.write(respJSON)


class Add(webapp2.RequestHandler):
  def post(self):
    user = users.get_current_user()
    assert(user)

    url = self.request.get('url')

    link = Link()
    link.url = db.Link(url)
    link.user = user
    link.put()

    respJSON = json.dumps( {'ok': True, 'id': str(link.key())} )
    self.response.headers['Content-Type'] = 'application/json'
    self.response.out.write(respJSON)


class Remove(webapp2.RequestHandler):
  def post(self):
    linkKey = self.request.get('id')

    link = Link.get(linkKey)
    if link:
        link.delete()

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write('{"ok" : true}')
    else:
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write('{"ok" : false}')

app = webapp2.WSGIApplication([('/list/', List), ('/add/', Add), ('/remove/', Remove)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
