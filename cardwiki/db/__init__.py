from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, Sequence, ForeignKey, Date, DateTime, ForeignKeyConstraint
from sqlalchemy.orm import relationship, sessionmaker

db_path = "wiki.db"

engine = create_engine('sqlite:///{0}'.format(db_path), echo=True)
Session = sessionmaker(bind=engine)

Base = declarative_base()

class Card(Base):
    __tablename__ = 'card'
    linkable_title = Column(String(200), primary_key=True)    
    version = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text())
    rendered_content = Column(Text())
    edited_at = Column(DateTime())    
    edited_by = Column(Integer, ForeignKey('user.id'))
    previous_title = Column(String(200))
    next_title = Column(String(200))
    wikilinks = relationship("CardWikiLink", backref="card", primaryjoin='and_(Card.title==CardWikiLink.from_card, Card.version == CardWikiLink.from_card_version)')
    tags = relationship("CardTag", backref="card")
    
    def __repr__(self):
        return "<Card(linkable_title={0}, title={1}, version={2}, "\
                "content={3}, rendered_content={4}, edited_at={5}, "\
                "edited_by={6})>".format(self.linkable_title, 
                                            self.title,
                                            self.version, 
                                            self.content, 
                                            self.rendered_content,
                                            self.edited_at, 
                                            self.edited_by)
    
    def to_dict(self):
        if self.edited_at is None:
            edited_at = None
        else:
            edited_at = self.edited_at.isoformat()
        return {"title":self.title, 
                "linkable_title":self.linkable_title,
                "version":self.version,
                "content":self.content,
                "rendered_content":self.rendered_content,
                "edited_at":edited_at,
                "edited_by":self.edited_by}
                
class CardWikiLink(Base):
    __tablename__ = 'card_wikilink'
    from_card = Column(String(200), ForeignKey('card.linkable_title'), primary_key=True)
    from_card_version = Column(Integer, ForeignKey('card.version'), primary_key=True)
    to_card = Column(String(200), ForeignKey('card.linkable_title'), primary_key=True)
    
    ForeignKeyConstraint(['from_card', 'from_card_version'], ['Card.linkable_title', 'Card.version'])
    
    def __repr__(self):
        return '<CardWikiLink(card_title={0}, '\
                'link={1})>'.format(self.from_card,
                                    self.to_card)
    def to_dict(self):
        return {"from_card":self.from_card,
                "from_card_version":self.from_card_version,
                "to_card":self.to_card}
    
class CardTag(Base):
    __tablename__ = 'card_tag'
    tagged_card = Column(String(200), ForeignKey('card.linkable_title'), primary_key=True)
    tag = Column(String, primary_key=True)
    
    def __repr__(self):
        return "<CardTag(tagged_card={0}, tag={1})>".format(self.tagged_card, 
                                                                self.tag)
    
    def to_dict(self):
        return {"tagged_card":self.tagged_card, "tag":self.tag}

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(50))
    google_id = Column(String(100))
    github_id = Column(String(100))
    facebook_id = Column(String(100))
    twitter_id = Column(String(100))
    yahoo_id = Column(String(100))

    repositories = relationship("UserRepository", backref="user")
    bio = relationship("UserBiography", uselist=False, backref="user")
    
    def to_dict(self):
        return {"id":self.id,
                    "username":self.username,
                    "google_id":self.google_id,
                    "github_id":self.github_id,
                    "facebook_id":self.facebook_id,
                    "twitter_id":self.twitter_id,
                    "yahoo_id":self.yahoo_id}
    
    def __repr__(self):
        return """<User(username='{0}', 
                    google_id='{1}', 
                    github_id='{2}', 
                    facebook_id='{3}', 
                    twitter_id='{4}', 
                    yahoo_id='{5}')>""".format(self.username, 
                                                self.google_id, 
                                                self.github_id, 
                                                self.facebook_id, 
                                                self.twitter_id, 
                                                self.yahoo_id)
								
class UserRepository(Base):
    __tablename__ = 'user_repository'
    id = Column(Integer, Sequence('user_repository_seq'), primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(1000))
    is_website = Column(Boolean())
    
    def to_dict(self):
        return {"id":self.id,
                "user_id":self.user_id,
                "name":self.name,
                "is_website":self.is_website}
    
    def __repr__(self):
        return "<UserRepository(user_id='{0}', name='{1}', "\
                "is_website='{2}')>".format(self.user_id, 
                                            self.name, 
                                            self.is_website)
        
class UserBiography(Base):
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
        return {"user_id":self.user_id,
                "name":self.name,
                "birthday":self.birthday.isoformat(),
                "email":self.email,
                "backup_email":self.backup_email,
                "phone":self.phone,
                "backup_phone":self.backup_phone,
                "bio":self.bio}
    
    def __repr__(self):
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
