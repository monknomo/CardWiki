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
    console.log($(document).height());
    $('html, body').animate({
        scrollTop: $(this).offset().top
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
            this.cards = []
            this.editors = []
            this.username = null;
            this.password = null;
        }
        
CardWiki.prototype.getCard = function(currentCardId, link, callback){
    if(this.cards[link] != null){
        if(this.cards[link] === "loading"){
            var that = this;
            setTimeout(function(){
                that.getCard(currentCardId, link, callback);
            }, 1200);
        }else if(this.cards[link] == "error"){
            //server communications, halt until user tries again
            this.cards[link] = null;
            if(callback){
                callback();
            }
        }else{
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
                            var card = new Card(data);
                            that.cards[card.link] = card;
                            if(currentCardId){
                                $("#card_"+currentCardId).after(card.getHtml());
                            }else{
                                $("#cardList").html(card.getHtml());
                            }
                            $("div#card_"+card.link).waitUntilExists(function(){
                                if(data.content == null){
                                    //card.editMode();  
                                    that.editCard(link);
                                }else{                            
                                    card.viewMode();
                                    //card.loadTags();
                                }
                            });                         
                        if(callback){
                            callback();
                        }   
                    },
                error: function(data){
                    that.cards[link] = "error";
                    if(data.status == 404){
                        $(currentCardId + " > div.announcements").html("<p><b>Something has gone very wrong, I can't find that card at all!</b></p>");
                    }else{
                        $(currentCardId + " > div.announcements").html("<p><b>The server fell over, try again in a bit.  Give it room to breathe!!</b></p>");
                    }
                    setTimeout(function(){$(currentCardId + " > div.announcements").html("");},10000);
                    if(callback){
                        callback();
                    }
                }
            });
    }
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
    this.cards[link].viewMode();
}

CardWiki.prototype.removeCard = function(link){
    //var title = obj.id.substring(11);
    $("#card_"+link).remove();
    this.editors[link] = null;
    this.cards[link] = null;

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
                        version:null});
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
                        card = new Card(data);
                        that.cards[link] = card;
                        card.viewMode();
                        if(that.editors[link]!=null){   
                            that.editors[link].unload();
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
                $('#tagsBox_' + cardLink + ' > input').importTags('');
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
                    $('#tagsBox_' + cardLink + ' > input').importTags(tagVals);	                 
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
        
 function Card(jsonData) {
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
        }
        
Card.card_template = "<div id='card_{0}' class='jumbotron card' ondblclick='openEditor_dblclick(this)'>"+
                            "<div class='card_title_holder'>" +
                                "<button id='removeCard_{0}' type='button' class='btn btn-danger' onclick='removeCard(this)' style='float:right;'><span class='glyphicon glyphicon-remove'></span></button>" +
                                "<span id='title_{0}' class='card_title'><h1>{2}</h1></span>" +
                                "<span id='titleEditor_{0}' class='cardTitleEditor input-group input-group-lg'><input id='titleEditorInput_{0}' type='text' class='form-control'value='{2}'></input></span>" +
                            "</div>" +
                            //"<hr>" +
                            "<div style='height:1em;width:100%;clear:both;'></div>"+	
                            "<div id='announcements_{0}' class='announcements'></div>"+
                            "<div id='content_{0}' class='card_content'>{1}</div>"+
                            "<div id='editor_{0}' class='epiceditor' style='margin-bottom:1em;'></div>" +
                            "<div id='tagsBox_{0}' style='margin-bottom:.5em;'><input id='tags_{0}' type='text' ></input></div> " +
                            "<div><p class='card-control-buttons'>"+
                                "<a id='editButton_{0}' class='btn btn-primary btn-sm editCardButton' role='button' onclick='openEditor(this)'>Edit</a>"+
                                "<a id='saveButton_{0}' class='btn btn-success btn-sm saveCardButton' role='button' onclick='saveCard(this)'>Save</a>"+
                                "<a id='cancelCardEditButton_{0}' class='btn btn-sm cancelCardEditButton' role='button' onclick='cancelEdit(this)'>Cancel</a>"+
                                "</p>" +
                            "</div>"+
                        "</div>";

Card.card_template_sans_title = "<div id='card_{0}' class='jumbotron card' ondblclick='openEditor_dblclick(this)'>" +
                                        "<div>"+
                                            "<button id='removeCard_{0}' type='button' class='btn btn-danger' onclick='removeCard(this)' style='float:right;'><span class='glyphicon glyphicon-remove'></span></button></div>" +
                                        "<div style='height:1em;clear:both;'></div>" +
                                        "<div id='announcements_{0}' class='announcements'></div>"+
                                        "<div id='content_{0}' class='card_content' >{1}</div>"+
                                        "<div id='editor_{0}' class='epiceditor' style='margin-bottom:1em;'></div>" +
                                        "<div id='tagsBox_{0}' style='margin-bottom:.5em;width:100%'><input id='tags_{0}' type='text' ></input></div> " +
                                        "<div style='clear:both;'><p class='card-control-buttons'>"+
                                            "<a id='editButton_{0}' class='btn btn-primary btn-sm editCardButton' role='button' onclick='openEditor(this)'>Edit</a>"+
                                            "<a id='saveButton_{0}' class='btn btn-success btn-sm saveCardButton' role='button' onclick='saveCard(this)'>Save</a>"+
                                            "<a id='cancelCardEditButton_{0}' class='btn btn-sm cancelCardEditButton' role='button' onclick='cancelEdit(this)'>Cancel</a>"+
                                        "</p></div>"+
                                    "</div>";

Card.prototype.getHtml = function(){
    if(this.link.slice(0,2) == "__"){
        return Card.card_template_sans_title.format(this.link, this.rendered_content);
    }else{
        //var pretty_title = this.title.replace("_", " ");
        return Card.card_template.format(this.link, this.rendered_content, this.display_title);
    }
};

Card.prototype.viewMode = function(){
    //card_'+this.link).show();
    var cardlink = this.link;
    $("div#content_"+ this.link).html(this.rendered_content);
    $('a#saveButton_'+this.link).hide();
    $('a#cancelCardEditButton_'+this.link).hide();
    $('span#titleEditor_'+this.link).hide();
    $("span#title_"+ this.link).show();
    $("div#content_"+ this.link).show();
    $("a#editButton_"+ this.link).show();
    $("div#editor_"+this.link).hide();
    $('div#card_'+this.link).show();
    $("div#card_"+this.link).waitUntilExists(function(){$("div#card_"+cardlink).goTo()});
    var taggedCardTitle = this.link;
    if(!$('#tags_' + this.link + "_tagsinput").length){
        var that = this;
        $('#tags_' + this.link).tagsInput({
            height:'100%',
            width:'85%',
            overwriteTagInput: false,
            onRemoveTag:function(tag){that.deleteTag(tag);},
            onAddTag:function(tag){that.addTag( tag);},
            onClickTag:function(tag){that,tagClicked(taggedCardTitle);}
        });
    }
};

Card.prototype.editMode = function(){
    var cardlink = this.link;
    $.deselectAll();
    $("#title_"+ this.link).hide();
    $("#titleEditor_"+ this.link).show();
    $("#content_"+ this.link).hide();
    $("#editButton_"+ this.link).hide();
    $("#saveButton_"+ this.link).show();
    $("#cancelCardEditButton_"+ this.link).show();    
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

Card.prototype.deleteTag = function(tag){
    console.log(tag);
};

Card.prototype.addTag = function(tag){
    console.log(tag);
};

Card.prototype.tagClicked = function(tag){
    console.log(tag);
}