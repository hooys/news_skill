---
name: ai-wechat-news-digest
description: Collect and summarize the three most recent publicly verifiable articles from each authoritative Chinese AI WeChat public account, using official WeChat article pages when available and otherwise using each account's official site, public sync pages, or reputable repost/aggregation pages for verification. Use when the user asks for AI WeChat news digests, latest articles from accounts such as 中国信通院CAICT, 中国人工智能学会, 智源社区, 机器之心, 量子位, DeepTech深科技, 新智元, AI科技评论, InfoQ, Datawhale, 智东西, or asks to expand/refresh that source set.
---

# AI WeChat News Digest

## Overview

Produce a concise news-style digest of recent AI articles from authoritative Chinese WeChat public accounts. By default, collect the three most recent publicly verifiable articles for each account. Keep the source method explicit: WeChat history pages are often not publicly crawlable, so public official sites, mirrored pages, and reputable aggregators may be used when they clearly correspond to the same account or article.

## Default Source Set

Start with this account range unless the user changes it:

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

## Retrieval Rules

Always browse or otherwise verify live results; do not rely on memory for latest-article requests.

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

For each candidate article, verify as many of these as possible:

- publication time or clear relative time
- source account or publisher
- title match across sources when using a repost
- article content is actually about AI, AI infrastructure, models, robotics, data, chips, developer tooling, or AI policy

If the user gives a relative time window, anchor it to the current date and timezone from the environment. For "past 12 hours", include only articles whose publication time can reasonably fit that window. If time is ambiguous, label it as "待复核" instead of treating it as confirmed.

When the user does not specify a time window, do not impose one. For each account, find up to three newest articles that can be publicly verified. If fewer than three are verifiable, include the available items and state the gap for that account.

## Source Labels

Label source type when it matters:

- `微信原文`: a direct `mp.weixin.qq.com` article.
- `官网同步`: the account or organization's own site.
- `内容社区`: official or semi-official content hubs such as 智源社区.
- `第三方转载`: reputable reposts such as Sina, Sohu, 51CTO, or similar pages.
- `聚合线索`: aggregator/search result only; use sparingly and mark as not fully verified.

Do not claim that an item came from the official WeChat article list unless it was actually obtained from a public WeChat page or official account list. It is acceptable to say the method retains the previous broader source approach: public web verification rather than strict WeChat-history extraction.

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
