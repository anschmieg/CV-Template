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
  [#connection-with-icon("location-dot")[{{ cv.location }}]],
{% endif %}
{% if cv.email %}
  [#link("mailto:{{ cv.email }}", icon: false, if-underline: false, if-color: false)[#connection-with-icon("envelope")[#text("{{ cv.email }}")]]],
{% endif %}
{% if cv.phone %}
  {% set phone_clean = cv.phone|replace("tel:", "")|replace("-", " ") %}
  [#link("tel:{{ phone_clean|replace(' ', '') }}", icon: false, if-underline: false, if-color: false)[#connection-with-icon("phone")[#text("{{ phone_clean }}")]]],
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
  {% set url_base = "https://" + network_lower + ".com/" %}
  [#link("{{ url_base }}{{ social.username }}", icon: false, if-underline: false, if-color: false)[#connection-with-icon("{{ icon_name }}")[{{ social.username }}]]],
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
