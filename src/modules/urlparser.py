# Author: George Lemanis <georlema@gmail.com>
import re
from urllib2 import urlopen
from urllib2 import URLError
from urllib2 import HTTPError
from basemodule import BaseModule, BaseCommandContext


class UrlParserContext(BaseCommandContext):
    
    def parse_url(self, txt):
        result = re.findall(r'www\S+|https?\S+', txt)
        return result
    
    def find_url_title(self, url):
        if url.find("://") == -1:
            url = "http://"+url 
        try:
            sock = urlopen(url)
            html = sock.read()
        except HTTPError, e:
            return e.code
        except URLError, e:
            return e.args
        else:
            sock.close()
            cmphtml = html.lower()
            start = cmphtml.find("<title>")
            end = cmphtml.find("</title>")
            if start == -1 or end == -1:
                return "Could not find page title!"
            else:
                html = html[start+7:end]
                return html.strip()

    def do_public(self):
        if super(UrlParserContext, self).do_public():
            return True
        urls = self.parse_url(self.input)
        if urls:
            for url in urls:
                self.send(self.channel, "%s - %s", url, self.find_url_title(url))
        return True

    def cmd_title(self, argument):
        """Parse argument for urls and return page title."""
        urls = self.parse_url(argument)
        target = self.channel if self.channel.startswith("#") else self.nick
        if urls:
            for url in urls:
                self.send(target, "%s - %s", url, self.find_url_title(url))
        else:
                self.send(target, "No url in argument")
        return True


class UrlParserModule(BaseModule):
    context_class = UrlParserContext


module = UrlParserModule
