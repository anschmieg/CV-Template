$(document).ready(function () {
  // Adjust document structure
  $(".email, .phone, .residence, .birthdate").insertAfter(".name");
  $(".lang").next("ul").addClass("lang-menu").insertBefore("#toc");
  $(".lang").remove();
  $("header").children("h3").wrapAll("<div class='contact'></div>");
  // wrap sections
  $("h1").each(function () {
    $(this)
      .nextUntil("h1, hr, .footer")
      .addBack()
      .wrapAll("<div class='section'></div>");
  });

  // wrap timeline entries
  $("h2").each(function () {
    $(this)
      .nextUntil("h2, h1, hr")
      .addBack()
      .wrapAll("<div class='entry'></div>");
  });

  // Add icons
  $(".email").prepend('<i class="fa fa-envelope"></i>&emsp;');
  $(".phone").prepend('<i class="fa fa-phone"></i>&emsp;');
  $(".residence").prepend('<i class="fa fa-home"></i>&emsp;');
  $(".birthdate").prepend('<i class="fa fa-birthday-cake"></i>&emsp;');
  $("h1").each(function () {
    if ($(this).hasClass("fa")) {
      // prepend i tag to nav with this id
      var thisId = $(this).attr("id");
      var thisClass = $(this).attr("class");
      var thisClass = $(this).attr("class").split(" ");
      var faClass = "";
      for (var i = 0; i < thisClass.length; i++) {
        if (thisClass[i].indexOf("fa") != -1) {
          var faClass = faClass + " " + thisClass[i];
        }
      }
      $("a#toc-" + thisId).prepend('<i class="' + faClass + '"></i> ');
      $(this).prepend('<i class="' + faClass + '"></i> ');
      // set up timeline
      if ($(this).hasClass("timeline")) {
        $(this).nextUntil("h1").wrapAll("<div class='timeline'></div>");
      }
      // set up skills
      if ($(this).hasClass("skills")) {
        $(this).nextUntil("h1").wrapAll("<div class='skills'></div>");
      }
      $(this).removeClass();
    }
  });

  // Circle diagrams
  var i = 1;
  $(".skills .entry").each(function () {
    // Each language
    var lang = $(this).children("h2");
    var langLevel = $(this).children("h2").next("ul").children("li")[0]
      .innerHTML;
    console.log(lang);
    console.log(langLevel);
    var langPercent = parseInt(
      $(this).children("h2").next("ul").children("li")[1].innerHTML
    );
    $(this).addBack().wrapAll("<div class='skill-item'></div>");
    $(this).append('<div class="progress-bar" data-percent="'+ 
        langPercent +'" data-name="'+ 
        langLevel +'" data-color="#aaa" data-duration="750"></div>'
    );
    $(".progress-bar").loading();
    i++;
  });
  // On hover skill-item, animate circle
    $(".skill-item").hover(
        function () {
            $(".progress-bar", this).attr("data-duration", "1000").loading();
        }
    );
    // dont animate after mouse out
    $(".skill-item").mouseleave(
        function () {
            $(".progress-bar", this).loading("stop");
        }
    );
});

// If no portrait picture, remove.
function noPortrait() {
  $(".profile-picture").remove();
}

// Helper for circles
function convertToRadians(degree) {
  return degree * (Math.PI / 180);
}
