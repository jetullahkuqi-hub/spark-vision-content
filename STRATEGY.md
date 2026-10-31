# Spark Vision – strategy log

Newest week on top. Each weekly run adds: what the data said, what changes, and the experiment for the coming week.
Rule from the owner: **keep changing the strategy and follow what works.**

---

## Run of Sat 31 Oct 2026 · review of week 1 — ⚠️ PUBLISHING BLOCKED

**Blocker:** since **Thu 29 Oct 07:00** every scheduled post (Instagram and TikTok) has failed in Metricool with
`"You have reached your Metricool account limit."` The last posts that went out were on 28 Oct. This run made **no new content and
scheduled nothing**, because new posts would fail the same way. The owner has to raise or reset the Metricool plan limit first.
Next run: check `getScheduledPosts` statuses for `ERROR` *before* producing anything. Keep the volume (3 IG + 10 TikTok per day = 91/week)
inside the plan's limit.

**Instagram, 26–28 Oct (6 feed posts + 3 of our Reels published). Followers flat at ~379.**
| Rank | Post | Type | Reach | Views | Likes | Saves | Shares |
|---|---|---|---|---|---|---|---|
| owner's own | golden eagle product reel (25 Oct) | Reel | 3094 | 5059 | 86 | 2 | 17 |
| owner's own | gk_electric website showcase (25 Oct) | Reel | 743 | 936 | 6 | 0 | 2 |
| 1 | likes-dont-pay-bills | Reel | 660 | 898 | 8 | 0 | 2 |
| 2 | every-move | Post | 450 | 581 | 4 | 1 | 0 |
| 3 | stop-posting-start-planning | Reel | 47 | 82 | 3 | 0 | 0 |
| … | growing-brands 41 · three-signs 29 · noise 26 · consistency 22 | Post | | | | | |
| bottom | what-we-do-in-10-seconds 36 · be-chosen 21 | Reel/Post | | | | | |
Average watch time on our Reels: 1.2–3.5 s (the owner's product reel: 4.7 s).

**TikTok, 28 Oct (10 of our videos + 2 of the owner's own).**
- Ours: 1–11 views each. Best: "just make it go viral" chat skit (11 views), "every designer has received this text" (7), "algorithm trust issues" (6).
  Worst: "never small, never before tomorrow" (1) and the IG cross-post "logo isn't your brand" (1).
- The owner's own: "Custom 3D scroll website" 34 views / 16 shares; "final_FINAL_v7" 24 views / 15 shares.
- Metricool shows TikTok followers 158 → 6 on 29 Oct; this is probably a data error. Check it in the TikTok app.

**What the data says (small sample, read with care):**
1. **Real work beats designed text.** The owner's real project content (product reel, website showcase) reached 1–5× more than our best item.
   That is the clearest signal so far.
2. One hot-take Reel ("Likes don't pay bills") and the chess post ("Every move has a purpose") clearly beat the other 7 items. Short, bold
   statements with a chess/strategy feel worked best; tip lists and service posts got the lowest reach (this supports hypothesis 3).
3. TikTok: a brand-new account posting 10 a day got 1–11 views per video. Too early to rank memes vs. chat vs. text.
   The educational IG cross-post did worst.

**Plan for when publishing works again:**
- Do more of: hot-take statements (≈40% of Reels), the chess metaphor, real-work showcases.
- Do less of: pure service posts (at most 1 every 2 days) and plain tip lists without a strong hook.
- **IG experiment 1:** "Behind the build" Reels using the owner's real project clips (with the clients' permission; no invented results).
  We need raw clips from the owner in `owner-clips/`.
- **IG experiment 2:** first carousel (3–5 slides, "myth vs fact") to test saves.
- **TikTok experiment:** POV/chat skits about building websites and products (the owner's 3D-website video won on TikTok), plus a
  question as the on-screen hook. Stop cross-posting educational IG Reels to TikTok; cross-post only funny ones.
- Best-time data was not re-checked this run, because nothing could be scheduled.

---

## Week 1 · Mon 26 Oct – Sat 31 Oct 2026 (baseline)

**Starting point:** 379 followers, few posts, no performance history in Metricool yet (brand connected 25 Oct).

**Cadence (owner's rule):** 3 per day — 10:00 feed post, 13:00 feed post, 18:00 Reel ("after every two posts, a video").
Times come from Metricool best-time data (weekday peak 10:00; second bump 17:00–18:00).

**Mix this week (12 posts + 6 Reels):**
| Pillar | Posts | Reels |
|---|---|---|
| Education / tips (save-worthy) | three-signs, consistency, stop-the-scroll, before-you-post | before-you-post-ask |
| Point of view / hot take (shareable) | every-move, noise, be-chosen, logo-not-brand | stop-posting-start-planning, likes-dont-pay-bills, logo-isnt-your-brand |
| Offer / services (conversion) | growing-brands, what-we-do, next-move | what-we-do-in-10-seconds, ready-for-your-next-move |
| Values / trust | focus-consistency-results | – |

**Formats:** single-image posts only; Reels are 12–13 s kinetic-text with generated music.

**Hypotheses to test from week 2:**
1. Reels will out-reach feed posts by a wide margin (non-follower reach).
2. Tip/checklist posts will get the most saves; hot takes the most shares.
3. Pure service posts will get the lowest reach.

**TikTok (added 27 Oct):** owner wants separate, funny videos on TikTok. Prepared 7 videos (4 chat-format, 3 kinetic-text),
1 per day at 19:00, waiting for TikTok to be connected in Metricool. Plan: `weeks/tiktok-2026-10-27.json`.
Hypothesis: chat-format skits (client DMs) will beat kinetic-text jokes on watch time.
Update 27 Oct: added 8 reaction memes (Mixkit free-license clips + caption). First 15 TikToks alternate meme / skit, **5 per day** (owner's request)
at 08:00 / 12:00 / 16:00 / 19:00 / 21:00 (`weeks/tiktok-2026-10-28.json`). Test: memes vs chat skits vs kinetic text — keep the format with best watch time and shares.

**TikTok went live 28 Oct 00:40** (connected in Metricool). Owner raised the cadence to **10 videos per day**.
Scheduled 34 videos through Sat 31 Oct 11:30 (memes, chat skits, kinetic text, 2 IG Reels). 16 stock clips in use.

**Cross-posting (added 28 Oct, owner's request):** mix content between networks. This week: IG Reels on Thu 29 and Sat 31 at 18:00
swapped for TikTok memes (needs-more-pop, just-post-something); two IG Reels (logo-isnt-your-brand, ready-for-your-next-move) added to the TikTok plan.
Question to answer: does humour grow the Instagram audience, and does the educational style work on TikTok?

**Ideas queued for later weeks:** carousels (multi-slide tips), "myth vs fact" series, before/after feed audits (generic, no real client names), Reels with a question hook, polls/questions in captions, posting-time test (e.g. 12:00 / 19:00).
