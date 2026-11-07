# Verve By the Glass

Verve Wine SF's weekly by-the-glass pours, worked through the WSET Level 3 Systematic Approach to Tasting. Study notes by Rodrigo Hernandez for the Verve team.

## How it works
- `index.html` renders everything; each week's wines live in `weeks/`.
- One JSON file per week, named `wYYYYMMDD.json` (start of the week), with `weekOf`, `label`, `short`, `wines[]` and `lineup`. Copy an existing week for the shape.
- Add each new week's id to the front of `weeks/index.json`. Never edit or delete past weeks: the page is a running library.
- Wine `type` must be `white`, `rose` or `red` (drives the Library filter). `sat` values are 1-based indexes into the WSET scales (alcohol has 3 levels, the others 5).
- Served by GitHub Pages from `main`, root folder.
