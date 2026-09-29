# -*- coding: utf-8 -*-
"""One page per image, at cover trim size, with the image data passed through
untouched.

PNG: PDF's FlateDecode understands PNG row predictors, so the original IDAT
stream is embedded verbatim — no decode, no re-encode, bit-identical pixels.
JPEG: DCTDecode takes the original entropy-coded bytes, so no generation loss.
Chrome's print path would have re-encoded both.
"""
import os, struct, sys

MM = 72 / 25.4
PAGE_W, PAGE_H = 135 * MM, 210 * MM      # the trim size of the book

def png_parts(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    idat, i = b"", 8
    w = h = depth = ctype = None
    while i < len(data):
        n = struct.unpack(">I", data[i:i+4])[0]
        typ = data[i+4:i+8]
        body = data[i+8:i+8+n]
        if typ == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", body)
            if depth != 8 or ctype != 2 or interlace:
                raise SystemExit(f"only 8-bit non-interlaced RGB handled (got depth={depth} type={ctype})")
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        i += 12 + n
    return w, h, idat

def jpeg_size(d):
    i = 2
    while i < len(d) - 9:
        if d[i] != 0xFF:
            i += 1; continue
        mk = d[i+1]
        if mk in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                  0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack(">HH", d[i+5:i+9]); return w, h
        if mk in (0xD8, 0xD9) or 0xD0 <= mk <= 0xD7:
            i += 2; continue
        i += 2 + struct.unpack(">H", d[i+2:i+4])[0]
    raise SystemExit("no JPEG frame header")

def image_object(path):
    raw = open(path, "rb").read()
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        w, h, stream = png_parts(raw)
        extra = (f"/Filter /FlateDecode /DecodeParms << /Predictor 15 /Colors 3 "
                 f"/BitsPerComponent 8 /Columns {w} >>")
    elif raw[:2] == b"\xff\xd8":
        w, h = jpeg_size(raw); stream = raw
        extra = "/Filter /DCTDecode"
    else:
        raise SystemExit(f"unsupported image: {path}")
    head = (f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} "
            f"/ColorSpace /DeviceRGB /BitsPerComponent 8 {extra} "
            f"/Length {len(stream)} >>").encode()
    return head, stream, w, h

def build(paths, out):
    objs = []                                   # 1-indexed body objects
    def add(b): objs.append(b); return len(objs)

    n = len(paths)
    kids_ids = [3 + i*3 for i in range(n)]      # page, content, image per file
    catalog = add(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{k} 0 R" for k in kids_ids)
    pages = add(f"<< /Type /Pages /Count {n} /Kids [{kids}] >>".encode())

    for i, p in enumerate(paths):
        pg, cid, iid = 3 + i*3, 4 + i*3, 5 + i*3
        add((f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W:.4f} {PAGE_H:.4f}] "
             f"/Resources << /XObject << /Im0 {iid} 0 R >> >> /Contents {cid} 0 R >>").encode())
        content = f"q {PAGE_W:.4f} 0 0 {PAGE_H:.4f} 0 0 cm /Im0 Do Q".encode()
        add(b"<< /Length %d >>\nstream\n%s\nendstream" % (len(content), content))
        head, stream, w, h = image_object(p)
        add(head + b"\nstream\n" + stream + b"\nendstream")
        print(f"  page {i+1}: {os.path.basename(p)}  {w}x{h}px  {w/135*25.4:.0f}dpi")

    buf = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for k, body in enumerate(objs, start=1):
        offsets.append(len(buf))
        buf += f"{k} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(buf)
    buf += f"xref\n0 {len(objs)+1}\n".encode()
    buf += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        buf += f"{off:010d} 00000 n \n".encode()
    buf += (f"trailer\n<< /Size {len(objs)+1} /Root {catalog} 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n").encode()
    open(out, "wb").write(buf)
    return out

if __name__ == "__main__":
    src = os.path.abspath("../originals")
    args = sys.argv[1:]
    out_name = "originals.pdf"
    if "--out" in args:
        i = args.index("--out"); out_name = args[i+1]; args = args[:i] + args[i+2:]
    names = args or ["tofes-17-b2-v2.png",              # amended
                     "enso-round4-v3.png",              # amended, no handwriting layer
                     "shalosh-maarachot-tor-c1.png"]    # unchanged
    files = [os.path.join(src, f) for f in names]
    for f in files:
        if not os.path.exists(f): raise SystemExit("missing: " + f)
    out = build(files, os.path.abspath("../" + out_name))
    print("wrote", out, f"{os.path.getsize(out)/1024/1024:.1f}MB")
