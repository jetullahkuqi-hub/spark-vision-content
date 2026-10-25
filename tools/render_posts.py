"""Render Instagram feed posts (1080x1440, 3:4) from posts-src/<slug>.html to posts/<slug>.jpg.

Usage:  python3 tools/render_posts.py [slug ...]     (no args = every file in posts-src/)
Templates use {{FONTS_CSS}}, {{LOGO_FULL}}, {{LOGO_MARK}} placeholders.
Also writes posts/_contact-sheet.jpg so the week can be checked at a glance,
and prints a warning when content overflows the 1440px frame.
"""
import pathlib, sys, tempfile
from playwright.sync_api import sync_playwright
from PIL import Image

REPO = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT, BRAND = REPO / "posts-src", REPO / "posts", REPO / "brand"
SUBS = {
    "{{FONTS_CSS}}": (BRAND / "fonts/fonts.css").as_uri(),
    "{{LOGO_FULL}}": (BRAND / "logo-full.png").as_uri(),
    "{{LOGO_MARK}}": (BRAND / "logo-mark.png").as_uri(),
}

def main(slugs):
    OUT.mkdir(exist_ok=True)
    slugs = slugs or sorted(p.stem for p in SRC.glob("*.html"))
    tmp = pathlib.Path(tempfile.mkdtemp())
    done = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1440})
        for s in slugs:
            html = (SRC / f"{s}.html").read_text()
            for k, v in SUBS.items():
                html = html.replace(k, v)
            f = tmp / f"{s}.html"; f.write_text(html)
            pg.goto(f.as_uri()); pg.wait_for_load_state("networkidle")
            pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(250)
            over = pg.evaluate("""() => { const r = document.querySelector('body > div');
                let m = 0; r.querySelectorAll('*').forEach(e => { const b = e.getBoundingClientRect(); if (b.width && b.bottom > m) m = b.bottom; });
                const foot = r.lastElementChild.getBoundingClientRect();
                return {maxBottom: m, footerBottom: foot.bottom, rootH: r.getBoundingClientRect().height}; }""")
            png = tmp / f"{s}.png"
            pg.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": 1080, "height": 1440})
            Image.open(png).convert("RGB").save(OUT / f"{s}.jpg", quality=93, subsampling=0)
            warn = "  <-- CHECK: footer pushed past 1380px (overflow)" if over["footerBottom"] > 1380 else ""
            print(f"{s}: footer bottom {over['footerBottom']:.0f}px{warn}")
            done.append(s)
        b.close()
    # contact sheet
    W, H, cols = 360, 480, 4
    rows = (len(done) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (W + 12), rows * (H + 12)), "white")
    for i, s in enumerate(done):
        sheet.paste(Image.open(OUT / f"{s}.jpg").resize((W, H)), ((i % cols) * (W + 12), (i // cols) * (H + 12)))
    sheet.save(REPO / "_contact-sheet.jpg", quality=80)
    print("contact sheet:", REPO / "_contact-sheet.jpg")

if __name__ == "__main__":
    main(sys.argv[1:])
