# 部署到 GitHub Profile

你的个人主页仓库是特殊的：**`https://github.com/beijixingdeyan/beijixingdeyan`**（仓库名与用户名同名），它的 `README.md` 会自动展示在 `https://github.com/beijixingdeyan` 顶部。

本目录 `E:\github\resume` 里的 `README.md` 就是为它准备的，已经融合了：

- **Awesome GitHub Profile README** 的 12 种风格（极简 / 动态打字 / 卡片化 / 数据看板 / 徽章墙 / 插画头尾等）
- **MajesticalProfiles** 的真实案例策展思路（精选 8 大代表作 + 完整 38 仓库矩阵）

## 一键推送（PowerShell）

```powershell
# 1. 克隆你的主页仓库（若还没克隆）
git clone https://github.com/beijixingdeyan/beijixingdeyan.git E:\github\beijixingdeyan-profile
# 或者如果已存在，直接更新
# git -C E:\github\beijixingdeyan-profile pull

# 2. 复制新版 README
Copy-Item E:\github\resume\README.md E:\github\beijixingdeyan-profile\README.md -Force

# 3. 同步蛇形动画 workflow（可选，但推荐）
Copy-Item E:\github\resume\.github -Destination E:\github\beijixingdeyan-profile\.github -Recurse -Force

# 4. 提交推送
git -C E:\github\beijixingdeyan-profile add .
git -C E:\github\beijixingdeyan-profile commit -m "feat: redesign profile README — Awesome + Majestical inspired"
git -C E:\github\beijixingdeyan-profile push
```

推送后 **1-5 分钟** 刷新 https://github.com/beijixingdeyan 即可看到效果。`capsule-render` / `skillicons` / `github-readme-stats` 等图片是动态生成的，首次加载稍慢属正常。

## 贡献蛇 Snake 动画

`README.md` 里已嵌入：

```md
![snake](https://raw.githubusercontent.com/beijixingdeyan/beijixingdeyan/output/github-contribution-grid-snake.svg)
```

需要让 `snake.yml` 跑一次才能生成 `output` 分支：

1. 推送后到仓库页 `Actions` → `Generate Snake` → `Run workflow`
2. 等待 1-2 分钟，`output` 分支出现后，README 里的蛇就会动起来
3. 之后每 6 小时自动更新

## 自定义

- **改名/学校/标语**：搜 `Pengqi` / `HNUST` / `Typing SVG` 即可改
- **精选项目**：改 `Featured` 表格，换成你最想展示的 6-8 个（建议保持 2 列布局）
- **技术栈图标**：改 `skillicons.dev/icons?i=...` 的 `i=` 列表，图标名见 https://skillicons.dev
- **配色**：`capsule-render` 的 `color=0:0f172a,...` 是渐变，可换成你喜欢的（如 `color=gradient` 或 `color=ff6b6b`）
- **统计主题**：`theme=tokyonight` 可换 `dracula` / `radical` / `github_dark` 等

## 本地预览

直接用 VS Code 打开 `E:\github\resume\README.md` 按 `Ctrl+Shift+V` 预览，或推送到 GitHub 后查看真实渲染（GitHub 对 HTML 表格支持更好）。

---

如需我帮你改成 **英文主版 / 中文主版 / 极简版**，直接说一声就行。
