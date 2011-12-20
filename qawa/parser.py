import re
from vumi.utils import normalize_msisdn

class QawaParserException(Exception): pass
class SyntaxError(QawaParserException): pass

class QawaParser(object):
    """
    A simple class to parse incoming text messages
    and return a type and parsed payload
    """

    # add to default group
    MSISDN = r'\+?\d+'
    NAME = r'[a-zA-Z_\-\s]*'
    GROUP_NAME = r'#?%s' % (NAME,)
    ADD_TO_DEFAULT_GROUP = r'^(?P<group>%s)\+(?P<msisdn>%s)+\s?(?P<name>%s)$' % (GROUP_NAME, MSISDN, NAME)

    def __init__(self):
        self.valid_patterns = [
            ('add', self.ADD_TO_DEFAULT_GROUP),
        ]

    def parse(self, text):
        for ptype, pattern in self.valid_patterns:
            match = re.match(pattern, text.strip())
            if match:
                handler = getattr(self, 'handle_%s' % ptype, self.noop)
                return handler(ptype, **match.groupdict())
        raise SyntaxError('Unable to parse %s' % (text,))

    def handle_add(self, ptype, group, msisdn, name):
        return (ptype, {
            'group': group or None,
            'msisdn': normalize_msisdn(msisdn, country_code='27'),
            'name': name or None,
        })

    def noop(self, ptype, **kwargs):
        raise QawaParserException('handle_%s(%s) not implemented' % (ptype, kwargs))
