$(document).ready(function () {
  var themeColor = 'rgb(' + $(":root").css("--theme-highlight") + ')';

  // mark current page
  var page = window.location.pathname.split("/").pop();
  $("a[href='" + page + "']").addClass("current");

  // Adjust document structure
  $(".email, .phone, .residence, .birthdate").insertAfter(".name");
  $(".lang").next("ul").addClass("lang-menu").insertBefore("#toc");
  $(".lang").remove();
  $("header").children("h3").wrapAll("<span class='contact'></span>");
  // wrap sections
  $(".page h1").each(function () {
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
      .wrapAll("<div class='entry'></div>")
      .children("ul")
      .first()
      .addClass("info");
  });

  // Add icons to contact info
  $(".email").prepend('<i class="fa fa-envelope"></i>&emsp;');
  $(".phone").prepend('<i class="fa fa-phone"></i>&emsp;');
  $(".residence").prepend('<i class="fa fa-home"></i>&emsp;');
  $(".birthdate").prepend('<i class="fa fa-birthday-cake"></i>&emsp;');

  // Set up section types
  $("h1").each(function () {
    // Wrap cards
    if ($(this).hasClass("cards")) {
      console.log("Wrapped cards.");
      $(this).nextUntil("h1").wrapAll("<div class='cards'></div>");
    }
    // Wrap timeline
    if ($(this).hasClass("timeline")) {
      console.log("Wrapped timeline.");
      $(this).nextUntil("h1").wrapAll("<div class='timeline-wrapper'><div class='timeline'></div></div>");
    }
    // Wrap skills
    if ($(this).hasClass("skills")) {
      console.log("Wrapped skills.");
      $(this).nextUntil("h1").wrapAll("<div class='skills'></div>");
    }
    // Add icons
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
      // remove class from heading to undo fa styling
      $(this).removeClass();
    }
  });

  // Cards
  $(".card .entry").each(function () {
    console.log("card");
    $(this).addBack().wrapAll("<div class='card-item'></div>");
  });

  // Skills
  var i = 1;
  $(".skills .entry").each(function () {
    // Each skill
    // var skill = $(this).children("h2");
    var skillLevel = $(this).children("h2").next("ul").children("li")[0]
      .innerHTML;
    var skillPercent = parseInt(
      $(this).children("h2").next("ul").children("li")[1].innerHTML
    );
    $(this).addBack().wrapAll("<div class='skill-item'></div>");
    $(this).prepend(
      '<div class="progress-bar" id="circle-' + i + '">' +
      '<div class="progress-label" id="label-' + i + '">' +
      skillLevel + '</div></div>'
    );
    // move progress bar to after skill name
    $(this).find(".progress-bar").insertAfter($(this).children("h2"));
    // Set up circle diagram
    $(this).find("#circle-" + i).circleProgress({
      value: Number(skillPercent / 100),
      size: 125,
      thickness: 10,
      reverse: true,
      startAngle: convertToRadians(-90),
      fill: {
        color: themeColor,
      },
      animation: {
        duration: 0 // load page without animation
      },
      lineCap: "round",
    });
    // .css("filter", "hue-rotate(0deg)");
    i++;
  });
  // On mouse over skill-item, animate skill circle diagram
  $(".skill-item").mouseenter(function () {
    $(this).find(".progress-bar").circleProgress({
      animation: {
        duration: 625,
        easing: "circleProgressEasing"
      }
    });
  });

  // fill footer for print
  $(".footer").attr("data-text", $("title").text());
});

// If no portrait picture, remove
function noPortrait() {
  $(".profile-picture").remove();
}

// Helper for skills
function convertToRadians(degree) {
  return degree * (Math.PI / 180);
}

// on media print, prepend online notice
function moveSubtitle() {
  $(".subtitle").prependTo(".page");
}
window.onbeforeprint = moveSubtitle;
window.onafterprint = function () {
  $(".subtitle").prependTo("header");
};

$.fn.isInViewport = function () {
  var elementTop = $(this).offset().top;
  var elementBottom = elementTop + $(this).outerHeight();
  var viewportTop = $(window).scrollTop();
  var viewportBottom = viewportTop + $(window).height();
  return elementBottom > viewportTop && elementTop < viewportBottom;
};

// run on every scroll
document.addEventListener('wheel', (event) => {
  // Trigger progress bars when section is in viewport
  $(".progress-bar").each(function () {
    var scrolled = $(this).data('scrolled') || 0;
    if (($(this).scrollTop() > $(this).offset().top - (window.screen.height) * 0.75)
      && $(this).isInViewport()
      && scrolled < 1) {
      scrolled += event.deltaY;
      $(this).data('scrolled', scrolled);
      $(this).circleProgress({
        animation: {
          duration: 1250
        },
      });
    }
  });
});