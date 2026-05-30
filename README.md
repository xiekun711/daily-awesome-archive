<div align="center">

# 📅 Daily Awesome Archive

**每日 AI 驱动的高质量开源项目精选**

*AI-Powered Daily Archive of High-Quality GitHub Projects*

[![GitHub Stars](https://img.shields.io/github/stars/xiekun711/daily-awesome-archive?style=flat-square&logo=github)](https://github.com/xiekun711/daily-awesome-archive)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/xiekun711/daily-awesome-archive/pulls)

---

**不是普通的 GitHub Trending。是我们自己训练出来的 AI 每天帮我们从 Trending 里挑真正有价值的项目。**

</div>

---

## 🎯 这个项目是做什么的

每天自动扫描 GitHub Trending，用 AI 精选 5 个重点领域的优质开源项目，并归档成每日报告。

```
08:00 → AI 扫描 GitHub Trending → 精选报告 → 飞书推送
08:10 → 自动归档 → GitHub 同步
```

## 🔥 我们的优势

| 维度 | 普通 GitHub Trending | Daily Awesome Archive |
|------|---------------------|---------------------|
| 筛选粒度 | 全站热门，不分领域 | 5 个重点垂直领域精筛 |
| AI Agent 评分 | 无 | 每项目多轮深度分析评分 |
| 量化交易资源 | ❌ 没有 | ✅ A股量化专项追踪 |
| AI Agent 专项 | ❌ 没有 | ✅ AI 记忆、Agent 框架专项 |
| 归档结构 | 散乱 | 每日归档，永久可查 |
| 推送渠道 | 需要自己刷 | 飞书每日推送 |

**核心差异化**：
- 🤖 **AI 筛选** — 不是按 star 数量排序，是按项目实际价值评分
- 📊 **垂直深耕** — AI Agent、量化交易、开发工具是我们的重点方向
- 🔍 **中文视角** — 关注国内好用的开源项目，不只是硅谷热门
- 🤝 **社区共建** — 欢迎提交你发现的好项目

## 🗂️ 归档日历

| 日期 | 项目数 | 链接 |
|------|--------|------|
| 2026-05-30 | 30 | [📄 查看](data/20260530.md) |
| 2026-05-29 | 30 | [📄 查看](data/20260529.md) |
| 2026-05-28 | 30 | [📄 查看](data/20260528.md) |

## 🔍 搜索领域

每天自动追踪这 5 个领域：

| 领域 | 说明 |
|------|------|
| 🤖 AI Agent / LLM 框架 | AI 智能体、大模型框架、自动化助手 |
| 🧠 AI 记忆 / 学习进化 | AI 记忆系统、知识图谱、RAG |
| 🔧 开发工具 / 效率 | CLI 工具、开发效率、DevOps |
| ⚡ 量化金融 | A 股量化、加密货币量化、算法交易 |
| 🔥 新颖有趣 | 创意项目、有趣的开源项目 |

## ⭐ 评分标准

每个项目按 4 档评分：

- 🔥 **强烈推荐** — 高价值项目，值得深入了解
- ⭐ **值得关注** — 不错的项目，值得收藏
- 👀 **可以看看** — 有意思，打发时间看看
- 📋 **一般** — 不太相关或质量一般

## 🤔 为什么值得看

1. **节省时间** — 不用自己刷 Trending，AI 帮你筛选出真正有价值的
2. **发现长尾** — 很多好项目 star 不高但实际很有用，AI 能发现它们
3. **垂直深入** — 普通 Trending 没有的垂直领域专项追踪
4. **量化资源** — A股/加密货币量化相关的开源资源持续追踪

## 🤝 如何参与

### 方式一：提交你发现的好项目（最简单）

直接提交 Issue 或 PR，格式随意，哪怕只发一个项目名+链接也行。

我们没有严格格式要求，只要你说清楚：
- 这是什么项目
- 为什么值得推荐
- 属于哪个领域

### 方式二：提搜索关键词建议

想追踪新的领域？在 Issue 里告诉我们：
- 你想追踪什么方向
- 建议的搜索关键词

### 方式三：贡献代码

- 改进 AI 评分算法
- 添加新的数据源
- 优化归档格式
- 修 Bug / 改进文档

👉 详见 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📂 项目结构

```
daily-awesome-archive/
├── data/                     # 每日归档
│   ├── 20260530.md          # 每日精选项目列表
│   └── ...
├── scripts/                  # 自动化脚本
│   ├── sync_to_github.sh    # 自动同步到 GitHub
│   └── parse_and_append.sh  # 解析原始报告
├── generate_promo_v2.py     # 推广文案生成
├── gen_video.py             # 视频生成
└── README.md
```

## ⚙️ 自动流程

```
08:00 (北京时间)
  └── Hermes Agent 定时触发
        ├── GitHub API 搜索 5 个领域
        ├── AI 评分 + 精选
        ├── 生成飞书推送报告
        └── 自动 commit 到 GitHub
```

> 由 [Hermes Agent](https://hermes-agent.nousresearch.com) 自动维护 · *Auto-maintained by AI*

---

## 📜 License

[MIT](LICENSE)

---

*觉得有用的话，给个 ⭐ 支持一下！*
