import markdownIt from 'markdown-it';

export default function fontAwesomePlugin(md) {
    const defaultRender = md.renderer.rules.text || function(tokens, idx, options, env, self) {
        return self.renderToken(tokens, idx, options);
    };

    md.renderer.rules.text = function (tokens, idx, options, env, self) {
        tokens[idx].content = tokens[idx].content.replace(/:fa-([a-z-]+):/g, '<i class="fa fa-$1"></i>');
        return defaultRender(tokens, idx, options, env, self);
    };
}
