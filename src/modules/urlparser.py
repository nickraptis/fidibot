# Author: George Lemanis <georlema@gmail.com>
import re
from urllib2 import urlopen
from urllib2 import URLError
from urllib2 import HTTPError
from basemodule import BaseModule, BaseContext


class UrlParserContext(BaseContext):
    
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
        urls = self.parse_url(self.input)
        if urls:
            for url in urls:
                self.send(self.channel, "%s - %s", url, self.find_url_title(url))
        return True
    
    def do_private(self):
        urls = self.parse_url(self.input)
        if urls:
            for url in urls:
                self.send(self.nick, "%s - %s", url, self.find_url_title(url))
        return True


class UrlParserModule(BaseModule):
    context_class = UrlParserContext


module = UrlParserModule
