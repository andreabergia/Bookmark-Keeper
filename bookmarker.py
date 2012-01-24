import webapp2
import json
import logging
import datetime
import os

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext.webapp import template


class Link(db.Model):
    url = db.LinkProperty()
    user = db.UserProperty()
    dateInsert = db.DateTimeProperty(auto_now_add=True)


def dbLinkToStoredObject(link):
    return {"url" : link.url, "id": str(link.key()), "dateInsert" : link.dateInsert}


def get_memcache_key(user):
    return 'user_list_' + user.user_id()


def toJson(object):
    class JsonEncoder(json.JSONEncoder):
        monthNames = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

        def default(self, obj):
            if isinstance(obj, datetime.datetime):
                # TODO: need to handle timezones here!!
                return "%d:%d - %d %s %d" % (obj.hour, obj.minute, obj.day, self.monthNames[obj.month], obj.year)
            return json.JSONEncoder.default(self, obj)
    return json.dumps(object, cls=JsonEncoder)


class List(webapp2.RequestHandler):
    def getLinks(self):
        user = users.get_current_user()
        assert user is not None, 'no current user!'

        # Try to hit the memcache
        urls = memcache.get(get_memcache_key(user))
        if urls is None:
            # No such luck... We'll need to go to the data store
            urls = []
            links = db.GqlQuery('SELECT * '
                                'FROM Link '
                                'WHERE user = :1',
                                user)
            for link in links:
                urls.append(dbLinkToStoredObject(link))
            if not memcache.add(get_memcache_key(user), urls, 360):
                logging.error('Memcache set failed!')

        return urls

    def get(self):
        urls = self.getLinks()

        self.response.headers['Content-Type'] = 'application/json'
        respJSON = toJson(urls)
        self.response.out.write(respJSON)


class Add(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        assert user is not None, 'no current user!'

        url = self.request.get('url')

        link = Link()
        link.url = db.Link(url)
        link.user = user
        link.put()

        # Try to update the memcache
        memcache_key = get_memcache_key(user)
        urls = memcache.get(memcache_key)
        if urls is not None:
            urls.append(dbLinkToStoredObject(link))
            if not memcache.replace(memcache_key, urls, 360):
                logging.error('Memcache set failed!')
                memcache.delete(memcache_key)

        respJSON = toJson( {'ok': True, 'id': str(link.key())} )
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(respJSON)


class Remove(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        assert user is not None, 'no current user!'

        linkKey = self.request.get('id')

        link = Link.get(linkKey)
        if link:
            link.delete()

            # Try to update the memcache
            memcache_key = get_memcache_key(user)
            urls = memcache.get(memcache_key)
            if urls is not None:
                urls = [link for link in urls if link['id'] != linkKey]
                if not memcache.replace(memcache_key, urls, 360):
                    logging.error('Memcache set failed!')
                    memcache.delete(memcache_key)

            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write('{"ok" : true}')
        else:
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write('{"ok" : false}')

class Links(webapp2.RequestHandler):
    def get(self):
        l = List()
        urls = l.getLinks()

        template_values = {'urls' : urls}

        path = os.path.join(os.path.join(os.path.dirname(__file__), 'static'), 'list.html')
        self.response.out.write(template.render(path, template_values))


app = webapp2.WSGIApplication([
    ('/list/', List),
    ('/add/', Add),
    ('/remove/', Remove),
    ('/links/', Links),
    ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
