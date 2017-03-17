function grantSubmit() {
  $.ajax({
        url:$SCRIPT_ROOT + "/manual_grant_submit",
        type:'POST',
        data:$('#manual-grant-form').serialize(),
        success:function(){
            document.getElementById("manual-grant-form").reset();
            $("#form-submission-text").html("Form has been submitted successfully");
            $("#form-submission-text").show(400, function() {
                $("#form-submission-text").delay(3000).hide(400);
            });
        },
        error:function() {
            $("#form-submission-text").html("Form was not able to be submitted. Please try again.");
            $("#form-submission-text").show(400, function() {
                $("#form-submission-text").delay(3000).hide(400);
            });
        }
    });
}

$(document).ready(function() {
    $("#form-submit").on("click", function(e) {
         e.preventDefault(); //prevent form from automatically submitting
         grantSubmit();
    })
});

