import cardwiki
from cardwiki.db import session_scope
from cardwiki import views
from cardwiki import Card, UndeletableAttributeException, InvalidKeyException
from sqlalchemy.orm.exc import NoResultFound
import unittest
import copy
import markdown
from cardwiki.wikilinks import WikiLinkExtension

class MockCardRequest:
    def __init__(self):
        self.json = {'link': "json_test_title",
                     'display_title': "json test title",
                     'version': "4",
                     'content': "test content",
                     'rendered_content': "<p>test content</p>",
                     'edited_by': "unittest"}

class MockTagRequest:
    def __init__(self):
        self.json = {'tags':[{'tag':'descriptive_tag', 
                              'tagged_card':'__startCard'}]}

class TestCardwikiCard(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_card_constructor(self):
        card = Card()
        self.assertEqual("", card.link)
        self.assertIsNone(card.display_title)
        self.assertIsNone(card.version)
        self.assertIsNone(card.content)
        self.assertIsNone(card.rendered_content)
        self.assertIsNone(card.edited_by)
        card = Card(link="link", display_title="link", version=1, content="a", rendered_content="<p>a</p>", edited_by="unittest")
        self.assertEqual("link", card.link)
        self.assertEqual("link", card.display_title)
        self.assertEqual(1, card.version)
        self.assertEqual("a", card.content)
        self.assertEqual("<p>a</p>", card.rendered_content)
        self.assertEqual("unittest", card.edited_by)
        mcr = MockCardRequest()
        card = Card(json_dict=mcr.json)
        self.assertEqual("json_test_title", card.link)
        self.assertEqual("json test title", card.display_title)
        self.assertEqual(4, card.version)
        self.assertEqual("test content", card.content)
        self.assertEqual("<p>test content</p>", card.rendered_content)
        self.assertEqual("unittest", card.edited_by)
        mcr = MockCardRequest()
        mcr.json.pop("version", None)
        card = Card(json_dict=mcr.json)
        self.assertEqual(1, card.version)
        mcr = MockCardRequest()
        mcr.json['content'] = "test content [[bears]]"
        mcr.json['rendered_content'] = None
        card = Card(json_dict=mcr.json)
        self.assertEqual("json_test_title", card.link)
        self.assertEqual("json test title", card.display_title)
        self.assertEqual(4, card.version)
        self.assertEqual("test content [[bears]]", card.content)
        self.assertEqual("<p>test content <a class=\"wikilink\" href=\"#card_bears\" onClick=\"appendCard(&quot;json_test_title&quot;, &quot;bears&quot;)\">bears</a></p>", card.rendered_content)
        self.assertEqual("unittest", card.edited_by)
        mcr = MockCardRequest()
        mcr.json['rendered_content'] = None
        card = Card(json_dict=mcr.json)
        self.assertEqual("json_test_title", card.link)
        self.assertEqual("json test title", card.display_title)
        self.assertEqual(4, card.version)
        self.assertEqual("test content", card.content)
        self.assertEqual("<p>test content</p>", card.rendered_content)
        self.assertEqual("unittest", card.edited_by)
        mcr = MockCardRequest()

    def test_derive_title_link(self):
        expected = "this_is_a_title"
        result = Card.derive_title_link("this is a title")
        self.assertEqual(expected, result)
        
class TestInvalidKeyException(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_constructor(self):
        e = InvalidKeyException("a value")
        self.assertEqual("a value", e.value)
        self.assertEqual("'a value'", str(e))

class TestUndeletableAttributeException(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
    
    def test_constructor(self):
        e = UndeletableAttributeException("a value")
        self.assertEqual("a value", e.value)
        self.assertEqual("'a value'", str(e))

class TestCardwikiMarkdown(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        pass
        
    def test_wikilink(self):
        content = """Welcome to *Card Wiki*
========================

Modify this card, or add new cards to get started.
Check out our documentation at our websites

Use [[wikilinks]] to make new cards"""
        rendered_content = markdown.markdown(content,
                                             extensions=[WikiLinkExtension(base_url='', card_link='__startCard')])
        expected = """<h1>Welcome to <em>Card Wiki</em></h1>
<p>Modify this card, or add new cards to get started.
Check out our documentation at our websites</p>
<p>Use <a class="wikilink" href="#card_wikilinks" onClick="appendCard(&quot;__startCard&quot;, &quot;wikilinks&quot;)">wikilinks</a> to make new cards</p>"""
        self.assertEqual(expected, rendered_content)

        
class TestCardwikiFunctions(unittest.TestCase):

    def setUp(self):
        pass
        
    def tearDown(self):
        with session_scope() as session:
            cardwiki._delete_card_versions(session)

    def test_get_cards(self):
        with session_scope() as session:
            cards = cardwiki.get_cards(session)
        print(cards)
        self.assertEqual('', cards[0]['display_title'])
        self.assertEqual('__startCard', cards[0]['link'])
        self.assertEqual(1, cards[0]['current_version'])

    def test_get_tags_for_card(self):
        tags = {}
        with session_scope() as session:
            tags = cardwiki.get_tags_for_card('__startCard', session)
        self.assertEqual(1, len(tags['tags']))
        self.assertEqual('administrivia', tags['tags'][0]['tag'])
        self.assertEqual('/tags/administrivia', tags['tags'][0]['href'])

    def test_get_newest_card(self):
        card = {}
        with session_scope() as session:
            card = cardwiki.get_newest_card('__startCard', session)
        self.assertEqual('__startCard', card['link'])
        self.assertEqual('', card['display_title'])

    def test_get_newest_card_nonexistent(self):
        card = None
        expected = Card(link='foobar', display_title='foobar', version=1)
        with session_scope() as session:
            card = cardwiki.get_newest_card('foobar', session)
        self.assertEqual(expected, card)

    def test_insert_card(self):
        try:
            with session_scope() as session:
                initial_card = {'display_title' : "test card",
                                'link':"test_card",
                                'content':"### test content",
                                'rendered_content':
                                    "<h3>test content</h3>",
                                'edited_by':"unittest"}
                card = cardwiki.insert_card(Card(json_dict=initial_card), session)
                self.assertIsNotNone(card['id'])
                self.assertEqual(initial_card['display_title'], card['display_title'])
                self.assertEqual(initial_card['link'], card['link'])
                self.assertEqual(initial_card['content'], card['content'])
                self.assertEqual(initial_card['rendered_content'], card['rendered_content'])
                self.assertEqual(initial_card['edited_by'], card['edited_by'])
        finally:
            with session_scope() as session:
                cardwiki.delete_card('test_card', session)

    def test_delete_card(self):
        card = {}
        expected = Card(link='test_card', display_title='test card', version=1)
        with session_scope() as session:
            initial_card = {'display_title' : "test card",
                                            'link':"test_card",
                                            'content':"### test content",
                                            'rendered_content':
                                                "<h3>test content</h3>",
                                            'edited_by':"admin"}
            card = cardwiki.insert_card(Card(json_dict=initial_card), session)
            self.assertIsNotNone(card['id'])
            cardwiki.delete_card(card['link'], session)
            card = cardwiki.get_newest_card(card['link'], session)
        self.assertEqual(expected, card)

    def test_delete_card_nonexistent(self):
        card = None
        try:
            with session_scope() as session:
                cardwiki.delete_card('foobar', session)
                self.fail()
        except cardwiki.CardNotFoundException as a:
            pass
        except:
            self.fail()

    def test_request_to_carddict(self):
        request = MockCardRequest()
        carddict = Card(json_dict=request.json)
        self.assertEqual(request.json['link'], carddict['link'])
        self.assertEqual(request.json['content'], carddict['content'])
        self.assertEqual(request.json['rendered_content'], carddict['rendered_content'])
        self.assertEqual(request.json['display_title'], carddict['display_title'])
        self.assertEqual(int(request.json['version']), carddict['version'])
        self.assertEqual(request.json['edited_by'], carddict['edited_by'])

    def test_request_to_carddict_no_version(self):
        request = MockCardRequest()
        request.json.pop("version", None)
        carddict = Card(json_dict=request.json)
        request.json['version'] = 1
        self.assertEqual(request.json, carddict)

    def test_insert_tags(self):
        tags = []
        tags.append({"tag":"interesting", "tagged_card":"__startCard"})
        tags.append({"tag":"admin", "tagged_card":"__startCard"})
        try:
            with session_scope() as session:
                cardwiki.insert_tags(tags, session)
                session.flush()
                for tag in tags:
                    cards = cardwiki.find_cards_for_tag(tag['tag'], session)
                    self.assertEqual(1, len(cards['cards']))
                    card = cards['cards'][0]
                    self.assertEqual('/cards/__startCard', card['href'])
        finally:
            with session_scope() as session:
                for tag in tags:
                    cardwiki.delete_tag(tag, session)

    def test_delete_tag(self):
        tags = []
        tags.append({"tag":"interesting", "tagged_card":"__startCard"})
        tags.append({"tag":"admin", "tagged_card":"__startCard"})
        try:
            with session_scope() as session:
                cardwiki.insert_tags(tags, session)
            with session_scope() as session:
                for tag in tags:
                    cards = cardwiki.find_cards_for_tag(tag['tag'], session)
                    self.assertEqual(1, len(cards['cards']))
                    card = cards['cards'][0]
                    self.assertEqual('/cards/__startCard', card['href'])
                    cardwiki.delete_tag(tag, session)
                    session.flush()
                    cards = cardwiki.find_cards_for_tag(tag['tag'], session)
                    self.assertEqual(0, len(cards['cards']))
        finally:
            with session_scope() as session:
                if len(cardwiki.find_all_tags(session)['tags']) > 1:
                    for tag in tags:
                        cardwiki.delete_tag(tag, session)

    def test_delete_spurious_tag(self):
        try:
            with session_scope() as session:
                cardwiki.delete_tag({'tag':'foobar','tagged_card':'goocar'}, session)
                self.fail()
        except cardwiki.CardNotFoundException:
            pass

    def test_find_all_tags(self):
        with session_scope() as session:
            tags = cardwiki.find_all_tags(session)
            self.assertEqual(1, len(tags['tags']))
            self.assertEqual('administrivia', tags['tags'][0]['tag'])
            self.assertEqual(1, tags['tags'][0]['count'])
            self.assertEqual('/tags/administrivia', tags['tags'][0]['href'])

    def test_perform_login(self):
        with session_scope() as session:
            result = cardwiki.perform_login('admin', 'admin', '/', session)
            self.assertEqual({'authentication_status':"success",
                               'request_url':'/'}, result)

    def test_perform_login_bad_password(self):
        with session_scope() as session:
            result = cardwiki.perform_login('admin', 'bogus', '/', session)
            self.assertEqual({"authentication_status":"failure",
                               "request_url":'/',
                               "reason":"We don't recognize your username with "\
                               "that password"}, result)

    def test_perform_login_bad_username(self):
        with session_scope() as session:
            result = cardwiki.perform_login('bogus', 'admin', '/', session)
            self.assertEqual({"authentication_status":"failure",
                               'reason':'User not found',
                               'request_url':'/' }, result)
                               
class TestCardwikiViews(unittest.TestCase):
    def setUp(self):
        self.__startCard = {'edited_by':'admin', 
                            'content':'''Welcome to *Card Wiki*\n========================\n\nModify this card, or add new cards to get started.\nCheck out our documentation at our websites\n\nUse [[wikilinks]] to make new cards''', 
                            'rendered_content':"""<h1>Welcome to <em>Card Wiki</em></h1>
<p>Modify this card, or add new cards to get started.
Check out our documentation at our websites</p>
<p>Use <a class="wikilink" href="#card_wikilinks" onClick="appendCard(&quot;__startCard&quot;, &quot;wikilinks&quot;)">wikilinks</a> to make new cards</p>""", 
                            'display_title':'', 
                            'link':'__startCard', 
                            'id':1, 
                            'edited_at':'2015-02-08T10:33:34.573496'}
        
    def tearDown(self):
        with session_scope() as session:
            cardwiki._delete_card_versions(session)
        
    def test_get_index(self):
        self.assertTrue(views.get_index().body.name.endswith('index.html'))
        
    def test_get_index_twice(self):
        first = views.get_index().body.name.endswith('index.html')
        second = views.get_index().body.name.endswith('index.html')
        self.assertEqual(first, second)
        
    def test_get_static(self):
        self.assertTrue(views.get_static('js/validator.min.js').body.name.endswith('validator.min.js'))
    
    def test_get_static_twice(self):
        first = views.get_static('js/validator.min.js').body.name.endswith('validator.min.js')
        second = views.get_static('js/validator.min.js').body.name.endswith('validator.min.js')
        self.assertEqual(first, second)
    
    def test_get_all_cards(self):
        self.assertEqual(1, len(views.get_all_cards()['cards']))
        
    def test_get_all_cards_twice(self):
        first = views.get_all_cards()
        second = views.get_all_cards()
        self.assertEqual(first, second)
    
    def test_get_card(self):
        self.assertEqual(self.__startCard['rendered_content'], views.get_card('__startCard')['rendered_content'])
        self.assertEqual(self.__startCard['content'], views.get_card('__startCard')['content'])
        self.assertEqual(self.__startCard['link'], views.get_card('__startCard')['link'])
        self.assertEqual(self.__startCard['display_title'], views.get_card('__startCard')['display_title'])
        self.assertEqual(self.__startCard['id'], views.get_card('__startCard')['id'])
        self.assertEqual(self.__startCard['edited_by'], views.get_card('__startCard')['edited_by'])
    
    def test_get_card_twice(self):
        first = views.get_card('__startCard')
        second = views.get_card('__startCard')
        self.assertEqual(first, second)
    
    def test_get_card_bogus_card(self):
        response = views.get_card('__startCardasdfasdf')
        expected = Card(link='__startCardasdfasdf', display_title=None, version=1)
        expected.status="success"
        self.assertEqual(expected, response)
    
    def test_get_card_version(self):
        __startCard_v1 = copy.deepcopy(self.__startCard)
        __startCard_v1['version'] = 1
        result = views.get_card_version('__startCard', 1)
        print(__startCard_v1['rendered_content'])
        print(result['rendered_content'])
        self.assertEqual(__startCard_v1['display_title'], result['display_title'])
        self.assertEqual(__startCard_v1['link'], result['link'])
        self.assertEqual(__startCard_v1['version'], result['version'])
        self.assertEqual(__startCard_v1['id'], result['id'])
        self.assertEqual(__startCard_v1['content'], result['content'])
        self.assertEqual(__startCard_v1['rendered_content'], result['rendered_content'])
        self.assertEqual(__startCard_v1['edited_by'], result['edited_by'])
    
    def test_get_card_version_twice(self):
        first = views.get_card_version('__startCard', 1)
        second = views.get_card_version('__startCard', 1)
        self.assertEqual(first, second)
    
    def test_get_all_card_versions(self):
        current = views.get_card_version('__startCard', 1)
        previous = None
        while current['next_version'] is not None:
            previous = current
            current = views.get_card_version('__startCard', int(current['next_version']))
            if current is not None and previous is not None:
                self.assertEqual(current['link'], previous['link'])
                self.assertEqual(previous['version'] + 1, current['version'])
                self.assertEqual(previous['next_version'], current['version'])
                self.assertNotEqual(previous['content'], current['content'])

    def test_get_card_version_bogus_version(self):
        response = views.get_card_version('__startCard', -1)
        expected = {"status":"failure", "reason":"No version -1 found for card '__startCard'"}
        self.assertEqual(expected, response)
    
    def test_get_card_version_bogus_card(self):
        response = views.get_card_version('bogon_from_space', 1)
        expected = {"status":"failure", "reason":"No version 1 found for card 'bogon_from_space'"}
        self.assertEqual(expected, response)
    
    def test_get_card_version_bogus_card_and_bogus_version(self):
        response = views.get_card_version('bogon_from_space', -1)
        expected = {"status":"failure", "reason":"No version -1 found for card 'bogon_from_space'"}
        self.assertEqual(expected, response)
    
    def test_create_card(self):
        views.request = MockCardRequest()
        try:
            created_card = views.create_card(views.request.json['link'])
            expected = Card(json_dict=views.request.json)
            self.assertEqual(expected['display_title'], created_card['display_title'])
            self.assertEqual(expected['edited_by'], created_card['edited_by'])
            self.assertEqual(expected['link'], created_card['link'])
            self.assertEqual(expected['content'], created_card['content'])
            self.assertEqual(expected['link'], created_card['link'])
            self.assertEqual(expected['rendered_content'], created_card['rendered_content'])
            self.assertIsNotNone(created_card['id'])
            self.assertIsNotNone(created_card['version'])
            self.assertIsNotNone(created_card['edited_at'])
        finally:
            with session_scope() as session:
                cardwiki.delete_card(views.request.json['link'], session)
    
    def test_create_card_twice(self):
        views.request = MockCardRequest()
        try:
            created_card = views.create_card(views.request.json['link'])
            second_created_card = views.create_card(views.request.json['link'])
            self.assertEquals(created_card, second_created_card)
        finally:
            with session_scope() as session:
                cardwiki.delete_card(views.request.json['link'], session)
    
    def test_create_card_with_changes(self):
        views.request = MockCardRequest()
        try:
            created_card = views.create_card(views.request.json['link'])
            views.request.json['content'] = "totally different content"
            created_card_with_changes = views.create_card(views.request.json['link'])
            expected = Card(json_dict=views.request.json)
            self.assertNotEqual(created_card, created_card_with_changes)
            self.assertEqual(expected['display_title'], created_card_with_changes['display_title'])
            self.assertEqual(expected['edited_by'], created_card_with_changes['edited_by'])
            self.assertEqual(expected['link'], created_card_with_changes['link'])
            self.assertEqual(expected['content'], created_card_with_changes['content'])
            self.assertEqual(expected['link'], created_card_with_changes['link'])
            self.assertEqual("<p>totally different content</p>", created_card_with_changes['rendered_content'])
            self.assertIsNotNone(created_card_with_changes['id'])
            self.assertIsNotNone(created_card_with_changes['version'])
            self.assertIsNotNone(created_card_with_changes['edited_at'])
        finally:
            with session_scope() as session:
                cardwiki.delete_card(views.request.json['link'], session)
    
    def test_create_card_with_same_changes_twice(self):
        views.request = MockCardRequest()
        try:
            created_card = views.create_card(views.request.json['link'])
            views.request.json['content'] = "totally different content"
            created_card_with_changes = views.create_card(views.request.json['link'])
            created_card_with_changes_second = views.create_card(views.request.json['link'])
            self.assertNotEqual(created_card, created_card_with_changes_second)
            self.assertEqual(created_card_with_changes, created_card_with_changes_second)
        finally:
            with session_scope() as session:
                cardwiki.delete_card(views.request.json['link'], session)
    
    def test_create_card_request_does_not_match_uri(self):
        views.request = MockCardRequest()
        try:
            expected = {"status":"failure", "reason":"resource uri does not match link in request"}
            response = views.create_card('testcard')   
            self.assertEqual(expected, response)
        finally:
            with session_scope() as session:
                card = cardwiki.get_newest_card(views.request.json['link'], session)
                if card['content'] is not None:
                    cardwiki.delete_card(views.request.json['link'], session)
    
    def test_delete_card(self):
        views.request = MockCardRequest()
        try:
            created_card = views.create_card(views.request.json['link'])
            response = views.delete_card(views.request.json['link'])
            expected = {"status":"success", "deleted_card":views.request.json['link']}
            self.assertEqual(expected, response)
                
        finally:
            with session_scope() as session:
                card = cardwiki.get_newest_card(views.request.json['link'], session)
                if card['content'] is not None:
                    cardwiki.delete_card(views.request.json['link'], session)
    
    def test_delete_card_twice(self):
        views.request = MockCardRequest()
        try:
            created_card = views.create_card(views.request.json['link'])
            response = views.delete_card(views.request.json['link'])
            response = views.delete_card(views.request.json['link'])
        finally:
            with session_scope() as session:
                card = cardwiki.get_newest_card(views.request.json['link'], session)
                if card['content'] is not None:
                    cardwiki.delete_card(views.request.json['link'], session)
    
    def test_delete_card_nonexistent(self):
        expected = {"status":"failure", "reason":"Tried to delete bogon_from_space, but it was not there"}  
        response = views.delete_card("bogon_from_space")
        self.assertEqual(expected, response)
            
    def test_get_card_tags(self):
        response = views.get_card_tags('__startCard')
        expected = {'tags':[{'tag':'administrivia','href':'/tags/administrivia'}]}
        self.assertEqual(expected, response)
    
    def test_get_card_tags_twice(self):
        first = views.get_card_tags('__startCard')
        second = views.get_card_tags('__startCard')
        self.assertEqual(first, second)
    
    def test_get_card_tags_bogus_card(self):
        response = views.get_card_tags('bogon_from_space')
    
    def test_create_card_tags(self):
        views.request = MockTagRequest()
        try:
            response = views.create_card_tags('__startCard')
            expected = {'tags': [{'href':'/tags/administrivia', 
                                  'tag':'administrivia'}, 
                                 {'href': '/tags/descriptive_tag', 
                                  'tag':'descriptive_tag'}]}
            self.assertEqual(expected, response)
        finally:
            views.delete_card_tags('__startCard', 'descriptive_tag')
    
    def test_create_card_tags_multiple_tags(self):
        views.request = MockTagRequest()
        views.request.json['tags'].append({'tag':'another_tag', 'tagged_card':'__startCard'})
        try:
            response = views.create_card_tags('__startCard')
            expected = {'tags': [{'href':'/tags/administrivia', 
                                  'tag':'administrivia'}, 
                                 {'href': '/tags/descriptive_tag', 
                                  'tag':'descriptive_tag'},
                                 {'tag':'another_tag', 
                                  'tagged_card':'__startCard'}]}
            self.assertCountEqual(expected, response)
        finally:
            views.delete_card_tags('__startCard', 'descriptive_tag')
            views.delete_card_tags('__startCard', 'another_tag')
    
    def test_create_card_tags_multiple_tags_twice(self):
        views.request = MockTagRequest()
        views.request.json['tags'].append({'tag':'another_tag', 'tagged_card':'__startCard'})
        try:
            first = views.create_card_tags('__startCard')
            second = views.create_card_tags('__startCard')
            self.assertCountEqual(first, second)
        finally:
            views.delete_card_tags('__startCard', 'descriptive_tag')
            views.delete_card_tags('__startCard', 'another_tag')
    
    def test_create_card_tags_twice(self):
        views.request = MockTagRequest()
        try:
            views.create_card_tags('__startCard')
            views.create_card_tags('__startCard')
            response = views.create_card_tags('__startCard')
            expected = {'tags': [{'href':'/tags/administrivia', 
                                  'tag':'administrivia'}, 
                                 {'href': '/tags/descriptive_tag', 
                                  'tag':'descriptive_tag'}]}
            self.assertCountEqual(expected, response)
        finally:
            views.delete_card_tags('__startCard', 'descriptive_tag')
            
    def test_create_card_tags_wrong_card_uri(self):  
        expected = {"reason": "Tag {'tag': 'descriptive_tag', 'tagged_card': '__startCard'} does not belong to card bogon_from_space", "status":"failure"}
        views.request = MockTagRequest()
        response = views.create_card_tags('bogon_from_space')
        self.assertEqual(expected, response)
    
    def test_create_card_tags_tag_does_not_match_uri(self):
        #400 error when uri is valid, but request does not match uri, or is otherwise invalid
        views.request = MockTagRequest()
        views.request.json['tags'][0]['tagged_card'] = 'bogon_from_space'
        expected = {'reason': "Card '__startCard' does not match {'tag':'descriptive_tag', 'tagged_card':'bogon_from_space'}",
                    'status': 'failure'}
        try:
            views.create_card_tags('__startCard')
            response = views.create_card_tags('__startCard')
            self.assertCountEqual(expected, response)
        finally:
            views.delete_card_tags('__startCard', 'descriptive_tag')
            
    def test_create_card_tags_tag_does_not_match_uri_and_uri_invalid(self):
        #404 error when uri is invalid
        views.request = MockTagRequest()
        expected = {'reason': "Tag {'tag': 'descriptive_tag', 'tagged_card': '__startCard'} does not belong to card bogon_from_space",
                    'status': 'failure'}
        response = views.create_card_tags('bogon_from_space')
        self.assertEqual(expected, response)
    
    def test_create_card_tags_invalid_uri(self):
        #404 error when uri is invalid
        views.request = MockTagRequest()
        views.request.json['tags'][0]['tagged_card'] = 'bogon_from_space'
        expected = {'reason': "Card 'bogon_from_space' does not exist",
                    'status': 'failure'}
        response = views.create_card_tags('bogon_from_space')
        self.assertEqual(expected, response)
    
    def test_delete_card_tags(self):
        views.request = MockTagRequest()
        response = views.create_card_tags('__startCard')
        views.delete_card_tags('__startCard', 'descriptive_tag')
        expected = {'tags': [{'tag':'administrivia', 'href':'/tags/administrivia'}]}
        self.assertEqual(expected, views.get_card_tags('__startCard'))
        
    def test_delete_card_tags_multiple(self):
        views.request = MockTagRequest()
        response = views.create_card_tags('__startCard')
        views.delete_card_tags('__startCard', 'descriptive_tag')
        views.delete_card_tags('__startCard', 'descriptive_tag')
        views.delete_card_tags('__startCard', 'descriptive_tag')
        views.delete_card_tags('__startCard', 'descriptive_tag')
        expected = {'tags': [{'tag':'administrivia', 'href':'/tags/administrivia'}]}
        self.assertEqual(expected, views.get_card_tags('__startCard'))
        
    def test_delete_card_tags_bogus_card_uri(self):
        views.request = MockTagRequest()
        response = views.create_card_tags('__startCard')        
        expected = {"status":"failure", "reason":"Tried deleting tag descriptive_tag for card bogon_from_space, but found no card"}
        result = views.delete_card_tags('bogon_from_space', 'descriptive_tag')
        self.assertEqual(expected, result)
    
    def test_delete_card_tags_bogus_tag_bogus_card(self):
        views.request = MockTagRequest()
        response = views.create_card_tags('__startCard')        
        expected = {"status":"failure", "reason":"Tried deleting tag bogus_tag for card bogon_from_space, but found no card"}
        result = views.delete_card_tags('bogon_from_space', 'bogus_tag')
        self.assertEqual(expected, result)
    
if __name__=='__main__':
    unittest.main()
    