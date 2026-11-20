# The 21 Day Fit Pregnancy Challenge player

One mobile web page that replaces the workout PDFs, plus a Day 1 to Day 21 calendar, the meal plan
in the app, lesson notes, and a printable version of every workout. Built on the Youth Athlete Edge
player engine and changed for how the challenge is sold: 21 days in order, habits in week 1, three
strength and two cardio workouts a week, all strength in week 3, and a 3 Day Butt & Thighs bonus.

## What's here

- `start.html` is the home page: today's workout first, then the rest.
- `calendar.html` is the 21 day calendar. The start date is the first day the app was opened; "Today is day N" moves it. Tick days off, see the streak.
- `index.html` is the list view: the whole workout on one page, start and end photos, tick rounds, rest timer under the circuit. Cardio workouts get a Go timer per move.
- `play.html` is play mode: one move at a time, one big button. Runs rest timers and, for cardio, the work timers.
- `meals.html` shows the meal plan PDFs as page images (iOS Safari only shows page one of an embedded PDF) with download links.
- `lessons.html` has the notes for each lesson video and the FAQ. Reads `data/lessons.json`.
- `print.html` is one landscape page per workout with photos. `pdf/` has the meal plan and bonus PDFs for download.
- `data/challenge.json` holds the whole program: weeks, workouts, every exercise with name, reps, cue, YouTube demo ID and photos, and the 21 days. Every page reads this one file.
- `images/` holds the start and end photos (`<video id>-start.webp`, `-end.webp`) and the untouched PDF composite (`-pdf.webp`). `images/meals/` holds the PDF page images.
- `diet/` is the Pregnancy Diet Plan as its own installable app (today's meals, week, 55 recipes with servings scaler, grocery lists by aisle, the rules). Reads `data/diet.json`, built by `tools/build_diet.py` with hand fixes in `tools/diet-fixes.json`. See `docs/diet-plan-notes.md`.
- `docs/catalogue.md` is what was found in Dropbox, the FG course and the sales page. `docs/review-notes.md` is what to fix in the members area.

## Links

Live at `https://michellemariefit.github.io/mmf-player/` once GitHub Pages is on (Settings → Pages → main, root).

| Link ends with | Shows |
| --- | --- |
| nothing | start.html (home) |
| `index.html#w1-arms` | only that workout, no pickers |
| `index.html#week-2` | week 2 with a picker (`#bonus` for the 3 Day bonus) |
| `index.html#all` | everything |
| `play.html#w3-legs` | play mode for that workout; `play.html` alone is the picker |
| `print.html#w2-butt` | one printable page; `print.html` is all 18 |
| `lessons.html#day3` | scrolls to that lesson |
| `meals.html#recipes` | opens that tab |
| `diet/` | the Pregnancy Diet Plan app |

Workout ids: `w1-full-body w1-cardio-1 w1-arms w1-cardio-2 w1-thighs w2-full-body w2-cardio-1 w2-arms w2-cardio-2 w2-butt w3-back w3-butt-core w3-arms w3-legs w3-burner bonus-day-1 bonus-day-2 bonus-day-3`.

## Put it in FG Funnels

Paste this in a lesson, changing the bit after `#` to the workout that lesson is about:

```html
<iframe src="https://michellemariefit.github.io/mmf-player/index.html#w1-full-body" style="width:100%;height:1400px;border:0" allow="encrypted-media; picture-in-picture" allowfullscreen></iframe>
```

## Rebuild the data and photos

`tools/build_challenge.py` holds the program (reps, sets, rest, YouTube ids) and pulls the photos
out of the PDFs. Put the PDFs from Dropbox in `tools/pdf/` (ignored by git), then:

```
pip install pypdf pdfplumber pillow numpy
python tools/build_challenge.py
```

It writes `data/challenge.json`, the photos in `images/`, and `tools/review.html` to check every pair.
Each exercise photo in the PDFs is a start-to-end composite with an arrow; the script splits it in two.
The 2022 PDFs (week 3, the Lateral Lunges photo excepted) are sharp; the 2020 ones are soft.

## Printable PDFs

`tools/make_pdfs.js` opens `print.html` in headless Chromium and writes one PDF per workout plus
`pdf/all-workouts.pdf`:

```
node tools/make_pdfs.js
```
