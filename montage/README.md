# Recovery montage builder

A small, tested pipeline for stitching a pile of phone clips (e.g. videos
shared in a WhatsApp group) into one clean montage video — the kind of thing
you'd make to celebrate a friend's recovery.

It is built to survive the mess that real phone/WhatsApp clips come in:

- **mixed resolutions** and **portrait / landscape / square** orientations
- **rotation metadata** (auto-applied so nothing ends up sideways)
- **different frame rates**
- **clips with or without an audio track**

Every clip is normalized onto one shared canvas. Portrait clips fill a
portrait canvas; landscape or square clips are centered over a softly
**blurred copy of themselves** so there are no ugly black bars. Frame rate
and audio format are unified (silence is synthesized for silent clips), so
the pieces join with perfect sync.

## What it can add

- an opening **title card** (title + subtitle)
- a per-clip **caption** (a milestone label on a translucent pill)
- a per-clip **trim** (`ss` = start seconds, `t` = length) so you can keep just
  the meaningful few seconds of a long clip
- a **progress timeline** across the top — a story-style filmstrip of circular
  thumbnails taken from the clips themselves: past ones lit, upcoming ones
  dimmed, the current clip enlarged with a glow, riding a line that fills as the
  story advances (driven by a per-clip `date`)
- a closing **outro card**
- **background music**, automatically *ducked* under any spoken audio in the
  clips (music dips when someone is talking, comes back up otherwise)
- **right-to-left text** (Hebrew / Arabic) rendered correctly (Pillow+libraqm
  when available, otherwise `python-bidi`)

## Requirements

- `ffmpeg` and `ffprobe` (any recent build) on `PATH`, or point to them with
  the `FFMPEG` / `FFPROBE` environment variables.
- Python 3 with `Pillow` (`pip install Pillow`).
- For Hebrew/Arabic captions, `python-bidi` (`pip install python-bidi`) and a
  font that covers the script (e.g. DejaVu Sans, which ships on most Linux).

If you don't have a system ffmpeg, static builds work fine:

```bash
npm install ffmpeg-static ffprobe-static
export FFMPEG=$(node -e "console.log(require('ffmpeg-static'))")
export FFPROBE=$(node -e "console.log(require('ffprobe-static').path)")
```

## Usage

1. Put the clips in a `clips/` folder (any names).
2. Copy `clips.example.json` to `clips.json` and edit it: list the clips in
   the order you want, give each an optional caption, set the title/outro,
   and point `music` at an audio file (or remove that key for no music).
3. Run:

```bash
python3 make_montage.py --config clips.json --out montage.mp4
```

### Config reference

| key            | meaning                                                        |
|----------------|----------------------------------------------------------------|
| `width/height` | output canvas. `1080x1920` = vertical (phones/WhatsApp), `1920x1080` = horizontal, `1080x1080` = square |
| `fps`          | output frame rate (30 is a good default)                       |
| `fontfile`     | path to a `.ttf` used for all text                             |
| `title`        | `{text, subtitle, secs}` opening card — omit for no title      |
| `clips`        | ordered list of `{path, caption, ss, t, date}` — all but `path` optional. `date` (ISO `YYYY-MM-DD`, or `DD.MM`) places the clip on the timeline; if omitted it is parsed from a `YYYY-MM-DD` in the filename |
| `timeline`     | `true` (default) draws the progress timeline when clip dates are known; `false` disables it |
| `outro`        | `{text, subtitle, secs}` closing card — omit for no outro      |
| `music`        | path to an audio file — omit for none (clips keep their audio) |
| `duck`         | `true` = dip music under speech; `false` = simple quiet mix    |
| `music_vol`    | base music level before ducking (0–1, default 0.6)            |
| `music_ss`     | start offset into the music track, seconds (default 0)        |
| `fade`         | music fade in/out length, seconds (default 2.5)               |
| `preset`       | libx264 speed/quality preset (default `medium`; `veryfast` for quick drafts) |

## Notes

- Order the clips **chronologically** for a recovery-progress feel; captions
  like "Week 1 · ICU → Week 10 · First steps" make the arc land.
- Music must be a file you have the right to use. Drop it in `clips/`.
- Longer/higher-resolution source clips take longer to encode; the pipeline
  re-encodes everything once to guarantee clean joins.
