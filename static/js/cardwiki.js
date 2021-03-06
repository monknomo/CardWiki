String.prototype.format = String.prototype.f = function() {
    var s = this
    var i = arguments.length;

    while (i--) {
        s = s.replace(new RegExp('\\{' + i + '\\}', 'gm'), arguments[i]);
    }
    return s;
};

$.fn.goTo = function() {
    console.log("scrolling to top");
    console.log($(this).offset().top);
    console.log($("#cardwiki-navbar-collapse-1").height());
    $('html, body').animate({
        scrollTop: $(this).offset().top - $("#cardwiki-navbar-collapse-1").height()
    }, 'fast');
    return this; // for chaining...
}

function bleeblorp(arg){
    $('html, body').animate({
        scrollTop: arg.offset().top - '70px'
    }, 'fast');
}

$.deselectAll = function() {
    if (window.getSelection) {
      if (window.getSelection().empty) {  // Chrome
        window.getSelection().empty();
      } else if (window.getSelection().removeAllRanges) {  // Firefox
        window.getSelection().removeAllRanges();
      }
    } else if (document.selection) {  // IE?
      document.selection.empty();
    }
}

function CardWiki(){
            this.cards = [];
            this.syntheticCards = [];
            this.editors = [];
            this.username = null;
            this.password = null;
            this.siteRoot = '/'
        }
        
CardWiki.prototype.getCard = function(currentCardSelector, link, callback){
    if(this.cards[link] != null){
        if(this.cards[link] === "loading"){
            var that = this;
            setTimeout(function(){
                that.getCard(currentCardSelector, link, callback);
            }, 1200);
        }else if(this.cards[link] == "error"){
            //server communications, halt until user tries again
            this.cards[link] = null;
            if(callback){
                callback();
            }
        }else{
            var targetCard = $("div#card_"+link);
            if (targetCard.length > 0){
                targetCard.goTo();
            }else{
            targetCard.waitUntilExists(function(){
                $("div#card_"+link).goTo();
                });
            }
            if(callback){
                callback();
            }
        }
    }else{
        var that = this;
        this.cards[link] = "loading";
        $.ajax({url:'/cards/' + link, 
                type:'GET', 
                dataType:'json',
                success: function(data){
                        console.log(data);                            
                            var card = new Card(data, false, that);
                            if(data.content == null){
                                that.addCard(currentCardSelector, card, true);    
                            }else{
                                that.addCard(currentCardSelector, card, false);    
                            }
                        that.getTags(link, callback);
                    },
                error: function(data){
                    that.cards[link] = "error";
                    if(data.status == 404){
                        $(currentCardSelector).filter(" > div.announcements").html("<p><b>Something has gone very wrong, I can't find that card at all!</b></p>");
                    }else{
                        $(currentCardSelector).filter(" > div.announcements").html("<p><b>The server fell over, try again in a bit.  Give it room to breathe!!</b></p>");
                    }
                    setTimeout(function(){$(currentCardSelector).filter(" > div.announcements").html("");},10000);
                    if(callback){
                        callback();
                    }
                }
            });
    }
}

CardWiki.prototype.addCard = function(currentCardSelector, card, editMode){
    editMode = typeof editMode !== 'undefined' ? editMode : false;
    if(card.synthetic){
        this.syntheticCards[card.link] = card;
    }else{
        this.cards[card.link] = card;
    }
    if(currentCardSelector){
        currentCardSelector.after(card.getHtml());
    }else{
        $("div#cardList").html(card.getHtml());
    }
    var that = this;
    $("div#card_"+card.link).waitUntilExists(function(){
        if(editMode){
            that.editCard(card.link);
        }else{                            
            card.viewMode();;
        }
    });         
}

CardWiki.prototype.editCard = function(link) {
    //link = fullLink.substring(7,fullLink.length - 1);
    
    var editor = null;
    if (this.editors[link] == null){
        editor = new EpicEditor({container:"editor_" + link, 
                                            basePath:'/static',
                                            autogrow:{minHeight:225, maxHeight:800, scroll:false},
                                            theme: {base: 'https://cdnjs.cloudflare.com/ajax/libs/epiceditor/0.2.2/themes/editor/epic-light.css',
                                            preview: 'https://cdnjs.cloudflare.com/ajax/libs/epiceditor/0.2.2/themes/editor/epic-light.css',
                                            editor: 'https://cdnjs.cloudflare.com/ajax/libs/epiceditor/0.2.2/themes/editor/epic-light.css'}});
         this.editors[link] = editor;
    }else{
        editor = this.editors[link];
    }
    editor.load();    
    if ( editor.getFiles('cardWiki_' + link) === undefined){
        editor.importFile('cardWiki_' + link, this.cards[link].content);
    }else{
        if( Date.parse(this.cards[link].edited_at) > Date.parse(editor.getFiles('cardWiki_' + link).modified) ){
            editor.importFile('cardWiki_' + link,this.cards[link].content);
        }else{
            editor.open('cardWiki_' + link);
        }        
    } 
    this.cards[link].editMode();    
}  

CardWiki.prototype.cancelEditCard = function(link){
   // var link = obj.id.substring(21);    
    delete this.editors[link];
    $("#editor_"+link).empty();
    this.cards[link].viewMode(this);;
}

CardWiki.prototype.removeCard = function(cardSelector){
    var link = cardSelector[0].id.substring(5);
    if(this.cards[link]){
        cardSelector.remove();
        this.editors[link] = null;
        this.cards[link] = null;
    }else{
        cardSelector.remove();
        this.editors[link] = null;
        this.syntheticCards[link] = null;
    }


}

CardWiki.prototype.requireLogin = function(callback, arg){
    console.log("requiring login");
}

CardWiki.prototype.saveCard = function(link, callback){
    //link = fullLink.substring(7,fullLink.length - 1);
    var editor = this.editors[link];
    editor.save();
    var content = editor.exportFile('cardWiki_'+link);	
    var newCard = new Card({title:null, 
                        link:link, 
                        content:content, 
                        rendered_content:null, 
                        edited_at:null, 
                        edited_by:this.username,
                        tags:[],
                        version:null}, false, this);
    if($("#titleEditorInput_"+link)[0]){
        newCard.display_title = $("#titleEditorInput_"+link)[0].value;
    }else{
        //consider whether cards need to have titles at all...
        newCard.display_title = link;
    }			
    //if(this.username!=null){
    //    newCard.username=this.username;
    //    newCard.password=this.password;
    //    newCard.edited_by=this.username;
    //}else{
    //    this.requireLogin();
    //    return;
    //}
    //perhaps we should just post to /cards/ as we don't know whether this exists or not
    var that = this;
    $.ajax({url:"/cards/"+link,
        type:'PUT',
        contentType:'application/json',
        dataType:'json',
        data:JSON.stringify(newCard),
        success: function(data){
                  if(data.status == "success"){
                        $("#announcements_"+link).hide();
                        link = data.link
                        card = new Card(data, false, that);
                        that.cards[link] = card;
                        card.viewMode(that);;
                        if(that.editors[link]!=null){   
                            that.editors[link].unload(function(){that.editors[link].remove('cardWiki_' + link)});
                            delete that.editors[link];                                      
                        }
                    } else {
                        that.requireLogin(that.saveCard,"/cards/" + link)
                    }
                    if(callback){
                        callback();
                    }
                },
        error: function(data){
            $("#announcements_"+link).html("<p><b>Something has gone wrong, try again in a bit</b></p>");
            $("#announcements_"+link).show();
            if(callback){
                callback();
            }
        }
        });
}

CardWiki.prototype.getTags = function(cardLink, callback){
    //var taggedCardTitle = this.linkable_title;
    $.ajax({url:'/cards/' + cardLink + '/tags/',
            type:'GET',
            dataType:'json',
            success: function(data){
                var tagInput = $('#tagsBox_' + cardLink + ' > input');
                tagInput.importTags('');
                if(data.tags == null || data.tags.length < 1){
                    //do nothing
                }else{
                    this.tags = data.tags;
                    var tagVals = "";
                    for( var i = 0; i < this.tags.length; i++){
                        if(tagVals == ""){
                            tagVals = this.tags[i].tag;
                        }else{
                            tagVals = tagVals + "," + this.tags[i].tag;
                        }
                    }
                    tagInput.importTags(tagVals);	                 
                }
                if(callback){
                    callback();
                }
            },
            error: function(data){
                if(callback){
                    callback();
                }
            }
            
    });
};

function listAllCards(){
    //$("#cardList").hide();
    //$("#admin").hide();
    //$("#queryDisplay").show();
    $.ajax({url:'/cards',
                type:'GET',
                success: function(data){
                    var tagCard = "<div id='card_{0}' class='jumbotron adminCard'>"+
                            "<div class='card_title_holder'>" +
                                "<button id='removeCard_{0}' type='button' class='btn btn-danger' onclick='removeCard(this)' style='float:right;'><span class='glyphicon glyphicon-remove'></span></button>" +
                                "<span id='title_{0}' class='adminCard_title'><h1>{2}</h1></span>" +
                                
                            "</div>" +
                            "<hr>" +
                            "<div style='height:1em;width:100%;clear:both;'></div>"+							
                            "<div id='content_{0}' class='adminCard_content'>{1}</div>"+  
                        "</div>";
                    //var cardList = "<div class='card_title_holder'><h1>Tag: "+tag+"</h1></div><ul>"
                    var cardList = "<ul>";
                    for(var i = 0; i < data.cards.length; i++){
                        cardList += "<li><a href='#card_{0}' onclick='appendCard(this, \"{1}\")'>{2}</a></li>".format(data.cards[i].linkable_title, data.cards[i].href, data.cards[i].display_title)
                    }
                    cardList += "</ul>";
                    console.log(cardList);
                    tagCard = tagCard.format("__adminAllCards", cardList, "All Cards");
                    console.log($("div#cardList div.card:first-child")[0]);
                    $("div#cardList div.card:first").before(tagCard); 
                    //$("#queryDisplay").html(tagCard);
                }
        });
}
        
 function Card(jsonData, synthetic, parent) {
    this.link= jsonData.link;
    if (this.link.slice(0,2) == "__"){
        this.display_title = "";
    }else{
        this.display_title = jsonData.display_title;
    }
    if (jsonData.content == null){            
        this.content = "";
        this.rendered_content = "";
    }else{
        this.content = jsonData.content;
        this.rendered_content = jsonData.rendered_content;
    }            
    this.edited_at = jsonData.edited_at;
    this.edited_by = jsonData.edited_by;
    //takes a seperate post to get these
    this.tags = [];
    this.version = jsonData.version;
    this.synthetic = synthetic
    this.parent = parent;
}

//This is for normal cards with a title.  Most cards are of this type        
Card.card_template = "<div id='card_{0}' class='jumbotron card' ondblclick='openEditor_dblclick(this)'>"+
                            "<div class='card_title_holder'>" +
                                "<span id='title_{0}' class='card_title'><h1><a href='{3}?cards={0}' onclick='appendCard(event, \"{0}\", \"{0}\")'>{2}</a></h1></span>" +
                                "<span id='titleEditor_{0}' class='cardTitleEditor input-group input-group-lg'><input id='titleEditorInput_{0}' type='text' class='form-control'value='{2}'></input></span>" +                                
                                "<span class='card-control-buttons'>"+
                                    "<button id='removeCard_{0}' type='button' class='btn btn-sm btn-danger hideCardButton' onclick='removeCard(this)'><span class='glyphicon glyphicon-remove'></span></button>" +
                                    "<button id='editButton_{0}' class='btn btn-primary btn-sm editCardButton' role='button' onclick='openEditor(this)'>Edit</button>"+
                                    "<button id='saveButton_{0}' class='btn btn-success btn-sm saveCardButton' role='button' onclick='saveCard(this)'>Save</button>"+
                                    "<button id='cancelCardEditButton_{0}' class='btn btn-sm cancelCardEditButton' role='button' onclick='cancelEdit(this)'>Cancel</button>"+                                    
                                "</span>" + 
                            "</div>" +
                            //"<hr>" +
                            "<div style='height:1em;width:100%;clear:both;'></div>"+	
                            "<div id='announcements_{0}' class='announcements'></div>"+
                            "<div id='content_{0}' class='card_content'>{1}</div>"+
                            "<div id='editor_{0}' class='epiceditor' style='margin-bottom:1em;'></div>" +
                            "<div class='cardBottomControls'>"+
                                "<div id='tagsBox_{0}' style='margin-bottom:.5em;width:100%'><input id='tags_{0}' type='text' ></input></div> " +
                                "<button id='deleteCardButton_{0}' class='btn btn-sm btn-danger deleteCardButton' role='button' onclick='deleteCard(this)'>Delete</button>"+
                            "</div>"+
                        "</div>";

//this is for special cards without a title, like the __startCard
Card.card_template_sans_title = "<div id='card_{0}' class='jumbotron card sanstitle' ondblclick='openEditor_dblclick(this)'>" +
                                        "<div>"+
                                            "<span class='card-control-buttons'>"+
                                                "<button id='removeCard_{0}' type='button' class='btn btn-sm btn-danger hideCardButton sanstitle' onclick='removeCard(this)'><span class='glyphicon glyphicon-remove'></span></button>" +
                                                "<button id='editButton_{0}' class='btn btn-primary btn-sm editCardButton sanstitle' role='button' onclick='openEditor(this)'>Edit</button>"+
                                                "<button id='saveButton_{0}' class='btn btn-success btn-sm saveCardButton sanstitle' role='button' onclick='saveCard(this)'>Save</button>"+
                                                "<button id='cancelCardEditButton_{0}' class='btn btn-sm cancelCardEditButton sanstitle' role='button' onclick='cancelEdit(this)'>Cancel</button>"+                                    
                                            "</span>" +
                                        "<div style='height:1em;clear:both;'></div>" +
                                        "<div id='announcements_{0}' class='announcements'></div>"+
                                        "<div id='content_{0}' class='card_content' >{1}</div>"+
                                        "<div id='editor_{0}' class='epiceditor' style='margin-bottom:1em;'></div>" +
                                        "<div class='cardBottomControls'>"+
                                            "<div id='tagsBox_{0}' style='margin-bottom:.5em;width:100%'><input id='tags_{0}' type='text' ></input></div> " +
                                            "<button id='deleteCardButton_{0}' class='btn btn-sm btn-danger deleteCardButton' role='button' onclick='deleteCard(this)'>Delete</button>"+
                                        "</div>"+

                                    "</div>";

//this is for displaying information that isn't stored in cards as though it were a card
Card.card_template_synthetic_card = "<div id='card_{0}' class='jumbotron card synthetic'>" +
                                        "<div>"+
                                            "<button id='removeCard_{0}' type='button' class='btn btn-danger' onclick='removeCard(this)' style='float:right;'><span class='glyphicon glyphicon-remove'></span></button></div>" +
                                        "<div style='height:1em;clear:both;'></div>" +
                                        "<div id='announcements_{0}' class='announcements'></div>"+
                                        "<div id='content_{0}' class='card_content' >{1}</div>"+
                                    "</div>";
                                    
Card.prototype.getHtml = function(){
    if(this.synthetic){
        return Card.card_template_synthetic_card.format(this.link, this.rendered_content);
    }else{
        if(this.link.slice(0,2) == "__"){
            return Card.card_template_sans_title.format(this.link, this.rendered_content);
        }else{
            return Card.card_template.format(this.link, this.rendered_content, this.display_title, this.parent.siteRoot);
        }
    }
};

Card.prototype.viewMode = function(){
    //card_'+this.link).show();
    var cardlink = this.link;
    $("div#content_"+ this.link).html(this.rendered_content);
    $('button#saveButton_'+this.link).hide();
    $('button#cancelCardEditButton_'+this.link).hide();
    $('button#deleteCardButton_'+this.link).hide();
    $('span#titleEditor_'+this.link).hide();
    $("span#title_"+ this.link).show();
    $("div#content_"+ this.link).show();
    $("button#editButton_"+ this.link).show();
    $("div#editor_"+this.link).hide();
    $('div#card_'+this.link).show();
    $("#removeCard_"+this.link).show();
    $("div#card_"+this.link).waitUntilExists(function(){$("div#card_"+cardlink).goTo()});
    var taggedCardTitle = this.link;
    if(!$('#tags_' + this.link + "_tagsinput").length){
        var that = this;
        $('#tags_' + this.link).tagsInput({
            height:'100%',
            width:'85%',
            overwriteTagInput: false,
            onRemoveTag:function(tag){that.deleteTag(tag);},
            onAddTag:function(tag){that.addTag(tag);},
            onClickTag:function(tag){that.tagClicked(tag);}
        });
    }
};

Card.prototype.editMode = function(){
    var cardlink = this.link;
    $.deselectAll();
    $("#title_"+ this.link).hide();
    $("#titleEditor_"+ this.link).show();
    $("#content_"+ this.link).hide();
    $("button#editButton_"+ this.link).hide();
    $("button#removeCard_"+this.link).hide();
    $("button#saveButton_"+ this.link).show();
    $("button#cancelCardEditButton_"+ this.link).show();  
$('button#deleteCardButton_'+this.link).show();    
    $("#editor_"+this.link).show();
    
    var cardSelector = $("div#card_"+this.link)
    //if(cardSelector.length>0){
    //    if(this.content=""){
    //        cardSelector.waitUntilExists(function(){cardSelector.goTo()});
    //    }
    //}else{
        cardSelector.waitUntilExists(function(){cardSelector.goTo()});
    //}

};

Card.prototype.deleteTag = function(tag, callback){
    $.ajax({url:"/cards/"+this.link+"/tags/"+tag,
        type:'DELETE',
        success: function(data){
                    if(callback){
                        callback();
                    }
                },
        error: function(data){
            console.log(data);
            if(callback){
                callback();
            }
        }
        });
};

Card.prototype.addTag = function(tag, callback){
    var newTag = {tags:[{tagged_card:this.link,tag:tag}]}
    $.ajax({url:"/cards/"+this.link+"/tags/",
        type:'POST',
        contentType:'application/json',
        dataType:'json',
        data:JSON.stringify(newTag),
        success: function(data){
                    if(callback){
                        callback();
                    }
                },
        error: function(data){
            console.log(data);
            if(callback){
                callback();
            }
        }
        });
};

Card.prototype.tagClicked = function(tag, callback){
    console.log(this);
    console.log(tag);
    var that = this;
    $.ajax({url:"/tags/"+tag,
        type:'GET',
        success: function(data){
                    console.log(data);
                    var syntheticCardContent = "<h1>Tag: {0}</h1><p><ul>{1}</ul></p>";
                    var listOfCards = ""
                    data.cards.forEach(function(element, index, array){
                        if(element.display_title)
                            listOfCards += "<li><a href='#cards_{0}' onClick=\"appendCard('__Tag_{0}', '{0}')\">{1}</a></li>".format(element.link, element.display_title);
                        else
                            listOfCards += "<li><a href='#cards_{0}' onClick=\"appendCard('__Tag_{0}', '{0}')\">{1}</a></li>".format(element.link, element.link);
                    });
                    console.log(listOfCards);
                    syntheticCardContent = syntheticCardContent.format(data.tag, listOfCards);
                    //console.log(syntheticCardContent);
                    console.log(listOfCards);
                    //var cardHtml = Card.card_template_synthetic_card.format("tag_"+tag, syntheticCardContent);
                    var cardOfTags = new Card({link:"__Tag_"+tag,display_title:"Tag: " + tag, content:syntheticCardContent, rendered_content:syntheticCardContent, edited_at:null, edited_by:'anonymous',version:1}, true, that.parent)
                    console.log(cardOfTags);
                    that.parent.addCard($("#card_"+that.link), cardOfTags, false);
                    if(callback){
                        callback();
                    }
                },
        error: function(data){
            console.log(data);
            if(callback){
                callback();
            }
        }
        });
}