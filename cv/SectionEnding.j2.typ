{% if entry_type in ["ReversedNumberedEntry"] %}
  ],
)
{% else %}
#if anschmiegcv_section_view_mode == "cards" {
  anschmiegcv_cards_render(layout: anschmiegcv_card_layout)
  anschmiegcv_cards_clear()
}
{% endif %}
#if anschmiegcv_section_view_mode == "timeline" {
  v({{ design.sections.space_between_regular_entries }} + {{ design.typography.line_spacing }})
}
#let anschmiegcv_card_columns = 1
#let anschmiegcv_card_layout = "one"
#let anschmiegcv_section_view_mode = "auto"
