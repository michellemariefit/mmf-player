"""
Build data/diet.json for the Pregnancy Diet Plan app from the PDFs in Dropbox.

    python tools/build_diet.py <folder>

<folder> holds (ignored by git, they are big):
  guide1.pdf   RAW FILES / Pregnancy Nutrition Guide1.pdf, the 1st edition (45 pages, real text):
               instructions, weeks 1 to 4, recipes 1 to 24, four snacks, the breakfasts.
  plan.pdf     MMF Pregnancy Diet Plan - Final.pdf, the 2nd edition (90 pages, flattened images):
               adds weeks 5 to 8 (recipes 25 to 54) and ten more snacks. Needs OCR (tesseract).
  pages/       plan.pdf rendered at 150 dpi: pdftoppm -r 150 -png plan.pdf pages/p
  docs/        the shopping list .docx drafts (Shopping Week N.docx, Snacks Shopping.docx, Baked Snacks Shopping.docx)

The output is one JSON file: weeks (7 days each: breakfast, lunch, dinner, with recipe ids), recipes
(number, name, sides, components with ingredients and instructions), snacks, breakfasts, shopping
lists by week and aisle, and the plan rules. tools/diet-fixes.json patches anything the OCR got wrong.
"""
import json, os, re, subprocess, sys, zipfile, html

import pdfplumber
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "tools", "diet-src")
OUT = os.path.join(ROOT, "data", "diet.json")
OCR_DIR = os.path.join(SRC, "ocr_cells")
os.makedirs(OCR_DIR, exist_ok=True)

DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def clean(s):
    s = s.replace("\x99", "").replace("\x92", "").replace("•", "").replace("ﬁ", "fi").replace("ﬂ", "fl")
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ------------------------------------------------------------------ 1st edition (real text)
def page_lines(p, x0=0, x1=9999, ytol=3):
    ws = [w for w in p.extract_words(x_tolerance=1.5, y_tolerance=2) if x0 <= w["x0"] < x1]
    rows = {}
    for w in ws:
        rows.setdefault(round(w["top"] / ytol), []).append(w)
    out = []
    for k in sorted(rows):
        r = sorted(rows[k], key=lambda w: w["x0"])
        out.append({"top": r[0]["top"], "x": r[0]["x0"], "h": r[0]["bottom"] - r[0]["top"], "text": " ".join(w["text"] for w in r)})
    return out


def parse_recipe_page(p):
    """A 1st-edition recipe or snack page: returns (heading, components).
    heading = {'number','name','sides'} or None. components = [{'title','servings','ingredients','instructions'}]"""
    left = [l for l in page_lines(p, 0, 300) if l["top"] > 60 and l["top"] < 740]
    right = [l for l in page_lines(p, 300, 9999) if l["top"] > 60 and l["top"] < 740]
    heading = None
    comps = []
    cur = None
    mode = None
    for l in left:
        t = clean(l["text"])
        if not t or t in ("Ingredients:", "SNACKS", "Breakfast Meals"):
            if t == "Ingredients:":
                mode = "ing"
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", t)
        if m and l["h"] > 13 and l["x"] < 45:
            heading = {"number": int(m.group(1)), "name": m.group(2).strip(), "sides": []}
            mode = "sides"; continue
        if mode == "sides" and l["h"] > 13 and l["x"] < 70:
            heading["sides"].append(t); continue
        if l["h"] > 17 and l["x"] > 80:   # centred box title
            cur = {"title": t, "servings": "", "ingredients": [], "instructions": []}
            comps.append(cur); mode = "title"; continue
        if cur is None:
            continue
        if mode == "ing":
            cur["ingredients"].append(t)
        elif mode == "title" and not cur["ingredients"]:
            # frittata page has no "Ingredients:" label: left column is steps
            cur["instructions"].append(t)
    # right column: servings and instructions, split by vertical position into the components
    tops = [c.get("_top", 0) for c in comps]
    for l in right:
        t = clean(l["text"])
        if not t or t == "Instructions:":
            continue
        m = re.search(r"\((\d[\d\s\-–]*)\s*Servings?\)", t)
        if m and l["h"] > 17:
            # attach to the component whose title sits on the same line
            c = min(comps, key=lambda c: abs(c.get("_top", -999) - l["top"])) if comps else None
            if c is not None:
                c["servings"] = m.group(1).strip()
            continue
        # which component: the last one whose box title is above this line
        c = None
        for cc in comps:
            if cc.get("_top", 0) <= l["top"]:
                c = cc
        if c is not None:
            c["instructions"].append(t)
    for c in comps:
        c.pop("_top", None)
    return heading, comps


def parse_recipe_page_positions(p):
    """A 1st-edition recipe, snack or breakfast page -> (heading, components).
    Titles are read full width (they are centred and cross the column split); ingredients come from
    the left column, instructions from the right, each assigned to the box whose title sits above."""
    full = [l for l in page_lines(p) if 60 < l["top"] < 740]
    heading, comps, headings = None, [], []
    for l in full:
        t = clean(l["text"])
        if not t or t in ("SNACKS", "Breakfast Meals"):
            continue
        m = re.match(r"^(\d+)\.\s+(.*)$", t)
        if m and 12 < l["h"] < 17 and l["x"] < 45:
            heading = {"number": int(m.group(1)), "name": m.group(2).strip(), "sides": [], "_top": l["top"], "_comps": []}
            headings.append(heading)
            continue
        if heading and 12 < l["h"] < 17 and l["x"] < 45 and l["top"] - heading["_top"] < 40:
            heading["name"] += " " + t; continue           # a heading that wrapped
        if heading and 12 < l["h"] < 17 and 50 <= l["x"] < 75 and l["top"] - heading["_top"] < 90:
            heading["sides"].append(t); continue
        if l["h"] >= 17 and l["x"] > 40:
            m2 = re.search(r"\((\d[\d\s\-–]*)\s*Servings?\)", t)
            title = re.sub(r"\(.*?Servings?\)", "", t).strip()
            if title.lower() in ("ingredients: instructions:",):
                continue
            if comps and abs(comps[-1]["_top"] - l["top"]) < 6:      # the servings sat on its own line
                comps[-1]["title"] = (comps[-1]["title"] + " " + title).strip()
                comps[-1]["servings"] = comps[-1]["servings"] or (m2.group(1).strip() if m2 else "")
                continue
            comps.append({"title": title, "servings": m2.group(1).strip() if m2 else "", "ingredients": [], "instructions": [], "_top": l["top"]})
            if heading:
                heading["_comps"].append(comps[-1])
    def owner(top):
        c = None
        for cc in comps:
            if cc["_top"] <= top + 2:
                c = cc
        return c
    for l in page_lines(p, 0, 300):
        t = clean(l["text"])
        if not (60 < l["top"] < 740) or not t or l["h"] >= 17 or t.startswith("Ingredients") or t in ("SNACKS", "Breakfast Meals"):
            continue
        if re.match(r"^\d+\.\s", t) or (heading and (l["x"] < 45 or 50 <= l["x"] < 75) and 12 < l["h"] < 17):
            continue
        c = owner(l["top"])
        if c is not None:
            c["ingredients"].append(t)
    for l in page_lines(p, 300, 9999):
        t = clean(l["text"])
        if not (60 < l["top"] < 740) or not t or l["h"] >= 17 or t.startswith("Instructions"):
            continue
        c = owner(l["top"])
        if c is not None:
            c["instructions"].append(t)
    for c in comps:
        c.pop("_top", None)
        # the frittata has no ingredients list: its left column is steps too
        if c["title"].startswith("Vegetable Frittata"):
            c["instructions"] = join_steps(c["ingredients"] + c["instructions"]); c["ingredients"] = []
        else:
            c["instructions"] = join_steps(c["instructions"])
    if headings:
        out = []
        for hd in headings:
            hc = hd.pop("_comps"); hd.pop("_top", None)
            out.append((hd, hc))
        return out
    return [(None, comps)]


def join_steps(lines):
    """OCR/extracted instruction lines -> list of steps. A new step starts after a bullet or a full stop at a line end."""
    steps, cur = [], ""
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("•") or ln.startswith("- "):
            if cur:
                steps.append(cur.strip())
            cur = ln.lstrip("•- ").strip()
        else:
            cur = (cur + " " + ln).strip() if cur else ln
    if cur:
        steps.append(cur.strip())
    # split long single steps on sentence ends
    out = []
    for s in steps:
        parts = re.split(r"(?<=[.!])\s+(?=[A-Z])", s)
        out.extend(p.strip() for p in parts if p.strip())
    return out


def parse_calendar_pdf(p):
    """A 1st-edition calendar page (landscape). Returns {day: {breakfast, lunch, dinner}} with cell items."""
    ws = p.extract_words(x_tolerance=1.5, y_tolerance=2)
    heads = {w["text"]: w for w in ws if w["text"] in ("Sun", "Mon", "Tue", "Wed", "Thur", "Fri", "Sat")}
    xs = sorted((heads[d]["x0"] + heads[d]["x1"]) / 2 for d in heads)
    bounds = [(xs[i] + xs[i - 1]) / 2 if i else 95 for i in range(7)] + [800]
    snack_tops = sorted({round(w["top"]) for w in ws if w["text"] == "Choose"})
    snack_bots = sorted({round(w["bottom"]) for w in ws if w["text"] == "Options"})
    rows = [("breakfast", heads["Sun"]["bottom"] + 2, snack_tops[0] - 2), ("lunch", snack_bots[0] + 2, snack_tops[1] - 2), ("dinner", snack_bots[1] + 2, 600)]
    cal = {d: {} for d in DAYS}
    for di in range(7):
        for name, y0, y1 in rows:
            cell = [w for w in ws if bounds[di] <= (w["x0"] + w["x1"]) / 2 < bounds[di + 1] and y0 <= w["top"] < y1 and w["x0"] >= 95]
            cell.sort(key=lambda w: (round(w["top"] / 3), w["x0"]))
            lines, last = [], None
            for w in cell:
                k = round(w["top"] / 3)
                if k != last:
                    lines.append(""); last = k
                lines[-1] += (" " if lines[-1] else "") + w["text"]
            cal[DAYS[di]][name] = split_cell(lines)
    return cal


def split_cell(lines):
    """Cell lines -> list of items. Items start with a bullet glyph (\x99) in the PDF; otherwise one item."""
    items, cur = [], ""
    for ln in lines:
        ln = ln.strip()
        if "\x99" in ln or ln.startswith("•"):
            if cur:
                items.append(clean(cur))
            cur = clean(ln)
        else:
            cur = (cur + " " + ln) if cur else ln
    if cur:
        items.append(clean(cur))
    # "Dinner Leftovers:" prefix becomes a flag
    out = []
    for it in items:
        it = it.replace("Dinner Leftovers:", "").strip()
        if it:
            out.append(it)
    return out


# ------------------------------------------------------------------ 2nd edition (OCR)
def ocr(img, psm=6):
    tmp = os.path.join(OCR_DIR, "tmp.png")
    img.save(tmp)
    r = subprocess.run(["tesseract", tmp, "stdout", "--psm", str(psm)], capture_output=True, text=True)
    return r.stdout


def fix_ocr(s):
    for a, b in (("¥Y,", "¼"), ("¥Y", "¼"), ("Y,", "¼"), ("¥,", "¼"), ("¼,", "¼"), ("%%/", "¾"), ("%/", "¾"), ("¥/", "½"), ("¥%", "½"), ("Y%", "½"), ("¥", "½")):
        s = s.replace(a, b)
    s = re.sub(r"\b(\d)%(?=\s*(cup|tsp|tbsp|lb|teaspoon|tablespoon))", r"\1½", s)
    s = re.sub(r"(?<![\d])%(?=\s*(cup|tsp|tbsp|lb|onion))", "½", s)
    s = re.sub(r"\b1egg\b|\blege\b", "1 egg", s)
    s = s.replace("¥,", "¼").replace("¥2", "½").replace("Y2", "½").replace("Ys", "⅓").replace("%,", "¾").replace("Vs", "⅓").replace("V2", "½").replace("V4", "¼")
    s = re.sub(r"\bl\b(?=\s*(cup|tsp|tbsp|lb))", "1", s)
    s = s.replace("|", "").replace("’", "'")
    for a, b in (("30wl", "Bowl"), ("furkey", "Turkey"), ("toasted Veggies", "Roasted Veggies"), ("Morracan", "Moroccan"), ("Rasberry", "Raspberry")):
        s = s.replace(a, b)
    return clean(s)


def ocr_page_cached(n, side, box, psm=6):
    f = os.path.join(OCR_DIR, f"p{n:02d}{side}.txt")
    if os.path.exists(f):
        return open(f).read()
    im = Image.open(os.path.join(SRC, "pages", f"p-{n:02d}.png"))
    t = ocr(im.crop(box), psm)
    open(f, "w").write(t)
    return t


def parse_ocr_recipe_pages(pages):
    """2nd-edition recipe/snack pages. Returns list of (heading, components) per page.
    Left crop = numbers, sides, ingredients. Right crop = instructions. Full page = box titles with servings."""
    results = []
    for n in pages:
        im = Image.open(os.path.join(SRC, "pages", f"p-{n:02d}.png")); w, h = im.size
        L = ocr_page_cached(n, "L", (0, int(h * 0.05), int(w * 0.47), int(h * 0.92)))
        R = ocr_page_cached(n, "R", (int(w * 0.47), int(h * 0.05), w, int(h * 0.92)))
        F = ocr_page_cached(n, "F", (0, int(h * 0.05), w, int(h * 0.92)), psm=4)
        # box titles from the full page: a line in caps, optionally with (N Servings)
        titles = []
        for ln in F.splitlines():
            t = clean(ln)
            t = re.sub(r"^[^A-Z0-9(]+", "", t)                      # leading dashes and box corners
            t = re.sub(r"^(A|SE|LA|RE|BO)\s+(?=[A-Z]{3})", "", t)   # stray letters read off the pink corner
            t = re.sub(r"\s+(Ly|Ky|La|LA|Lh|LY|KY|i|a|ee|Oo|OO|ea)\)?\s*$", "", t)
            m = re.search(r"([A-Z][A-Z0-9&'’,\-\.\s]{5,}?)\s*\((?:\d[\d\s\-–]*)\s*[Ss]ervings?\)", t) or re.search(r"([A-Z][A-Z0-9&'’,\-\.\s]{5,}?)\s*\((?:Makes[^)]*)\)", t)
            if not m and re.match(r"^[^a-z]*$", t) and len(re.findall(r"[A-Z]{3,}", t)) >= 2 and not re.search(r"MICHELLE|WEEK|SNACKS|GUIDE", t):
                m = re.match(r"^(.*)$", t)
            if m and not re.search(r"Nutrition Guide|MICHELLE|WEEK \d|SNACKS", t):
                sm = re.search(r"\((\d[\d\s\-–]*)\s*[Ss]ervings?\)", t) or re.search(r"\(Makes\s*([^)]*?)\.?\)", t)
                name = re.sub(r"[^A-Za-z0-9&'’,\-\.\s]", " ", m.group(1)).strip(" -—_|.")
                name = re.sub(r"^(SE|LA|RE)\s+", "", name).strip()
                if len(name) > 5:
                    titles.append({"title": name.title().replace("'S", "'s").replace("’S", "’s"), "servings": sm.group(1).strip() if sm else ""})
        heading, comps = None, []
        cur, mode = None, None
        ti = 0
        for ln in L.splitlines():
            t = fix_ocr(ln)
            if not t or re.search(r"Nutrition Guide|MICHELLE|^MARIE|^FIT$|^WEEK \d|^SNACKS", t, re.I):
                continue
            m = re.match(r"^(\d{1,2})[\.\,]\s+(.*)$", t)
            if m and cur is None and heading is None:
                heading = {"number": int(m.group(1)), "name": m.group(2).strip(), "sides": []}; mode = "sides"; continue
            if heading and mode == "sides" and cur is None and not re.match(r"^[^a-z]*$", t) and not re.match(r"^Ingredients", t, re.I):
                heading["name"] += " " + t; continue      # the heading wrapped onto another line
            if re.match(r"^Ingredients", t, re.I):
                cur = {"title": titles[ti]["title"] if ti < len(titles) else "", "servings": titles[ti]["servings"] if ti < len(titles) else "", "ingredients": [], "instructions": []}
                ti += 1; comps.append(cur); mode = "ing"; continue
            if mode == "sides":
                continue
            if mode == "ing" and cur is not None:
                if re.match(r"^[A-Z0-9&'’,\-\s]{8,}$", t) and len(t.split()) >= 2:   # a second box title leaked into the left crop
                    continue
                cur["ingredients"].append(t)
        # instructions: split the right crop at "Instructions" markers
        blocks = re.split(r"(?i)instructions\s*:?", R)[1:]
        if not comps and blocks and heading:
            comps.append({"title": heading["name"], "servings": "", "ingredients": [], "instructions": []})
        for i, b in enumerate(blocks):
            lines = [fix_ocr(x) for x in b.splitlines()]
            lines = [x for x in lines if x and not re.search(r"Nutrition Guide|MICHELLE|^MARIE|^FIT$|Servings\)|^[A-Z0-9&'’,\-\s]{10,}$", x)]
            if i < len(comps):
                comps[i]["instructions"] = join_steps(lines)
        for c in comps:
            c["title"] = re.sub(r"\s+(Ly|Ky|La|Lh)$", "", c["title"]).replace("Ricesalad", "Rice Salad").replace("Bbq", "BBQ").replace("Tex-Mexturkey", "Tex-Mex Turkey")
            if not c["title"] and heading:
                c["title"] = heading["name"]
        if heading:
            heading["name"] = re.sub(r"\s*[“\"].*$", "", heading["name"]).replace("Tex-MexTurkey", "Tex-Mex Turkey").replace("SouthWestern", "Southwestern")
        results.append((n, heading, comps))
    return results


def calendar_rows(im):
    """Row bands of a 2nd-edition calendar page. The cells are light grey, so every row shows up as a
    band of grey pixels across the day columns, separated by thin white gaps. After the dark header
    the bands run breakfast, snack, lunch, snack, dinner."""
    import numpy as np
    a = np.asarray(im.convert("L"))
    grey = (a[:, 185:1210] < 215).mean(1) > 0.95
    groups, start, prev = [], None, None
    for y in np.where(grey)[0]:
        if start is None:
            start = y
        elif y != prev + 1:
            groups.append((start, prev)); start = y
        prev = y
    if start is not None:
        groups.append((start, prev))
    bands = [g for g in groups if g[0] > 459 and g[1] - g[0] > 20]
    names = ["breakfast", "snack", "lunch", "snack", "dinner"]
    return {n: (int(b[0]), int(b[1])) for n, b in zip(names, bands) if n != "snack"}


def parse_ocr_calendar(n):
    """Weeks 5 to 8 calendar pages: OCR each cell of the grid (binarised and enlarged)."""
    im = Image.open(os.path.join(SRC, "pages", f"p-{n:02d}.png"))
    cols = [178, 333, 483, 634, 790, 940, 1080, 1216]      # Sun .. Sat on the 150 dpi render
    rows = calendar_rows(im)
    cal = {d: {} for d in DAYS}
    for di in range(7):
        for name, (y0, y1) in rows.items():
            key = f"c{n}_{di}_{name}_v3"
            f = os.path.join(OCR_DIR, key + ".txt")
            if os.path.exists(f):
                t = open(f).read()
            else:
                crop = im.crop((cols[di] + 3, y0 + 2, cols[di + 1] - 3, y1 - 2)).convert("L")
                crop = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
                crop = crop.point(lambda v: 0 if v < 150 else 255)
                t = ocr(crop, 6); open(f, "w").write(t)
            lines = [fix_ocr(x) for x in t.splitlines() if fix_ocr(x)]
            items, cur = [], ""
            for ln in lines:
                starts = bool(re.match(r"^[^A-Za-z0-9]{1,3}\s*[A-Z]", ln)) or ln.lower().startswith("dinner leftovers")
                if starts and cur:
                    items.append(cur)
                    cur = re.sub(r"^[^A-Za-z0-9]+", "", ln)
                else:
                    cur = (cur + " " + re.sub(r"^[^A-Za-z0-9]+", "", ln)).strip() if cur else re.sub(r"^[^A-Za-z0-9]+", "", ln)
            if cur:
                items.append(cur)
            clean_items = []
            for it in items:
                it = re.sub(r"^Dinner Leftovers:?\s*", "", it, flags=re.I).strip()
                it = re.sub(r"\s*Choose from Snack Option.*$", "", it, flags=re.I).strip()
                if it and it.lower() not in ("dinner leftovers", "dinner leftovers:"):
                    clean_items.append(it)
            cal[DAYS[di]][name] = clean_items
    return cal


# ------------------------------------------------------------------ shopping lists (docx)
AISLES = ["Dairy", "Spices & Baking", "Spices and Baking", "Canned Goods", "Grains", "Produce", "Condiments", "Frozen Foods", "Protein", "Misc.", "Misc"]


def docx_lines(path):
    z = zipfile.ZipFile(path)
    x = z.read("word/document.xml").decode("utf8")
    x = re.sub(r"</w:p>", "\n", x); x = re.sub(r"</w:tc>", "\n", x)
    t = html.unescape(re.sub(r"<[^>]+>", "", x))
    return [l.strip() for l in t.splitlines() if l.strip()]


def parse_shopping(path):
    lists, cur, aisle = [], None, None
    for ln in docx_lines(path):
        if re.match(r"^(MMF )?(Shopping List|Shopping List for|MMF Shopping List)", ln, re.I) or re.match(r"^MMF Baked Snacks|^Snacks Shopping List", ln, re.I):
            m = re.search(r"Week\s*(\d)", ln)
            cur = {"title": ln.strip(), "week": int(m.group(1)) if m else None, "aisles": {}}
            lists.append(cur); aisle = None; continue
        if cur is None:
            continue
        if ln.rstrip(".") in [a.rstrip(".") for a in AISLES]:
            aisle = ln.replace("Spices and Baking", "Spices & Baking").rstrip(".") or "Misc"
            if aisle == "Misc":
                aisle = "Misc"
            cur["aisles"].setdefault(aisle, []); continue
        if aisle:
            # some cells hold several items separated by big gaps
            for item in re.split(r"\s{3,}", ln):
                item = item.strip()
                if item and item not in cur["aisles"][aisle]:
                    cur["aisles"][aisle].append(item)
    return lists


def main():
    data = {"program": "MMF Pregnancy Diet Plan", "weeks": [], "recipes": [], "snacks": [], "breakfasts": [], "shopping": {}, "rules": {}}

    # ---- 1st edition: instructions, weeks 1-4, recipes 1-24, snacks, breakfasts
    with pdfplumber.open(os.path.join(SRC, "guide1.pdf")) as pdf:
        txt = lambda n: pdf.pages[n - 1].extract_text() or ""
        def cols(n):
            """Pages 2-4 are two text columns; read left then right, drop the running header lines."""
            pg = pdf.pages[n - 1]; out = []
            for bb in ((0, 0, pg.width / 2, pg.height), (pg.width / 2, 0, pg.width, pg.height)):
                for l in (pg.within_bbox(bb).extract_text() or "").split("\n"):
                    l = clean(l)
                    if not l or l.isdigit() or re.match(r"^(Pregnancy [NM]|Instr|trition Guide|ctions|al Plan Steps)", l): continue
                    out.append(l)
            return out
        def paras(lines):
            """Lines -> paragraphs. A paragraph ends at a line that closes with a full stop and is followed by a new sentence."""
            ps, cur = [], ""
            for l in lines:
                cur = (cur + " " + l).strip()
                if re.search(r"[.!?:]$", l) or l.endswith("key!"):
                    ps.append(cur); cur = ""
            if cur: ps.append(cur)
            return ps
        data["rules"]["intro"] = paras(cols(2))
        data["rules"]["how"] = paras(cols(3))
        steps = re.split(r"\s(?=\d{1,2}\.\s)", " ".join(cols(4)))
        data["rules"]["steps"] = [clean(s) for s in steps if re.match(r"^\d{1,2}\.", clean(s))]
        avoid = [clean(l).lstrip("Î ").strip() for l in txt(5).split("\n")[2:] if clean(l).lstrip("Î ").strip()]
        data["rules"]["avoid"] = [a for a in avoid if a and not a.isdigit()]
        cal_pages = {1: 6, 2: 15, 3: 22, 4: 29}
        for wk, pn in cal_pages.items():
            data["weeks"].append({"week": wk, "days": parse_calendar_pdf(pdf.pages[pn - 1])})
        recipe_pages = list(range(9, 15)) + list(range(17, 22)) + list(range(24, 29)) + list(range(31, 37))
        for pn in recipe_pages:
            for heading, comps in parse_recipe_page_positions(pdf.pages[pn - 1]):
                if heading:
                    data["recipes"].append({**heading, "week": 1 + (heading["number"] - 1) // 6, "components": comps, "source": f"guide1 p{pn}"})
        for pn in range(38, 42):
            for _, comps in parse_recipe_page_positions(pdf.pages[pn - 1]):
                for c in comps:
                    data["snacks"].append({**c, "source": f"guide1 p{pn}"})
        # breakfasts: p42 list + recipes on 42-45
        data["rules"]["breakfastList"] = ["Banana Split Oatmeal and Scrambled Egg Whites", "Regular Oatmeal and Veggie Egg White Omelet",
            "Gluten-Free Toast or English Muffin with Scrambled Egg Whites and Cottage Cheese", "Protein Smoothie", "Oatmeal Pancakes",
            "Egg White Veggie Frittata and Oatmeal", "Egg White Veggie Frittata and Gluten-Free Toast"]
        for pn in range(42, 46):
            for _, comps in parse_recipe_page_positions(pdf.pages[pn - 1]):
                for c in comps:
                    if c["ingredients"] or c["instructions"]:
                        data["breakfasts"].append({**c, "source": f"guide1 p{pn}"})

    # ---- 2nd edition: snacks 2 (pages 12-20) and weeks 5-8
    snack_pages = list(range(12, 21))
    norm = lambda t: re.sub(r"^\d+\s*", "", t.lower()).replace("rasberry", "raspberry").strip()
    for n, heading, comps in parse_ocr_recipe_pages(snack_pages):
        for c in comps:
            c["title"] = re.sub(r"^\d+\s*", "", c["title"]).replace("Rasberry", "Raspberry")
            if c["title"] and not any(norm(s["title"]) == norm(c["title"]) for s in data["snacks"]):
                data["snacks"].append({**c, "source": f"plan p{n}"})
    week_pages = {5: (52, list(range(54, 62))), 6: (62, list(range(64, 71))), 7: (71, list(range(73, 82))), 8: (82, list(range(84, 91)))}
    for wk, (cal_pn, rps) in week_pages.items():
        data["weeks"].append({"week": wk, "days": parse_ocr_calendar(cal_pn)})
        for n, heading, comps in parse_ocr_recipe_pages(rps):
            if heading:
                data["recipes"].append({**heading, "week": wk, "components": comps, "source": f"plan p{n}"})
            elif comps:
                # a continuation page: add the components to the previous recipe
                if data["recipes"]:
                    data["recipes"][-1]["components"].extend(comps)

    # ---- shopping lists
    docs = os.path.join(SRC, "docs")
    for f in sorted(os.listdir(docs)):
        if f.endswith(".docx") and ("Shopping" in f):
            for lst in parse_shopping(os.path.join(docs, f)):
                key = f"week{lst['week']}" if lst["week"] else ("baked-snacks" if "Baked" in lst["title"] else "snacks")
                data["shopping"][key] = lst

    # ---- fixes written by hand after reviewing
    fx = os.path.join(ROOT, "tools", "diet-fixes.json")
    if os.path.exists(fx):
        fixes = json.load(open(fx))
        for r in data["recipes"]:
            f = fixes.get("recipes", {}).get(str(r["number"]))
            if f:
                r.update(f)
        for s in data["snacks"] + data["breakfasts"]:
            f = fixes.get("snacks", {}).get(s["title"])
            if f:
                s.update(f)
        for w in data["weeks"]:
            f = fixes.get("weeks", {}).get(str(w["week"]))
            if f:
                for d, v in f.items():
                    w["days"].setdefault(d, {}).update(v)

        data["easySnacks"] = fixes.get("easySnacks", [])
        for r in data["recipes"]:
            r.pop("source", None)

    # ---- link every calendar item to the recipes it names, so the app can open them
    STOP = {"with", "and", "or", "the", "a", "of", "over", "&", "grilled", "baked", "brown", "rice", "jasmine", "salad", "greens", "roasted", "veggies", "vegetables", "side", "your", "choice", "any", "quinoa"}
    def toks(t):
        return {w for w in re.findall(r"[a-z]+", t.lower()) if w not in STOP and len(w) > 2}
    def find(text):
        t = text.lower(); best = []
        for r in data["recipes"]:
            names = [r["name"]] + [c["title"] for c in r["components"]]
            for nm in names:
                n = nm.lower()
                if len(n) > 5 and (n in t or t in n):
                    best.append(r["number"]); break
                rt = toks(nm)
                if rt and len(rt & toks(text)) / len(rt) >= 0.75 and len(rt) >= 2:
                    best.append(r["number"]); break
        return sorted(set(best))
    for w in data["weeks"]:
        for d, meals in w["days"].items():
            for meal in ("lunch", "dinner"):
                if meals.get(meal + "Ids"):
                    continue                      # set by hand in diet-fixes.json
                items = meals.get(meal, [])
                ids = []
                for it in items:
                    for i in find(it):
                        if i not in ids:
                            ids.append(i)
                # prefer recipes from the same week when a name matches several
                same = [i for i in ids if any(r["number"] == i and r["week"] == w["week"] for r in data["recipes"])]
                meals[meal + "Ids"] = same or ids
            b = " ".join(meals.get("breakfast", []))
            meals["breakfastIds"] = [s["title"] for s in data["breakfasts"] if s["title"].lower().split(" protein")[0] in b.lower() and len(s["title"]) > 8]
    # recipe tags from the ingredients, for the aversion filters
    def tags(r):
        txt = " ".join(i for c in r["components"] for i in c["ingredients"]).lower() + " " + r["name"].lower()
        out = []
        if re.search(r"chicken", txt): out.append("chicken")
        if re.search(r"turkey", txt): out.append("turkey")
        if re.search(r"fish|salmon|tuna|shrimp|scallop", txt): out.append("fish")
        if re.search(r"steak|flank", txt): out.append("beef")
        if re.search(r"\begg", txt): out.append("eggs")
        if re.search(r"cheese|yogurt|feta|parmesan|mozzarella|cottage|milk(?! almond)|sour cream", txt) and not re.search(r"dairy free|non-dairy|dairy-free", txt): out.append("dairy")
        if re.search(r"almond|walnut|cashew|pine nut|pecan|nut butter|peanut", txt): out.append("nuts")
        if not any(x in out for x in ("chicken", "turkey", "fish", "beef")): out.append("meatless")
        return out
    for r in data["recipes"]:
        r["tags"] = tags(r)
    for s in data["snacks"]:
        s["tags"] = tags({"components": [s], "name": s["title"]})

    json.dump(data, open(OUT, "w"), indent=1, ensure_ascii=False)

    # ---- review page: every PDF page beside what was read off it
    pages = {}
    for r in data["recipes"]:
        pass
    rows = []
    for n in range(1, 91):
        rows.append(f'<div class="pg"><img src="diet-pages/p-{n:02d}.webp" loading="lazy"><div class="t"><b>Page {n}</b></div></div>')
    open(os.path.join(ROOT, "tools", "diet-review.html"), "w").write(
        "<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Pregnancy Diet Plan · source pages</title>"
        "<style>body{font:15px system-ui;margin:16px;color:#362d70}.pg{display:grid;grid-template-columns:320px 1fr;gap:12px;margin-bottom:14px;border-top:1px solid #eee;padding-top:10px}img{width:100%;border:1px solid #ddd}</style>"
        "<h1>The 90 pages of the PDF</h1><p>What the app shows comes from these pages. If something in the app reads wrong, find the page here and tell me the page number.</p>" + "".join(rows))
    print("recipes", len(data["recipes"]), "snacks", len(data["snacks"]), "breakfasts", len(data["breakfasts"]), "weeks", len(data["weeks"]), "shopping", list(data["shopping"]))


if __name__ == "__main__":
    main()
