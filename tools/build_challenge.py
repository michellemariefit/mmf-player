"""
Build data/challenge.json and the exercise photos for the 21 Day Fit Pregnancy Challenge player.

    pip install pypdf pdfplumber pillow numpy
    python tools/build_challenge.py

Inputs (tools/pdf/, ignored by git): the workout PDFs from Dropbox (PRODUCTS & PROGRAMS / 21 DAY
PREGNANCY CHALLENGE / PDF WORKOUTS), the two Week 2 PDFs from michellemariefit.com/wp-content,
and the three "3 Day Pregnancy Butt & Thighs Challenge_Day N.docx" files from FREEMIUMS.

What it does:
  1. The program (days, workouts, exercises, reps, YouTube demo IDs) is written out below. It was
     read off the PDFs, the FG lesson text and the docx files by hand, so a wrong number is a one-line fix.
  2. Every exercise photo in the PDFs is a "start -> end" composite: two polaroid frames with a blue
     arrow. The script pulls each composite out of the PDF (matched to its exercise by position on the
     page), splits it in two, trims the arrow and the white border, and writes
     images/<video id>-start.webp, -end.webp and -pdf.webp (the composite, untouched).
  3. Writes tools/review.html so every pair can be checked at a glance.

The original recordings behind the 2020 and 2022 photos were not found in Dropbox, so the photos
are the PDF ones. The 2022 PDFs (Week 3) have 1920x1080 composites; the 2020 ones are about 500 px
wide, so those pairs are soft. tools/overrides.json can point an exercise at a different photo file.
"""
import io, json, os, re, zipfile

import numpy as np
import pdfplumber
from PIL import Image
from pypdf import PdfReader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDFS = os.path.join(ROOT, "tools", "pdf")
IMAGES = os.path.join(ROOT, "images")
OUT = os.path.join(ROOT, "data", "challenge.json")
REVIEW = os.path.join(ROOT, "tools", "review.html")
os.makedirs(IMAGES, exist_ok=True)

# ---------------------------------------------------------------------------------------------
# The program. One entry per workout. `photos` says which PDF (and page order) each exercise's
# composite comes from; exercises are matched to images top to bottom on each page.
# Cues come from the FG lesson text (Michelle's own form notes).
# ---------------------------------------------------------------------------------------------
CUES = {
    "Dips": "Hands on a couch, table or chair, butt close to it. Feet far from your hands (closer makes it easier). Chest up, shoulders down. Bend the elbows to 90 degrees, press back up and squeeze the back of the arms.",
    "Dumbbell Rows": "Bend from the hips with a flat, arched back, almost parallel to the floor. Dumbbells hanging at your sides. Pull the elbows up and squeeze the shoulder blades together, then lower slowly.",
    "Plie Squats": "Feet wide, toes pointed out. Hold one or both dumbbells between the thighs. Chest up, hips tucked. Lower slowly as far as you can, then come up and squeeze inner thighs and butt.",
    "Dumbbell Shoulder Presses": "Dumbbells at shoulder height, palms facing in. Chest up, shoulder blades down. Press overhead until the arms are straight, then lower slowly.",
    "Dumbbell Shoulder Press": "Dumbbells at shoulder height, palms facing in. Chest up, shoulder blades down. Press overhead until the arms are straight, then lower slowly.",
    "Dumbbell Shoulder Press Neutral Grip": "Dumbbells at shoulder height, palms facing in. Chest up, shoulder blades down. Press overhead until the arms are straight, then lower slowly.",
    "Stability Ball Leg Curls": "Lie on your back, heels on the ball, hips lifted. Pull the ball in with your heels, then roll it back out under control. Keep the hips up the whole set.",
    "Stability Ball Single Leg Hip Extensions": "Upper back on the ball, hands on the floor. One foot up, the other flat with the knee at 90 degrees. Lift the hips and squeeze, lower until the butt almost touches the floor.",
    "Stability Ball Supine Single Leg Hip Extensions": "Upper back on the ball, hands on the floor. One foot up, the other flat with the knee at 90 degrees. Lift the hips and squeeze, lower until the butt almost touches the floor.",
    "Stability Ball Hip Extensions": "Upper back on the ball, feet flat, knees at 90 degrees. Lift the hips and squeeze the butt, then lower until it almost touches the floor.",
    "Hammer Curls": "Chest up, shoulders down. Dumbbells at your sides, palms facing in. Curl towards the shoulders, squeeze the front of the arms, lower slowly.",
    "Dumbbell Bicep Curls": "Chest up, shoulders down. Dumbbells at your sides, palms facing up. Curl towards the shoulders, squeeze, lower slowly.",
    "Twisting Bicep Curls": "Start with palms facing your legs. Curl and turn the palms up as you lift. Squeeze at the top, lower slowly.",
    "Squat": "Feet a little wider than shoulder width. Chest up, shoulders down. Sit back and down to about 90 degrees with a slight arch in the back. Stand up and squeeze the booty.",
    "Dumbbell Squats": "Feet a little wider than shoulder width, dumbbells at your sides. Chest up. Sit back and down to about 90 degrees. Stand up and squeeze the booty.",
    "Deadlifts": "Dumbbells in front of the thighs. Chest up, shoulders back. Hinge from the hips like a door, keep the lower back flat. Come up and squeeze the back of the legs and butt.",
    "Reverse Lunges": "Step one foot back onto the ball of the foot. Lower straight down, weight on the front heel, chest up. Push back up through the front leg and squeeze the butt.",
    "Stationary Lunges": "One foot in front of the other, back heel up. Lower as far as comfortable with the hips tucked and chest up. Push back up and squeeze the back leg glute.",
    "High Rows": "Bend from the hips, back flat and almost parallel to the floor, thumbs in. Pull the elbows up and out to make two 90 degree angles, squeeze the back, lower slowly.",
    "Upright Rows": "Dumbbells by the thighs. Chest up, shoulder blades down. Pull the elbows up and out, wrists straight. Lower slowly.",
    "Bowlers": "Stand on one leg, the other behind. Hinge forward and reach across to tap the floor by your foot, then come back up. It is a quick, flowing movement.",
    "Front Raises": "Dumbbells in front of the legs, palms facing you. Lift the arms to shoulder height with a soft elbow, then lower under control.",
    "Lateral Raises": "Dumbbells at your sides, soft elbows. Lift out to the sides to shoulder height, then lower slowly.",
    "Tricep Kickbacks Underhand": "Bend from the hips, chest up, back flat. Elbows tucked, palms facing forward. Extend the arms back and squeeze the back of the arms, then return.",
    "Tricep Kickbacks Overhand Grip": "Bend from the hips, chest up, back flat. Elbows tucked, palms facing back. Extend the arms back and squeeze the back of the arms, then return.",
    "Overhead Tricep Extensions": "Hold one dumbbell overhead with both hands. Elbows pointing forward, lower the weight behind your head, then press back up.",
    "Side Kicks": "Hold a wall or chair. Pivot the standing foot out and hinge slightly. Bend the knee of the working leg, then extend it out to the side and squeeze the side of the butt.",
    "Single Leg Squats": "Stand on one leg, the other just off the floor. Hold on to something if you need to. Sit back and down as far as comfortable, then stand and squeeze the glute.",
    "Lateral Lunges": "Step wide to one side and sit into that hip, the other leg straight. Chest up. Push back to standing.",
    "Walking Lunges": "Step forward and lower until both knees are at 90 degrees. Push through the front heel and step the back foot through into the next lunge.",
    "Single Leg Reaches": "Stand on one leg. Hinge forward and reach towards the floor while the other leg goes back. Squeeze the standing glute to come back up.",
    "Pushups Knees": "On your knees, hands a little wider than the shoulders. Lower the chest towards the floor and press back up. Keep the hips in line with the body.",
    "Tubing Chest Presses": "Band anchored behind you. Press both hands forward at chest height until the arms are straight, then return slowly.",
    "Tubing Chest Flys": "Band anchored behind you, arms wide with soft elbows. Bring the hands together in front of the chest, then open slowly.",
    "Dumbbell Reverse Flys": "Bend from the hips, back flat, dumbbells hanging. Lift the arms out to the sides and squeeze the shoulder blades, lower slowly.",
    "Dumbbell Straight Arm Pulls": "Bend from the hips, arms straight in front. Pull the dumbbells back towards the hips in an arc, squeeze the back, return slowly.",
    "Curtsy Lunges": "Step one foot back and across behind the other, like a curtsy. Lower, keeping the front knee over the foot, then push back up.",
    "Quadruped Bent Knee Hip Extensions": "On hands and knees, back flat. Lift one bent knee towards the ceiling, foot flat, squeeze the butt, lower without touching the floor.",
    "Quadruped Arm & Leg Extension": "On hands and knees. Reach one arm forward and the opposite leg back, hold for a second, return. Keep the belly drawn in.",
    "Quadruped Single Leg Hip Extensions In & Outs": "On hands and knees. Extend one leg back, then swing it out to the side and back in without lowering it.",
    "Side Plank with Hip Lifts": "On your forearm and knee or feet, hips stacked. Lower the hip towards the floor and lift it back up. Skip this if you have diastasis recti.",
}

# Template link IDs that were left behind when the 2022 PDFs were made from the Toned Arms PDF.
TEMPLATE_IDS = {"7FcLkHdf4Js", "RdnPNgzKTSU", "iJcMgzNCkV0", "XAsfEvsmSDg", "IvXGVym4t_Y", "WbuvVZAbhPY"}

def ex(name, video, reps="20", note="", **kw):
    e = {"name": name, "video": video, "reps": reps, "note": note}
    e.update(kw)
    return e

WORKOUTS = [
    # ---------------- Week 1 ----------------
    {"id": "w1-full-body", "week": 1, "name": "Full Body Fat Blast", "kind": "strength",
     "pdf": "Full Body Fat Blast Workout.pdf", "lessonVideo": "2MrlTKhl24k",
     "sets": 2, "setsLabel": "2 rounds, 3 if you have it in you", "reps": "20", "restSeconds": 75, "restLabel": "60 to 90 s", "circuit": True,
     "how": "Five exercises, one after the other, with as little rest as you can handle. Rest at the end of the circuit, then go again.",
     "gear": "dumbbells, stability ball, a chair or couch",
     "blocks": [{"label": "Circuit", "exercises": [
         ex("Dumbbell Rows", "p1XtX2cVNZc"), ex("Plie Squats", "Mywk7zS_We4"), ex("Dips", "RdnPNgzKTSU"),
         ex("Stability Ball Leg Curls", "XAYfZo9RJPY"), ex("Dumbbell Shoulder Presses", "nj0FUHY7rko")]}]},
    {"id": "w1-cardio-1", "week": 1, "name": "Cardio Fat Burning I", "kind": "cardio",
     "lessonVideo": "tMVQexQyfu4",
     "sets": 3, "setsLabel": "3 rounds, 2 is fine", "work": 60, "restSeconds": 0, "restLabel": "catch your breath", "circuit": True,
     "how": "60 seconds of each move, in order. Lateral shuffles come back between every exercise. Rest only as long as you need to catch your breath, then the next move. About 15 to 20 minutes.",
     "gear": "nothing",
     "blocks": [{"label": "Circuit", "exercises": [
         ex("Plie Squats", "", "60 s"), ex("Lateral Shuffles", "", "60 s"), ex("Squat with Back Kick", "", "60 s"), ex("Lateral Shuffles", "", "60 s"),
         ex("Walking Lunges", "", "60 s"), ex("Lateral Shuffles", "", "60 s"), ex("Plank Butt Kicks", "", "60 s", "Skip this one if you have diastasis recti"), ex("Lateral Shuffles", "", "60 s")]}]},
    {"id": "w1-arms", "week": 1, "name": "Toned Arms", "kind": "strength",
     "pdf": "Toned Arms Workout.pdf", "lessonVideo": "1Ty1ZnqnpjE",
     "sets": 2, "setsLabel": "2 rounds", "reps": "20", "restSeconds": 75, "restLabel": "60 to 90 s", "circuit": True,
     "how": "Six arm exercises back to back, 20 reps each. Rest after the last one, then go again. About 15 to 20 minutes.",
     "gear": "dumbbells, a chair or couch",
     "blocks": [{"label": "Circuit", "exercises": [
         ex("Dumbbell Shoulder Press Neutral Grip", "7FcLkHdf4Js"), ex("Dips", "RdnPNgzKTSU"), ex("Hammer Curls", "iJcMgzNCkV0"),
         ex("Lateral Raises", "XAsfEvsmSDg"), ex("Tricep Kickbacks Underhand", "IvXGVym4t_Y"), ex("Dumbbell Bicep Curls", "WbuvVZAbhPY")]}]},
    {"id": "w1-cardio-2", "week": 1, "name": "Cardio Fat Burning II", "kind": "cardio",
     "sets": 4, "setsLabel": "3 to 5 rounds", "work": 45, "restSeconds": 45, "restLabel": "same as the work", "circuit": True,
     "how": "30 to 60 seconds of each move, then rest the same amount of time. Go through all five, that is one round. 3 to 5 rounds to reach 15 to 20 minutes.",
     "gear": "nothing",
     "blocks": [{"label": "Circuit", "exercises": [
         ex("Plie Squats", "", "45 s"), ex("Lateral Shuffles", "", "45 s"), ex("Squat Kick", "", "45 s"), ex("Butt Kickers", "", "45 s"), ex("Lateral Lunges", "", "45 s")]}]},
    {"id": "w1-thighs", "week": 1, "name": "Slimming & Toning The Thighs", "kind": "strength",
     "pdf": "Slimming & Toning The Thighs Workout.pdf", "lessonVideo": "u6XovbrNPtQ",
     "sets": 2, "setsLabel": "2 rounds of each circuit", "reps": "20", "restSeconds": 75, "restLabel": "60 to 90 s", "circuit": True,
     "how": "Circuit A: three exercises in a row, rest, repeat. Then circuit B the same way. Drink water and stretch after.",
     "gear": "dumbbells",
     "blocks": [{"label": "A", "exercises": [ex("Dumbbell Squats", "6CbpPRbbDb8"), ex("Deadlifts", "q8RHLWKgRqY"), ex("Reverse Lunges", "6JMzQ2D9LDQ", "20 per side")]},
                {"label": "B", "exercises": [ex("Bowlers", "hYDdcmwFUY8"), ex("Side Kicks", "57V67yN3nh4", "20 per side")]}]},
    # ---------------- Week 2 ----------------
    {"id": "w2-full-body", "week": 2, "name": "Burn The Excess Fat Full Body", "kind": "strength",
     "pdf": "Burn The Excess Fat Full Body Workout.pdf", "lessonVideo": "0ExCZIR-HS0",
     "sets": 3, "setsLabel": "3 rounds, 4 if you can", "reps": "20", "restSeconds": 75, "restLabel": "60 to 90 s", "circuit": True,
     "how": "Five exercises in a circuit with minimal rest between them. Rest at the end, recover, repeat. 20 minutes of cardio after if you feel up to it.",
     "gear": "dumbbells, stability ball",
     "blocks": [{"label": "Circuit", "exercises": [
         ex("Stationary Lunges", "bLZPKMxGQ2o", "20 per side"), ex("High Rows", "b-BYZkIZwPQ"), ex("Stability Ball Supine Single Leg Hip Extensions", "3swvJ_oGOx4", "20 per side"),
         ex("Upright Rows", "3Sc_BEMB14I"), ex("Overhead Tricep Extensions", "uicoxUY-unM")]}]},
    {"id": "w2-cardio-1", "week": 2, "name": "Cardio Fat Killa I", "kind": "cardio",
     "lessonVideo": "Q8AfbDxqS6E",
     "sets": 2, "setsLabel": "2 rounds, 3 max", "work": 50, "restSeconds": 0, "restLabel": "catch your breath", "circuit": True,
     "how": "Seven exercises, 45 to 60 seconds each. Recover just enough to catch your breath between them. Complete the circuit 2 to 3 times. Follow Michelle in the video for the moves.",
     "gear": "nothing",
     "todo": "The seven exercises are only in the video. Add them here once Michelle lists them.",
     "blocks": [{"label": "Circuit", "exercises": [ex(f"Exercise {i}", "", "50 s", "Follow the video") for i in range(1, 8)]}]},
    {"id": "w2-arms", "week": 2, "name": "Sexy Prego Arms", "kind": "strength",
     "pdf": "Sexy-Prego-Arms-Workout_PDF-File.pdf", "lessonVideo": "3e7VlZZv-dA",
     "sets": 3, "setsLabel": "3 rounds, 4 if you can", "reps": "20", "restSeconds": 75, "restLabel": "60 to 90 s", "circuit": True,
     "how": "Back to back with minimal rest. Rest at the end of the circuit, catch your breath, begin again. About 15 minutes.",
     "gear": "dumbbells, a chair or couch",
     "blocks": [{"label": "Circuit", "exercises": [
         ex("Front Raises", "D3eIIeP0RcY"), ex("Tricep Kickbacks Overhand Grip", "nQy1waEKPhY"), ex("Twisting Bicep Curls", "gvYUU5lXQMc"),
         ex("Dumbbell Shoulder Press", "nj0FUHY7rko"), ex("Dips", "RdnPNgzKTSU"), ex("Hammer Curls", "iJcMgzNCkV0")]}]},
    {"id": "w2-cardio-2", "week": 2, "name": "Cardio Fat Killa II", "kind": "cardio",
     "sets": 3, "setsLabel": "2 to 5 rounds", "work": 50, "restSeconds": 0, "restLabel": "catch your breath", "circuit": True,
     "how": "Five exercises, 45 to 60 seconds each. Catch your breath between them, no long rests. 2 to 5 rounds to reach 15 to 20 minutes. Eaten protein and carbs an hour before? Good.",
     "gear": "nothing",
     "blocks": [{"label": "Circuit", "exercises": [
         ex("Quick Feet", "", "50 s"), ex("Reverse Lunges", "", "50 s"), ex("In & Out Quick Feet", "", "50 s"), ex("Running In Place", "", "50 s"), ex("Skiers", "", "50 s")]}]},
    {"id": "w2-butt", "week": 2, "name": "Tone & Lift The Prego Butt", "kind": "strength",
     "pdf": "Tone-Lift-The-Prego-Butt_PDF-File.pdf", "lessonVideo": "JzmB0YnQzWQ",
     "sets": 3, "setsLabel": "3 rounds, 4 if you can", "reps": "20", "restSeconds": 75, "restLabel": "60 to 90 s", "circuit": True,
     "how": "Back to back with minimal rest. Rest at the end, catch your breath, go again. Last workout of week 2: the hips and butt.",
     "gear": "dumbbells, stability ball, something to hold on to",
     "blocks": [{"label": "Circuit", "exercises": [
         ex("Lateral Lunges", "j6PWWcyeUno", "20 per side"), ex("Single Leg Squats", "CN4AyMsLts4", "20 per side"),
         ex("Stability Ball Hip Extensions", "ZxgZ7J5r8Sw"), ex("Side Kicks", "57V67yN3nh4", "20 to 30 per side")]}]},
    # ---------------- Week 3 ----------------
    {"id": "w3-back", "week": 3, "name": "Bra & Back Fat", "kind": "strength",
     "pdf": "Bra & Back Fat Prego Workout.pdf",
     "sets": 3, "setsLabel": "3 rounds of each circuit", "reps": "20", "restSeconds": 90, "restLabel": "90 s", "circuit": True,
     "how": "Two circuits of three. Do A1, A2, A3 in a row, rest 90 seconds, repeat twice more. Then the same with B. No cardio this week, five short weight workouts instead.",
     "gear": "resistance band or tubing, dumbbells",
     "blocks": [{"label": "A", "exercises": [ex("Tubing Chest Presses", "BTfQ536mJ34"), ex("Tubing Chest Flys", "2Y0TlHw_BhU"), ex("Pushups Knees", "vOPVNwnK5iA")]},
                {"label": "B", "exercises": [ex("Dumbbell Reverse Flys", "prQqq9R5Fso"), ex("Dumbbell Straight Arm Pulls", "hYnUMhkfVOc"), ex("Dumbbell Rows", "0JjGINr6jSg")]}]},
    {"id": "w3-butt-core", "week": 3, "name": "Butt & Core", "kind": "strength",
     "pdf": "Butt & Core Prego Workout.pdf",
     "sets": 2, "setsLabel": "2 rounds of each circuit", "reps": "20", "restSeconds": 90, "restLabel": "90 s", "circuit": True,
     "how": "Two circuits of three. A1 to A3 in a row, rest 90 seconds, one more round. Then B the same way.",
     "gear": "dumbbells, a mat",
     "blocks": [{"label": "A", "exercises": [ex("Curtsy Lunges", "4KBbFMIzh0Q", "20 per side"), ex("Quadruped Bent Knee Hip Extensions", "KrcFks4Ac50", "20 per side"), ex("Quadruped Arm & Leg Extension", "VIt03PSoH34", "20 per side")]},
                {"label": "B", "exercises": [ex("Lateral Lunges", "2smpeUvfg8s", "20 per side", photoFrom=("Tone-Lift-The-Prego-Butt_PDF-File.pdf", 0)),
                                             ex("Quadruped Single Leg Hip Extensions In & Outs", "NCqReUnN9tI", "20 per side"),
                                             ex("Side Plank with Hip Lifts", "wGKG_76FnOw", "10 per side", "Skip this one if you have diastasis recti")]}]},
    {"id": "w3-arms", "week": 3, "name": "Prego Lean Arms", "kind": "strength",
     "pdf": "Prego Lean Arms Workout.pdf",
     "sets": 3, "setsLabel": "3 rounds of each circuit", "reps": "20", "restSeconds": 90, "restLabel": "90 s", "circuit": True,
     "how": "Two circuits of three plus one finisher. A1 to A3 in a row, rest 90 seconds, repeat twice more. Then B. Then the kickbacks on their own.",
     "gear": "dumbbells, a mat",
     "blocks": [{"label": "A", "exercises": [ex("Front Raises", "f4FTCUD6F8Q"), ex("Hammer Curls", "Ko4In6Hca4E"), ex("Pushups Knees", "vOPVNwnK5iA")]},
                {"label": "B", "exercises": [ex("Overhead Tricep Extensions", "qLPaZ_qQ8uI"), ex("Lateral Raises", "A7g06iUnhT8"), ex("Twisting Bicep Curls", "gvYUU5lXQMc")]},
                {"label": "C", "exercises": [ex("Tricep Kickbacks Underhand", "NrIh6YCyfUo")]}]},
    {"id": "w3-legs", "week": 3, "name": "Lean Legs", "kind": "strength",
     "pdf": "Lean Legs Prego Workout.pdf",
     "sets": 3, "setsLabel": "3 rounds", "reps": "20", "restSeconds": 90, "restLabel": "90 s", "circuit": True,
     "how": "One circuit of four. Do them in a row, rest 90 seconds, repeat twice more.",
     "gear": "dumbbells, stability ball",
     "blocks": [{"label": "Circuit", "exercises": [ex("Walking Lunges", "Zt8MUV7N474", "20 per side"), ex("Stability Ball Leg Curls", "MBcIiW0W3c8"), ex("Squat", "rDL47VYziWo"), ex("Single Leg Reaches", "WVfg-Hizz50", "20 per side")]}]},
    {"id": "w3-burner", "week": 3, "name": "Full Body Burner", "kind": "strength",
     "sets": 2, "setsLabel": "2 rounds", "reps": "20", "restSeconds": 90, "restLabel": "90 s", "circuit": True,
     "how": "One long circuit of seven exercises. Do them all in a row, rest 90 seconds, one more round, and you are done.",
     "gear": "dumbbells, stability ball",
     "todo": "The PDF for this workout is a broken file in Dropbox (a saved 404 page) and the exercise list is only in the FG Files section. Fill in the seven exercises once Michelle sends the PDF.",
     "blocks": [{"label": "Circuit", "exercises": [ex(f"Exercise {i}", "", "20", "PDF needed") for i in range(1, 8)]}]},
    # ---------------- Bonus: 3 Day Butt & Thighs ----------------
    {"id": "bonus-day-1", "week": 0, "name": "3 Day Butt & Thighs · Day 1", "kind": "strength",
     "docx": "Day 1.docx",
     "sets": 3, "setsLabel": "2 to 3 rounds", "reps": "20", "restSeconds": 75, "restLabel": "60 to 90 s", "circuit": True,
     "how": "Four exercises in a row, rest 60 to 90 seconds, repeat. No band? Do them without it and add 10 reps to each.",
     "gear": "mini band, a mat",
     "blocks": [{"label": "Circuit", "exercises": [
         ex("Side Walking Plie Squats", "4o1eHeFCSDw", "10 per side"), ex("Bent Knee Band Hip Extensions", "KLZ-zMZ85Uw", "20"),
         ex("Side Lying Band Abductions", "OuZUC0_o0A0", "20 per side + 20 pulses"), ex("Flutters", "g4r8FJUKLCo", "1 minute", "Flutter 5 seconds, hold down 5 seconds, repeat for a minute")]}]},
    {"id": "bonus-day-2", "week": 0, "name": "3 Day Butt & Thighs · Day 2", "kind": "strength",
     "docx": "Day 2.docx",
     "sets": 3, "setsLabel": "2 to 3 rounds", "reps": "20", "restSeconds": 75, "restLabel": "60 to 90 s", "circuit": True,
     "how": "Five exercises in a row, rest 60 to 90 seconds, repeat.",
     "gear": "mini band, a mat",
     "blocks": [{"label": "Circuit", "exercises": [
         ex("Squat Kicks", "SwXQoySvqTQ", "20"), ex("Straight Leg Back Kicks", "YCZv2e3BNY8", "20 to 30 per side"),
         ex("Lying Hip Extensions with Abductions", "DOD-agA1G78", "20 + 20 abductions"), ex("Side Kicks", "1IbmT1hfDpo", "20 per side"),
         ex("The CAT", "xMZJcGfp2gY", "10", "Inhale 6 seconds and drop the belly, exhale 6 seconds and pull the belly in")]}]},
    {"id": "bonus-day-3", "week": 0, "name": "3 Day Butt & Thighs · Day 3", "kind": "strength",
     "docx": "Day 3.docx",
     "sets": 3, "setsLabel": "2 to 3 rounds", "reps": "20", "restSeconds": 75, "restLabel": "60 to 90 s", "circuit": True,
     "how": "Four exercises in a row, rest 60 to 90 seconds, repeat. Finish each round in the deep squat hold, breathing.",
     "gear": "mini band, a mat",
     "blocks": [{"label": "Circuit", "exercises": [
         ex("Reverse Lunges with Kick", "1MiyIDslZwg", "20 per side"), ex("Butterfly Hip Extensions", "bHpThj7mC18", "20 + 20 pulses"),
         ex("Standing Band Abductions", "KBemSo8sjr8", "20 per side"), ex("Deep Squat Hold", "wA2bvSLveeI", "1 minute", "Inhale 6 seconds and hold the deep squat, exhale 6 seconds pushing the knees out with the elbows")]}]},
]

# The 21 days. Habit lessons sit on days 1 to 7 alongside the Week 1 workouts (FG titles them
# "Day 1" to "Day 7" and the Week 1 workout schedule is Day 1 to 5 plus two rest days).
DAYS = [
    {"day": 1, "lesson": "day1", "workout": "w1-full-body"},
    {"day": 2, "lesson": "day2", "workout": "w1-cardio-1"},
    {"day": 3, "lesson": "day3", "workout": "w1-arms"},
    {"day": 4, "lesson": "day4", "workout": "w1-cardio-2"},
    {"day": 5, "lesson": "day5", "workout": "w1-thighs", "extra": "Optional: the Prego Core bonus video after this workout"},
    {"day": 6, "lesson": "day6", "workout": None, "title": "Rest day"},
    {"day": 7, "lesson": "day7", "workout": None, "title": "Rest day"},
    {"day": 8, "workout": "w2-full-body"},
    {"day": 9, "workout": "w2-cardio-1"},
    {"day": 10, "workout": "w2-arms"},
    {"day": 11, "workout": "w2-cardio-2"},
    {"day": 12, "workout": "w2-butt"},
    {"day": 13, "workout": None, "title": "Rest day"},
    {"day": 14, "workout": None, "title": "Rest day"},
    {"day": 15, "workout": "w3-back"},
    {"day": 16, "workout": "w3-butt-core"},
    {"day": 17, "workout": "w3-arms"},
    {"day": 18, "workout": "w3-legs"},
    {"day": 19, "workout": "w3-burner"},
    {"day": 20, "workout": None, "title": "Rest day", "extra": "Stretch, walk, drink water. Tomorrow you finish."},
    {"day": 21, "lesson": "celebrate", "workout": None, "title": "Celebrate & share your results"},
]

WEEKS = {1: {"name": "Week 1", "intro": "Healthy habits plus your first five workouts. 15 to 20 minutes each. Three strength, two cardio."},
         2: {"name": "Week 2", "intro": "Same rhythm, a little more. Three strength, two cardio."},
         3: {"name": "Week 3", "intro": "Five short weight workouts, no cardio. Strength is what preps you for labor and burns the most."},
         0: {"name": "Bonus: 3 Day Butt & Thighs", "intro": "Three mini band workouts for the hips, butt and thighs. Do them any time, all through pregnancy."}}


# ---------------------------------------------------------------------------------------------
# Photos
# ---------------------------------------------------------------------------------------------
def composites_from_pdf(path):
    """Composite images in page order, top to bottom: list of PIL images (exercise photos only)."""
    out = []
    reader = PdfReader(path)
    with pdfplumber.open(path) as pdf:
        for pi, page in enumerate(pdf.pages):
            if pi == 0:
                continue
            placed = [im for im in page.images
                      if im["srcsize"][0] > 300 and im["srcsize"][1] > 200 and not (im["srcsize"][0] > 1600 and im["srcsize"][1] < 300)]
            placed.sort(key=lambda im: im["top"])
            natives = {im.name.split(".")[0]: im.image for im in reader.pages[pi].images}
            for im in placed:
                key = im["name"]
                img = natives.get(key) or natives.get(key.split(".")[0])
                if img is None:   # fall back to any native with the same pixel size
                    img = next((v for v in natives.values() if v.size == tuple(im["srcsize"])), None)
                if img is not None:
                    out.append(img.convert("RGB"))
    return out


def composites_from_docx(path):
    out = []
    z = zipfile.ZipFile(path)
    names = sorted((n for n in z.namelist() if n.startswith("word/media/")),
                   key=lambda n: int(re.sub(r"\D", "", n) or 0))
    for n in names:
        try:
            img = Image.open(io.BytesIO(z.read(n)))
        except Exception:
            continue
        w, h = img.size
        if w < 300 or w > 700:     # banners and the logo are much bigger, icons smaller
            continue
        out.append(img.convert("RGB"))
    return out


def split_composite(im):
    """Two crops (start, end) from a 'photo -> photo' composite with a blue arrow on black."""
    a = np.asarray(im).astype(int)
    h, w = a.shape[:2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    nonblack = (r + g + b) > 70
    blue = (b > r + 50) & (b > g + 20) & (b > 120)
    content = nonblack & ~blue
    # the gap between the two photos: the emptiest column near the middle (ignore the arrow rows at the top)
    band = content[int(h * 0.4):, :].mean(0)
    lo, hi = int(w * 0.44), int(w * 0.56)
    cut = lo + int(np.argmin(band[lo:hi]))
    crops = []
    for x0, x1 in ((0, cut), (cut, w)):
        m = content[:, x0:x1]
        ys, xs = np.where(m)
        if len(xs) < 50:
            continue
        bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
        rows = m.sum(1)
        top = by0
        while top < by1 and rows[top] < 0.6 * (bx1 - bx0):   # rows that are only arrow
            top += 1
        bw, bh = bx1 - bx0, by1 - top
        px = int(bw * 0.075)
        crop = im.crop((x0 + bx0 + px, top + int(bh * 0.15), x0 + bx1 - px, by1 - int(bh * 0.08)))
        crops.append(crop)
    return crops


def save_webp(img, name, maxw=960):
    w, h = img.size
    if w > maxw:
        img = img.resize((maxw, int(h * maxw / w)), Image.LANCZOS)
    img.save(os.path.join(IMAGES, name), "WEBP", quality=84)
    return "images/" + name


def main():
    overrides = {}
    op = os.path.join(ROOT, "tools", "overrides.json")
    if os.path.exists(op):
        overrides = {k: v for k, v in json.load(open(op)).items() if not k.startswith("_")}

    cache = {}
    def comps(src):
        if src not in cache:
            p = os.path.join(PDFS, src)
            if not os.path.exists(p):
                cache[src] = []
            elif src.endswith(".docx"):
                cache[src] = composites_from_docx(p)
            else:
                cache[src] = composites_from_pdf(p)
        return cache[src]

    review = []
    for w in WORKOUTS:
        src = w.get("pdf") or w.get("docx")
        imgs = comps(src) if src else []
        i = 0
        code_n = 0
        for blk in w["blocks"]:
            for k, e in enumerate(blk["exercises"], 1):
                code_n += 1
                e["code"] = (blk["label"] + str(k)) if blk["label"] not in ("Circuit",) else str(code_n)
                if e["name"] in CUES and not e.get("cue"):
                    e["cue"] = CUES[e["name"]]
                vid = e.get("video")
                comp = None
                pf = e.pop("photoFrom", None)
                if pf:
                    alt = comps(pf[0])
                    comp = alt[pf[1]] if len(alt) > pf[1] else None
                    i += 1  # the PDF's own image for this slot is wrong, skip it
                elif src and i < len(imgs):
                    comp = imgs[i]; i += 1
                if comp is None or not vid:
                    continue
                if vid in overrides and overrides[vid].get("skip"):
                    continue
                pdfname = f"{vid}-pdf.webp"
                e["photo"] = save_webp(comp, pdfname)
                pair = split_composite(comp)
                if len(pair) == 2:
                    e["startPhoto"] = save_webp(pair[0], f"{vid}-start.webp")
                    e["endPhoto"] = save_webp(pair[1], f"{vid}-end.webp")
                    small = comp.size[0] < 900
                    review.append((w, e, comp.size, small))
        if src and i != len(imgs) and not w.get("todo"):
            print(f"note: {w['name']}: {len(imgs)} photos in {src}, {i} used")

    data = {"program": "21 Day Fit Pregnancy Challenge", "short": "21 Day Challenge",
            "weeks": [{"id": k, **v} for k, v in WEEKS.items()],
            "workouts": WORKOUTS, "days": DAYS}
    json.dump(data, open(OUT, "w"), indent=1, ensure_ascii=False)
    print("wrote", os.path.relpath(OUT, ROOT), len(WORKOUTS), "workouts,", len(review), "photo pairs")

    rows = []
    for n, (w, e, size, small) in enumerate(review, 1):
        rows.append(
            f'<div class="r {"small" if small else ""}" id="{e["video"]}"><h3><span class="n">{n}</span> {e["name"]} '
            f'<small>{w["name"]} · {e["code"]} · <code>{e["video"]}</code> · composite {size[0]}×{size[1]}{" · low res, from the 2020 PDF" if small else ""}</small></h3>'
            f'<div class="pics"><figure><img src="../{e["startPhoto"]}" loading="lazy"><figcaption>Start</figcaption></figure>'
            f'<figure><img src="../{e["endPhoto"]}" loading="lazy"><figcaption>End</figcaption></figure>'
            f'<figure class="c"><img src="../{e["photo"]}" loading="lazy"><figcaption>As in the PDF</figcaption></figure></div></div>')
    todo = "".join(f"<li><b>{w['name']}</b>: {w['todo']}</li>" for w in WORKOUTS if w.get("todo"))
    open(REVIEW, "w").write(
        "<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>21 Day Challenge · exercise photos to approve</title><style>body{font:15px/1.4 system-ui;margin:16px;max-width:1100px;color:#362d70}"
        ".r{margin-bottom:26px;border-top:1px solid #e6d9e2;padding-top:10px}.pics{display:grid;grid-template-columns:1fr 1fr 1.6fr;gap:8px;align-items:start}"
        "figure{margin:0;position:relative}img{width:100%;border-radius:8px;display:block}figure.c img{border:1px solid #ddd;background:#000}"
        "figcaption{position:absolute;left:8px;top:8px;background:#fff;padding:2px 6px;border-radius:4px;font-size:12px;font-weight:700}"
        "code{color:#dd2289}h3{font-size:16px;margin:0 0 8px}small{color:#777;font-weight:400;display:block;margin-top:2px}"
        ".n{display:inline-block;background:#dd2289;color:#fff;border-radius:6px;padding:2px 7px;margin-right:6px}.small h3 small{color:#b0295e}"
        "ul{background:#f8e4ed;padding:12px 12px 12px 30px;border-radius:10px}@media(max-width:700px){.pics{grid-template-columns:1fr 1fr}figure.c{grid-column:1/-1}}</style>"
        f"<h1>Check every pair ({len(review)})</h1>"
        "<p>Left is the start position, right is the end, third is the photo as it sits in the PDF today. "
        "Both halves are cut from that PDF photo, so they can only be as sharp as the PDF. Pairs marked in red come from the 2020 PDFs, "
        "where the photos are about 500 px wide. Tell me the number of any pair to swap, crop differently or drop.</p>"
        + (f"<h2>Still missing</h2><ul>{todo}</ul>" if todo else "") + "".join(rows))
    print("wrote tools/review.html")


if __name__ == "__main__":
    main()
