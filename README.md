# Lazy Sleep - Smart Shutdown Timer

An Electron-based shutdown timer app. Set a timer with a slider or manual input, schedule Windows shutdown, and forget about it.

## Todo

### Core Functionality

- [x] **Slider timer** — Horizontal slider (0–180 min) to pick shutdown delay
- [x] **Custom time input** — Toggle to manual hours/minutes entry for any duration
- [x] **Schedule shutdown** — Execute `shutdown -s -t <seconds>` via Node child_process
- [x] **Cancel shutdown** — Execute `shutdown -a` to abort a pending shutdown
- [x] **Countdown display** — Show the calculated shutdown time (e.g. "Shutdown at: 11:42 PM")
- [x] **Prompt before shutdown** — If >3 min scheduled, prompt user 3 min before to confirm/cancel
- [x] **Immediate shutdown confirmation** — Confirm dialog when slider is at 0

### UI / Visuals (follows designrules.md)

- [x] **Flat, opaque UI** — No gradients, no shadows, no glassmorphism, solid matte backgrounds
- [x] **1px border containers** — All panels, buttons, inputs defined by thin dark borders
- [x] **Technical sans-serif typography** — Clean, utilitarian font (e.g. Inter, IBM Plex Sans)
- [x] **Functional type scaling** — Large countdown/time display, small uniform labels
- [x] **Muted natural palette** — Monochromatic base (off-white / sage / dark grey) with black text/lines
- [x] **No emojis** — Thin-stroke line-art icons only
- [x] **Rigid grid layout** — Dashboard/schematic aesthetic, compartmentalised zones
- [x] **Aggressively 2D** — No depth, no layering effects, hard edges only

### Theming

- [x] **Theme switcher** — Dropdown to select: white, light grey, dark grey, black
- [x] **Persist theme** — Save selection to config.json, restore on launch

### Window Behaviour

- [x] **Always on top** — Window stays above all others
- [x] **Invisibility mode** — Toggle to auto-hide (opacity 0) when mouse leaves detection radius; reappear on hover
- [x] **Personalised greeting** — Display "Hello, {username}!" using OS account name

### Packaging

- [ ] **Electron Builder** — Package as standalone `.exe` for Windows via `electron-builder`
- [ ] **Custom icon** — App icon (clock2.ico) applied to window and exe

## Development

```bash
npm install
npm start
```

## Build

```bash
npm run build
```

## Requirements

- Windows 10/11
- Node.js 18+
