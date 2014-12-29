from cardwiki import db
import os
import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
import datetime

if os.path.isfile(db.db_path):
    #database exists, do nothing
    pass
else:
    #create the database
    db.Base.metadata.create_all(db.engine)
    #put the starting card in the db
    session = db.Session()
    content = """Welcome to *Card Wiki*
========================

Modify this card, or add new cards to get started.
Check out our documentation at our websites"""
    rendered_content = markdown.markdown(content, 
                                            extensions=[WikiLinkExtension(base_url='/cards/')])
    session.add(db.Card(linkable_title="__startCard",
                        title="Start Card", 
                        version=1, 
                        content=content, 
                        rendered_content = rendered_content,
                        edited_at=datetime.datetime.utcnow(), 
                        edited_by=None))
    session.commit()