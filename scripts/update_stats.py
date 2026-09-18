#!/usr/bin/env python3
"""Regenerate local stats SVG cards for the sdhfsl profile repo (green forest theme)."""

import json
import os
import urllib.request
from datetime import datetime, timezone

USER = "sdhfsl"
PROFILE_REPO = "sdhfsl"
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
    "CSS": "#a074c4",
    "HTML": "#e34c26",
    "SCSS": "#c6538c",
    "NSIS": "#9e9e9e",
    "Makefile": "#427819",
    "Dockerfile": "#384d54",
    "C": "#888888",
}

BG = "#0d1117"
CARD = "#131c15"
BORDER = "#26a641"
BORDER_SOFT = "#23482f"
TITLE = "#39d353"
TEXT = "#e6f4ea"
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
        ("📦 仓库", public_repos),
        ("⭐ Stars", stars),
        ("⑂ Forks", forks),
        ("👥 粉丝", followers),
        ("➕ 关注", following),
    ]
    rects = []
    x = 28
    for label, value in cards:
        cx = x + 68
        rects.append(
            f'<rect x="{x}" y="80" width="136" height="84" rx="10" fill="{CARD}" stroke="{BORDER_SOFT}" stroke-width="1.5"/>'
            f'<rect x="{x}" y="80" width="136" height="5" rx="2.5" fill="{TITLE}" opacity="0.9"/>'
            f'<text x="{cx}" y="110" text-anchor="middle" {FONT} font-size="13" fill="{MUTED}">{label}</text>'
            f'<text x="{cx}" y="146" text-anchor="middle" {FONT} font-size="30" font-weight="700" fill="{TITLE}">{value}</text>'
        )
        x += 150
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="184" viewBox="0 0 800 184">'
        f'<defs><linearGradient id="gbar" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#0e4429"/><stop offset="0.5" stop-color="#26a641"/><stop offset="1" stop-color="#39d353"/>'
        f'</linearGradient></defs>'
        f'<rect x="1" y="1" width="798" height="182" rx="12" fill="{BG}" stroke="{BORDER_SOFT}" stroke-width="1.5"/>'
        f'<rect x="1" y="1" width="798" height="6" rx="3" fill="url(#gbar)"/>'
        f'<text x="28" y="42" {FONT} font-size="20" font-weight="700" fill="{TITLE}">🌿 sdhfsl 的 GitHub 数据</text>'
        f'<text x="28" y="64" {FONT} font-size="13" fill="{MUTED}">{public_repos} public repos · {stars} stars · {forks} forks · updated {updated}</text>'
        + "".join(rects) +
        "</svg>\n"
    )


def langs_svg(top_langs, updated):
    rows = []
    y = 100
    for name, pct in top_langs:
        color = LANG_COLORS.get(name, "#39d353")
        w = max(10, round(pct / 100 * 420))
        rows.append(
            f'<circle cx="42" cy="{y - 5}" r="7" fill="{color}" stroke="#0d1117" stroke-width="1"/>'
            f'<text x="58" y="{y}" {FONT} font-size="14" font-weight="600" fill="{TEXT}">{name}</text>'
            f'<rect x="210" y="{y - 17}" width="420" height="13" rx="6.5" fill="#21262d"/>'
            f'<rect x="210" y="{y - 17}" width="{w}" height="13" rx="6.5" fill="{color}"/>'
            f'<text x="644" y="{y}" {FONT} font-size="13" font-weight="700" fill="{TITLE}">{pct:.1f}%</text>'
        )
        y += 30
    height = y + 30
    footer_y = y + 10
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{height}" viewBox="0 0 800 {height}">'
        f'<defs><linearGradient id="gbar2" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#0e4429"/><stop offset="0.5" stop-color="#26a641"/><stop offset="1" stop-color="#39d353"/>'
        f'</linearGradient></defs>'
        f'<rect x="1" y="1" width="798" height="{height - 2}" rx="12" fill="{BG}" stroke="{BORDER_SOFT}" stroke-width="1.5"/>'
        f'<rect x="1" y="1" width="798" height="6" rx="3" fill="url(#gbar2)"/>'
        f'<text x="28" y="42" {FONT} font-size="20" font-weight="700" fill="{TITLE}">💚 常用语言 / Most Used Languages</text>'
        f'<text x="28" y="64" {FONT} font-size="13" fill="{MUTED}">按代码字节统计 · 含在研 Fork 项目 · updated {updated}</text>'
        + "".join(rows) +
        f'<text x="28" y="{footer_y}" {FONT} font-size="12" fill="{FAINT}">每日由 Actions 自动更新 · 数据来自 GitHub 官方 API · 永不挂图 🌿</text>'
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
        except Exception as exc:
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
