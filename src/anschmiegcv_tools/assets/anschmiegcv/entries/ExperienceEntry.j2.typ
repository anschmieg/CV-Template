#timeline-entry(
  [
{% for line in entry.date_and_location_column.splitlines() %}
    {{ line|indent(4) }}

{% endfor %}
  ],
  [
{% for line in entry.main_column.splitlines() %}
    {{ line|indent(4) }}

{% endfor %}
  ],
)
