#!/usr/bin/env python3
"""Generates every SVG in this folder. Edit the text here, then run:

    pip install fonttools
    python build_assets.py

Fonts are subset and embedded, so the graphics look the same on every device.
"""
import base64
import html
import io
import math
import random
import re
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT
OUT.mkdir(exist_ok=True)

BG, PANEL, TILE, LINE = "#070b14", "#0b1222", "#111a2e", "#25324f"
TEXT, MUTED = "#e8eefc", "#9fb0cc"
CYAN, VIOLET, PINK, TEAL = "#22d3ee", "#a855f7", "#ec4899", "#2dd4bf"

FONTS = {
    "disp": ("Orbitron-Bold.ttf", 700),
    "black": ("Orbitron-Black.ttf", 900),
    "mono": ("JetBrainsMono-Regular.ttf", 400),
    "monob": ("JetBrainsMono-Bold.ttf", 700),
    "sans": ("Inter-Regular.otf", 400),
    "semi": ("Inter-SemiBold.otf", 600),
}


def font_css(body):
    """Embed only the glyphs and fonts this file really uses."""
    css = []
    for key, (file, weight) in FONTS.items():
        chars = set()
        for m in re.finditer(r'<text[^>]*class="[^"]*\bf-%s\b[^"]*"[^>]*>(.*?)</text>' % key, body, re.S):
            chars |= set(html.unescape(re.sub(r"<[^>]+>", "", m.group(1))))
        if not chars:
            continue
        font = TTFont(ROOT / file)
        options = subset.Options()
        options.flavor = "woff"
        options.layout_features = ["kern", "liga"]
        options.notdef_outline = True
        options.drop_tables += ["FFTM"]
        sub = subset.Subsetter(options)
        sub.populate(text="".join(chars) + " ")
        sub.subset(font)
        font.flavor = "woff"
        buf = io.BytesIO()
        font.save(buf)
        data = base64.b64encode(buf.getvalue()).decode()
        css.append(
            f"@font-face{{font-family:'{key}';font-weight:{weight};"
            f"src:url(data:font/woff;base64,{data}) format('woff')}}"
            f".f-{key}{{font-family:'{key}',ui-monospace,monospace;font-weight:{weight}}}"
        )
    return "".join(css)


def save(name, w, h, body, css="", title=""):
    style = font_css(body) + css + "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{html.escape(title or name)}"><title>{html.escape(title or name)}</title>'
        f"<style>{style}</style>{body}</svg>"
    )
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")


def text(x, y, s, size, cls="sans", fill=TEXT, anchor="start", spacing=0, extra=""):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (
        f'<text x="{x}" y="{y}" class="f-{cls}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}"{ls} {extra}>{html.escape(s)}</text>'
    )


GRAD = (
    f'<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}"/>'
    f'<stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>'
)


def card(w, h, r=16, fill=PANEL, op=1):
    return (
        f'<rect x="1.5" y="1.5" width="{w-3}" height="{h-3}" rx="{r}" fill="{fill}" '
        f'stroke="url(#edge)" stroke-width="1.5" stroke-opacity="{op}"/>'
    )


def corners(w, h, m=14, l=18, color=CYAN):
    p = [
        f"M{m} {m+l}V{m}H{m+l}", f"M{w-m-l} {m}H{w-m}V{m+l}",
        f"M{m} {h-m-l}V{h-m}H{m+l}", f"M{w-m-l} {h-m}H{w-m}V{h-m-l}",
    ]
    return f'<path d="{" ".join(p)}" fill="none" stroke="{color}" stroke-width="2" opacity=".85"/>'


def grid_bg(w, h, step=32):
    return (
        f'<pattern id="g" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
        f'<path d="M{step} 0H0V{step}" fill="none" stroke="{CYAN}" stroke-opacity=".06"/></pattern>'
        f'<rect x="3" y="3" width="{w-6}" height="{h-6}" rx="14" fill="url(#g)"/>'
    )


# ---------------------------------------------------------------- banner
def banner():
    w, h = 1200, 300

    def wave(base, amp, phase):
        pts = [(x, base + amp * math.sin(x / 1200 * 2 * math.pi + phase)) for x in range(0, 1201, 150)]
        d = f"M0 0H1200V{pts[-1][1]:.0f}"
        for (x0, y0), (x1, y1) in zip(reversed(pts[1:]), reversed(pts[:-1])):
            mx = (x0 + x1) / 2
            d += f"C{mx:.0f} {y0:.0f} {mx:.0f} {y1:.0f} {x1} {y1:.0f}"
        return d + "Z"

    a, b, c = (wave(235, 24, p) for p in (0, 2.1, 4.2))
    a2, b2 = wave(255, 18, 1), wave(255, 18, 3.5)
    random.seed(10)
    stars = "".join(
        f'<circle class="tw" style="animation-delay:{random.uniform(0,3):.1f}s" '
        f'cx="{x}" cy="{random.randint(20,185)}" r="{random.choice([1.5,2,2.5])}" fill="#fff"/>'
        for x in [random.choice([random.randint(30,175), random.randint(1025,1170)]) for _ in range(30)]
    )
    body = (
        f'<defs><linearGradient id="w" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9d17c9"/>'
        f'<stop offset=".5" stop-color="#4f46e5"/><stop offset="1" stop-color="#0d9488"/></linearGradient>'
        f'<linearGradient id="w2" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ec4899"/>'
        f'<stop offset="1" stop-color="{CYAN}"/></linearGradient></defs>'
        f'<path fill="url(#w2)" opacity=".42" d="{a2}"><animate attributeName="d" dur="9s" repeatCount="indefinite" '
        f'values="{a2};{b2};{a2}"/></path>'
        f'<path fill="url(#w)" d="{a}"><animate attributeName="d" dur="11s" repeatCount="indefinite" '
        f'values="{a};{b};{c};{a}"/></path>{stars}'
        + text(600, 128, "Gourab Krishna Saha", 62, "black", "#fff", "middle")
        + text(600, 172, "AI / ML  ·  SOFTWARE DEVELOPMENT  ·  RESEARCH", 20, "monob", "#d9fbff", "middle", 3)
    )
    css = ".tw{animation:tw 3s ease-in-out infinite}@keyframes tw{0%,100%{opacity:.15}50%{opacity:1}}"
    save("banner", w, h, body, css, "Gourab Krishna Saha")


def footer_wave():
    w, h = 1200, 100
    p1 = "M0 100V50C200 10 400 90 600 50S1000 10 1200 50V100Z"
    p2 = "M0 100V50C200 90 400 10 600 50S1000 90 1200 50V100Z"
    body = (
        f'<defs><linearGradient id="w" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#9d17c9"/>'
        f'<stop offset=".5" stop-color="#4f46e5"/><stop offset="1" stop-color="#0d9488"/></linearGradient></defs>'
        f'<path fill="url(#w)" d="{p1}"><animate attributeName="d" dur="9s" repeatCount="indefinite" '
        f'values="{p1};{p2};{p1}"/></path>'
    )
    save("footer_wave", w, h, body, title="Footer wave")


# ---------------------------------------------------------------- typing line
def typing():
    w, h = 900, 64
    lines = [
        "CSE Undergraduate at BRAC University",
        "Exploring AI, ML, CV and NLP",
        "Building Full-Stack Web Applications",
        "Learning and improving, one project at a time",
    ]
    size, cw = 24, 14.4  # JetBrains Mono advance is 0.6em
    tick, hold, per = 0.055, 1.4, []
    for ln in lines:
        per.append(len(ln) * tick * 1.5 + hold)
    total = sum(per)
    groups, caret_x, caret_t, start = "", [], [], 0.0
    for i, ln in enumerate(lines):
        n = len(ln)
        x0 = (w - n * cw) / 2
        frames = []  # (time, chars shown)
        t = start
        for k in range(n + 1):
            frames.append((t, k))
            t += tick
        t += hold - tick
        for k in range(n, -1, -2):
            frames.append((t, k))
            t += tick
        frames.append((start + per[i], 0))
        times = [0.0] + [min(f[0] / total, 1) for f in frames] + [1.0]
        chars = [0] + [f[1] for f in frames] + [0]
        keep = sorted({(round(a, 5), b) for a, b in zip(times, chars)}, key=lambda z: z[0])
        dedup = []
        for a, b in keep:
            if dedup and dedup[-1][0] == a:
                dedup[-1] = (a, b)
            else:
                dedup.append((a, b))
        dedup[0], dedup[-1] = (0.0, 0), (1.0, 0)
        kt = ";".join(f"{a:g}" for a, _ in dedup)
        widths = ";".join(f"{b*cw:.1f}" for _, b in dedup)
        xs = ";".join(f"{x0+b*cw:.1f}" for _, b in dedup)
        w0, w1 = round(start / total, 5), round((start + per[i]) / total, 5)
        vis = ";".join("1" if w0 <= a < w1 else "0" for a, _ in dedup)
        groups += (
            f'<clipPath id="c{i}"><rect x="{x0:.1f}" y="10" height="44" width="0">'
            f'<animate attributeName="width" calcMode="discrete" dur="{total:.2f}s" repeatCount="indefinite" '
            f'keyTimes="{kt}" values="{widths}"/></rect></clipPath>'
            f'<g clip-path="url(#c{i})">' + text(f"{x0:.1f}", 41, ln, size, "monob", CYAN) + "</g>"
            f'<rect y="17" width="3" height="30" fill="{PINK}" x="-10" opacity="0">'
            f'<animate attributeName="x" calcMode="discrete" dur="{total:.2f}s" repeatCount="indefinite" '
            f'keyTimes="{kt}" values="{xs}"/>'
            f'<animate attributeName="opacity" calcMode="discrete" dur="{total:.2f}s" repeatCount="indefinite" '
            f'keyTimes="{kt}" values="{vis}"/></rect>'
        )
        start += per[i]
    body = f'<defs>{GRAD}</defs>' + card(w, h, 14, BG) + groups
    save("typing", w, h, body, title=" / ".join(lines))


# ---------------------------------------------------------------- control surface
def neural(ox, oy, w, h):
    layers = [3, 5, 5, 2]
    nodes = []
    for i, n in enumerate(layers):
        x = ox + i * w / (len(layers) - 1)
        nodes.append([(x, oy + (j + 0.5) * h / n) for j in range(n)])
    out, k = "", 0
    for a, b in zip(nodes, nodes[1:]):
        for p in a:
            for q in b:
                d = f"M{p[0]:.0f} {p[1]:.0f}L{q[0]:.0f} {q[1]:.0f}"
                out += f'<path d="{d}" stroke="{CYAN}" stroke-opacity=".16"/>'
                if k % 3 == 0:
                    out += f'<path class="pulse" pathLength="100" style="animation-delay:{(k*.23)%3:.2f}s" d="{d}"/>'
                k += 1
    for i, layer in enumerate(nodes):
        for j, (x, y) in enumerate(layer):
            color = [CYAN, VIOLET, VIOLET, PINK][i]
            out += (
                f'<circle cx="{x:.0f}" cy="{y:.0f}" r="9" fill="{BG}" stroke="{color}" stroke-width="2"/>'
                f'<circle class="node" style="animation-delay:{(i*.4+j*.25):.2f}s" cx="{x:.0f}" cy="{y:.0f}" r="4" fill="{color}"/>'
            )
    return out


NET_CSS = (
    f".pulse{{fill:none;stroke:{PINK};stroke-width:2;stroke-dasharray:10 90;stroke-dashoffset:110;"
    "animation:p 3s linear infinite}@keyframes p{to{stroke-dashoffset:0}}"
    ".node{animation:n 2.4s ease-in-out infinite}@keyframes n{0%,100%{opacity:.35}50%{opacity:1}}"
)


def control():
    w, h = 1000, 320
    nodes = [
        ("EDUCATION", "CSE Undergraduate", "BRAC University", CYAN),
        ("FOCUS", "AI / ML + Software", "CV  ·  NLP  ·  Full-Stack", VIOLET),
        ("OPEN TO", "Research + Projects", "Learning opportunities", PINK),
    ]
    b = f'<defs>{GRAD}</defs>' + card(w, h) + grid_bg(w, h) + corners(w, h)
    b += text(44, 62, "PROFILE // ONLINE", 15, "monob", TEAL, spacing=3)
    b += f'<circle class="node" cx="268" cy="57" r="5" fill="{TEAL}"/>'
    b += text(44, 112, "CONTROL SURFACE", 40, "black", TEXT)
    b += text(44, 146, "Practical problems, working software, and steady research.", 18, "sans", MUTED)
    x = 44
    for label, main, sub, color in nodes:
        b += (
            f'<rect x="{x}" y="176" width="204" height="108" rx="12" fill="{TILE}" stroke="{color}" stroke-opacity=".6"/>'
            f'<rect x="{x+16}" y="194" width="26" height="3" fill="{color}"/>'
            + text(x + 16, 218, label, 13, "monob", color, spacing=2)
            + text(x + 16, 246, main, 16.5, "semi", TEXT)
            + text(x + 16, 268, sub, 13.5, "sans", MUTED)
        )
        x += 216
    b += neural(730, 44, 220, 232)
    save("control_surface", w, h, b, NET_CSS, "Profile control surface: CSE undergraduate at BRAC University, focused on AI, ML and software")


# ---------------------------------------------------------------- system access
def title_access():
    w, h = 900, 60
    b = (
        f'<defs>{GRAD}<linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{CYAN}"/></linearGradient><linearGradient id="r" x1="0" x2="1">'
        f'<stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient></defs>'
        f'<rect x="60" y="29" width="250" height="2" fill="url(#l)"/><rect x="590" y="29" width="250" height="2" fill="url(#r)"/>'
        + text(450, 39, "SYSTEM ACCESS", 26, "disp", "#7c8cf8", "middle", 7)
    )
    save("title_system_access", w, h, b, title="System access")


def portal():
    w, h = 900, 250
    b = f'<defs>{GRAD}</defs>' + card(w, h) + grid_bg(w, h) + corners(w, h, color=VIOLET)
    b += f'<ellipse class="gl" cx="450" cy="118" rx="330" ry="84" fill="{VIOLET}"/>'
    b += text(450, 62, "PRIMARY NODE  //  PORTFOLIO", 15, "monob", CYAN, "middle", 4)
    b += text(450, 128, "GOURAB MAIN SYSTEM", 46, "black", TEXT, "middle", 2)
    b += text(450, 164, "Projects  |  Journey  |  Research  |  Contact", 18, "sans", MUTED, "middle")
    b += (
        f'<rect x="355" y="184" width="190" height="42" rx="21" fill="{BG}" stroke="url(#edge)" stroke-width="1.5"/>'
        + text(450, 210, "ENTER SYSTEM  >", 15, "monob", CYAN, "middle", 2)
    )
    css = ".gl{filter:blur(46px);animation:g 4s ease-in-out infinite}@keyframes g{0%,100%{opacity:.14}50%{opacity:.3}}"
    save("portal_main", w, h, b, css, "Gourab main system: open the portfolio")


def lab(name, title, sub, tag, color, glyph):
    w, h = 280, 118
    b = f'<defs>{GRAD}</defs>' + card(w, h, 12)
    b += f'<circle class="node" cx="46" cy="59" r="26" fill="{color}" fill-opacity=".14"/>'
    b += f'<circle cx="46" cy="59" r="26" fill="none" stroke="{color}" stroke-dasharray="6 5"/>'
    b += f'<g fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{glyph}</g>'
    b += text(86, 38, tag, 11.5, "monob", color, spacing=1.5)
    b += text(86, 63, title, 17.5, "disp", TEXT)
    b += text(86, 86, sub, 13, "sans", MUTED)
    save(name, w, h, b, ".node{animation:n 2.4s ease-in-out infinite}@keyframes n{0%,100%{opacity:.5}50%{opacity:1}}", f"{title}: {sub}")


def labs():
    lab("lab_researchflow", "ResearchFlow", "RAG research assistant", "LIVE // AI", CYAN,
        '<path d="M36 47h13l9 9v16H36z"/><path d="M41 60h12M41 66h8"/>')
    lab("lab_gitworth", "GitWorth", "GitHub portfolio reviewer", "LIVE // TOOL", VIOLET,
        '<path d="M46 45l4 9 10 1-7 7 2 10-9-5-9 5 2-10-7-7 10-1z"/>')
    lab("lab_spendora", "Spendora", "Personal finance tracker", "LIVE // FINANCE", PINK,
        '<path d="M34 72V60M43 72V50M52 72V56M60 72V46"/>')
    w, h = 300, 62
    b = f'<defs>{GRAD}</defs>' + card(w, h, 30, TILE)
    b += text(150, 38, "EXPLORE ALL PROJECTS  >", 15, "monob", CYAN, "middle", 1.5)
    save("explore_projects", w, h, b, title="Explore all projects")


def core():
    w, h = 900, 330
    cols = [
        ("BUILD SYSTEMS", "What I make", CYAN, ["Full-stack web applications", "AI tools with retrieval (RAG)", "Peer-to-peer and real-time apps", "Computer graphics projects"]),
        ("INTERESTS", "What I study", VIOLET, ["Artificial Intelligence", "Machine Learning", "Computer Vision", "Natural Language Processing"]),
        ("PHILOSOPHY", "How I work", PINK, ["Solve practical problems", "Learn from experienced people", "Aim for real-world impact", "Improve one project at a time"]),
    ]
    b = f'<defs>{GRAD}</defs>' + card(w, h) + grid_bg(w, h)
    cx = 450
    b += (
        f'<g class="spin"><rect x="{cx-15}" y="27" width="30" height="30" rx="4" fill="none" stroke="{CYAN}" stroke-width="2"/></g>'
        f'<rect class="node" x="{cx-6}" y="36" width="12" height="12" rx="2" fill="{TEAL}"/>'
        + text(cx, 90, "SYSTEM CORE", 24, "disp", TEXT, "middle", 5)
    )
    x = 26
    for title, sub, color, items in cols:
        b += (
            f'<rect x="{x}" y="110" width="272" height="194" rx="12" fill="{TILE}" stroke="{color}" stroke-opacity=".6"/>'
            + text(x + 20, 144, title, 18, "disp", color)
            + text(x + 20, 166, sub, 13.5, "sans", MUTED)
        )
        for i, item in enumerate(items):
            y = 196 + i * 27
            b += f'<rect x="{x+20}" y="{y-9}" width="7" height="7" rx="1.5" fill="{color}"/>' + text(x + 36, y, item, 15, "sans", TEXT)
        x += 284
    css = (
        ".spin{transform-origin:450px 42px;animation:s 8s linear infinite}@keyframes s{to{transform:rotate(360deg)}}"
        ".node{animation:n 2.4s ease-in-out infinite}@keyframes n{0%,100%{opacity:.5}50%{opacity:1}}"
    )
    save("system_core", w, h, b, css, "System core: what I build, what I study, how I work")


# ---------------------------------------------------------------- dividers
def dividers():
    w, h = 900, 34
    defs = (
        f'<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/>'
        f'<stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient></defs>'
    )
    flow = ".f{stroke-dasharray:60 240;animation:d 4s linear infinite}@keyframes d{to{stroke-dashoffset:-300}}"
    save("divider_pulse", w, h, defs +
         f'<rect x="40" y="16" width="820" height="2" fill="url(#fade)"/>'
         f'<path class="f" d="M40 17H860" stroke="{PINK}" stroke-width="3" fill="none"/>'
         f'<circle cx="450" cy="17" r="6" fill="{BG}" stroke="{CYAN}" stroke-width="2"/>', flow, "Divider")
    path = "M40 17H300l10-10H420l10 10h40l10 10H590l10-10H860"
    save("divider_circuit", w, h, defs +
         f'<path d="{path}" stroke="url(#fade)" stroke-width="2" fill="none"/>'
         f'<path class="f" d="{path}" stroke="{TEAL}" stroke-width="3" fill="none"/>', flow, "Divider")
    pills = "".join(
        f'<rect class="c" style="animation-delay:{i*.18:.2f}s" x="{330+i*36}" y="11" width="24" height="12" rx="6" fill="{CYAN}"/>'
        for i in range(7)
    )
    save("divider_capsule", w, h, defs + f'<rect x="40" y="16" width="820" height="2" fill="url(#fade)"/>' + pills,
         ".c{animation:c 2.4s ease-in-out infinite}@keyframes c{0%,100%{opacity:.2}50%{opacity:1}}", "Divider")
    save("divider_tracks", w, h, defs +
         f'<rect x="40" y="10" width="820" height="2" fill="url(#fade)"/><rect x="40" y="22" width="820" height="2" fill="url(#fade)"/>'
         f'<path class="f" d="M40 11H860" stroke="{PINK}" stroke-width="3" fill="none"/>'
         f'<path class="f r" d="M40 23H860" stroke="{CYAN}" stroke-width="3" fill="none"/>',
         flow + ".r{animation-direction:reverse}", "Divider")


# ---------------------------------------------------------------- tech grid
def recolor(svg, *pairs):
    for a, b in pairs:
        svg = svg.replace(a, b)
    return svg


def icon(name):
    svg = (ROOT / f"{name}.svg").read_text(encoding="utf-8")
    if name == "nextjs":
        svg = recolor(svg, ('<circle cx="64" cy="64" r="64"/>', '<circle cx="64" cy="64" r="64" fill="#fff"/>'),
                      ('stop-color="#fff"', 'stop-color="#000"'), ('stop-color="white"', 'stop-color="#000"'))
    if name == "vercel":
        svg = recolor(svg, ("<path d", '<path fill="#fff" d'))
    if name == "prisma":
        svg = re.sub(r'fill="#[0-9a-fA-F]{3,6}"', 'fill="#fff"', svg) if "fill=" in svg else svg.replace("<path", '<path fill="#fff"')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def custom(name):
    glyphs = {
        "sql": '<g fill="none" stroke="#38bdf8" stroke-width="9"><ellipse cx="64" cy="30" rx="40" ry="15"/><path d="M24 30v68c0 8 18 15 40 15s40-7 40-15V30M24 64c0 8 18 15 40 15s40-7 40-15"/></g>',
        "mongoose": '<rect x="14" y="14" width="100" height="100" rx="20" fill="#880000"/><path fill="none" stroke="#fff" stroke-width="11" stroke-linejoin="round" stroke-linecap="round" d="M38 90V40l26 30 26-30v50"/>',
        "framer": '<path fill="#fff" d="M32 14h64v34H64zM32 48h32l32 34H64v32L32 82z"/>',
        "overleaf": '<path fill="#47a141" d="M104 18C60 18 24 44 24 78c0 18 13 32 30 32 15 0 27-12 27-26 0-11-8-20-19-20-6 0-11 2-15 6 7-20 30-36 57-36-6 8-9 18-7 28 9-9 13-24 7-44z"/>',
        "zod": '<rect x="14" y="14" width="100" height="100" rx="20" fill="#3068b7"/><path fill="none" stroke="#fff" stroke-width="12" stroke-linejoin="round" d="M40 42h48L40 86h48"/>',
        "nextauth": '<path fill="#7c3aed" d="M64 10l44 16v34c0 28-18 48-44 58-26-10-44-30-44-58V26z"/><path fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round" d="M44 64l14 14 28-30"/>',
        "recharts": '<path fill="#8884d8" d="M18 112V70h20v42zM54 112V40h20v72zM90 112V18h20v94z"/>',
    }
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">{glyphs[name]}</svg>'
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def tech():
    items = [
        ("python", "Python"), ("javascript", "JavaScript"), ("typescript", "TypeScript"), ("c", "C"), ("cplusplus", "C++"),
        ("tensorflow", "TensorFlow"), ("pytorch", "PyTorch"), ("opencv", "OpenCV"), ("jupyter", "Jupyter"), ("*sql", "SQL"),
        ("html5", "HTML5"), ("css3", "CSS3"), ("react", "React"), ("nextjs", "Next.js"), ("nodejs", "Node.js"),
        ("tailwindcss", "Tailwind"), ("*framer", "Framer"), ("mongodb", "MongoDB"), ("*mongoose", "Mongoose"), ("postgresql", "PostgreSQL"),
        ("*nextauth", "NextAuth"), ("*zod", "Zod"), ("*recharts", "Recharts"), ("prisma", "Prisma"), ("php", "PHP"),
        ("git", "Git"), ("linux", "Linux"), ("vscode", "VS Code"), ("*overleaf", "Overleaf"), ("vercel", "Vercel"),
    ]
    w, h = 520, 660
    cell_w, cell_h = 96, 104
    ox, oy = 20, 18
    b = f'<defs>{GRAD}</defs>' + card(w, h, 14)
    for i, (key, label) in enumerate(items):
        x = ox + (i % 5) * cell_w
        y = oy + (i // 5) * cell_h + 4
        uri = custom(key[1:]) if key.startswith("*") else icon(key)
        b += (
            f'<rect x="{x}" y="{y}" width="{cell_w-8}" height="{cell_h-8}" rx="10" fill="{TILE}" stroke="{LINE}"/>'
            f'<image href="{uri}" x="{x+22}" y="{y+13}" width="44" height="44"/>'
            + text(x + (cell_w - 8) / 2, y + 79, label, 12.5, "semi", TEXT, "middle")
        )
    save("tech_grid", w, h, b, title="Technologies: " + ", ".join(i[1] for i in items))


# ---------------------------------------------------------------- orbs
def orb(name, w, h, cx, title, sub, c1, c2, sats, cy, cta=True, ty=None):
    ty = ty or h - 120
    b = (
        f'<defs>{GRAD}<radialGradient id="o"><stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="{c1}"/>'
        f'<stop offset="1" stop-color="{c2}" stop-opacity="0"/></radialGradient></defs>' + card(w, h, 14, BG)
        + f'<circle class="b" cx="{cx}" cy="{cy}" r="88" fill="url(#o)"/>'
    )
    for i, r in enumerate((62, 86)):
        b += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{c1}" stroke-opacity=".3" stroke-dasharray="4 8"/>'
    for i in range(sats):
        a = 2 * math.pi * i / sats
        r = 86 if i % 2 else 62
        b += (
            f'<g class="o{i%2}"><circle cx="{cx + r*math.cos(a):.1f}" cy="{cy + r*math.sin(a):.1f}" r="5" fill="{c1 if i%2 else "#fff"}"/></g>'
        )
    b += text(w / 2, ty, title, 21, "disp", TEXT, "middle", 1)
    y = ty + 38
    for line in sub:
        b += text(w / 2, y, line, 17, "semi" if cta else "sans", MUTED, "middle")
        y += 28
    if cta:
        b += text(w / 2, h - 28, "OPEN  >", 14, "monob", CYAN, "middle", 2)
    css = (
        f".o0,.o1{{transform-origin:{cx}px {cy}px;animation:r 18s linear infinite}}"
        ".o1{animation-duration:26s;animation-direction:reverse}@keyframes r{to{transform:rotate(360deg)}}"
        f".b{{transform-origin:{cx}px {cy}px;animation:b 4s ease-in-out infinite}}"
        "@keyframes b{0%,100%{transform:scale(.88);opacity:.8}50%{transform:scale(1.05);opacity:1}}"
    )
    save(name, w, h, b, css, title.title())


def orbs():
    orb("orb_projects", 240, 660, 120, "PROJECTS", ["ResearchFlow", "GitWorth", "Spendora", "File Pathao", "Rent A Car", "+ 8 more"], VIOLET, "#4f46e5", 6, cy=170, ty=345)
    orb("orb_ai", 240, 660, 120, "AI DOMAINS", ["Machine Learning", "Computer Vision", "NLP", "Retrieval (RAG)"], CYAN, VIOLET, 6, cy=170, ty=345)


def collab():
    w, h = 370, 180
    b = f'<defs>{GRAD}<radialGradient id="o"><stop offset="0" stop-color="#fff"/><stop offset=".3" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient></defs>' + card(w, h, 14, BG)
    b += f'<circle class="b" cx="115" cy="72" r="46" fill="url(#o)"/><circle class="b d" cx="255" cy="72" r="46" fill="url(#o)"/>'
    b += f'<path class="f" d="M115 72H255" stroke="{PINK}" stroke-width="3"/>'
    b += text(185, 142, "COLLABORATION", 19, "disp", TEXT, "middle", 2)
    b += text(185, 164, "OPEN  >", 13, "monob", CYAN, "middle", 2)
    css = (
        ".b{animation:b 3s ease-in-out infinite}.d{animation-delay:1.5s}@keyframes b{0%,100%{opacity:.55}50%{opacity:1}}"
        ".f{stroke-dasharray:12 12;animation:d 1.6s linear infinite}@keyframes d{to{stroke-dashoffset:-24}}"
    )
    save("orb_collab", w, h, b, css, "Collaboration")


def buttons():
    for name, label, value, color in [
        ("btn_website", "WEBSITE", "portfolio-gks-10.vercel.app", CYAN),
        ("btn_email", "EMAIL", "gourabarko100@gmail.com", PINK),
        ("btn_linkedin", "LINKEDIN", "gourab-krishna-saha", VIOLET),
    ]:
        w, h = 370, 52
        b = (
            f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="10" fill="{TILE}" stroke="{color}" stroke-opacity=".7"/>'
            f'<path d="M1 11a10 10 0 0 1 10-10h87v{h-2}H11a10 10 0 0 1-10-10z" fill="{color}" fill-opacity=".16"/>'
            + text(50, 31, label, 12.5, "monob", color, "middle", 1)
            + text(112, 31, value, 14.5, "sans", TEXT)
        )
        save(name, w, h, b, title=f"{label}: {value}")


if __name__ == "__main__":
    banner(); footer_wave(); typing(); control(); title_access(); portal(); labs(); core()
    dividers(); tech(); orbs(); collab(); buttons()
    print(f"built {len(list(OUT.glob('*.svg')))} files in {OUT}")
