import httplib
import sys
import urllib
import urllib2
import cookielib
import datetime
import re
import logging

from posy.util import loadjson
from posy.api import PosyError

GLOBAL_PATTERN = re.compile('(?m)var\s+GLOBAL\s*=\s*(\{.+\})')
log = logging.getLogger(__name__)

class PlurkError(PosyError):
    pass


class Plurk(object):
    baseurl = 'http://www.plurk.com/'
    display_name = 'Plurk'

    def __init__(self, username, password):
        self.username = username
        self.password = password
        handler = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        self.opener = urllib2.build_opener(handler)

    def update(self, content, **kw):
        when = kw.pop('datetime')
        lang = kw.pop('lang', 'en')
        no_comments = kw.pop('no_comments', 0)
        qualifier = kw.pop('qualifier', ':')

        # Get auth cookie
        data = urllib.urlencode(dict(nick_name=self.username,
            password=self.password))
        request = urllib2.Request(self.baseurl + 'Users/login', data)

        try:
            response = self.opener.open(request)
        except (urllib2.HTTPError, httplib.HTTPException, urllib2.URLError), e:
            raise PlurkError(e)

        data = response.read()
        #log.debug('response data: %s', data)

        m = GLOBAL_PATTERN.search(data)
        error = PlurkError('Error in server response. No uid found.')
        if m is None:
            raise error

        data = loadjson(m.group(1))
        if not data:
            raise error 

        error = PlurkError('Login failed.')
        session_user = data.get('session_user')
        if session_user is None:
            raise error

        uid = session_user.get('uid')
        if uid is None:
            raise error

        data = urllib.urlencode(dict(content=content,
            lang=lang,
            no_comments=no_comments,
            uid=uid,
            qualifier=qualifier,
            posted=when.strftime('%FT%T')))
        request = urllib2.Request(self.baseurl + 'TimeLine/addPlurk', data)

        try:
            response = self.opener.open(request)
        except (urllib2.HTTPError, httplib.HTTPException, urllib2.URLError), e:
            raise PlurkError(e)

        data = loadjson(response.read())
        if data['error']:
            raise PlurkError(data['error'])
        return data

def main():
    username = 'timka_org'
    password = 'secret'
    plurk = Plurk(username, password)
    plurk.update(sys.argv[1])


if __name__ == '__main__':
    main()
