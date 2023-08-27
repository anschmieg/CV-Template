$(document).ready(function() {
    $(".blocker").css("visibility", "hidden");

    // Adjust document structure
    $(".email, .phone, .residence, .birthdate").insertAfter(".name");
    $(".languages").next("ul").addClass("lang-menu").insertBefore("#toc");

    // Add icons
    $(".email").prepend('<i class="fa fa-envelope"></i> ');
    $(".phone").prepend('<i class="fa fa-phone"></i> ');
    $(".residence").prepend('<i class="fa fa-home"></i> ');
    $(".birthdate").prepend('<i class="fa fa-birthday-cake"></i> ');
});