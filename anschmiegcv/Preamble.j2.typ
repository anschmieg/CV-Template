// Import the rendercv function and all the refactored components
#import "@preview/rendercv:0.1.0": *

// Apply the rendercv template with custom configuration
#show: rendercv.with(
  name: "{{ cv.name }}",
  footer: {{ cv._footer }},
  top-note: [ {{ cv._top_note }} ],
  locale-catalog-language: "{{ locale.language_iso_639_1 }}",
  page-size: "{{ design.page.size }}",
  page-top-margin: {{ design.page.top_margin }},
  page-bottom-margin: {{ design.page.bottom_margin }},
  page-left-margin: {{ design.page.left_margin }},
  page-right-margin: {{ design.page.right_margin }},
  page-show-footer: {{ design.page.show_footer|lower }},
  page-show-top-note: {{ design.page.show_top_note|lower }},
  colors-body: {{ design.colors.body.as_rgb() }},
  colors-name: {{ design.colors.name.as_rgb() }},
  colors-headline: {{ design.colors.headline.as_rgb() }},
  colors-connections: {{ design.colors.connections.as_rgb() }},
  colors-section-titles: {{ design.colors.section_titles.as_rgb() }},
  colors-links: {{ design.colors.links.as_rgb() }},
  colors-footer: {{ design.colors.footer.as_rgb() }},
  colors-top-note: {{ design.colors.top_note.as_rgb() }},
  typography-line-spacing: {{ design.typography.line_spacing }},
  typography-alignment: "{{ design.typography.alignment }}",
  typography-date-and-location-column-alignment: {{ design.typography.date_and_location_column_alignment }},
  typography-font-family-body: "{{ design.typography.font_family.body }}",
  typography-font-family-name: "{{ design.typography.font_family.name }}",
  typography-font-family-headline: "{{ design.typography.font_family.headline }}",
  typography-font-family-connections: "{{ design.typography.font_family.connections }}",
  typography-font-family-section-titles: "{{ design.typography.font_family.section_titles }}",
  typography-font-size-body: {{ design.typography.font_size.body }},
  typography-font-size-name: {{ design.typography.font_size.name }},
  typography-font-size-headline: {{ design.typography.font_size.headline }},
  typography-font-size-connections: {{ design.typography.font_size.connections }},
  typography-font-size-section-titles: {{ design.typography.font_size.section_titles }},
  typography-small-caps-name: {{ design.typography.small_caps.name|lower }},
  typography-small-caps-headline: {{ design.typography.small_caps.headline|lower }},
  typography-small-caps-connections: {{ design.typography.small_caps.connections|lower }},
  typography-small-caps-section-titles: {{ design.typography.small_caps.section_titles|lower }},
  typography-bold-name: {{ design.typography.bold.name|lower }},
  typography-bold-headline: {{ design.typography.bold.headline|lower }},
  typography-bold-connections: {{ design.typography.bold.connections|lower }},
  typography-bold-section-titles: {{ design.typography.bold.section_titles|lower }},
  links-underline: {{ design.links.underline|lower }},
  links-show-external-link-icon: {{ design.links.show_external_link_icon|lower }},
  header-alignment: {{ design.header.alignment }},
  header-photo-width: {{ design.header.photo_width }},
  header-space-below-name: {{ design.header.space_below_name }},
  header-space-below-headline: {{ design.header.space_below_headline }},
  header-space-below-connections: {{ design.header.space_below_connections }},
  header-connections-hyperlink: {{ design.header.connections.hyperlink|lower }},
  header-connections-show-icons: {{ design.header.connections.show_icons|lower }},
  header-connections-display-urls-instead-of-usernames: {{ design.header.connections.display_urls_instead_of_usernames|lower }},
  header-connections-separator: "{{ design.header.connections.separator }}",
  header-connections-space-between-connections: {{ design.header.connections.space_between_connections }},
  section-titles-type: "{{ design.section_titles.type }}",
  section-titles-line-thickness: {{ design.section_titles.line_thickness }},
  section-titles-space-above: {{ design.section_titles.space_above }},
  section-titles-space-below: {{ design.section_titles.space_below }},
  sections-allow-page-break: {{ design.sections.allow_page_break|lower }},
  sections-space-between-text-based-entries: {{ design.sections.space_between_text_based_entries }},
  sections-space-between-regular-entries: {{ design.sections.space_between_regular_entries }},
  entries-date-and-location-width: {{ design.entries.date_and_location_width }},
  entries-side-space: {{ design.entries.side_space }},
  entries-space-between-columns: {{ design.entries.space_between_columns }},
  entries-allow-page-break: {{ design.entries.allow_page_break|lower }},
  entries-short-second-row: {{ design.entries.short_second_row|lower }},
  entries-summary-space-left: {{ design.entries.summary.space_left }},
  entries-summary-space-above: {{ design.entries.summary.space_above }},
  entries-highlights-bullet: {% if design.entries.highlights.bullet == "●" %} text(13pt, [•], baseline: -0.6pt) {% else %} "{{ design.entries.highlights.bullet }}" {% endif %},
  entries-highlights-nested-bullet: {% if design.entries.highlights.nested_bullet == "●" %} text(13pt, [•], baseline: -0.6pt) {% else %} "{{ design.entries.highlights.nested_bullet }}" {% endif %},
  entries-highlights-space-left: {{ design.entries.highlights.space_left }},
  entries-highlights-space-above: {{ design.entries.highlights.space_above }},
  entries-highlights-space-between-items: {{ design.entries.highlights.space_between_items }},
  entries-highlights-space-between-bullet-and-text: {{ design.entries.highlights.space_between_bullet_and_text }},
  date: datetime(
    year: {{ settings.current_date.year }},
    month: {{ settings.current_date.month }},
    day: {{ settings.current_date.day }},
  ),
)

#let anschmiegcv_section_view_mode = "auto"
#let anschmiegcv_card_layout = "one"
#let anschmiegcv_cards_state = state("anschmiegcv.cards.state", ())

#let anschmiegcv_cards_clear() = context {
  anschmiegcv_cards_state.update(_ => ())
}

#let anschmiegcv_cards_push(card, colspan: 1) = context {
  anschmiegcv_cards_state.update(items => items + ((card, colspan),))
}

#let anschmiegcv_cards_columns(layout) = {
  if layout == "four" {
    (1fr, 1fr, 1fr, 1fr)
  } else if layout == "three_equal" {
    (1fr, 1fr, 1fr)
  } else if layout == "three_weighted" {
    (1fr, 1fr, 2fr)
  } else if layout == "two" {
    (1fr, 1fr)
  } else {
    (1fr,)
  }
}

#let anschmiegcv_cards_render(layout: "one") = context {
  let items = anschmiegcv_cards_state.get()
  if items.len() == 0 {
    none
  } else {
    let item_count = items.len()
    let cells = range(0, item_count).map(index => {
      let (card, colspan) = items.at(index)
      let span = if layout == "two" and calc.rem(item_count, 2) == 1 and index == item_count - 1 {
        2
      } else if layout == "three_weighted" and colspan > 1 {
        2
      } else {
        1
      }
      grid.cell(
        colspan: span,
        inset: 8pt,
        stroke: 0.7pt + {{ design.colors.connections.as_rgb() }},
      )[
        #card
      ]
    })
    grid(
      columns: anschmiegcv_cards_columns(layout),
      column-gutter: 0.24cm,
      row-gutter: 0.24cm,
      ..cells,
    )
  }
}

// Custom timeline entry function for Experience and Education sections
#let timeline-entry(
  date-and-location-column,
  main-column,
  main-column-second-row: none,
  dot-color: {% if design.colors.timeline_dot %}{{ design.colors.timeline_dot.as_rgb() }}{% else %}{{ design.colors.connections.as_rgb() }}{% endif %},
  line-color: {% if design.colors.timeline_line %}{{ design.colors.timeline_line.as_rgb() }}{% else %}{{ design.colors.connections.as_rgb() }}{% endif %},
) = context {
  let body-font-size = {{ design.typography.font_size.body }}
  let line-spacing = {{ design.typography.line_spacing }}
  let cap-height = measure(text(size: body-font-size)[H]).height
  let dot-size = cap-height / 1.00
  let line-width = body-font-size * 0.095
  let dot-outline-width = dot-size * 0.16
  let dot-outer-size = dot-size + dot-outline-width
  let date-column-width = {{ design.entries.date_and_location_width }}
  let space-between-columns = {{ design.entries.space_between_columns }}
  let timeline-indent = space-between-columns
  let entry-gap = {{ design.sections.space_between_regular_entries }} + line-spacing

  // Render one continuous vertical track per entry, including its continuation gap.
  block(
    breakable: true,
    above: 0pt,
    below: 0pt,
    grid(
      columns: (date-column-width, space-between-columns, 1fr),
      column-gutter: 0pt,
      row-gutter: 0pt,
      align: ({{ design.typography.date_and_location_column_alignment }}, left, left),
      date-and-location-column,
      [],
      [
        #box(
          inset: (left: timeline-indent),
          stroke: (left: line-width + line-color),
          [
            #place(
              top + left,
              dx: -timeline-indent - dot-outer-size / 2,
              dy: (cap-height - dot-size - dot-outline-width) / 2,
              circle(radius: dot-size / 2, fill: dot-color, stroke: dot-outline-width + white),
            )
            #main-column
            #if main-column-second-row != none {
              linebreak()
              main-column-second-row
            }
            #v(entry-gap)
          ],
        )
      ]
    ),
  )
}

// Timeline education entry wrapper
// Note: degree-column parameter is accepted for template compatibility but not rendered
// as a separate column in the timeline layout. Degree information should be included in
// the main-column content via the education entry template configuration.
#let timeline-education-entry(
  date-and-location-column,
  main-column,
  degree-column: none,
  main-column-second-row: none,
  dot-color: {% if design.colors.timeline_dot %}{{ design.colors.timeline_dot.as_rgb() }}{% else %}{{ design.colors.connections.as_rgb() }}{% endif %},
  line-color: {% if design.colors.timeline_line %}{{ design.colors.timeline_line.as_rgb() }}{% else %}{{ design.colors.connections.as_rgb() }}{% endif %},
) = context {
  // Use same timeline layout as regular entries
  timeline-entry(
    date-and-location-column,
    main-column,
    main-column-second-row: main-column-second-row,
    dot-color: dot-color,
    line-color: line-color,
  )
}

// Custom regular entry that aligns with timeline entries for consistent spacing
// Used for Publications, Certifications, Volunteer - same left padding, no timeline graphics
#let regular-entry(
  main-column,
  date-and-location-column,
  main-column-second-row: none,
) = context {
  let body-font-size = {{ design.typography.font_size.body }}
  let line-spacing = {{ design.typography.line_spacing }}
  let date-column-width = {{ design.entries.date_and_location_width }}
  let space-between-columns = {{ design.entries.space_between_columns }}
  let timeline-indent = space-between-columns
  let entry-gap = {{ design.sections.space_between_regular_entries }} + line-spacing

  block(
    breakable: true,
    above: 0pt,
    below: 0pt,
    grid(
      columns: (date-column-width, space-between-columns, 1fr),
      column-gutter: 0pt,
      row-gutter: 0pt,
      align: ({{ design.typography.date_and_location_column_alignment }}, left, left),
      date-and-location-column,
      [],
      [
        #box(
          inset: (left: timeline-indent),
          [
            #main-column
            #if main-column-second-row != none {
              linebreak()
              main-column-second-row
            }
            #v(entry-gap)
          ],
        )
      ]
    ),
  )
}

// Custom regular entry with minimal left padding
// Date flows inline above content instead of in a wide left column
#let regular-entry(
  main-column,
  date-and-location-column,
  main-column-second-row: none,
) = context {
  let line-spacing = {{ design.typography.line_spacing }}
  let entry-gap = {{ design.sections.space_between_regular_entries }} + line-spacing
  let regular-entry-indent = 0.08cm

  block(
    breakable: true,
    above: 0pt,
    below: 0pt,
    [
      // Date flows inline at the start, then content
      #box(
        inset: (left: regular-entry-indent),
        [
          #text(size: 0.9em, fill: {{ design.colors.connections.as_rgb() }})[
            #date-and-location-column
          ]
          #v(0.1em)
          #main-column
          #if main-column-second-row != none {
            linebreak()
            main-column-second-row
          }
          #v(entry-gap)
        ],
      )
    ]
  )
}
