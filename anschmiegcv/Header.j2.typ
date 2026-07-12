{% macro image() %}
#pad(left: {{ design.header.photo_space_left }}, right: {{ design.header.photo_space_right }}, image("{{ cv.photo.name }}", width: {{ design.header.photo_width }}))
{% endmacro %}

{% if cv.photo %}
{% set photo = "image(\"" + cv.photo|string + "\", width: "+ design.header.photo_width + ")" %}
#grid(
{% if design.header.photo_position == "left" %}
  columns: (auto, 1fr),
{% else %}
  columns: (1fr, auto),
{% endif %}
  column-gutter: 0cm,
  align: horizon + left,
{% if design.header.photo_position == "left" %}
  [{{ image() }}],
  [
{% else %}
  [
{% endif %}
{% endif %}
{% if cv.name %}
= {{ cv.name }}
{% endif %}

{% if cv.headline %}
  #headline([{{ cv.headline }}])

{% endif %}
#connections(
{% if cv.location %}
{% if design.header.connections.show_icons %}
  [#connection-with-icon("location-dot")[{{ cv.location }}]],
{% else %}
  [{{ cv.location }}],
{% endif %}
{% endif %}
{% if cv.email %}
{% if design.header.connections.hyperlink %}
{% if design.header.connections.show_icons %}
  [#link("mailto:{{ cv.email }}", icon: false, if-underline: false, if-color: false)[#connection-with-icon("envelope")[#text("{{ cv.email }}")]]],
{% else %}
  [#link("mailto:{{ cv.email }}", icon: false, if-underline: false, if-color: false)[#text("{{ cv.email }}")]],
{% endif %}
{% else %}
{% if design.header.connections.show_icons %}
  [#connection-with-icon("envelope")[#text("{{ cv.email }}")]],
{% else %}
  [#text("{{ cv.email }}")],
{% endif %}
{% endif %}
{% endif %}
{% if cv.phone %}
{% if design.header.connections.hyperlink %}
{% if design.header.connections.show_icons %}
  [#link("tel:{{ cv.phone|replace('tel:', '') }}", icon: false, if-underline: false, if-color: false)[#connection-with-icon("phone")[{{ cv.phone|replace('tel:', '') }}]]],
{% else %}
  [#link("tel:{{ cv.phone|replace('tel:', '') }}", icon: false, if-underline: false, if-color: false)[{{ cv.phone|replace('tel:', '') }}]],
{% endif %}
{% else %}
{% if design.header.connections.show_icons %}
  [#connection-with-icon("phone")[{{ cv.phone|replace('tel:', '') }}]],
{% else %}
  [{{ cv.phone|replace('tel:', '') }}],
{% endif %}
{% endif %}
{% endif %}
{% if cv.social_networks %}
{% for social in cv.social_networks %}
  {% set network_lower = social.network|lower %}
  {% set icon_name = network_lower %}
  {% if network_lower == "linkedin" %}
    {% set icon_name = "linkedin" %}
  {% elif network_lower == "github" %}
    {% set icon_name = "github" %}
  {% elif network_lower == "twitter" or network_lower == "x" %}
    {% set icon_name = "twitter" %}
  {% elif network_lower == "gitlab" %}
    {% set icon_name = "gitlab" %}
  {% elif network_lower == "stackoverflow" or network_lower == "stack overflow" %}
    {% set icon_name = "stack-overflow" %}
  {% elif network_lower == "researchgate" or network_lower == "research gate" %}
    {% set icon_name = "researchgate" %}
  {% elif network_lower == "google-scholar" or network_lower == "google scholar" %}
    {% set icon_name = "google" %}
  {% elif network_lower == "orcid" %}
    {% set icon_name = "orcid" %}
  {% endif %}
  {% if network_lower == "linkedin" %}
    {% set social_url = "https://linkedin.com/in/" + social.username %}
  {% elif network_lower == "github" %}
    {% set social_url = "https://github.com/" + social.username %}
  {% else %}
    {% set social_url = "https://" + network_lower + ".com/" + social.username %}
{% endif %}
  {% set social_label = social_url|clean_url if design.header.connections.display_urls_instead_of_usernames else social.username %}
{% if design.header.connections.hyperlink %}
{% if design.header.connections.show_icons %}
  [#link("{{ social_url }}", icon: false, if-underline: false, if-color: false)[#connection-with-icon("{{ icon_name }}")[{{ social_label }}]]],
{% else %}
  [#link("{{ social_url }}", icon: false, if-underline: false, if-color: false)[{{ social_label }}]],
{% endif %}
{% else %}
{% if design.header.connections.show_icons %}
  [#connection-with-icon("{{ icon_name }}")[{{ social_label }}]],
{% else %}
  [{{ social_label }}],
{% endif %}
{% endif %}
{% endfor %}
{% endif %}
)
{% if cv.photo %}
{% if design.header.photo_position == "left" %}
  ]
)
{% else %}
  ],
  [{{ image() }}],
)
{% endif %}
{% endif %}
