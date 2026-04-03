{% set main_column_template = "" %}
{% set has_custom_main_column_template = false %}
{% if design.templates.education_entry is defined and design.templates.education_entry.model_fields_set is defined and "main_column" in design.templates.education_entry.model_fields_set %}
{% set has_custom_main_column_template = true %}
{% endif %}
{% if has_custom_main_column_template and design.templates.education_entry.main_column is defined and design.templates.education_entry.main_column %}
{% set main_column_template = design.templates.education_entry.main_column %}
{% endif %}

{# Determine what goes in main-column (first column) #}
{# Format: "AREA, DEGREE" using entry.area and entry.degree #}
{% set area_value = entry.area if entry.area is defined and entry.area else "" %}
{% set degree_value = entry.degree if entry.degree is defined and entry.degree else "" %}
{% set institution_value = entry.institution if entry.institution is defined and entry.institution else "" %}

{% set main_column_first_line = "" %}
{% if has_custom_main_column_template %}
{# Use template formatting #}
{% if "**AREA**, **DEGREE**" in main_column_template or "**AREA**, DEGREE" in main_column_template or "**AREA**, **DEGREE**" in main_column_template %}
{% set main_column_first_line = "#strong[" ~ area_value ~ "], " ~ degree_value %}
{% elif "*AREA*, DEGREE" in main_column_template %}
{% set main_column_first_line = "#emph[" ~ area_value ~ "], " ~ degree_value %}
{% elif "AREA, DEGREE" in main_column_template %}
{% set main_column_first_line = area_value ~ ", " ~ degree_value %}
{% elif "AREA" in main_column_template and "DEGREE" in main_column_template %}
{% set main_column_first_line = area_value ~ ", " ~ degree_value %}
{% else %}
{% set main_column_first_line = area_value ~ ", " ~ degree_value %}
{% endif %}
{% else %}
{% set main_column_first_line = area_value ~ ", " ~ degree_value %}
{% endif %}

{% set area_style = "default" %}
{% if has_custom_main_column_template and main_column_template %}
{% if "**AREA**" in main_column_template %}
{% set area_style = "bold" %}
{% elif "*AREA*" in main_column_template %}
{% set area_style = "italic" %}
{% endif %}
{% endif %}

{% set institution_style = "default" %}
{% if has_custom_main_column_template and main_column_template %}
{% if "**INSTITUTION**" in main_column_template %}
{% set institution_style = "bold" %}
{% elif "*INSTITUTION*" in main_column_template %}
{% set institution_style = "italic" %}
{% endif %}
{% endif %}

#timeline-education-entry(
  [
{% for line in entry.date_and_location_column.splitlines() %}
    {{ line|indent(4) }}

{% endfor %}
  ],
  [
    #text(fill: {{ design.colors.name.as_rgb() }}, weight: {% if area_style == "bold" %}700{% else %}600{% endif %})[
{% if area_style == "bold" %}
      #strong[{{ main_column_first_line }}]
{% elif area_style == "italic" %}
      #emph[{{ main_column_first_line }}]
{% else %}
      {{ main_column_first_line }}
{% endif %}
    ]
  ],
  main-column-second-row: [
{% if institution_value %}
    #text(
      fill: {{ design.colors.footer.as_rgb() }},
      weight: {% if institution_style == "bold" %}700{% elif institution_style == "italic" %}400{% else %}600{% endif %},
    )[
{% if institution_style == "bold" %}
      #strong[{{ institution_value }}]
{% elif institution_style == "italic" %}
      #emph[{{ institution_value }}]
{% else %}
      {{ institution_value }}
{% endif %}
    ]
{% endif %}
{% if entry.highlights %}
{% for highlight in entry.highlights %}
    {{ highlight|indent(4) }}

{% endfor %}
{% endif %}
  ],
)
