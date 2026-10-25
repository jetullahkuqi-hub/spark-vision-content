# Weekly playbook – running @spark_visionn on autopilot

The owner (Jetullah, writes in Albanian) asked Claude to run the Spark Vision Instagram fully:
make the posts and videos, upload and schedule them itself, **keep changing the strategy and follow what works.**
Read `BRAND.md` and `STRATEGY.md` before doing anything.

## Fixed facts
- Metricool brand id / blogId: **7653072** · timezone **Europe/Belgrade** · network `instagram` (account spark_visionn).
- Public media URL for any file in this repo: `https://raw.githubusercontent.com/jetullahkuqi-hub/spark-vision-content/main/<path>`
  (Metricool copies the file at scheduling time, so the file must be pushed **before** scheduling).
- Cadence set by the owner: **3 per day, every day: feed post, feed post, then a Reel** ("after every two posts, a video").
  Default times 10:00 / 13:00 / 18:00 — times may move if the data shows better slots, but keep the post-post-Reel order.
- Posts publish automatically (`autoPublish: true`, `draft: false`). The owner approved this.

## Each weekly run
1. **Set up.** Clone the repo (see the scheduled task prompt), then
   `pip install --break-system-packages playwright numpy pillow >/dev/null` only if imports fail (Chromium, Playwright and ffmpeg are usually preinstalled).
2. **Find the gap.** `getScheduledPosts` for today → +14 days. The new week starts the day after the last scheduled post
   (never double-book a slot). Plan 7 days = 14 feed posts + 7 Reels.
3. **Measure what worked.** Use Metricool analytics for every published post since the last run:
   - `getAnalyticsAvailableMetrics` (network `instagram`, connectors `posts` and `reels`) to see metric ids,
     then `getAnalyticsDataByMetrics` for the period. Pull per-post reach, impressions/views, likes, comments, saves, shares,
     and account-level followers gained.
   - Join each post with `weeks/*.json` (path, pillar, topic, hook) and rank by reach and by
     engagement rate = (likes+comments+saves+shares)/reach. Compare: Reels vs posts, pillar vs pillar, hook style, time slot.
   - Also call `getBestTimeToPostByNetwork` for the coming week.
   - If there is too little data (few posts, tiny numbers), say so honestly and lean on best practice — don't over-read noise.
4. **Change the strategy.** Write a new section at the top of `STRATEGY.md`: the numbers that mattered (top 3 / bottom 3),
   what to do more of, what to drop, and **one or two clear experiments** for the coming week
   (new format, hook style, topic series, time slot, CTA, carousel…). Rough split: ~70 % what is proven, ~30 % experiments.
   Never repeat a topic already used in `weeks/*.json` word-for-word; evolve winning themes into new angles instead.
5. **Make the feed posts.** For each new post, copy the closest `posts-src/*.html` template to `posts-src/<new-slug>.html`
   and rewrite text/layout (keep header, footer, colours, fonts from `BRAND.md`; vary layouts so the grid doesn't look repetitive).
   Carousels: make `<slug>-1.html`, `<slug>-2.html`… and send all image URLs in one post's `media` list.
   Render with `python3 tools/render_posts.py <slugs…>`; open `_contact-sheet.jpg` with the Read tool and fix any
   overflow, clipped or awkward text before moving on (the script warns when the footer is pushed down).
6. **Make the Reels.** Write `reels-src/<slug>.json` (format documented at the top of `tools/make_reels.py`),
   check with `python3 tools/make_reels.py <slug> --preview` and look at `reels/_preview/`, then render without `--preview`.
   First scene must start at 0.0 with the hook. 10–15 s. Give each Reel a different `music_seed`.
7. **Write the plan file** `weeks/<monday-or-first-day>.json`: list of
   `{"date":"YYYY-MM-DDTHH:MM:SS","type":"POST"|"REEL","path":"posts/x.jpg","pillar":"…","hook":"…","text":"caption"}`.
   Captions in English: hook line, 2–5 short lines of value, one CTA (save / share / comment / DM), 5–8 hashtags incl. #sparkvision.
8. **Publish the files.** `git add -A && git commit -m "Week of <date>: …" && git fetch origin main && git rebase origin/main && git push`.
   If the push fails, stop and report — do not schedule posts whose media is not online.
9. **Schedule.** One `createScheduledPost` per item, `blogId` 7653072, `date` with `+01:00` (or `+02:00` in summer time):
   ```json
   {"autoPublish": true, "descendants": [], "draft": false, "firstCommentText": "", "hasNotReadNotes": false,
    "media": ["https://raw.githubusercontent.com/jetullahkuqi-hub/spark-vision-content/main/posts/<slug>.jpg"],
    "mediaAltText": ["Spark Vision post: <headline>"], "providers": [{"network": "instagram"}],
    "publicationDate": {"dateTime": "2026-11-02T10:00:00", "timezone": "Europe/Belgrade"},
    "shortener": false, "smartLinkData": {"ids": []}, "text": "<caption>",
    "instagramData": {"type": "POST", "collaborators": [], "showReelOnFeed": true}}
   ```
   Reels: media = the `.mp4`, `"mediaAltText": []`, `"instagramData": {"type": "REEL", …}`, plus `"videoCoverMilliseconds": 1000`.
   Afterwards run `getScheduledPosts` again and confirm every slot of the new week is there exactly once.
10. **Report to the owner in Albanian** (short): what worked last week (with the real numbers), what changes this week and why,
    and the new schedule. If anything failed, say exactly what and what he needs to do.

## Don'ts
- Don't delete or edit posts that are already published. Don't touch other Metricool brands.
- No prices, invented stats, fake testimonials or client names; no copyrighted music or characters.
- Don't change the cadence rule or language without the owner asking.
