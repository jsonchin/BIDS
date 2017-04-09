$(document).ready(function() {
    $(document).on("click", ".grant-card-view-matches", function() {
        var cardMatchesContainer = $(this).parent();
        var descriptionContainer = cardMatchesContainer.parent().children(".grant-card-desc");
        var span1 = descriptionContainer.children("span");
        //http://stackoverflow.com/questions/3442394/using-text-to-retrieve-only-text-not-nested-in-child-tags
        var descPart1 = span1.clone()    //clone the element
                        .children() //select all the children
                        .remove()   //remove all the children
                        .end()  //again go back to selected element
                        .text();
        var descPart2 = span1.find(".other-content").text();

        var title = cardMatchesContainer.parent().children(".grant-card-title").text();

        var description = descPart1 + descPart2;
        cardMatchesContainer.css("margin-top", "2vh");

        $.ajax({
            type:'POST',
            url:$SCRIPT_ROOT + "/grant_get_top_k_faculty",
            data:{"grant_description":description,
                    "grant_title":title},
            success:function(data) {
                $(cardMatchesContainer).html(data);
            },
            fail: function(response) {
              alert("failed");
            }
        });
    });

    $("#show-more-grants-btn").on("click", function() {
        $.ajax({
            type:'POST',
            url:$SCRIPT_ROOT + "/get_k_more_grants",
            data:{"offset":$("#grant-card-container").children().length},
            success:function(data) {
                $(data).appendTo("#grant-card-container")
                        .children(".grant-card-desc")
                        .children(".read-more")
                        .each(initializeReadMore);
            },
            fail: function(response) {
              alert("failed");
            }
        });
    });
});