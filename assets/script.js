$(document).ready(function() {
    // Adjust document structure
    $(".email, .phone, .residence, .birthdate").insertAfter(".name");
    $(".languages").next("ul").addClass("lang-menu").insertBefore("#toc");
    $("header").children("h3").wrapAll("<div class='contact'></div>");

    // Add icons
    $(".email").prepend('<i class="fa fa-envelope"></i>&emsp;');
    $(".phone").prepend('<i class="fa fa-phone"></i>&emsp;');
    $(".residence").prepend('<i class="fa fa-home"></i>&emsp;');
    $(".birthdate").prepend('<i class="fa fa-birthday-cake"></i>&emsp;');
    $("h1").each(function() {
        if ($(this).hasClass("fa")) {
            // prepend i tag to nav with this id
            var id = $(this).attr("id");
            var classes = $(this).attr("class");
            $("a#toc-" + id).prepend('<i class="' + classes + '"></i>&emsp;');
            $(this).prepend('<i class="' + classes + '"></i>&emsp;');
            $(this).removeClass();
        }
    });
});