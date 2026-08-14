#!/usr/bin/env python3
"""
Compose a montage from a set of (messy) mobile / WhatsApp video clips.

Handles the real-world mess of phone clips:
  - mixed resolutions and portrait/landscape orientations
  - rotation metadata (auto-applied on decode)
  - different frame rates
  - clips with or without an audio track

Every clip is normalized to one common canvas with a blurred fill behind it
(so portrait clips fill the frame and landscape clips get a tasteful blurred
backdrop instead of hard black bars), a unified frame rate, and a unified
audio track (silence is synthesized where a clip has none). Titles and
per-clip captions are rendered to transparent PNGs (Pillow) and overlaid,
so we get full control over fonts, colour and shadow.

Usage:
  python3 make_montage.py --config clips.json --out montage.mp4
"""
import argparse, json, os, subprocess, sys, tempfile, shutil
from PIL import Image, ImageDraw, ImageFont

def _resolve(name, envvar, *fallbacks):
    if os.environ.get(envvar):
        return os.environ[envvar]
    onpath = shutil.which(name)
    if onpath:
        return onpath
    for f in fallbacks:
        if f and os.path.exists(f):
            return f
    return name  # last resort; will error clearly if missing

SP = os.path.dirname(os.path.abspath(__file__))
FFMPEG  = _resolve("ffmpeg",  "FFMPEG",
                   os.path.join(SP, "node_modules/ffmpeg-static/ffmpeg"))
FFPROBE = _resolve("ffprobe", "FFPROBE",
                   os.path.join(SP, "node_modules/ffprobe-static/bin/linux/x64/ffprobe"))

DEFAULT_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        sys.stderr.write("CMD FAILED: %s\n%s\n" % (" ".join(cmd), p.stderr[-4000:]))
        raise SystemExit(1)
    return p


def probe(path):
    p = run([FFPROBE, "-v", "error", "-print_format", "json",
             "-show_streams", "-show_format", path])
    info = json.loads(p.stdout)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if v is None:
        raise SystemExit("No video stream in %s" % path)
    dur = float(info["format"].get("duration") or v.get("duration") or 0)
    return {"w": int(v["width"]), "h": int(v["height"]),
            "has_audio": a is not None, "dur": dur}


def _font(path, size):
    try:
        return ImageFont.truetype(path or DEFAULT_FONT, size)
    except Exception:
        return ImageFont.truetype(DEFAULT_FONT, size)


def _text_size(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1], b[1]


def caption_png(path, cw, ch, text, fontfile):
    """Lower-third caption on a translucent pill, centered horizontally."""
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fs = max(30, ch // 26)
    font = _font(fontfile, fs)
    tw, th, off = _text_size(d, text, font)
    padx, pady = int(fs * 0.7), int(fs * 0.45)
    bw, bh = tw + 2 * padx, th + 2 * pady
    bx = (cw - bw) // 2
    by = ch - bh - ch // 12
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2,
                        fill=(14, 11, 20, 150))
    d.text((bx + padx, by + pady - off), text, font=font, fill=(244, 241, 236, 255))
    img.save(path)


def title_png(path, cw, ch, text, subtitle, fontfile):
    """Centered title (+ optional subtitle) with a soft shadow."""
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fs = max(52, cw // 11)
    font = _font(fontfile, fs)

    # wrap title to fit width
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if _text_size(d, t, font)[0] <= cw * 0.86 or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)

    line_h = int(fs * 1.16)
    subf = _font(fontfile, max(30, cw // 20))
    sub_h = int(subf.size * 1.4) if subtitle else 0
    total = len(lines) * line_h + sub_h
    y = (ch - total) // 2
    for ln in lines:
        tw, th, off = _text_size(d, ln, font)
        x = (cw - tw) // 2
        d.text((x + 3, y + 3), ln, font=font, fill=(0, 0, 0, 120))     # shadow
        d.text((x, y - off + int(fs * 0.16)), ln, font=font, fill=(244, 241, 236, 255))
        y += line_h
    if subtitle:
        tw, th, off = _text_size(d, subtitle, subf)
        d.text(((cw - tw) // 2, y + int(subf.size * 0.2) - off),
               subtitle, font=subf, fill=(182, 156, 255, 255))
    img.save(path)


def normalize(src, dst, cw, ch, fps, caption, fontfile, workdir, idx):
    info = probe(src)
    vf = (
        "[0:v]scale={cw}:{ch}:force_original_aspect_ratio=increase,"
        "crop={cw}:{ch},boxblur=luma_radius=40:luma_power=2,setsar=1[bg];"
        "[0:v]scale={cw}:{ch}:force_original_aspect_ratio=decrease,setsar=1[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[base]"
    ).format(cw=cw, ch=ch)

    extra_inputs, last = [], "[base]"
    if caption:
        png = os.path.join(workdir, "cap_%02d.png" % idx)
        caption_png(png, cw, ch, caption, fontfile)
        extra_inputs = ["-i", png]
        vf += ";[base][{n}:v]overlay=0:0[base2]".format(n=1 + (0 if info["has_audio"] else 1))
        last = "[base2]"
    vf += ";{last}fps={fps},format=yuv420p[v]".format(last=last, fps=fps)

    cmd = [FFMPEG, "-y", "-i", src]
    if not info["has_audio"]:
        cmd += ["-f", "lavfi", "-t", "%.3f" % max(info["dur"], 0.1),
                "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
    cmd += extra_inputs
    cmd += ["-filter_complex", vf, "-map", "[v]"]
    if info["has_audio"]:
        cmd += ["-map", "0:a", "-af",
                "aresample=48000,aformat=channel_layouts=stereo,"
                "loudnorm=I=-16:TP=-1.5:LRA=11"]
    else:
        cmd += ["-map", "1:a"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-r", str(fps), dst]
    run(cmd)


def make_card(dst, cw, ch, fps, text, subtitle, fontfile, secs, workdir, tag):
    png = os.path.join(workdir, "card_%s.png" % tag)
    title_png(png, cw, ch, text, subtitle, fontfile)
    vf = "[0:v][1:v]overlay=0:0,format=yuv420p[v]"
    run([FFMPEG, "-y",
         "-f", "lavfi", "-i", "color=c=0x0E0B14:s=%dx%d:r=%d:d=%s" % (cw, ch, fps, secs),
         "-i", png,
         "-f", "lavfi", "-t", str(secs),
         "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
         "-filter_complex", vf, "-map", "[v]", "-map", "2:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", "-b:a", "192k", "-r", str(fps), dst])


def concat(parts, dst, workdir):
    # All parts are already normalized to identical params, so the concat
    # *filter* joins them with perfect A/V sync (the concat demuxer can pad
    # gaps at boundaries when re-encoding). One -i per part.
    cmd = [FFMPEG, "-y"]
    for p in parts:
        cmd += ["-i", p]
    n = len(parts)
    streams = "".join("[%d:v][%d:a]" % (i, i) for i in range(n))
    fc = "%sconcat=n=%d:v=1:a=1[v][a]" % (streams, n)
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", dst]
    run(cmd)


def add_music(video, music, dst, duck=True):
    if duck:
        fc = ("[1:a]volume=0.9[m];"
              "[0:a][m]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=500[a]")
    else:
        fc = "[1:a]volume=0.25[m];[0:a][m]amix=inputs=2:duration=first[a]"
    run([FFMPEG, "-y", "-i", video, "-stream_loop", "-1", "-i", music,
         "-filter_complex", fc, "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", dst])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()

    cfg = json.load(open(args.config))
    cw, ch, fps = cfg.get("width", 1080), cfg.get("height", 1920), cfg.get("fps", 30)
    font = cfg.get("fontfile") or DEFAULT_FONT
    work = tempfile.mkdtemp(prefix="montage_")
    parts = []
    try:
        if cfg.get("title"):
            t = cfg["title"]
            p = os.path.join(work, "00_title.mp4")
            make_card(p, cw, ch, fps, t.get("text", ""), t.get("subtitle", ""),
                      font, t.get("secs", 3), work, "title")
            parts.append(p)

        for i, clip in enumerate(cfg["clips"], 1):
            src = clip["path"] if isinstance(clip, dict) else clip
            cap = clip.get("caption", "") if isinstance(clip, dict) else ""
            p = os.path.join(work, "%02d_clip.mp4" % i)
            print("normalizing (%d/%d): %s" % (i, len(cfg["clips"]), src))
            normalize(src, p, cw, ch, fps, cap, font, work, i)
            parts.append(p)

        if cfg.get("outro"):
            o = cfg["outro"]
            p = os.path.join(work, "99_outro.mp4")
            make_card(p, cw, ch, fps, o.get("text", ""), o.get("subtitle", ""),
                      font, o.get("secs", 3), work, "outro")
            parts.append(p)

        tmp = os.path.join(work, "concat.mp4")
        concat(parts, tmp, work)
        if cfg.get("music") and os.path.exists(cfg["music"]):
            add_music(tmp, cfg["music"], args.out, duck=cfg.get("duck", True))
        else:
            shutil.copy(tmp, args.out)
        print("DONE ->", args.out)
    finally:
        if args.keep:
            print("temp:", work)
        else:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
