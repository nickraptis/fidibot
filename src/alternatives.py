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
    merge_alts = {'Test %s': ['TEST %s', 'tEST %s']}
    alternatives.merge_with(merge_alts)
    print alternatives
    for i in xrange(4):
        print _('Test %s') % i
