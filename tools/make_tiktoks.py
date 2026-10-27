"""Render funny TikTok videos (1080x1920, 30fps) from tiktok-src/<slug>.json into tiktok/<slug>.mp4.

Usage:  python3 tools/make_tiktoks.py [slug ...] [--preview]

Two formats:

1) "chat"  – fake-but-generic DM conversation between "Client" and the agency, with typing dots and pop sounds.
{
  "type": "chat", "duration": 12.0, "music_seed": 5,
  "caption": "Every designer at [[11 PM]]:",        # meme caption above the chat ([[ ]] = blue)
  "contact": "Client",
  "messages": [                                       # "from": "them" (client, left) | "us" (agency, right)
    {"from": "them", "t": "Quick question", "at": 0.4, "typing": false},   # first message visible at once = hook
    {"from": "us", "t": "Sure!", "at": 2.0},          # typing dots appear 0.7 s before "at" (set typingFor to change)
  ],
  "end": {"at": 10.0, "line": "We speak fluent [[client.]]", "cta": "FOLLOW FOR MORE"}
}
Keep it to ~6-8 short messages so they fit the chat panel.

2) "text"  – kinetic text, same scene format as reels-src/*.json (see tools/make_reels.py), plus "type": "text".

3) "meme"  – classic reaction meme: caption on top, a licensed stock clip (stock/, see stock/SOURCES.md) in a square below.
{
  "type": "meme", "music_seed": 4,
  "caption": "When the client says it needs more [[pop]]",
  "cap_size": 84,                                  # optional, shrink for long captions
  "clip": "stock/mixkit-25575.mp4", "start": 1.0, "length": 7.0,
  "cx": 0.45, "cy": 0.5,                          # crop centre (0..1) of the square cut from the clip
  "end": {"line": "We speak fluent [[client.]]", "cta": "FOLLOW FOR MORE", "length": 2.2}
}

Humour rules: relatable agency / client / small-business-owner situations, punch up never down, no real people or
brands, no insults about clients' appearance, nationality etc. English only.
"""
import json, pathlib, subprocess, sys, shutil, tempfile
import numpy as np, wave
from playwright.sync_api import sync_playwright

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import music, make_reels  # noqa: E402

FPS, SR = 30, music.SR
BRAND = REPO / "brand"

def chat_html(data, tmp):
    full = (BRAND / "logo-full.png").as_uri()
    h = ((REPO / "tools/chat_template.html").read_text()
         .replace("FONTS_CSS", (BRAND / "fonts/fonts.css").as_uri())
         .replace("LOGOFULL", full).replace("__DATA__", json.dumps(data)))
    f = tmp / "chat.html"; f.write_text(h); return f

def pop(freq=880, dur=0.09):
    t = np.arange(int(dur * SR)) / SR
    f = freq * (1 + 0.6 * np.exp(-t * 40))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35) * 0.5

def soundtrack(data, path, slug):
    total = data["duration"]
    x = music.track(total, data.get("music_seed", hash(slug) % 97)) * 0.45
    times = []
    if data["type"] == "chat":
        times = [(m["at"], 1100 if m["from"] == "us" else 760) for m in data["messages"]]
        times.append((data["end"]["at"], 520))
    else:
        times = [(sc["start"], 700) for sc in data["scenes"] if sc["start"] > 0]
    for at, fq in times:
        s = pop(fq); a = int(at * SR)
        if a < x.size:
            x[a:a + s.size] += s[: x.size - a]
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.85
    pcm = (np.stack([x, x], axis=1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

VIDEO_TOP = 520

def render_meme(data, slug, tmp, pg, out, preview):
    full = (BRAND / "logo-full.png").as_uri()
    acc = lambda t: t.replace("[[", '<span class="a">').replace("]]", "</span>")
    h = ((REPO / "tools/meme_frame.html").read_text()
         .replace("FONTS_CSS", (BRAND / "fonts/fonts.css").as_uri()).replace("LOGOFULL", full)
         .replace("VIDEO_TOP", str(VIDEO_TOP)).replace("VIDEO_BOTTOM", str(VIDEO_TOP + 1080))
         .replace("CAP_SIZE", str(data.get("cap_size", 84)))
         .replace(">CAPTION<", ">" + acc(data["caption"]) + "<")
         .replace(">ENDLINE<", ">" + acc(data["end"]["line"]) + "<").replace(">CTA<", ">" + data["end"]["cta"] + "<"))
    f = tmp / "meme.html"; f.write_text(h)
    pg.goto(f.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
    pg.screenshot(path=str(tmp / "frame.png"), omit_background=True)
    pg.evaluate("document.getElementById('frame').style.display='none';document.getElementById('end').style.display='flex'")
    pg.screenshot(path=str(tmp / "end.png"))
    L, E = data["length"], data["end"].get("length", 2.2)
    cx, cy = data.get("cx", 0.5), data.get("cy", 0.5)
    clip = str(REPO / data["clip"])
    vf = (f"color=c=0x050c26:s=1080x1920:r=30:d={L}[bg];"
          f"[0:v]crop=w='min(iw,ih)':h='min(iw,ih)':x='(iw-min(iw,ih))*{cx}':y='(ih-min(iw,ih))*{cy}',scale=1080:1080,setsar=1,fps=30[v];"
          f"[bg][v]overlay=0:{VIDEO_TOP}:shortest=1[b1];[b1][1:v]overlay=0:0,format=yuv420p,setsar=1[m];"
          f"[2:v]scale=1080:1920,fps=30,format=yuv420p,setsar=1[e];[m][e]concat=n=2:v=1:a=0[out]")
    if preview:
        pd = out / "_preview"; pd.mkdir(exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(data["start"] + L / 2), "-t", "0.1", "-i", clip,
                        "-loop", "1", "-t", "0.1", "-i", str(tmp / "frame.png"), "-loop", "1", "-t", "0.1", "-i", str(tmp / "end.png"),
                        "-filter_complex", vf.replace(f"d={L}", "d=0.1"), "-map", "[out]", "-frames:v", "1", str(pd / f"{slug}-0.jpg")], check=True)
        shutil.copy(tmp / "end.png", pd / f"{slug}-1.png"); print("preview", slug); return
    total = L + E
    wav = tmp / "a.wav"
    x = music.track(total, data.get("music_seed", hash(slug) % 97)) * 0.4
    for at, fq in ((0.0, 900), (L, 520)):
        sp = pop(fq); a = int(at * SR); x[a:a + sp.size] += sp[: x.size - a]
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.85
    pcm = (np.stack([x, x], axis=1) * 32767).astype(np.int16)
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(data["start"]), "-t", str(L), "-i", clip,
                    "-loop", "1", "-t", str(L), "-i", str(tmp / "frame.png"), "-loop", "1", "-t", str(E), "-i", str(tmp / "end.png"),
                    "-i", str(wav), "-filter_complex", vf, "-map", "[out]", "-map", "3:a", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    str(out / f"{slug}.mp4")], check=True)
    print("tiktok", slug)

def main(slugs, preview):
    slugs = slugs or sorted(p.stem for p in (REPO / "tiktok-src").glob("*.json"))
    out = REPO / "tiktok"; out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for slug in slugs:
            data = json.loads((REPO / "tiktok-src" / f"{slug}.json").read_text())
            tmp = pathlib.Path(tempfile.mkdtemp())
            if data["type"] == "meme":
                pg.set_viewport_size({"width": 1080, "height": 1920})
                render_meme(data, slug, tmp, pg, out, preview); shutil.rmtree(tmp); continue
            f = chat_html(data, tmp) if data["type"] == "chat" else make_reels.build_html(data, tmp)
            pg.goto(f.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
            if preview:
                pd = out / "_preview"; pd.mkdir(exist_ok=True)
                if data["type"] == "chat":
                    marks = [data["end"]["at"] - 0.1, data["end"]["at"] + 1.0, 0.5]
                else:
                    marks = [min(sc["end"] - 0.35, sc["start"] + 1.4) for sc in data["scenes"]]
                for i, t in enumerate(marks):
                    pg.evaluate(f"setTime({t})")
                    pg.screenshot(path=str(pd / f"{slug}-{i}.jpg"), type="jpeg", quality=70)
                print("preview", slug); continue
            fd = tmp / "frames"; fd.mkdir()
            for i in range(int(data["duration"] * FPS)):
                pg.evaluate(f"setTime({i / FPS})")
                pg.screenshot(path=str(fd / f"{i:04d}.jpg"), type="jpeg", quality=90)
            wav = tmp / "a.wav"; soundtrack(data, wav, slug)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(fd / "%04d.jpg"),
                            "-i", str(wav), "-c:a", "aac", "-b:a", "192k", "-shortest",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", str(out / f"{slug}.mp4")], check=True)
            shutil.rmtree(tmp)
            print("tiktok", slug)
        b.close()

if __name__ == "__main__":
    a = sys.argv[1:]
    main([x for x in a if not x.startswith("--")], "--preview" in a)
