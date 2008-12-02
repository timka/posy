import sys
import httplib
import urllib
import urllib2
from base64 import encodestring as b64str

from posy.util import loadjson
from posy.api import PosyError

class TwitterError(PosyError):
    pass

class Twitter(object):
    baseurl = 'https://twitter.com/'
    display_name = 'Twitter'

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def update(self, content, **kw):
        # Remove linebreak
        auth = b64str(':'.join([self.username, self.password])).rstrip()
        request = urllib2.Request(self.baseurl + 'statuses/update.json')
        request.add_header('Authorization', 'Basic %s' % auth)
        data = urllib.urlencode(dict(status=content))
        try:
            response = urllib2.urlopen(request, data)
        except (urllib2.HTTPError, httplib.HTTPException, urllib2.URLError), e:
            raise TwitterError(e)
        data = loadjson(response.read())
        return data


def main():
    username = 'timka_org'
    password = 'secret'
    tw = Twitter(username, password)
    tw.update(sys.argv[1])


if __name__ == '__main__':
    main()
