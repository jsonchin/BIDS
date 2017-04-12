/**
 * grantSubmit just shows top k faculty matches for now
 */

function grantSubmit() {
    d = {}
    d['corpus'] = $("#inputDescription").val();

    $.ajax({
        url:$SCRIPT_ROOT + "/faculty_get_top_k_grants",
        type:'POST',
        data:d,
        success:function(response){
            $("#top-k-grant-matches-container").html(response);
            $("#top-k-grant-matches-container").find(".read-more").each(initializeReadMore);
        },
        error:function() {

        }
    });

}

$(document).ready(function() {
    $("#form-submit").on("click", function(e) {
         e.preventDefault(); //prevent form from automatically submitting
         grantSubmit();
    })
});

