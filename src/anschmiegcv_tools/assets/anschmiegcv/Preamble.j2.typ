// Import the rendercv function and all the refactored components
#import "@preview/rendercv:0.1.0": *

// Apply the rendercv template with custom configuration
#show: rendercv.with(
  name: "{{ cv.name }}",
  footer: {{ cv.footer }},
  top-note: [ {{ cv.top_note }} ],
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

// Custom timeline entry function for Experience and Education sections
#let timeline-entry(
  date-and-location-column,
  main-column,
  main-column-second-row: none,
  dot-color: {% if design.colors.timeline_dot %}{{ design.colors.timeline_dot.as_rgb() }}{% else %}{{ design.colors.connections.as_rgb() }}{% endif %},
  line-color: {% if design.colors.timeline_line %}{{ design.colors.timeline_line.as_rgb() }}{% else %}{{ design.colors.connections.as_rgb() }}{% endif %},
) = {
  let dot-size = 10pt
  let line-width = 2.5pt
  let date-column-width = {{ design.entries.date_and_location_width }}
  let side-space = {{ design.entries.side_space }}
  let space-between-columns = {{ design.entries.space_between_columns }}
  let timeline-indent = 0.18cm

  // Draw timeline as a left border on the main content column. This guarantees
  // a stable vertical line that follows entry height and page breaking.
  block(
    breakable: true,
    grid(
      columns: (side-space, date-column-width - side-space, space-between-columns, 1fr, side-space),
      column-gutter: 0pt,
      row-gutter: 0pt,
      align: (left, {{ design.typography.date_and_location_column_alignment }}, left, left, left),

      [],
      date-and-location-column,
      [],
      [
        #box(
          inset: (left: timeline-indent, bottom: {{ design.sections.space_between_regular_entries }}),
          stroke: (left: line-width + line-color),
          [
            #place(dx: -timeline-indent - dot-size / 2 + line-width / 2, dy: 0.45em, circle(radius: dot-size / 2, fill: dot-color, stroke: 1.8pt + white))
            #main-column
            #if main-column-second-row != none [
              #linebreak()
              #main-column-second-row
            ]
          ],
        )
      ],
      [],
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
) = {
  // Use same timeline layout as regular entries
  timeline-entry(
    date-and-location-column,
    main-column,
    main-column-second-row: main-column-second-row,
    dot-color: dot-color,
    line-color: line-color,
  )
}
