{% set date_blocks = cv_parse_styled_blocks(entry.date_and_location_column, design) %}
{% set main_blocks = cv_parse_styled_blocks(entry.main_column, design) %}
{% set main_template = cv_entry_main_template(entry, design) %}
{% set header_count = cv_count_header_lines(main_template) %}
{% if header_count == 0 and main_blocks %}
{% set header_count = 1 %}
{% endif %}
#timeline-education-entry(
  [
{% for block in date_blocks %}
{% if block.type == "line" %}
    {% for segment in block.segments %}
    {% set text_options = cv_typst_text_options(segment.style, default_color=design.colors.footer.as_rgb(), default_size="0.85em") %}
    #text({{ text_options }})[{{ segment.text|indent(6) }}]
    {% endfor %}
{% else %}
    {% set block_options = cv_typst_text_options(block.style) %}
    {% if block_options %}
    {% if is_header_line %}
    #text({{ block_options }})[{{ block.text|indent(6) }}]
    {% else %}
    #pad(left: 0.18cm)[#text({{ block_options }})[{{ block.text|indent(6) }}]]
    {% endif %}
    {% else %}
    {% if is_header_line %}
    {{ block.text|indent(4) }}
    {% else %}
    #pad(left: 0.18cm)[{{ block.text|indent(6) }}]
    {% endif %}
    {% endif %}
{% endif %}
{% if not loop.last %}
    #linebreak()
{% endif %}
{% endfor %}
  ],
  [
{% if main_blocks %}
{% set primary_block = main_blocks[0] %}
{% if primary_block.type == "line" %}
    {% for segment in primary_block.segments %}
    {% set text_options = cv_typst_text_options(segment.style, default_color=(design.colors.body.as_rgb() if header_count > 1 else design.colors.headline.as_rgb()), default_weight=600) %}
    #text({{ text_options }})[
      {{ segment.text|indent(6) }}
    ]
    {% endfor %}
{% else %}
    {% set block_options = cv_typst_text_options(primary_block.style) %}
    {% if block_options %}
    #text({{ block_options }})[{{ primary_block.text|indent(6) }}]
    {% else %}
    {{ primary_block.text|indent(4) }}
    {% endif %}
{% endif %}
{% endif %}
  ],
{% if main_blocks|length > 1 %}
  main-column-second-row: [
{% for block in main_blocks[1:] %}
{% set is_header_line = loop.index0 < (header_count - 1) %}
{% if block.type == "line" %}
{% if is_header_line %}
    {% for segment in block.segments %}
    {% set text_options = cv_typst_text_options(segment.style, default_color=(design.colors.headline.as_rgb() if is_header_line else none), default_weight=(500 if is_header_line else 400)) %}
    #text({{ text_options }})[
      {{ segment.text|indent(6) }}
    ]
    {% endfor %}
{% else %}
    #pad(left: 0.18cm)[
    {% for segment in block.segments %}
    {% set text_options = cv_typst_text_options(segment.style, default_color=(design.colors.headline.as_rgb() if is_header_line else none), default_weight=(500 if is_header_line else 400)) %}
    #text({{ text_options }})[
      {{ segment.text|indent(6) }}
    ]
    {% endfor %}
    ]
{% endif %}
{% else %}
    {% set block_options = cv_typst_text_options(block.style) %}
    {% if block_options %}
    {% if is_header_line %}
    #text({{ block_options }})[{{ block.text|indent(6) }}]
    {% else %}
    #pad(left: 0.18cm)[#text({{ block_options }})[{{ block.text|indent(6) }}]]
    {% endif %}
    {% else %}
    {% if is_header_line %}
    {{ block.text|indent(4) }}
    {% else %}
    #pad(left: 0.18cm)[{{ block.text|indent(6) }}]
    {% endif %}
    {% endif %}
{% endif %}
{% if not loop.last %}
    #linebreak()
{% endif %}
{% endfor %}
  ],
{% endif %}
  continue-line: {{ (not is_last_entry)|lower if is_last_entry is defined else "true" }},
)
