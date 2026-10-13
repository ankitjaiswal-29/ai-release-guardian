"""Light glass evidence-mesh graphic for the connect screen."""

from __future__ import annotations

from html import escape
from typing import Any


def build_neural_topology_html(
    enabled_map: dict[str, bool],
    integrations: list[dict[str, Any]],
) -> str:
    nodes = [item for item in integrations if item["id"] != "orchestrator"]
    core_on = bool(enabled_map.get("orchestrator", True))
    linked = [item for item in nodes if enabled_map.get(item["id"])]
    live = len(linked) if core_on else 0
    cx, cy = 268, 196

    defs: list[str] = []
    ribbons: list[str] = []
    packets: list[str] = []
    cards: list[str] = []

    for index, item in enumerate(nodes):
        iid = item["id"]
        accent = item["accent"]
        source_on = bool(enabled_map.get(iid))
        on = source_on and core_on
        y = 32 + index * 48
        x = 690
        name = escape(item["name"])
        detail = escape(item["telemetry"])
        defs.append(
            f'<linearGradient id="g-{iid}" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="#94a3b8" stop-opacity="0.15"/>'
            f'<stop offset="0.45" stop-color="{accent}" stop-opacity="0.85"/>'
            f'<stop offset="1" stop-color="{accent}"/>'
            f"</linearGradient>"
        )
        if on:
            path = (
                f"M {cx + 34} {cy} C 430 {cy}, 520 {y}, {x} {y}"
            )
            ribbons.append(
                f'<path d="{path}" fill="none" stroke="{accent}" stroke-width="7" stroke-opacity="0.08"/>'
            )
            ribbons.append(
                f'<path d="{path}" fill="none" stroke="url(#g-{iid})" stroke-width="1.6"/>'
            )
            ribbons.append(
                f'<path d="{path}" class="beam" fill="none" stroke="#ffffff" stroke-width="1.4" '
                f'stroke-dasharray="2 10" stroke-opacity="0.9"/>'
            )
            duration = 2.4 + index * 0.22
            packets.append(
                f'<circle r="2.4" fill="{accent}">'
                f'<animateMotion dur="{duration:.2f}s" repeatCount="indefinite" path="{path}"/>'
                f"</circle>"
            )
            cards.append(
                f'<g>'
                f'<rect x="{x}" y="{y - 16}" width="360" height="32" rx="10" fill="#ffffff" '
                f'stroke="{accent}" stroke-opacity="0.45"/>'
                f'<rect x="{x}" y="{y - 16}" width="3" height="32" rx="2" fill="{accent}"/>'
                f'<circle cx="{x + 16}" cy="{y}" r="3" fill="{accent}"/>'
                f'<text x="{x + 28}" y="{y - 2}" font-size="11" font-weight="700" fill="#0f172a">{name}</text>'
                f'<text x="{x + 28}" y="{y + 11}" font-size="9" fill="#64748b">{detail}</text>'
                f'<text x="{x + 308}" y="{y + 3}" font-size="9" font-weight="700" fill="#047857">Live</text>'
                f"</g>"
            )
        elif source_on:
            cards.append(
                f'<g>'
                f'<rect x="{x}" y="{y - 16}" width="360" height="32" rx="10" fill="#ffffff" stroke="#e2e8f0"/>'
                f'<text x="{x + 16}" y="{y - 2}" font-size="11" font-weight="700" fill="#0f172a">{name}</text>'
                f'<text x="{x + 16}" y="{y + 11}" font-size="9" fill="#64748b">{detail}</text>'
                f'<text x="{x + 292}" y="{y + 3}" font-size="9" font-weight="700" fill="#b45309">No core</text>'
                f"</g>"
            )
        else:
            cards.append(
                f'<g opacity="0.55">'
                f'<rect x="{x}" y="{y - 16}" width="360" height="32" rx="10" fill="#f8fafc" '
                f'stroke="#e2e8f0" stroke-dasharray="4 3"/>'
                f'<text x="{x + 16}" y="{y - 2}" font-size="11" font-weight="650" fill="#94a3b8">{name}</text>'
                f'<text x="{x + 16}" y="{y + 11}" font-size="9" fill="#cbd5e1">Not linked</text>'
                f"</g>"
            )

    core_fill = "#312e81" if core_on else "#94a3b8"
    status = "Core online" if core_on else "Core offline"
    status_color = "#4338ca" if core_on else "#64748b"

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/>
<style>
  body {{ margin:0; background:transparent; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
  .frame {{
    height:392px; border-radius:16px; overflow:hidden;
    background:
      radial-gradient(420px 220px at 268px 196px, rgba(99,102,241,.16), transparent 70%),
      linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border:1px solid #e2e8f0;
    box-shadow:0 16px 40px rgba(15,23,42,.05);
  }}
  .orbit {{ transform-origin:{cx}px {cy}px; animation:spin 28s linear infinite; }}
  .orbit-b {{ transform-origin:{cx}px {cy}px; animation:spin 18s linear infinite reverse; }}
  .halo {{ transform-origin:{cx}px {cy}px; animation:pulse 3.6s ease-in-out infinite; }}
  .beam {{ animation:flow 1.8s linear infinite; }}
  @keyframes spin {{ to {{ transform:rotate(360deg); }} }}
  @keyframes pulse {{ 50% {{ opacity:.55; }} }}
  @keyframes flow {{ to {{ stroke-dashoffset:-48; }} }}
</style></head>
<body><div class="frame">
<svg width="100%" height="392" viewBox="0 0 1080 392">
  <defs>
    <pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="0.7" fill="#cbd5e1"/>
    </pattern>
    <radialGradient id="orb" cx="32%" cy="30%" r="70%">
      <stop offset="0" stop-color="#eef2ff"/>
      <stop offset="42%" stop-color="#818cf8"/>
      <stop offset="100%" stop-color="{core_fill}"/>
    </radialGradient>
    <filter id="soft"><feGaussianBlur stdDeviation="6"/></filter>
    {''.join(defs)}
  </defs>
  <rect width="1080" height="392" fill="url(#dots)" opacity="0.45"/>
  <g>{''.join(ribbons)}</g>
  <g>{''.join(packets)}</g>
  <g>
    <rect x="28" y="28" width="132" height="54" rx="12" fill="#ffffff" stroke="#e2e8f0"/>
    <text x="42" y="50" font-size="10" fill="#64748b">Stories</text>
    <text x="42" y="70" font-size="16" font-weight="700" fill="#0f172a">24</text>
    <rect x="28" y="94" width="132" height="54" rx="12" fill="#ffffff" stroke="#e2e8f0"/>
    <text x="42" y="116" font-size="10" fill="#64748b">Tests</text>
    <text x="42" y="136" font-size="16" font-weight="700" fill="#0f172a">156</text>
    <rect x="28" y="160" width="132" height="54" rx="12" fill="#ffffff" stroke="#e2e8f0"/>
    <text x="42" y="182" font-size="10" fill="#64748b">Open defects</text>
    <text x="42" y="202" font-size="16" font-weight="700" fill="#0f172a">7</text>
  </g>
  <g>
    <circle class="halo" cx="{cx}" cy="{cy}" r="78" fill="#c7d2fe" filter="url(#soft)" opacity="0.85"/>
    <ellipse class="orbit" cx="{cx}" cy="{cy}" rx="108" ry="78" fill="none" stroke="#c7d2fe" stroke-dasharray="3 7"/>
    <ellipse class="orbit-b" cx="{cx}" cy="{cy}" rx="86" ry="60" fill="none" stroke="#bae6fd" stroke-dasharray="2 6"/>
    <circle cx="{cx}" cy="{cy}" r="34" fill="url(#orb)"/>
    <circle cx="{cx - 10}" cy="{cy - 12}" r="8" fill="#ffffff" opacity="0.55"/>
    <text x="{cx}" y="{cy + 58}" text-anchor="middle" font-size="11" font-weight="750" fill="#0f172a">Release Guardian</text>
    <text x="{cx}" y="{cy + 74}" text-anchor="middle" font-size="10" fill="{status_color}">{status} · {live} live</text>
  </g>
  <g>{''.join(cards)}</g>
</svg>
</div></body></html>"""
