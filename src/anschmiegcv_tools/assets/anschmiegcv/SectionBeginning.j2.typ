{% set display_title = section_title.split('{')[0]|strip %}
== {{ display_title }}
{% if entry_type in ["ReversedNumberedEntry"] %}

#reversed-numbered-entries(
  [
{% endif %}
