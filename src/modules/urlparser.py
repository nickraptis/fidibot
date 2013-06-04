# Author: George Lemanis <georlema@gmail.com>
"""
Module for parsing URLs in chat or on demand
"""

import re
import requests
from basemodule import BaseModule, BaseCommandContext

regex = re.compile("""
                   ^(                # Starts with
                    https?://|       # http:// or https:// or
                    www\.            # www.
                   )\S+$             # more characters until the end
                   """, re.IGNORECASE | re.VERBOSE)

def is_url(token):
    """Return true if the input is a URL"""
    return regex.match(token)


class UrlParserContext(BaseCommandContext):

    def parse_urls(self, txt):
        """Return a list of all urls in line of text"""
        urls = [w for w in txt.split() if is_url(w)]
        return urls

    def find_url_title(self, url):
        """Retrieve the title of a given URL"""
        if url.find("://") == -1:
            url = "http://" + url
        try:
            resp = requests.get(url)
            html = resp.text
        except requests.RequestException as e:
            self.logger.warning(e)
            return url, e.__doc__
        except ValueError as e:
            self.logger.warning(e)
            return url, "Failed to parse url"
        else:
            resp.close()
            cmphtml = html.lower()
            start = cmphtml.find("<title>")
            end = cmphtml.find("</title>")
            if start == -1 or end == -1:
                return resp.url, "Could not find page title!"
            else:
                html = html[start+7:end]
                return resp.url, html.strip()

    def do_public(self):
        """Try to find URLs in every line and send back their title"""
        if super(UrlParserContext, self).do_public():
            return True
        urls = self.parse_urls(self.input)
        if urls:
            for url in urls:
                final_url, title = self.find_url_title(url)
                self.send(self.channel, "%s - %s", final_url, title)
            return True
        return False

    def cmd_title(self, argument):
        """Treat the argument as urls and return page title."""
        urls = argument.split()
        target = self.channel if self.channel.startswith("#") else self.nick
        if urls:
            for url in urls:
                final_url, title = self.find_url_title(url)
                self.send(target, "%s - %s", final_url, title)
            return True
        else:
            self.send(target, "No url in argument")
        return False


class UrlParserModule(BaseModule):
    context_class = UrlParserContext

module = UrlParserModule


# testing the regex #
#####################
should_be_urls = ('http://google.com', 'www.google.com',)
should_not_be = ('asdadadasda',)

def test_regex():
    for i in should_be_urls:
        if is_url(i):
            print "PASS: %s worked" % i
        else:
            print "FAIL: %s should have worked" % i
    for i in should_not_be:
        if not is_url(i):
            print "PASS: %s failed as expected" % i
        else:
            print "FAIL: %s should have failed" % i

if __name__ == '__main__':
    test_regex()
