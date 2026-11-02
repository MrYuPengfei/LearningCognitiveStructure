# 研究笔记：学习与建构概念图：一项元分析（Studying and Constructing Concept Maps: A Meta-Analysis）

> 本笔记由 MinerU 解析原始 PDF 后整理，公式与统计结果按原文逐条收录；表格数值取自原文（含解析切图）并核对一致。

## 一、基本信息（Basic Information）

| 项目 | 内容 |
| --- | --- |
| 英文标题 | Studying and Constructing Concept Maps: A Meta-Analysis |
| 中文译名 | 学习与建构概念图：一项元分析 |
| 作者 | Noah L. Schroeder, John C. Nesbit, Carlos J. Anguiano, Olusola O. Adesope |
| 机构 | 原文未明确说明（四位作者均来自概念图研究领域，Adesope 与 Nesbit 为前期代表性元分析 Nesbit & Adesope, 2006 的作者） |
| 发表 venue 与年份 | Educational Psychology Review（in press，DOI: 10.1007/s10648-017-9403-9） |
| 代码链接 | 原文未提供（使用商业软件 Comprehensive Meta-Analysis 2.2.064 与 IBM SPSS 23） |
| 任务 | 对"使用概念图（concept map）进行学习"相对于其他教学干预的效果进行随机效应（random-effects）元分析，并检验多个调节变量（moderator） |
| 关键词 | Concept map（概念图）、knowledge map（知识图）、meta-analysis（元分析）、cmap、kmap |

## 二、一句话概括（One-sentence Summary）

本研究合并了 142 个独立效应量（n = 11,814），发现使用概念图/知识图进行学习能产生中等且统计显著的效果（Hedges' g = .58, p < .001）；其中**建构**概念图（g = .72）优于**研读**概念图（g = .43），且效果在学科领域、地区、学段、协作/个体等多种条件下均稳健存在。

## 三、研究问题与动机（Problem and Motivation）

概念图（concept map）是一种节点—连线（node-link）图示：每个节点代表一个概念，每条连线标明其所连接两概念之间的关系（如"海洋酸化—减缓—珊瑚生长"可解读为命题"海洋酸化减缓珊瑚生长"）。现代意义下的概念图由 Novak 等在 1970 年代提出，作为促进有意义学习（meaningful learning）的工具；知识图（knowledge map，Dansereau 等）则被视为概念图的一种，其连线须从一组固定的关系词（如 type、example、leads to）中选取。

已有两项早期元分析给出积极但有限的结论：Horton 等（1993，18 项课堂研究）发现学生建构概念图平均效应量 .42、研读教师所制概念图平均效应量 .59（但仅 3 项研究）；Nesbit 与 Adesope（2006，67 个效应量）发现建构（g = .82）与研读（g = .37）均显著优于对照组。然而自 2006 年以来大量新研究涌现，且出现了与概念图相左的发现——如 Karpicke 与 Blunt（2011）、Blunt 与 Karpicke（2014）发现"提取练习（retrieval practice）写文本"比边看原文边画概念图更有效。因此有必要用更大样本重估并更新结论。

本研究的核心问题为：**使用概念图对学习的影响是什么？** 并通过调节分析进一步追问该影响如何随（a）对照干预方式、（b）学科（STEM/非 STEM）、（c）概念图类型、（d）干预时长、（e）研读还是建构、（f）研究地区、（g）学段、（h）协作或个体学习而变化。作者特别指出，既有研究多为"评价取向（evaluation-oriented）"而非"理论取向（theory-oriented）"，即多验证"概念图是否有效"，少有检验"为何有效"的认知机制。

## 四、记号与预备知识（Notation and Preliminaries）

| 记号 | 含义 |
| --- | --- |
| 概念图（concept map） | 节点表概念、连线表关系的 node-link 图示 |
| 知识图（knowledge map） | 连线须从固定 9 个关系词中选取的概念图变体 |
| 效应量 g（Hedges' g） | 标准化均值差（standardized mean difference）的校正估计，本文主报告指标；g ≈ .2 小、.5 中、.8 大 |
| k | 独立效应量（independent effect size）的个数（与研究篇数不同） |
| n | 该层合并的样本量（参与者人数） |
| SE | 效应量的标准误（standard error） |
| 95% CI | 效应量的 95% 置信区间 |
| Q_B | 组间异质性检验（between-group heterogeneity / moderator test）的统计量，服从 χ² 分布，下标为自由度 |
| I² | 异质性比例，表示总变异中由真实效应差异（而非抽样误差）解释的百分比；本文 I² = 87.50 表示高度异质 |
| Cohen's κ | 编码者间一致性系数（interrater reliability）；本文 κ = .88 |
| Z | 用于离群值（outlier）判定的标准分；判定准则 \|Z\| ≥ 3.3（p < .001） |
| 调节变量（moderator） | 用于解释效应量间差异的研究特征变量 |

## 五、方法：元分析流程（Proposed Method）

**文献检索（Literature Search）。** 聚焦 2005 年之后（承接 Nesbit & Adesope 2006 的检索），关键词为 "concept map* OR knowledge map* OR node-link map*"。2014-02-28 检索 AERA（2006–2014，54 篇）与 NARST（2007–2013，53 篇）会议摘要；2014-03-06 检索 Web of Science（1083）、ERIC（815）、Academic Search Complete（513）、PsychINFO（292）、Dissertation Abstracts（131）、PsychARTICLES（7），共定位 2,966 篇新研究。

**纳入标准（Inclusion Criteria）。** 须同时满足：(a) 对比地图的研读/建构/操作与其他学习活动；(b) 测量认知或动机结果（回忆、迁移、学习技能、兴趣、态度）；(c) 报告可估计标准化均值差的数据；(d) 干预前分组；(e) 随机分组或以前测等协变量控制组间差异。前测效应量超出 −.40 < d < .40 范围者排除（引自 Nesbit & Adesope, 2006）。

**编码流程（Coding Procedures）。** 两阶段编码：阶段Ⅰ依题名/摘要筛查，训练集 300 篇达成一致后扩展，筛得 347 篇；阶段Ⅱ全文审查再剔除 284 篇，余 63 篇。编码表沿用 Nesbit & Adesope（2006），但部分菜单项更新（如学科改分为 STEM/非 STEM）。效应量提取优先取最延迟的知识测验（如有一周后的后测则取之）。63 篇新研究产出 75 个独立效应量，与 Nesbit & Adesope（2006）的 67 个合并，**共 142 个独立效应量**。

**分析与离群值处理（Analyses）。** 缺描述统计时由报告的统计检验（如 t 值）反推效应量；同一研究含多组时按加权均值与合并标准差（pooled standard deviation）保持独立性。两个效应量（g = 3.82、g = 5.94）被判为离群（−3.3 ≥ Z ≥ 3.3, p < .001），依 Tabachnick & Fidell（2013）调整为接近次高值（g = 2.67）的 g = 2.70 与 g = 2.75。编码者一致性以 IBM SPSS 23 计算 Cohen's κ：随机抽取 20.6% 样本双编码，κ = .88（p < .001）。数据分析用 Comprehensive Meta-Analysis（CMA）2.2.064。

## 六、理论框架与认知假设（Theoretical Framework）

原文未给出形式化定理/证明，但系统阐述了概念图为何有效的两类解释，以及七条可被理论取向研究检验的认知假设（Nesbit & Adesope, 2013），故本节以中文复述其理论框架。

**两类解释机制。**（1）促进有意义学习（meaningful learning，Ausubel 提出）：概念图迫使学习者通过自我解释（self-explanation）、精细加工质询（elaborative interrogation）等把新知识与已有结构整合；（2）降低外在认知负荷（extraneous cognitive load）：概念图的语法远比自然语言简单，低先验知识或低言语能力者获益更大，符合"概念图减少外在负荷"的预期。

**七条认知取向假设（可用于解释概念图优于文本/讲授/讨论等）。** ① 概念图使信息在长时记忆的言语与视觉双通道双重编码（dual coding），利于提取；② 相比文本，认知负荷可分布于视觉与言语通道，避免言语工作记忆过载；③ 概念图将同一概念的多次指涉汇聚于空间一点（空间邻近，spatial contiguity），促进语义整合；④ Novak 式层级关系（上位—下位）比文本更显著；⑤ 名词—动词—名词的简式句法对弱读者/写作者更友好；⑥ 建构概念图的决策比写说明文需要更多精细/相关加工（germane processing）；⑦ 概念图占用更多空间，迫使更精炼/概括，进而促发更多精细加工。

作者强调：上述机制几乎缺乏直接实证支持，亟需"理论取向"的对比实验（如对比说明文、概念图、与概念图语义等价的简式命题列表）来验证。

## 七、实验设计（Experimental Design）

**研究规模与样本。** 合并数据库涵盖 1972（概念图诞生）至 2014 年，共 **142 个独立效应量、总样本 n = 11,814**。新检索得 2,966 篇，经两阶段筛选保留 63 篇（75 个效应量），加前期 67 个，构成本分析主体。

**研究类型分布（由对照/条件多样性体现）。** 干预侧含"建构（constructed）"与"研读（studied）"概念图；对照侧高度异质，包括讨论/讲授、文本、提纲、列表、大纲、其他干预等。

**调节变量（Moderators）及其操作化。** 本研究检验以下调节变量（部分在整体层与"按使用方式分层"两层分别检验）：
1. 替代性治疗（Alternative Treatments）：对照条件类别；
2. 学科领域（Domain）：STEM vs 非 STEM；
3. 概念图类型（Map Type）：静态（static，不运动不交互）、动画（animated，随旁白或点击逐步显现）、交互（interactive，需超出"下一步"按钮的操作）、混合（mixed）；
4. 干预时长（Duration）：< 1 周、1–4 周、> 4 周、未报告；
5. 使用方式（Map Use）：建构 vs 研读；
6. 地区（Region）：非洲、亚洲、欧洲、中东、美/加、其他/未报告；
7. 学科细分（Field，按使用方式分层）：STEM/非 STEM；
8. 概念图类型（按使用方式分层）；
9. 对照治疗（按使用方式分层）；
10. 学段（Grade Level）：中间年级（4–8）、中学（9–12）、中学后及以上；
11. 协作水平（Collaboration）：小组、个体、混合、其他、未知；
12. 研究时长（按使用方式分层）。

**统计模型。** 采用随机效应模型（random-effects model）；组间差异以 Q_B（χ² 检验）评估；异质性以 Q 与 I² 报告；发表偏倚以经典失安全 N（classic fail-safe N）与 Egger 线性回归检验。

## 八、实验结果（Experimental Results）

### 8.1 总体效果（Overall Results）

142 个独立效应量合并得 **g = .58（p < .001）**，样本庞大且异质显著：**Q_B(141) = 1,127.73, p < .001，I² = 87.50**，故进行调节分析。

### 8.2 替代性治疗（Alternative Treatments，Table 1）

组间差异显著 **Q_B(5) = 28.40, p < .001**。概念图显著优于讨论/讲授（g = 1.05），亦中等优于提纲/列表与文本。

| 对照条件 | n | k | g | SE | 95% CI |
| --- | --- | --- | --- | --- | --- |
| Discussion/Lecture（讨论/讲授） | 3,626 | 37 | 1.05* | .12 | [.81, 1.29] |
| Studied or Constructed Lists（研读/建构列表） | 626 | 13 | .43* | .18 | [.07, .78] |
| Studied or Constructed Outlines（研读/建构提纲） | 870 | 8 | .48* | .16 | [.17, .79] |
| Studied Text（研读文本） | 3,375 | 44 | .29* | .08 | [.13, .45] |
| Constructed Text（建构文本） | 1,054 | 13 | .39* | .13 | [.14, .65] |
| Other（其他） | 2,263 | 27 | .57* | .11 | [.36, .78] |

### 8.3 学科领域（Domain，Table 2）

无显著差异 **Q_B(2) = 3.00, p = .22**；STEM 与非 STEM 效果一致（假设"STEM 获益更大"未获支持）。

| 领域 | n | k | g | SE | 95% CI |
| --- | --- | --- | --- | --- | --- |
| STEM | 10,055 | 118 | .60* | .06 | [.47, .73] |
| Non-STEM（非 STEM） | 1,725 | 23 | .51* | .10 | [.30, .71] |
| Not Reported（未报告） | 34 | 1 | .05 | .34 | [−.61, .71] |

### 8.4 概念图类型（Map Type，Table 3）

无显著差异 **Q_B(3) = 1.34, p = .72**（动画/交互优于静态的假设未获支持，但动画组 k 仅 7、置信区间宽）。

| 类型 | n | k | g | SE | 95% CI |
| --- | --- | --- | --- | --- | --- |
| Animated（动画） | 520 | 7 | .47* | .19 | [.09, .84] |
| Interactive（交互） | 1,956 | 24 | .60* | .14 | [.33, .87] |
| Static（静态） | 8,855 | 105 | .60* | .07 | [.47, .73] |
| Mixed（混合） | 483 | 6 | .35 | .24 | [−.13, .82] |

### 8.5 干预时长（Duration，Table 4，整体层）

差异显著 **Q_B(3) = 22.47, p < .001**；时长越长效果越大，> 4 周达 g = .72，与 Nesbit & Adesope（2006）"短时更新奇效应"相反。

| 时长 | n | k | g | SE | 95% CI |
| --- | --- | --- | --- | --- | --- |
| < 1 week | 4,102 | 47 | .36* | .08 | [.20, .53] |
| 1–4 weeks | 3,380 | 53 | .68* | .10 | [.48, .88] |
| > 4 weeks | 4,088 | 41 | .72* | .10 | [.53, .92] |
| Unknown | 244 | 1 | .06 | .13 | [−.19, .31] |

### 8.6 使用方式（Map Use，Table 5）

差异显著 **Q_B(1) = 7.06, p = .01**。**建构（g = .72）显著优于研读（g = .43）**。作者解释：建构需主动精细加工，且建构研究多以"讨论/讲授"为对照（被动活动），故放大了效应。

| 使用方式 | n | k | g | SE | 95% CI |
| --- | --- | --- | --- | --- | --- |
| Constructed（建构） | 6,880 | 75 | .72* | .08 | [.56, .88] |
| Studied（研读） | 4,934 | 67 | .43* | .07 | [.29, .57] |

### 8.7 按使用方式分层的调节分析

**地区（Region，Table 6）：** 建构 Q_B(5) = 26.71, p < .001；研读 Q_B(4) = 26.46, p < .001。建构在非洲最大（g = 1.44），美/加最小（g = .49）；研读在亚洲最大（g = 1.04）。

| 使用方式 | 地区 | n | k | g | SE | 95% CI |
| --- | --- | --- | --- | --- | --- | --- |
| Constructed | Africa | 1,388 | 7 | 1.44* | .15 | [1.15, 1.74] |
| Constructed | Asia | 802 | 9 | .78* | .30 | [.19, 1.37] |
| Constructed | Europe | 589 | 9 | .82* | .19 | [.44, 1.19] |
| Constructed | Middle East | 786 | 13 | .75* | .17 | [.42, 1.09] |
| Constructed | USA/Canada | 2,775 | 33 | .49* | .11 | [.27, .71] |
| Constructed | Other/Not Reported | 540 | 4 | .62* | .21 | [.21, 1.03] |
| Studied | Asia | 523 | 5 | 1.04* | .37 | [.32, 1.76] |
| Studied | Europe | 209 | 3 | .46* | .17 | [.13, .79] |
| Studied | Middle East | 150 | 2 | .96* | .17 | [.62, 1.29] |
| Studied | USA/Canada | 3,667 | 51 | .25* | .07 | [.12, .38] |
| Studied | Other/Not Reported | 385 | 6 | 1.29* | .32 | [.67, 1.91] |

**学科细分（Field，Table 7）：** 建构 Q_B(1) = .33, p = .57；研读 Q_B(2) = 1.29, p = .53，均无显著差异。

| 使用方式 | 领域 | n | k | g | SE | 95% CI |
| --- | --- | --- | --- | --- | --- | --- |
| Constructed | STEM | 6,005 | 64 | .73* | .09 | [.55, .92] |
| Constructed | Non-STEM | 875 | 11 | .62* | .17 | [.28, .96] |
| Studied | STEM | 4,050 | 54 | .44* | .08 | [.28, .60] |
| Studied | Non-STEM | 850 | 12 | .41* | .13 | [.16, .66] |
| Studied | Not Reported | 34 | 1 | .05 | .34 | [−.61, .71] |

**概念图类型（按使用方式，Table 8）：** 建构 Q_B(2) = .02, p = .99；研读 Q_B(3) = .77, p = .86，均无显著差异（与认知负荷理论预测相悖）。

| 使用方式 | 类型 | n | k | g | SE | 95% CI |
| --- | --- | --- | --- | --- | --- | --- |
| Constructed | Interactive | 694 | 8 | .71* | .14 | [.44, .99] |
| Constructed | Static | 6,109 | 66 | .72* | .09 | [.54, .90] |
| Constructed | Mix | 77 | 1 | .75* | .25 | [.27, 1.24] |
| Studied | Interactive | 1,262 | 16 | .54* | .20 | [.16, .92] |
| Studied | Static | 2,746 | 39 | .40* | .08 | [.24, .57] |
| Studied | Animated | 520 | 7 | .47* | .19 | [.09, .84] |
| Studied | Mix | 406 | 5 | .27 | .28 | [−.28, .82] |

**对照治疗（按使用方式，Table 9）：** 建构 Q_B(4) = 15.25, p < .01；研读 Q_B(5) = 11.38, p = .04。建构对讨论/讲授效应最大（g = 1.05）；研读对文本仅小效应（g = .29），但对提纲/列表达中等（g = .72，k 小）。

| 使用方式 | 对照 | n | k | g | SE | 95% CI |
| --- | --- | --- | --- | --- | --- | --- |
| Constructed | Discussion/Lecture | 3,272 | 32 | 1.05* | .13 | [.78, 1.31] |
| Constructed | Studied/Constructed Outline | 650 | 6 | .40* | .19 | [.03, .77] |
| Constructed | Studied Text | 546 | 5 | .33 | .33 | [−.32, .97] |
| Constructed | Constructed Text | 865 | 10 | .48* | .15 | [.18, .78] |
| Constructed | Other | 1,547 | 22 | .47* | .10 | [.27, .66] |
| Studied | Discussion/Lecture | 354 | 5 | 1.09* | .30 | [.49, 1.68] |
| Studied | Studied/Constructed Lists | 626 | 13 | .43* | .18 | [.07, .78] |
| Studied | Studied/Constructed Outline | 220 | 2 | .72* | .34 | [.06, 1.39] |
| Studied | Studied Text | 2,829 | 39 | .29* | .08 | [.13, .45] |
| Studied | Constructed Text | 189 | 3 | .10 | .25 | [−.38, .59] |
| Studied | Other | 716 | 5 | .98* | .39 | [.22, 1.74] |

**学段（Grade Level，Table 10）：** 建构 Q_B(2) = .08, p = .96（各学段均中—大效应）；研读 Q_B(2) = 25.30, p < .001，中学段最大（g = 1.24，k = 4 较小），中学后最小（g = .32）。

| 使用方式 | 学段 | n | k | g | SE | 95% CI |
| --- | --- | --- | --- | --- | --- | --- |
| Constructed | Intermediate（中间年级） | 1,654 | 22 | .68* | .17 | [.35, 1.01] |
| Constructed | Secondary（中学） | 2,776 | 25 | .74* | .13 | [.48, 1.00] |
| Constructed | Postsecondary+（中学后及以上） | 2,450 | 28 | .73* | .14 | [.46, 1.00] |
| Studied | Intermediate | 521 | 7 | .82* | .10 | [.62, 1.02] |
| Studied | Secondary | 216 | 4 | 1.24* | .23 | [.79, 1.69] |
| Studied | Postsecondary+ | 4,197 | 56 | .32* | .08 | [.17, .47] |

**协作水平（Collaboration，Table 11）：** 建构 Q_B(4) = 8.79, p = .07；研读 Q_B(3) = 1.47, p = .69，均无显著差异（与 2006 年"协作更优"结论相反）。

| 使用方式 | 协作 | n | k | g | SE | 95% CI |
| --- | --- | --- | --- | --- | --- | --- |
| Constructed | In Groups | 1,609 | 14 | .91* | .19 | [.53, 1.29] |
| Constructed | Individual | 2,788 | 32 | .55* | .12 | [.32, .78] |
| Constructed | Mixed | 1,740 | 22 | .91* | .17 | [.58, 1.23] |
| Constructed | Other | 115 | 2 | .95 | .51 | [−.05, 1.94] |
| Constructed | Unknown | 628 | 5 | .29 | .19 | [−.09, .67] |
| Studied | In Groups | 476 | 10 | .48* | .22 | [.04, .92] |
| Studied | Individual | 4,296 | 55 | .41* | .08 | [.26, .57] |
| Studied | Other | 56 | 1 | .75* | .27 | [.22, 1.29] |
| Studied | Unknown | 106 | 1 | .47* | .20 | [.09, .86] |

**研究时长（按使用方式，Table 12）：** 建构 Q_B(3) = 22.32, p < .001，与整体趋势一致——1–4 周（g = .94）与 > 4 周（g = .72）优于 < 1 周（g = .40），**否定了 2006 年"短时才有效"的新奇效应说**；研读 Q_B(2) = 5.22, p = .07，无显著差异，但 > 4 周组 g = .70（k = 4 偏小）。

| 使用方式 | 时长 | n | k | g | SE | 95% CI |
| --- | --- | --- | --- | --- | --- | --- |
| Constructed | < 1 week | 1,204 | 14 | .40* | .14 | [.13, .68] |
| Constructed | 1–4 weeks | 1,662 | 23 | .94* | .18 | [.58, 1.30] |
| Constructed | > 4 weeks | 3,770 | 37 | .72* | .11 | [.51, .94] |
| Constructed | Unknown | 244 | 1 | .06 | .13 | [−.19, .31] |
| Studied | < 1 week | 2,898 | 33 | .34* | .10 | [.14, .55] |
| Studied | 1–4 weeks | 1,718 | 30 | .48* | .11 | [.27, .70] |
| Studied | > 4 weeks | 318 | 4 | .70* | .12 | [.47, .92] |

### 8.8 发表偏倚（Publication Bias）

经典失安全 N 检验显示需 **8,394** 篇零效应研究才能使 p > .05，远超 Rosenthal（1995）的 5k + 10 = 720 阈值；Egger 线性回归截距 = .48，t(140) = .63，p = .53，**未发现显著发表偏倚**。

## 九、相关工作（Related Work）

与两项前期元分析直接衔接：Horton 等（1993，18 项课堂研究）报告建构 .42、研读 .59（仅 3 项）；Nesbit 与 Adesope（2006，67 个效应量）报告建构 g = .82、研读 g = .37，并发现建构对动画概念图（g = .74, k = 2）、提纲/列表（g = .28, k = 10）等特定对照的效应。本文在更大样本（142 vs 67）上复现并更新了这些结论，且**推翻了 2006 年"短时干预更新奇效应更强"与"协作优于个体"的发现**。与提取练习研究（Karpicke & Blunt, 2011；Blunt & Karpicke, 2014）形成对话：本文仅少量研究含提取练习对照，指出需未来研究比较概念图与其他提取练习形式。

## 十、结论（Conclusion）

建构与研读概念图相对多种其他教学策略均有效，且在小组/个体、STEM/非 STEM、各学段均成立。本文较 2006 年分析纳入更多研究后，未发现使用方式（协作/个体）与概念图类型（静态/动画/交互）的显著差异。作者呼吁从"评价取向"转向"理论取向"研究，以检验七条认知假设、厘清概念图有效的机制，并比较不同地图设计以改进概念图本身。本元分析综合了 42 年（1972–2014）关于概念图学习效果的研究。

## 十一、批判性评价与启发（Critical Appraisal）

### 11.1 优点
- **样本体量大、时效性强**：142 个独立效应量、n = 11,814，并更新了十年间新证据，结论稳健。
- **调节分析系统全面**：从对照条件、学科、类型、时长、使用方式、地区、学段、协作等 8+ 维度拆解，并区分"建构/研读"两层，避免了笼统结论。
- **方法透明**：离群值处理、效应量提取规则（取最延迟测验）、编码者一致性（κ = .88）、发表偏倚双检验均明确报告。
- **诚实区分研究取向**：明确指出领域缺乏"为何有效"的理论检验，并给出可操作的实验设计建议。

### 11.2 局限与可质疑之处
- **高度异质性未充分解释**：I² = 87.50，绝大多数变异未被调节变量解释，说明存在未被编码的重要边界条件。
- **对照条件内部极不均质**：讨论/讲授类包含教师主导讨论、非交互讲授等，实际学习者活动常未被监控/报告，使效应量解释存疑。
- **小样本亚组不可靠**：多个调节层（如研读×动画、研读×中东）k = 2–7，置信区间极宽，结论宜谨慎；作者亦自承"样本量是否造成假象"尚不可知。
- **"评价取向"主导导致机制证据薄弱**：七条认知假设几乎无直接检验，本文结论仍停留在"有效"层面。
- **地区效应难以解释**：非洲 g = 1.44 但无新增研究，地区差异可能反映"建构活动 vs 当地传统讲授"的对比强度，而非概念图本身的普适优势。

### 11.3 与本课题（Learning Cognitive Structure）的关联
概念图本质是把学习者的认知结构（cognitive structure）外显化、空间化的表征工具。本元分析证明"主动建构概念图"（g = .72）优于被动研读，呼应"知识精炼/精细加工生成更优认知结构"的假设；其七条认知机制（双编码、负荷分布、空间邻近、简式句法、精细加工等）为"学习认知结构"提供了可检验的中介/机制框架。对课题的启示：可借鉴其"理论取向"实验设计，比较不同结构表征（空间聚合 vs 离散节点）对学习迁移的影响。

> 以下为笔记撰写者的延伸思考，非原文内容：本课题若要量化"认知结构的变化"，可结合概念图的网络指标（节点度、层级深度、交叉连接数）作为认知结构复杂度的代理变量，并以迁移测验为效标，弥补原文仅以"对照效应量"推断机制的不足。

## 附录 A：全文公式汇总（Formula Index）

本文为元分析，无独立推导公式，核心为下列统计量与检验（数值均取自原文/解析切图）：

| 编号 | 公式/统计量 | 含义 |
| --- | --- | --- |
| A1 | $g = .58\;(p < .001)$ | 随机效应模型下总体标准化均值差（Hedges' g）效应量 |
| A2 | $n = 11{,}814,\;k = 142$ | 总样本量与独立效应量个数 |
| A3 | $Q_B(141) = 1{,}127.73,\;p < .001$ | 总体异质性检验（自由度 141） |
| A4 | $I^2 = 87.50$ | 异质性比例，表明高度异质（真实效应差异主导） |
| A5 | 离群判定：$-3.3 \ge Z \ge 3.3,\;p < .001$ | 标准分超界即判离群；两例 $g=3.82,5.94$ 调至 $2.70,2.75$（贴近次高值 $g=2.67$，依 Tabachnick & Fidell, 2013） |
| A6 | 替代治疗：$Q_B(5)=28.40,\;p<.001$ | Table 1 组间差异显著 |
| A7 | 领域：$Q_B(2)=3.00,\;p=.22$ | Table 2 无显著差异 |
| A8 | 图类型：$Q_B(3)=1.34,\;p=.72$ | Table 3 无显著差异 |
| A9 | 时长：$Q_B(3)=22.47,\;p<.001$ | Table 4 差异显著 |
| A10 | 使用方式：$Q_B(1)=7.06,\;p=.01$ | Table 5 建构>研读 |
| A11 | 地区：建构 $Q_B(5)=26.71,\;p<.001$；研读 $Q_B(4)=26.46,\;p<.001$ | Table 6 |
| A12 | 学科细分：建构 $Q_B(1)=.33,\;p=.57$；研读 $Q_B(2)=1.29,\;p=.53$ | Table 7 均无显著差异 |
| A13 | 类型（分层）：建构 $Q_B(2)=.02,\;p=.99$；研读 $Q_B(3)=.77,\;p=.86$ | Table 8 |
| A14 | 对照（分层）：建构 $Q_B(4)=15.25,\;p<.01$；研读 $Q_B(5)=11.38,\;p=.04$ | Table 9 |
| A15 | 学段（分层）：建构 $Q_B(2)=.08,\;p=.96$；研读 $Q_B(2)=25.30,\;p<.001$ | Table 10 |
| A16 | 协作（分层）：建构 $Q_B(4)=8.79,\;p=.07$；研读 $Q_B(3)=1.47,\;p=.69$ | Table 11 均无显著差异 |
| A17 | 时长（分层）：建构 $Q_B(3)=22.32,\;p<.001$；研读 $Q_B(2)=5.22,\;p=.07$ | Table 12 |
| A18 | $\kappa = .88\;(p < .001)$ | 编码者间一致性（Cohen's Kappa），20.6% 双编码 |
| A19 | 失安全 N $= 8{,}394$；Rosenthal 阈值 $5k+10 = 720$ | 经典失安全 N 检验，远超阈值→结果稳健 |
| A20 | Egger 截距 $= .48,\;t(140)=.63,\;p=.53$ | Egger 回归检验，无显著发表偏倚 |

> 注：效应量由报告统计（如 t 值）反推、多组取加权均值与合并标准差（pooled SD）等计算，原文未给出其符号化公式，仅描述流程；images/ 下 `page_*_equation_4.jpg` 仅为表格显著性脚注"*p < .05"的切图，非独立公式，故未单列。

## 附录 B：图表索引（Figure & Table Index）

| 编号 | 内容 | 文件路径 |
| --- | --- | --- |
| Figure 1 | 概念图示例（CmapTools 制作的猛禽 raptors 概念图，节点—连线结构） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_61_image_2.jpg |
| Figure 2 | 研究筛选流程图（PRISMA 式：初检 2,966 → 阶段Ⅰ 347 → 阶段Ⅱ 63 → 75+67=142 效应量） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_62_image_2.jpg |
| Table 1 | 替代性治疗（Alternative Treatments）效应量 | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_49_table_3.jpg |
| Table 2 | 学科领域（Domain: STEM/非 STEM） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_50_table_3.jpg |
| Table 3 | 概念图类型（Map Type: 静态/动画/交互/混合） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_51_table_3.jpg |
| Table 4 | 干预时长（Duration，整体层） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_52_table_3.jpg |
| Table 5 | 使用方式（Map Use: 建构 vs 研读） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_53_table_3.jpg |
| Table 6 | 地区（Region，按使用方式分层） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_54_table_3.jpg |
| Table 7 | 学科细分（Field，按使用方式分层） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_55_table_3.jpg |
| Table 8 | 概念图类型（按使用方式分层） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_56_table_3.jpg |
| Table 9 | 对照治疗（按使用方式分层） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_57_table_3.jpg |
| Table 10 | 学段（Grade Level，按使用方式分层） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_58_table_3.jpg |
| Table 11 | 协作水平（Collaboration，按使用方式分层） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_59_table_3.jpg |
| Table 12 | 研究时长（按使用方式分层） | ../md/Schroeder_et_al_2018_Concept_Maps_Meta_Analysis_markdown/images/page_60_table_3.jpg |

> 说明：原文以"—Insert Figure/Table X about here—"占位，未直接内嵌图；上述路径为 MinerU 解析切图，文件名中的 `table_3`/`image_2` 为解析器内部标签，已按 PDF 页码顺序与正文表格编号（Table 1→page_49 … Table 12→page_60；Figure 1→page_61，Figure 2→page_62）逐一核对对应。
