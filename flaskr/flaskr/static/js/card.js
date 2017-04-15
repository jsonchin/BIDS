//https://codepen.io/maxds/pen/jgeoA
var showChar = 400;
var ellipsis = "...";
var moretext = "Show more >";
var lesstext = "Show less";

function initializeReadMore () {
    var content = $(this).html();

    var showChar = parseInt($(this).data("show-n-char"));

    if(content.length > showChar) {

        var c = content.substr(0, showChar);
        var h = content.substr(showChar, content.length - showChar);

        var html = c + '<span class="moreellipses">' + ellipsis +
            '&nbsp;</span><span class="morecontent"><span class="other-content">' + h
            + '</span>&nbsp;&nbsp;<a class="morelink">' + moretext + '</a></span>';

        $(this).html(html);
    }
}


//http://stackoverflow.com/questions/203198/event-binding-on-dynamically-created-elements
$(document).on("click", ".morelink", function() { //use delegation
    if($(this).hasClass("less")) {
        $(this).removeClass("less");
        $(this).html(moretext);
    } else {
        $(this).addClass("less");
        $(this).html(lesstext);
        $(this).parent().parent().parent().parent().css("height", "auto");
    }
    $(this).parent().prev().toggle();
    $(this).prev().toggle();
    return false;
});

$(document).ready(function () {
    $('.read-more').each(initializeReadMore);
});