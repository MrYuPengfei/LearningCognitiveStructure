# 研究笔记：感知符号系统（Perceptual Symbol Systems）

> 本笔记由 MinerU 解析原始 PDF 后整理，公式按原文逐条收录。原文为 Lawrence W. Barsalou 1999 年发表于 *Behavioral and Brain Sciences* 的目标论文（target article，含开放同行评议），正文本身以理论构建为主，未报告作者原创实验。

## 一、基本信息（Basic Information）

| 项目 | 内容 |
| --- | --- |
| 英文标题 | Perceptual symbol systems |
| 中文译名 | 感知符号系统 |
| 作者 | Lawrence W. Barsalou |
| 机构 | Department of Psychology, Emory University, Atlanta |
| 发表 venue 与年份 | *Behavioral and Brain Sciences*（目标论文，1999；据论文体例与文末 BBS 引文推断，原文未给出明确卷期页码） |
| 代码链接 | 原文未提供 |
| 任务 | 提出一种以感觉-运动（sensory-motor）系统为基础的"感知符号系统"知识表征理论，系统反驳"非模态符号系统（amodal symbol systems）"的主导地位 |
| 关键词 | analogue processing（类比加工）；categories（范畴）；concepts（概念）；frames（框架）；imagery（心象）；knowledge（知识）；perception（感知）；simulation（模拟）；symbol grounding（符号 grounding）；symbol systems（符号系统） |

## 二、一句话概括（One-sentence Summary）

Barsalou 主张，知识并非建立在任意的、与感知脱钩的非模态（amodal）符号之上，而是建立在感觉-运动系统中经选择性注意提取并长期存储的"感知符号"之上：相关感知符号跨实例整合为"模拟器（simulator）"，模拟器可生成无限"模拟（simulation）"，从而自然地实现类型表征、范畴推理、组合生产性（productivity）、命题（proposition）与抽象概念，构成一个在功能上完整可用的概念系统。

## 三、研究问题与动机（Problem and Motivation）

**1. 认知与感知的世纪分裂。** 20 世纪以来，认知科学深受逻辑、统计与编程语言发展的影响，转向以"非模态符号系统"为核心的理论（特征表、框架、语义网、产生式系统、联结主义等）。这类系统假设：感知状态被"转导（transduction）"为一种结构上与感知毫无相似性的新表征语言，符号与世界之间靠任意的约定关联。作者认为这种"认知与感知相互独立"的图景从根本上就是错误的。

**2. 非模态符号系统的四大难题（原文 1.2.2 节）。**
- **缺乏直接实证**：许多研究表明概念符号具有感知特征（Glaser 1992；Glenberg et al. 1998b），而非模态假设缺乏支持；
- **神经科学反证**：范畴知识定位于感觉-运动脑区，损伤特定感觉-运动区会破坏相应范畴的概念加工（Damasio 1989；Gainotti et al. 1995；Pulvermüller 1999）；
- **转导过程（transduction）缺失**：从未解释感知状态如何映射为 amodal 符号，且脑中不存在该过程的证据；
- **符号 grounding 问题（symbol grounding problem）**（Harnad 1987, 1990；Searle 1980）：无法说明 amodal 符号如何回指感知状态与世界，若引入"中介感知表征"则 amodal 符号本身冗余。

此外，作者指出 amodal 系统"过于强大"——可对任何现象事后（post hoc）解释却缺乏可证伪的先验预测（Anderson 1978）。

**3. 对感知理论的常见误解。** 批评者常把感知理论歪曲成"全息记录、仅含意识图像、仅限感觉通道、静态、不支持命题"。作者强调，严谨的感知理论（如 Locke、Russell、Price 等）早已包含成分性、无意识表征、内省（introspection）维度、动态性与类型-个例（type-token）映射。

**4. 核心目标。** 证明"感知符号系统"能像 amodal 系统一样实现完全功能的概念系统所需的全部性质——类型/个例表征、范畴推理、组合生产性、命题、抽象概念——且避免后者的难题。

## 四、记号与预备知识（Notation and Preliminaries）

| 术语 | 含义 |
| --- | --- |
| 感知状态（perceptual state） | 感觉-运动系统中由物理输入激活的神经状态，含"无意识神经表征"与"可选的意识体验"两层 |
| 感知符号（perceptual symbol） | 对感知状态中某一连贯方面的图式化（schematic）神经记录的子集，而非全息脑状态；本质是神经元联结模式，动态而非离散 |
| 模拟器（simulator） | 跨多个范畴实例，把相关感知符号整合进一个"框架（frame）"，并能据此生成无限"模拟"的生成机制；**概念 ≡ 模拟器** |
| 模拟（simulation） | 由模拟器在 Working Memory 中激活特定子集而构造的具体、局部、往往有偏的实例表征（类比于心理意象） |
| 框架（frame） | 模拟器内部的整合结构，含空间/时间骨架与各子区的"内容专门化（specialization）"，对应谓词、属性-值绑定、约束与递归四类基本性质 |
| 多模态（multimodal） | 符号形成过程适用于视觉、听觉、触觉、嗅觉、味觉、本体感觉（proprioception）与内省（introspection） |
| 可供性（affordance） | 感知/动作经验中捕获的"某物可用于何种交互"的属性，是范畴推理与计划的物理基础（Gibson 1979） |
| 类型-个例映射（type-token mapping） | 把记忆中的"类型"（概念/模拟器）绑定到当下感知的"个例"（token），即命题的核心 |
| 变身体现（variable embodiment） | 符号意义随其所栖身的物理系统而变化；是感知符号系统特有、amodal 系统（功能主义）所无的性质 |

## 五、方法：感知符号系统（Proposed Method）

论文给出的是**高层功能架构**，作者明确声明不进行形式化定义，也不绑定具体神经机制（原文 2 节开头）。

### 5.1 六个核心性质（实现"基本"概念系统）

1. **神经表征位于感觉-运动系统（2.1）**。感知符号是对感知期间神经激活的记录；默认定义落在神经层——无意识神经表征（而非意识图像）才是感知符号的核心内容。这区别于"图片"或"心象"。
2. **图式化成分（2.2）**。注意选择性地隔离并存储感知的某一连贯方面（如形状、颜色、举起），形成"图式化"符号；其动态、成分性、可指代任意个例、可不确定（indeterminate）等性质由神经元通道与质性编码（qualitative neurons）保证。
3. **多模态（2.3）**。形成过程适用于一切被经验到的方面，符号广泛分布于各模态专属脑区；"感知"在此涵盖本体感觉与内省，远超通常的"感觉"义。
4. **模拟器与模拟（2.4）**。相关符号围绕一个对象/事件中心参考系（object-centered reference frame）整合为框架，框架再生成无限模拟。模拟器=两层结构：①跨实例整合的底层框架；②由其生成的潜在无限模拟集。它统一了概念（长期记忆中的类知识）与概念化（工作记忆中的具体思考），并能解释范畴化（模拟与感知"直接比较"而非"异质表征比较"）、范畴推理（模拟超越所见、推出 rear panel、内部组件等）、可供性、概念稳定性与认知可穿透性（cognitive penetration）。
5. **框架（2.5）**。框架含空间/内容两层（呼应 Ungerleider & Mishkin 的空间/客体双通路），其四性质为：谓词（未专门化的框架）、属性-值绑定（子区专门化）、约束（专门化间联想，可弱化导致重构错误）、递归（模拟器内嵌模拟器，深度不限）。具体模拟的构造是一个约束满足/吸引子过程，并可对信息做放大、旋转、平移、切分、合并等变换。
6. **语言索引与控制（2.6）**。词语符号本身也是经注意从"说出的/写出的词"提取的感知符号，与概念模拟器建立联结，从而"索引并控制"模拟的构建——语言句法提供搭建感知模拟的指令。

### 5.2 四个派生性质（实现"完全功能"概念系统，第 3 节）

- **生产性（productivity, 3.1）**：模拟器经组合（combinatorial）与递归（recursive）处理生成无限复杂模拟（图 4）。本质上是"符号形成过程"的逆操作——把被滤掉的图式细节重新加回；并受可供性约束、产生涌现属性（emergent properties）。语言语法与概念结构相对应，使人能彼此控制对方在缺乏实指时的模拟。
- **命题（propositions, 3.2）**：命题 = 把模拟器（类型）绑定到感知个例（个例）并经模拟融合。成功绑定即真（true）命题；绑定失败/缺失即假（false）或否定（negation）命题；层级模拟实现嵌套命题；模拟的要点（gist）可被多种措辞转述（图 5）。作者还处理了意向性（intentionality）：符号内容既不必要也不充分决定指称，但感知内容可在确定指称时起启发式作用（图 5、式 9）。
- **变身体现（variable embodiment, 3.3）**：与 amodal/功能主义（functionalism）不同，感知符号形式变化具有语义含义（图 6）——杯子符号变大⇒指称显得更大；而词"CUP"变换形态不改变指称。这使概念系统适应个体感知差异，也带来概念变异与稳定的第二来源。
- **抽象概念（abstract concepts, 3.4）**：用三机制表示抽象概念——①以模拟的事件序列"框定（framing）"抽象概念；②选择性注意突出其核心内容；③内省状态（introspection）的感知符号。据此给出真/假/否定/愤怒（图 7）、析取（disjunction，图 8，以中间区"交替模拟"实现"或"）、以及 ad hoc 范畴（图 9）的感知表征方案。

## 六、理论分析（Theoretical Analysis）

本文是理论构建型目标论文，给出的是**功能/言语论证**，而非数学定理与形式证明；故本节复述其关键的理论推演与形式记号，而非"证明"。

**1. 命题的形式记号（对比 amodal 系统的逻辑式）。** 作者用谓词-论元记号展示 amodal 系统如何表达命题，并论证感知符号系统通过"模拟 + 融合"实现同等命题（详见附录 A 公式 1–8，及正文式 (9) 的限定描述 "The computer on my office desk is broken"）。这些逻辑式本身是作为对照示例给出的，重点在于：感知符号系统不依赖离散 amodal 符号也能完成类型-个例绑定、否定、层级嵌套与要点保持。

**2. 生产性何以"自然涌现"。** 论点是：图式化（schematicity）使生产性成为可能——符号形成时滤掉的信息（颜色、纹理）可在生产性时加回（3.1.1）。组合与递归在物理图式系统（建筑制图、电路图）中本就存在，故认知中的图式感知表征亦可如此（Price 1953）。

**3. 抽象概念可表征的猜想（3.4.2）。** 作者提出：对任意抽象概念，先识别框定它的事件序列，再刻画其中的物理与内省符号，最后定位作为核心表征的焦点元素——此策略"应当总能给出满意说明"。这是可错的研究纲领，需实证检验；作者报告了与 Solomon 的初步实验（抽象概念比具体概念引发更多关于事件序列与内省的特征）及 Pulvermüller（1999）前额叶激活的吻合作为佐证。

**4. 理论自评（局限）。** 作者明确承认（2 节）：理论未指定感知特征集、未解释注意为何聚焦某些特征、未解释世界如何被划分为范畴、未解释抽象/拟合如何计算、未解释组合约束的来源；并声明这些在"所有"知识理论中大都仍未解决。

## 七、实验设计（Experimental Design）

**目标论文本身未报告作者原创实验**，其核心证据为理论性的；文中援引的实证支持主要来自他人研究，类型包括：
- **神经心理学/神经影像**：范畴特异性损伤（视觉区损伤破坏鸟类等视觉范畴的概念加工；运动/体感区损伤破坏工具范畴）、神经影像显示动物概念激活视觉区、工具概念激活运动/体感区（Damasio & Damasio 1994；A. Martin et al. 1995, 1996；Pulvermüller 1999；Rösler et al. 1995）；
- **行为/计算**：Glenberg 等的"可供性（affordance）"语言理解实验、内隐记忆定位于感觉-运动系统（Buckner et al. 1995）、意象激活早期感觉/运动皮层（Kosslyn et al. 1995；Crammond 1997）等。

作为代表，文末开放评议中 Glenberg 介绍的实验（非目标论文本人实验，特此注明）：让被试在"设定句"语境下判断"可 afford（afforded）"与"不可 afford（non-afforded）"句子的合理度（7 点量表），并设"相关（related，熟悉）"句对照，以分离"基于经验的推理"与"基于可供性模拟的理解"。

## 八、实验结果（Experimental Results）

目标论文为理论文章，**无作者本人实验数值结果**。其援引的实证要点摘要如下（均来自所引研究，非本文测量）：

- **神经定位**：处理动物概念时视觉区高度活跃，处理工具概念时运动/体感区高度活跃（A. Martin et al. 1995, 1996 等），支持"多模态、分布于模态专属区"的假设；
- **抽象概念**：Pulvermüller（1999）综述显示抽象概念倾向于激活前额叶（协调多模态信息与时序加工），与本文"抽象概念 = 多模态 + 时序事件序列"一致；
- **Glenberg 等可供性实验（评议中报告，作外部佐证）**：afforded 句平均合理度 **4.58/7**，non-afforded 句 **1.25/7**；afforded 与 related（熟悉）句阅读时间无显著差异，二者均快于 non-afforded 句——支持"概念表征必须包含类感知符号以供新颖可供性推导"及"具身约束限制概念组合"。

> 说明：以上 Glenberg 数值为目标论文开放评议中报告，旨在佐证而非本文原创实验；其余为作者综述他研究的定性结论。

## 九、相关工作（Related Work）

- **非模态符号系统**：Fodor（1975）、Pylyshyn（1984）、Newell & Simon（1972）、Dennett（1969）、Haugeland（1985）的形式/计算表征纲领，以及 feature lists、frames、semantic nets、production systems；联结主义（McClelland et al. 1986；Rumelhart et al. 1986）多数也因随机初值而具任意性，但 Pulvermüller（1999）等共享联结网络可非 amodal。
- **早期经验主义/感知理论**：Aristotle、Locke、Berkeley、Hume、Kant、Reid、Russell（1919b）、Price（1953）的意象/图式/意向性论述。
- **认知语言学与具身认知**：Lakoff & Johnson（1980, 1999）、Langacker（1986–1997）、Johnson（1987）、Talmy（1983）、Fauconnier & Turner（1998）、Gibbs（1994）、Glenberg（1997）、Prinz（1997）等，主张知识具感知性；本文与之一致但强调"直接（非仅隐喻）"表征抽象概念。
- **神经科学**：Damasio（1989）收敛区（convergence zones）、Pulvermüller（1999）范畴具身、Martin 等神经影像。
- **开放同行评议（BBS 格式，构成本文重要对话）**：Edelman & Erlhagen 指出"绑定问题（binding problem）"未充分解决，主张以空间（视网膜拓扑）框架支撑组合性；Fauconnier 强调隐喻/类比/反事实的复杂映射与"后台认知"；Gabora 主张感知符号可经自组织转化为 amodal 抽象，批评作者过速否定联结主义；Gibbs & Berg 主张隐喻对抽象概念更具构成性；Glenberg 以"索引假设（Indexical Hypothesis）"提供可供性实证；Freksa 等从空间认知/计算机科学视角补充。

## 十、结论（Conclusion）

Barsalou 论证：感知理论并非只能做"记录系统"，而可构成"完全功能的概念系统"。经由选择性注意提取感知成分、跨实例整合为模拟器，感知符号系统能表征类型、产生范畴推理、组合生产性、建立命题、表示抽象概念，并因变身体现而超越功能主义。该框架同时重塑了对注意、工作记忆、长时记忆、语言理解、问题解决、推理与人工智能的理解，并与神经科学、演化与发展、AI 相融贯。其要义是：**认知本质上就是感知的**，二者共享神经机制，不应被割裂。

## 十一、批判性评价与启发（Critical Appraisal）

### 11.1 优点
- 系统回答了"感知理论能否胜任概念系统"这一长期质疑，把 grounding 从"待解难题"转为"架构内在属性"；
- 用统一机制（模拟器/模拟 + 框架 + 选择性注意）覆盖从具体范畴到真/假/否定/析取/anger 等抽象概念，解释力强；
- 与神经科学（范畴特异性、意象激活早期皮层、内隐记忆定位）高度吻合，且对注意、记忆、语言等现象给出统一重构；
- 强调"无意识神经表征"而非"意识图像"，避开了对心理意象的诸多传统批评。

### 11.2 局限与可质疑之处
- **绑定问题（binding problem）未充分解决**（Edelman & Erlhagen 评议）：组合性需要把成分"绑定"进结构，作者归因于框架/模拟却缺乏感知层面的具体绑定机制；
- **组合约束与涌现属性的来源未形式化**（Fauconnier 评议）："形成过程"本身如何产生 emergent properties 与量化/连接词/反事实，语焉不详；
- **对联结主义过于轻易地否定**（Gabora 评议）：仅以"随机初值⇒任意"打发，忽视了吸引子动力学可自然产生类别表征；
- **缺乏可计算的形式模型**：全文为功能描述，无具体算法、复杂度或量化预测，难以直接证伪/复现；
- **隐喻作用可能被低估**（Gibbs & Berg 评议）：抽象概念（如 anger）或对具身隐喻更依赖，而非仅"直接感知符号 + 隐喻修饰"；
- **变身体现对功能主义的批评或偏强**：能否完全排除"硬件无关"的抽象计算层仍存争议；
- **抽象概念猜想待实证**：作者自承"成功不蕴含人真如此表征"，需未来实验检验。

### 11.3 与本课题（Learning Cognitive Structure）的关联
- **认知结构的"感知根基"**：本课题关注"学习认知结构"，本文提供的启示是——个体习得的范畴/概念结构本质上是其在感觉-运动经验中经注意提取、跨实例整合而成的模拟器网络；"结构"不是抽象的节点-连线，而是模态分布、可动态模拟的神经生成机制。
- **从记录到概念的学习跃迁**：学习的关键不在于积累全息经验，而在于注意如何"切分"经验为图式成分并建立跨实例框架——这直接对应"结构化表示如何习得"的核心问题。
- **抽象/高阶认知的习得**：真、否定、析取等抽象结构的形成，可视为对"模拟与情境是否成功匹配"这一事件序列的内省性模拟学习，为"高阶认知结构如何从无到有"提供发展性线索。
- **以下为笔记撰写者的延伸思考，非原文内容**：将"模拟器"视作一种可学习的生成世界模型（world model），可与当代具身 AI、潜变量生成模型与神经符号系统对接——用感知/动作轨迹训练出的模拟器，或可成为"学习型认知结构"的计算载体；同时应警惕把"感知"窄化为视觉，需纳入本体感觉与内省以覆盖社会性/抽象学习。

## 附录 A：全文公式汇总（Formula Index）

| 编号 | 公式 | 含义 |
| --- | --- | --- |
| (1) | $\begin{array}{l} \text{CHAIR} \\ \text{seat} \\ \text{back} \\ \text{legs} \end{array}$ | 以特征表（feature list）形式用词语表示 amodal 符号的示例：椅子由 seat/back/legs 等特征组成 |
| (2) | $\begin{array}{l} EAT \\ \text{Agent = horse} \\ \text{Object = hay} \end{array}$ | 以谓词-论元（predicate-argument）结构表示 amodal 符号的示例：吃这一事件的关系/论元/值 |
| (3) | $\begin{array}{l} \text{CONTAINS (grocery store, apples)} \\ \text{ABOVE (ceiling, floor)} \end{array}$ | 用 amodal 形式对"杂货店"场景的两种不同命题化描述（选择不同方面） |
| (4) | $\begin{array}{l} \text{ABOVE (ceiling, floor)} \\ \text{BELOW (floor, ceiling)} \end{array}$ | 对同一空间关系用不同概念（above / below）的两种命题化 |
| (5) | $\text{CAUSE (HUNGRY (shopper), BUY (shopper, groceries))}$ | 命题的层级嵌套：因果内含状态与事件，体现复杂命题的组合性 |
| (6) | $\text{CONTAINS (grocery store, mountains)}$ | 一个假命题（false proposition）示例 |
| (7) | $\text{NOT} (\text{CONTAINS (grocery store, mountains)})$ | 否定命题（此处为真）示例 |
| (8) | $\text{GIVE (Agent = marshall, Recipient = rick, Object = watch}$ | 命题捕捉句子"要点（gist）"，可被"Rick received a watch from Marshall"等多种措辞转述 |
| (9) | "The computer on my office desk is broken."（限定描述，非 LaTeX） | 说明"限定描述"等符号内容之外的外部机制可确立指称（intentionality） |

**公式图片留存说明**：MinerU 在 `images/` 下另切出若干公式图片——`page_18_equation_3.jpg`、`page_18_equation_5.jpg`、`page_18_equation_8.jpg`、`page_18_equation_11.jpg`、`page_18_equation_13.jpg`、`page_18_equation_16.jpg` 与 `page_2_equation_5.jpg`、`page_2_equation_7.jpg`。经核对，其内容与正文命题表达式（约对应公式 3–8 附近的逻辑式）一致；因正文已提供 LaTeX 转录，此处以图片留存为视觉证据，路径见上，未单列额外公式。

## 附录 B：图表索引（Figure & Table Index）

| 编号 | 内容 | 文件路径 |
| --- | --- | --- |
| Figure 1 | 感知符号系统的基本假设：感觉-运动系统中感知状态的子集被提取并存储为符号，符号具模态性且与感知状态类比相关 | `../md/Barsalou_1999_Perceptual_Symbol_Systems_markdown/images/page_1_image_1.jpg`（另 `page_0_image_13.jpg` 同节出现） |
| Figure 2 | 非模态符号系统的基本假设：感知状态被转导为全新、与感知无关的非模态表征 | `../md/Barsalou_1999_Perceptual_Symbol_Systems_markdown/images/page_2_image_1.jpg` |
| Figure 3 | 框架的形成与演化（A 首例建立；B 第二例后演化；C 由框架构造模拟），箭头为兴奋连接、圆圈为抑制连接 | `../md/Barsalou_1999_Perceptual_Symbol_Systems_markdown/images/page_13_image_7.jpg` |
| Figure 4 | 对象范畴（A）与空间关系（B）经组合（C）与递归（D）处理实现生产性；细实线框=模拟器，粗虚线框=模拟 | `../md/Barsalou_1999_Perceptual_Symbol_Systems_markdown/images/page_16_image_6.jpg` |
| Figure 5 | （A）感知实体与模拟融合形成真命题；（B）复杂层级命题；（C）同一场景的另类解释。细实线=模拟器，粗虚线=模拟，粗实线=感知情境 | `../md/Barsalou_1999_Perceptual_Symbol_Systems_markdown/images/page_18_image_25.jpg`、`page_18_image_26.jpg`、`page_18_image_27.jpg` |
| Figure 6 | 变换词/amodal 符号不改变指称，而变换感知模拟则对应指称的相应变化（变身体现） | `../md/Barsalou_1999_Perceptual_Symbol_Systems_markdown/images/page_22_image_1.jpg` |
| Figure 7 | （A）真、（B）假、（C）否定的感知符号说明 | `../md/Barsalou_1999_Perceptual_Symbol_Systems_markdown/images/page_24_image_5.jpg` |
| Figure 8 | 析取（disjunction）的感知符号说明：中间区"交替模拟"马与牛实现"或" | `../md/Barsalou_1999_Perceptual_Symbol_Systems_markdown/images/page_25_image_5.jpg` |
| Figure 9 | ad hoc 范畴（换灯泡可踩之物 / 顶门之物）对同一场景中实体的不同释义 | `../md/Barsalou_1999_Perceptual_Symbol_Systems_markdown/images/page_26_image_1.jpg` |
