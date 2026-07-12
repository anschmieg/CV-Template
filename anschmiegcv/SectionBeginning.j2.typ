{% set display_title = section_title.split('{')[0]|strip %}
{% set raw_title = section_title %}
{% set view_mode = "auto" %}
{% set card_columns = 1 %}
{% set card_layout = "auto" %}
{% if ".cards" in raw_title %}
{% set view_mode = "cards" %}
{% if ".cards-4" in raw_title %}
{% set card_columns = 4 %}
{% set card_layout = "four" %}
{% elif ".cards-3w" in raw_title %}
{% set card_columns = 4 %}
{% set card_layout = "three-weighted" %}
{% elif ".cards-3" in raw_title %}
{% set card_columns = 3 %}
{% set card_layout = "three" %}
{% elif ".cards-2" in raw_title %}
{% set card_columns = 2 %}
{% set card_layout = "two" %}
{% elif ".cards-1" in raw_title %}
{% set card_columns = 1 %}
{% set card_layout = "one" %}
{% endif %}
{% elif ".list" in raw_title %}
{% set view_mode = "list" %}
{% elif ".timeline" in raw_title %}
{% set view_mode = "timeline" %}
{% endif %}
{% if ".pdf-list" in raw_title %}
{% set view_mode = "list" %}
{% endif %}
{% if view_mode == "auto" and entry_type in ["NormalEntry", "OneLineEntry"] %}
{% set view_mode = "cards" %}
{% endif %}
{% if view_mode == "cards" %}
{% set card_layout = cv_resolve_card_layout(section_entries, card_layout) %}
{% if card_layout == "four" %}
{% set card_columns = 4 %}
{% elif card_layout in ["three", "dynamic"] %}
{% set card_columns = 3 %}
{% elif card_layout in ["two", "three-weighted"] %}
{% set card_columns = 2 %}
{% else %}
{% set card_columns = 1 %}
{% endif %}
{% endif %}
#let anschmiegcv_section_view_mode = "{{ view_mode }}"
#let anschmiegcv_card_columns = {{ card_columns }}
#let anschmiegcv_card_layout = "{{ card_layout }}"
== {{ display_title }}
{% if entry_type in ["ReversedNumberedEntry"] %}

#reversed-numbered-entries(
  [
{% elif view_mode == "cards" %}

#anschmiegcv_cards_clear()
{% endif %}
