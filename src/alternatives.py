# Author: Nick Raptis <airscorp@gmail.com>
"""
Random alternatives to format strings

The way this is implemented mimics the way translations
work in other frameworks. What we are doing different is
returning a random string alternative instead of a localized one.

To use, import _ from this module and then wrap your string
as such 'Welcome %s' --> _('Welcome %s')
"""

import random
from os.path import dirname, join
from os import walk
import json

import logging
log = logging.getLogger(__name__)


alternatives_dict = {
    'Welcome %s': [
        'Welcome %s',
        'Hello %s',
        'How YA doing %s',
    ]
}

class Alternatives(dict):

    def random_alternative(self, fmt_string):
        """Return a random alternative"""
        # Find alternatives
        try:
            alts = self[fmt_string]
        except KeyError:
            # There are no alternatives for this string
            return fmt_string
        return random.choice(alts)

    def merge_with(self, other_dict):
        for key, lst in other_dict.iteritems():
            if not self.get(key):
                self[key] = lst
            else:
                new = self[key] + lst
                self[key] = new

    def clean_duplicates(self):
        for key, lst in self.iteritems():
            # Delete empty lists
            if not lst:
                self.pop(key, None)
            s = set()
            self[key] = [x for x in lst if x not in s and not s.add(x)]


def read_files():
    """Scan the alternatives directory and return dict"""
    alts = Alternatives()
    alt_dir = join(dirname(__file__), "alternatives")
    fmt_str = "Retrieving alternative strings from file %s"
    for dirpath, dirnames, filenames in walk(alt_dir, followlinks=True):
        for filename in filenames:
            if filename.lower().endswith(".json"):
                log.info(fmt_str, filename)
                with open(join(dirpath, filename)) as fp:
                    alts.merge_with(json.load(fp))
    return alts



# Make an instance to be imported and used globally to add to
alternatives = Alternatives(alternatives_dict)

# Import and use this as a shortcut
_ = alternatives.random_alternative



# Test translations #
#####################
if __name__ == '__main__':
    print alternatives
    for i in xrange(4):
        print _('Welcome %s') % i
    other_alts = {'Test %s': ['Test %s', 'test %s',]}
    alternatives.update(other_alts)
    print alternatives
    for i in xrange(4):
        print _('Test %s') % i
    for i in xrange(4):
        print _('Welcome %s') % i
    merge_alts = {'Test %s': ['Test %s', 'test %s', 'TEST %s', 'tEST %s']}
    alternatives.merge_with(merge_alts)
    print alternatives
    alternatives.clean_duplicates()
    print alternatives
    for i in xrange(4):
        print _('Test %s') % i
    read_files()
