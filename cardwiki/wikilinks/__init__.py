'''
WikiLinks Extension for Python-Markdown
======================================
Converts [[WikiLinks]] to relative links.
See <https://pythonhosted.org/Markdown/extensions/wikilinks.html> 
for documentation.
Original code Copyright [Waylan Limberg](http://achinghead.com/).
All changes Copyright The Python Markdown Project
License: [BSD](http://www.opensource.org/licenses/bsd-license.php) 
'''

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree
import re

def build_url(label, base, end):
    """ Build a url from the label, a base, and an end. """
    clean_label = re.sub(r'([ ]+_)|(_[ ]+)|([ ]+)', '_', label)
    return '%s%s%s'% (base, clean_label, end)


class WikiLinkExtension(Extension):

    def __init__ (self, *args, **kwargs):
        self.config = {
            'base_url' : ['/', 'String to append to beginning or URL.'],
            'end_url' : ['', 'String to append to end of URL.'],
            'html_class' : ['wikilink', 'CSS hook. Leave blank for none.'],
            'build_url' : [build_url, 'Callable formats URL from label.'],
            'card_link' : ['', 'link for the wiki card this link belongs to']
        }
        
        super(WikiLinkExtension, self).__init__(*args, **kwargs)
    
    def extendMarkdown(self, md, md_globals):
        self.md = md
    
        # append to end of inline patterns
        #WIKILINK_RE = r'\[\[([\w0-9|_ -]+)\]\]'
        WIKILINK_RE = r'\[\[(.*?)\]\]'
        wikilinkPattern = WikiLinks(WIKILINK_RE, self.getConfigs())
        wikilinkPattern.md = md
        md.inlinePatterns.add('wikilink', wikilinkPattern, "<not_strong")


class WikiLinks(Pattern):
    def __init__(self, pattern, config):
        super(WikiLinks, self).__init__(pattern)
        self.config = config
  
    def handleMatch(self, m):
        if m.group(2).strip():
            print("%%%%%%%%%%%%%%%%%")
            print(self._getMeta())
            base_url, end_url, html_class, card_link = self._getMeta()
            wl = m.group(2).strip()
            wl_pair = wl.split("|", 1)
            print(wl_pair)
            if len(wl_pair) == 2:
                #matches things like [[description | http://www.website.com]]
                #display = re.sub(r'\|', '', wl_pair[1].strip())
                label = wl_pair[0].strip()
                url = wl_pair[1].strip()
                #url = self.config['build_url'](label, base_url, end_url)
                a = self._getExternalLink(label, url)
            elif len(wl_pair) == 1:
                label = wl_pair[0].strip()
                display = label
                url = self.config['build_url'](label, base_url, end_url)
                label = re.sub(r'([ ]+)', '%20', label)
                a = self._getInternalLink(display, label, url)
            else:
                label = m.group(2).strip()
                display = label
                url = self.config['build_url'](label, base_url, end_url)
                label = re.sub(r'([ ]+)', '%20', label)
                a = self._getInternalLink(display, label, url)
        else:
            a = ''
        return a
    
    def _getInternalLink(self, display, label, url):
        base_url, end_url, html_class, card_link = self._getMeta()
        a = etree.Element('a')
        a.text = display
        a.set('href', '#card_' + label)
        a.set('onClick', "appendCard(\""+card_link+"\", \""+url+"\")") 
        if html_class:
                a.set('class', html_class)
        return a
    
    def _getExternalLink(self, display, url):
        base_url, end_url, html_class, card_link = self._getMeta()
        a = etree.Element('a')
        a.text = display
        a.set('href', url)
        #if html_class:
        #        a.set('class', html_class)
        a.set('class', "externalLink")
        return a
    
    def _getMeta(self):
        """ Return meta data or config data. """
        base_url = self.config['base_url']
        end_url = self.config['end_url']
        html_class = self.config['html_class']
        card_link = self.config['card_link']
        if hasattr(self.md, 'Meta'):
            if 'wiki_base_url' in self.md.Meta:
                base_url = self.md.Meta['wiki_base_url'][0]
            if 'wiki_end_url' in self.md.Meta:
                end_url = self.md.Meta['wiki_end_url'][0]
            if 'wiki_html_class' in self.md.Meta:
                html_class = self.md.Meta['wiki_html_class'][0]
        return base_url, end_url, html_class, card_link
    

def makeExtension(*args, **kwargs) :
    return WikiLinkExtension(*args, **kwargs)