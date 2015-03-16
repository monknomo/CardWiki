"""cardwiki module

This module is container for manipulating the parts of a cardwiki and interacting
with the cardwiki database in a predictable and predefined way
"""
from sqlalchemy import func, and_, exists
from sqlalchemy.orm.exc import NoResultFound
import markdown
from passlib.hash import bcrypt
from sqlalchemy.orm.exc import NoResultFound as SqlAlchemyNoResultFound

import cardwiki.db as db
import re
import datetime
import copy

BASE_URL = "/"

class CardNotFoundException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
        
def get_cards(session):
    """Returns a list of cards in the database

    Args:
        session (sqlalchemy session): a session with the database

    Returns:
        []: A list of dictonaries representing all the cards contained in the
        database.
    """
    result = []
    for card in session.query(db.Card):
        result.append({'display_title':card.display_title,
                       'link':card.link,
                       'current_version':len(card.versions.all())})
    return result

def derive_title_link(title):
    """Returns a cardwiki-style link; replaces spaces with underscores and non-html
        safe characters with an empty string.

    Args:
        title (str): A title of  a card

    Returns:
        str: A modified title, substituting underscores for spaces and removing
        non-html friendly characters
    """
    title = re.sub(r'[\ ]', '_', title)
    title = re.sub(r'[^a-zA-Z0-9_~\-\.]', '', title)
    return title

def get_newest_card(link, session):
    """Returns a dictionary representing the newest card for a given link

    Args:
        link (str): A link to a card
        session (sqlalchemy session): a session with the database

    Returns:
        dict: A dictionary represenation of the newest version of the card corresponding
        with the link
    """
    try:
        newest_card = session.query(db.Card).filter(db.Card.link == link).one()
        return newest_card.to_dict()
    except NoResultFound:
        return None

def get_card_version(link, version, session):
    cards = session.query(db.Card).filter(db.Card.link == link).one()
    try:
        card = cards.versions[version-1]
        value = card.to_dict()
        value = copy.deepcopy(value)
        value['version'] = version
        return value
    except IndexError:
        return None
        
def insert_card(card, session):
    """Inserts a card into the database

    Args:
        card (dict): A dictionary representing a card
        session (sqlalchemy session): a session with the database

    Returns:
        dict: a dictionary representing the card after insertion into the database
    """
    new_card = db.Card(display_title=card['display_title'],
                       link=card['link'],
                       content=card['content'],
                       rendered_content=card['rendered_content'],
                       edited_by=card['edited_by'])
    session.add(new_card)
    session.flush()

    result = new_card.to_dict()
    result['version'] = new_card.versions.count() + 1
    return result

def delete_card(link, session):
    """Deletes a card in the database

    Args:
        link (str): A link to a card
        session (sqlalchemy session): a session with the database
    """
    if session.query(db.Card).filter(db.Card.link == link).count() > 0:
        for card in session.query(db.Card).filter(db.Card.link == link).all():
            session.delete(card)
    else:
        value = "Tried to delete {0}, but it was not there".format(link)
        e = CardNotFoundException(value)
        print(e)
        raise e
        
def get_tags_for_card(link, session):
    """Gets all tags for a link to a card

    Args:
        link (str): A link to a card
        session (sqlalchemy session): a session with the database

    Returns:
        list: A list of tags corresponding to the card at the link
    """
    query = session.query(db.CardTag)
    try:
        target_card = session.query(db.Card).filter(db.Card.link == link).one()
        target_card = target_card.id
    except SqlAlchemyNoResultFound:
        value = "Tried to find tags for card {0}, but found no card".format(link)
        e = CardNotFoundException(value)
        raise e
    query = query.filter(db.CardTag.tagged_card == target_card)
    results = {"tags":[]}
    for tag in query:
        results["tags"].append({"tag":tag.tag,
                                "href":"{0}tags/{1}".format(BASE_URL,
                                                            tag.tag)})
    return results

def request_to_carddict(request):
    """Converts a bottle request to a dictionary representing a card

    Args:
        request (bottle.request): A bottle request with json corresponding to a cardwiki card

    Returns:
        dict: a dictionary representing a card
    """
    formatted_url = ['wikilinks(base_url={0}cards/)'.format(BASE_URL)]
    rendered_content = markdown.markdown(request.json['content'], formatted_url)
    try:
        version = request.json['version']
        return {'link': request.json['link'],
                'display_title': request.json['display_title'].strip(),
                'version': version,
                'content': request.json['content'],
                'rendered_content': rendered_content,
                'edited_by': request.json['edited_by']}
    except KeyError as keyerror:
        return {'link': request.json['link'],
                'display_title': request.json['display_title'].strip(),
                'version': 1,
                'content': request.json['content'],
                'rendered_content': rendered_content,
                'edited_by': request.json['edited_by']}

def insert_tags(tags, session):
    """Inserts a list of tag dictionaries into the database

    Args:
        tags (list): A list of tags, where each tag is a dict with a 'tag' key
            and a 'tagged_card' key
        session (sqlalchemy session): a session with the database

    Returns:
        list: A list of dictionaries representations of tags
    """
    inserted_tags = []
    for tag in tags:
        try:
            target_card = session.query(db.Card).filter(db.Card.link == tag['tagged_card']).one()
            card_id = target_card.id
        except SqlAlchemyNoResultFound:
            value = "Tried to inserting tags for card {0}, but found no card".format(tag['tagged_card'])
            raise CardNotFoundException(value)
        split_tags = re.split(r"[:,;+\.| ]", tag["tag"])
        
        for split_tag in split_tags:
            if split_tag.strip() != "":
                query = session.query(db.CardTag)
                query = query.filter(db.CardTag.tagged_card ==
                                     card_id,
                                     db.CardTag.tag == split_tag)
                if query.count() == 0:
                    print("inserting tag")
                    tag_to_insert = db.CardTag(tagged_card=card_id,
                                               tag=split_tag)
                    session.add(tag_to_insert)
                    inserted_tags.append(tag_to_insert.to_dict())
    return tags

def delete_tag(tag, session):
    """Deletes a tag

    Args:
        tag (dict): a dict with a 'tag' key and a 'tagged_card' key
        session (sqlalchemy session): a session with the database
    """
    try:
        target_card = session.query(db.Card).filter(db.Card.link == tag['tagged_card']).one()
        card_id = target_card.id
    except SqlAlchemyNoResultFound:
        value = "Tried deleting tag {0} for card {1}, but found no card".format(tag['tag'], tag['tagged_card'])
        raise CardNotFoundException(value)
    tag_to_be_deleted = session.query(db.CardTag)
    tag_to_be_deleted = tag_to_be_deleted.filter(db.CardTag.tag == tag['tag'],
                                                 db.CardTag.tagged_card ==
                                                 card_id)
    for dtag in tag_to_be_deleted:
        session.delete(dtag)



def find_all_tags(session):
    """Finds all the tags in the database

    Args:
        session (sqlalchemy session): a session with the database

    Returns:
        dict: A dictionary containing a list of tag dictionaries
    """
    query = session.query(db.CardTag.tag, func.count(db.CardTag.tag))
    query = query.group_by(db.CardTag.tag).all()
    result = {"tags":[]}
    for tag in query:
        href = '{0}tags/{1}'.format(BASE_URL, tag[0].replace(" ", "_"))
        result["tags"].append({"tag":tag[0], "count":tag[1], "href":href})
    return result

def find_cards_for_tag(tag, session):
    """Finds all the cards corresponding to a tag

    Args:
        tag (str): A tag
        session (sqlalchemy session): a session with the database
    """
    tags = session.query(db.CardTag.tagged_card).filter(db.CardTag.tag == tag)
    cards = session.query(db.Card).filter(db.Card.id.in_(tags)).all()
    result = {"cards":[]}
    for card in cards:
        card_dict = card.to_dict()
        card_dict['href'] = '{0}cards/{1}'.format(BASE_URL, card_dict['link'])
        result["cards"].append(card_dict)
    return result

def perform_login(username, password, request_url, session):
    """Attempts to authenticate a user for an initial login.  Each REST resource
    that requires authentication requires a username and password be sent, and
    this method determines whether authentication suceeds or fails

    Args:
        username (str): a username
        password (str): a plain text password
        request_url (str): the requested resources url
        session (sqlalchemy session): a session with the database

    Returns:
        dict: containing the key 'authentication_status' with the values 'success'
        or 'failure'.  If the value of 'authentication_status' is 'failure', also
        contains 'request_url' with the path of the requested resource and 'reason'
        with a reason for failure.
    """
    try:
        user = session.query(db.User).filter(db.User.username == username).one()
        if bcrypt.verify(password, user.passwordhash):
            user.last_seen = datetime.datetime.utcnow()
            session.add(user)
            return {'authentication_status':"success",
                    'request_url':request_url}
        else:
            return {"authentication_status":"failure",
                    "request_url":request_url,
                    "reason":"We don't recognize your username with that password"}
    except NoResultFound:
        return {"authentication_status":"failure",
                'reason':'User not found',
                'request_url':request_url}
