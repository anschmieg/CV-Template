#if anschmiegcv_section_view_mode == "cards" [
  #let anschmiegcv_card = [
{% if entry.label is defined and entry.label %}
    #text(weight: 600)[{{ entry.label }}]
{% if entry.details is defined and entry.details %}
    #linebreak()
    #v(0.18em)
    {{ entry.details }}
{% endif %}
{% else %}
    {{ entry.main_column }}
{% endif %}
  ]
  #anschmiegcv_cards_push(anschmiegcv_card)
] else if anschmiegcv_section_view_mode == "list" [
  #block(
    below: {{ design.typography.line_spacing }},
  )[
    {{entry.main_column}}
  ]
] else [
  {{entry.main_column}}
]
