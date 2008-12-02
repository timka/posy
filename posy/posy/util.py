import re
import simplejson 

DATE_PATTERN = re.compile('new\s+Date\((".+?")\)')

def loadjson(source):
    source = DATE_PATTERN.sub(r'\1', source)
    data = simplejson.loads(source)
    return data
