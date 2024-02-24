// import node modules markdown-it and markdown-it-attrs
import markdownit from "markdown-it";
import markdownitAttrs from "markdown-it-attrs";

// check if node modules are working
console.log("markdown-it:", markdownit);
console.log("markdown-it-attrs:", markdownitAttrs);

var md = markdownit({
  html: true,
  linkify: true,
  typographer: true,
}).use(markdownitAttrs);

// Get language from URL
var url = new URL(window.location.href);
var lang = url.searchParams.get("lang");
if (!lang) {
  lang = "en";
}

// Log language
console.log("Selected language (from URL):", lang);

// Fetch and render CV
fetch("cv-files/" + lang + ".md")
  .then((response) => response.text())
  .then((markdownContent) => {
    var htmlContent = md.render(markdownContent);
    document.getElementById("cv-content").innerHTML = htmlContent;
  })
  .catch((error) => console.error("Error:", error));
