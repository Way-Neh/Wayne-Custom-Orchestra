#!/usr/bin/env python3
"""
Wayne Custom Orchestra - Research Intelligence CLI Tool (`research_tools.py`)
Deterministic, dependency-free utility for:
1. Video & Short-Form Multimedia Extraction (yt-dlp & ffmpeg: metadata, subtitles, comments, keyframes)
2. Forum & Discussion Scraping (Reddit JSON, Hacker News Algolia, Telegram public channels)
3. Cross-Lingual Query Matrix Generation (EN, ZH, JA, KO, RU localized search operators)
"""

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"

def safe_run_command(cmd, timeout=60):
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=False
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s: {' '.join(cmd)}"
    except Exception as e:
        return -2, "", str(e)


def clean_vtt_subtitles(vtt_text):
    """Parse WebVTT or SRT content into deduplicated, timestamped text blocks."""
    lines = vtt_text.splitlines()
    cleaned = []
    seen_text = set()
    current_time = ""
    current_text = []

    time_pattern = re.compile(r"(\d{2}:\d{2}(?::\d{2})?(?:\.\d{3})?)\s*-->\s*(\d{2}:\d{2}(?::\d{2})?(?:\.\d{3})?)")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
            continue
        
        match = time_pattern.search(line)
        if match:
            if current_time and current_text:
                full_seg = " ".join(current_text).strip()
                if full_seg and full_seg not in seen_text:
                    seen_text.add(full_seg)
                    cleaned.append(f"[{current_time}] {full_seg}")
            current_time = match.group(1).split(".")[0]
            current_text = []
            continue

        # Strip inline VTT tags like <c> </c> <00:01:02.000>
        text_line = re.sub(r"<[^>]+>", "", line).strip()
        # Decode HTML entities
        text_line = html.unescape(text_line)
        if text_line and text_line not in current_text:
            current_text.append(text_line)

    if current_time and current_text:
        full_seg = " ".join(current_text).strip()
        if full_seg and full_seg not in seen_text:
            cleaned.append(f"[{current_time}] {full_seg}")

    return "\n".join(cleaned)


def extract_video_intel(url, extract_sub=True, extract_comments=True, max_comments=15, extract_frames=False, frames_interval=10, out_dir=None):
    """Extract metadata, subtitles, comments, and optional keyframes from video platforms."""
    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        return {"error": "yt-dlp binary not found in PATH."}

    ffmpeg = shutil.which("ffmpeg")

    result = {
        "url": url,
        "metadata": {},
        "subtitles": {},
        "comments": [],
        "frames": []
    }

    if out_dir:
        out_path = Path(out_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)
    else:
        out_path = Path(tempfile.mkdtemp(prefix="research_video_"))

    # 1. Fetch metadata JSON
    meta_cmd = [yt_dlp, "--dump-single-json", "--no-warnings", "--skip-download", url]
    code, stdout, stderr = safe_run_command(meta_cmd, timeout=45)
    if code != 0:
        return {"error": f"yt-dlp failed to inspect URL: {stderr.strip() or stdout.strip()}"}

    try:
        data = json.loads(stdout)
    except Exception as e:
        return {"error": f"Failed to parse yt-dlp JSON: {e}"}

    result["metadata"] = {
        "id": data.get("id"),
        "title": data.get("title"),
        "uploader": data.get("uploader") or data.get("channel"),
        "uploader_id": data.get("uploader_id"),
        "duration_seconds": data.get("duration"),
        "view_count": data.get("view_count"),
        "like_count": data.get("like_count"),
        "comment_count": data.get("comment_count"),
        "upload_date": data.get("upload_date"),
        "description": data.get("description", "")[:1500],
        "tags": data.get("tags") or [],
        "categories": data.get("categories") or [],
        "webpage_url": data.get("webpage_url") or url
    }

    # 2. Extract Subtitles / Captions
    if extract_sub:
        sub_tmp = out_path / "subs"
        sub_tmp.mkdir(exist_ok=True)
        sub_cmd = [
            yt_dlp,
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs", "en.*,zh.*,ja.*,ko.*,ru.*,es.*",
            "--sub-format", "vtt/srt/best",
            "-o", str(sub_tmp / "%(id)s.%(ext)s"),
            url
        ]
        safe_run_command(sub_cmd, timeout=60)

        # Look for downloaded subtitle files
        for sub_file in sub_tmp.glob("*.*"):
            if sub_file.suffix in [".vtt", ".srt"]:
                lang = sub_file.stem.split(".")[-1]
                try:
                    content = sub_file.read_text(encoding="utf-8", errors="replace")
                    cleaned_transcript = clean_vtt_subtitles(content)
                    if cleaned_transcript.strip():
                        result["subtitles"][lang] = cleaned_transcript
                except Exception as ex:
                    result["subtitles"][lang] = f"Error reading subtitle: {ex}"

    # 3. Extract Top Comments
    if extract_comments:
        comm_cmd = [
            yt_dlp,
            "--skip-download",
            "--get-comments",
            "--dump-json",
            url
        ]
        # Run bounded comment extraction
        try:
            p = subprocess.Popen(comm_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            comments = []
            for line in p.stdout:
                if len(comments) >= max_comments:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    cdata = json.loads(line)
                    comments.append({
                        "author": cdata.get("author"),
                        "text": cdata.get("text"),
                        "like_count": cdata.get("like_count", 0),
                        "timestamp": cdata.get("timestamp")
                    })
                except json.JSONDecodeError:
                    continue
            p.terminate()
            result["comments"] = comments
        except Exception as e:
            result["comments_error"] = str(e)

    # 4. Extract Keyframes via ffmpeg if requested
    if extract_frames and ffmpeg:
        frames_dir = out_path / "keyframes"
        frames_dir.mkdir(exist_ok=True)
        # Download lowest resolution video stream for rapid keyframe sampling
        vid_file = out_path / "low_res.mp4"
        dl_cmd = [
            yt_dlp,
            "-f", "worst[ext=mp4]/worst",
            "-o", str(vid_file),
            "--max-filesize", "30M",
            url
        ]
        dl_code, _, _ = safe_run_command(dl_cmd, timeout=60)
        if dl_code == 0 and vid_file.exists():
            # Sample 1 frame every frames_interval seconds
            ff_cmd = [
                ffmpeg, "-i", str(vid_file),
                "-vf", f"fps=1/{frames_interval}",
                "-q:v", "2",
                str(frames_dir / "frame_%03d.jpg")
            ]
            safe_run_command(ff_cmd, timeout=45)
            frame_files = sorted(list(frames_dir.glob("*.jpg")))
            result["frames"] = [str(f) for f in frame_files]

    return result


def fetch_reddit(query_or_url, limit=10):
    """Query Reddit public JSON for discussions or comments."""
    is_url = query_or_url.startswith("http://") or query_or_url.startswith("https://")
    if is_url:
        json_url = query_or_url.rstrip("/") + ".json"
    else:
        encoded_q = urllib.parse.quote(query_or_url)
        json_url = f"https://www.reddit.com/search.json?q={encoded_q}&sort=relevance&limit={limit}"

    req = urllib.request.Request(
        json_url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {
            "error": f"Failed to fetch Reddit JSON directly: {e}",
            "guidance": "Reddit frequently blocks automated datacenter IPs with 403. Use `search_web` with `site:reddit.com \"<query>\"` to mine Reddit discussions and comment consensus."
        }

    results = []
    # If search endpoint
    if isinstance(data, dict) and "data" in data and "children" in data["data"]:
        for child in data["data"]["children"]:
            item = child.get("data", {})
            results.append({
                "title": item.get("title"),
                "subreddit": item.get("subreddit"),
                "author": item.get("author"),
                "score": item.get("score"),
                "num_comments": item.get("num_comments"),
                "url": f"https://reddit.com{item.get('permalink')}",
                "selftext": (item.get("selftext") or "")[:800]
            })
    # If thread endpoint (returns list [listing_post, listing_comments])
    elif isinstance(data, list) and len(data) >= 1:
        post_data = data[0]["data"]["children"][0]["data"]
        comments = []
        if len(data) > 1 and "children" in data[1]["data"]:
            for c in data[1]["data"]["children"][:limit]:
                cd = c.get("data", {})
                if cd.get("body"):
                    comments.append({
                        "author": cd.get("author"),
                        "score": cd.get("score"),
                        "body": cd.get("body")[:600]
                    })
        return {
            "title": post_data.get("title"),
            "subreddit": post_data.get("subreddit"),
            "author": post_data.get("author"),
            "score": post_data.get("score"),
            "selftext": post_data.get("selftext"),
            "comments": comments
        }

    return {"results": results}


def fetch_hacker_news(query, limit=10):
    """Query Hacker News via Algolia API."""
    encoded_q = urllib.parse.quote(query)
    api_url = f"https://hn.algolia.com/api/v1/search?query={encoded_q}&tags=story&hitsPerPage={limit}"

    req = urllib.request.Request(
        api_url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"error": f"Failed to fetch HN Algolia API: {e}"}

    hits = data.get("hits", [])
    results = []
    for hit in hits:
        results.append({
            "title": hit.get("title"),
            "author": hit.get("author"),
            "points": hit.get("points"),
            "num_comments": hit.get("num_comments"),
            "created_at": hit.get("created_at"),
            "story_url": hit.get("url"),
            "hn_discussion": f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        })
    return {"results": results}


def fetch_telegram_channel(channel_name, limit=10):
    """Parse public Telegram channel previews from t.me/s/<channel>."""
    clean_channel = channel_name.lstrip("@").split("/")[-1]
    url = f"https://t.me/s/{clean_channel}"

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html_text = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return {"error": f"Failed to fetch Telegram preview: {e}"}

    # Extract messages using regex on HTML tags
    msg_blocks = re.findall(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', html_text, re.DOTALL)
    views = re.findall(r'<span class="tgme_widget_message_views">([^<]+)</span>', html_text)
    dates = re.findall(r'<time datetime="([^"]+)"', html_text)

    posts = []
    for i, msg in enumerate(reversed(msg_blocks[-limit:])):
        clean_text = re.sub(r'<[^>]+>', ' ', msg).strip()
        clean_text = html.unescape(clean_text)
        view_cnt = views[-(i+1)] if (i+1) <= len(views) else "N/A"
        date_str = dates[-(i+1)] if (i+1) <= len(dates) else "N/A"
        posts.append({
            "date": date_str,
            "views": view_cnt,
            "text": clean_text[:800]
        })

    return {
        "channel": clean_channel,
        "url": url,
        "posts": posts
    }


def generate_query_matrix(concept):
    """Generate localized query operators for major platforms and languages."""
    matrix = {
        "concept": concept,
        "languages": {
            "en": {
                "general_web": f'"{concept}" review OR benchmark OR architecture',
                "reddit": f'site:reddit.com "{concept}" (experience OR issue OR benchmark)',
                "hacker_news": f'site:news.ycombinator.com "{concept}"',
                "youtube_shorts": f'{concept} #shorts review breakdown',
                "twitter_x": f'"{concept}" (min_faves:50 lang:en)'
            },
            "zh-Hans": {
                "bilibili": f'{concept} 深度解析 OR 实测 OR 踩坑',
                "xiaohongshu": f'{concept} 真实体验 OR 避坑指南 OR 评测',
                "zhihu": f'site:zhihu.com "{concept}" (架构 OR 源码 OR 优缺点)',
                "v2ex": f'site:v2ex.com/t "{concept}"',
                "douyin": f'{concept} 核心原理 OR 对比评测'
            },
            "ja": {
                "qiita_zenn": f'site:qiita.com OR site:zenn.dev "{concept}" (使ってみた OR 比較)',
                "2ch_5ch": f'site:5ch.net "{concept}" (評判 OR 不具合)',
                "note_jp": f'site:note.com "{concept}" (レビュー OR メリット)'
            },
            "ru": {
                "habr": f'site:habr.com "{concept}" (обзор OR архитектура OR опыт)',
                "telegram": f'site:t.me "{concept}"',
                "vk": f'site:vk.com "{concept}"'
            },
            "ko": {
                "dcinside_naver": f'"{concept}" 후기 OR 실사용 OR 장단점'
            }
        }
    }
    return matrix


def main():
    parser = argparse.ArgumentParser(description="Wayne Swarm Research Tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Video extraction
    p_video = subparsers.add_parser("video", help="Extract video metadata, subtitles, comments, and keyframes")
    p_video.add_argument("url", help="URL of video (YouTube/Shorts, TikTok, Reels, Bilibili, Douyin)")
    p_video.add_argument("--no-sub", action="store_true", help="Skip subtitle extraction")
    p_video.add_argument("--no-comments", action="store_true", help="Skip comments extraction")
    p_video.add_argument("--max-comments", type=int, default=15, help="Max comments to fetch (default 15)")
    p_video.add_argument("--frames", action="store_true", help="Sample visual keyframes using ffmpeg")
    p_video.add_argument("--interval", type=int, default=10, help="Seconds between keyframes (default 10s)")
    p_video.add_argument("--out-dir", type=str, default=None, help="Directory to save artifacts and keyframes")

    # Forum extraction
    p_forum = subparsers.add_parser("forum", help="Extract discussions from Reddit, Hacker News, or Telegram")
    p_forum.add_argument("platform", choices=["reddit", "hn", "telegram"], help="Forum platform")
    p_forum.add_argument("target", help="Query or URL / Channel")
    p_forum.add_argument("--limit", type=int, default=10, help="Max results")

    # Query matrix
    p_matrix = subparsers.add_parser("matrix", help="Generate multilingual search query matrix")
    p_matrix.add_argument("concept", help="Subject or concept to localize")

    args = parser.parse_args()

    if args.command == "video":
        data = extract_video_intel(
            args.url,
            extract_sub=not args.no_sub,
            extract_comments=not args.no_comments,
            max_comments=args.max_comments,
            extract_frames=args.frames,
            frames_interval=args.interval,
            out_dir=args.out_dir
        )
        print(json.dumps(data, indent=2, ensure_ascii=False))

    elif args.command == "forum":
        if args.platform == "reddit":
            data = fetch_reddit(args.target, limit=args.limit)
        elif args.platform == "hn":
            data = fetch_hacker_news(args.target, limit=args.limit)
        elif args.platform == "telegram":
            data = fetch_telegram_channel(args.target, limit=args.limit)
        print(json.dumps(data, indent=2, ensure_ascii=False))

    elif args.command == "matrix":
        data = generate_query_matrix(args.concept)
        print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
