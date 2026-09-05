---
tags:
  - collection
cat: cat/rl
desc: 强化学习与人在环训练
---

# RL 强化学习

强化学习训练机器人策略的工作，人在环干预、离线到在线、真机 RL 都在这。

```dataview
TABLE WITHOUT ID file.link AS "论文", aliases[0] AS "短名", year AS "年份", choice(reading, "✓", "⌛") AS "精读"
FROM #paper and #cat/rl
SORT year DESC, file.name ASC
```
