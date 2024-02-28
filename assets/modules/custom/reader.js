import markdownIt from "markdown-it";
import markdownItAttrs from "markdown-it-attrs";
import markdownItAnchor from "markdown-it-anchor";

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


function setIcons(md) {
  const defaultRender = md.renderer.rules.heading_open || function(tokens, idx, options, env, self) {
    return self.renderToken(tokens, idx, options);
  };

  md.renderer.rules.heading_open = function (tokens, idx, options, env, self) {
    const token = tokens[idx];
    const classAttr = token.attrGet('class');

    if (classAttr && classAttr.includes('fa-')) {
      const iconClass = classAttr.split(' ').find(cls => cls.startsWith('fa-'));
      tokens[idx + 1].children.unshift({
        type: 'html_inline',
        content: `<i class="${iconClass}" style='font-style: unset;'></i> `,
      });
      token.attrSet('class', classAttr.replace(iconClass, '').trim());
    }

    return defaultRender(tokens, idx, options, env, self);
  };
}

/**
 * Splits the CV into sections based on h2 headings.
 * @param {string} markdownContent - The markdown content of the CV.
 * @returns {Array} - An array of sections, each containing the content and title.
 */
function wrapSections(markdownContent) {
  const sections = [];
  const tokens = markdownIt().parse(markdownContent, {});

  let currentSection = null;
  for (const token of tokens) {
    if (token.type === 'heading_open' && token.tag === 'h2') {
      currentSection = {
        title: '',
        content: '',
      };
    } else if (token.type === 'heading_close' && token.tag === 'h2') {
      sections.push(currentSection);
      currentSection = null;
    } else if (currentSection) {
      if (token.type === 'inline' && currentSection.title === '') {
        currentSection.title = token.content;
      }
      currentSection.content += markdownIt().renderer.render([token], {}, {}).trim();
    }
  }

  // Wrap sections in divs
  const wrappedSections = sections.map(section => `<div><h2>${section.title}</h2>${section.content}</div>`);

  return wrappedSections.join('');
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
      slugify: s => encodeURIComponent(String(s).trim().toLowerCase().replace(/\s+/g, '-'))
    });

  setIcons(md);

  return md.render(markdownContent);
}

export { renderMarkdown, readMarkdown };