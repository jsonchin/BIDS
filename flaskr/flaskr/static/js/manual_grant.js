/**
 * grantSubmit just shows top k faculty matches for now
 */

function grantSubmit() {
//  $.ajax({
//        url:$SCRIPT_ROOT + "/manual_grant_submit",
//        type:'POST',
//        data:$('#manual-grant-form').serialize(),
//        success:function(){
//            document.getElementById("manual-grant-form").reset();
//            $("#form-submission-text").html("Form has been submitted successfully");
//            $("#form-submission-text").show(400, function() {
//                $("#form-submission-text").delay(3000).hide(400);
//            });
//        },
//        error:function() {
//            $("#form-submission-text").html("Form was not able to be submitted. Please try again.");
//            $("#form-submission-text").show(400, function() {
//                $("#form-submission-text").delay(3000).hide(400);
//            });
//        }
//    });

    d = {}
    d['grant_description'] = $("#inputDescription").val();
    d['grant_title'] = $("#inputGrantTitle").val();

    $.ajax({
        url:$SCRIPT_ROOT + "/grant_get_top_k_faculty",
        type:'POST',
        data:d,
        success:function(response){
            $("#top-k-faculty-matches-container").html(response);
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

