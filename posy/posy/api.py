import pkg_resources
import logging

__all__ = ['Posy', 'PosyError', 'retrieve_services']

log = logging.getLogger(__name__)

class PosyError(Exception):
    pass


def retrieve_services(name=None):
    return [ (ep.name, ep.load())
       for ep in pkg_resources.iter_entry_points('posy.services', name) ]


class Posy(object):
    def __init__(self):
        self.services = retrieve_services() 
        self.services.sort()

    def update(self, content, **kw):
        for name, service in self.services:
            try:
                service.update(content, **kw)
            except PosyError, e:
                log.error('Posy.update: error: %s', e)

    def __getitem__(self, name):
        return dict(self.services)[name]

    def __contains__(self, name):
        return name in dict(self.services)

    def __iter__(self):
        return iter(self.services)


def main():
    logging.basicConfig(level=logging.DEBUG)
    posy = Posy()


if __name__ == '__main__':
    main()
