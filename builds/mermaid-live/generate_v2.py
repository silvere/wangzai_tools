#!/usr/bin/env python3
"""Generate Mermaid Live Editor V2 with rich templates."""

# Templates organized by category
templates_js = r'''const templates={
// === 基础图表 ===
flowchart:`flowchart TD
    A[🚀 开始] --> B{条件判断}
    B -->|条件1| C[处理 A]
    B -->|条件2| D[处理 B]
    B -->|条件3| E[处理 C]
    C --> F[合并结果]
    D --> F
    E --> F
    F --> G{验证}
    G -->|通过| H[✅ 完成]
    G -->|失败| B`,

sequence:`sequenceDiagram
    participant U as 👤 用户
    participant F as 🖥️ 前端
    participant G as 🔀 网关
    participant B as ⚙️ 后端
    participant C as 📦 缓存
    participant D as 🗄️ 数据库
    U->>F: 发起请求
    F->>G: API 调用
    G->>C: 查缓存
    alt 缓存命中
        C-->>G: 返回缓存
        G-->>F: 200 OK
    else 缓存未命中
        G->>B: 转发请求
        B->>D: 查询数据
        D-->>B: 返回结果
        B-->>G: JSON 响应
        G->>C: 写入缓存
        G-->>F: 200 OK
    end
    F-->>U: 渲染页面`,

'class':`classDiagram
    class LLM {
        +String name
        +int parameters
        +float temperature
        +generate(prompt) String
        +embed(text) Vector
        +finetune(dataset) void
    }
    class Evaluator {
        +String benchmark
        +List~Metric~ metrics
        +evaluate(model) Score
        +compare(models) Report
        +export(format) File
    }
    class Dataset {
        +String name
        +int size
        +String format
        +load() List
        +sample(n) List
        +split(ratio) Tuple
    }
    class Metric {
        <<interface>>
        +compute(pred, ref) float
        +name() String
    }
    LLM --> Evaluator : 被评测
    Dataset --> Evaluator : 提供数据
    Metric --> Evaluator : 计算指标
    Metric <|.. BLEU
    Metric <|.. ROUGE
    Metric <|.. PassAtK`,

state:`stateDiagram-v2
    [*] --> 待处理
    待处理 --> 评测中 : 开始评测
    评测中 --> 自动评分 : 推理完成
    评测中 --> 失败 : 运行出错
    自动评分 --> 人工审核 : 低置信度
    自动评分 --> 已通过 : 高置信度
    人工审核 --> 已通过 : 审核通过
    人工审核 --> 待修改 : 需要修改
    待修改 --> 评测中 : 重新评测
    失败 --> 待处理 : 重试
    已通过 --> 归档 : 记录结果
    归档 --> [*]`,

er:`erDiagram
    MODEL ||--o{ EVALUATION : "被评测"
    EVALUATION }|--|| BENCHMARK : "使用"
    BENCHMARK ||--|{ TASK : "包含"
    EVALUATION ||--|{ RESULT : "产生"
    RESULT }|--|| METRIC : "度量"
    USER ||--o{ EVALUATION : "发起"
    MODEL {
        string name PK
        int params
        string provider
        date release_date
    }
    BENCHMARK {
        string name PK
        string category
        int task_count
        string version
    }
    EVALUATION {
        int id PK
        datetime created_at
        string status
        float overall_score
    }`,

gantt:`gantt
    title 项目排期
    dateFormat YYYY-MM-DD
    section 需求
        需求分析           :a1, 2026-03-01, 5d
        方案设计           :a2, after a1, 3d
        技术评审           :milestone, after a2, 0d
    section 开发
        前端开发           :b1, after a2, 10d
        后端开发           :b2, after a2, 12d
        API 联调           :b3, after b1, 3d
        联调测试           :b4, after b2, 5d
    section 测试
        功能测试           :c1, after b4, 5d
        性能测试           :c2, after c1, 3d
        安全审计           :c3, after c1, 2d
    section 上线
        灰度发布           :d1, after c2, 3d
        全量上线           :milestone, after d1, 0d`,

pie:`pie title 模型 API 调用分布
    "GPT-4o" : 35
    "Claude 3.5" : 28
    "Gemini Pro" : 18
    "DeepSeek" : 12
    "其他" : 7`,

git:`gitGraph
    commit id: "init"
    branch develop
    commit id: "setup CI"
    branch feature/eval
    commit id: "add benchmark"
    commit id: "add metrics"
    commit id: "add tests"
    checkout develop
    merge feature/eval
    branch feature/report
    commit id: "add charts"
    commit id: "add export"
    checkout develop
    merge feature/report
    checkout main
    merge develop tag: "v1.0"
    branch hotfix
    commit id: "fix scoring"
    checkout main
    merge hotfix tag: "v1.0.1"`,

mindmap:`mindmap
  root((LLM 评测体系))
    代码能力
      HumanEval / MBPP
      SWE-bench
      LiveCodeBench
      Terminal-Bench
    推理与数学
      GSM8K / MATH
      AIME 2024
      ARC-AGI
      ZebraLogic
    知识理解
      MMLU / MMLU-Pro
      GPQA
      SimpleQA
      Humanity Last Exam
    Agent
      WebArena
      GAIA
      Tau-bench
    多模态
      MMMU
      MathVista
      Video-MME
    安全
      TruthfulQA
      BBQ`,

// === 软件工程 ===
'ci-cd':`flowchart LR
    A[📝 Git Push] --> B[🔍 Lint & Format]
    B --> C[🧪 单元测试]
    C --> D[🏗️ 构建镜像]
    D --> E{测试通过?}
    E -->|是| F[📦 推送镜像]
    E -->|否| G[❌ 通知开发者]
    F --> H[🚀 部署 Staging]
    H --> I[🧪 集成测试]
    I --> J{通过?}
    J -->|是| K[✅ 部署 Production]
    J -->|否| G
    G --> A

    style K fill:#1a3a2a,color:#4ade80
    style G fill:#3a1a1a,color:#f87171`,

microservice:`flowchart TD
    Client[📱 客户端] --> Gateway[🔀 API Gateway]
    Gateway --> Auth[🔐 认证服务]
    Gateway --> UserSvc[👤 用户服务]
    Gateway --> OrderSvc[🛒 订单服务]
    Gateway --> PaySvc[💳 支付服务]
    Gateway --> NotifySvc[📧 通知服务]
    UserSvc --> UserDB[(👤 用户DB)]
    OrderSvc --> OrderDB[(🛒 订单DB)]
    PaySvc --> PayDB[(💳 支付DB)]
    OrderSvc --> MQ[📨 消息队列]
    MQ --> NotifySvc
    MQ --> PaySvc
    OrderSvc --> Cache[⚡ Redis]
    UserSvc --> Cache

    style Gateway fill:#4a57d4,color:#fff
    style MQ fill:#d4a74a,color:#fff
    style Cache fill:#d44a4a,color:#fff`,

'api-flow':`sequenceDiagram
    participant C as 📱 Client
    participant LB as ⚖️ Load Balancer
    participant S1 as ⚙️ Server 1
    participant S2 as ⚙️ Server 2
    participant DB as 🗄️ Database
    participant MQ as 📨 Message Queue

    C->>LB: POST /api/evaluate
    LB->>S1: 转发请求
    S1->>DB: 保存任务
    S1->>MQ: 发布评测任务
    S1-->>C: 202 Accepted (task_id)
    MQ->>S2: 消费任务
    S2->>S2: 执行评测
    S2->>DB: 保存结果
    S2->>MQ: 发布完成事件
    Note over C: 轮询结果...
    C->>LB: GET /api/result/{id}
    LB->>S1: 转发
    S1->>DB: 查询结果
    S1-->>C: 200 OK (results)`,

'docker-arch':`flowchart TD
    subgraph Host["🖥️ 宿主机"]
        Docker[🐳 Docker Engine]
        subgraph Net["🌐 Bridge Network"]
            Nginx[📡 Nginx:80]
            App1[⚙️ App:8080]
            App2[⚙️ App:8081]
            Redis[⚡ Redis:6379]
            PG[🐘 Postgres:5432]
        end
        V1[(📁 Volume: data)]
        V2[(📁 Volume: logs)]
    end
    User[👤 用户] --> Nginx
    Nginx --> App1
    Nginx --> App2
    App1 --> Redis
    App2 --> Redis
    App1 --> PG
    App2 --> PG
    PG --> V1
    App1 --> V2`,

// === 数据与AI ===
'ml-pipeline':`flowchart TD
    A[📊 原始数据] --> B[🧹 数据清洗]
    B --> C[🔄 特征工程]
    C --> D[✂️ 数据分割]
    D --> E[Train Set 80%]
    D --> F[Val Set 10%]
    D --> G[Test Set 10%]
    E --> H[🤖 模型训练]
    F --> I[📈 验证调参]
    H --> I
    I --> J{指标达标?}
    J -->|否| K[🔧 调整超参]
    K --> H
    J -->|是| L[🧪 测试集评估]
    G --> L
    L --> M[📦 模型导出]
    M --> N[🚀 部署上线]
    N --> O[📊 监控告警]
    O -->|数据漂移| A

    style N fill:#1a3a2a,color:#4ade80
    style O fill:#3a2a1a,color:#ffcc80`,

'rag-arch':`flowchart TD
    User[👤 用户提问] --> Router{🔀 意图路由}
    Router -->|知识问答| RAG[📚 RAG 流程]
    Router -->|闲聊| Chat[💬 直接对话]
    Router -->|工具调用| Tool[🔧 Agent]

    subgraph RAG Flow
        RAG --> Embed[🔢 Query Embedding]
        Embed --> Search[🔍 向量检索]
        Search --> Rerank[📊 重排序]
        Rerank --> Context[📄 上下文组装]
    end

    subgraph Knowledge Base
        Doc[📄 文档] --> Chunk[✂️ 分块]
        Chunk --> VecEmbed[🔢 Embedding]
        VecEmbed --> VecDB[(🗄️ 向量数据库)]
        Search --> VecDB
    end

    Context --> LLM[🤖 LLM 生成]
    Chat --> LLM
    Tool --> LLM
    LLM --> Answer[💡 回答用户]

    style LLM fill:#4a57d4,color:#fff
    style VecDB fill:#d4a74a,color:#fff`,

'data-flow':`flowchart LR
    subgraph Sources["📥 数据源"]
        API[🌐 API]
        DB[🗄️ 数据库]
        File[📁 文件]
        Stream[📡 实时流]
    end
    subgraph ETL["🔄 ETL"]
        Extract[提取]
        Transform[转换]
        Load[加载]
    end
    subgraph Storage["📦 存储"]
        DW[(🏢 数据仓库)]
        DL[(🌊 数据湖)]
    end
    subgraph Analytics["📊 分析"]
        BI[📈 BI 报表]
        ML[🤖 机器学习]
        Ad[🔍 即席查询]
    end

    API --> Extract
    DB --> Extract
    File --> Extract
    Stream --> Extract
    Extract --> Transform
    Transform --> Load
    Load --> DW
    Load --> DL
    DW --> BI
    DW --> Ad
    DL --> ML`,

// === 产品与业务 ===
'user-journey':`journey
    title 用户使用 LLM 评测平台的旅程
    section 注册
      访问官网: 5: 用户
      注册账号: 3: 用户
      邮箱验证: 2: 用户
    section 首次使用
      阅读文档: 3: 用户
      上传数据集: 4: 用户
      选择模型: 5: 用户
      运行评测: 5: 用户
    section 查看结果
      查看报告: 5: 用户
      对比模型: 5: 用户
      导出结果: 4: 用户
    section 持续使用
      设置定时评测: 4: 用户
      邀请团队: 3: 用户
      升级套餐: 2: 用户`,

'login-flow':`flowchart TD
    A[👤 用户访问] --> B{已登录?}
    B -->|是| C[🏠 进入首页]
    B -->|否| D[📝 登录页面]
    D --> E{登录方式}
    E -->|账号密码| F[输入账号密码]
    E -->|手机验证码| G[输入手机号]
    E -->|第三方| H[OAuth 授权]
    F --> I{验证}
    G --> J[发送验证码] --> K[输入验证码] --> I
    H --> L[跳转授权页] --> M[授权回调] --> I
    I -->|成功| N[生成 Token]
    I -->|失败| O{重试次数}
    O -->|< 5次| D
    O -->|>= 5次| P[🔒 账号锁定]
    N --> Q[写入 Cookie]
    Q --> C

    style C fill:#1a3a2a,color:#4ade80
    style P fill:#3a1a1a,color:#f87171`,

'sprint':`gantt
    title Sprint 2026-03 迭代计划
    dateFormat YYYY-MM-DD
    axisFormat %m/%d

    section 🔴 P0 紧急
        修复评测结果不一致    :crit, p0_1, 2026-03-01, 2d
        修复并发超时问题      :crit, p0_2, 2026-03-01, 3d

    section 🟡 P1 重要
        新增 MMLU-Pro 支持    :p1_1, after p0_1, 4d
        评测报告导出 PDF      :p1_2, after p0_2, 3d
        模型对比可视化        :p1_3, after p1_1, 3d

    section 🟢 P2 优化
        优化评测速度          :p2_1, after p1_2, 5d
        UI 暗色主题           :p2_2, after p1_3, 2d
        文档更新              :p2_3, after p2_2, 2d

    section 📋 里程碑
        Sprint Review         :milestone, 2026-03-15, 0d`,

// === LLM 专用 ===
'llm-eval':`flowchart TD
    A[📝 准备评测数据] --> B[🤖 模型推理]
    B --> C{自动评测}
    C -->|BLEU/ROUGE| D[指标计算]
    C -->|GPT-4 Judge| E[LLM 评分]
    C -->|代码执行| F[Pass@k]
    D --> G[📊 汇总报告]
    E --> G
    F --> G
    G --> H{达标?}
    H -->|是| I[✅ 发布模型]
    H -->|否| J[🔄 调优迭代]
    J --> B

    style A fill:#1a3a5c,color:#fff
    style I fill:#1a3a2a,color:#4ade80
    style J fill:#3a2a1a,color:#ffcc80`,

'llm-train':`flowchart TD
    subgraph Pretrain["📚 预训练"]
        D1[🌐 网页数据] --> Clean[🧹 数据清洗]
        D2[📖 书籍] --> Clean
        D3[💻 代码] --> Clean
        Clean --> Tok[🔤 Tokenizer]
        Tok --> PT[🏋️ 预训练]
    end

    subgraph Align["🎯 对齐"]
        PT --> SFT[📝 SFT 微调]
        SFT --> RM[🏆 奖励模型]
        RM --> RLHF[🔄 RLHF/DPO]
    end

    subgraph Eval["📊 评测"]
        RLHF --> Auto[🤖 自动评测]
        RLHF --> Human[👤 人工评测]
        RLHF --> Arena[⚔️ Arena 对战]
    end

    Auto --> Deploy{达标?}
    Human --> Deploy
    Arena --> Deploy
    Deploy -->|是| Ship[🚀 发布]
    Deploy -->|否| SFT

    style PT fill:#4a57d4,color:#fff
    style RLHF fill:#d44a7a,color:#fff
    style Ship fill:#1a3a2a,color:#4ade80`,

'prompt-eng':`flowchart TD
    Task[📋 任务需求] --> V1[✏️ Prompt V1]
    V1 --> Test1[🧪 测试]
    Test1 --> Analyze1{效果如何?}
    Analyze1 -->|差| Technique{优化技巧}
    Analyze1 -->|好| Deploy[🚀 部署]

    Technique -->|结构化| CoT[Chain-of-Thought]
    Technique -->|示例| FewShot[Few-Shot]
    Technique -->|角色| Role[角色设定]
    Technique -->|约束| Format[输出格式约束]
    Technique -->|分解| Decompose[任务分解]

    CoT --> V2[✏️ Prompt V2]
    FewShot --> V2
    Role --> V2
    Format --> V2
    Decompose --> V2
    V2 --> Test2[🧪 测试]
    Test2 --> Analyze2{效果如何?}
    Analyze2 -->|差| Technique
    Analyze2 -->|好| Deploy

    style Deploy fill:#1a3a2a,color:#4ade80`,

'agent-arch':`flowchart TD
    User[👤 用户] --> Agent[🤖 Agent]

    subgraph Agent Core
        Agent --> Plan[📋 规划]
        Plan --> Think[🧠 推理]
        Think --> Act[⚡ 执行]
        Act --> Observe[👁️ 观察]
        Observe --> Think
    end

    subgraph Tools["🔧 工具箱"]
        Act --> Search[🔍 搜索]
        Act --> Code[💻 代码执行]
        Act --> Browse[🌐 浏览器]
        Act --> File[📁 文件操作]
        Act --> API[🔌 API 调用]
        Act --> DB[🗄️ 数据库]
    end

    subgraph Memory["💾 记忆"]
        Observe --> STM[短期记忆]
        Observe --> LTM[长期记忆]
        STM --> Think
        LTM --> Think
    end

    Observe --> |任务完成| Result[💡 返回结果]
    Result --> User

    style Agent fill:#4a57d4,color:#fff`
};'''

# Template menu HTML with categories
menu_html = '''<div class="templates-menu" id="templatesMenu">
        <div class="cat">📐 基础图表</div>
        <div class="item" onclick="loadTemplate('flowchart')">流程图 <span class="tag">flowchart</span></div>
        <div class="item" onclick="loadTemplate('sequence')">时序图 <span class="tag">sequence</span></div>
        <div class="item" onclick="loadTemplate('class')">类图 <span class="tag">class</span></div>
        <div class="item" onclick="loadTemplate('state')">状态图 <span class="tag">state</span></div>
        <div class="item" onclick="loadTemplate('er')">ER 图 <span class="tag">erDiagram</span></div>
        <div class="item" onclick="loadTemplate('gantt')">甘特图 <span class="tag">gantt</span></div>
        <div class="item" onclick="loadTemplate('pie')">饼图 <span class="tag">pie</span></div>
        <div class="item" onclick="loadTemplate('git')">Git 图 <span class="tag">gitGraph</span></div>
        <div class="item" onclick="loadTemplate('mindmap')">思维导图 <span class="tag">mindmap</span></div>
        <div class="cat">🏗️ 软件工程</div>
        <div class="item" onclick="loadTemplate('ci-cd')">CI/CD 流水线 <span class="tag">flowchart</span></div>
        <div class="item" onclick="loadTemplate('microservice')">微服务架构 <span class="tag">flowchart</span></div>
        <div class="item" onclick="loadTemplate('api-flow')">API 调用流程 <span class="tag">sequence</span></div>
        <div class="item" onclick="loadTemplate('docker-arch')">Docker 部署 <span class="tag">flowchart</span></div>
        <div class="cat">🤖 数据与 AI</div>
        <div class="item" onclick="loadTemplate('ml-pipeline')">ML 训练流水线 <span class="tag">flowchart</span></div>
        <div class="item" onclick="loadTemplate('rag-arch')">RAG 架构 <span class="tag">flowchart</span></div>
        <div class="item" onclick="loadTemplate('data-flow')">数据流架构 <span class="tag">flowchart</span></div>
        <div class="cat">📋 产品与业务</div>
        <div class="item" onclick="loadTemplate('user-journey')">用户旅程 <span class="tag">journey</span></div>
        <div class="item" onclick="loadTemplate('login-flow')">登录流程 <span class="tag">flowchart</span></div>
        <div class="item" onclick="loadTemplate('sprint')">Sprint 排期 <span class="tag">gantt</span></div>
        <div class="cat">🧠 LLM 专用</div>
        <div class="item" onclick="loadTemplate('llm-eval')">LLM 评测流程 <span class="tag">flowchart</span></div>
        <div class="item" onclick="loadTemplate('llm-train')">LLM 训练全流程 <span class="tag">flowchart</span></div>
        <div class="item" onclick="loadTemplate('prompt-eng')">Prompt 工程迭代 <span class="tag">flowchart</span></div>
        <div class="item" onclick="loadTemplate('agent-arch')">Agent 架构 <span class="tag">flowchart</span></div>
      </div>'''

# Read original HTML and replace templates + menu
with open('/root/clawd/builds/mermaid-live/index.html', 'r') as f:
    html = f.read()

# Add category style
cat_style = '''.templates-menu .cat{padding:6px 14px 3px;font-size:10px;color:var(--accent);font-weight:600;text-transform:uppercase;letter-spacing:.5px;margin-top:4px}
.templates-menu .cat:first-child{margin-top:0}'''

html = html.replace('.templates-menu .item:hover .tag{background:rgba(255,255,255,.2);color:#fff}',
    '.templates-menu .item:hover .tag{background:rgba(255,255,255,.2);color:#fff}\n' + cat_style)

# Replace menu - need to also increase max-height
html = html.replace('max-height:300px', 'max-height:450px')

# Replace the menu HTML
import re
html = re.sub(
    r'<div class="templates-menu" id="templatesMenu">.*?</div>\s*</div>\s*</div>',
    menu_html + '\n    </div>',
    html,
    flags=re.DOTALL,
    count=1
)

# Replace templates JS
html = re.sub(
    r'const templates=\{.*?\};',
    templates_js,
    html,
    flags=re.DOTALL,
    count=1
)

with open('/root/clawd/builds/mermaid-live/index.html', 'w') as f:
    f.write(html)

print(f"Updated index.html ({len(html)} bytes) with {templates_js.count('`:')} templates")
