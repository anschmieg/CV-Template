import markdownIt from "markdown-it";
import markdownItAttrs from "markdown-it-attrs";
import markdownItAnchor from "markdown-it-anchor";
import { fontAwesomePlugin, sectionPlugin } from "./markdownItPlugins";

/**
 * Reads the CV file based on the specified language.
 * @param {string} lang - The language of the CV file.
 * @param {function} callback - The callback function to handle the result.
 */
async function readMarkdown(lang) {
  try {
    const response = await fetch("cv-files/" + lang + ".md");
    const markdownContent = await response.text();
    return markdownContent;
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
}

/**
 * Renders the given markdown content using markdown-it library.
 * @param {string} markdownContent - The markdown content to be rendered.
 * @returns {string} - The rendered HTML content.
 */
function renderMarkdown(markdownContent) {
  var md = markdownIt()
    .use(markdownItAttrs)
    .use(markdownItAnchor, {
      slugify: (s) =>
        encodeURIComponent(String(s).trim().toLowerCase().replace(/\s+/g, "-")),
    })
    .use(sectionPlugin('h2', 'section', 'h3', 'subsection'))
    .use(fontAwesomePlugin);

  return md.render(markdownContent);
}

export { renderMarkdown, readMarkdown };
