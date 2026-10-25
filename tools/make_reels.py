"""Render animated kinetic-text Reels (1080x1920, 30fps, H.264 + AAC) from reels-src/<slug>.json.

Usage:  python3 tools/make_reels.py [slug ...] [--preview]
  --preview  only writes one still per scene to reels/_preview/ (fast check of text fit)

Scene JSON format (see existing files in reels-src/ for examples):
{
  "tag": "STRATEGY",                # pill in the top-right corner
  "duration": 12.0,                 # seconds
  "music_seed": 3,                  # optional, varies the generated soundtrack
  "scenes": [
    {"start": 0.0, "end": 3.0, "lines": [
        {"t": "MARKETING TIP", "cls": "kick"},       # small spaced label
        {"t": "Stop", "size": 190},                   # big condensed headline line
        {"t": "Start [[planning.]]", "size": 130}     # [[...]] = blue accent; keep [[ ]] inside ONE line
    ]},
    {"start": 9.0, "end": 12.0, "center": true, "lines": [
        {"logo": true}, {"t": "Strategy that delivers.", "cls": "sub"}, {"pill": "SEND US A DM"}]}
  ]
}
Rules: the first scene must start at 0.0 (it is visible on frame 1 = the hook / cover).
Keep each line under ~12 characters at size 150 (text area is 900px wide).
"""
import json, pathlib, subprocess, sys, shutil, tempfile
from playwright.sync_api import sync_playwright

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import music  # noqa: E402

FPS = 30
BRAND = REPO / "brand"

def build_html(data, tmp):
    tpl = (REPO / "tools/reel_template.html").read_text()
    full = (BRAND / "logo-full.png").as_uri()
    html = (tpl.replace("FONTS_CSS", (BRAND / "fonts/fonts.css").as_uri())
            .replace("TAGTEXT", data["tag"])
            .replace('src="LOGOFULL"', f'src="{full}"')
            .replace("LOGOFULLSRC", json.dumps(full))
            .replace('"LOGOMARK"', json.dumps((BRAND / "logo-mark.png").as_uri()))
            .replace("__DATA__", json.dumps(data)))
    f = tmp / "reel.html"; f.write_text(html); return f

def main(slugs, preview):
    slugs = slugs or sorted(p.stem for p in (REPO / "reels-src").glob("*.json"))
    out = REPO / "reels"; out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for slug in slugs:
            data = json.loads((REPO / "reels-src" / f"{slug}.json").read_text())
            tmp = pathlib.Path(tempfile.mkdtemp())
            f = build_html(data, tmp)
            pg.goto(f.as_uri()); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
            if preview:
                pd = out / "_preview"; pd.mkdir(exist_ok=True)
                for i, sc in enumerate(data["scenes"]):
                    pg.evaluate(f"setTime({min(sc['end'] - 0.35, sc['start'] + 1.4)})")
                    pg.screenshot(path=str(pd / f"{slug}-{i}.jpg"), type="jpeg", quality=70)
                print("preview", slug); continue
            fd = tmp / "frames"; fd.mkdir()
            for i in range(int(data["duration"] * FPS)):
                pg.evaluate(f"setTime({i / FPS})")
                pg.screenshot(path=str(fd / f"{i:04d}.jpg"), type="jpeg", quality=92)
            wav = tmp / "music.wav"
            music.write(wav, data["duration"], data.get("music_seed", hash(slug) % 97))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(fd / "%04d.jpg"),
                            "-i", str(wav), "-c:a", "aac", "-b:a", "192k", "-shortest",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", str(out / f"{slug}.mp4")], check=True)
            shutil.rmtree(tmp)
            print("reel", slug)
        b.close()

if __name__ == "__main__":
    a = sys.argv[1:]
    main([x for x in a if not x.startswith("--")], "--preview" in a)
