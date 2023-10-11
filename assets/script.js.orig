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
    // Each language
    // var lang = $(this).children("h2");
    var langLevel = $(this).children("h2").next("ul").children("li")[0]
      .innerHTML;
    var langPercent = parseInt(
      $(this).children("h2").next("ul").children("li")[1].innerHTML
    ) / 100;
    $(this).addBack().wrapAll("<div class='skill-item'></div>");
    $(this).append(
<<<<<<< HEAD
      '<div class="progress-bar circle"'
      // + ' data-percent="' +
      // langPercent +
      // '" data-name="' +
      // langLevel +
      // '" data-color="#aaa" data-duration="750"'
      + '></div>'
    );
    $(this).find(".progress-bar circle").circleProgress({
      value: langPercent,
      size: 100,
      thickness: 10,
      fill: {
        color: "#814141",
      },
      animation: {
        duration: 750,
      },
    });
    // Assign homogenized duration to progress bar
    // var duration = Math.round(
    //   Number($(this).find(".progress-bar").attr("data-duration"))
    //   / 100
    //   * Number($(this).find(".progress-bar").attr("data-percent"))
    // );
    // $(this).find(".progress-bar").attr("data-duration", duration);
    // Load progress bar
    // $(".progress-bar").loading();
    i++;
  });
  // On hover skill-item, animate skill circle diagram
  $(".skill-item").on("mouseenter", function () {
    // $(".progress-bar", this).loading();
    // $(this).find(".progress-bar").loading();
=======
      '<div class="progress-bar" id="circle-' + i + '"></div>'
    );
    // Set up circle diagram
    $(this).find("#circle-" + i).circleProgress({
      value: Number(langPercent / 100),
      size: 100,
      thickness: 10,
      reverse: true,
      startAngle: convertToRadians(-90),
      fill: {
        color: themeColor,
      },
      animation: {
        duration: 1200,
        easing: "circleProgressEasing"
      },
      lineCap: "round",
    });
    // .css("filter", "hue-rotate(0deg)");
    i++;
  });
  // On mouse over skill-item, animate skill circle diagram
  $(".skill-item").mouseenter(function () {
    $(this).find(".progress-bar").circleProgress();
>>>>>>> progress-bar
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
      $(this).circleProgress();
    }
  });

});