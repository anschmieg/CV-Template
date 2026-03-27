{% set ns = namespace(header="", body=[]) %}
{% for raw_line in entry.main_column.splitlines() %}
{% set trimmed = raw_line.strip() %}
{% if not ns.header and trimmed %}
{% set ns.header = trimmed %}
{% elif ns.header %}
{% set ns.body = ns.body + [raw_line] %}
{% endif %}
{% endfor %}
{% if "], " in ns.header and "[" in ns.header %}
{% set header_parts = ns.header.split("], ", 1) %}
{% set organization_line = header_parts[0] ~ "]" %}
{% set position_line = header_parts[1] %}
{% else %}
{% set header_parts = ns.header.rsplit(", ", 1) %}
{% if header_parts|length == 2 %}
{% set organization_line = header_parts[0] %}
{% set position_line = header_parts[1] %}
{% else %}
{% set organization_line = entry.company if entry.company is defined and entry.company else "" %}
{% set position_line = ns.header %}
{% endif %}
{% endif %}
{% set organization_plain = organization_line|replace("#strong[", "")|replace("#emph[", "") %}
{% if organization_plain[-1:] == "]" %}
{% set organization_plain = organization_plain[:-1]|trim %}
{% endif %}
{% set main_column_template = "" %}
{% set has_custom_main_column_template = false %}
{% if design.templates.experience_entry is defined and design.templates.experience_entry.model_fields_set is defined and "main_column" in design.templates.experience_entry.model_fields_set %}
{% set has_custom_main_column_template = true %}
{% endif %}
{% if has_custom_main_column_template and design.templates.experience_entry.main_column is defined and design.templates.experience_entry.main_column %}
{% set main_column_template = design.templates.experience_entry.main_column %}
{% endif %}
{% set position_style = "default" %}
{% if has_custom_main_column_template and main_column_template %}
{% if "**POSITION**" in main_column_template %}
{% set position_style = "bold" %}
{% elif "*POSITION*" in main_column_template %}
{% set position_style = "italic" %}
{% else %}
{% set position_style = "plain" %}
{% endif %}
{% endif %}
{% set organization_style = "default" %}
{% if has_custom_main_column_template and main_column_template %}
{% if "**COMPANY**" in main_column_template %}
{% set organization_style = "bold" %}
{% elif "*COMPANY*" in main_column_template %}
{% set organization_style = "italic" %}
{% else %}
{% set organization_style = "plain" %}
{% endif %}
{% endif %}
#timeline-entry(
  [
{% for line in entry.date_and_location_column.splitlines() %}
{% if loop.index0 == 0 %}
    {{ line|indent(4) }}
{% else %}
    #emph[{{ line|indent(4) }}]
{% endif %}

{% endfor %}
  ],
  [
{% if position_line %}
    #text(fill: {{ design.colors.name.as_rgb() }}, weight: {% if design.typography.bold.section_titles %}700{% else %}600{% endif %})[
{% if position_style == "bold" %}
      #strong[{{ position_line|indent(6) }}]
{% elif position_style == "italic" %}
      #emph[{{ position_line|indent(6) }}]
{% else %}
      {{ position_line|indent(6) }}
{% endif %}
    ]
{% elif organization_line %}
    #text(
      fill: {{ design.colors.footer.as_rgb() }},
      weight: {% if organization_style == "default" %}600{% else %}400{% endif %},
    )[
{% if organization_style == "bold" %}
      #strong[{{ organization_plain|indent(6) }}]
{% elif organization_style == "italic" %}
      #emph[{{ organization_plain|indent(6) }}]
{% else %}
      {{ organization_plain|indent(6) }}
{% endif %}
    ]
{% endif %}
  ],
{% if (position_line and organization_line) or ns.body|length > 0 %}
  main-column-second-row: [
{% if position_line and organization_line %}
    #text(
      fill: {{ design.colors.footer.as_rgb() }},
      weight: {% if organization_style == "default" %}600{% else %}400{% endif %},
    )[
{% if organization_style == "bold" %}
      #strong[{{ organization_plain|indent(6) }}]
{% elif organization_style == "italic" %}
      #emph[{{ organization_plain|indent(6) }}]
{% else %}
      {{ organization_plain|indent(6) }}
{% endif %}
    ]
{% endif %}
{% for line in ns.body %}
    {{ line|indent(4) }}

{% endfor %}
  ],
{% endif %}
  is_last_entry: {{ is_last_entry|lower }},
)
