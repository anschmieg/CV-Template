{% set display_title = section_title.split('{')[0]|strip %}
{% set raw_title = section_title %}
{% set view_mode = "auto" %}
{% set card_columns = 1 %}
{% set card_layout = "one" %}
{# Auto-detect publication sections and enable cards mode #}
{% set is_publication_section = false %}
{% if section_content is defined and section_content %}
{% set first_entry = section_content[0] %}
{% if first_entry is not string %}
{% if first_entry.doi is defined or first_entry.authors is defined or first_entry.journal is defined or (first_entry.url is defined and first_entry.title is defined) %}
{% set is_publication_section = true %}
{% endif %}
{% endif %}
{% endif %}
{% if ".cards" in raw_title %}
{% set view_mode = "cards" %}
{% set card_columns = 2 %}
{% set card_layout = "two" %}
{% if ".cards-4" in raw_title %}
{% set card_columns = 4 %}
{% set card_layout = "four" %}
{% elif ".cards-3w" in raw_title %}
{% set card_columns = 4 %}
{% set card_layout = "three_weighted" %}
{% elif ".cards-3" in raw_title %}
{% set card_columns = 3 %}
{% set card_layout = "three_equal" %}
{% elif ".cards-2" in raw_title %}
{% set card_columns = 2 %}
{% set card_layout = "two" %}
{% elif ".cards-1" in raw_title %}
{% set card_columns = 1 %}
{% set card_layout = "one" %}
{% endif %}
{% elif is_publication_section %}
{# Auto-enable cards for publication sections with default layout #}
{% set view_mode = "cards" %}
{% set card_columns = 2 %}
{% set card_layout = "two" %}
{% elif ".list" in raw_title %}
{% set view_mode = "list" %}
{% elif ".timeline" in raw_title %}
{% set view_mode = "timeline" %}
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
