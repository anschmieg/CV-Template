// Imports
import { readMarkdown, renderMarkdown } from "./custom/reader.js";
import { createLangMenu, createNav } from "./custom/nav.js";
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
    // Create navigation menu in left panel
    var leftPanel = document.getElementById("left-panel");
    createNav(leftPanel);

    return displayProfile();  // Assuming displayProfile returns a Promise
  })
  .then(function (profile) {
    // Create profile section
    document.getElementById("profile").innerHTML = profile;
  })
  .catch(function (err) {
    console.error("Error:", err);
  });

// Create language menu in left panel
createLangMenu(document.getElementById("left-panel"));
