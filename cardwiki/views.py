from bottle import get, post, put, delete, run, template, request, static_file
import cardwiki.db as db
from sqlalchemy import func, exists, distinct, and_
from sqlalchemy.orm.exc import NoResultFound
import json
import datetime
import markdown
from cardwiki.wikilinks import WikiLinkExtension
import re
from passlib.hash import bcrypt

base_url = "/"

def get_cards(session):
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
    return result

def get_wikilinks(linkable_title, session):
    card_exists = exists().where(db.Card.linkable_title == linkable_title)
    if session.query(db.Card).filter(card_exists).count() > 0:
        newest_card = session.query(db.Card).filter(db.Card.linkable_title == linkable_title).order_by(db.Card.version.desc()).first()
        session.close()
        wikilinks = []
        for wikilink in newest_card.wikilinks:
            wikilink_dict = wikilink.to_dict();
            wikilink_dict['href'] = '{0}cards/{1}'.format(base_url, 
                                                            wikilink.to_card.replace(" ", "_"))
            wikilinks.append(wikilink_dict)
        return wikilinks
    else:
        return []

def derive_title_link(title):
    title = re.sub(r'[\ ]', '_', title)
    title = re.sub(r'[^a-zA-Z0-9_~\-\.]', '', title)
    return title
    
def get_newest_card(linkable_title, session):
    if session.query(db.Card).filter(db.Card.linkable_title==linkable_title).count() > 0:
        return session.query(db.Card).filter(db.Card.linkable_title == linkable_title).order_by(db.Card.version.desc()).first()
    else:
        return None
        
def insert_card(card, session):
    session.add(card)
    wikilinks = re.finditer('\[\[([\w0-9_ -]+)\]\]', request.json['content'])
    for link in wikilinks:
        wikilink = db.CardWikiLink(from_card = card.linkable_title,
                                    to_card = link.group(0)[2:-2],
                                    from_card_version = card.version)
        session.add(wikilink)
    return card

def get_tags_for_card(linkable_title, session):
    query = session.query(db.CardTag).filter(db.CardTag.tagged_card == linkable_title)
    results = {"tags":[]}
    for tag in query:
        results["tags"].append({"tag":tag.tag, 
                                "href":"{0}tags/{1}".format(base_url, 
                                                            tag.tag)})
    return results

def insert_tags(tags, session):
    for tag in tags:
        print(tag)
        split_tags = re.split("[:,;+\.| ]", tag["tag"])
        print(split_tags)
        for split_tag in split_tags:
            if split_tag.strip() != "":
                if session.query(db.CardTag).filter(db.CardTag.tagged_card == tag["tagged_card"], db.CardTag.tag == split_tag).count() == 0:
                    print("inserting tag")
                    session.add(db.CardTag(tagged_card = tag["tagged_card"], tag = split_tag))
    return tags

def find_all_tags(session):    
    q = session.query(db.CardTag.tag, func.count(db.CardTag.tag)).group_by(db.CardTag.tag).all()
    result = {"tags":[]}
    for tag in q:
        result["tags"].append({"tag":tag[0], "count":tag[1], "href":'{0}tags/{1}'.format(base_url, tag[0].replace(" ", "_"))})
    return result

def find_cards_for_tag(tag, session):
    tags = session.query(db.CardTag.tagged_card).filter(db.CardTag.tag == tag)
    cards = session.query(db.Card).filter(db.Card.linkable_title.in_(tags))
    cards = cards.group_by(db.Card.linkable_title)
    cards = cards.having(func.max(db.Card.version))
    result = {"cards":[]}
    for card in cards:
        card_dict = card.to_dict()
        card_dict['href'] = '{0}cards/{1}'.format(base_url, card_dict['linkable_title'])
        card_dict['wikilinks'] = '{0}cards/{1}/wikilinks'.format(base_url, card_dict['linkable_title'])
        result["cards"].append(card_dict)
    return result

def require_authentication(func):
    def check_auth(*args, **kwargs):
        with db.session_scope() as session:
            try:
                username = request.json['username']
            except:
                try:
                    password = request.json['password']
                except:
                    return {"authentication_status":"failed",
                            "requested_url":request.path,
                            "reason":"We need both a username and password"
                            }
                return {"authentication_status":"failed",
                        "requested_url":request.path(),
                        "reason":"We need a username to go with your password"
                        }
            password = request.json['password']            
            user = session.query(db.User).filter(db.User.username == username).one()
            if bcrypt.verify(password, user.passwordhash):
                value = func(*args, **kwargs)
                print(value)
                value['authentication_status']="success"
                print(value)
                return value
                #return func(*args, **kwargs)           
            else:
                return {"authentication_status":"failure",
                        "requested_url":request.path(),
                        "reason":"We don't recognize your username with that password"
                        }
    return check_auth

def perform_login(username, password, session):
    try:
        user = session.query(db.User).filter(db.User.username == username).one()
        if bcrypt.verify(password, user.passwordhash):
            user.last_seen = datetime.datetime.utcnow()
            session.add(user)
            return {'authentication_status':"success"}
        else:
            return {"authentication_status":"failure",
                        "requested_url":request.path(),
                        "reason":"We don't recognize your username with that password"
                        }
    except NoResultFound:
        return {"authentication_status":"failure",
                        'reason':'User not found'
                    }
    
@post('{0}login/'.format(base_url))
def login():    
    missing_fields = []
    try:
        username = request.json['username']
    except:
        missing_fields.append("username")
    try:
        password = request.json['password']
    except:
        missing_fields.append("password")
    if len(missing_fields) > 0:
        return {"authentication_status":"failure",
                    'missing_fields':missing_fields,
                    'reason':'Missing fields'
                }
    with db.session_scope() as session:
        return perform_login(username, password, session)
    
@get('{0}'.format(base_url))
def get_index():
    return static_file('index.html', root='.')
    
@get('{0}static/<filename:path>'.format(base_url))
def get_static(filename):
    return static_file(filename, root='./static')
    
@get('{0}cards/'.format(base_url))
def get_all_cards():
    with db.session_scope() as session:      
        return {"cards":get_cards(session)}
    
@get('{0}cards/<linkable_title>'.format(base_url))
def get_card(linkable_title): 
    with db.session_scope() as session:
        newest_card = get_newest_card(linkable_title, session)
        if newest_card is None:
            return {'linkable_title':linkable_title, 
                    'title':linkable_title.replace("_"," "),
                    'content':None, 
                    'rendered_content':None,
                    'edited_at':None, 
                    'edited_by':None,
                    'version':0}
        else:
            return newest_card.to_dict()
        
@get('{0}cards/<linkable_title>/wikilinks/'.format(base_url))
def get_card_links(linkable_title):
    with db.session_scope() as session:
        return {'card': 'cards/{0}/'.format(linkable_title),
                'wikilinks': get_wikilinks(linkable_title, session)}
    
@get('{0}cards/<linkable_title>/<version:int>'.format(base_url))
def get_card(linkable_title,version):
    '''redo this to use to_dict'''
    with db.session_scope() as session:
        newest_card = get_newest_card(linkable_title, session)
        if newest_card is None:
            return {'title':title, 
                    'content':None, 
                    'rendered_content':None,
                    'edited_at':None, 
                    'edited_by':None,
                    'version':0}
        else:            
            return newest_card.to_dict()
    
@put('{0}cards/<linkable_title>'.format(base_url))
@require_authentication
def create_card(linkable_title):
    with db.session_scope() as session:
        newest_card = get_newest_card(linkable_title, session)
        if newest_card is not None:      
            if newest_card.content != request.json['content']:      
                new_card = insert_card(db.Card(linkable_title=linkable_title, 
                                                title=request.json['title'].strip(),
                                                version=newest_card.version  + 1, 
                                                content=request.json['content'], 
                                                rendered_content = markdown.markdown(request.json['content'], extensions=[WikiLinkExtension(base_url='/cards/')]),
                                                edited_at=datetime.datetime.utcnow(), 
                                                edited_by=None), 
                                        session)
            else:
                new_card = None
        else:
            new_card = insert_card(db.Card(linkable_title=linkable_title, 
                                            title=request.json['title'],
                                            version=1, 
                                            content=request.json['content'], 
                                            rendered_content = markdown.markdown(request.json['content'], ['wikilinks(base_url={0}cards/)'.format(base_url)]),
                                            edited_at=datetime.datetime.utcnow(), 
                                            edited_by=None), 
                                    session)
        if new_card is None:
            return newest_card.to_dict()
        else:
            return new_card.to_dict()


        
@get('{0}cards/<linkable_title>/tags/'.format(base_url))
def get_card_tags(linkable_title):
    with db.session_scope() as session:
        return get_tags_for_card(linkable_title, session)

@put('{0}cards/<linkable_title>/tags/'.format(base_url))
@require_authentication
def create_card_tags(linkable_title):
    '''    
    session = db.session()
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
    session.close()    
    return get_card_tags(linkable_title)
    '''
    with db.session_scope() as session:
        insert_tags(request.json['tags'], session)
    with db.session_scope() as session:
        return get_tags_for_card(linkable_title, session)

    
'''
ACTUALLY DO THIS AT SOME POINT
@delete('{0}cards/<linkable_title>/tags/<tag>'.format(base_url))
@require_authentication
def create_card_tags(linkable_title, tag):
    session = db.session()
    db_tag = session.query(db.CardTag).filter(db.CardTag.tagged_card == linkable_title, db.CardTag.tag == tag).first()
    session.delete(db_tag)
    session.commit()
    session.close()
'''


    
@get('{0}tags/'.format(base_url))
def get_all_tags():
    '''
    session = db.session()
    q = session.query(db.CardTag.tag, func.count(db.CardTag.tag)).group_by(db.CardTag.tag).all()
    session.close()
    result = {"tags":[]}
    for tag in q:
        result["tags"].append({"tag":tag[0], "count":tag[1], "href":'{0}tags/{1}'.format(base_url, tag[0].replace(" ", "_"))})
    return result
    '''
    with db.session_scope() as session:
        return find_all_tags(session)
    
@get('{0}tags/<tag>'.format(base_url))
def get_cards_for_tag(tag):
    '''
    session = db.session()
    tags = session.query(db.CardTag.tagged_card).filter(db.CardTag.tag == tag)
    cards = session.query(db.Card).filter(db.Card.linkable_title.in_(tags))
    session.close()
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
    '''
    with db.session_scope() as session:
        find_cards_for_tag(tag, session)
