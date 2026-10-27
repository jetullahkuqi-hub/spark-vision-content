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

def main(slugs, preview):
    slugs = slugs or sorted(p.stem for p in (REPO / "tiktok-src").glob("*.json"))
    out = REPO / "tiktok"; out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for slug in slugs:
            data = json.loads((REPO / "tiktok-src" / f"{slug}.json").read_text())
            tmp = pathlib.Path(tempfile.mkdtemp())
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
