$(document).ready(function() {
    $(".sidebar-li").on("click", function() {
        window.location.href = $(this).children("a").attr("href");
    });
});