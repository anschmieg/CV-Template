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
{# Pattern: [markdown]Organization, Area #}
{% set header_parts = ns.header.split("], ", 1) %}
{% set organization_line = header_parts[0] ~ "]" %}
{% set area_line = header_parts[1] %}
{% set degree_line = none %}
{% elif ", " in ns.header %}
{# Check for AREA, DEGREE pattern (comma-separated area and degree) #}
{% set header_parts = ns.header.split(", ", 1) %}
{% set first_part = header_parts[0].strip() %}
{% set second_part = header_parts[1].strip() if header_parts|length == 2 else "" %}
{# Check if this matches known area and degree values #}
{% set entry_area = entry.area if entry.area is defined and entry.area else "" %}
{% set entry_degree = entry.degree if entry.degree is defined and entry.degree else "" %}
{% if (first_part == entry_area and second_part == entry_degree) or (first_part == entry_degree and second_part == entry_area) %}
{# Pattern: Area, Degree or Degree, Area - both parts match known values #}
{% if first_part == entry_area %}
{% set area_line = entry_area %}
{% set degree_line = entry_degree %}
{% else %}
{% set area_line = entry_area %}
{% set degree_line = entry_degree %}
{% endif %}
{% set organization_line = entry.institution if entry.institution is defined and entry.institution else "" %}
{% set institution_stripped = organization_line|replace("#strong[", "")|replace("]", "")|replace("#emph[", "")|trim %}
{% if ns.body and ns.body[0].strip() == institution_stripped %}
{% set ns.body = ns.body[1:] %}
{% elif ns.body and ns.body[0].strip() == organization_line %}
{% set ns.body = ns.body[1:] %}
{% endif %}
{% else %}
{# Pattern: Organization, Area #}
{% set organization_line = header_parts[0] %}
{% set area_line = header_parts[1] %}
{% set degree_line = none %}
{% endif %}
{% else %}
{# Pattern: Degree Area (space-separated) or just Area #}
{% set organization_line = entry.institution if entry.institution is defined and entry.institution else "" %}
{% set area_line = ns.header %}
{# When degree+area appear in header, split them using entry.degree and entry.area #}
{% set degree_line = entry.degree if entry.degree is defined and entry.degree else none %}
{% set area_line = entry.area if entry.area is defined and entry.area else "" %}
{# When organization comes from entry.institution, skip it in body to avoid duplication #}
{% set institution_stripped = organization_line|replace("#strong[", "")|replace("]", "")|replace("#emph[", "")|trim %}
{% if ns.body and ns.body[0].strip() == institution_stripped %}
{% set ns.body = ns.body[1:] %}
{% elif ns.body and ns.body[0].strip() == organization_line %}
{% set ns.body = ns.body[1:] %}
{% endif %}
{% endif %}
{% set organization_plain = organization_line|replace("#strong[", "")|replace("#emph[", "") %}
{% if organization_plain[-1:] == "]" %}
{% set organization_plain = organization_plain[:-1]|trim %}
{% endif %}
{# Education styling uses Typst variables injected from design_config.yaml #}
{# Default values match the YAML defaults: degree=grey/600, area=grey/700, institution=teal/600 #}
{% set degree_color = "anschmiegcv_education_degree_color" %}
{% set degree_weight = "anschmiegcv_education_degree_weight" %}
{% set area_color = "anschmiegcv_education_area_color" %}
{% set area_weight = "anschmiegcv_education_area_weight" %}
{% set institution_color = "anschmiegcv_education_institution_color" %}
{% set institution_weight = "anschmiegcv_education_institution_weight" %}
{# Legacy template style detection #}
{% set main_column_template = "" %}
{% set has_custom_main_column_template = false %}
{% if design.templates.education_entry is defined and design.templates.education_entry.model_fields_set is defined and "main_column" in design.templates.education_entry.model_fields_set %}
{% set has_custom_main_column_template = true %}
{% endif %}
{% if has_custom_main_column_template and design.templates.education_entry.main_column is defined and design.templates.education_entry.main_column %}
{% set main_column_template = design.templates.education_entry.main_column %}
{% endif %}
{% set area_style = "default" %}
{% if has_custom_main_column_template and main_column_template %}
{% if "**AREA**" in main_column_template %}
{% set area_style = "bold" %}
{% elif "*AREA*" in main_column_template %}
{% set area_style = "italic" %}
{% else %}
{% set area_style = "plain" %}
{% endif %}
{% endif %}
{% set organization_style = "default" %}
{% if has_custom_main_column_template and main_column_template %}
{% if "**INSTITUTION**" in main_column_template %}
{% set organization_style = "bold" %}
{% elif "*INSTITUTION*" in main_column_template %}
{% set organization_style = "italic" %}
{% endif %}
{% endif %}
#timeline-education-entry(
  [
{% for line in entry.date_and_location_column.splitlines() %}
    #emph[{{ line|indent(4) }}]
{% endfor %}
  ],
  [
{% if degree_line %}
    #text(fill: {{ area_color }}, weight: {{ area_weight }})[{{ area_line }},]#text(fill: {{ degree_color }}, weight: {{ degree_weight }})[ {{ degree_line }}]
{% elif area_line %}
    #text(
      fill: {{ area_color }},
      weight: {{ area_weight }},
    )[
{% if area_style == "bold" %}
      #strong[{{ area_line|indent(6) }}]
{% elif area_style == "italic" %}
      #emph[{{ area_line|indent(6) }}]
{% else %}
      {{ area_line|indent(6) }}
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
{% if (degree_line and organization_line) or (area_line and organization_line) or entry.degree_column or ns.body|length > 0 %}
  main-column-second-row: [
{% if degree_line and organization_line %}
    #text(
      fill: {{ institution_color }},
      weight: {{ institution_weight }},
    )[
      {{ organization_plain|indent(6) }}
    ]
{% elif area_line and organization_line %}
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
{% if entry.degree_column %}
    {{ entry.degree_column|indent(4) }}

{% endif %}
{% for line in ns.body %}
    {{ line|indent(4) }}

{% endfor %}
  ],
{% endif %}
  is_last_entry: {{ is_last_entry|lower }},
)