import model

import webapp2
import json
import datetime
import os
from common.templatefilters import formatDateDistance

from google.appengine.api import users
from google.appengine.ext.webapp import template


class List(webapp2.RequestHandler):
    def get(self):
        def toJson(object):
            class JsonEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, datetime.datetime):
                        return formatDateDistance(obj)
                    return json.JSONEncoder.default(self, obj)
            return json.dumps(object, cls=JsonEncoder)

        user = users.get_current_user()
        assert user is not None, 'no current user!'

        urls = model.getLinks(user)

        self.response.headers['Content-Type'] = 'application/json'
        respJSON = toJson(urls)
        self.response.out.write(respJSON)


class Add(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        assert user is not None, 'no current user!'

        link = model.addLinkForUser(user, request.get('url'))

        respJSON = toJson( {'ok': True, 'id': str(link.key())} )
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(respJSON)


class Remove(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        assert user is not None, 'no current user!'

        linkKey = self.request.get('id')
        if model.delLinkForUser(user, linkKey):
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write('{"ok" : true}')
        else:
            self.response.headers['Content-Type'] = 'application/json'
            self.response.out.write('{"ok" : false}')

class Links(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        assert user is not None, 'no current user!'

        urls = model.getLinks(user)
        template_values = {'urls' : urls}

        path = os.path.join(os.path.join(os.path.dirname(__file__), 'static'), 'list.html')
        self.response.out.write(template.render(path, template_values))


template.register_template_library('common.templatefilters')
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
