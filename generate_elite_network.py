#!/usr/bin/env python3
"""
中东石油地缘政治精英网络图谱生成脚本
Geopolitical Elite Network: Middle East Oil Power (1973-2026)

Phase 0 确认参数:
  - 地理范围: 中东、波斯湾、北非、以色列-海湾、土耳其走廊
  - 时间范围: 1973-2026 (背景层1973-2000, 重点层2010-2026)
  - 分析粒度: 派系级
  - 节点: 35个
"""

import graphviz

# ──────────────────────────────────────────
# 置信度视觉规范 (confidence_spec)
# HIGH:     solid, penwidth=2.5
# MED:      solid, penwidth=1.5
# LOW:      dashed, penwidth=1.2
# INFERRED: dotted, penwidth=0.8
# ──────────────────────────────────────────

def conf_node_style(level):
    """节点边框置信度编码"""
    return {
        "HIGH":     {"style": "filled,solid",   "penwidth": "2.5"},
        "MED":      {"style": "filled,solid",   "penwidth": "1.5"},
        "LOW":      {"style": "filled,dashed",  "penwidth": "1.2"},
        "INFERRED": {"style": "filled,dotted",  "penwidth": "0.8"},
    }[level]

def conf_edge_style(level):
    """边置信度编码"""
    return {
        "HIGH":     {"style": "solid",  "penwidth": "2.5"},
        "MED":      {"style": "solid",  "penwidth": "1.5"},
        "LOW":      {"style": "dashed", "penwidth": "1.0"},
        "INFERRED": {"style": "dotted", "penwidth": "0.7"},
    }[level]

# ──────────────────────────────────────────
# 节点颜色 (visual_spec — 按行为体类型)
# ──────────────────────────────────────────
COLORS = {
    "state_elite":      "#1A3A5C",   # 深蓝 — 国家精英派系
    "militia_proxy":    "#8B0000",   # 深红 — 非国家代理武装
    "intl_org":         "#2E5E3F",   # 深绿 — 国际组织/多边机制
    "corp_national":    "#5C4A1A",   # 深棕 — 国家石油企业
    "corp_western":     "#4A1A5C",   # 深紫 — 西方石油巨头
    "chokepoint":       "#1A5C5C",   # 深青 — 战略通道/节点
    "ideology":         "#5C5C1A",   # 橄榄 — 意识形态/思想谱系节点
    "timeline":         "#F0F0F0",   # 时间线节点 (浅灰)
}
FONT_COLOR = "#FFFFFF"              # 白色字体 (深色节点)
FONT_COLOR_DARK = "#333333"         # 深色字体 (浅色节点)

# ──────────────────────────────────────────
# 时代纪元定义 (Temporal Era Segmentation)
# ──────────────────────────────────────────
ERAS = [
    {"id": "era1", "label": "七姐妹时代 (1945-1973)",     "range": [1945, 1973],
     "desc": "西方石油垄断；中东国家尚未掌握定价权"},
    {"id": "era2", "label": "石油武器时代 (1973-2000)",     "range": [1973, 2000],
     "desc": "OPEC崛起；两次石油危机；海湾战争"},
    {"id": "era3", "label": "多极博弈时代 (2000-2020)",     "range": [2000, 2020],
     "desc": "页岩革命；中国崛起为第一大买家；阿拉伯之春"},
    {"id": "era4", "label": "新秩序时代 (2020-2026)",       "range": [2020, 2026],
     "desc": "价格战；红海危机；沙伊复交；去美元化探索"},
]

# ──────────────────────────────────────────
# 节点数据 (Phase 3 置信度审计后)
# 格式: (id, label, type, confidence, note, era)
#   era: 该节点活跃的纪元列表
# ──────────────────────────────────────────
NODES = [
    # ── 海湾国家精英派系 ──
    ("SA_MBS",    "沙特王室\n（MBS派系）\n+ 公共投资基金PIF",  "state_elite", "HIGH",
     "♟ Vision2030核心；控制Aramco；OPEC实际主导方",
     ["era3", "era4"]),
    ("SA_ARAMCO", "沙特阿拉伯\n国家石油公司\nAramco",          "corp_national","HIGH",
     "♟ 全球最大石油公司；估值最高时超2万亿美元",
     ["era2", "era3", "era4"]),
    ("UAE_MBZ",   "阿联酋\n（MBZ网络）\n+ ADNOC",            "state_elite", "HIGH",
     "♟ 亚伯拉罕协议签署方；主权财富基金ADQ/Mubadala",
     ["era3", "era4"]),
    ("QA_FUND",   "卡塔尔\n（埃米尔派系）\n+ QIA + 半岛电视台","state_elite", "HIGH",
     "♟ 全球最大LNG出口国；软实力网络",
     ["era3", "era4"]),
    ("KW_GOVT",   "科威特政府\n+ KPC",                       "state_elite", "MED",
     "♟ 重要OPEC成员；2020价格战缓冲方",
     ["era2", "era3", "era4"]),
    ("IQ_GOVT",   "伊拉克政府\n（巴格达派系）",               "state_elite", "MED",
     "♟ OPEC第二大产油国；受PMF影响严重",
     ["era1", "era2", "era3", "era4"]),

    # ── 伊朗体系 ──
    ("IR_SL",     "伊朗\n最高领袖办公室\n（哈梅内伊体系）",   "state_elite", "HIGH",
     "♟ IRGC最高指挥权；\"抵抗轴心\"总设计师",
     ["era2", "era3", "era4"]),
    ("IR_IRGC",   "伊朗革命卫队\n（IRGC）\n+ 圣城军Quds Force","militia_proxy","HIGH",
     "♟ 经济帝国+代理战争调度器；控制Khatam al-Anbiya",
     ["era2", "era3", "era4"]),
    ("HOUTHI",    "也门胡塞武装\n（安萨尔真主）",             "militia_proxy","HIGH",
     "♟ 控制曼德海峡；2023-2025红海袭击",
     ["era3", "era4"]),  # 2014入萨那(era3)及2023红海(era4)
    ("PMF_IQ",    "伊拉克\n人民动员力量PMF\n（亲伊朗派系）",  "militia_proxy","HIGH",
     "♟ 控制部分油田和炼油厂；走私网络",
     ["era3", "era4"]),
    ("HEZBOLLAH", "黎巴嫩真主党\n+ Al-Amana能源网络",        "militia_proxy","HIGH",
     "♟ 伊朗石油黎巴嫩中转；年收入约$7亿（美估值）",
     ["era2", "era3", "era4"]),

    # ── 俄罗斯体系 ──
    ("RU_KREMLIN","俄罗斯\n（克宫能源外交）\n+ Rosneft",      "state_elite", "HIGH",
     "♟ OPEC+共同主导方；制裁后重组出口路线",
     ["era2", "era3", "era4"]),

    # ── 美国体系 ──
    ("US_SHALE",  "美国\n页岩油集团\n（德州-华盛顿轴）",     "state_elite", "HIGH",
     "♟ 2019成全球最大产油国；IEA主要推力",
     ["era3", "era4"]),
    ("US_CENTCOM","美国中央司令部\n（CENTCOM）",              "state_elite", "HIGH",
     "♟ 波斯湾军事保护伞；第5舰队巴林",
     ["era2", "era3", "era4"]),

    # ── 中国体系 ──
    ("CN_NOC",    "中国国家石油企业\n中石油/中石化/中海油",   "corp_national","HIGH",
     "♟ 中东第一大石油买家；BRI能源投资2024达$390亿",
     ["era3", "era4"]),

    # ── 以色列 ──
    ("IL_GOVT",   "以色列政府\n（内塔尼亚胡派系）",           "state_elite", "HIGH",
     "♟ 亚伯拉罕协议；CENTCOM区责；加沙战争后外交搁置",
     ["era3", "era4"]),

    # ── 土耳其体系 ──
    ("TR_ERDOGAN","土耳其\n（埃尔多安政府）\n能源枢纽战略",   "state_elite", "MED",
     "♟ Kirkuk-Ceyhan管道；土耳其海峡；BTC管道",
     ["era3", "era4"]),

    # ── 多边机制 ──
    ("OPEC_PLUS", "OPEC+\n多边生产配额机制",                 "intl_org",    "HIGH",
     "♟ 沙俄联合主导；调节全球约40%石油供给",
     ["era2", "era3", "era4"]),
    ("IEA",       "国际能源署IEA\n（西方消费国集团）",        "intl_org",    "HIGH",
     "♟ 全球战略储备协调；与OPEC博弈",
     ["era2", "era3", "era4"]),

    # ── 西方油企 ──
    ("MAJORS_W",  "西方石油巨头\nExxon/BP/Shell\n/TotalEnergies","corp_western","HIGH",
     "♟ 中东开采合同；逐步被国家油企替代",
     ["era1", "era2", "era3", "era4"]),

    # ── 非洲产油国 ──
    ("LY_CHAOS",  "利比亚\n（碎片化政权）\n+ NOC",           "state_elite", "MED",
     "♟ OPEC豁免生产；欧洲主要供应方；2025产量十年高峰",
     ["era3", "era4"]),
    ("NG_GOVT",   "尼日利亚政府\n+ NNPC",                    "state_elite", "MED",
     "♟ 非洲最大产油国；尼日尔三角洲安全复杂",
     ["era2", "era3", "era4"]),

    # ── 战略通道节点 ──
    ("HORMUZ",    "霍尔木兹海峡\n（波斯湾咽喉）",             "chokepoint",  "HIGH",
     "🚢 全球石油流量~21%；伊朗封锁威胁",
     ["era1", "era2", "era3", "era4"]),
    ("BAB_MAND",  "曼德海峡\n（红海入口）",                   "chokepoint",  "HIGH",
     "🚢 胡塞袭击中心；全球贸易~12%绕行",
     ["era1", "era2", "era3", "era4"]),
    ("SUEZ",      "苏伊士运河\n（埃及控制）",                 "chokepoint",  "HIGH",
     "🚢 中东→欧洲最短海路；2021Ever Given事件",
     ["era1", "era2", "era3", "era4"]),
    ("BTC_PIPE",  "BTC管道\n（巴库-第比利斯-杰伊汉）",        "chokepoint",  "MED",
     "🚢 里海油绕俄输欧；土耳其通道杠杆",
     ["era2", "era3", "era4"]),

    # ── 意识形态节点 ──
    ("WAHHABISM", "瓦哈比主义\n国家意识形态输出",             "ideology",    "MED",
     "💡 沙特通过伊斯兰合作组织输出；与伊朗什叶主义竞争",
     ["era1", "era2", "era3", "era4"]),
    ("SHIA_CRES", "什叶新月意识形态\n（伊朗版本）",            "ideology",    "MED",
     "💡 伊拉克→叙利亚→黎巴嫩轴线；抵抗轴心意识形态基础",
     ["era2", "era3", "era4"]),

    # ── 历史背景层节点 ──
    ("ARAMCO_HIST","七姐妹时代\n（美英石油垄断）\n1945-1973背景层","ideology", "HIGH",
     "📜 历史：西方主导被1973危机打断",
     ["era1"]),
    ("OPEC_1973", "OPEC石油禁运\n（1973-1974）\n背景层",      "ideology",    "HIGH",
     "📜 历史：第一次\"石油武器\"；重塑全球经济秩序",
     ["era1", "era2"]),
]

# ──────────────────────────────────────────
# 边数据 (Phase 3 置信度审计后)
# 格式: (from, to, label, confidence, direction, note, era)
#   label: dict — 按纪元拆分的事件描述 {"era1": "...", "era2": "...", ...}
#          或 str — 不区分纪元的通用描述（向后兼容）
#   era: 该关系活跃的纪元列表
# ──────────────────────────────────────────
EDGES = [
    # ── 定价权轴线 (OPEC+核心) ──
    ("SA_MBS",    "OPEC_PLUS",
     {"era3": "2016主导OPEC+减产协议", "era4": "2020史诗级减产970万桶/日 · 2024延长自愿减产至Q1'25"},
     "HIGH", "both",    "", ["era3", "era4"]),
    ("RU_KREMLIN","OPEC_PLUS",
     {"era3": "2016加入OPEC+联盟", "era4": "2020沙俄价格战→3月协议 · 2024制裁下维持配额合作"},
     "HIGH", "both",    "", ["era3", "era4"]),
    ("UAE_MBZ",   "OPEC_PLUS",
     {"era3": "参与OPEC+减产框架", "era4": "2021争取更高基准配额 · 2024扩产能至500万桶/日目标"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("QA_FUND",   "OPEC_PLUS",
     {"era3": "OPEC成员国参与配额", "era4": "2019退出OPEC转LNG · 仍参与OPEC+协调机制"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("IQ_GOVT",   "OPEC_PLUS",
     {"era2": "1960创始成员国", "era3": "配额合规率长期偏低", "era4": "2024合规率仅~65% · 超产争议"},
     "MED",  "forward", "", ["era2", "era3", "era4"]),
    ("OPEC_PLUS", "IEA",
     {"era3": "供需信息博弈", "era4": "2022 IEA协调释放6000万桶储备 · 2023定价权拉锯战"},
     "HIGH", "both",    "", ["era3", "era4"]),
    ("US_SHALE",  "IEA",
     {"era3": "2015页岩油使美成净出口国", "era4": "2022 SPR释放1.8亿桶 · 西方能源安全支柱"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("US_SHALE",  "OPEC_PLUS",
     {"era3": "2014页岩革命冲击油价", "era4": "2020产量战相互消耗 · 2024美产1300万桶/日纪录"},
     "HIGH", "forward", "", ["era3", "era4"]),

    # ── 石油公司关系 ──
    ("SA_MBS",    "SA_ARAMCO",
     {"era3": "国家100%战略控制", "era4": "2019 Aramco IPO(1.7万亿估值) · 2024重组下游扩张"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("SA_ARAMCO", "OPEC_PLUS",
     {"era3": "产量数据核心支撑", "era4": "闲置产能全球最大(~200万桶/日)"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("UAE_MBZ",   "SA_ARAMCO",
     {"era3": "ADNOC vs Aramco区域竞争", "era4": "2023 ADNOC产能450万桶/日 · 下游石化投资角力"},
     "MED",  "both",    "", ["era3", "era4"]),
    ("CN_NOC",    "SA_ARAMCO",
     {"era3": "石油长约买方关系建立", "era4": "2023中石化长约50年合作 · 2024对华出口170万桶/日"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("CN_NOC",    "IQ_GOVT",
     {"era3": "中石油鲁迈拉油田(2009-)", "era4": "2023中企伊拉克投资超$200亿 · 最大外国油企投资者"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("CN_NOC",    "IR_IRGC",
     {"era3": "制裁灰色渠道采购", "era4": "2021中伊25年合作协议 · 2024进口伊朗油~150万桶/日"},
     "MED",  "forward", "", ["era3", "era4"]),
    ("MAJORS_W",  "IQ_GOVT",
     {"era1": "1928-1972 IPC特许权时期 · 西方垄断伊拉克开采权",
      "era3": "BP鲁迈拉/Exxon西古尔纳",
      "era4": "2023 TotalEnergies $270亿天然气项目 · 战后重建合同"},
     "HIGH", "forward", "", ["era1", "era3", "era4"]),
    ("MAJORS_W",  "SA_ARAMCO",
     {"era2": "1973部分国有化 · 1988 Aramco完全国有化", "era3": "技术合作合同递减"},
     "MED",  "forward", "", ["era2", "era3"]),
    ("RU_KREMLIN","CN_NOC",
     {"era4": "2022制裁后管道对华扩至200万桶/日 · 2024中俄能源贸易$700亿+ · 人民币结算占比↑"},
     "HIGH", "forward", "", ["era4"]),

    # ── 伊朗代理网络（抵抗轴心）──
    ("IR_SL",     "IR_IRGC",
     {"era2": "1979革命卫队成立 · 最高领袖直接指挥权", "era3": "IRGC经济帝国扩张", "era4": "2020苏莱曼尼遇刺后重组"},
     "HIGH", "forward", "", ["era2", "era3", "era4"]),
    ("IR_IRGC",   "HOUTHI",
     {"era3": "2014胡塞武装夺萨那 · 提供无人机/反舰导弹技术", "era4": "2024红海袭击军事支援"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("IR_IRGC",   "PMF_IQ",
     {"era3": "2014 PMF成立(反ISIS) · 伊朗系指挥官渗透", "era4": "2024超15万民兵准军事化"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("IR_IRGC",   "HEZBOLLAH",
     {"era2": "1982创建真主党", "era3": "$7亿+/年资金+武器", "era4": "2024以黎冲突升级"},
     "HIGH", "forward", "", ["era2", "era3", "era4"]),
    ("PMF_IQ",    "IQ_GOVT",
     {"era3": "2016 PMF合法化(国会法案)", "era4": "渗透议会/内政部 · 准国家暴力垄断"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("PMF_IQ",    "SA_ARAMCO",
     {"era4": "2019无人机袭击Abqaiq设施 · 威胁沙特东部油田安全"},
     "LOW",  "forward", "", ["era4"]),
    ("HEZBOLLAH", "IR_IRGC",
     {"era3": "伊朗油经叙利亚→黎巴嫩分销", "era4": "2024战后经济困境加深依赖"},
     "HIGH", "forward", "", ["era3", "era4"]),

    # ── 曼德海峡/红海封锁 ──
    ("HOUTHI",    "BAB_MAND",
     {"era4": "2023.11起袭击商船200+次 · 反舰导弹+无人艇+无人机 · 全球贸易12%绕行好望角"},
     "HIGH", "forward", "", ["era4"]),
    ("BAB_MAND",  "SUEZ",
     {"era4": "2024红海危机→苏伊士通行量↓45% · 运费飙升300%+ · 航运保险费暴涨"},
     "HIGH", "both",    "", ["era4"]),
    ("US_CENTCOM","HOUTHI",
     {"era4": "2024.1繁荣卫士行动(OPG) · 空袭也门胡塞据点 · 多国海军护航联盟"},
     "HIGH", "forward", "", ["era4"]),
    ("SA_MBS",    "HOUTHI",
     {"era3": "2015沙特联军介入也门", "era4": "2023停火谈判推进 · 也门和平路线图磋商"},
     "HIGH", "forward", "", ["era3", "era4"]),

    # ── 战略通道控制 ──
    ("IR_IRGC",   "HORMUZ",
     {"era2": "1988油轮战争先例", "era3": "2019扣押英国油轮", "era4": "持续封锁威胁21%全球油运"},
     "HIGH", "forward", "", ["era2", "era3", "era4"]),
    ("US_CENTCOM","HORMUZ",
     {"era2": "1987护航行动开始 · 第五舰队常驻巴林", "era3": "持续自由航行巡逻", "era4": "霍尔木兹分舰队常态化部署"},
     "HIGH", "forward", "", ["era2", "era3", "era4"]),
    ("TR_ERDOGAN","SUEZ",
     {"era3": "Kirkuk-Ceyhan管道替代方案", "era4": "2014后库区石油独立出口争议"},
     "MED",  "forward", "", ["era3", "era4"]),
    ("TR_ERDOGAN","BTC_PIPE",
     {"era3": "2006 BTC管道投运 · 里海油经土耳其输欧", "era4": "通道税收/地缘杠杆持续"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("BTC_PIPE",  "HORMUZ",
     {"era2": "1990s设计绕俄绕伊替代通道", "era3": "里海油避开霍尔木兹风险"},
     "MED",  "both",    "", ["era2", "era3"]),

    # ── 以色列-海湾对齐 ──
    ("IL_GOVT",   "UAE_MBZ",
     {"era4": "2020亚伯拉罕协议签署 · 2024双边贸易$30亿+ · 情报/科技/军事合作"},
     "HIGH", "both",    "", ["era4"]),
    ("IL_GOVT",   "SA_MBS",
     {"era4": "2023正常化谈判(10.7前) · 2024加沙战争后搁置 · 非正式安全情报渠道持续"},
     "MED",  "both",    "", ["era4"]),
    ("US_CENTCOM","IL_GOVT",
     {"era3": "铁穹/F-35武器供应", "era4": "2021以色列入CENTCOM区责 · 2024加沙军事支持"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("SA_MBS",    "IL_GOVT",
     {"era4": "2023美斡旋正常化框架 · 10.7后MBS搁置谈判 · 条件:巴勒斯坦建国路径"},
     "MED",  "both",    "", ["era4"]),

    # ── 沙伊博弈 ──
    ("SA_MBS",    "IR_SL",
     {"era4": "2023.3中国调解沙伊复交 · 2016断交→2023恢复外交 · 战略对冲/降温信号"},
     "HIGH", "both",    "", ["era4"]),
    ("SA_MBS",    "IR_IRGC",
     {"era3": "2015也门代理战争对抗", "era4": "2019 Aramco遇袭(伊朗关联) · 双边对抗持续"},
     "HIGH", "both",    "", ["era3", "era4"]),
    ("IR_SL",     "QA_FUND",
     {"era3": "什叶-逊尼叙事竞争 · 半岛电视台信息战", "era4": "2017断交危机(沙特指控亲伊)"},
     "INFERRED","both","", ["era3", "era4"]),

    # ── 中国地缘利益 ──
    ("CN_NOC",    "QA_FUND",
     {"era4": "2022 QatarEnergy-中石化27年LNG合同 · 400万吨/年($600亿+) · 最大单笔LNG长约"},
     "HIGH", "forward", "", ["era4"]),
    ("CN_NOC",    "UAE_MBZ",
     {"era3": "2018 ADNOC股权投资", "era4": "2024中国进口阿联酋油~60万桶/日 · 石化联合投资"},
     "HIGH", "forward", "", ["era3", "era4"]),
    ("SA_MBS",    "CN_NOC",
     {"era4": "2023首笔人民币结算LNG · 沙特→中国原油$500亿/年 · 去美元化试探"},
     "MED",  "forward", "", ["era4"]),

    # ── 非洲节点 ──
    ("LY_CHAOS",  "OPEC_PLUS",
     {"era3": "2011内战后产量崩溃", "era4": "2024恢复至120万桶/日 · 豁免配额参与"},
     "MED",  "forward", "", ["era3", "era4"]),
    ("NG_GOVT",   "OPEC_PLUS",
     {"era2": "1971加入OPEC", "era3": "长期配额合规成员", "era4": "2024产量~150万桶/日"},
     "HIGH", "forward", "", ["era2", "era3", "era4"]),
    ("MAJORS_W",  "LY_CHAOS",
     {"era3": "2004制裁解除后重返 · 2011内战撤出→2017部分回归", "era4": "ENI/BP油田开发"},
     "MED",  "forward", "", ["era3", "era4"]),

    # ── 意识形态层 ──
    ("WAHHABISM", "SA_MBS",
     {"era3": "瓦哈比意识形态国家输出", "era4": "MBS 2017后削弱宗教警察权力 · 愿景2030世俗化转型"},
     "MED",  "forward", "", ["era3", "era4"]),
    ("SHIA_CRES", "IR_IRGC",
     {"era2": "1979革命输出什叶意识形态", "era3": "伊拉克→叙利亚→黎巴嫩轴线", "era4": "抵抗轴心意识形态基础"},
     "HIGH", "forward", "", ["era2", "era3", "era4"]),
    ("OPEC_1973", "OPEC_PLUS",
     {"era2": "1973石油禁运→价格四倍 · 重塑全球能源秩序 · →演化为OPEC+机制"},
     "HIGH", "forward", "", ["era2"]),
    ("ARAMCO_HIST","SA_ARAMCO",
     {"era1": "1933美沙特许权协议 · 七姐妹完全控制", "era2": "1973部分国有化 · 1988完全国有化→Saudi Aramco"},
     "HIGH", "forward", "", ["era1", "era2"]),

    # ── 七姐妹时代 (era1) 补充核心关系 ──
    ("MAJORS_W",  "SUEZ",
     {"era1": "1956苏伊士危机前西方资本控制 · 战后欧洲石油供应生命线"},
     "HIGH", "both",    "", ["era1"]),
    ("MAJORS_W",  "ARAMCO_HIST",
     {"era1": "1933-1973特许权时期 · Exxon/Mobil/Chevron/Texaco完全控制产量定价"},
     "HIGH", "forward", "", ["era1"]),
    ("WAHHABISM", "ARAMCO_HIST",
     {"era1": "1945大苦湖会晤确立\"石油换安全\" · 意识形态与能源利益早期绑定"},
     "HIGH", "forward", "", ["era1"]),
    ("MAJORS_W",  "HORMUZ",
     {"era1": "1971年前属英国势力范围/保护国 · 西方油轮绝对主导航权"},
     "HIGH", "forward", "", ["era1"]),
]

# ──────────────────────────────────────────
# 阵营分组数据 (供 HTML Viewer 复合节点使用)
# ──────────────────────────────────────────
GROUPS = [
    {"id": "grp_gulf",     "label": "🛢️ 海湾产油轴（沙特主导）",    "color": "#1A3A5C", "bg": "#EBF5FB",
     "members": ["SA_MBS","SA_ARAMCO","UAE_MBZ","QA_FUND","KW_GOVT"]},
    {"id": "grp_iran",     "label": "☪️ 伊朗抵抗轴心（什叶弧）",    "color": "#8B0000", "bg": "#FDEDEC",
     "members": ["IR_SL","IR_IRGC","HOUTHI","PMF_IQ","HEZBOLLAH"]},
    {"id": "grp_powers",   "label": "🌍 大国外部介入（美/俄/中）",  "color": "#2E5E3F", "bg": "#EAF7EF",
     "members": ["US_SHALE","US_CENTCOM","RU_KREMLIN","CN_NOC"]},
    {"id": "grp_choke",    "label": "🚢 战略咽喉节点",             "color": "#1A5C5C", "bg": "#EAF7F7",
     "members": ["HORMUZ","BAB_MAND","SUEZ","BTC_PIPE"]},
    {"id": "grp_multi",    "label": "⚖️ 多边机制",                 "color": "#2E5E3F", "bg": "#F0FFF0",
     "members": ["OPEC_PLUS","IEA"]},
    {"id": "grp_periph",   "label": "🔷 区域外围玩家",             "color": "#444488", "bg": "#F5F5FF",
     "members": ["IL_GOVT","TR_ERDOGAN","LY_CHAOS","NG_GOVT","MAJORS_W"]},
    {"id": "grp_ideology", "label": "📜 意识形态 / 历史背景层",     "color": "#8B7355", "bg": "#FAFAF0",
     "members": ["WAHHABISM","SHIA_CRES","OPEC_1973","ARAMCO_HIST"]},
]

# ──────────────────────────────────────────
# 主图构建
# ──────────────────────────────────────────
dot = graphviz.Digraph(
    name="MiddleEastOilEliteNetwork",
    engine="dot",
    graph_attr={
        "bgcolor":    "white",
        "fontname":   "Arial",
        "fontsize":   "11",
        "label":      "中东石油地缘政治精英网络图谱 (1973-2026)\nMiddle East Oil Geopolitical Elite Network | Phase: Faction Level | © 2026",
        "labelloc":   "t",
        "labeljust":  "c",
        "fontsize":   "14",
        "rankdir":    "TB",
        "dpi":        "150",
        "nodesep":    "0.7",
        "ranksep":    "1.2",
        "splines":    "ortho",
        "overlap":    "false",
    },
    node_attr={
        "fontname":  "Arial",
        "fontsize":  "9",
        "fontcolor": FONT_COLOR,
        "shape":     "box",
        "margin":    "0.15,0.1",
        "width":     "1.8",
    },
    edge_attr={
        "fontname":    "Arial",
        "fontsize":    "7.5",
        "fontcolor":   "#222222",
        "arrowsize":   "0.7",
        "labelfloat":  "true",
        "decorate":    "false",
    }
)

# ──────────────────────────────────────────
# 添加节点
# ──────────────────────────────────────────
for nid, label, ntype, conf, note, *_ in NODES:
    color = COLORS.get(ntype, "#333333")
    ns = conf_node_style(conf)
    # 历史背景层节点使用不同底色
    if ntype == "ideology" and ("背景层" in label or "历史" in label or "七姐妹" in label or "1973" in label):
        fc = FONT_COLOR_DARK
        bg = "#F5F0E8"
        border = "#8B7355"
    elif ntype == "chokepoint":
        fc = FONT_COLOR
        bg = "#1A5C5C"
        border = "#0D3333"
    elif ntype == "ideology":
        fc = FONT_COLOR
        bg = "#5C5C1A"
        border = "#3D3D10"
    elif ntype == "timeline":
        fc = FONT_COLOR_DARK
        bg = "#F0F0F0"
        border = "#AAAAAA"
    else:
        fc = FONT_COLOR
        bg = color
        border = "#000000"

    dot.node(
        nid,
        label=label,
        fillcolor=bg,
        color=border,
        fontcolor=fc,
        **ns,
    )

# ──────────────────────────────────────────
# 添加边
# ──────────────────────────────────────────
def edge_label_flat(label):
    """将 label (str 或 dict) 展平为单一字符串，用于 Graphviz/tooltip"""
    if isinstance(label, dict):
        return "\n".join(label.values())
    return label

for src, dst, label, conf, direction, note, *_ in EDGES:
    es = conf_edge_style(conf)
    arrow_dir = "both" if direction == "both" else "forward"
    color_map = {
        "HIGH":     "#CC2222",  # 红
        "MED":      "#1A5296",  # 蓝
        "LOW":      "#888888",  # 灰
        "INFERRED": "#AAAAAA",  # 浅灰
    }
    # 使用 xlabel（外部标签）确保标签紧贴对应边，避免 splines 错位问题
    dot.edge(
        src, dst,
        xlabel=edge_label_flat(label),
        dir=arrow_dir,
        color=color_map[conf],
        fontcolor=color_map[conf],  # 标签与边同色，更易对应
        **es,
    )

# ──────────────────────────────────────────
# 聚类子图（阵营分组）
# ──────────────────────────────────────────

# 阵营1: 海湾产油轴 (沙特主导联盟)
with dot.subgraph(name="cluster_gulf_axis") as c:
    c.attr(
        label="🛢️ 海湾产油轴（沙特主导）",
        style="rounded,filled", fillcolor="#EBF5FB",
        color="#1A3A5C", penwidth="2"
    )
    for n in ["SA_MBS","SA_ARAMCO","UAE_MBZ","QA_FUND","KW_GOVT"]:
        c.node(n)

# 阵营2: 伊朗抵抗轴心
with dot.subgraph(name="cluster_iran_axis") as c:
    c.attr(
        label="☪️ 伊朗抵抗轴心（什叶弧）",
        style="rounded,filled", fillcolor="#FDEDEC",
        color="#8B0000", penwidth="2"
    )
    for n in ["IR_SL","IR_IRGC","HOUTHI","PMF_IQ","HEZBOLLAH"]:
        c.node(n)

# 阵营3: 大国外部势力
with dot.subgraph(name="cluster_great_powers") as c:
    c.attr(
        label="🌍 大国外部介入（美/俄/中）",
        style="rounded,filled", fillcolor="#EAF7EF",
        color="#2E5E3F", penwidth="2"
    )
    for n in ["US_SHALE","US_CENTCOM","RU_KREMLIN","CN_NOC"]:
        c.node(n)

# 阵营4: 战略通道节点
with dot.subgraph(name="cluster_chokepoints") as c:
    c.attr(
        label="🚢 战略咽喉节点",
        style="rounded,dashed", fillcolor="#EAF7F7",
        color="#1A5C5C", penwidth="1.5"
    )
    for n in ["HORMUZ","BAB_MAND","SUEZ","BTC_PIPE"]:
        c.node(n)

# 阵营5: 多边机制
with dot.subgraph(name="cluster_multilateral") as c:
    c.attr(
        label="⚖️ 多边机制",
        style="rounded,filled", fillcolor="#F0FFF0",
        color="#2E5E3F", penwidth="1.5"
    )
    for n in ["OPEC_PLUS","IEA"]:
        c.node(n)

# 阵营6: 以色列-土耳其-区域外围
with dot.subgraph(name="cluster_periphery") as c:
    c.attr(
        label="🔷 区域外围玩家",
        style="rounded,filled", fillcolor="#F5F5FF",
        color="#444488", penwidth="1.5"
    )
    for n in ["IL_GOVT","TR_ERDOGAN","LY_CHAOS","NG_GOVT","MAJORS_W"]:
        c.node(n)

# 阵营7: 意识形态/历史层
with dot.subgraph(name="cluster_ideology") as c:
    c.attr(
        label="📜 意识形态 / 历史背景层",
        style="rounded,dashed", fillcolor="#FAFAF0",
        color="#8B7355", penwidth="1"
    )
    for n in ["WAHHABISM","SHIA_CRES","OPEC_1973","ARAMCO_HIST"]:
        c.node(n)

# ──────────────────────────────────────────
# Legend 图例子图
# ──────────────────────────────────────────
with dot.subgraph(name="cluster_legend") as leg:
    leg.attr(
        label="📊 图例 Legend",
        style="rounded,filled", fillcolor="#FAFAFA",
        color="#444444", penwidth="1.5",
        fontsize="10"
    )
    # 节点类型图例
    leg.node("L_state",    "国家精英派系",   shape="box", style="filled,solid",
             fillcolor=COLORS["state_elite"],    fontcolor=FONT_COLOR, penwidth="1.5", width="1.5")
    leg.node("L_militia",  "代理武装",       shape="box", style="filled,solid",
             fillcolor=COLORS["militia_proxy"], fontcolor=FONT_COLOR, penwidth="1.5", width="1.5")
    leg.node("L_intl",     "多边机制",       shape="box", style="filled,solid",
             fillcolor=COLORS["intl_org"],       fontcolor=FONT_COLOR, penwidth="1.5", width="1.5")
    leg.node("L_corp_n",   "国家石油公司",   shape="box", style="filled,solid",
             fillcolor=COLORS["corp_national"],  fontcolor=FONT_COLOR, penwidth="1.5", width="1.5")
    leg.node("L_corp_w",   "西方油企",       shape="box", style="filled,solid",
             fillcolor=COLORS["corp_western"],   fontcolor=FONT_COLOR, penwidth="1.5", width="1.5")
    leg.node("L_choke",    "战略通道",       shape="box", style="filled,solid",
             fillcolor=COLORS["chokepoint"],     fontcolor=FONT_COLOR, penwidth="1.5", width="1.5")

    # 置信度图例
    leg.node("LH", "HIGH\n3+来源交叉验证",  shape="box", style="filled,solid",  penwidth="2.5",
             fillcolor="#DDFFDD", fontcolor="#333333", width="1.5")
    leg.node("LM", "MED\n2个独立来源",       shape="box", style="filled,solid",  penwidth="1.5",
             fillcolor="#DDDDFF", fontcolor="#333333", width="1.5")
    leg.node("LL", "LOW\n1个来源/有偏差",    shape="box", style="filled,dashed", penwidth="1.2",
             fillcolor="#FFEECC", fontcolor="#333333", width="1.5")
    leg.node("LI", "INFERRED\n行为模式推断", shape="box", style="filled,dotted", penwidth="0.8",
             fillcolor="#FFDDDD", fontcolor="#333333", width="1.5")

    # 置信度边图例（使用 xlabel，与正文边保持一致）
    leg.edge("LH","LM", xlabel="HIGH边(红实线粗)", style="solid",  penwidth="2.5", color="#CC2222",  fontcolor="#CC2222")
    leg.edge("LM","LL", xlabel="MED边(蓝实线)",   style="solid",  penwidth="1.5", color="#1A5296",  fontcolor="#1A5296")
    leg.edge("LL","LI", xlabel="LOW边(灰虚线)",   style="dashed", penwidth="1.0", color="#888888",  fontcolor="#888888")
    leg.edge("LI","LH", xlabel="INFERRED(点线)",  style="dotted", penwidth="0.7", color="#AAAAAA",  fontcolor="#AAAAAA",
             dir="forward", constraint="false")

# ──────────────────────────────────────────
# export_html() — 生成交互式 HTML 查看器
# ──────────────────────────────────────────

import json
import os

def export_html(output_base, title, nodes, edges, colors, groups, eras=None):
    """
    将图谱数据注入 viewer_template.html，输出独立 HTML 文件。
    Cytoscape.js 库从本地 cytoscape.min.js 内联进 HTML，
    确保完全离线可用。
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "viewer_template.html")
    cytoscape_path = os.path.join(script_dir, "cytoscape.min.js")

    # ── 读取模板 ──
    if not os.path.exists(template_path):
        print(f"⚠️  未找到 viewer_template.html，跳过 HTML 生成")
        return
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # ── 读取 Cytoscape.js 库（内联） ──
    if not os.path.exists(cytoscape_path):
        print(f"⚠️  未找到 cytoscape.min.js，尝试下载...")
        import urllib.request
        url = "https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"
        try:
            urllib.request.urlretrieve(url, cytoscape_path)
            print(f"✅ 已下载 cytoscape.min.js")
        except Exception as e:
            print(f"❌ 下载失败: {e}。请手动放置 cytoscape.min.js 到脚本目录。")
            return
    with open(cytoscape_path, "r", encoding="utf-8") as f:
        cytoscape_js = f.read()

    # ── 序列化数据 ──
    nodes_json = json.dumps(
        [{"id": n[0], "label": n[1], "type": n[2], "confidence": n[3], "note": n[4],
          "era": n[5] if len(n) > 5 else []}
         for n in nodes],
        ensure_ascii=False, indent=None
    )
    edges_json = json.dumps(
        [{"source": e[0], "target": e[1], "label": e[2], "confidence": e[3],
          "era": e[6] if len(e) > 6 else []}
         for e in edges],
        ensure_ascii=False, indent=None
    )
    colors_json = json.dumps(colors, ensure_ascii=False, indent=None)
    groups_json = json.dumps(groups, ensure_ascii=False, indent=None)
    eras_json = json.dumps(eras, ensure_ascii=False, indent=None)

    # ── 替换占位符 ──
    html = template
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{CYTOSCAPE_JS}}", cytoscape_js)
    html = html.replace("{{NODES_JSON}}", nodes_json)
    html = html.replace("{{EDGES_JSON}}", edges_json)
    html = html.replace("{{COLORS_JSON}}", colors_json)
    html = html.replace("{{GROUPS_JSON}}", groups_json)
    html = html.replace("{{ERAS_JSON}}", eras_json)

    # ── 写入文件 ──
    html_path = f"{output_base}_Viewer.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ HTML 已生成: {html_path}")


# ──────────────────────────────────────────
# 渲染输出
# ──────────────────────────────────────────
if __name__ == "__main__":
    output_path = "MiddleEastOil_EliteNetwork"

    print(f"📊 节点数: {len(NODES)}, 边数: {len(EDGES)}")

    # 交互式 HTML 查看器
    graph_title = "中东石油地缘政治精英网络图谱 (1973-2026)"
    export_html(output_path, graph_title, NODES, EDGES, COLORS, GROUPS, ERAS)
