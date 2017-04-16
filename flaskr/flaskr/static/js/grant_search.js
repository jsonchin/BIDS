$(document).ready(function() {
    $(document).on("click", ".grant-card-view-matches", function() {
        var linkHTML = $(this).html();
        if (linkHTML == "View faculty matches") {
            var matchesContainer = $(this).parent().children(".grant-card-view-matches-container");
            var descriptionContainer = matchesContainer.parent().children(".grant-card-desc");
            var span1 = descriptionContainer.children("span");
            //http://stackoverflow.com/questions/3442394/using-text-to-retrieve-only-text-not-nested-in-child-tags
            var descPart1 = span1.clone()    //clone the element
                            .children() //select all the children
                            .remove()   //remove all the children
                            .end()  //again go back to selected element
                            .text();
            var descPart2 = span1.find(".other-content").text();

            var title = matchesContainer.parent().children(".grant-card-title").text();

            var description = descPart1 + descPart2;

            $.ajax({
                type:'POST',
                url:$SCRIPT_ROOT + "/grant_get_top_k_faculty",
                data:{"grant_description":description,
                        "grant_title":title},
                success:function(data) {
                    $(matchesContainer).html(data);
                    matchesContainer.find('.read-more').each(initializeReadMore);
                },
                fail: function(response) {
                  alert("failed");
                }
            });
            $(this).html("Hide faculty matches");
            matchesContainer.css("padding-top", "10px");
        } else if (linkHTML == "Hide faculty matches") {
            $(this).parent().children(".grant-card-view-matches-container").hide();
            $(this).html("Show faculty matches");
        } else if (linkHTML == "Show faculty matches") {
            $(this).parent().children(".grant-card-view-matches-container").show();
            $(this).html("Hide faculty matches");
        }


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