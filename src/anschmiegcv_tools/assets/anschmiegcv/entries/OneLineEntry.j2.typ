{# OneLineEntry template - supports cards mode for label/details entries #}
{% set card_ns = namespace(title="", details="") %}
{% if entry.label is defined and entry.label %}
{% set card_ns.title = entry.label %}
{% elif entry.name is defined and entry.name %}
{% set card_ns.title = entry.name %}
{% elif entry.title is defined and entry.title %}
{% set card_ns.title = entry.title %}
{% endif %}
{% if entry.details is defined and entry.details %}
{% set card_ns.details = entry.details %}
{% elif entry.summary is defined and entry.summary %}
{% set card_ns.details = entry.summary %}
{% endif %}
{# Calculate card score for density estimation #}
{% set card_score = namespace(value=0.0) %}
{% if card_ns.title %}
{% set card_score.value = card_score.value + (card_ns.title|length / 34) + 0.6 %}
{% endif %}
{% if card_ns.details %}
{% set card_score.value = card_score.value + (card_ns.details|length / 50) + 0.8 %}
{% endif %}
{% set card_colspan = 1 %}
{% if card_score.value >= 9.8 %}
{% set card_colspan = 2 %}
{% endif %}
#if anschmiegcv_section_view_mode == "cards" [
  #let anschmiegcv_card = [
{% if card_ns.title %}
    #align(center)[
      #text(fill: {{ design.colors.name.as_rgb() }}, weight: 700)[{{ card_ns.title|indent(6) }}]
{% if card_ns.details %}
      #linebreak()
      #text(fill: {{ design.colors.footer.as_rgb() }}, size: 0.92em)[{{ card_ns.details|indent(6) }}]
{% endif %}
    ]
{% elif card_ns.details %}
    {{ card_ns.details|indent(4) }}
{% endif %}
  ]
  #anschmiegcv_cards_push(anschmiegcv_card, colspan: {{ card_colspan }})
] else [
  {{ entry.main_column }}
]
