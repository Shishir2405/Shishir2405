#!/usr/bin/env python3
"""
generate_svg.py — build dark_mode.svg and light_mode.svg
(ASCII portrait on the left + neofetch-style info panel on the right).

Reads ascii_dark.txt / ascii_light.txt produced by img_to_ascii.py.
The panel carries the id="" fields that today.py updates on schedule.
Run:  python3 generate_svg.py
"""
import json
from xml.sax.saxutils import escape

# ─── card geometry
W, H = 1130, 530
PANEL_X, PANEL_Y0, PANEL_STEP = 460, 30, 20      # neofetch panel: 16px font, 20px step
ASCII_X, ASCII_Y0, ASCII_STEP, ASCII_FS = 15, 26, 10, 9   # portrait: 9px font, 10px step

# ─── starting values shown until the GitHub Action refreshes them each day
#     (repos/followers are the real public numbers at build time)
DATA = {
    "host":        "Unjob.ai  (Full-Stack Engineer)",
    "role":        "Full-Stack Developer · AI Builder",
    "os":          "Linux, macOS, Windows",
    "ide":         "VS Code, Cursor, Neovim",
    "lang_prog":   "JavaScript, TypeScript, Python, Java",
    "lang_front":  "React, Next.js, Tailwind CSS",
    "lang_back":   "Node.js, Express, Django, PostgreSQL",
    "stack_cloud": "AWS (EC2, S3, SES), Docker, Prisma",
    "stack_rt":    "Socket.io, WebRTC, REST, GraphQL",
    "email":       "shishirshrivastava30@gmail.com",
    "portfolio":   "shishir24.in",
    "linkedin":    "shishirshrivastava2405",
    "twitter":     "shishir_2405",
    "awards":      "2× SIH National Winner · 9.47 CGPA",
    # dynamic (updated by today.py)
    "age":       "22 years, 1 month, 17 days",
    "repos":     "40",
    "contrib":   "55",
    "stars":     "20",
    "commits":   "1,200",
    "followers": "19",
    "loc":       "250,000",
    "loc_add":   "300,000",
    "loc_del":   "50,000",
}

THEMES = {
    "dark": {
        "bg": "#0d1117", "text": "#e6edf3", "color_idx": 1,
        "key": "#3fb950", "value": "#58a6ff", "cc": "#6e7681",
        "add": "#3fb950", "del": "#f85149",
        "out": "dark_mode.svg",
    },
    "light": {
        "bg": "#ffffff", "text": "#1f2328", "color_idx": 2,
        "key": "#1a7f37", "value": "#0969da", "cc": "#afb8c1",
        "add": "#1a7f37", "del": "#cf222e",
        "out": "light_mode.svg",
    },
}

DASH = "—" * 30


def ascii_block(color_idx):
    """Colored portrait from portrait.json. color_idx: 1=dark-theme, 2=light-theme
    color for each cell. Consecutive same-color cells merge into one <tspan>."""
    try:
        with open("portrait.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        return (f'<text x="{ASCII_X}" y="{ASCII_Y0}">'
                f'<tspan x="{ASCII_X}" y="{ASCII_Y0}">(run img_to_ascii.py to build portrait.json)</tspan></text>')

    out = [f'<text x="{ASCII_X}" y="{ASCII_Y0}" font-size="{ASCII_FS}px" font-weight="bold">']
    for i, row in enumerate(data["cells"]):
        y = ASCII_Y0 + i * ASCII_STEP
        spans, run, run_color = [], "", None
        def flush():
            nonlocal run, run_color
            if run:
                spans.append(f'<tspan fill="{run_color}">{escape(run)}</tspan>' if run_color else escape(run))
            run = ""
        for cell in row:
            color = None if cell is None else cell[color_idx]
            char = " " if cell is None else cell[0]
            if color != run_color:
                flush(); run_color = color
            run += char
        flush()
        out.append(f'<tspan x="{ASCII_X}" y="{y}" xml:space="preserve">{"".join(spans)}</tspan>')
    out.append("</text>")
    return "\n".join(out)


def K(t):   return f'<tspan class="key">{escape(t)}</tspan>'
def V(t, i=None):
    idattr = f' id="{i}"' if i else ""
    return f'<tspan class="value"{idattr}>{escape(t)}</tspan>'
def C(t, i=None):
    idattr = f' id="{i}"' if i else ""
    return f'<tspan class="cc"{idattr}>{escape(t)}</tspan>'
def dot(n):  return C(" " + "." * n + " ")


def panel(d):
    """Right-hand neofetch panel. Only value spans with ids get auto-updated."""
    x = PANEL_X
    L = []  # (text_html)
    L.append(f'shishir@Shishir2405 <tspan class="cc">{DASH}</tspan>')
    L.append(C(". ") + K("OS") + ":" + dot(18) + V(d["os"]))
    L.append(C(". ") + K("Uptime") + ":" + C(" ", "age_data_dots") + V(d["age"], "age_data"))
    L.append(C(". ") + K("Host") + ":" + dot(14) + V(d["host"]))
    L.append(C(". ") + K("Role") + ":" + dot(14) + V(d["role"]))
    L.append(C(". ") + K("IDE") + ":" + dot(17) + V(d["ide"]))
    L.append(C(". "))
    L.append(C(". ") + K("Languages") + "." + K("Programming") + ":" + dot(3) + V(d["lang_prog"]))
    L.append(C(". ") + K("Languages") + "." + K("Frontend") + ":" + dot(6) + V(d["lang_front"]))
    L.append(C(". ") + K("Languages") + "." + K("Backend") + ":" + dot(7) + V(d["lang_back"]))
    L.append(C(". "))
    L.append(C(". ") + K("Stack") + "." + K("Cloud") + ":" + dot(8) + V(d["stack_cloud"]))
    L.append(C(". ") + K("Stack") + "." + K("Realtime") + ":" + dot(5) + V(d["stack_rt"]))
    L.append(C(". "))
    L.append(f'- Contact <tspan class="cc">{DASH}</tspan>')
    L.append(C(". ") + K("Email") + ":" + dot(13) + V(d["email"]))
    L.append(C(". ") + K("Portfolio") + ":" + dot(9) + V(d["portfolio"]))
    L.append(C(". ") + K("LinkedIn") + ":" + dot(10) + V(d["linkedin"]))
    L.append(C(". ") + K("X / Twitter") + ":" + dot(7) + V(d["twitter"]))
    L.append(f'- GitHub Stats <tspan class="cc">{DASH}</tspan>')
    L.append(C(". ") + K("Repos") + ":" + C(" .... ", "repo_data_dots") + V(d["repos"], "repo_data")
             + " {" + K("Contributed") + ": " + V(d["contrib"], "contrib_data") + "} | "
             + K("Stars") + ":" + C(" ..... ", "star_data_dots") + V(d["stars"], "star_data"))
    L.append(C(". ") + K("Commits") + ":" + C(" ..... ", "commit_data_dots") + V(d["commits"], "commit_data")
             + " | " + K("Followers") + ":" + C(" ..... ", "follower_data_dots") + V(d["followers"], "follower_data"))
    L.append(C(". ") + K("Lines of Code on GitHub") + ":" + C(" ", "loc_data_dots") + V(d["loc"], "loc_data")
             + ' ( <tspan class="addColor" id="loc_add">' + escape(d["loc_add"]) + '</tspan><tspan class="addColor">++</tspan>, '
             + C(" ", "loc_del_dots") + '<tspan class="delColor" id="loc_del">' + escape(d["loc_del"])
             + '</tspan><tspan class="delColor">--</tspan> )')
    L.append(C(". ") + K("Achievements") + ":" + dot(4) + V(d["awards"]))

    out = [f'<text x="{PANEL_X}" y="{PANEL_Y0}" class="panel">']
    for i, html in enumerate(L):
        y = PANEL_Y0 + i * PANEL_STEP
        out.append(f'<tspan x="{PANEL_X}" y="{y}">{html}</tspan>')
    out.append("</text>")
    return "\n".join(out)


def make_svg(theme):
    t = THEMES[theme]
    style = f"""<style>
@font-face {{ src: local('Consolas'), local('Consolas Bold'); font-family: 'ConsolasFallback'; font-display: swap; size-adjust: 109%; }}
text, tspan {{ white-space: pre; }}
.panel {{ fill: {t['text']}; }}
.key {{ fill: {t['key']}; }}
.value {{ fill: {t['value']}; }}
.cc {{ fill: {t['cc']}; }}
.addColor {{ fill: {t['add']}; }}
.delColor {{ fill: {t['del']}; }}
</style>"""
    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="{W}px" height="{H}px" font-size="16px">
{style}
<rect width="{W}px" height="{H}px" fill="{t['bg']}" rx="15"/>
{ascii_block(t['color_idx'])}
{panel(DATA)}
</svg>
"""
    with open(t["out"], "w") as f:
        f.write(svg)
    print("wrote", t["out"])


if __name__ == "__main__":
    make_svg("dark")
    make_svg("light")
