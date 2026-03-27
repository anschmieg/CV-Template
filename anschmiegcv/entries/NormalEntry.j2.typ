{% if not design.entries.short_second_row %}
{% set first_row_lines = entry.date_and_location_column.splitlines()|length %}
{% if first_row_lines == 0 %} {% set first_row_lines = 1 %} {% endif %}
{% else %}
{% set first_row_lines = entry.main_column.splitlines()|length %}
{% endif %}
{% set card_ns = namespace(title="", body=[]) %}
{% for raw_line in entry.main_column.splitlines() %}
{% set trimmed = raw_line.strip() %}
{% if not card_ns.title and trimmed %}
{% set card_ns.title = trimmed %}
{% elif card_ns.title %}
{% set card_ns.body = card_ns.body + [raw_line] %}
{% endif %}
{% endfor %}
{% set organization_line = "" %}
{% if entry.company is defined and entry.company %}
{% set organization_line = entry.company %}
{% elif entry.institution is defined and entry.institution %}
{% set organization_line = entry.institution %}
{% elif entry.position is defined and entry.position %}
{% set organization_line = entry.position %}
{% endif %}
{% set card_score = namespace(value=0.0) %}
{% if card_ns.title %}
{% set card_score.value = card_score.value + (card_ns.title|length / 34) + 0.6 %}
{% endif %}
{% for line in card_ns.body %}
{% if line.strip() %}
{% set card_score.value = card_score.value + (line|length / 42) + 0.32 %}
{% endif %}
{% endfor %}
{% if organization_line %}
{% set card_score.value = card_score.value + (organization_line|length / 42) + 0.45 %}
{% endif %}
{% for line in entry.date_and_location_column.splitlines() %}
{% if line.strip() %}
{% set card_score.value = card_score.value + 0.28 %}
{% endif %}
{% endfor %}
{% set card_colspan = 1 %}
{% if card_score.value >= 9.8 %}
{% set card_colspan = 2 %}
{% endif %}
{% set card_meta = namespace(has_date=false) %}
{% for line in entry.date_and_location_column.splitlines() %}
{% if line.strip() %}
{% set card_meta.has_date = true %}
{% endif %}
{% endfor %}
#if anschmiegcv_section_view_mode == "cards" [
  #let anschmiegcv_card = [
{% if card_ns.title or organization_line or card_meta.has_date %}
    #align(center)[
{% if card_ns.title %}
      {{ card_ns.title|indent(6) }}
{% endif %}
{% if organization_line %}
      #linebreak()
      #text(fill: {{ design.colors.footer.as_rgb() }}, weight: 600)[#connection-with-icon("building")[{{ organization_line|indent(6) }}]]
{% endif %}
{% for line in entry.date_and_location_column.splitlines() %}
{% if line.strip() %}
      #linebreak()
      #text(fill: {{ design.colors.footer.as_rgb() }}, size: 0.85em)[{{ line|indent(6) }}]
{% endif %}
{% endfor %}
    ]
{% endif %}
{% for line in card_ns.body %}
    {{ line|indent(4) }}

{% endfor %}
  ]
  #anschmiegcv_cards_push(anschmiegcv_card, colspan: {{ card_colspan }})
] else [
  #regular-entry(
    [
{% for line in entry.main_column.splitlines()[:first_row_lines] %}
      {{ line|indent(6) }}

{% endfor %}
    ],
    [
{% for line in entry.date_and_location_column.splitlines() %}
      {{ line|indent(6) }}

{% endfor %}
    ],
{% if not design.entries.short_second_row %}
    main-column-second-row: [
{% for line in entry.main_column.splitlines()[first_row_lines:] %}
      {{ line|indent(6) }}

{% endfor %}
    ],
{% endif %}
    is_last_entry: {{ is_last_entry|lower }},
  )
]
