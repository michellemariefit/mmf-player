# Pregnancy Diet Plan: what I built, what I found, what to check

Source: Dropbox › PRODUCTS & PROGRAMS › MMF PREGNANCY DIET PLAN › `MMF Pregnancy Diet Plan - Final.pdf` (77 MB, 90 pages, image-only, so weeks 5–8 were read by OCR). Plus the editable `.docx` grocery lists in the same folder and the 1st-edition PDF, which still has live text for weeks 1–4.

The app: **`diet/index.html`** (open `/diet/` on the site). Data: `data/diet.json`, built by `python tools/build_diet.py <folder>`. Hand corrections live in `tools/diet-fixes.json` so a rebuild never loses them.

## What the PDF contains

| Part | Count | Where |
|---|---|---|
| Weeks of meal calendars | 8 | 1st edition pp 6–29 (weeks 1–4), 2nd edition pp 46–87 (weeks 5–8) |
| Dinner recipes | 55 | numbered 1–55, 6–8 per week |
| Snack recipes | 14 | 8 original baked snacks + 6 newer (cookies, brownies, muffins, bites) |
| Breakfast recipes | 7 | frittata, oatmeal pancakes, shakes, Nutty Choco-Nana, Chunky Monkey |
| Grocery lists | 10 | one per week, plus two snack-baking lists |
| Rules | 9 steps, 8 foods to avoid, 7 breakfast options, 6 easy no-cook snacks | pp 2–5 |

## What the app does that the PDF can't

- **Tells her what to eat today.** Five slots: breakfast, snack, lunch, snack, dinner. She ticks them off. Lunch shows yesterday's dinner automatically, because that is the plan's rule.
- **Knows where she is.** Week 1–8 and the day of the week come from a start date she sets once ("This is today"). The plan loops after week 8.
- **Eat every 2–3 hours, enforced.** An "I just ate" button; the app shows the time the next bite is due.
- **Cook once, eat twice.** Every recipe has as-written / 1.5× / 2× buttons and the quantities rescale, fractions included.
- **Aversion filters.** No fish, no eggs, no dairy, no nuts. Recipes get a warning tag or disappear. Dinners can be swapped for any of the 55, and the swap sticks on her week.
- **Snack picker.** Two snack slots a day, filled from the 14 baked snacks or the easy ones. Sunday shows a "prep" card: shop, then bake two batches.
- **Grocery list by aisle** for each week with ticks that persist, hide-what-I-have, add-your-own items, copy to clipboard, print. The two snack lists are there too.
- **Water** (8 glasses), a done-today count and a streak.
- **Favourites**, search by recipe or ingredient, cross-off-as-you-cook ingredient lists.
- Installs to the home screen and works offline (own `manifest.json` and `sw.js`).

Everything is saved on her phone only (no login, no server). Same stack as the 21-day player, so it can sit inside the same site and share the look.

## Black Friday angle

The product she sells is no longer "a PDF". It is the plan that lives on your phone and does the thinking:

1. "Open it in the morning and it tells you what to eat today. Including the snacks."
2. "It writes your grocery list for the week. By aisle."
3. "Cook dinner once and it shows you tomorrow's lunch is already done."
4. "Can't face fish this week? Tap once and every fish dinner is swapped out."
5. "It nags you, kindly, to eat every 2–3 hours. That is the whole secret to less nausea and less weight gain, and the one thing nobody follows from a PDF."
6. Upgrade story for past buyers: "You bought the PDF. Here is the app, free / for $X."

Possible add-ons if she wants more to say: a 7-day "taster" version for leads, or a "first trimester nausea mode" that promotes the blander dinners and the ginger/crackers snacks. Both are data changes, not new builds.

## Things in the PDF that need her eye

Content gaps (the app shows these days correctly but with no recipe button):

- **Week 1 Sunday lunch** is "Chicken with Nectarine Salad". There is no such recipe anywhere in the book.
- **Week 5 Wednesday dinner** is "Veggie Supreme Rice". No recipe in the book.
- **Week 6 Saturday breakfast** is blank in the PDF. Saturday lunch there also doesn't match Friday's dinner.
- Several weeks list a dinner on the calendar with a different name than the recipe page (e.g. "Sun-dried Tomato Feta Turkey Meatloaf"). I matched them by hand in `tools/diet-fixes.json`; worth a skim.

Stale text in her own intro (pp 2–4, copied verbatim into the Plan tab):

- Says "I am giving you 4 weeks of meal plans" and "For the 4 weeks, you have a total of 8 recipes for snacks". The 2nd edition has 8 weeks and 14 snacks. I did not edit her words; tell me and I will.
- Step 9 links to Dale's Raw Protein Bars at a dead URL. I kept the recommendation and dropped the link.
- Two typos she may want fixed: "left over's", "weigh that is necessary", "So if I you are on week 3".

OCR check: weeks 5–8 and recipes 25–55 were read by OCR. Fractions (¼ ½ ¾) were the main risk and I corrected the patterns I could see, but a human pass is cheap. **Open `tools/diet-review.html`**: every recipe is shown next to its page image. Ten minutes.

## Questions for Michelle

1. Is this a replacement for the PDF buyers get, or an add-on? That decides whether the PDF download stays in the app.
2. Price and delivery for Black Friday: same FG Funnels product with a new link in the thank-you page, or a new product?
3. Do the recipes need macros or calories? The PDF has none. Adding them is a day of work with a nutrition database and should be labelled "approximate".
4. Is she OK with me rewriting the intro for 8 weeks, or does she want to re-record it as a 60-second welcome video instead (the app can embed it)?
5. The 2nd edition dropped the snack photos. Does she have food photos anywhere, or should the app stay text-only? (Text-only is fine on a phone; photos are mostly for the sales page.)
6. Does she want the diet app linked from the 21-day challenge calendar (meal plan page), so challengers see the upsell on day 1?

## Files

- `diet/index.html`, `diet/manifest.json`, `diet/sw.js` — the app
- `data/diet.json` — all content
- `tools/build_diet.py`, `tools/diet-fixes.json` — builder and hand fixes
- `tools/diet-review.html`, `tools/diet-pages/` — side-by-side review of every recipe against the PDF page
