import markdownIt from "markdown-it";
import markdownItAttrs from "markdown-it-attrs";

/**
 * Reads the CV file based on the specified language.
 * @param {string} lang - The language of the CV file.
 * @param {function} callback - The callback function to handle the result.
 */
function readMarkdown(lang, callback) {
  fetch("cv-files/" + lang + ".md")
    .then((response) => response.text())
    .then((markdownContent) => callback(null, markdownContent))
    .catch((error) => callback(error));
}

/**
 * Renders the given markdown content using markdown-it library.
 * @param {string} markdownContent - The markdown content to be rendered.
 * @returns {string} - The rendered HTML content.
 */
function renderMarkdown(markdownContent) {
  var md = markdownIt().use(markdownItAttrs);
  return md.render(markdownContent);
}

// Expose the functions to the global scope
export { renderMarkdown, readMarkdown };
