# Author: George Lemanis <georlema@gmail.com>
import re
import requests
from requests.exceptions import RequestException
from basemodule import BaseModule, BaseCommandContext


class UrlParserContext(BaseCommandContext):
    
    def parse_url(self, txt):
        result = re.findall(r'www\S+|https?\S+', txt)
        return result
    
    def find_url_title(self, url):
        if url.find("://") == -1:
            url = "http://"+url 
        try:
            resp = requests.get(url)
            html = resp.text
        except RequestException as e:
            return url, e.__doc__
        except ValueError as e:
            return url, "Failed to parse url"
        else:
            resp.close()
            cmphtml = html.lower()
            start = cmphtml.find("<title>")
            end = cmphtml.find("</title>")
            if start == -1 or end == -1:
                return "Could not find page title!"
            else:
                html = html[start+7:end]
                return resp.url, html.strip()

    def do_public(self):
        if super(UrlParserContext, self).do_public():
            return True
        urls = self.parse_url(self.input)
        if urls:
            for url in urls:
                final_url, title = self.find_url_title(url)
                self.send(self.channel, "%s - %s", final_url, title)
        return True

    def cmd_title(self, argument):
        """Parse argument for urls and return page title."""
        urls = self.parse_url(argument)
        target = self.channel if self.channel.startswith("#") else self.nick
        if urls:
            for url in urls:
                final_url, title = self.find_url_title(url)
                self.send(target, "%s - %s", final_url, title)
        else:
                self.send(target, "No url in argument")
        return True


class UrlParserModule(BaseModule):
    context_class = UrlParserContext


module = UrlParserModule
