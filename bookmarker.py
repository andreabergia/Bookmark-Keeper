import webapp2
import json
import logging

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

class Link(db.Model):
    url = db.LinkProperty()
    user = db.UserProperty()


def get_memcache_key(user):
    return 'user_list_' + user.user_id()


class List(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'application/json'

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
                urls.append({"url" : link.url, "id" : str(link.key())})
            if not memcache.add(get_memcache_key(user), urls, 360):
                logging.error('Memcache set failed!')

        respJSON = json.dumps(urls)
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
            urls.append({"url" : link.url, "id" : str(link.key())})
            if not memcache.replace(memcache_key, urls, 360):
                logging.error('Memcache set failed!')
                memcache.delete(memcache_key)

        respJSON = json.dumps( {'ok': True, 'id': str(link.key())} )
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

app = webapp2.WSGIApplication([('/list/', List), ('/add/', Add), ('/remove/', Remove)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
