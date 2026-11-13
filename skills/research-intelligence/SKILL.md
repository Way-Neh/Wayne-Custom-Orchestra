---
name: research-intelligence
description: Autonomous deep research methodology across multilingual mediums (English, Chinese, Japanese, Korean, Russian), community forums (Reddit, Hacker News, Telegram, niche boards), social media (X/Twitter, Xiaohongshu), and short-form video (TikTok, YouTube Shorts, Reels, Bilibili) with deep multimodal extraction.
---

# Research Intelligence Skill (`research-intelligence`)

Comprehensive methodology and execution guide for high-signal autonomous research across multilingual platforms, community forums, social networks, and short-form video.

---

## 1. Cross-Lingual & Native Query Localization

Emerging technical practices, supply-chain dynamics, consumer feedback, and AI model developments frequently appear first outside the English-speaking web. Never rely on literal Google Translate strings. Use platform-native terminology:

### 🇨🇳 Chinese Ecosystem (Bilibili, Xiaohongshu/RED, Zhihu, V2EX, Douyin)
- **Architecture & Code Deep Dive**: `架构设计`, `源码剖析`, `底层原理`, `实战分享`, `性能优化`
- **Real-World Experience & Post-Mortems**: `实测`, `真实体验`, `踩坑指南`, `避坑`, `翻车记录`, `深度评测`
- **Search Operators**:
  - `site:zhihu.com "<concept>" (架构 OR 源码 OR 优缺点)`
  - `site:v2ex.com/t "<concept>"`
  - `python3 /home/wayne/.gemini/config/plugins/wayne-custom-orchestra/scripts/research_tools.py matrix "<concept>"`

### 🇯🇵 Japanese Ecosystem (Qiita, Zenn, Note.com, 5ch)
- **Hands-on Trials**: `使ってみた`, `触ってみた`, `やってみた`
- **Comparisons & Trade-Offs**: `比較`, `メリット・デメリット`, `所感`, `評判`, `不具合`
- **Search Operators**:
  - `site:qiita.com OR site:zenn.dev "<concept>" (使ってみた OR 比較)`
  - `site:5ch.net "<concept>" (評判 OR バグ)`

### 🇷🇺 Russian & Eastern European Tech (Habr, Telegram, VK)
- **Deep Technical Articles**: `разбор`, `архитектура`, `опыт внедрения`, `бенчмарк`
- **Practical Caveats**: `грабли`, `подводные камни`, `проблемы`, `сравнение`
- **Search Operators**:
  - `site:habr.com "<concept>" (обзор OR опыт OR грабли)`
  - `site:t.me "<concept>"`

---

## 2. Forum & Discussion Scraping

Forums capture the authentic, unfiltered practitioner perspective:

### Hacker News (Algolia API)
```bash
# Query stories or discussions
python3 /home/wayne/.gemini/config/plugins/wayne-custom-orchestra/scripts/research_tools.py forum hn "<query>" --limit 10
```
- Focus on Ask HN threads, launch feedback, and comments with high points.

### Reddit (Public JSON)
```bash
# Search across subreddits
python3 /home/wayne/.gemini/config/plugins/wayne-custom-orchestra/scripts/research_tools.py forum reddit "<query>" --limit 10

# Ingest specific thread and comments
python3 /home/wayne/.gemini/config/plugins/wayne-custom-orchestra/scripts/research_tools.py forum reddit "https://www.reddit.com/r/reactjs/comments/..."
```
- Pay attention to upvote ratios. If a post is 60% upvoted, the top comments typically contain the decisive counter-arguments.

### Telegram Channels
```bash
# Parse public channel feed
python3 /home/wayne/.gemini/config/plugins/wayne-custom-orchestra/scripts/research_tools.py forum telegram "<channel_name>" --limit 15
```

---

## 3. Short-Form Video & Multimedia Ingestion

Short-form videos (TikTok, Shorts, Reels, Douyin) compress high-density tutorials, benchmark setups, and product demonstrations into 30–90 seconds. To extract technical value:

```bash
# 1. Fast extraction (Subtitles + Metadata + Top 15 Comments)
python3 /home/wayne/.gemini/config/plugins/wayne-custom-orchestra/scripts/research_tools.py video "<url>"

# 2. Deep Multimodal (Subtitles + Comments + Keyframes via ffmpeg)
python3 /home/wayne/.gemini/config/plugins/wayne-custom-orchestra/scripts/research_tools.py video "<url>" --frames --interval 5 --out-dir "/tmp/video_intel"
```

### Multimodal Synthesis Protocol:
1. **Timestamped Spoken Narrative**: Review subtitle timestamps to pinpoint when key concepts are explained.
2. **Keyframe Visual Verification**: If the speaker shows terminal code, benchmark charts, or architectural blocks, inspect the sampled frames in the output directory.
3. **Community Validation (Comments)**: Always check top comments. Practitioners often post: "Note: in v2.0 this flag changed to..." or "This benchmark is flawed because...".

---

## 4. Machine Blackboard Contract: `research_dossier.md`

All findings must be formatted into `.agents/blackboard/research_dossier.md` with numbered tags:
- `[RES-META]`: Research scope, primary languages probed, platforms targeted.
- `[RES-QUERY-MATRIX]`: Exact localized search queries used.
- `[RES-FINDINGS]`: Synthesized insights (`[RES-01]`, `[RES-02]`).
- `[RES-SOURCES]`: Complete provenance table.
- `[RES-MULTIMEDIA-EXTRACTS]`: Video subtitles, comments, visual frame notes.
- `[RES-IMPACT-RECOMMENDATIONS]`: Concrete recommendations for PM spec & architecture schema.
