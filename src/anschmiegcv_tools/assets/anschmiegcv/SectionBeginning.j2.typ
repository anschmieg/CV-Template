{% set display_title = section_title.split('{')[0]|strip %}
{% set raw_title = section_title %}
{% set view_mode = "auto" %}
{% if ".cards" in raw_title %}
{% set view_mode = "cards" %}
{% elif ".list" in raw_title %}
{% set view_mode = "list" %}
{% elif ".timeline" in raw_title %}
{% set view_mode = "timeline" %}
{% endif %}
#let anschmiegcv_section_view_mode = "{{ view_mode }}"
== {{ display_title }}
{% if entry_type in ["ReversedNumberedEntry"] %}

#reversed-numbered-entries(
  [
{% endif %}
