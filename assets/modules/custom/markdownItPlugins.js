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
export function sectionPlugin(tag, sectionClass, subTag, subSectionClass) {
  return function (md) {
    let inSection = false;
    let inSubSection = false;

    const defaultRender =
      md.renderer.rules.heading_open ||
      function (tokens, idx, options, env) {
        return md.renderer.renderToken(tokens, idx, options);
      };

    md.renderer.rules.heading_open = function (tokens, idx, options, env) {
      let result = '';
      if (tokens[idx].tag === tag) {
        if (inSubSection) {
          result += "</div>";
          inSubSection = false;
        }
        if (inSection) {
          result += "</div>";
        }
        inSection = true;
      } else if (tokens[idx].tag === subTag) {
        if (inSubSection) {
          result += "</div>";
        }
        inSubSection = true;
      }
      result += defaultRender(tokens, idx, options, env);
      return result;
    };

    md.renderer.rules.heading_close = function (tokens, idx, options, env) {
      let result = md.renderer.renderToken(tokens, idx, options);
      if (tokens[idx].tag === tag && inSection) {
        result += '<div class="' + sectionClass + '">';
      } else if (tokens[idx].tag === subTag && inSubSection) {
        result += '<div class="' + subSectionClass + '">';
      }
      return result;
    };

    // Close the section and subsection at the end of the document, if one is open
    md.renderer.rules.eof = function () {
      let result = "";
      if (inSubSection) {
        result += "</div>";
        inSubSection = false;
      }
      if (inSection) {
        result += "</div>";
        inSection = false;
      }
      return result;
    };
  };
}