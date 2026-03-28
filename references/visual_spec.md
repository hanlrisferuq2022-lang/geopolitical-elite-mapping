# 可视化规范 (Graphviz SVG)

> Phase 4 节点配色、边样式、置信度视觉编码、时间轴、Legend 的完整规范。

## 节点类型 + 配色规范

节点类型完整定义（shape / fillcolor / 边框色）见 [data_schema.md](data_schema.md#节点类型)，此处不再重复。

⚠️ 必须严格遵守：节点 fillcolor 按类型固定，边框色（`color`）按所属利益阵营动态分配。

## 阵营边框色

由 Phase 1 的行为体发现动态确定，按阵营发现顺序依次分配：

| 序号 | 边框色 | 色名 |
|------|--------|------|
| 阵营 1 | `#3d85c6` | 蓝 |
| 阵营 2 | `#6aa84f` | 绿 |
| 阵营 3 | `#8e7cc3` | 紫 |
| 阵营 4 | `#cc4125` | 红 |
| 阵营 5 | `#e69138` | 橙 |
| 阵营 6+ | `#999999` | 灰 |

---

## 置信度视觉编码 ⚠️

> [!CAUTION]
> 置信度必须编码进图谱视觉本身，不是可选注释。以下规则不可跳过。

### 节点边框置信度编码

| 置信度 | `style` | `penwidth` | 视觉效果 |
|--------|---------|------------|---------|
| **HIGH** | `solid` | `2.5` | 粗实线边框 — 高确定性 |
| **MED** | `solid` | `1.5` | 中等实线边框 |
| **LOW** | `dashed` | `1.2` | 虚线边框 — 提示不确定性 |
| **INFERRED** | `dotted` | `1.0` | 点线边框 — 明确标注为推断 |

```python
# 节点置信度编码示例
def node_style(confidence: str) -> dict:
    styles = {
        'HIGH':     {'style': 'filled,bold',   'penwidth': '2.5'},
        'MED':      {'style': 'filled',        'penwidth': '1.5'},
        'LOW':      {'style': 'filled,dashed', 'penwidth': '1.2'},
        'INFERRED': {'style': 'filled,dotted', 'penwidth': '1.0'},
    }
    return styles.get(confidence, styles['MED'])
```

### 边（主边）置信度编码

| 置信度 | `style` | `penwidth` | 视觉效果 |
|--------|---------|------------|---------|
| **HIGH** | `solid` | `2.5` | 粗实线 — 高确定性关系 |
| **MED** | `solid` | `1.5` | 中等实线 |
| **LOW** | `dashed` | `1.0` | 虚线 — 不确定关系 |
| **INFERRED** | `dotted` | `0.7` | 极细点线 — 推断性关系 |

### 边（注释层）置信度编码

注释层边默认使用虚线。置信度通过线宽区分：

| 置信度 | `style` | `penwidth` | 视觉效果 |
|--------|---------|------------|---------|
| **HIGH** | `dashed` | `1.5` | 中等虚线 |
| **MED** | `dashed` | `1.0` | 普通虚线 |
| **LOW** | `dotted` | `0.7` | 点线 |
| **INFERRED** | `dotted` | `0.5` | 极细点线 |

```python
# 边置信度编码示例
def edge_style(confidence: str, is_annotation: bool = False) -> dict:
    if is_annotation:
        styles = {
            'HIGH':     {'style': 'dashed', 'penwidth': '1.5'},
            'MED':      {'style': 'dashed', 'penwidth': '1.0'},
            'LOW':      {'style': 'dotted', 'penwidth': '0.7'},
            'INFERRED': {'style': 'dotted', 'penwidth': '0.5'},
        }
    else:
        styles = {
            'HIGH':     {'style': 'solid',  'penwidth': '2.5'},
            'MED':      {'style': 'solid',  'penwidth': '1.5'},
            'LOW':      {'style': 'dashed', 'penwidth': '1.0'},
            'INFERRED': {'style': 'dotted', 'penwidth': '0.7'},
        }
    return styles.get(confidence, styles['MED'])
```

---

## 核心节点标注

- **权力中心**：`penwidth` 在置信度基础上 +0.5，`bold=True`
- **关键脆弱节点**：节点内标注 `🔗 关键连接点`
- **存在叙事竞争的节点**：节点内附加 `🔀`
- **INFERRED 节点**：节点内附加 `❓ INFERRED — [推断依据简述]`

---

## 边类型颜色

| 边类型 | 基底颜色 | 说明 |
|--------|---------|------|
| 贸易/投资 (trade_investment) | `#27ae60` 绿 | 经济关系 |
| 战争/冲突 (war_conflict) | `#cc4125` 红 | 军事对抗 |
| 资源控制 (resource_control) | `#e69138` 橙 | 战略资源 |
| 安全同盟 (security_alliance) | `#5b9bd5` 蓝 | 安全合作 |
| 代理关系 (proxy) | `#cc4125` 红 | 间接支持 |
| 竞争/对抗 (rivalry) | `#e74c3c` 深红 | 非军事对抗 |
| 条约框架 (treaty_framework) | `#6aa84f` 绿 | 正式协定（注释层） |
| 思想影响 (ideological_influence) | `#8e7cc3` 紫 | 意识形态（注释层） |
| 人事关联 (personnel_link) | `#b4b4b4` 灰 | 人员流动（注释层） |
| 时间轴 (timeline) | `#cccccc` 浅灰 | 时间连接 |

> ⚠️ 边的颜色由关系类型决定，线型（实/虚/点）和粗细由置信度决定。两者独立编码。

---

## 时间轴锚定

⚠️ 必须实现：
- 左侧使用 `plaintext` 节点作为时间刻度（如 1945, 1973, 1990s, 2001, 2010s, ...）
- 时间刻度之间用虚线连接：`style='dotted', arrowhead='none'`
- 使用 `rank=same` 子图约束：同一时代的事件/节点水平对齐

```python
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('E1973'); s.node('Oil_Crisis_1973'); s.node('OPEC_Power')
```

---

## Legend 子图 ⚠️

- 必须包含 `cluster_legend` 子图
- **必须包含的内容**：
  1. 所有节点类型 + 颜色含义
  2. ⚠️ **置信度图例**（核心）：展示 HIGH/MED/LOW/INFERRED 的边框和线型样例
  3. 主边 vs 注释层的视觉区分说明
  4. 边颜色含义（贸易=绿、冲突=红、资源=橙、同盟=蓝）
- 位置：图谱右下角

```python
with g.subgraph(name='cluster_legend') as legend:
    legend.attr(label='图例 Legend', style='solid', color='#333333',
                fontsize='12', fontname='Arial')

    # 节点类型示例
    legend.node('leg_faction', '政治派系', shape='box', fillcolor='#dae8fc',
                style='filled', fontsize='10')
    legend.node('leg_oligarch', '财阀集团', shape='box', fillcolor='#d5e8d4',
                style='filled,rounded', fontsize='10')
    # ... 其他节点类型

    # 置信度图例（核心！）
    legend.node('leg_high', 'HIGH 置信度', shape='box', fillcolor='white',
                style='bold', penwidth='2.5', fontsize='10')
    legend.node('leg_med', 'MED 置信度', shape='box', fillcolor='white',
                style='solid', penwidth='1.5', fontsize='10')
    legend.node('leg_low', 'LOW 置信度', shape='box', fillcolor='white',
                style='dashed', penwidth='1.2', fontsize='10')
    legend.node('leg_inferred', 'INFERRED', shape='box', fillcolor='white',
                style='dotted', penwidth='1.0', fontsize='10')
```

---

## 布局约束规范（Layout Constraints）

> [!CAUTION]
> Graphviz `dot` 引擎的节点位置完全由**边方向**和**rank 约束**决定。以下规则必须严格遵守。

### 1. 边方向规则（source → target = 上 → 下）

`rankdir=TB` 意味着**边的 source 在上方，target 在下方**。

| 边类型 | source（上方） | target（下方） | 语义 |
|--------|---------------|---------------|------|
| 安全同盟 (alliance) | 主导方 | 从属方 | 或用 `constraint=false` |
| 贸易/投资 | 资本输出方 | 资本接收方 | 或用 `constraint=false` |
| 战争/冲突 | 较早卷入方 | 较晚卷入方 | 或按权力层级 |
| 资源控制 | 控制方 | 依赖方 | 供应方在上 |
| 代理关系 | 幕后支持方 | 代理方 | 主从关系 |
| 思想影响 | 思想源头 | 受影响方 | 按时间/层级 |
| 条约框架 | 条约节点 | 签约方 | 或用 `constraint=false` |
| 人事关联 | 原组织 | 新组织 | 旋转门方向 |
| 时间轴 | 较早年份 | 较晚年份 | 时间正序 |

⚠️ **绝不允许反向连边**。如果语义上方向模糊（如双边贸易），使用 `dir=both` 或 `constraint=false`。

### 2. 阵营聚类（Cluster Subgraphs）

Phase 3 输出的 3-8 个阵营，每个阵营必须使用 `cluster_` 前缀的子图包裹：

```python
with g.subgraph(name='cluster_us_bloc') as c:
    c.attr(label='美国主导阵营', style='dashed', color='#3d85c6')
    c.node('US_MIC')
    c.node('NATO')
    # ... 该阵营的所有节点
```

### 3. Edge Weight / Constraint 设置

| 场景 | Graphviz 属性 | 效果 |
|------|--------------|------|
| 核心权力关系（骨架） | `weight=3` | 强制垂直对齐 |
| 次要利益关系 | `weight=2` | 次优先垂直对齐 |
| 跨阵营关联 | `constraint=false` | 不影响垂直 rank |
| 注释层关系 | `constraint=false` | 不影响主布局 |
| 时间轴→内容节点的隐形对齐边 | `style=invis, weight=0` | 辅助水平对齐 |
| 双边对等关系 | `constraint=false` | 避免强制一方在另一方上 |

### 4. 时间轴 Rank 锚定

```python
# 1) 时间轴节点串联
timeline_years = ['1945', '1973', '1990s', '2001', '2010s', '2020s']
for i in range(len(timeline_years) - 1):
    g.edge(timeline_years[i], timeline_years[i+1],
           style='dotted', arrowhead='none')

# 2) rank=same 绑定同时代节点
with g.subgraph() as s:
    s.attr(rank='same')
    s.node('1973')
    s.node('Oil_Crisis_1973')
    s.node('OPEC_Peak_Power')
```

### 5. 节点排列顺序

同一 `rank=same` 子图内的节点，dot 引擎按**代码中添加节点的顺序**从左到右排列。因此：
- 同一 rank 下，先添加核心行为体，再添加辅助行为体
- 按阵营 cluster 自然分组，避免视觉混乱

### 6. 调试 checklist

生成 SVG 后，必须检查以下布局问题：

- [ ] 核心权力关系是否形成清晰的上下层级？
- [ ] 同一阵营的节点是否在同一个 cluster 内？
- [ ] 时间轴是否从上到下递增？
- [ ] 是否有边穿越整个图谱造成视觉混乱？（如有 → 给该边加 `constraint=false`）
- [ ] Legend 是否与主图重叠？
- [ ] 置信度视觉编码是否正确（HIGH=粗实线，LOW=虚线，INFERRED=点线）？
- [ ] 主边和注释层是否有明确的视觉区分？
