#!/usr/bin/env python3
"""Build the portable theme and a local, dependency-free design preview."""

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSS_LIMIT = 20_000


def luminance(color):
    channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
              for value in channels]
    return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(foreground, background):
    low, high = sorted((luminance(foreground), luminance(background)))
    return (high + 0.05) / (low + 0.05)


def read_theme():
    theme = json.loads((ROOT / "src/theme.json").read_text())
    css = (ROOT / "src/paper-ink.css").read_text()
    if theme.get("version") != 1:
        raise ValueError("ThemeFile version must be 1.")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", theme.get("id", "")):
        raise ValueError("Invalid theme id.")
    if not isinstance(theme.get("name"), str) or not 1 <= len(theme["name"]) <= 48:
        raise ValueError("Theme name must have 1–48 characters.")
    if theme.get("appearance") != "light":
        raise ValueError("Paper / Ink currently supports light appearance only.")
    if not isinstance(theme.get("colors"), dict) or not theme["colors"]:
        raise ValueError("A palette is required.")
    for role, color in theme["colors"].items():
        if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
            raise ValueError(f"{role}: source palette values must be six-digit hex colors.")
    css_length = len(css.encode("utf-16-le")) // 2
    if not 0 < css_length <= CSS_LIMIT:
        raise ValueError(f"CSS is {css_length} characters; the limit is {CSS_LIMIT}.")
    if re.search(r"@import\b|image-set\s*\(", css, re.IGNORECASE):
        raise ValueError("Custom CSS cannot load external styles or image sets.")
    for url in re.findall(r"url\(\s*['\"]?([^\s'\")]+)", css, re.IGNORECASE):
        if not url.lower().startswith(("data:", "#")):
            raise ValueError("Custom CSS image URLs must be embedded data or fragment URLs.")
    return {**theme, "css": css}


def palette_css(colors):
    roles = {
        "background": "canvas", "foreground": "text", "muted": "muted",
        "muted-foreground": "mutedForeground", "border": "border", "input": "input",
        "primary": "messageAction", "primary-foreground": "messageActionForeground",
        "accent": "accentSurface", "accent-foreground": "accentSurfaceForeground",
        "secondary": "secondary", "secondary-foreground": "secondaryForeground",
        "code-background": "codeBackground", "sidebar": "sidebar",
        "sidebar-foreground": "sidebarForeground", "message-surface": "messageSurface",
        "message-foreground": "messageForeground", "popover": "surfaceOverlay",
        "error": "error", "error-foreground": "errorForeground", "error-surface": "errorSurface",
        "warning": "warning", "warning-foreground": "warningForeground",
        "warning-surface": "warningSurface", "update-foreground": "updateForeground",
    }
    declarations = [f"--{token}: {colors[role]};" for token, role in roles.items()]
    return ":root {\n" + "\n".join(declarations) + "\n}"


def artifacts(theme):
    template = (ROOT / "src/preview.html").read_text()
    for placeholder in ("{{PALETTE_CSS}}", "{{THEME_CSS}}"):
        if template.count(placeholder) != 1:
            raise ValueError(f"Preview must include {placeholder} exactly once.")
    # The theme is trusted repository source, but must not terminate its HTML style block.
    css = re.sub(r"</style", r"<\/style", theme["css"], flags=re.IGNORECASE)
    preview = template.replace("{{PALETTE_CSS}}", palette_css(theme["colors"]))
    preview = preview.replace("{{THEME_CSS}}", css)
    return {
        ROOT / "paper-ink.json": json.dumps(theme, ensure_ascii=False, indent=2) + "\n",
        ROOT / "preview.html": preview,
    }


def check_contrast(colors):
    pairs = [
        ("text", "canvas"), ("text", "surface"), ("textMuted", "canvas"),
        ("mutedForeground", "surface"), ("placeholder", "input"),
        ("sidebarForeground", "sidebar"), ("sidebarMutedForeground", "sidebar"),
        ("messageForeground", "messageSurface"), ("codeForeground", "codeBackground"),
        ("terminalForeground", "terminalBackground"),
        ("messageActionForeground", "messageAction"),
        ("messageActionForeground", "messageActionHover"),
        ("errorForeground", "errorSurface"), ("warningForeground", "warningSurface"),
        ("updateForeground", "updateSurface"),
    ]
    ratios = []
    for foreground, background in pairs:
        ratio = contrast(colors[foreground], colors[background])
        if ratio < 4.5:
            raise ValueError(f"{foreground} on {background}: {ratio:.2f}:1, expected at least 4.5:1.")
        ratios.append(ratio)
    print(f"Palette: {len(pairs)} text pairs pass 4.5:1; minimum {min(ratios):.2f}:1.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check"))
    action = parser.parse_args().action
    theme = read_theme()
    outputs = artifacts(theme)
    check_contrast(theme["colors"])
    if action == "build":
        for path, contents in outputs.items():
            temporary = path.with_suffix(path.suffix + ".tmp")
            temporary.write_text(contents)
            temporary.replace(path)
        print("Built paper-ink.json and preview.html.")
    else:
        stale = [path.name for path, expected in outputs.items()
                 if not path.exists() or path.read_text() != expected]
        if stale:
            raise ValueError("Generated files are stale: " + ", ".join(stale) + ". Run the build.")
        print("Generated files match the sources.")
    print(f"Custom CSS: {len(theme['css'].encode('utf-16-le')) // 2}/{CSS_LIMIT} characters.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
