import sys
import datetime
import xmlrpclib
import md5

import posy.api

class LJError(posy.api.PosyError):
    pass


def md5hex(data):
    return md5.md5(data).hexdigest()


class LJServer(object):
    def __init__(self, *args, **kw):
        self.proxy = xmlrpclib.ServerProxy(*args, **kw)

    def __getattr__(self, name):
        method = getattr(self.proxy.LJ.XMLRPC, name)
        def wrapper(**kw):
            return method(kw)
        wrapper.func_name = name

        return wrapper


class LJ(object):
    baseurl = 'https://www.livejournal.com/interface/xmlrpc'
    display_name = 'LiveJournal'

    def __init__(self, username, password):
        self.lj = LJServer(self.baseurl, verbose=True)
        self.username = username
        self.password = password

    def make_common_args(self):
        response = self.lj.getchallenge()
        challenge = response['challenge']
        auth_response = md5hex(challenge + md5hex(self.password))
        return dict(username=self.username, ver=1, auth_method='challenge',
                auth_challenge=challenge, auth_response=auth_response)

    def update(self, content, **kw):
#        when = kw.pop('datetime', datetime.datetime.now())
        when = kw.pop('datetime')
        args = dict(kw)
        try:
            args.update(self.make_common_args())
            args.update(year=when.year, mon=when.month, day=when.day, min=when.minute,
                    hour=when.hour)
            response = self.lj.postevent(event=content, **args)
        except xmlrpclib.Error, e:
            raise LJError(e)


def main():
    username = 'liago0sh'
    password = 'secret'
    content = 'Playing with LJ XMLRPC interface'
    lj = LJ(username, password)
    lj.update(content=sys.argv[1])


if __name__ == '__main__':
    main()
