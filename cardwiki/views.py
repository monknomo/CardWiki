from bottle import get, post, put, delete, run, template, request, static_file
import cardwiki.db as db
from sqlalchemy import func, exists, distinct, and_
import json
import datetime
import markdown
from cardwiki.wikilinks import WikiLinkExtension
import re

base_url = "/"

@get('{0}'.format(base_url))
def get_index():
    return static_file('index.html', root='.')
    
@get('{0}static/<filename:path>'.format(base_url))
def get_static(filename):
    return static_file(filename, root='./static')

@get('{0}cards'.format(base_url))
def get_all_cards():
    session = db.Session()
    result = []    
    max_v_by_title = session.query(db.Card, 
                                    func.max(db.Card.version).\
                                    label('max_version')).\
                                group_by(db.Card.title).\
                                subquery()
    for card in session.query(max_v_by_title).\
        filter(and_(db.Card.version == max_v_by_title.c.max_version, 
                        db.Card.title == max_v_by_title.c.title)).all():
        result.append({'title':card.title, 
                        'linkable_title':card.linkable_title,
                        'current_version':card.max_version})
    return {"cards":result}
    
@get('{0}cards/<linkable_title>'.format(base_url))
@get('{0}cards/<linkable_title>/'.format(base_url))
def get_card(linkable_title):
    session = db.Session()
    card_exists = exists().where(db.Card.linkable_title == linkable_title)
    if session.query(db.Card).filter(card_exists).count() > 0:
        newest_card = session.query(db.Card).filter(db.Card.linkable_title == linkable_title).order_by(db.Card.version.desc()).first()
        """
        wikilinks = []
        for wikilink in newest_card.wikilinks:
            wikilink_dict = wikilink.to_dict();
            wikilink_dict['href'] = '{0}cards/{1}'.format(base_url, 
                                                            wikilink.to_card.replace(" ", "_"))
            wikilinks.append(wikilink_dict)
        
        tags = []
        for tag in newest_card.tags:
            tag_dict = tag.to_dict()
            tag_dict['href'] = '{0}tags/{1}'.format(base_url, tag.tag.replace(" ", "_"))
            tags.append(tag_dict)
        """
        card = {'linkable_title':linkable_title, 
                'title':newest_card.title,
                'content':newest_card.content, 
                'rendered_content': newest_card.rendered_content,
                'edited_at':newest_card.edited_at.isoformat(), 
                'edited_by':newest_card.edited_by,
                'version':newest_card.version,
                'wikilinks':'cards/{0}/wikilinks'.format(linkable_title),
                'tags':'cards/{0}/tags'.format(linkable_title),}
    else:
        card = {'linkable_title':linkable_title, 
                'title':linkable_title.replace("_"," "),
                'content':None, 
                'rendered_content':None,
                'edited_at':None, 
                'edited_by':None,
                'version':0}
    print(card)
    return card

@get('{0}cards/<title>/wikilinks'.format(base_url))
def get_card_links(title):
    session = db.Session()
    card_exists = exists().where(db.Card.title == title)
    if session.query(db.Card).filter(card_exists).count() > 0:
        newest_card = session.query(db.Card).filter(db.Card.title == title).order_by(db.Card.version.desc()).first()
        wikilinks = []
        for wikilink in newest_card.wikilinks:
            wikilink_dict = wikilink.to_dict();
            wikilink_dict['href'] = '{0}cards/{1}'.format(base_url, 
                                                            wikilink.to_card.replace(" ", "_"))
            wikilinks.append(wikilink_dict)
    return {'card': 'cards/{0}/'.format(title),
            'wikilinks': wikilinks}
    
@get('{0}cards/<title>/<version:int>'.format(base_url))
def get_card(title,version):
    session = db.Session()
    card_exists = exists().where(db.Card.title == title)
    if session.query(db.Card).filter(card_exists).count() > 0:
        newest_card = session.query(db.Card).filter(and_(db.Card.title == title, db.Card.version == version)).order_by(db.Card.version.desc()).first()
        wikilinks = []
        for wikilink in newest_card.wikilinks:
            wikilink_dict = wikilink.to_dict();
            wikilink_dict['href'] = '{0}cards/{1}'.format(base_url, 
                                                            wikilink.to_card.replace(" ", "_"))
            wikilinks.append(wikilink_dict)
        card = {'title':title, 
                'content':newest_card.content, 
                'rendered_content': newest_card.rendered_content,
                'edited_at':newest_card.edited_at.isoformat(), 
                'edited_by':newest_card.edited_by,
                'version':newest_card.version,
                'wikilinks':wikilinks}
        
    else:
        card = {'title':title, 
                'content':None, 
                'rendered_content':None,
                'edited_at':None, 
                'edited_by':None,
                'version':0}
    print(card)
    return card

def derive_title_link(title):
    title = re.sub(r'[\ ]', '_', title)
    title = re.sub(r'[^a-zA-Z0-9_~\-\.]', '', title)
    return title
    
@put('{0}cards/<linkable_title>'.format(base_url))
def create_card(linkable_title):
    session = db.Session()
    if session.query(db.Card).filter(db.Card.linkable_title==linkable_title).count() > 0:
        newest_card = session.query(db.Card).filter(db.Card.linkable_title == linkable_title).order_by(db.Card.version.desc()).first()
        max_version = newest_card.version
       
        if newest_card.content != request.json['content']:      
            new_card = db.Card(linkable_title=linkable_title, 
                                    title=request.json['title'].strip(),
                                    version=max_version + 1, 
                                    content=request.json['content'], 
                                    rendered_content = markdown.markdown(request.json['content'], extensions=[WikiLinkExtension(base_url='/cards/')]),
                                    edited_at=datetime.datetime.utcnow(), 
                                    edited_by=None)
            session.add(new_card)
            wikilinks = re.finditer('\[\[([\w0-9_ -]+)\]\]', request.json['content'])
            for link in wikilinks:
                wikilink = db.CardWikiLink(from_card = new_card.linkable_title,
                                            to_card = link.group(0)[2:-2],
                                            from_card_version = new_card.version)
                session.add(wikilink)
            session.commit()
            
        else:
            new_card = None;
    else:  
        new_card = db.Card(linkable_title=linkable_title, 
                            title=request.json['title'],
                            version=1, 
                            content=request.json['content'], 
                            rendered_content = markdown.markdown(request.json['content'], ['wikilinks(base_url={0}cards/)'.format(base_url)]),
                            edited_at=datetime.datetime.utcnow(), 
                            edited_by=None)
        session.add(new_card)
        session.commit()
    if new_card is None:
        return newest_card.to_dict()
    else:
        return new_card.to_dict()
    
@get('{0}cards/<linkable_title>/tags'.format(base_url))
def get_card_tags(linkable_title):
    session = db.Session()
    query = session.query(db.CardTag).filter(db.CardTag.tagged_card == linkable_title)
    results = {"tags":[]}
    for tag in query:
        results["tags"].append({"tag":tag.tag, 
                                "href":"{0}tags/{1}".format(base_url, 
                                                            tag.tag)})
    return results
    
@put('{0}cards/<linkable_title>/tags'.format(base_url))
@put('{0}cards/<linkable_title>/tags/'.format(base_url))
def create_card_tags(linkable_title):
    session = db.Session()
    print(request.json['tags'])
    for tag in request.json['tags']:
        print(tag)
        split_tags = re.split("[:,;+\.| ]", tag["tag"])
        print(split_tags)
        for split_tag in split_tags:
            if split_tag.strip() != "":
                if session.query(db.CardTag).filter(db.CardTag.tagged_card == tag["tagged_card"], db.CardTag.tag == split_tag).count() == 0:
                    print("inserting tag")
                    session.add(db.CardTag(tagged_card = tag["tagged_card"], tag = split_tag))
    session.commit()    
    return get_card_tags(linkable_title)
    
@delete('{0}cards/<linkable_title>/tags/<tag>'.format(base_url))
@delete('{0}cards/<linkable_title>/tags/<tag>/'.format(base_url))
def create_card_tags(linkable_title, tag):
    session = db.Session()
    db_tag = session.query(db.CardTag).filter(db.CardTag.tagged_card == linkable_title, db.CardTag.tag == tag).first()
    session.delete(db_tag)
    session.commit()

@get('{0}tags'.format(base_url))
def get_all_tags():
    session = db.Session()
    q = session.query(db.CardTag.tag, func.count(db.CardTag.tag)).group_by(db.CardTag.tag).all()
    result = {"tags":[]}
    for tag in q:
        result["tags"].append({"tag":tag[0], "count":tag[1], "href":'{0}tags/{1}'.format(base_url, tag[0].replace(" ", "_"))})
    return result
    
@get('{0}tags/<tag>'.format(base_url))
def get_cards_for_tag(tag):
    session = db.Session()
    tags = session.query(db.CardTag.tagged_card).filter(db.CardTag.tag == tag)
    cards = session.query(db.Card).filter(db.Card.linkable_title.in_(tags))
    cards = cards.group_by(db.Card.linkable_title)
    cards = cards.having(func.max(db.Card.version))
    result = {"cards":[]}
    print(cards)
    for card in cards:
        card_dict = card.to_dict()
        card_dict['href'] = '{0}cards/{1}'.format(base_url, card_dict['linkable_title'])
        card_dict['wikilinks'] = '{0}cards/{1}/wikilinks'.format(base_url, card_dict['linkable_title'])
        result["cards"].append(card_dict)
    return result
    
