# Pregnancy Diet Plan sales page: what to change now it's an app

Page reviewed: fitpregnancyworkouts.com/pregnancynutritionplan (desktop and phone, Nov 20).
Promo images are in `promo/`. They are rendered from the live app by `tools/promo/make_promo.js`, so if the app changes, run it again and they update.

## The one-line verdict

The page sells a PDF. Every proof point is a stack of printed pages and every bullet is about reading. The product is now something she opens on her phone every morning, and the page should say that in the first screen and prove it with the phone in every "what's included" block. The story, the testimonials, and Michelle's voice can stay. The headline, the three included blocks, the price box, three FAQ answers, and the mockups change.

## Bugs on the live page (fix regardless)

| Where | Problem | Fix |
|---|---|---|
| Desktop headline | Reads "For A Healthy Baby & **Healthy Baby**". The phone version correctly says "& Fit Pregnancy". | Make desktop match the phone version. |
| Guarantee | "…the measly **$27**" while the price is $37. | $37, or drop the number. |
| Price box | "84 Recipe Cards", "9 Printable Shopping Lists". The app has 79 recipes and 10 lists. | Use the real numbers (below). |
| Testimonial block | The text "meals.It" is auto-linked to http://meals.it (a dead domain). | Add the missing space. |
| Hero | The banner reads "PREGNANT MAMA'S" with an apostrophe. | "PREGNANT MAMAS". |

## Copy swaps, top to bottom

**Top banner.** Keep. Optionally: "Attention PREGNANT MAMAS Who Want To Eat Well, Gain Less & Satisfy Cravings."

**Headline.** Now: "This Is HOW YOU EAT For A Healthy Baby & Fit Pregnancy."
Swap to one of:
- "The Pregnancy Diet Plan Is Now An App. It Tells You What To Eat Today."
- "Open It Every Morning. It Tells You What To Eat For A Healthy Baby & A Fit Pregnancy."
- Keep her headline and change only the sub-line: "Now an app on your phone: it tells you what to eat today, writes your grocery list, and reminds you to eat every 2 to 3 hours. No PDF to scroll."

**Button text.** "SEND ME THE MEAL PLAN!" implies a file. Swap to "GIVE ME THE APP" / "I WANT THE PLAN ON MY PHONE". Keep the first line of each button as is.

**Under the video.** Add one sentence after "…keeping momma in shape!": "And now it lives on your phone, so you never have to think about what's next."

**New section, right after the first testimonials (use `promo/before.png`).**
Heading: "From a PDF you scroll to an app that does the work."
Body: "Same plan I followed through two pregnancies. Same recipes. But now you open it in the morning and it tells you what to eat today, including snacks. It writes your grocery list by aisle. It turns tonight's dinner into tomorrow's lunch. And when you can't face fish this week, one tap swaps every fish dinner out."

**"THIS IS PERFECT FOR MAMAS WHO…"** Add a sixth line: "Are too tired or too nauseous to plan, and want someone to just tell them what to eat next."

**"YOU CAN HAVE A HEALTHY & FIT PREGNANCY… Even with food aversions, morning sickness…"** This is now literally a feature. Add: "The app has an aversion switch for fish, eggs, dairy and nuts, and a reminder to eat every 2 to 3 hours, which is the single biggest thing that keeps nausea down."

**What's Included (the three numbered blocks).** Replace the page-stack images with the phone images and rewrite the bullets around doing, not reading.

01 — was "Meal Plan Calendars". Now **"Your Day, Decided"** (image: `promo/today.png` or `promo/screen-today.png`)
- Open it in the morning and see breakfast, two snacks, lunch and dinner for today. Tick them off.
- Lunch is yesterday's dinner, already filled in. Cook once, eat twice.
- An "I just ate" button that tells you when the next bite is due. Eat every 2 to 3 hours without thinking about it.
- 8 weeks of plans that know what day it is, then they repeat.

02 — was "Recipe Cards". Now **"79 Recipes That Scale"** (image: `promo/cook.png` or `promo/screen-recipe.png`)
- 57 dinners, 14 baked snacks, 8 breakfasts. All 30 minutes or less, all "normal" grocery-store ingredients.
- Tap 1.5× or 2× and every amount rescales for leftovers.
- Tap an ingredient to cross it off while you cook. Save favourites. Search by ingredient.
- Can't face fish, eggs, dairy or nuts right now? Switch them off and every recipe that has them is flagged. Swap any dinner for one that works.

03 — was "Shopping Lists". Now **"Your Grocery List, Written For You"** (image: `promo/shop.png` or `promo/screen-shop.png`)
- One list per week, sorted by aisle. Tick as you shop. Hide what you have. Add your own.
- Two snack-baking lists for your Sunday batches.
- Copy it to your notes, text it to your husband, or print it.

Add a fourth block, **"Yours, On Your Phone"** (image: `promo/week.png`)
- Installs to your home screen in two taps. No app store, no login, works without signal in the store.
- Michelle's rules, the foods to avoid, the easy no-cook snacks, all in the Plan tab.
- Still want paper? Print any week, list or recipe.

**Price box.** Replace the PDF-stack mockup with `promo/hero.png` (or `promo/included.png` for a vertical layout). Bullets:
- The Pregnancy Diet Plan app: 8 weeks of daily meal plans that tell you what to eat today
- 79 scalable recipes with aversion filters and swaps
- 10 grocery lists by aisle, plus printable versions of everything
- Eat-every-2-to-3-hours reminder and water tracker

Keep "Total Value $97 / Regularly $47 / $37" for now. Honest note: the app is a bigger product than the PDF was, and the value stack should grow before Black Friday discounts it. See pricing below.

**FAQ rewrites** (the current answers were written for a PDF and three of them now undersell):
- *What if I'm a picky eater?* "Swap any dinner for any other with one tap. Favourite the ones you love and the app shows you your favourites first."
- *What if I have a lot of aversions?* "Tell the app what you can't stomach right now (fish, eggs, dairy, nuts). It flags every recipe that has it and offers swaps. Turn it back on when the aversion passes."
- *What if I'm too nauseous?* "Nausea gets worse when you're empty. The app reminds you to eat every 2 to 3 hours and keeps the snack list one tap away, which is exactly what you need on the bad days."
- *I work a lot, will I still be able to do this?* "The app writes the grocery list, you shop once, bake two batches of snacks on Sunday, and cook double at dinner. Lunch packs itself."
- Add: *Is it an app from the app store?* "No. It opens in your phone's browser and installs to your home screen in two taps. Nothing to download, no account, and it works offline. iPhone and Android."
- Add: *Can I still print it?* "Yes. Any week, any list, any recipe, from the app."

**Guarantee.** "Try the Pregnancy Diet Plan for 30 days. Open it every morning. Cook the recipes. Shop with the lists." Fix the $27.

**Sign-off paragraph.** Keep. Change "my Pregnancy Nutrition Plan" to "the Pregnancy Diet Plan app".

## Images: what goes where

| File | Size | Use |
|---|---|---|
| `promo/hero.png` | 3200×2000 | Price box mockup, Black Friday ad, email header |
| `promo/before.png` | 3200×2000 | New "From a PDF to an app" section |
| `promo/today.png` | 2400×2400 | Included block 01, Instagram |
| `promo/cook.png` | 2400×2400 | Included block 02, Instagram |
| `promo/shop.png` | 2400×2400 | Included block 03, Instagram |
| `promo/aversion.png` | 2400×2400 | Aversions section, Instagram, story |
| `promo/week.png` | 2400×2400 | Block 04, Instagram |
| `promo/included.png` | 2400×2400 | Dark variant for the price box or a Black Friday post |
| `promo/screen-*.png` | 780×1688 | Raw phone screens for Canva, stories, ads |

Everything is in the page's pink/purple/cream already. The phones show a real Friday in week 1 with breakfast and a snack ticked.

Replace, don't add: the three page-stack images and the "Pregnancy Diet Plan" PDF cover in the price box are the main reason the page reads as a PDF. The six broken icon boxes in the "Struggles Women Have" section on desktop also need images or removal.

## Pricing and the Black Friday angle

Three ways to frame it. Pick one before the sale, not during.

1. **Same price, bigger product.** $37 stays. The sale is "the app launched this week and Black Friday is the first time you can get it." The upgrade is the news. Lowest risk.
2. **Raise the anchor, sale back to $37.** Regularly $67 (it was $47 for a PDF; an app that plans your day is worth more), Black Friday $37. Only honest if $67 actually becomes the price afterwards.
3. **Bundle.** Diet Plan app + 21 Day Fit Pregnancy Challenge for one Black Friday price, with the Challenge calendar linking straight to the meal app on day 1. This is the one that feeds FMTB, because it puts both products in the same phone.

Past buyers: email them the app link free. It costs nothing, it earns the testimonials and screenshots the page needs, and the ask is "post a screenshot of your Today tab."

Talking points for stories (one per slide):
- "It tells you what to eat today. Including snacks."
- "It writes your grocery list. By aisle."
- "Cook dinner once. Tomorrow's lunch is already in there."
- "Can't face fish this week? One tap."
- "It nags you, nicely, to eat every 2 to 3 hours. That's the whole nausea secret."
- "No app store. No login. Two taps and it's on your home screen."

## Things I can't do from here

- Edit the FG Funnels page itself. I can write the exact blocks if you want them pasted.
- Replace the testimonials with app screenshots: none exist yet. First buyers will make them.
- Confirm the "200,000 women" claim or the TV logos. Left as is.
