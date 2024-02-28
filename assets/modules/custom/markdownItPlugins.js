export function fontAwesomePlugin(md) {
  md.core.ruler.push("font_awesome", function (state) {
    state.tokens.forEach(function (token) {
      if (token.type === "inline" && token.children) {
        for (let i = token.children.length - 1; i >= 0; i--) {
          let child = token.children[i];
          if (child.type === "text") {
            let text = child.content;
            let match = text.match(/:fa-([a-z-]+):/);
            if (match) {
              let before = text.slice(0, match.index);
              let after = text.slice(match.index + match[0].length);
              let icon = new state.Token("html_inline", "", 0);
              icon.content = '<i class="fa fa-' + match[1] + '"></i>';

              if (before) {
                let beforeToken = new state.Token("text", "", 0);
                beforeToken.content = before;
                token.children.splice(i, 1, beforeToken, icon);
                i++;
              } else {
                token.children[i] = icon;
              }

              if (after) {
                let afterToken = new state.Token("text", "", 0);
                afterToken.content = after;
                token.children.splice(i + 1, 0, afterToken);
              }
            }
          }
        }
      }
    });
  });
}

function createSectionPlugin(tag, sectionClass) {
  return function(md) {
    let inSection = false;

    const defaultRender =
      md.renderer.rules.heading_open ||
      function (tokens, idx, options, env, self) {
        return self.renderToken(tokens, idx, options);
      };

    md.renderer.rules.heading_open = function (tokens, idx, options, env, self) {
      if (tokens[idx].tag === tag) {
        let result = "";
        // If this is the start of a new section, close the previous section
        if (inSection) {
          result += "</div>";
        }
        // Start a new section
        let classes = "";
        if (tokens[idx].attrs) {
          for (let i = 0; i < tokens[idx].attrs.length; i++) {
            if (tokens[idx].attrs[i][0] === "class") {
              classes = tokens[idx].attrs[i][1];
              break;
            }
          }
        }
        result +=
          '<div class="' +
          sectionClass +
          ' ' +
          classes +
          '">' +
          defaultRender(tokens, idx, options, env, self);
        inSection = true;
        return result;
      }
      return defaultRender(tokens, idx, options, env, self);
    };

    // Close the section at the end of the document, if one is open
    md.renderer.rules.eof = function (tokens, idx, options, env, self) {
      if (inSection) {
        inSection = false;
        return "</div>";
      }
      return "";
    };
  };
}

export const sectionPlugin = createSectionPlugin("h2", "section");
export const subSectionPlugin = createSectionPlugin("h3", "subsection");