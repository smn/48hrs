import re
from vumi.utils import normalize_msisdn

class QawaParserException(Exception): pass
class SyntaxError(QawaParserException): pass

def normalize(string):
    return normalize_msisdn(string, country_code='27')

class QawaParser(object):
    """
    A simple class to parse incoming text messages
    and return a type and parsed payload
    """

    # add to default group
    MSISDN = r'\+?\d{10,12}'
    NAME = r'[a-zA-Z_\-]'
    QUERY = r'^\?(?P<name>%s+)' % (NAME,)
    ADD_TO_GROUP = r'^#?(?P<group>%s*)\s?\+(?P<msisdn>%s)\s?(?P<name>%s*)$' % (NAME, MSISDN, NAME)
    REMOVE_FROM_GROUP = r'^#?(?P<group>%s*)\s?\-(?P<msisdn>%s)$' % (NAME, MSISDN)

    def __init__(self):
        # Unfortunately order is important
        self.valid_patterns = [
            ('query', re.compile(self.QUERY)),
            ('remove', re.compile(self.REMOVE_FROM_GROUP)),
            ('add', re.compile(self.ADD_TO_GROUP)),
        ]

    def parse(self, text):
        for ptype, pattern in self.valid_patterns:
            match = pattern.match(text.strip())
            if match:
                handler = getattr(self, 'handle_%s' % ptype, self.noop)
                return handler(ptype, **match.groupdict())
        raise SyntaxError('Unable to parse %s' % (text,))

    def find_groups(self, text):
        pattern = r'#(?P<group>%s+)' % (self.NAME,)
        return re.findall(pattern, text)

    def handle_add(self, ptype, group, msisdn, name):
        return (ptype, {
            'group': group or None,
            'msisdn': normalize(msisdn),
            'name': name or None,
        })

    def handle_remove(self, ptype, group, msisdn):
        return (ptype, {
            'group': group or None,
            'msisdn': normalize(msisdn),
        })

    def handle_query(self, ptype, name):
        return (ptype, {
            'name': name,
        })

    def noop(self, ptype, **kwargs):
        raise QawaParserException('handle_%s(%s) not implemented' % (ptype, kwargs))
