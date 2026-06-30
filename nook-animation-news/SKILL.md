---
name: nook-animation-news
description: >
  动画行业新闻聚合器，从 14 个权威 RSS 源实时抓取新闻。支持两种输出模式：
  JSON 原始数据（fetch）和 aihot 风格 Markdown 简报（brief）。
  当用户询问动画行业最新动态、想看动画新闻、搜索特定动画话题时触发。
---

# 动画行业新闻聚合器

从 14 个 RSS 源实时抓取动画行业新闻，核心脚本为 `scripts/fetch_news.py`。

## 使用方式

### 输出 aihot 风格简报（推荐，用户要求看新闻时使用）

```bash
python scripts/fetch_news.py brief [选项]
```

输出格式：按"动画电影/剧集 → 行业动态 → 制作技术/工具 → 社区话题"分组，
全局编号，时间转换为中文相对时间（"11 小时前"、"昨天"），
自动过滤低质量 Reddit 帖子。

### 输出 JSON 原始数据

```bash
python scripts/fetch_news.py fetch [选项]
```

### 通用选项

| 选项 | 说明 |
|------|------|
| `--category, -c` | 按分类筛选（见下表）|
| `--source, -s` | 按来源名称筛选 |
| `--search, -q` | 关键词搜索（匹配标题和摘要）|
| `--date, -d` | 按日期过滤 `YYYY-MM-DD` |
| `--limit, -n` | 最大条数，默认 20 |

### 辅助命令

```bash
python scripts/fetch_news.py categories   # 列出所有分类
python scripts/fetch_news.py sources      # 列出所有来源
```

## 简报分组规则（brief 模式）

| 简报分组 | 匹配的原始分类 | 说明 |
|----------|---------------|------|
| 动画电影 / 剧集 | industry_news（标题含 film/movie/season/series/anime/cour/trailer/annecy 等）| 作品发布、续订、票房、预告 |
| 行业动态 | industry_news（其余）| 公司动态、行业活动、工作室签约 |
| 制作技术 / 工具 | motion_design | 动态设计作品、技术教程、工具更新 |
| 社区话题 | community / careers / 3d_animation / academic / motion_design（低信息量帖二次过滤）| 值得关注的社区讨论 |

## 质量过滤

brief 模式自动跳过：仅含 `submitted by [link] [comments]` 的空壳帖、摘要不足 50 字的 Reddit 帖。

## 执行注意事项

1. 脚本首次运行时自动安装 `feedparser`、`httpx`、`beautifulsoup4` 依赖
2. 使用 `shell_executor` 执行，目录切换到技能根目录
3. **用户要求看新闻时优先使用 `brief` 子命令**，直接输出格式化简报

## 新闻源列表

| 名称 | 分类 | 网站 |
|------|------|------|
| Cartoon Brew | industry_news | cartoonbrew.com |
| Animation World Network | industry_news | awn.com |
| Animation Magazine | industry_news | animationmagazine.net |
| Skwigly | industry_news | skwigly.co.uk |
| Stop Motion Magazine | industry_news | stopmotionmagazine.com |
| Animation World | industry_news | animationworld.net |
| European Animation Journal | industry_news | europeananimationjournal.com |
| Motionographer | motion_design | motionographer.com |
| Stash Media | motion_design | stashmedia.tv |
| Reddit r/MotionDesign | motion_design | reddit.com/r/MotionDesign |
| Reddit r/animation | community | reddit.com/r/animation |
| Reddit r/animationcareer | careers | reddit.com/r/animationcareer |
| Reddit r/blender | 3d_animation | reddit.com/r/blender |
| Animation Studies | academic | blog.animationstudies.org |
