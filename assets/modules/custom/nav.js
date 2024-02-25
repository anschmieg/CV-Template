import $ from "jquery";

/**
 * Creates a navigation menu inside the specified container element.
 * @param {HTMLElement} container - The container element where the navigation menu will be created.
 */
function createLangMenu(container) {
  var langMenu = document.getElementById("lang-menu");
  createLangButtons(langMenu);
}

/**
 * Creates language buttons and appends them to the specified parent element.
 * @param {HTMLElement} parent - The parent element to which the language buttons will be appended.
 */
function createLangButtons(parent) {
  // Get content of cv-files directory
  fetch("cv-files/")
    .then((response) => response.text())
    .then((htmlContent) => {
      var parser = new DOMParser();
      var doc = parser.parseFromString(htmlContent, "text/html");
      var files = Array.from(doc.querySelectorAll("a")).map(
        (a) => a.textContent
      );

      // Filter out non-md files
      var mdFiles = files.filter((file) => file.endsWith(".md"));
      var languages = mdFiles.map((file) => file.split(".")[0]);

      // Create buttons for each language
      languages.forEach((lang) => {
        // Skip if lang is empty
        if (!lang) return;

        var button = document.createElement("button");
        button.className = "btn btn-primary lang-button";
        button.dataset.lang = lang;
        button.textContent = lang;
        button.onclick = function () {
          window.location.href = window.location.pathname + "?lang=" + lang;
        };
        parent.appendChild(button);
      });
    })
    .catch((error) => console.error("Error:", error));
}

function createNav(container) {
  // create a container for the navigation menu
  var nav = document.createElement("nav");
  nav.className = "nav";
  // Select all h2 elements on the page
  $("#cv-content")
    .find("h2")
    .each(function () {
      var div = document.createElement("div");
      div.style.width = "100%"; // Set the div width to 100%
      var anchor = document.createElement("a");
      anchor.textContent = this.textContent;
      anchor.href = "#" + this.id;

      // Add Bootstrap classes to the anchor
      anchor.className = "btn btn-block btn-secondary my-1";

      // Add the anchor to the div
      div.appendChild(anchor);
      nav.appendChild(div);
    });
  container.appendChild(nav);
}

// Export the functions
export { createLangMenu, createNav };
