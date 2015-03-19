"""Initializes a sqlite database with just enough information to use cardwiki"""
from cardwiki import db
import os
import markdown
from cardwiki.wikilinks import WikiLinkExtension

def create_db():
    """Creates the initial sqlite database"""
    card_id = 1

    if os.path.isfile(db.DB_PATH):
        #database exists, do nothing
        pass
    else:
        #create the database
        db.BASE.metadata.create_all(db.ENGINE)
        #put the starting card in the db
        with db.session_scope() as session:
            session.add(db.User(username="admin", plainpassword="admin"))
            content = """Welcome to *Card Wiki*
========================

Modify this card, or add new cards to get started.
Check out our documentation at our websites

Use [[wikilinks]] to make new cards"""
            rendered_content = markdown.markdown(content,
                                                 extensions=[WikiLinkExtension(base_url='', card_link="__startCard")])

            card = db.Card(display_title="",
                           link="__startCard",
                           content=content,
                           rendered_content=rendered_content,
                           edited_by='admin')
            session.add(card)
            session.flush()
            card_id = card.id
            tag = db.CardTag(tagged_card=card_id, tag="administrivia")
            session.add(tag)

if __name__ == '__main__':
    create_db()
