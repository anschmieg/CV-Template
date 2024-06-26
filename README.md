# CV-Template
Build a responsive and printable resume webpage from a structured markdown file. Screenshots [here](#screenshots).

## How to

### 1. Fill in your resumé information in markdown format

An example can be found in _YourResume.md_.

Some elements are needed to convert the information to the proper structure. 

- Empty lines are needed to separate elements
- Dashes `-` and numbers `1.` start a list
- Hash tags `#` indicate a heading (one # for first level, two ## for second level etc.)
- Curly braces `{}` assign attributes to headings, e.g. `{.cards}`
  - Some headings `#` contain `.fa .fa-something` in `{}`. This assigns an icon to the heading. Icons can be found [here](https://fontawesome.com/search).
  - Skills `{.skills}` sections contain a list `-` with  
    `- the text in the middle of the skill circle`  
    `- a percentage to fill the circle by`.
  - Cards `{.cards}` sections can contain virtually any content.
  - Timelines `{.timeline}` accept a table with info to display above an entry – the header will be displayed, the body will be hidden.
- Tables are written as:

```
| Col 1 | Col 2 |
| ----- | ----- |
| cont- | -ent  |
```

Therefore timeline information is entered as:

```
| Date | Location |
|-|-|
```

### 2. Run the following command:
```
pandoc -s --toc --toc-depth 1 -t html5 --template assets/template.html -o index.html YourResume.md
```
while replacing `YourResume.md` with your own file.

## Multi-lingual support
Repeat the above steps for each language, while linking the remaining languages at the top of each file in the `{.lang}` section.

For example, change `index.html` in the command to `fr.html` for the French page and link it as  

> `[French](fr.html)`

## Well done, that should be it! ✅

# Screenshots

## Desktop: 

![Screenshot - Desktop 1](pics/screenshots/desktop-1.png)
![Screenshot - Desktop 2](pics/screenshots/desktop-2.png)

## Mobile:

|![Screenshot - Mobile 1](pics/screenshots/mobile-1.png)|![Screenshot - Mobile 2](pics/screenshots/mobile-2.png)|
|-|-|


# Documentation

## Progress Bar Plugin

The plugin used is [kottenator/jquery-circle-progress](https://github.com/kottenator/jquery-circle-progress).