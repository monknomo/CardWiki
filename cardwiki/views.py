from bottle import get, post, put, delete, run, template, request, static_file, request
import cardwiki
from cardwiki.db import session_scope
from sqlalchemy import func, exists, distinct, and_
from sqlalchemy.orm.exc import NoResultFound
import json
import datetime
import markdown
from cardwiki.wikilinks import WikiLinkExtension
import re
from passlib.hash import bcrypt

base_url = "/"

def require_authentication(func):
    def check_auth(*args, **kwargs):
        with db.session_scope() as session:
            try:
                username = request.json['username']
            except:
                try:
                    password = request.json['password']
                except:
                    return {"status":"failure",
                            "requested_url":request.path,
                            "reason":"We need both a username and password"
                            }
                return {"status":"failure",
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
                return {"status":"failure",
                        "requested_url":request.path(),
                        "reason":"We don't recognize your username with that password"
                        }
    return check_auth

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
        return {"status":"failure",
                    'missing_fields':missing_fields,
                    'reason':'Missing fields'
                }
    with db.session_scope() as session:
        return cardwiki.perform_login(username, password, session)

@get('{0}'.format(base_url))
def get_index():
    return static_file('index.html', root='.')

@get('{0}static/<filename:path>'.format(base_url))
def get_static(filename):
    return static_file(filename, root='./static')

@get('{0}cards/'.format(base_url))
def get_all_cards():
    with session_scope() as session:
        return {"cards":cardwiki.
        get_cards(session)}

@get('{0}cards/<linkable_title>'.format(base_url))
def get_card(linkable_title):
    with session_scope() as session:
        result = cardwiki.get_newest_card(linkable_title, session)
        if result is None or result == {}:
            request.status = 404
            return {"status":"failure","reason":"Card {0} not found".format(linkable_title)}
        return result
        
@get('{0}cards/<linkable_title>/<version:int>'.format(base_url))
def get_card_version( linkable_title,version):
    with session_scope() as session:
        return cardwiki.get_card_version(linkable_title, version, session)

@put('{0}cards/<linkable_title>'.format(base_url))
#@require_authentication
def create_card(linkable_title):
    card = cardwiki.request_to_carddict(request)
    if linkable_title is not card['link']:
        request.status = 400
        return {"status":"failure", "reason":"resource uri does not match link in request"}
    with session_scope() as session:
        return cardwiki.insert_card(card,  
                                    session)

@delete('{0}cards/<linkable_title>'.format(base_url))
def delete_card(linkable_title):
    with session_scope() as session:
        try:
            cardwiki.delete_card(linkable_title, session)
        except cardwiki.CardNotFoundException as cardNotFound:
            return {"status":"failure", "reason":cardNotFound.value}  
    return {"status":"success", "deleted_card":linkable_title}
                                    
@get('{0}cards/<linkable_title>/tags/'.format(base_url))
def get_card_tags(linkable_title):
    with session_scope() as session:
        try:
            return cardwiki.get_tags_for_card(linkable_title, session)
        except cardwiki.CardNotFoundException as cardNotFound:
            return {"status":"failure", "reason":cardNotFound.value}  

@put('{0}cards/<linkable_title>/tags/'.format(base_url))
#@require_authentication 
def create_card_tags(linkable_title):
    for tag in request.json['tags']:
        if tag['tagged_card'] is not linkable_title:
            print(tag['tag'])
            return {"status":"failure", "reason":"Tag {{'tag': '{0}', 'tagged_card': '{1}'}} does not belong to card {2}".format(tag['tag'], tag['tagged_card'], linkable_title)
            }
    with session_scope() as session:
        cardwiki.insert_tags(request.json['tags'], session)
    with session_scope() as session: 
        return cardwiki.get_tags_for_card(linkable_title, session)
        
@delete('{0}cards/<linkable_title>/tags/<tag>'.format(base_url))
#@require_authentication
def delete_card_tags(linkable_title, tag):
    with session_scope() as session:
        try:
            cardwiki.delete_tag({"tag":tag, "tagged_card":linkable_title}, session)
        except cardwiki.CardNotFoundException as cardNotFound:
            return {"status":"failure", "reason":cardNotFound.value}
            
@get('{0}tags/'.format(base_url))
def get_all_tags():
    with db.session_scope() as session:
        return cardwiki.find_all_tags(session)

@get('{0}tags/<tag>'.format(base_url))
def get_cards_for_tag(tag):
    with db.session_scope() as session:
        return cardwiki.find_cards_for_tag(tag, session)
