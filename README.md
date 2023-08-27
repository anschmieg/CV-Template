# CV-Template: build a resume webpage from a structured markdown file
## Project Objective (Functionality)
1. Fill `YourResume.md` with the wanted info, following the demo'ed syntax
2. Run the following command:
```
pandoc -s --toc --toc-depth 1 -t html5 --template assets/template.html -o index.html YourResume.md
```

## Multi-lingual support
Repeat the above steps for each language, while linking the remaining languages in each file. 

## That should be it! ✅
