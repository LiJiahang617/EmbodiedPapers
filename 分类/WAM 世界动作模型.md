---
tags:
  - collection
cat: cat/wam
desc: 联合建模未来预测与动作生成的世界动作模型
---

# WAM 世界动作模型

联合建模未来预测与动作生成的一族，视频生成式与潜空间式都算，含 WAM 的后训练与适配工作。

```dataview
TABLE WITHOUT ID file.link AS "论文", aliases[0] AS "短名", year AS "年份", choice(reading, "✓", "⌛") AS "精读"
FROM #paper and #cat/wam
SORT year DESC, file.name ASC
```
