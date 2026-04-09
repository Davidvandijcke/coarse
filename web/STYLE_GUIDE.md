# 'coarse — Visual Style Guide

## Concept: "The Blackboard"

The aesthetic is a worn classroom blackboard. Dark slate surface, chalk writing with varying intensity, subtle dust texture. The name "coarse" implies roughness and imperfection — lean into that. Nothing should look polished or corporate.

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--board` | `#1E2529` | Primary background — dark blue-slate, like a real blackboard |
| `--board-surface` | `#242D33` | Slightly lighter surfaces (panels, code blocks, drop zones) |
| `--chalk` | `#D8D3CA` | Body text — warm off-white, like chalk on slate |
| `--chalk-bright` | `#EDE9E3` | Headings, emphasis — fresh chalk, brighter |
| `--dust` | `#6B6862` | Muted text, labels, faded content — erased chalk residue |
| `--yellow-chalk` | `#D4A843` | Primary accent — yellow chalk stick. Scores, active states, CTA buttons |
| `--blue-chalk` | `#7BA7BC` | Links, secondary accent — blue chalk |
| `--red-chalk` | `#C27C6B` | Blockquote borders, errors — red chalk / teacher's corrections |
| `--tray` | `#2A3138` | Borders, dividers — the blackboard tray/ledge |
| `--smudge` | `rgba(216, 211, 202, 0.04)` | Subtle background tint |

### Rules
- Never use pure black (`#000`) or pure white (`#fff`)
- The board colors have a blue undertone, not brown or green
- Chalk colors are warm (yellowish white), not cool/blue-white
- Accents are dusty and muted, not saturated or neon

## Typography

| Role | Font | Fallback | Usage |
|------|------|----------|-------|
| Display/headings | `Young Serif` | Georgia, serif | Page titles, section headings, logo. Weight 400 only — it has natural warmth without bolding. |
| Handwritten/labels | `Caveat` | "Marker Felt", cursive | Section labels, annotations, metric labels, buttons, helper text. The chalk-handwriting feel. 400-700 weight range. |
| Body | `Georgia` | "Times New Roman", serif | Review content, paragraphs, long-form text. System font, highly readable. |
| Code/mono | `Space Mono` | "Courier New", monospace | Code blocks, API keys, technical values. |

### Rules
- Young Serif is NOT italic and NOT bold. Use it at weight 400. Its character comes from its shape, not weight.
- Caveat replaces all instances where you'd previously use small-caps mono labels. It's warmer and more human.
- Never use Inter, Roboto, Arial, or system sans-serif fonts anywhere.
- Body text is always Georgia — don't switch it to Young Serif or Caveat for paragraphs.

## Textures & Effects

### Chalk dust overlay
Applied via `body::after` — a fixed full-screen noise texture at very low opacity (0.035) with `mix-blend-mode: overlay`. Uses high-frequency fractalNoise (baseFrequency 1.2) for fine grain.

### Ink-rough filter
SVG filter (`#ink-rough`) using feTurbulence + feDisplacementMap. Applied to:
- Horizontal rules (CharcoalRule component)
- Active chalk-tab underlines
- Review content `<hr>` elements

This gives lines a hand-drawn, slightly uneven quality. The displacement is subtle (scale=2).

### Chalk underline (active tabs)
Active selector tabs get a 2.5px bottom pseudo-element in `--yellow-chalk`, filtered through `ink-rough`. On hover (inactive), the underline appears at 0.3 opacity. This replaces bordered button boxes.

## Layout Principles

### No borders where possible
- Header has no bottom border — just floats on the board
- Panel dividers use a thin SVG chalk line (0.5px, 20% opacity, ink-rough filtered) instead of CSS borders
- Sections are separated by CharcoalRule (textured SVG line) or whitespace

### Selectors are text, not buttons
- Tabs/selectors are plain text with chalk underlines, not bordered boxes
- Active = bright chalk text + yellow underline
- Inactive = dust-colored text
- Disabled = tray-colored text, no underline, no pointer

### Quality scores feel scrawled
- Large Caveat font, yellow-chalk color
- Slight rotation (`rotate(-1.5deg)`) like a grade written on a paper
- Metric labels (Coverage, Specificity, Depth) in Caveat, dust-colored

### The compare page is a split blackboard
- Two panels side by side, separated by a thin chalk line
- Left panel is labeled "'coarse" above the model selectors
- Both panels scroll independently with thin (4px) chalk-colored scrollbars

## Component Patterns

### CharcoalRule
Textured horizontal SVG line. Stroke: chalk color at 35% opacity, ink-rough filtered. Used as section dividers.

### HeroMarks
Faint yellow-chalk SVG annotations (brackets, circles, underlines, check marks, question marks) suggesting academic markup. Very low opacity (0.06-0.18). Positioned absolutely behind hero content.

### PanelErrorBoundary
React error boundary wrapping each ReactMarkdown panel. Fallback message in Caveat font, dust color.

## Anti-patterns

- No purple gradients, no gradient backgrounds of any kind
- No rounded corners > 2px
- No box shadows
- No sans-serif fonts
- No uppercase monospace labels (use Caveat instead)
- No bordered/filled button-style selectors (use chalk underlines)
- No bright saturated colors — everything is dusty and warm
- No hover effects that add backgrounds or fill — use color/opacity transitions only
