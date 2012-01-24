import logging

from google.appengine.ext import db
from google.appengine.api import memcache


class Link(db.Model):
    url = db.LinkProperty()
    user = db.UserProperty()
    dateInsert = db.DateTimeProperty(auto_now_add=True)


def dbLinkToStoredObject(link):
    return {'url' : link.url, 'id': str(link.key()), 'dateInsert' : link.dateInsert}


def get_memcache_key(user):
    return 'user_list_' + user.user_id()


def getLinks(user):
    assert user is not None, 'User is none!'

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


def addLinkForUser(user, url):
    assert user is not None, 'User is none!'
    assert url is not None, 'url is none!'

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

    return link

def delLinkForUser(user, linkKey):
    assert user is not None, 'User is none!'
    assert linkKey is not None, 'linkKey is none!'

    link = Link.get(linkKey)
    if link:
        link.delete()

        # Try to update the memcache
        memcache_key = get_memcache_key(user)
        urls = memcache.get(memcache_key)
        if urls is not None:
            urls = [link for link in urls if link['id'] != linkKey] # Remove the link from the array
            if not memcache.replace(memcache_key, urls, 360):
                logging.error('Memcache set failed!')
                memcache.delete(memcache_key)

        return True
    else:
        return False
