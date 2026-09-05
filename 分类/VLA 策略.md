---
tags:
  - collection
cat: cat/vla
desc: 视觉语言动作策略本体的工作
---

# VLA 策略

视觉语言动作策略本体的工作，训练配方、推理机制、监督设计、结构改动都算。一篇论文若同时是 WAM 或基础模型，会在对应分类里再次出现。

```dataview
TABLE WITHOUT ID file.link AS "论文", aliases[0] AS "短名", year AS "年份", choice(reading, "✓", "⌛") AS "精读"
FROM #paper and #cat/vla
SORT year DESC, file.name ASC
```
