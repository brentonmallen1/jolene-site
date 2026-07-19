#!/usr/bin/env python3
"""One-time content import from the Wix site scrape.

Copies the in-use images from images/ (raw Wix media dump, gitignored) into
src/assets/images/<section>/ with URL-safe kebab-case names, and generates the
content/ files (galleries in original page order, verbatim site text).

Idempotent: re-running overwrites the generated content files and re-copies
images. Hand edits to content/ made through the CMS will be lost on re-run.

Usage: python3 scripts/import-content.py
"""

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "images"
ASSETS = ROOT / "src" / "assets" / "images"
CONTENT = ROOT / "content"
MAPPING = json.loads((Path(__file__).parent / "image_section_mapping.json").read_text())

# The conceptual section's 31 images belong to three projects, in page order.
CONCEPTUAL_SPLITS = [
    ("ambrosial-day-spa", 0, 11),
    ("a-pup-of-tea", 11, 20),
    ("leeding-well-design", 20, 31),
]


def kebab(stem: str) -> str:
    stem = stem.strip().replace("_", " ")
    stem = re.sub(r"[^A-Za-z0-9 -]", "", stem)
    return re.sub(r"[ -]+", "-", stem).strip("-").lower()


def prettify(stem: str) -> str:
    """Filename stem -> readable alt text (used when the site had no alt)."""
    s = stem.strip().replace("_", " ")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*(PIX|JUNE)$", "", s)  # drop employer suffixes from alts
    return s


def local_index() -> dict:
    idx = {}
    for f in RAW.iterdir():
        if f.suffix.lower() == ".webp":
            idx[f.stem.strip().lower()] = f
    return idx


LOCAL = local_index()


_claimed: dict[Path, str] = {}  # dest path -> source stem that owns it


def copy_image(wix_name: str, dest_dir: Path) -> str:
    """Copy the local webp matching a Wix fileName into dest_dir; return new filename."""
    stem = Path(wix_name).stem.strip().lower()
    src = LOCAL.get(stem)
    if src is None:
        sys.exit(f"ERROR: no local image found for '{wix_name}'")
    base = kebab(Path(wix_name).stem)
    # Distinct sources can kebab to the same name (e.g. "NAOMI COCOA Square"
    # vs "NAOMI_COCOA Square"); suffix until the name is free.
    n, new_name = 1, base + ".webp"
    while _claimed.get(dest_dir / new_name, stem) != stem:
        n += 1
        new_name = f"{base}-{n}.webp"
    _claimed[dest_dir / new_name] = stem
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest_dir / new_name)  # copyfile: don't inherit APFS compression flags
    return new_name


def yml_str(s: str) -> str:
    return '"' + s.replace('"', '\\"') + '"'


# Wide interior views that pan in place by default (flat pan tiles).
PAN_DEFAULTS = {
    "spa-bedroom-rendering-finished",
    "spa-final-gym-rendering-color",
    "spa-final-living-room-color-rendering",
}


def gallery_yaml(items, section_dir: str, indent: int = 2, rel: str = "../") -> str:
    """rel: path from the content file's directory up to the repo root."""
    pad = " " * indent
    lines = []
    for it in items:
        new_name = copy_image(it["file"], ASSETS / Path(section_dir))
        alt = it["alt"] or prettify(Path(it["file"]).stem)
        view = "wide" if Path(new_name).stem in PAN_DEFAULTS else "still"
        lines.append(f"{pad}- image: {rel}src/assets/images/{section_dir}/{new_name}")
        lines.append(f"{pad}  alt: {yml_str(alt)}")
        lines.append(f"{pad}  view: {view}")
    return "\n".join(lines)


# ---------------------------------------------------------------- settings ---
hero_img = copy_image("Cabin.jpg", ASSETS / "hero")
(CONTENT).mkdir(exist_ok=True)
(CONTENT / "settings.yml").write_text(f"""\
site_title: "Jolene Mallen Designs"
theme: classic
palette: gallery
default_mode: light
hero:
  heading: "JOLENE MALLEN"
  subheading: "DESIGNER"
  image: ../src/assets/images/hero/{hero_img}
  image_alt: "Modern lakeside cabin with a stone patio and fire pit"
footer:
  email: "mallen.jolene@gmail.com"
  linkedin: "https://www.linkedin.com/in/jolenemallen/"
""")

# ------------------------------------------------------------------- about ---
headshot = copy_image("Headshot.jpg", ASSETS / "about")
leed = copy_image("LEED_GAcmyk.jpg", ASSETS / "about")
(CONTENT / "about.md").write_text(f"""\
---
title: About
order: 1
headshot: ../src/assets/images/about/{headshot}
headshot_alt: "Jolene Mallen"
badges:
  - image: ../src/assets/images/about/{leed}
    alt: "LEED Green Associate"
---
Hi, I’m Jolene. I’m an interior designer residing in North Carolina with a strong interest in lighting, chairs, and how design impacts our daily lives by incorporating sustainable design practices into my projects.

I graduated from the University of North Carolina at Greensboro with a Bachelor of Fine Arts degree in Interior Architecture. While attending school, I was considered for two national design competitions for my conceptual design work; completed two internships at an upholstery textile design company in High Point, NC; became accredited by the Green Business Certification Institute (GBCI) as a LEED Green Associate, and graduated Magna Cum Laude.

Professionally, I have experience in high-end residential design, product design, and designing marketing imagery for commercial companies to use in national ad campaigns. Additionally, I'm currently in the process of becoming NCIDQ certified.

When I’m not working, I love to crochet and knit, play video games, throw pottery on a wheel, cultivate houseplants, and generally learn and experience new types of crafts.
""")

# --------------------------------------------------------------- galleries ---
SPHERES_360 = [
    ("big-house-day-360.jpg", "Big House — daytime"),
    ("big-house-night-360.jpg", "Big House — evening"),
    ("pix-kitchen-360.jpg", "Kitchen concept"),
]

def spheres_yaml() -> str:
    lines = []
    for fname, alt in SPHERES_360:
        src = RAW / fname
        if not src.exists():
            sys.exit(f"ERROR: 360 source missing: {src}")
        (ASSETS / "portfolio").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, ASSETS / "portfolio" / fname)
        lines.append(f"  - image: ../../src/assets/images/portfolio/{fname}")
        lines.append(f"    alt: {yml_str(alt)}")
        lines.append(f'    view: "360"')
    return "\n".join(lines)


(CONTENT / "galleries").mkdir(exist_ok=True)
(CONTENT / "galleries" / "portfolio.yml").write_text(f"""\
title: Portfolio
order: 2
layout: masonry
notes:
  - "* All CGI imagery owned by PIX-US — responsible for all design and propping direction"
gallery:
{gallery_yaml(MAPPING["portfolio"], "portfolio", rel="../../")}
{spheres_yaml()}
""")

(CONTENT / "galleries" / "sketching.yml").write_text(f"""\
title: Sketching
order: 4
layout: masonry
notes:
  - "* Images were sketched/designed by me while employed at PIX-US, original images owned by PIX-US."
  - "** Images were sketched/designed by me while employed at June Delugas Interiors inc., original images owned by June Delugas Interiors inc."
gallery:
{gallery_yaml(MAPPING["sketching"], "sketching", rel="../../")}
""")

# -------------------------------------------------------------- conceptual ---
(CONTENT / "conceptual").mkdir(exist_ok=True)

PROJECTS = {
    "ambrosial-day-spa": {
        "num": "01",
        "title": "Ambrosial Day Spa",
        "label": "Project One",
        "brief": "Design a space for patients suffering from Multiple Sclerosis to visit and participate in physical therapy, doctor visits and checkups as well as partake in relaxing spa like activities.",
        "body": """The clients of this project are asking for a dual purpose space, one in which they could work and live in; with a clear separation of the two areas. Both spaces need to comply with ADA established codes to help assist all who may have trouble with mobility whilst visiting. It is also asked that the majority of the space be dedicated to the spa while the living space be just large enough to accommodate their everyday basic needs.

This project was completed during my junior year of college at UNCG (fall semester 2015).

This project was entered and considered for the 2016 Bienenstock Furniture Library Interior Design Competition.""",
    },
    "a-pup-of-tea": {
        "num": "02",
        "title": "A Pup of Tea",
        "label": "Project Two",
        "brief": "Create a conceptual design for a potential space at a local beer garden called Tracks, located in downtown Greensboro, North Carolina. The hypothetical design concept should help the developer and potential vendors see the possibilities of running a business at this venue upon completion of the project.",
        "body": """The concept I developed for the space is a dog friendly tea house; I felt this concept would help drive in key demographics targeted by Tracks: Millennials and Gen Z. After having done research on the statistics of Millennials and Gen Z individuals who care for dogs and consume tea, I felt it would be a good fit. Whilst the added focus on tea vs. alcohol aims to appeal to those who may prefer other beverages aside from alcohol.

This project was completed during my senior year (summer semester 2016).

This project was presented to the developer. This was part of a summer class and it is unknown if he used the proposed design to attract potential vendors.""",
    },
    "leeding-well-design": {
        "num": "03",
        "title": "LEEDing WELL Design",
        "label": "Project Three",
        "brief": "Provide a conceptual re-design of the newly renovated ASID Headquarters office located in Washington D.C. The finished design should achieve both LEED ID+C Commercial Interiors and WELL New and Existing Interiors Platinum Certification, as well as compliance with building and ADA codes and regulations.",
        "body": """The overall finished space should aim to help promote an environment that is healthy to all employees and visitors while also encouraging creativity, innovation, wellness and sustainable design.

The client of this project is asking that an emphasis be placed on employee collaboration and interaction and desires an open work space with unassigned workstations to help promote mobility and prevent repetitive daily activities.

In this project, the client is asking that the office be completely re-designed, along with the public men's and women's bathroom (located on the same floor) and one of the two employee exclusive patio spaces at the top of the building.

This project was completed during my senior year (fall semester 2016).

This project was presented to the CEO and employees of ASID as well as the design firm that actually re-designed the space in Washington D.C.""",
    },
}

for slug, start, end in CONCEPTUAL_SPLITS:
    p = PROJECTS[slug]
    items = MAPPING["conceptual"][start:end]
    (CONTENT / "conceptual" / f"{p['num']}-{slug}.md").write_text(f"""\
---
title: "{p['title']}"
label: "{p['label']}"
order: {int(p['num'])}
brief: {yml_str(p['brief'])}
layout: masonry
gallery:
{gallery_yaml(items, f"conceptual/{slug}", rel="../../")}
---
{p['body']}
""")

# ---------------------------------------------------------------- textiles ---
(CONTENT / "textiles").mkdir(exist_ok=True)

TEXTILE_META = {
    "tilly": ("01", "Tilly", "Killer Whales"),
    "jordy": ("02", "Jordy", "Space Travel"),
    "naomi": ("03", "Naomi", "The Southwest"),
}

def textile_key(fname: str) -> str:
    low = fname.lower()
    if "tilly" in low:
        return "tilly"
    if "jordy" in low:
        return "jordy"
    return "naomi"

groups: dict[str, list] = {"tilly": [], "jordy": [], "naomi": []}
for it in MAPPING["textiles"]:
    groups[textile_key(it["file"])].append(it)

for key, items in groups.items():
    num, name, inspiration = TEXTILE_META[key]
    lines = []
    for it in items:
        new_name = copy_image(it["file"], ASSETS / "textiles" / key)
        is_header = it["alt"].startswith("Pattern:")
        colorway = "Main" if is_header else it["alt"]
        lines.append(f"  - image: ../../src/assets/images/textiles/{key}/{new_name}")
        lines.append(f"    colorway: {yml_str(colorway)}")
    (CONTENT / "textiles" / f"{num}-{key}.yml").write_text(f"""\
name: "{name}"
inspiration: "{inspiration}"
order: {int(num)}
swatches:
{chr(10).join(lines)}
""")

# ------------------------------------------------------------------ resume ---
(CONTENT / "resume.yml").write_text("""\
title: Resume
order: 6
pdf: /resume.pdf
email: "mallen.jolene@gmail.com"
""")

copied = sum(1 for _ in ASSETS.rglob("*.webp"))
print(f"Done. {copied} images copied into {ASSETS.relative_to(ROOT)}/")
print(f"Content files written to {CONTENT.relative_to(ROOT)}/")
