// Imports
import { readMarkdown, renderMarkdown } from "./custom/reader.js";
import { createNav } from './custom/nav.js';
import { rearrangePage } from './custom/rearrange.js';

// Get language from URL
var url = new URL(window.location.href);
var lang = url.searchParams.get("lang");
if (!lang) {
  lang = "en";
}

// Expose language to the global scope
window.lang = lang;

// Log language
console.log("Selected language (from URL):", lang);

// Read and render CV
readMarkdown(lang, function (err, markdownContent) {
  if (err) {
    console.error("Error:", err);
    return;
  }

  var htmlContent = renderMarkdown(markdownContent);
  document.getElementById("cv-content").innerHTML = htmlContent;
});

// Create navigation menu in left panel
createNav(document.getElementById("left-panel"));

// Rearrange resume content
// ---------- Watch out! ----------
// This function moves elements around in the DOM statically.
rearrangePage();
