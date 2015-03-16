__startCard = new Card({title:"__startCard", 
                        link:"__startCard", 
                        content:"This is the start card", 
                        rendered_content:"<p>This is the start card <a id='__startCardWikilink' href='#' class='wikilink'>wikilink</a></p>", 
                        edited_at:null, 
                        edited_by:"admin",
                        tags:[],
                        version:1});

recipeCard = new Card({title:"Recipe Card", 
                        link:"recipe_card", 
                        content:"This is a recipe", 
                        rendered_content:"<p>This is a recipe</p>", 
                        edited_at:null, 
                        edited_by:"chef",
                        tags:[],
                        version:7});

card400 = new Card({title:"Card 400", 
                        link:"card_400", 
                        content:"This card throws a 400 error", 
                        rendered_content:"<p>This card throws a 400 error</p>", 
                        edited_at:null, 
                        edited_by:"badmonkey",
                        tags:[],
                        version:1});
                        
$.mockjax({
    url: "/cards/recipe_card",
    type: "put",
    dataType: "json",
    response: function(settings){
        var input = JSON.parse(settings.data);
        if(input.version == null){
            input.version = 1;
        }
        var now = new Date()
        this.responseText=  JSON.stringify({"title":input.title,
                                            "link":input.link,
                                            "content":input.content,
                                            "rendered_content":marked(input.content),
                                            "edited_at":now.toISOString(),
                                            "edited_by":input.edited_by,
                                            "version":input.version,
                                            "authentication_status":"success"
                                            });
        return;
    }
});

$.mockjax({
    url: "/cards/recipe_card",
    type: "get",
    dataType: "json",
    responseText:  {"title":"Recipe Card", 
                    "link":"recipe_card", 
                    "content":"This is a recipe", 
                    "rendered_content":"<p>This is a recipe</p>", 
                    "edited_at":null, 
                    "edited_by":"chef",
                    "tags":[],
                    "version":7}

});

$.mockjax({
    url: "/cards/__startCard",
    type: "get",
    dataType: "json",
    responseText:  {"title":null, 
                    "link":"__startCard", 
                    "content":"This is the start card", 
                    "rendered_content":"<p>This is the start card <a id='__startCardWikilink' href='#' class='wikilink'>wikilink</a></p>",
                    "edited_at":null, 
                    "edited_by":"admin",
                    "tags":[],
                    "version":1}

});

$.mockjax({
    url: "/cards/recipe_card/tags/",
    type:"get",
    dataType:"json",
    responseText: {"tags":[{"tag":"cooking",
                            "tagged_card":"recipe_card", 
                            "href":"/tags/cooking"},
                        {"tag":"how-to",
                            "tagged_card":"recipe_card", 
                            "href":"/tags/cooking"}],
                    "status":"success"
                    }
});

$.mockjax({
    url: "/cards/card_404/tags/",
    type:"get",
    dataType:"json",
    status:404,
    responseText: {"status":"failure", 
                   "reason":"No Card '404_card' found"}
});

$.mockjax({
    url: "/cards/brand_new_card",
    type: "get",
    dataType: "json",
    responseText:  {"title":"Brand New Card", 
                    "link":"brand_new_card", 
                    "content":null, 
                    "rendered_content":null, 
                    "edited_at":null, 
                    "edited_by":"chef",
                    "tags":[],
                    "version":7}

});

$.mockjax({
    url:"/cards/card_400",
    type: "put",
    datatype: "json",  
    response : function(settings){
        this.status=400;
        this.responseText= JSON.stringify({"status":"failure", 
                                      "reason":"resource uri does not match link in request"})
    }
});

$.mockjax({
    url:"/cards/card_404",
    type: "get",
    datatype: "json",  
    status:404,
    response: function(settings){
        this.responseText= JSON.stringify({"status":"failure", 
                                           "reason":"No Card '404_card' found"})
    }
});

$.mockjax({
    url:"/cards/card_500",
    type: "get",
    datatype: "json",  
    status:500,
    response: function(settings){
        this.responseText= JSON.stringify({"status":"failure", 
                                           "reason":"Something went badly wrong"})
    }
});

$.mockjax({
    url:"/cards/slow_card",
    type: "get",
    datatype: "json",
    responseTime: 750,
    response: function(settings){
        var now = new Date()
        this.responseText=  JSON.stringify({"title":"Slow Card",
                                            "link":"slow_card",
                                            "content":"This card is pretty slow",
                                            "rendered_content":"<p>This card is pretty slow</p>",
                                            "edited_at":now.toISOString(),
                                            "edited_by":"ghostinthemachine",
                                            "version":1,
                                            "authentication_status":"success"
                                            });
    }
});

QUnit.module("cardwiki ui tests", {
    beforeEach: function(){
        $("body").prepend("<div id='cardList' class='container' style='display:none'></div>");
        cw = new CardWiki();
        cw.cards[__startCard.link] = __startCard;
        cw.cards[recipeCard.link] = recipeCard;
    },
    afterEach: function(){
        $("#cardList").remove();
}});
                        
QUnit.test( "CardWiki init test", function(assert) {
    assert.deepEqual(cw.cards, [], "empty card array");
    assert.deepEqual(cw.editors, [], "empty editor array");
    assert,ok(cw.password == null, "no password");
    assert.ok(cw.username == null, "no username");
});

QUnit.test( "CardWiki edit __ Card", function(assert) {
    $('#cardList').append(__startCard.getHtml());
    cw.editCard('__startCard');
        $("#cardList").show();
        assert.ok(cw.editors[__startCard.link] != null, "epic editor exists");
        assert.ok(!$("#title_"+ __startCard.link).is(":visible"), "title is not showing");
        assert.ok(!$("#titleEditor_"+ __startCard.link).is(":visible"), "title editor is not showing");
        assert.ok(!$("#content_"+ __startCard.link).is(":visible"), "content is not showing");
        assert.ok(!$("#editButton_"+ __startCard.link).is(":visible"), "edit button is not showing");
        assert.ok($("#saveButton_"+ __startCard.link).is(":visible"),"save button is showing");
        assert.ok($("#cancelCardEditButton_"+ __startCard.link).is(":visible"),"cancel edit button is showing"); 
        assert.ok($("#editor_"+__startCard.link).is(":visible"),"editor is showing");
});

QUnit.test( "CardWiki edit Card", function(assert) {
    $('#cardList').append(recipeCard.getHtml());
    cw.editCard(recipeCard.link);

        $("#cardList").show();
        assert.ok(cw.editors[recipeCard.link] != null, "epic editor exists");
        assert.ok(!$("#title_"+ recipeCard.link).is(":visible"), "title is not showing");
        assert.ok($("#titleEditor_"+ recipeCard.link).is(":visible"), "title editor is showing");
        assert.ok(!$("#content_"+ recipeCard.link).is(":visible"), "content is not showing");
        assert.ok(!$("#editButton_"+ recipeCard.link).is(":visible"), "edit button is not showing");
        assert.ok($("#saveButton_"+ recipeCard.link).is(":visible"),"save button is showing");
        assert.ok($("#cancelCardEditButton_"+ recipeCard.link).is(":visible"),"cancel edit button is showing"); 
        assert.ok($("#editor_"+recipeCard.link).is(":visible"),"editor is showing");
});

QUnit.test( "CardWiki cancel edit Card", function(assert) {
    $('#cardList').append(recipeCard.getHtml());
    cw.editCard(recipeCard.link);

        $("#cardList").show();
        assert.ok(cw.editors[recipeCard.link] != null, "epic editor exists");
        cw.cancelEditCard(recipeCard.link);
        assert.ok(cw.editors[recipeCard.link] == null, "editor removed from editor pool");
        assert.ok($("div.card_title_holder > span#title_"+ recipeCard.link).is(":visible"), "title is showing");
        assert.ok(!$("#titleEditor_"+ recipeCard.link).is(":visible"), "title editor is not showing");
        assert.ok($("#content_"+ recipeCard.link).is(":visible"), "content is showing");
        assert.ok($("#editButton_"+ recipeCard.link).is(":visible"), "edit button is showing");
        assert.ok(!$("#saveButton_"+ recipeCard.link).is(":visible"),"save button is not showing");
        assert.ok(!$("#cancelCardEditButton_"+ recipeCard.link).is(":visible"),"cancel edit button is not showing"); 
        assert.ok(!$("#editor_"+recipeCard.link).is(":visible"),"editor is not showing");

});

QUnit.test( "CardWiki remove Card", function(assert) {

    $('#cardList').append(recipeCard.getHtml());
    cw.editCard(recipeCard.link);
        $("#cardList").show();
        cw.removeCard(recipeCard.link);
        assert.ok(cw.editors[recipeCard.link] == null, "no editor");
        assert.ok(cw.cards[recipeCard.link] == null, "no card");

});

QUnit.test( "CardWiki save card", function(assert) {    
    cw.username = "test";
    cw.password = "test";
    $('#cardList').append(recipeCard.getHtml());
    $("#cardList").show();        
    cw.editCard(recipeCard.link);
    cw.editors[recipeCard.link].importFile('cardWiki_'+recipeCard.link, "totally different content, man");
    var done = assert.async();        
    cw.saveCard(recipeCard.link, function(){   
        assert.equal(cw.cards[recipeCard.link].content, "totally different content, man", "content appears updated");
        assert.equal(cw.cards[recipeCard.link].rendered_content, marked("totally different content, man"), "content appears rendered");
        assert.equal(cw.editors[recipeCard.link], null, "editor removed from editor pool");
        assert.ok($("div.card_title_holder > span#title_"+ recipeCard.link).is(":visible"), "title is showing");
        assert.ok(!$("#titleEditor_"+ recipeCard.link).is(":visible"), "title editor is not showing");
        assert.ok($("#content_"+ recipeCard.link).is(":visible"), "content is showing");
        assert.ok($("#editButton_"+ recipeCard.link).is(":visible"), "edit button is showing");
        assert.ok(!$("#saveButton_"+ recipeCard.link).is(":visible"),"save button is not showing");
        assert.ok(!$("#cancelCardEditButton_"+ recipeCard.link).is(":visible"),"cancel edit button is not showing"); 
        assert.ok(!$("#editor_"+recipeCard.link).is(":visible"),"editor is not showing");
        done()
    });    
});

QUnit.test("CardWiki save card 400 error", function(assert){
    cw.cards[card400.link] = card400;
    cw.username = "test";
    cw.password = "test";
    $('#cardList').append(card400.getHtml());
    $("#cardList").show();        
    cw.editCard(card400.link);
    cw.editors[card400.link].importFile('cardWiki_'+card400.link, "totally different content, man");
    var done = assert.async();
    cw.saveCard(card400.link, function(){
            assert.ok($("#editor_"+card400.link).is(":visible"),"editor is showing");
            assert.equal("<p><b>Something has gone wrong, try again in a bit</b></p>", $("#announcements_"+card400.link).html(), "expected announcement");
        done();
    });
});

QUnit.test("CardWiki get card", function(assert){
    cw.cards[recipeCard.link] = null;
    $('#cardList').append(__startCard.getHtml());
    $("#cardList").show();  
    var done = assert.async();
    cw.getCard("#card___startCard", recipeCard.link, function(){
        assert.ok($("#card_"+recipeCard.link).length, "recipe card exists");    
        assert.ok($("div.card_title_holder > span#title_"+ recipeCard.link).is(":visible"), "title is showing");
        assert.ok(!$("#titleEditor_"+ recipeCard.link).is(":visible"), "title editor is not showing");
        assert.ok($("#content_"+ recipeCard.link).is(":visible"), "content is showing");
        assert.ok($("#editButton_"+ recipeCard.link).is(":visible"), "edit button is showing");
        assert.ok(!$("#saveButton_"+ recipeCard.link).is(":visible"),"save button is not showing");
        assert.ok(!$("#cancelCardEditButton_"+ recipeCard.link).is(":visible"),"cancel edit button is not showing"); 
        assert.ok(!$("#editor_"+recipeCard.link).is(":visible"),"editor is not showing");
        done();
    });
});

QUnit.test("CardWiki get card, first card", function(assert){
    cw.cards[recipeCard.link] = null;
    cw.cards[__startCard.link] = null;
    $("#cardList").show();  
    var done = assert.async();
    cw.getCard(null, __startCard.link, function(){
        assert.ok($("#card_"+__startCard.link).length, "__start card exists");    
        assert.ok(!$("div.card_title_holder > span#title_"+ recipeCard.link).is(":visible"), "title is not showing");
        assert.ok(!$("#titleEditor_"+ __startCard.link).is(":visible"), "title editor is not showing");
        assert.ok($("#content_"+ __startCard.link).is(":visible"), "content is showing");
        assert.ok($("#editButton_"+ __startCard.link).is(":visible"), "edit button is showing");
        assert.ok(!$("#saveButton_"+ __startCard.link).is(":visible"),"save button is not showing");
        assert.ok(!$("#cancelCardEditButton_"+ __startCard.link).is(":visible"),"cancel edit button is not showing"); 
        assert.ok(!$("#editor_"+__startCard.link).is(":visible"),"editor is not showing");
        done();
    });
});

QUnit.test("CardWiki get new card", function(assert){
    cw.cards[recipeCard.link] = null;
    $('#cardList').append(__startCard.getHtml());
    $("#cardList").show();  
    var done = assert.async();
    var brandNewCardLink = "brand_new_card";
    cw.getCard("#card___startCard", brandNewCardLink, function(){
        assert.ok($("#card_"+brandNewCardLink).length, "recipe card exists"); 
        assert.notEqual(cw.cards[brandNewCardLink], null);
        assert.ok(!$("div.card_title_holder > span#title_"+ brandNewCardLink).is(":visible"), "title is Not showing");
        assert.ok($("#titleEditor_"+ brandNewCardLink).is(":visible"), "title editor is showing");
        assert.ok(!$("#content_"+ brandNewCardLink).is(":visible"), "content is not showing");
        assert.ok(!$("#editButton_"+ brandNewCardLink).is(":visible"), "edit button is not showing");
        assert.ok($("#saveButton_"+ brandNewCardLink).is(":visible"),"save button is showing");
        assert.ok($("#cancelCardEditButton_"+ brandNewCardLink).is(":visible"),"cancel edit button is showing"); 
        assert.ok($("#editor_"+brandNewCardLink).is(":visible"),"editor is showing");
        done();
    });
});

QUnit.test("CardWiki get card twice", function(assert){
    cw.cards[recipeCard.link] = null;
    $('#cardList').append(__startCard.getHtml());
    $("#cardList").show();  

    var done = assert.async();
    console.log("getting recipe card for first time");
    cw.getCard("#card___startCard", recipeCard.link, function(){
       console.log("inside second recipe card get");
       console.log($(".jumbotron.card"));
       assert.equal($(".jumbotron.card").length, 2, "1st get - only one recipe card exists");
       done();
    });
     var done2 = assert.async();
        console.log("getting start card for second time");
        cw.getCard("#card___startCard", recipeCard.link, function(){
            console.log("recipe card gotten for second time");
            console.log($(".jumbotron.card"));
            assert.equal($(".jumbotron.card").length, 2, "2nd get - only one recipe card exists 2");
            done2();
        });
        
});

QUnit.test("CardWiki get card twice, politely sequentially", function(assert){
    cw.cards[recipeCard.link] = null;
    $('#cardList').append(__startCard.getHtml());
    $("#cardList").show();  

    var done = assert.async();
    var done2 = assert.async();
    cw.getCard("#card___startCard", recipeCard.link, function(){
       assert.equal($(".jumbotron.card").length, 2, "1st get - only one recipe card exists");
        assert.equal(cw.cards[recipeCard.link].link, recipeCard.link, "recipe card is in the cached list, same title");
        assert.equal(cw.cards[recipeCard.link].content, recipeCard.content, "recipe card is in the cached list, same content");
        
        cw.getCard("#card___startCard", recipeCard.link, function(){
            assert.equal($(".jumbotron.card").length, 2, "2nd get - only one recipe card exists 2");
            done2();
        });
       done();
    });

        
});

QUnit.test("CardWiki get card 5 times 'impatient clicker'", function(assert){
    cw.cards[recipeCard.link] = null;
    $('#cardList').append(__startCard.getHtml());
    $("#cardList").show();  
    var asyncCounter = 0;
    var done = assert.async();
    console.log("getting recipe card for first time");
    cw.getCard("#card___startCard", recipeCard.link, function(){
       console.log("inside second recipe card get");
       console.log($(".jumbotron.card"));
       assert.equal($(".jumbotron.card").length, 2, "1st get - only one recipe card exists");
        done();
    });
     var done2 = assert.async();
        console.log("getting start card for second time");
        cw.getCard("#card___startCard", recipeCard.link, function(){
            console.log("recipe card gotten for second time");
            console.log($(".jumbotron.card"));
            assert.equal($(".jumbotron.card").length, 2, "2nd get - only one recipe card exists");
            done2();
        });
     var done3 = assert.async();
        console.log("getting start card for second time");
        cw.getCard("#card___startCard", recipeCard.link, function(){
            console.log("recipe card gotten for second time");
            console.log($(".jumbotron.card"));
            assert.equal($(".jumbotron.card").length, 2, "3rd get - only one recipe card exists");
            done3();
        });
     var done4 = assert.async();
        console.log("getting start card for second time");
        cw.getCard("#card___startCard", recipeCard.link, function(){
            console.log("recipe card gotten for second time");
            console.log($(".jumbotron.card"));
            assert.equal($(".jumbotron.card").length, 2, "4th get - only one recipe card exists");
            done4();
        });
     var done5 = assert.async();
        console.log("getting start card for second time");
        cw.getCard("#card___startCard", recipeCard.link, function(){
            console.log("recipe card gotten for second time");
            console.log($(".jumbotron.card"));
            assert.equal($(".jumbotron.card").length, 2, "5th - only one recipe card exists");
            done5();
        });
});

QUnit.test("CardWiki get 404'd card", function(assert){
    cw.cards[recipeCard.link] = null;
    $('#cardList').append(__startCard.getHtml());
    $("#cardList").show();  
    var done = assert.async();
    var done2 = assert.async();
    var card404Link = "card_404";
    cw.getCard("#card___startCard", card404Link, function(){
        assert.equal($("#card_"+card404Link).length, 0, "404 card does not exist"); 
        assert.equal(cw.cards[card404Link], "error");
        assert.equal($("#card___startCard > div.announcements").html(), "<p><b>Something has gone very wrong, I can't find that card at all!</b></p>", "error announcement displayed in parent card");
        
        setTimeout(function(){
            assert.equal($("#card___startCard > div.announcements").html(), "", "announcements clear after about 10 seconds");
            done2();
        }, 11000);
        done();
    });
});

QUnit.test("CardWiki get 404'd card twice, sequentially", function(assert){
    cw.cards[recipeCard.link] = null;
    $('#cardList').append(__startCard.getHtml());
    $("#cardList").show();  
    var done = assert.async();
    var done2 = assert.async();
    var card404Link = "card_404";
    cw.getCard("#card___startCard", card404Link, function(){
        assert.equal($("#card_"+card404Link).length, 0, "404 card does not exist"); 
        assert.equal(cw.cards[card404Link], "error");
        assert.equal($("#card___startCard > div.announcements").html(), "<p><b>Something has gone very wrong, I can't find that card at all!</b></p>", "error announcement displayed in parent card");
        
        cw.getCard("#card___startCard", card404Link, function(){
            assert.equal($("#card_"+card404Link).length, 0, "404 card does not exist"); 
            assert.equal(cw.cards[card404Link], null);
            assert.equal($("#card___startCard > div.announcements").html(), "<p><b>Something has gone very wrong, I can't find that card at all!</b></p>", "error announcement displayed in parent card");
            done2();
        });        
        done();
    });
});

QUnit.test("CardWiki get 404'd card twice, simultaneously", function(assert){
    cw.cards[recipeCard.link] = null;
    $('#cardList').append(__startCard.getHtml());
    $("#cardList").show();  
    var done = assert.async();
    var done2 = assert.async();
    var card404Link = "card_404";
    cw.getCard("#card___startCard", card404Link, function(){
        assert.equal($("#card_"+card404Link).length, 0, "404 card does not exist"); 
        assert.equal(cw.cards[card404Link], "error");
        assert.equal($("#card___startCard > div.announcements").html(), "<p><b>Something has gone very wrong, I can't find that card at all!</b></p>", "error announcement displayed in parent card");      
        done();
    });
    cw.getCard("#card___startCard", card404Link, function(){
            assert.equal($("#card_"+card404Link).length, 0, "404 card does not exist"); 
            assert.equal(cw.cards[card404Link], null);
            assert.equal($("#card___startCard > div.announcements").html(), "<p><b>Something has gone very wrong, I can't find that card at all!</b></p>", "error announcement displayed in parent card");
            done2();
        }); 
});

QUnit.test("CardWiki get 500 error'd card", function(assert){
    cw.cards[recipeCard.link] = null;
    $('#cardList').append(__startCard.getHtml());
    $("#cardList").show();  
    var done = assert.async();
    var done2 = assert.async();
    var card500Link = "card_500";
    cw.getCard("#card___startCard", card500Link, function(){
        assert.equal($("#card_"+card500Link).length, 0, "404 card does not exist"); 
        assert.equal(cw.cards[card500Link], "error");
        assert.equal($("#card___startCard > div.announcements").html(), "<p><b>The server fell over, try again in a bit.  Give it room to breathe!!</b></p>", "error announcement displayed in parent card");
       
        setTimeout(function(){
            assert.equal($("#card___startCard > div.announcements").html(), "", "announcements clear after about 10 seconds");
            done2();
        }, 11000);
        done();
    });
});

QUnit.test("CardWiki load tags for recipe_card", function(assert){
    $('#cardList').append(__startCard.getHtml());
    $('#cardList').append(recipeCard.getHtml());
    recipeCard.viewMode();
    $("#cardList").show();  
    var done = assert.async();
    console.log($("#cardList").html());
    cw.getTags(recipeCard.link, function(){
        assert.equal($('#tags_' + recipeCard.link +"_tagsinput").children().length, 4, "correct number of tags present");
        $('#tags_' + recipeCard.link +"_tagsinput").children().each(function(index){
            var expected = ""
            if(index == 0){
                expected = "<span>cooking&nbsp;&nbsp;</span><a href=\"#\" title=\"Removing tag\">x</a>"
            } else if(index == 1){
                expected = "<span>how-to&nbsp;&nbsp;</span><a href=\"#\" title=\"Removing tag\">x</a>"
            }else if(index ==2){
                expected = "<input id=\"tags_recipe_card_tag\" value=\"\" data-default=\"add a tag\" style=\"width: 80px; color: rgb(102, 102, 102);\">"
            }else{
                //expected should be ""
            }
            assert.equal($(this).html(), expected, "comparing tag " + index);           
        });
        done();
    });
});

QUnit.test("CardWiki load tags for recipe_card twice, simultaneously", function(assert){
    $('#cardList').append(__startCard.getHtml());
    $('#cardList').append(recipeCard.getHtml());
    recipeCard.viewMode();
    $("#cardList").show();  
    var done = assert.async();
    cw.getTags(recipeCard.link, function(){
        assert.equal($('#tags_' + recipeCard.link +"_tagsinput").children().length, 4, "correct number of tags present");
        assert.equal($('#tagsBox_' + recipeCard.link).children().length, 2, "correct number of recipe tag inputs");

        
        $('#tags_' + recipeCard.link +"_tagsinput").children().each(function(index){
            var expected = ""
            if(index == 0){
                expected = "<span>cooking&nbsp;&nbsp;</span><a href=\"#\" title=\"Removing tag\">x</a>"
            } else if(index == 1){
                expected = "<span>how-to&nbsp;&nbsp;</span><a href=\"#\" title=\"Removing tag\">x</a>"
            }else if(index ==2){
                expected = "<input id=\"tags_recipe_card_tag\" value=\"\" data-default=\"add a tag\" style=\"width: 80px; color: rgb(102, 102, 102);\">"
            }else{
                //expected should be ""
            }
            assert.equal($(this).html(), expected, "comparing tag " + index);           
        });
        done();
    });
  
    var done2 = assert.async();
    cw.getTags(recipeCard.link, function(){
        assert.equal($('#tags_' + recipeCard.link +"_tagsinput").children().length, 4, "correct number of tags present");
        assert.equal($('#tagsBox_' + recipeCard.link).children().length, 2, "correct number of recipe tag inputs");
        $('#tags_' + recipeCard.link +"_tagsinput").children().each(function(index){
            var expected = ""
            if(index == 0){
                expected = "<span>cooking&nbsp;&nbsp;</span><a href=\"#\" title=\"Removing tag\">x</a>"
            } else if(index == 1){
                expected = "<span>how-to&nbsp;&nbsp;</span><a href=\"#\" title=\"Removing tag\">x</a>"
            }else if(index ==2){
                expected = "<input id=\"tags_recipe_card_tag\" value=\"\" data-default=\"add a tag\" style=\"width: 80px; color: rgb(102, 102, 102);\">"
            }else{
                //expected should be ""
            }
            assert.equal($(this).html(), expected, "comparing tag " + index);           
        });
        done2();
    });
});

QUnit.test("CardWiki load tags for non existent card", function(assert){
    $('#cardList').append(recipeCard.getHtml());
    recipeCard.viewMode();
    $("#cardList").show();  
    var done = assert.async();
    console.log($("#cardList").html());
    cw.getTags("card_404", function(){
        assert.ok($('#tags_' + recipeCard.link +"_tagsinput > div#tags_" + recipeCard.link + "_addTag"), "add tag div is there");
        assert.ok($('#tags_' + recipeCard.link +"_tagsinput > div.tags_clear"), "clear tag div is there");
        assert.equal($('#tags_' + recipeCard.link +"_tagsinput").children().length, 2, "correct number of tags present");
        done();
    });
});

QUnit.test("Card constructor", function(assert){
    var now = new Date()
    var cardJson = {
                        title: "New Title",
                        link: "new_title",
                        content: "test content",
                        rendered_content: "<p>test content</p>",
                        edited_at:now.toISOString(),
                        edited_by: "test user",
                        tags:[],
                        version:1
                    };
    var testCard = new Card(cardJson);
    assert.equal(testCard.title, cardJson.title, "titles match");
    assert.equal(testCard.link, cardJson.link, "links match");
    assert.equal(testCard.content, cardJson.content, "contents match");
    assert.equal(testCard.rendered_content, cardJson.rendered_content, "rendered contents match");
    assert.equal(testCard.edited_at, cardJson.edited_at, "edited_ats match");
    assert.equal(testCard.edited_by, cardJson.edited_by, "edited_bys match");
    assert.deepEqual(testCard.tags, [], "tags empty");
    assert.equal(testCard.version, cardJson.version, "versions match");    
    
    var cardJsonNoTags = {
                        title: "New Title",
                        link: "new_title",
                        content: "test content",
                        rendered_content: "<p>test content</p>",
                        edited_at:now.toISOString(),
                        edited_by: "test user",
                        version:1
                    };
    var testCard2 = new Card(cardJsonNoTags);
    assert.equal(testCard2.title, cardJsonNoTags.title, "titles match");
    assert.equal(testCard2.link, cardJsonNoTags.link, "links match");
    assert.equal(testCard2.content, cardJsonNoTags.content, "contents match");
    assert.equal(testCard2.rendered_content, cardJsonNoTags.rendered_content, "rendered contents match");
    assert.equal(testCard2.edited_at, cardJsonNoTags.edited_at, "edited_ats match");
    assert.equal(testCard2.edited_by, cardJsonNoTags.edited_by, "edited_bys match");
    assert.deepEqual(testCard2.tags, [], "tags empty");
    assert.equal(testCard2.version, cardJsonNoTags.version, "versions match");  
    
    var cardJsonTags = {
                        title: "New Title",
                        link: "new_title",
                        content: "test content",
                        rendered_content: "<p>test content</p>",
                        edited_at:now.toISOString(),
                        edited_by: "test user",
                        tags: [{"tag":"taggo",},{"tag":"poop"}],
                        version:1
                    };
    var testCard3 = new Card(cardJsonTags);
    assert.equal(testCard3.title, cardJsonTags.title, "titles match");
    assert.equal(testCard3.link, cardJsonTags.link, "links match");
    assert.equal(testCard3.content, cardJsonTags.content, "contents match");
    assert.equal(testCard3.rendered_content, cardJsonTags.rendered_content, "rendered contents match");
    assert.equal(testCard3.edited_at, cardJsonTags.edited_at, "edited_ats match");
    assert.equal(testCard3.edited_by, cardJsonTags.edited_by, "edited_bys match");
    assert.deepEqual(testCard3.tags, [], "tags empty");
    assert.equal(testCard3.version, cardJsonTags.version, "versions match");  
});

