# Verve By the Glass

Verve Wine SF's weekly by-the-glass pours, worked through the WSET Level 3 Systematic Approach to Tasting. Study notes by Rodrigo Hernandez for the Verve team.

## How it works
- `btg/index.html` renders everything; each week's wines live in `btg/weeks/`. The site lives at /verve/btg/; the root and /BTG/ redirect there.
- One JSON file per week, named `wYYYYMMDD.json` (start of the week), with `weekOf`, `label`, `short`, `wines[]` and `lineup`. Copy an existing week for the shape.
- Add each new week's id to the front of `btg/weeks/index.json`. Never edit or delete past weeks: the page is a running library.
- Wine `type` must be `white`, `rose` or `red` (drives the Library filter). `sat` values are 1-based indexes into the WSET scales (alcohol has 3 levels, the others 5).
- Served by GitHub Pages from `main`, root folder.

**For Verve Wine staff only.** Internal study notes; please don't share outside the team. The page carries a `noindex` tag so search engines skip it, but the repo and site are public: anyone with the link can open them.
