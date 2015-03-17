"""
Database objects and access definitions for cardwiki
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text
from sqlalchemy import Sequence, ForeignKey, Date, DateTime
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship, sessionmaker, backref, configure_mappers
from sqlalchemy_continuum import make_versioned, version_class, transaction_class
from passlib.hash import bcrypt
from contextlib import contextmanager
import datetime as dt
import re

make_versioned(user_cls=None)

DB_PATH = "wiki.db"
ENGINE = create_engine('sqlite:///{0}'.format(DB_PATH), echo=False)
BASE = declarative_base()

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""

    session = sessionmaker(bind=ENGINE)()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def derive_title_link(title):
    """Derives a title sutiable for linking to"""
    title = re.sub(r'[\ ]', '_', title)
    title = re.sub(r'[^a-zA-Z0-9_~\-\.]', '', title)
    return title

class Card(BASE):
    """A Card object for persistence"""
    __versioned__ = {}
    __tablename__ = 'card'

    id = Column(Integer, primary_key=True, autoincrement=True)
    display_title = Column(String(200), nullable=False)
    link = Column(String(200), nullable=False)
    content = Column(Text())
    rendered_content = Column(Text())
    edited_at = Column(DateTime(), default=dt.datetime.utcnow())
    edited_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    tags = relationship("CardTag", backref="card")



    def __repr__(self):
        """returns a repr of this Card"""
        return "<Card(id={0}, display_title={1}, link={2}, content={3}, "\
               "rendered_content={4}, edited_at={5}, "\
               "edited_by={6})>".format(self.id,
                                        self.display_title,
                                        self.link,
                                        self.content,
                                        self.rendered_content,
                                        self.edited_at,
                                        self.edited_by)

    def to_dict(self):
        """returns a dictionary of this card, suitable for json serializing"""
        return {"id":self.id,
                "display_title":self.display_title,
                "link":self.link,
                "content":self.content,
                "rendered_content":self.rendered_content,
                "edited_at":self.edited_at.isoformat(),
                "edited_by":self.edited_by}


                
class CardTag(BASE):
    """An object for relating tags to Cards, and persisting that relationship"""
    __tablename__ = 'card_tag'
    tagged_card = Column(Integer,
                         ForeignKey('card.id'),
                         primary_key=True)
    tag = Column(String, primary_key=True)

    def __repr__(self):
        """returns a repr of this CardTag"""
        return "<CardTag(tagged_card={0}, tag={1})>".format(self.tagged_card,
                                                            self.tag)

    def to_dict(self):
        """return a dictionary of this CardTag suitable for serializing to json"""
        return {"tagged_card":self.tagged_card, "tag":self.tag}

class User(BASE):
    """An object for persisting users"""

    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(254))
    google_id = Column(String(100))
    github_id = Column(String(100))
    facebook_id = Column(String(100))
    twitter_id = Column(String(100))
    yahoo_id = Column(String(100))
    passwordhash = Column(String(5000))
    last_seen = Column(DateTime(), default=dt.datetime.utcnow())
    bio = relationship("UserBiography", uselist=False, backref="user")
    cards = relationship("Card", backref="card")

    def __init__(self, **kwargs):
        """A custom init method that allows passing in of plaintext passords
            to ensure that they are hashed with the preferred bcrypt algorithm"""
        if kwargs['plainpassword'] is not None:
            kwargs['passwordhash'] = bcrypt.encrypt(kwargs['plainpassword'])
            kwargs.pop('plainpassword')
        super(User, self).__init__(**kwargs)

    def to_dict_dangerous(self):
        """returns a dictionary of this User, suitable for serializing to json.
        Dangerous because it includes the password hash.  Don't just give this back"""
        if self.last_seen is None:
            last_seen = None
        else:
            last_seen = self.last_seen.isoformat()
        return {"id":self.id,
                "username":self.username,
                "passwordhash":self.passwordhash,
                "google_id":self.google_id,
                "github_id":self.github_id,
                "facebook_id":self.facebook_id,
                "twitter_id":self.twitter_id,
                "yahoo_id":self.yahoo_id,
                "last_seen":last_seen}

    def to_dict(self):
        """Returns a dictionary of this User, suitable for serializing to json.
        No password included, safe to pass around"""
        if self.last_seen is None:
            last_seen = None
        else:
            last_seen = self.last_seen.isoformat()
        return {"id":self.id,
                "username":self.username,
                "google_id":self.google_id,
                "github_id":self.github_id,
                "facebook_id":self.facebook_id,
                "twitter_id":self.twitter_id,
                "yahoo_id":self.yahoo_id,
                "last_seen":last_seen}


    def __repr__(self):
        """Returns a repr of this User"""
        return """<User(username='{0}',
                    passwordhash='{6}',
                    google_id='{1}',
                    github_id='{2}',
                    facebook_id='{3}',
                    twitter_id='{4}',
                    yahoo_id='{5}')>""".format(self.username,
                                               self.google_id,
                                               self.github_id,
                                               self.facebook_id,
                                               self.twitter_id,
                                               self.yahoo_id,
                                               self.passwordhash)

class UserBiography(BASE):
    """An object to allow users to persist a little something about themselves"""
    __tablename__ = 'user_biography'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    name = Column(String(500))
    birthday = Column(Date())
    email = Column(String(200))
    backup_email = Column(String(200))
    phone = Column(String(20))
    backup_phone = Column(String(20))
    bio = Column(String(2000))

    def to_dict(self):
        """returns a dictionary representation of this UserBiography suitable
        for serializing to json"""
        return {"user_id":self.user_id,
                "name":self.name,
                "birthday":self.birthday.isoformat(),
                "email":self.email,
                "backup_email":self.backup_email,
                "phone":self.phone,
                "backup_phone":self.backup_phone,
                "bio":self.bio}

    def __repr__(self):
        """returns a repr for this UserBiography"""
        return "<UserBiography(user_id='{0}', name='{1}', birthday='{2}', "\
                "email='{3}', backup_email='{4}', phone='{5}', "\
                "backup_phone='{6}', bio='{7}')>".format(self.user_id,
                                                         self.name,
                                                         self.birthday,
                                                         self.email,
                                                         self.backup_email,
                                                         self.phone,
                                                         self.backup_phone,
                                                         self.bio)
                                                         

configure_mappers()
CardVersion = version_class(Card)
print("%%%%%%%%%%%%%%%%"+str(Card.__versioned__))
CardTransaction = transaction_class(Card)


def _card_version_to_dict(class_):
    return {"id":class_.id,
                "display_title":class_.display_title,
                "link":class_.link,
                "content":class_.content,
                "rendered_content":class_.rendered_content,
                "edited_at":class_.edited_at.isoformat(),
                "edited_by":class_.edited_by}

CardVersion.to_dict = _card_version_to_dict