# Author: George Lemanis <georlema@gmail.com>
"""
Module for parsing URLs in chat or on demand
"""

import re
import requests
from googl import Googl
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
        headers = {'User-Agent': 'Wget/1.13.4 (linux-gnu)'}
        if url.find("://") == -1:
            url = "http://" + url
        try:
            # a HEAD first to thwart attacks
            requests.head(url, headers=headers, timeout=5)
            # now the actual request
            resp = requests.get(url, headers=headers)
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
            start = cmphtml.find("<title")
            end = cmphtml.find("</title>")
            if start == -1 or end == -1:
                return resp.url, "Could not find page title!"
            else:
                html = html[start+7:end]
                html = html[html.find('>')+1:]
                return resp.url, html.strip()

    def shorten(self, long_url):
        goog = Googl()
        resp = goog.shorten(long_url)
        if resp.get('error'):
            error = resp['error']['message']
            self.logger.warning("Failed to shorten %s - %s", long_url, error)
            return long_url
        short_url = resp['id']
        return short_url

    def do_public(self):
        """
        Try to find URLs in every line and send back
        short url andtheir title
        """
        if super(UrlParserContext, self).do_public():
            return True
        urls = self.parse_urls(self.input)
        return self._do_urls(urls)

    def cmd_title(self, argument):
        """Shorten url(s) and return page title(s)."""
        if not argument:
            self.send(self.target, "No url in argument")
        urls = argument.split()
        return self._do_urls(urls)

    def cmd_url(self, argument):
        """Shorten url(s) and return page title(s)."""
        self.cmd_title(argument)

    def _do_urls(self, urls):
        if urls:
            for url in urls:
                final_url, title = self.find_url_title(url)
                short_url = self.shorten(final_url)
                self.send(self.target, "%s - %s", short_url, title)
            return True
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
