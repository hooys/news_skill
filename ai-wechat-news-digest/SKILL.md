---
name: ai-wechat-news-digest
description: Digest recent AI news from Chinese WeChat-adjacent sources using stable official sites first and best-effort WeChat/sync pages second.
metadata:
  openclaw:
    always: true
    emoji: "📰"
    user-invocable: true
    homepage: "https://github.com/hooys/news_skill/tree/main/ai-wechat-news-digest"
---

# AI WeChat News Digest

## Overview

Produce a concise news-style digest of recent AI articles from authoritative Chinese WeChat-adjacent public accounts and media sources. By default, collect the three most recent publicly verifiable articles for each account/source. Keep the source method explicit: WeChat history pages are often not publicly crawlable, so public official sites, content hubs, mirrored pages, and reputable aggregators may be used when they clearly correspond to the same account or article.

This is a workflow skill, not a standalone crawler. It does not install or run a private WeChat scraper. It relies on whatever web search, web fetch, browser, RSS, or user-provided URL tools are available in the host agent.

## Platform Compatibility

This skill is compatible with Codex and OpenClaw as an instruction-only skill.

For OpenClaw:

- Install the skill directory itself, not the multi-skill repository root. The `hooys/news_skill` repository contains multiple skills, while OpenClaw Git installs generally expect a `SKILL.md` at the source root.
- Local install example: `openclaw skills install ./ai-wechat-news-digest --as ai-wechat-news-digest`.
- Workspace placement example: copy this folder to `<workspace>/skills/ai-wechat-news-digest/`.
- Global placement example: copy this folder to `~/.openclaw/skills/ai-wechat-news-digest/`.
- Start a new OpenClaw session or refresh skills after installing, because skill snapshots may be reused during a session.

If OpenClaw has no working web search, browser, or fetch capability, use only direct URLs supplied by the user and report that source discovery is unavailable. Do not pretend to have checked latest articles.

## Default Source Set

Start with this source range unless the user changes it:

- 中国信通院CAICT
- 中国人工智能学会
- 智源社区 / 智源研究院
- 机器之心 / 机器之心Pro
- 量子位
- DeepTech深科技
- 新智元
- AI科技评论
- InfoQ / AI前线
- Datawhale
- 智东西

Treat this as an extensible list. Add adjacent high-authority AI sources when the user asks to expand the range, but keep the final output clear about which accounts were actually checked.

## Source Tiers

Use stable official non-WeChat sources first:

- 中国信通院CAICT: official CAICT website and report/news pages.
- 中国人工智能学会: official CAAI website.
- 智源社区 / 智源研究院: BAAI Hub and official site pages.
- 机器之心 / 机器之心Pro: `jiqizhixin.com` and official Pro pages.
- 量子位: `qbitai.com`.
- AI科技评论: 雷峰网 AI科技评论 author/channel pages.
- InfoQ / AI前线: InfoQ Chinese AI channel and InfoQ AI/ML/Data Engineering pages.
- 智东西: `zhidx.com`.

Treat these as best-effort sources, not stable default crawlers:

- DeepTech深科技: use MIT Technology Review China pages, Sohu/Sina/other reputable sync pages, or user-provided URLs. Do not assume a stable official article list.
- 新智元: use Sohu, 36Kr, 智源社区 sync pages, or user-provided URLs when the official article list is not available.
- Datawhale: use Datawhale official site, GitHub projects, docs, or community posts. Treat it as a learning/community source rather than a daily news site.

WeChat-specific behavior:

- Direct `mp.weixin.qq.com` article URLs may be parsed if publicly accessible.
- Public WeChat history/profile pages are often blocked by 403, login requirements, anti-bot checks, expiring parameters, or unavailable cookies. Do not make them the default discovery path.
- If WeChat access fails, say so and continue with stable non-WeChat sources.

## Retrieval Rules

Always browse or otherwise verify live results; do not rely on memory for latest-article requests.

Before searching, identify the available host capabilities:

- If web search is available, use it to discover recent articles.
- If only web fetch/browser is available, start from stable official source pages and user-provided URLs.
- If neither search nor fetch/browser is available, ask the user for URLs or say latest article discovery is blocked.
- If RSS/API tools are available for a source, prefer them over search-result scraping.

Prefer sources in this order:

1. `mp.weixin.qq.com` article pages from the official account.
2. The account's official website or official content hub.
3. Public sync pages from the same organization or account.
4. Reputable repost/aggregation pages that preserve title, source account, and publication time.

Use search queries that combine account name, "latest" intent, date hints, and likely domain, for example:

- `site:mp.weixin.qq.com 量子位 微信公众号 最新 AI`
- `机器之心 微信公众号 最新 3篇`
- `site:qbitai.com 量子位 最新 AI`
- `site:hub.baai.ac.cn/view 智源社区 最新`
- `site:caict.ac.cn 中国信通院 人工智能 最新`

In OpenClaw environments where SearXNG or another search provider is missing, do not mark the whole skill as failed. Degrade to stable source pages and direct URLs; list sources that could not be checked.

For each candidate article, verify as many of these as possible:

- publication time or clear relative time
- source account or publisher
- title match across sources when using a repost
- article content is actually about AI, AI infrastructure, models, robotics, data, chips, developer tooling, or AI policy

For best-effort sources, require stronger evidence before including an item: title match, source attribution, publication time, and a reputable host. If these are missing, label the item `待复核` or omit it.

If the user gives a relative time window, anchor it to the current date and timezone from the environment. For "past 12 hours", include only articles whose publication time can reasonably fit that window. If time is ambiguous, label it as "待复核" instead of treating it as confirmed.

When the user does not specify a time window, do not impose one. For each account, find up to three newest articles that can be publicly verified. If fewer than three are verifiable, include the available items and state the gap for that account.

## Source Labels

Label source type when it matters:

- `微信原文`: a direct `mp.weixin.qq.com` article.
- `官网同步`: the account or organization's own site.
- `内容社区`: official or semi-official content hubs such as 智源社区.
- `第三方转载`: reputable reposts such as Sina, Sohu, 51CTO, or similar pages.
- `聚合线索`: aggregator/search result only; use sparingly and mark as not fully verified.
- `不可用`: source discovery failed because the required web/search/fetch capability was unavailable or the source blocked access.

Do not claim that an item came from the official WeChat article list unless it was actually obtained from a public WeChat page or official account list. It is acceptable to say the method retains the previous broader source approach: public web verification rather than strict WeChat-history extraction.

## Failure Handling

Use explicit, non-misleading fallback language:

- If a source blocks access: `该源公开抓取受限，本次未能核验近期 3 篇。`
- If only one or two items are verified: include those items and state `仅公开核验到 N 篇。`
- If search is unavailable: `当前环境缺少 web search，无法做全网发现；仅检查可直接访问的官网/URL。`
- If WeChat returns 403: `微信公众号历史页 403，未作为有效来源。`

Never fill gaps with stale, unrelated, or unverified articles just to reach three items.

## Digest Format

Default to a line-by-line list grouped by account, not a table, unless the user asks for a table. Include up to three articles under each account.

For each article, include:

- account name as a bold group heading
- article title as a Markdown link
- publication time
- source type if not a direct WeChat original
- 1-3 sentence news-style summary

Example:

- **量子位**
  - [文章标题一](https://example.com)  
    2026-06-30 16:46，官网同步。用 1-3 句概括新闻事实、主体、动作、影响或技术重点。
  - [文章标题二](https://example.com)  
    2026-06-30 12:10，微信原文。用 1-3 句概括新闻事实、主体、动作、影响或技术重点。

End with a short note listing accounts where fewer than three recent articles were publicly verifiable, if any.

## Quality Bar

Prioritize accuracy over exhaustiveness. Do not fill gaps with unrelated or stale articles just to reach three items. If the user specified a time window and a source's newest item is outside that window, say so. If the only available link is a repost, disclose that. Avoid overclaiming official status when the retrieval path was public web search.
