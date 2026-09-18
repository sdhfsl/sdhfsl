#!/usr/bin/env python3
"""Regenerate local stats SVG cards for the sdhfsl profile repo.

Reads public data from the GitHub REST API (stdlib only) and writes:
  assets/stats.svg  - repo / star / fork / follower overview
  assets/langs.svg  - top-8 languages by bytes across code repos

Run locally:  python scripts/update_stats.py
In CI the workflow passes GH_TOKEN / GITHUB_TOKEN automatically.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone

USER = "sdhfsl"
PROFILE_REPO = "sdhfsl"  # language stats skip this repo (no code)
API = "https://api.github.com"
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

LANG_COLORS = {
    "Go": "#00ADD8",
    "TypeScript": "#3178C6",
    "JavaScript": "#f1e05a",
    "Python": "#3572A5",
    "C#": "#178600",
    "Rust": "#dea584",
    "Shell": "#89e051",
    "CSS": "#563d7c",
    "HTML": "#e34c26",
    "SCSS": "#c6538c",
    "NSIS": "#777777",
    "Makefile": "#427819",
    "Dockerfile": "#384d54",
    "C": "#555555",
}

BG = "#0d1117"
CARD = "#161b22"
BORDER = "#30363d"
TITLE = "#00c6ff"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
FAINT = "#6e7681"
FONT = "font-family=\"'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif\""


def api(path):
    req = urllib.request.Request(
        API + path,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "sdhfsl-stats-cards"},
    )
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def stats_svg(public_repos, stars, forks, followers, following, updated):
    cards = [
        ("\U0001f4e6 \u4ed3\u5e93 Repos", public_repos),
        ("\u2b50 Stars", stars),
        ("\U0001f374 Forks", forks),
        ("\U0001f465 Followers", followers),
        ("\u2795 Following", following),
    ]
    rects = []
    x = 28
    for label, value in cards:
        cx = x + 68
        rects.append(
            f'<rect x="{x}" y="76" width="136" height="82" rx="8" fill="{CARD}" stroke="{BORDER}"/>'
            f'<text x="{cx}" y="102" text-anchor="middle" {FONT} font-size="13" fill="{MUTED}">{label}</text>'
            f'<text x="{cx}" y="138" text-anchor="middle" {FONT} font-size="30" font-weight="700" fill="#ffffff">{value}</text>'
        )
        x += 150
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="176" viewBox="0 0 800 176">'
        f'<rect x="1" y="1" width="798" height="174" rx="10" fill="{BG}" stroke="{BORDER}"/>'
        f'<text x="28" y="38" {FONT} font-size="20" font-weight="700" fill="{TITLE}">\U0001f4ca sdhfsl \u7684 GitHub \u6570\u636e</text>'
        f'<text x="28" y="60" {FONT} font-size="13" fill="{MUTED}">{public_repos} public repos \u00b7 {stars} stars earned \u00b7 {forks} forks \u00b7 updated {updated}</text>'
        + "".join(rects) +
        "</svg>\n"
    )


def langs_svg(top_langs, updated):
    rows = []
    y = 96
    for name, pct in top_langs:
        color = LANG_COLORS.get(name, "#858585")
        w = max(8, round(pct / 100 * 440))
        rows.append(
            f'<circle cx="40" cy="{y - 5}" r="7" fill="{color}"/>'
            f'<text x="56" y="{y}" {FONT} font-size="14" fill="{TEXT}">{name}</text>'
            f'<rect x="200" y="{y - 17}" width="440" height="12" rx="6" fill="#21262d"/>'
            f'<rect x="200" y="{y - 17}" width="{w}" height="12" rx="6" fill="{color}"/>'
            f'<text x="652" y="{y}" {FONT} font-size="13" fill="{MUTED}">{pct:.1f}%</text>'
        )
        y += 30
    height = y + 22
    footer_y = y + 6
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{height}" viewBox="0 0 800 {height}">'
        f'<rect x="1" y="1" width="798" height="{height - 2}" rx="10" fill="{BG}" stroke="{BORDER}"/>'
        f'<text x="28" y="38" {FONT} font-size="20" font-weight="700" fill="{TITLE}">\U0001f4bb \u5e38\u7528\u8bed\u8a00 / Most Used Languages</text>'
        f'<text x="28" y="60" {FONT} font-size="13" fill="{MUTED}">\u6309\u4ee3\u7801\u5b57\u8282\u7edf\u8ba1 \u00b7 \u542b\u5728\u7814 Fork \u9879\u76ee \u00b7 updated {updated}</text>'
        + "".join(rows) +
        f'<text x="28" y="{footer_y}" {FONT} font-size="12" fill="{FAINT}">\u6bcf\u65e5\u7531 Actions \u81ea\u52a8\u66f4\u65b0 \u00b7 \u6c38\u4e0d\u6302\u56fe</text>'
        "</svg>\n"
    )


def main():
    user = api(f"/users/{USER}")
    repos = api(f"/users/{USER}/repos?per_page=100")
    code_repos = [r for r in repos if r["name"] != PROFILE_REPO]
    stars = sum(r.get("stargazers_count", 0) for r in repos)
    forks = sum(r.get("forks_count", 0) for r in repos)

    lang_total = {}
    for repo in code_repos:
        name = repo["name"]
        try:
            langs = api(f"/repos/{USER}/{name}/languages")
        except Exception as exc:  # keep old cards rather than fail the run
            print(f"warn: languages for {name} failed: {exc}")
            continue
        for lang, count in langs.items():
            lang_total[lang] = lang_total.get(lang, 0) + count

    if not lang_total:
        raise SystemExit("no language data fetched, keeping old cards")

    total = sum(lang_total.values())
    top = sorted(lang_total.items(), key=lambda kv: -kv[1])[:8]
    top_pct = [(name, count / total * 100) for name, count in top]
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets = os.path.join(root, "assets")
    os.makedirs(assets, exist_ok=True)
    with open(os.path.join(assets, "stats.svg"), "w", encoding="utf-8") as fh:
        fh.write(stats_svg(user.get("public_repos", 0), stars, forks,
                            user.get("followers", 0), user.get("following", 0), updated))
    with open(os.path.join(assets, "langs.svg"), "w", encoding="utf-8") as fh:
        fh.write(langs_svg(top_pct, updated))
    print(f"wrote stats.svg + langs.svg ({len(code_repos)} code repos, {total} bytes)")


if __name__ == "__main__":
    main()
