function setFacultyInfoTable(faculty_name, num_matches) {
   return $.ajax({
        type:'POST',
        url:$SCRIPT_ROOT + "/faculty_search_query",
        data:{'faculty_name':faculty_name,
                'num_matches':num_matches},
        success:function(data) {
          $("#response-container").html(data);
          $('.read-more').each(initializeReadMore);
        },
        fail: function(response) {
          alert("failed");
        }
    });
}