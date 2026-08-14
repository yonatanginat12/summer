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
- a per-clip **caption** (a date or milestone label, on a translucent pill)
- a per-clip **trim** (`ss` = start seconds, `t` = length) so you can keep just
  the meaningful few seconds of a long clip
- a closing **outro card**
- **background music**, automatically *ducked* under any spoken audio in the
  clips (music dips when someone is talking, comes back up otherwise)
- **right-to-left text** (Hebrew / Arabic) rendered correctly, via `python-bidi`

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
| `clips`        | ordered list of `{path, caption, ss, t}` — `caption`, `ss` (start offset, seconds) and `t` (length, seconds) are all optional |
| `outro`        | `{text, subtitle, secs}` closing card — omit for no outro      |
| `music`        | path to an audio file — omit for none (clips keep their audio) |
| `duck`         | `true` = dip music under speech; `false` = simple quiet mix    |

## Notes

- Order the clips **chronologically** for a recovery-progress feel; captions
  like "Week 1 · ICU → Week 10 · First steps" make the arc land.
- Music must be a file you have the right to use. Drop it in `clips/`.
- Longer/higher-resolution source clips take longer to encode; the pipeline
  re-encodes everything once to guarantee clean joins.
