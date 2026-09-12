#!/usr/bin/env python3
"""
全自动同步脚本：
- 从 GitHub API 拉取 beijixingdeyan 的仓库列表（排除 beijixingdeyan、deepseek-harness）
- 统计总数、Top 语言、最新 8 个仓库
- 自动更新 README.md 中的：
  1. About Me 仓库数
  2. English 版仓库数
  3. 顶部 Typing SVG 的 38+Repositories
  4. AUTO_REPOS 区域：最新 8 个仓库的表格（按 updated_at 降序）
  5. 分类矩阵中的总数提示
- 同步更新 index.html 中的仓库数展示（可选）
"""
import os, re, json, sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError

USERNAME = "beijixingdeyan"
# 只排除非原创的 deepseek-harness，保留 beijixingdeyan 配置仓库以保持总数 37
EXCLUDE = {"deepseek-harness"}
README = "README.md"
INDEX_HTML = "index.html"
API_URL = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated"

TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""

def fetch_repos():
    headers = {
        "User-Agent": "auto-update-profile",
        "Accept": "application/vnd.github+json",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = Request(API_URL, headers=headers)
    try:
        with urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            return data
    except HTTPError as e:
        print(f"API error {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
        sys.exit(1)

def main():
    repos = fetch_repos()
    # 过滤：仅排除 deepseek-harness，不再过滤 fork（保留所有原创）
    filtered = [r for r in repos if r["name"] not in EXCLUDE]
    # 按 updated_at 降序
    filtered.sort(key=lambda r: r["updated_at"], reverse=True)
    total = len(filtered)
    print(f"Total filtered repos: {total} (raw {len(repos)})")
    # Top 8 latest：排除配置仓库本身，只展示项目
    latest_candidates = [r for r in filtered if r["name"] != "beijixingdeyan"]
    latest = latest_candidates[:8]

    # 读取 README
    if not os.path.exists(README):
        print(f"{README} not found", file=sys.stderr)
        sys.exit(1)
    content = open(README, encoding="utf-8").read()
    original = content

    # 1. 更新中文计数
    # 匹配 <!-- AUTO_COUNT_START -->...<!-- AUTO_COUNT_END -->
    def repl_count(m):
        inner = m.group(1)
        # inner 形如 "- 📍 湘潭 · 湖南 | **38** 个公开仓库 ..."
        new_inner = re.sub(r"\*\*\d+\*\* 个公开仓库", f"**{total}** 个公开仓库", inner)
        return f"<!-- AUTO_COUNT_START -->{new_inner}<!-- AUTO_COUNT_END -->"
    content = re.sub(r"<!-- AUTO_COUNT_START -->(.*?)<!-- AUTO_COUNT_END -->", repl_count, content, flags=re.DOTALL)

    # 2. 更新英文计数
    def repl_count_en(m):
        inner = m.group(1)
        new_inner = re.sub(r"\d+ public repos", f"{total} public repos", inner)
        return f"<!-- AUTO_COUNT_EN_START -->{new_inner}<!-- AUTO_COUNT_EN_END -->"
    content = re.sub(r"<!-- AUTO_COUNT_EN_START -->(.*?)<!-- AUTO_COUNT_EN_END -->", repl_count_en, content, flags=re.DOTALL)

    # 3. 更新 Typing SVG（兼容 %2B 编码与 +）
    def repl_typing(m):
        inner = m.group(1)
        # 把 37%2BRepositories 或 37+Repositories 换成 N%2BRepositories（保持 URL 编码正确，修复 400）
        new_inner = re.sub(r"\d+(?:\+|%2B)Repositories", f"{total}%2BRepositories", inner)
        return f"<!-- AUTO_TYPING_START -->{new_inner}<!-- AUTO_TYPING_END -->"
    content = re.sub(r"<!-- AUTO_TYPING_START -->(.*?)<!-- AUTO_TYPING_END -->", repl_typing, content, flags=re.DOTALL)

    # 辅助：当 GitHub description 为空时，抓取 README 首段作为简介
    def fetch_readme_brief(repo_name: str) -> str:
        api = f"https://api.github.com/repos/{USERNAME}/{repo_name}/readme"
        headers = {
            "User-Agent": "auto-update-profile",
            "Accept": "application/vnd.github+json",
        }
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
        try:
            req = Request(api, headers=headers)
            with urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode())
                b64 = data.get("content", "")
                if not b64:
                    return ""
                import base64
                raw = base64.b64decode(b64).decode("utf-8", errors="ignore")
                for line in raw.splitlines():
                    s = line.strip()
                    if not s:
                        continue
                    if s.startswith("#") and len(s) < 80:
                        continue
                    if s.startswith("![") or s.startswith("[![") or s.startswith("<"):
                        continue
                    if s.startswith("```"):
                        continue
                    clean = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", s)
                    clean = re.sub(r"[*_`>]", "", clean).strip()
                    clean = clean.replace("|", "/")
                    if len(clean) < 6:
                        continue
                    if len(clean) > 60:
                        clean = clean[:57] + "..."
                    return clean
        except Exception:
            return ""
        return ""

    # 4. 生成 AUTO_REPOS 表格
    # 格式：| 排名 | 仓库 | 语言 | ⭐ | 更新时间 | 一句话 |
    # 逻辑：优先 GitHub description，空则取 README 首段
    rows = []
    for i, r in enumerate(latest, 1):
        name = r["name"]
        lang = r["language"] or "-"
        stars = r["stargazers_count"]
        updated = r["updated_at"][:10]
        desc = (r["description"] or "").replace("|", "/").replace("\n", " ").strip()
        if not desc:
            desc = fetch_readme_brief(name)
        if len(desc) > 60:
            desc = desc[:57] + "..."
        if not desc:
            desc = f"{lang} 项目 · 更新于 {updated}"
        rows.append(f"| {i} | [**{name}**](https://github.com/{USERNAME}/{name}) | {lang} | {stars} | {updated} | {desc} |")
    table = ""
    if rows:
        now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
        table = (
            "\n> 🤖 **自动同步**（每天 02:00 + 每次 push 后更新）— 最新 8 个仓库按 `updated_at` 排序\n\n"
            "| # | 仓库 | 语言 | ⭐ | 更新 | 简介 |\n"
            "|---|---|---|---|---|---|\n"
            + "\n".join(rows)
            + f"\n\n<sub>最后同步：{now} CST · 总数 **{total}** · 由 `auto-update.yml` 自动生成</sub>\n"
        )
    # 替换 AUTO_REPOS 区域
    content = re.sub(
        r"<!-- AUTO_REPOS_START -->.*?<!-- AUTO_REPOS_END -->",
        f"<!-- AUTO_REPOS_START -->{table}<!-- AUTO_REPOS_END -->",
        content,
        flags=re.DOTALL,
    )

    # 5. 更新分类矩阵标题中的 38
    content = re.sub(
        r"查看完整 \d+ 个仓库分类矩阵",
        f"查看完整 {total} 个仓库分类矩阵",
        content,
    )

    if content != original:
        open(README, "w", encoding="utf-8").write(content)
        print("README.md updated")
    else:
        print("README.md no change")

    # 6. 同步 index.html（可选）— 覆盖所有计数位置
    if os.path.exists(INDEX_HTML):
        html = open(INDEX_HTML, encoding="utf-8").read()
        orig_html = html
        html = re.sub(r"\d+ 个精选公开仓库", f"{total} 个精选公开仓库", html)
        # 徽章：37%20Repos 或 37 Repos
        html = re.sub(r"\d+%20Repos", f"{total}%20Repos", html)
        html = re.sub(r"\d+ Repos", f"{total} Repos", html)
        # meta 描述：37+ repositories / 37 repositories
        html = re.sub(r"\d+\+\s*repositories", f"{total}+ repositories", html, flags=re.IGNORECASE)
        html = re.sub(r"\d+\s+repositories", f"{total} repositories", html, flags=re.IGNORECASE)
        # 标题中的 37+ 
        html = re.sub(r"(\d+)\+\s*repositories", f"{total}+ repositories", html, flags=re.IGNORECASE)
        if html != orig_html:
            open(INDEX_HTML, "w", encoding="utf-8").write(html)
            print("index.html updated")

if __name__ == "__main__":
    main()
