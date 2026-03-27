{# PublicationEntry template - supports cards mode for publication entries #}
{% set pub_ns = namespace(
  title="",
  authors="",
  venue="",
  date_location="",
  citation="",
  details="",
  summary="",
  highlights=[],
  doi="",
  url=""
) %}
{% set entry_title = entry.title if entry.title is defined and entry.title else (entry.name if entry.name is defined and entry.name else '') %}
{% set pub_ns.title = entry_title %}
{% if entry.authors is defined and entry.authors %}
  {% if entry.authors is sequence and entry.authors is not string %}
    {% set pub_ns.authors = entry.authors|join(', ') %}
  {% else %}
    {% set pub_ns.authors = entry.authors %}
  {% endif %}
{% endif %}
{% if entry.journal is defined and entry.journal %}
  {% set pub_ns.venue = entry.journal %}
{% elif entry.publisher is defined and entry.publisher %}
  {% set pub_ns.venue = entry.publisher %}
{% elif entry.venue is defined and entry.venue %}
  {% set pub_ns.venue = entry.venue %}
{% elif entry.booktitle is defined and entry.booktitle %}
  {% set pub_ns.venue = entry.booktitle %}
{% elif entry.conference is defined and entry.conference %}
  {% set pub_ns.venue = entry.conference %}
{% endif %}
{% if entry.date %}
  {% set pub_ns.date_location = entry.date %}
  {% if entry.location %}
    {% set pub_ns.date_location = pub_ns.date_location ~ " · " ~ entry.location %}
  {% endif %}
{% elif entry.location %}
  {% set pub_ns.date_location = entry.location %}
{% endif %}
{% if entry.citation is defined and entry.citation %}
  {% set pub_ns.citation = entry.citation %}
{% endif %}
{% if entry.details is defined and entry.details %}
  {% set pub_ns.details = entry.details %}
{% endif %}
{% if entry.summary is defined and entry.summary %}
  {% set pub_ns.summary = entry.summary %}
{% endif %}
{% if entry.highlights is defined and entry.highlights %}
  {% set pub_ns.highlights = entry.highlights %}
{% endif %}
{% if entry.doi is defined and entry.doi %}
  {% set pub_ns.doi = entry.doi %}
{% endif %}
{% if entry.url is defined and entry.url %}
  {% set pub_ns.url = entry.url %}
{% endif %}
{# Calculate card score for density estimation #}
{% set card_score = namespace(value=0.0) %}
{% if pub_ns.title %}
{% set card_score.value = card_score.value + (pub_ns.title|length / 44) + 0.35 %}
{% endif %}
{% if pub_ns.authors %}
{% set card_score.value = card_score.value + (pub_ns.authors|length / 64) + 0.55 %}
{% endif %}
{% if pub_ns.venue %}
{% set card_score.value = card_score.value + (pub_ns.venue|length / 52) + 0.8 %}
{% endif %}
{% if pub_ns.date_location %}
{% set card_score.value = card_score.value + 0.22 %}
{% endif %}
{% if pub_ns.citation %}
{% set card_score.value = card_score.value + (pub_ns.citation|length / 52) + 0.8 %}
{% endif %}
{% if pub_ns.details %}
{% set card_score.value = card_score.value + (pub_ns.details|length / 52) + 0.8 %}
{% endif %}
{% if pub_ns.summary %}
{% set card_score.value = card_score.value + (pub_ns.summary|length / 52) + 0.8 %}
{% endif %}
{% for highlight in pub_ns.highlights %}
{% if highlight %}
{% set card_score.value = card_score.value + (highlight|length / 58) + 0.85 %}
{% endif %}
{% endfor %}
{% set card_colspan = 1 %}
{% if card_score.value >= 9.8 %}
{% set card_colspan = 2 %}
{% endif %}
#if anschmiegcv_section_view_mode == "cards" [
  #let anschmiegcv_card = [
{% if pub_ns.title %}
    #align(left)[
      #text(fill: {{ design.colors.name.as_rgb() }}, weight: 700)[{{ pub_ns.title|indent(4) }}]
{% if pub_ns.authors %}
      #linebreak()
      #text(fill: {{ design.colors.connections.as_rgb() }}, size: 0.92em)[{{ pub_ns.authors|indent(4) }}]
{% endif %}
{% if pub_ns.venue %}
      #linebreak()
      #text(size: 0.92em)[{{ pub_ns.venue|indent(4) }}]
{% endif %}
{% if pub_ns.date_location %}
      #linebreak()
      #text(fill: {{ design.colors.footer.as_rgb() }}, size: 0.85em)[{{ pub_ns.date_location|indent(4) }}]
{% endif %}
{% if pub_ns.citation %}
      #linebreak()
      #text(size: 0.88em)[{{ pub_ns.citation|indent(4) }}]
{% endif %}
{% if pub_ns.details %}
      #linebreak()
      #text(size: 0.88em)[{{ pub_ns.details|indent(4) }}]
{% endif %}
{% if pub_ns.summary %}
      #linebreak()
      #text(size: 0.88em)[{{ pub_ns.summary|indent(4) }}]
{% endif %}
{% if pub_ns.highlights %}
      #linebreak()
{% for highlight in pub_ns.highlights %}
{% if highlight %}
      #text(size: 0.88em)[• {{ highlight|indent(4) }}]
{% endif %}
{% endfor %}
{% endif %}
{% if pub_ns.doi or pub_ns.url %}
      #linebreak()
      #text(fill: {{ design.colors.links.as_rgb() }}, size: 0.85em)[
{% if pub_ns.doi %}
        #link("https://doi.org/{{ pub_ns.doi|replace('https://doi.org/', '')|replace('http://doi.org/', '')|replace('doi:', '')|replace('DOI:', '')|trim }}")[DOI: {{ pub_ns.doi|replace('https://doi.org/', '')|replace('http://doi.org/', '')|replace('doi:', '')|replace('DOI:', '')|trim }}]
{% endif %}
{% if pub_ns.doi and pub_ns.url %} · {% endif %}
{% if pub_ns.url %}
        #link("{{ pub_ns.url }}")[{{ pub_ns.url }}]
{% endif %}
      ]
{% endif %}
    ]
{% endif %}
  ]
  #anschmiegcv_cards_push(anschmiegcv_card, colspan: {{ card_colspan }})
] else [
{% if not design.entries.short_second_row %}
{% set first_row_lines = entry.date_and_location_column.splitlines()|length %}
{% if first_row_lines == 0 %} {% set first_row_lines = 1 %} {% endif %}
{% else %}
{% set first_row_lines = entry.main_column.splitlines()|length %}
{% endif %}
  #regular-entry(
    [
{% for line in entry.main_column.splitlines()[:first_row_lines] %}
      {{ line|indent(4) }}

{% endfor %}
    ],
    [
{% for line in entry.date_and_location_column.splitlines() %}
      {{ line|indent(4) }}

{% endfor %}
    ],
{% if not design.entries.short_second_row %}
    main-column-second-row: [
{% for line in entry.main_column.splitlines()[first_row_lines:] %}
      {{ line|indent(4) }}

{% endfor %}
    ],
{% endif %}
    is_last_entry: {{ is_last_entry|lower }},
  )
]