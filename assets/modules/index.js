// Imports
import { readMarkdown, renderMarkdown } from "./custom/reader.js";
import { createNav } from "./custom/nav.js";
import { displayProfile } from "./custom/profile.js";

// Get language from URL
var url = new URL(window.location.href);
var lang = url.searchParams.get("lang");
if (!lang) {
  lang = "en";
}

// Expose language to the global scope
console.log("Selected language (from URL):", lang);
window.lang = lang;

// Assuming readMarkdown returns a Promise
readMarkdown(lang)
  .then(function (markdownContent) {
    var cvContent = renderMarkdown(markdownContent);
    document.getElementById("cv-content").innerHTML = cvContent;
    return displayProfile();  // Assuming displayProfile returns a Promise
  })
  .then(function (profile) {
    document.getElementById("profile").innerHTML = profile;
  })
  .catch(function (err) {
    console.error("Error:", err);
  });

// Create navigation menu in left panel
createNav(document.getElementById("left-panel"));
