# What to fix in the members area, and what the player changes

Written 9 Nov 2026 after cataloguing the FG course, Dropbox and the sales page. Nothing live has been touched.

## Broken or wrong today

1. **Full Body Burner (Week 3, Workout 5) has no usable PDF.** The Dropbox file is a saved Dropbox 404 page named `.pdf`. The lesson text says "one long circuit of 7 exercises" and nothing else. The real list exists only in the FG lesson's Files section, which the API does not expose. The player shows seven placeholders until the PDF arrives.
2. **Cardio Fat Killa I (Week 2) has no exercise list** anywhere in text. Seven moves, only in the video. Same placeholder treatment.
3. **Lateral Lunges in the Butt & Core PDF shows the wrong photo.** The PDF displays the Dumbbell Reverse Flys photo (pool, bent over) under the Lateral Lunges title. The player uses the Lateral Lunges photo from the Tone & Lift The Prego Butt PDF instead.
4. **The 2022 PDFs carry hidden leftover links.** They were made by copying the Toned Arms PDF, and the old link rectangles (shoulder press, dips, hammer curls, lateral raises, kickbacks, bicep curls) are still on top of the new ones. Tapping a photo in the Bra & Back, Butt & Core, Lean Arms or Lean Legs PDF can open the wrong demo. The player uses the correct ids.
5. **Two Week 2 PDFs are not in Dropbox** (Sexy Prego Arms, Tone & Lift The Prego Butt). They only live on michellemariefit.com/wp-content. Copies are now in `tools/pdf/` locally; worth putting in Dropbox.
6. **Lesson text contradicts the PDFs on sets.** Full Body Fat Blast: lesson says "repeat 1 or 2 more times", PDF says 2 sets. Burn The Excess Fat: lesson says 3 to 4 rounds, PDF says 2. Prego Lean Arms: lesson says 3 sets, PDF says 2 (and 3 for the kickbacks). The player uses the lesson numbers where they disagree, with the PDF number as the "if that is all you have" option.
7. **The Celebrate lesson says "2 weeks" and "10 total workouts".** The course has three weeks of workouts (15). The sales page FAQ also says workouts start in week 2 and run 2 weeks. Decide which is true and make the copy match (see question 1).
8. **Every single Week 1 lesson ends with the same Fit Mom To Be 50OFF block**, and Day 2 promises coupons you "unlock as you go" that are the same code each time. Members notice. This is the upsell clutter that makes the area feel like a funnel, not a program.
9. **The Nutrition Tips lesson in the 3 Day bonus is a 1,500 word sales page** for mPower and the vitamins, with shop links every paragraph. The actual nutrition rules are five lines.
10. **Dead or stale links**: the Day 2 shop link is malformed (`collections/all-productstps://shop...`), the Day 3 affirmation cards point at a michellemariefit.com page, the Bonuses course embeds Teachable CDN PDFs from the old platform.
11. **Sales page promises not in the course**: a "Meal Planning & Prepping Hacks video", a diastasis recti bonus (FAQ 18). A 2018 meal prepping video and 8 diastasis recti recordings exist in Dropbox and could be added.

## Videos: keep, refilm, or delete

| Video | Where | Verdict |
| --- | --- | --- |
| 10 per-exercise demos per 2020 workout (lake) and the 2022 set (pool, turf) | YouTube, linked from PDFs | **Keep.** These are the exercise demos the player links to. Consistent, short, useful. |
| 5 follow-along workout videos (Full Body Fat Blast, Toned Arms, Thighs, Burn The Excess Fat, Sexy Arms, Tone & Lift Butt) | YouTube, embedded in lessons | **Optional.** The player makes them redundant for anyone using Play mode. Keep as "follow along with Michelle" if the quality holds up; otherwise drop. Nothing in the player depends on them. |
| Cardio videos (Fat Burning I, Fat Killa I) | YouTube | **Needed until the moves are written down.** Cardio Fat Killa I's list is only in the video. |
| Week 1 habit videos (Days 1B to 7) | YouTube, 2019 | **Refilm short.** They are the 2019 Module videos (500 MB to 1 GB originals in Dropbox). The player has notes for each, so a 60 to 90 second version per day is enough. |
| Module 1 Welcome, the two Walkthroughs | Dropbox | **Replace** with one 2 minute screen recording of the player: Play, List, Print, calendar, meals. |
| Equipment, Safety, Post-workout videos (FG hosted) | FG | **Keep**, add the notes (already in lessons.html). |
| 3 Day Butt & Thighs edited clips (14 mp4s) | Dropbox | **Upload to YouTube unlisted** if the current links break; they are the demo source for the bonus. |

## What the player does differently

- One calendar, 21 days, fixed order. Today is always one tap away. Progress and streak on the phone.
- Workouts tick by rounds, rest timers run themselves. Cardio runs a work timer per move.
- Photos come from Michelle's own PDF photos (start and end split apart), with her form cues from the lessons under each move.
- Meal plan pages are inside the app, not a Files download.
- Lesson notes mean nobody has to watch a 10 minute 2019 video to find out what to do.
- No upsell blocks. One line at Day 21 about Fit Mom To Be.

## Questions for Michelle

See the message that came with this file; the same list is kept here.

1. Is the challenge 21 days with habits running alongside the Week 1 workouts (what I built), or 7 habit days followed by 14 workout days (what the sales page FAQ says)? The course has three weeks of workouts, which only fits the first reading.
2. Please send the Full Body Burner PDF (or the list of its 7 exercises) and the 7 moves in Cardio Fat Killa I.
3. Where are the 2020 lake recordings and the 2022 pool recordings? They are not in the Dropbox folders I was given. With them, the Week 1 and 2 photos get sharp again (today they are 500 px crops).
4. Sets: do you want the lesson numbers (3 rounds in weeks 2 and 3) or the PDF numbers (2)? I used the lesson numbers.
5. Lateral Lunges in Butt & Core: keep the 2020 photo I substituted, or do you have a 2022 one?
6. The meal plan is a 2016 freebie (Pregnancy Without The Pounds). Is it still what you want members eating, or is this the moment to rebuild it: same meals, new design, a day-by-day view in the app with a tappable shopping list?
7. Which upsell do you want to keep, and where? One mention at Day 21 is my suggestion.
8. The FG Facebook group and Sparkle texts: still live? Day 1A depends on both.
9. Do you want the 3 Day Butt & Thighs bonus on the calendar (for example days 6, 13, 20) or left as a free extra?
10. Fit Mom To Be handoff: do you want the player to carry a "what happens after day 21" page that previews FMTB, so the next step is inside the app she already uses?
