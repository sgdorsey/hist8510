import re, glob, os, csv, sys

SRC = "/Users/sharondorsey/Desktop/hist8510/06-OCR-LLMs/ocr-results"
files = sorted(glob.glob(os.path.join(SRC, "IMG_*.txt")))

lines = []
for f in files:
    raw = [l.strip() for l in open(f, encoding="utf-8").read().splitlines()]
    raw = [l for l in raw if l]
    # intro page: skip everything before first county header
    if f.endswith("IMG_7956.txt"):
        i = next(i for i, l in enumerate(raw) if "County:" in l)
        raw = raw[i:]
    # left-margin fragments bleeding in from the facing page
    i = 0
    while i < len(raw) and len(raw[i]) < 30:
        i += 1
    raw = raw[i:]
    # page numbers (standalone digits)
    raw = [l for l in raw if not re.fullmatch(r"\d+", l)]
    # OCR repeated the same line twice in a row
    dedup = []
    for l in raw:
        if dedup and dedup[-1] == l:
            continue
        dedup.append(l)
    lines.extend(dedup)

# join lines, repairing line-break hyphenation
text = ""
for l in lines:
    if not text:
        text = l
    elif text.endswith("-") and l[0].islower():
        text = text[:-1] + l
    elif text.endswith("-"):
        text = text + l
    elif re.search(r"(^|[\s.])[A-Z]\.$", text) and re.match(r"[A-Z]\.", l):
        text = text + l          # abbreviation split across lines, e.g. A.R. / P.
    else:
        text = text + " " + l

# fix the overlap between IMG_7984 (last line) and IMG_7985 (first line)
text = text.replace("St. Paul's M.E.S., Saluda; St. Paul's M.E.S., Saluda;",
                    "St. Paul's M.E.S., Saluda;", 1)

DENOM_PATTERNS = [
    r"\([^()]*\)",                                   # trailing parenthetical e.g. (Negro)
    r"Fire Baptized Holiness Church of God of America",
    r"Holiness Church of God", r"Church of God and Christ", r"Church of God",
    r"Church of Christ", r"Church of Jesus Christ of Latter[- ]Day Saints",
    r"Disciples of Christ", r"Assembly of God", r"Assemblies of God",
    r"A\.\s?M\.\s?E\.\s?Zion", r"M\.\s?E\.\s?Zion", r"A\.\s?M\.\s?E\.?", r"C\.\s?M\.\s?E\.?",
    r"M\.\s?E\.\s?S\.?", r"M\.\s?E\.?", r"S\.\s?B\.\s?C\.?\.?", r"SBC", r"A\.\s?R\.\s?P\.?",
    r"A\.\s?F\.\s?W\.?", r"R\.\s?U\.\s?M\.\s?E\.?", r"R\.\s?M\.\s?U\.\s?E\.?", r"U\.\s?S\.",
    r"Nat'l Bap\.\s?Con(vention)?\.?( Inc\.)?", r"Nat'l Bap\.", r"Convention\)?",
    r"Southern", r"Northern", r"Negro", r"African", r"Free Will", r"Primitive",
    r"Missionary", r"Baptist", r"Bap\.", r"Baptized", r"Fire", r"Hardshell", r"Hard Shell",
    r"Methodist", r"Meth\.?", r"Episcopal", r"Epis(copal)?\.?", r"Protestant", r"Prot\.",
    r"Reformed", r"Ref\.", r"Reform", r"Presbyterian", r"Pres\.", r"Associate",
    r"Holiness", r"Hol\.", r"Pentecostal", r"Pent\.", r"Sanctified", r"Apostolic",
    r"Congregational", r"Congregation", r"Lutheran", r"Luth\.?", r"Evangelical", r"Evang\.",
    r"Ev\.", r"United", r"Unit\.", r"German", r"Roman", r"Catholic", r"Cath\.",
    r"Greek", r"Orthodox", r"Jewish", r"Synagogue", r"Christian Science", r"Christian",
    r"Seventh Day Adventist", r"Adventist", r"Wesleyan", r"Independent", r"Reformed Methodist Union Episcopal", r"Union American", r"R\.\s?Union M\.E\.", r"Union M\.E\.",
    r"Undenom\.?", r"non-denom\.?", r"Interdenominational", r"Unitarian", r"Mormon",
    r"Nazarene", r"African Zion", r"Methodist Zion", r"Zion Methodist", r"Evan\.", r"Mis\.", r"Bapt\.?", r"Neg\.", r"Prim\.", r"Hebrew",
    r"Ch\.\s?of God( of the Americas| of America)?", r"Ch\.", r"Hol\.\s?Ch\.\s?of God", r"Interdenom\.?",
    r"A\.F\.W\.B\.", r"M\.E\.Ch\.S\.", r"M\.E\.U\.", r"Epis\.\s?South", r"Freewill", r"Original Free Will",
    r"National", r"Nat'l", r"Salvation Army", r"Four Square", r"International Four Square", r"Soc\. Israelites",
    r"Apostolic Faith", r"Evening Light", r"Christ's Sanctified Holy Church", r"Non-denom\.", r"undenom\.",
    r"Of God", r"of God", r"Church of Christ-Scientist", r"Latter Day Saints", r"Christ-Scientist",
]
DENOM_RE = [re.compile(r"(?:^|(?<=[\s\-.]))(" + p + r")\s*[-]?\s*$") for p in DENOM_PATTERNS]
STRONG = re.compile(r"Baptist|Bap\.|S\.\s?B\.\s?C|SBC|M\.\s?E|A\.\s?R\.\s?P|Presbyter|Method|Meth|Episc|Epis|Holiness|Hol\.|Pent|Luth|Catholic|Cath|Jewish|Synagogue|Congregation|Christian|Disciples|Church of God|Adventist|A\.F\.W|Orthodox|Mormon|Latter|Assembl|Unitarian|Sanctified|Apostolic|Undenom|non-denom|Interdenom|Reform|R\.\s?U\.\s?M|R\.\s?M\.\s?U|Nazarene|Hebrew|Salvation|Four Square|Neg\.|Ch\.|Evan\.|Mis\.|Prim\.|Israelites")

TAIL = re.compile(r"\s*(\s|-)(Chapel|Mission|Church|Tabernacle|Ch\.|Church \(No\. \d\)|No\. \d|#\d)( \([^()]*\))?$")
def split_denom(s):
    m = TAIL.search(s)
    if m:
        n, d = split_denom(s[:m.start()])
        return (s, d) if d else (s, "")
    rest = s.rstrip()
    while True:
        for rx in DENOM_RE:
            m = rx.search(rest)
            if m and m.start() > 0 or (m and m.start() == 0):
                new = rest[:m.start()].rstrip(" -")
                if new == rest:
                    continue
                rest = new
                break
        else:
            break
        if not rest:
            break
    denom = s[len(rest):].strip(" -") if rest else s
    # denomination must actually name one, not just "(Negro)" / "Union" / "Zion"
    if not STRONG.search(denom):
        return s, ""
    m2 = re.match(r"(United|Free Will) (S\.B\.C\.)$", s)
    if m2:
        return m2.group(1), m2.group(2)
    if not rest:
        # whole entry is a denomination (e.g. "Church of God", "Pentecostal Holiness")
        return s, s
    # the first word(s) peeled off are a church name like "Zion", "Union", "Christian"? keep as is
    return rest, denom

rows = []
county = ""
text = re.sub(r"\s*([A-Z][A-Za-z]+ County:)", r"; \1", text)
for seg in re.split(r";", text):
    seg = seg.strip()
    if not seg:
        continue
    m = re.match(r"([A-Z][A-Za-z]+) County:\s*(.*)$", seg)
    if m:
        county = m.group(1)
        seg = m.group(2).strip()
        if not seg:
            continue
    seg = re.sub(r"\.$", "", seg) if seg.endswith("..") else seg
    if seg.endswith(".") and not re.search(r"[A-Z]\.$|Epis\.$|Luth\.$|Meth\.$|Cath\.$|denom\.$|Con\.$|Inc\.$|Prot\.$|Hol\.$|Evang\.$|Bap\.$", seg):
        seg = seg[:-1]      # period that ends a county's list
    # separate trailing ", Location"
    parts = [p.strip() for p in seg.split(",")]
    # entries glued together by a comma instead of a semicolon: "X M.E.S., Y A.M.E."
    entries = [[parts[0]]]
    for p in parts[1:]:
        if split_denom(p)[1] and split_denom(p)[0] != p and not re.fullmatch(r"(Holiness|Pentecostal Holiness)", p):
            entries.append([p])
        else:
            entries[-1].append(p)
    for e in entries:
        body, loc = e[0], ", ".join(e[1:])
        name, denom = split_denom(body)
        # "Church of God, Holiness, Anderson": denomination continues after the comma
        if denom and name == denom and len(e) > 2 and split_denom(e[1]) == (e[1], e[1]):
            name = denom = body + ", " + e[1]
            loc = ", ".join(e[2:])
        if not denom and loc:
            # e.g. "Church of God, Holiness, Anderson" -> denomination sits after comma
            n2, d2 = split_denom(e[1]) if len(e) > 1 else (None, "")
            if d2 and n2 == d2 and len(e) > 2:
                denom = e[1]
                loc = ", ".join(e[2:])
        rows.append({"Church Name": name, "County": county, "Denomination": denom,
                     "Location": loc, "_raw": ", ".join(e)})

out = sys.argv[1]
with open(out, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["Church Name", "County", "Denomination", "Location"], extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
with open(out + ".review.tsv", "w", encoding="utf-8") as fh:
    for r in rows:
        fh.write("\t".join([r["County"], r["Church Name"], r["Denomination"], r["Location"], r["_raw"]]) + "\n")
print(len(rows), "rows")
