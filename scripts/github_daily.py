#!/usr/bin/env python3
"""
GitHub 每日高质量项目推送
多维度搜索 + 智能分析 + 价值判断
每天早上8点运行，推送结果到飞书
"""

import requests
import json
import time
import datetime
from datetime import datetime as dt
from pathlib import Path
import re
import sys
from collections import defaultdict

# ============ 配置 ============
SEARCH_DOMAINS = [
    {
        "name": "🤖 AI Agent / LLM 框架",
        "terms": ["ai agent", "llm framework", "autonomous agent", "ai assistant", "agent framework"],
        "min_stars": 100,
        "days": 30,
    },
    {
        "name": "🧠 AI 记忆 / 学习进化",
        "terms": ["ai memory", "knowledge graph", "rag", "continual learning", "personal ai", "agent memory"],
        "min_stars": 80,
        "days": 30,
    },
    {
        "name": "🔧 开发工具 / 效率",
        "terms": ["developer tool", "cli tool", "productivity", "automation", "devops"],
        "min_stars": 100,
        "days": 30,
    },
    {
        "name": "⚡ A股 / 量化金融",
        "terms": ["quantitative trading", "stock", "algorithmic trading", "trading bot", "finance"],
        "min_stars": 50,
        "days": 30,
    },
    {
        "name": "🔥 新颖有趣 / 创意项目",
        "terms": ["python-toolkit", "rust-cli", "go-microservice", "typescript-library", "open-source"],
        "min_stars": 50,
        "days": 14,
    }, {
        "name": "📱 开源移动端 / 跨平台",
        "terms": ["react-native", "flutter-app", "mobile-app", "ios-android", "cross-platform"],
        "min_stars": 50,
        "days": 14,
    },
]

# Hermes 相关关键词（用于匹配项目相关性）
HERMES_KEYWORDS = [
    "hermes", "agent", "ai assistant", "llm", "memory", "knowledge", "plugin",
    "autonomous", "tool", "workflow", "automation", "cli", "terminal",
    "coding agent", "code assistant", "mcp", "function calling", "rag",
    "multi-agent", "orchestrator", "skill", "prompt",
]

# 你的兴趣领域（用于给项目打标签）
INTEREST_TAGS = {
    "ai-agent": ["agent", "autonomous", "multi-agent", "orchestrator", "framework"],
    "memory-learning": ["memory", "knowledge", "rag", "learning", "knowledge-graph", "continual"],
    "cli-tool": ["cli", "terminal", "developer-tools", "productivity"],
    "quant-finance": ["stock", "trading", "quant", "finance", "market"],
    "creative-novel": ["game", "creative", "art", "music", "novel", "visual", "design"],
    "oss-ecosystem": ["open-source", "community", "plugin", "extension", "api"],
}

# ============ API 调用 ============

def github_search(query, sort="stars", order="desc", per_page=30, page=1):
    """搜索 GitHub 仓库

    重要：sort="stars" 时返回的是全时间 star 总数排序，
    这会让30天窗口内反复出现同一批老明星项目。
    对于日常发现场景，默认用 sort="created" 让最新项目排前面，
    配合 days 窗口过滤即可获得真正的新项目。
    """
    # 搜索排序策略：默认 created（最新项目优先），
    # 避免 sort=stars 让30天窗口内反复出现同一批老明星项目
    effective_sort = sort if sort != "stars" else "created"
    url = "https://api.github.com/search/repositories"
    headers = {"Accept": "application/vnd.github+json"}
    params = {
        "q": query,
        "sort": effective_sort,
        "order": order,
        "per_page": min(per_page, 100),
        "page": page,
    }
    time.sleep(0.5)
    r = requests.get(url, headers=headers, params=params, timeout=15)
    if r.status_code == 403:
        return {"error": "rate_limited", "items": []}
    if r.status_code == 422:
        return {"error": f"invalid_query: {r.text[:200]}", "items": []}
    if r.status_code != 200:
        return {"error": f"http_{r.status_code}", "items": []}
    data = r.json()
    return {"items": data.get("items", []), "total": data.get("total_count", 0)}

def analyze_project(repo):
    """分析项目并返回分析结果字典（确保永远返回 dict）"""
    try:
        desc = repo.get("description") or ""
        topics = repo.get("topics") or []
        lang = repo.get("language") or ""
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        created = repo.get("created_at", "")
        updated = repo.get("updated_at", "")
        html_url = repo.get("html_url", "")
        owner_type = repo.get("owner", {}).get("type", "")
        readme_text = repo.get("readme_text", "")

        description_text = f"{repo.get('name', '')} {desc} {' '.join(topics)}".lower()

        # 1. 计算与 Hermes Agent 的相关度
        hermes_relevance = 0
        for kw in HERMES_KEYWORDS:
            if kw.lower() in description_text:
                hermes_relevance += 1

        # 2. 计算与用户兴趣领域的匹配
        matched_tags = []
        for tag, keywords in INTEREST_TAGS.items():
            for kw in keywords:
                if kw.lower() in description_text:
                    matched_tags.append(tag)
                    break

        # 3. 质量评估
        quality_score = 0
        quality_factors = []

        if desc and len(desc) > 20:
            quality_score += 1
            quality_factors.append("有详细描述")

        if len(topics) >= 3:
            quality_score += 1
            quality_factors.append("多标签")

        if forks > 0 and stars / forks < 50:
            quality_score += 1
            quality_factors.append("社区活跃")

        if repo.get("license"):
            quality_score += 1
            quality_factors.append("开源许可")

        if updated:
            updated_dt = datetime.datetime.strptime(updated[:10], "%Y-%m-%d")
            if (datetime.datetime.now() - updated_dt).days < 14:
                quality_score += 1
                quality_factors.append("近期更新")

        # 4. 新颖性打分
        novelty_score = 0
        novelty_factors = []
        if created:
            created_dt = datetime.datetime.strptime(created[:10], "%Y-%m-%d")
            days_old = (datetime.datetime.now() - created_dt).days
            if days_old < 14:
                novelty_score += 2
                novelty_factors.append("全新项目")
            elif days_old < 30:
                novelty_score += 1
                novelty_factors.append("本月创建")

        org_project = owner_type == "Organization"

        return {
            "hermes_relevance": hermes_relevance,
            "matched_tags": list(set(matched_tags)),
            "quality_score": quality_score,
            "quality_factors": quality_factors,
            "novelty_score": novelty_score,
            "novelty_factors": novelty_factors,
            "org_project": org_project,
        }
    except Exception as e:
        # 任何异常都返回有效默认 dict，不让 analysis 变成 string
        return {
            "hermes_relevance": 0,
            "matched_tags": [],
            "quality_score": 0,
            "quality_factors": [],
            "novelty_score": 0,
            "novelty_factors": [],
            "org_project": False,
        }

def rate_project(analysis, repo):
    """综合评分，判断推荐优先级"""
    stars = repo.get("stargazers_count", 0)
    score = 0

    # 核心权重
    score += analysis["hermes_relevance"] * 3  # 对Hermes有用
    score += len(analysis["matched_tags"]) * 2  # 相关领域
    score += analysis["quality_score"] * 2      # 质量
    score += analysis["novelty_score"] * 2      # 新颖性
    if analysis["org_project"]:
        score += 1                              # 组织项目加分

    # Star 数量加分（但不过分看重）
    if stars >= 10000:
        score += 3
    elif stars >= 5000:
        score += 2
    elif stars >= 1000:
        score += 1

    # 判断推荐等级
    if score >= 15:
        level = "🔥 强烈推荐"
    elif score >= 10:
        level = "⭐ 值得关注"
    elif score >= 6:
        level = "👀 可以看看"
    else:
        level = "📋 一般"

    return score, level

def get_readme_preview(owner, repo_name):
    """获取 README 的前几行用于分析"""
    for branch in ["main", "master"]:
        url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/README.md"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                lines = r.text.split("\n")
                # 返回前50行或前1000字符
                preview = "\n".join(lines[:50])
                return preview[:1500]
        except:
            pass
    return ""

# ============ 推送历史去重 ============
# 持久化记录每天推送过的项目及推送次数
# 逻辑：第一次推→只推送；第二次推→推送+入学习队列；已学习→永不再推
PUSH_HISTORY_FILE = Path("/home/ubuntu/hermes-agent/scripts/github_push_history.json")

def get_push_history(days=14):
    """读取最近N天各项目的推送次数 {full_name: count}"""
    if not PUSH_HISTORY_FILE.exists():
        return {}
    try:
        history = json.loads(PUSH_HISTORY_FILE.read_text())
    except:
        return {}
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
    result = {}
    for date_str, entries in history.items():
        if date_str >= cutoff:
            for name in entries:
                result[name] = result.get(name, 0) + 1
    return result

def get_push_count(full_name):
    """查某项目最近14天被推过几次"""
    return get_push_history().get(full_name, 0)

def mark_pushed_and_learn(project_names):
    """记录今日推送；若项目是第二次推，自动加入 hourly_learn 队列"""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    history = {}
    if PUSH_HISTORY_FILE.exists():
        try:
            history = json.loads(PUSH_HISTORY_FILE.read_text())
        except:
            history = {}
    # 合并今日推送（去重）
    today_projects = list(set(history.get(today, [])) | set(project_names))
    history[today] = today_projects
    # 清理超过30天的旧记录
    cutoff = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    history = {d: n for d, n in history.items() if d >= cutoff}
    PUSH_HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2))

    # 检查哪些项目是第二次推送 → 自动入学习队列
    all_counts = get_push_history(days=14)
    for name in project_names:
        if all_counts.get(name, 0) == 2:
            # 第二次推送，自动加进学习队列
            try:
                queue_file = Path("/home/ubuntu/hermes-learning/_learn_queue.json")
                existing = json.loads(queue_file.read_text()) if queue_file.exists() else []
                existing_names = {p["name"] for p in existing}
                if name not in existing_names:
                    existing.append({
                        "name": name,
                        "url": f"https://github.com/{name}",
                        "desc": "github_daily 第二次推送自动加入",
                        "priority": "P1",
                        "added": dt.now().isoformat(),
                        "source": "github_daily_auto_learn",
                        "score": 0,
                        "stars": 0,
                    })
                    queue_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
                    print(f"    📚 {name} 第二次推送，自动加入学习队列")
            except Exception as e:
                print(f"    ⚠️ 自动入队列失败: {e}")

def is_already_pushed(full_name):
    """检查项目是否在最近14天推送过"""
    return get_push_count(full_name) > 0

# ============ 原有函数 ============

def get_learned_names():
    """从 hourly_learn 状态文件读取已学项目列表"""
    try:
        state_file = Path("/home/ubuntu/hermes-learning/_hourly_state.json")
        if state_file.exists():
            state = json.loads(state_file.read_text())
            return set(state.get("learned", []))
    except:
        pass
    return set()

def is_learned(full_name):
    """检查项目是否已学过（支持 owner/repo 和 owner-repo 两种格式）"""
    learned = get_learned_names()
    if not learned:
        return False
    # 归一化比较
    normalized = full_name.lower().replace('/', '_')
    for name in learned:
        if name.lower().replace('/', '_') == normalized:
            return True
    return False

def should_skip(full_name):
    """综合去重判断：已学习过的项目永不再推"""
    return is_learned(full_name)

def fetch_trending_repos():
    """从 GitHub Trending 页面抓取涨星最快的项目"""
    trending_repos = []
    try:
        r = requests.get('https://github.com/trending?since=daily',
                       headers={'Accept': 'text/html', 'User-Agent': 'Mozilla/5.0'}, timeout=10)
        html = r.text
        for m in re.finditer(r'href="(/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)"', html):
            path = m.group(1)
            parts = path.split('/')
            if len(parts) == 3 and parts[0] == '' and parts[1] not in ('login', 'organizations', 'topics', 'collections', 'trending'):
                owner_repo = f'{parts[1]}/{parts[2]}'
                if owner_repo not in trending_repos:
                    trending_repos.append(owner_repo)
    except Exception as e:
        print(f'    ⚠️ Trending 抓取失败: {e}')
    return trending_repos[:15]

def search_trending_growth(all_repos):
    """搜索涨星最快的项目，合并到 all_repos"""
    trending = fetch_trending_repos()
    if not trending:
        return
    print(f'    📈 Trending 抓到 {len(trending)} 个，筛选未学习...')
    new_count = 0
    for full_name in trending:
        if full_name in all_repos or should_skip(full_name):
            continue
        owner, repo = full_name.split('/', 1)
        url = f'https://api.github.com/repos/{owner}/{repo}'
        try:
            r = requests.get(url, headers={'Accept': 'application/vnd.github.v3+json'}, timeout=10)
            data = r.json()
            repos = data.get('stargazers_count', 0)
            desc = data.get('description', '') or 'GitHub Trending 涨星最快项目'
            topics = data.get('topics', [])
            lang = data.get('language', '') or '未知'
            repo_data = {
                'full_name': full_name,
                'name': repo,
                'description': desc,
                'stargazers_count': repos,
                'forks_count': data.get('forks_count', 0),
                'owner': {'login': owner, 'type': data.get('owner', {}).get('type', 'User')},
                'language': lang,
                'topics': topics,
                'html_url': data.get('html_url', ''),
                'created_at': data.get('created_at', ''),
                'updated_at': data.get('updated_at', ''),
                'license': data.get('license'),
            }
            analysis = analyze_project(repo_data)
            score, level = rate_project(analysis, repo_data)
            all_repos[full_name] = {
                'repo': repo_data,
                'analysis': analysis,
                'score': score,
                'level': level,
                'domains': ['📈 涨星最快'],
            }
            new_count += 1
        except Exception as e:
            pass
        time.sleep(0.3)
    print(f'    ✅ 新项目 +{new_count} 个')

def search_all_domains():
    """执行所有领域搜索，返回合并结果（自动跳过已学项目）"""
    all_repos = {}  # full_name -> {repo, analysis, score, level, domain}
    learned = get_learned_names()
    skipped_learned = 0

    for domain in SEARCH_DOMAINS:
        name = domain["name"]
        min_stars = domain.get("min_stars", 100)
        days = domain.get("days", 30)
        broad = domain.get("broad_search", False)

        since = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d")

        if broad:
            search_query = f"created:>{since} stars:>{min_stars}"
        elif "terms" in domain:
            term_queries = [f'"{t}"' if " " in t else t for t in domain["terms"]]
            all_terms = " OR ".join(term_queries)
            search_query = f"{all_terms} created:>{since} stars:>{min_stars}"
        elif "query" in domain:
            search_query = f"{domain['query']} created:>{since} stars:>{min_stars}"
        else:
            search_query = f"created:>{since} stars:>{min_stars}"

        print(f"  🔍 搜索: {name}")
        print(f"     查询: {search_query}")

        result = github_search(search_query, per_page=30)

        if "error" in result:
            print(f"     ⚠️  {result['error']}")
            continue

        items = result.get("items", [])
        print(f"     📊 找到 {len(items)} 个项目")

        domain_learned = 0
        for repo in items:
            fn = repo["full_name"]

            # 跳过已学或近期已推送项目
            if should_skip(fn):
                skipped_learned += 1
                domain_learned += 1
                continue

            if fn in all_repos:
                all_repos[fn]["domains"].append(name)
                continue

            # 获取 README 预览
            if repo.get("description") and len(repo.get("description", "")) < 100:
                readme_preview = get_readme_preview(
                    repo["owner"]["login"], repo["name"]
                )
                repo["readme_text"] = readme_preview
            else:
                repo["readme_text"] = ""

            analysis = analyze_project(repo)
            score, level = rate_project(analysis, repo)

            all_repos[fn] = {
                "repo": repo,
                "analysis": analysis,
                "score": score,
                "level": level,
                "domains": [name],
            }

            time.sleep(0.3)  # 避免限流

        if domain_learned > 0:
            print(f"     ⏭️ 跳过 {domain_learned} 个已学项目")

    print(f"\n📊 搜索完成: {len(all_repos)} 个新项目 (跳过 {skipped_learned} 个已学)")
    return all_repos

def format_repo(repo_data):
    """格式化单个项目为 Markdown"""
    repo = repo_data["repo"]
    analysis = repo_data["analysis"]
    level = repo_data["level"]
    score = repo_data["score"]
    domains = repo_data["domains"]

    name = repo["full_name"]
    desc = repo.get("description") or "暂无描述"
    stars = repo.get("stargazers_count", 0)
    lang = repo.get("language") or ""
    topics = repo.get("topics") or []
    url = repo.get("html_url", "")
    forks = repo.get("forks_count", 0)
    issues = repo.get("open_issues_count", 0)
    created = repo.get("created_at", "")[:10]

    # 标签
    tag_str = ""
    if topics:
        tag_str = " `" + "` `".join(topics[:5]) + "`"

    meta_parts = []
    if lang:
        meta_parts.append(f"🔵 {lang}")
    meta_parts.append(f"⭐{stars}")
    if forks > 0:
        meta_parts.append(f"⑂{forks}")
    meta = " · ".join(meta_parts)

    # 推荐理由
    reasons = []
    if analysis["hermes_relevance"] >= 3:
        reasons.append("与 Hermes Agent 高度相关")
    if analysis["matched_tags"]:
        tags_cn = {
            "ai-agent": "AI Agent",
            "memory-learning": "记忆/学习",
            "cli-tool": "开发工具",
            "quant-finance": "量化金融",
            "creative-novel": "创意新颖",
            "oss-ecosystem": "开源生态",
        }
        reason_tags = [tags_cn.get(t, t) for t in analysis["matched_tags"][:3]]
        reasons.append("相关领域: " + "/".join(reason_tags))
    if analysis["quality_factors"]:
        reasons.append("亮点: " + "、".join(analysis["quality_factors"][:3]))
    if analysis["novelty_factors"]:
        reasons.append("、".join(analysis["novelty_factors"]))
    if analysis["org_project"]:
        reasons.append("组织项目")

    reason_str = ""
    if reasons:
        reason_str = f"  _💡 {'. '.join(reasons)}_"

    day_created = created
    tags_display = tag_str

    return (
        f"- **[{name}]({url})** {level}\n"
        f"  _{desc}_\n"
        f"  {meta}{tags_display}\n"
        f"{reason_str}\n"
    )

def load_yesterday_stars():
    """加载昨天的 star 快照，返回 {full_name: star_count}"""
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y%m%d")
    snapshot_file = Path(f"/home/ubuntu/daily-awesome-archive/data/.star_snapshots/{yesterday}.json")
    if snapshot_file.exists():
        try:
            return json.loads(snapshot_file.read_text())
        except:
            pass
    return {}


def save_today_stars(all_repos):
    """保存今天的 star 快照，用于明天计算涨幅"""
    today = datetime.datetime.now().strftime("%Y%m%d")
    snapshot_dir = Path("/home/ubuntu/daily-awesome-archive/data/.star_snapshots")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    snapshot = {fn: item["repo"].get("stargazers_count", 0) for fn, item in all_repos.items()}
    (snapshot_dir / f"{today}.json").write_text(json.dumps(snapshot, ensure_ascii=False))


def generate_report(all_repos):
    """生成推送报告"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    items = list(all_repos.values())

    # 按评分排序
    items.sort(key=lambda x: x["score"], reverse=True)

    top_items = items[:30]  # 最多显示30个

    lines = []
    lines.append(f"📡 **GitHub 每日高质量项目推送** | {now}")
    lines.append("")
    lines.append("*多维搜索 + 智能分析，自动判断推荐优先级*\n")

    # ============ 第一部分：涨星最快（独立专区）============
    trending_items = [x for x in top_items if "📈 涨星最快" in x.get("domains", [])]
    if trending_items:
        # 按 star 数排序（涨星最快的 GitHub Trending 项目）
        trending_items.sort(key=lambda x: x["repo"].get("stargazers_count", 0), reverse=True)
        yesterday_stars = load_yesterday_stars()
        
        lines.append("## 📈 涨星最快（GitHub Trending 今日赢家）")
        lines.append("_GitHub Trending 24小时涨星排名_\n")
        for i, item in enumerate(trending_items[:10], 1):
            repo = item["repo"]
            fn = repo["full_name"]
            stars = repo.get("stargazers_count", 0)
            yesterday = yesterday_stars.get(fn, stars)  # 没有昨天数据就显示今日总数
            delta = stars - yesterday if yesterday else 0
            delta_str = f"+{delta}" if delta > 0 else str(delta) if delta < 0 else "—"
            if delta > 0:
                delta_str = f"+📈{delta}"
            elif delta == 0 and yesterday:
                delta_str = "—"
            
            level = item["level"]
            url = repo.get("html_url", "")
            desc = repo.get("description") or "暂无描述"
            lang = repo.get("language") or ""
            forks = repo.get("forks_count", 0)
            
            meta = f"⭐{stars}"
            if lang:
                meta += f" · 🔵{lang}"
            if forks > 0:
                meta += f" · ⑂{forks}"
            if delta > 0:
                meta += f" · {delta_str}"
            
            lines.append(f"{i}. **[{fn}]({url})** {level}")
            lines.append(f"   _{desc}_")
            lines.append(f"   {meta}\n")
        lines.append("")

    # ============ 第二部分：强烈推荐 ============
    hot = [x for x in top_items if x["level"] == "🔥 强烈推荐"]
    if hot:
        lines.append("## 🔥 强烈推荐")
        lines.append("_高价值项目，建议深入了解一下_\n")
        for item in hot:
            lines.append(format_repo(item))
        lines.append("")

    # ============ 第三部分：按领域分组 ============
    worthwhile = [x for x in top_items if x["level"] != "🔥 强烈推荐"]
    if worthwhile:
        # 按 domain 分组
        domain_items = defaultdict(list)
        for item in worthwhile:
            for d in item["domains"]:
                domain_items[d].append(item)

        lines.append("## 📂 按领域分类")
        for domain_name in [d["name"] for d in SEARCH_DOMAINS]:
            domain_repos = domain_items.get(domain_name, [])
            if not domain_repos:
                continue
            # 只展示评分最高的
            domain_repos.sort(key=lambda x: x["score"], reverse=True)
            top_domain = domain_repos[:5]

            lines.append(f"### {domain_name}")
            for item in top_domain:
                lines.append(format_repo(item))
            lines.append("")

    # ============ 第四部分：统计信息 ============
    lines.append("---")
    lines.append("📊 **统计**")
    lines.append(f"- 共扫描 {len(SEARCH_DOMAINS)} 个领域，发现 {len(all_repos)} 个项目")
    lines.append(f"- 🔥 强烈推荐: {len(hot)} 个")
    levels = defaultdict(int)
    for item in items:
        levels[item["level"]] += 1
    for lv, cnt in sorted(levels.items()):
        lines.append(f"- {lv}: {cnt} 个")
    lines.append(f"- 数据来源: GitHub API (未认证)")
    lines.append(f"- ✅ 本次推送 {len(all_repos)} 个项目，全部含 GitHub 仓库地址")
    lines.append("")

    # ============ 宣传 ============
    lines.append("---")
    lines.append("📅 **收藏精选项目？**")
    lines.append("> 每日 GitHub 高质量项目归档 → [**Daily Awesome Archive**](https://github.com/xiekun711/daily-awesome-archive)")
    lines.append("> 每天自动搜索精选，按日期归档，再也不怕错过好项目 ✨")
    lines.append("")

    return "\n".join(lines)


# ============ 主函数 ============

def main():
    print("🌐 GitHub 每日高质量项目推送")
    print("=" * 50)
    print(f"开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    # 先检查限流
    r = requests.get("https://api.github.com/rate_limit")
    rate = r.json().get("rate", {})
    remaining = rate.get("remaining", 0)
    limit = rate.get("limit", 60)
    print(f"📊 API 配额: {remaining}/{limit}")
    
    if remaining < 10:
        print("⚠️  API 配额不足，跳过搜索")
        return ""
    
    print("")

    # 先抓 Trending 涨星最快的项目
    print("📈 抓取 Trending 涨星最快项目...")
    all_repos = {}
    search_trending_growth(all_repos)

    # 执行关键词搜索
    print("\n🔍 开始关键词搜索...")
    keyword_repos = search_all_domains()

    # 合并结果
    for fn, item in keyword_repos.items():
        if fn not in all_repos:
            all_repos[fn] = item

    print(f"\n📊 总发现 {len(all_repos)} 个项目")

    # 生成报告
    print("\n📝 生成报告...")
    report = generate_report(all_repos)

    # 保存今日 star 快照（用于明天计算涨幅）
    try:
        save_today_stars(all_repos)
        print("✅ 今日 star 快照已保存")
    except Exception as e:
        print(f"⚠️ star 快照保存失败: {e}")

    # 保存到文件（带日期后缀，确保 hourly_learn 能找到）
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    output_path = f"/home/ubuntu/hermes-agent/scripts/github_daily_output_{today_str}.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ 报告已保存: {output_path}")

    # 同时追加到 hourly_learn 的队列
    try:
        import json
        from pathlib import Path

        queue_file = Path("/home/ubuntu/hermes-learning/_learn_queue.json")
        existing = json.loads(queue_file.read_text()) if queue_file.exists() else []
        existing_names = {p["name"] for p in existing}

        added = 0
        for fn, item in all_repos.items():
            if fn in existing_names:
                continue
            entry = {
                "name": fn,
                "url": item["repo"]["html_url"],
                "desc": item.get("analysis", ""),
                "priority": item.get("level", "P1"),
                "added": dt.now().isoformat(),
                "source": "github_daily",
                "score": item.get("score", 0),
                "stars": item["repo"].get("stargazers_count", 0),
            }
            existing.append(entry)
            added += 1

        queue_file.write_text(json.dumps(existing, ensure_ascii=False, indent=2))
        print(f"✅ 队列已更新: +{added} 个新项目 (队列共 {len(existing)} 个)")
    except Exception as e:
        print(f"⚠️ 队列更新失败: {e}")

    # 记录今日推送项目到历史（第二次推送自动入学习队列）
    try:
        mark_pushed_and_learn(list(all_repos.keys()))
        print(f"✅ 推送历史已更新")
    except Exception as e:
        print(f"⚠️ 推送历史记录失败: {e}")

    # 输出简要版到 stdout（Hermes cron 会捕获这个）
    print("\n" + "=" * 50)
    print("报告摘要:")
    print(report)

    return report


if __name__ == "__main__":
    report = main()
    # main() 内部已经 print 了 report
    if report:
        print("\n--- 推送至此结束 ---")
