# 供应来源说明

本目录是 vendored（随库携带）的第三方 skill，不是 git submodule。

| 项 | 值 |
|---|---|
| 上游 | https://github.com/pencil20388-eng/stop-slop-zh |
| 上游 commit | fb45e0c |
| 取用日期 | 2026-08-20 |
| 许可 | MIT，见 LICENSE |

## 为什么 vendor 而不是 submodule

本库对上游做了两处必要修改（见下），submodule 存不下这些改动。而且 submodule 要求新机器 clone 时加 `--recurse-submodules`，与「pull 完就能直接用」的目标冲突。

## 相对上游的修改

1. `SKILL.md` 补了 YAML frontmatter（`name` / `description`）。上游没有 frontmatter，Claude Code 不会把它注册成可调用 skill。
2. `SKILL.md` 增加`适用场景分流`一节，把学术笔记场景路由到 `references/academic-notes-profile.md`。
3. 新增 `references/academic-notes-profile.md`。上游规则面向公众号长文，硬禁小标题、bullet、编号结构，与本库 `AGENTS.md` 要求的精读稿骨架冲突。该文件做分层裁决。
4. 未取用上游的 `README.md` 和 `docs/`（站点验证页），与本库无关。

## 同步上游

上游更新时手动比对，注意不要覆盖掉上面四条。`references/` 下除 `academic-notes-profile.md` 外都是上游原文，可以直接替换。
