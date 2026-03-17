#!/usr/bin/env python3
"""Generate Mermaid Live Editor HTML tool."""

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mermaid 实时编辑器 | Mermaid Live</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0f1117;--surface:#1a1d27;--surface2:#242836;--border:#2e3348;--text:#e4e6f0;--text2:#8b8fa8;--accent:#6c7cff;--accent2:#4a57d4;--err:#f87171;--ok:#4ade80}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column;overflow:hidden}
.header{padding:10px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;flex-shrink:0}
.header h1{font-size:17px;font-weight:600;display:flex;align-items:center;gap:8px}
.header h1 span{font-size:20px}
.toolbar{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.btn{padding:5px 12px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);cursor:pointer;font-size:12px;transition:all .15s;white-space:nowrap}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn.active{background:var(--accent);border-color:var(--accent);color:#fff}
select.btn{appearance:none;padding-right:24px;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%238b8fa8' d='M3 5l3 3 3-3'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 8px center}
.body{flex:1;display:flex;overflow:hidden}
.editor-panel{width:40%;border-right:1px solid var(--border);display:flex;flex-direction:column;flex-shrink:0}
.preview-panel{flex:1;display:flex;flex-direction:column;overflow:hidden}
.panel-header{padding:6px 14px;font-size:11px;color:var(--text2);background:var(--surface);border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-shrink:0}
textarea{flex:1;background:var(--surface);color:var(--text);border:none;padding:12px 14px;font-size:13px;line-height:1.7;resize:none;outline:none;font-family:'SF Mono',Monaco,'Cascadia Code','Fira Code',monospace;tab-size:2}
textarea::placeholder{color:var(--text2);opacity:.4}
.preview-container{flex:1;overflow:auto;display:flex;align-items:center;justify-content:center;padding:20px;background:#fff}
.preview-container.dark{background:var(--surface)}
.preview-container svg{max-width:100%;height:auto}
.error-bar{padding:8px 14px;background:#3a1a1a;color:var(--err);font-size:12px;border-top:1px solid #5a2a2a;display:none;flex-shrink:0;max-height:80px;overflow:auto;font-family:monospace}
.status-bar{padding:4px 14px;font-size:11px;color:var(--text2);background:var(--surface);border-top:1px solid var(--border);flex-shrink:0;display:flex;justify-content:space-between}
.status-dot{width:6px;height:6px;border-radius:50%;display:inline-block;margin-right:4px}
.status-dot.ok{background:var(--ok)}.status-dot.err{background:var(--err)}
.toast{position:fixed;bottom:20px;right:20px;background:var(--accent);color:#fff;padding:8px 18px;border-radius:8px;font-size:12px;opacity:0;transition:opacity .3s;pointer-events:none;z-index:99}
.toast.show{opacity:1}
.templates-dropdown{position:relative;display:inline-block}
.templates-menu{display:none;position:absolute;top:100%;left:0;margin-top:4px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:4px 0;z-index:50;min-width:200px;max-height:300px;overflow:auto;box-shadow:0 8px 24px rgba(0,0,0,.4)}
.templates-menu.show{display:block}
.templates-menu .item{padding:6px 14px;font-size:12px;cursor:pointer;color:var(--text);display:flex;align-items:center;gap:6px}
.templates-menu .item:hover{background:var(--accent);color:#fff}
.templates-menu .item .tag{font-size:10px;color:var(--text2);background:var(--surface);padding:1px 6px;border-radius:3px}
.templates-menu .item:hover .tag{background:rgba(255,255,255,.2);color:#fff}
@media(max-width:768px){
  .body{flex-direction:column}
  .editor-panel{width:100%;max-height:40vh;border-right:none;border-bottom:1px solid var(--border)}
}
</style>
</head>
<body>
<div class="header">
  <h1><span>🧜‍♀️</span> Mermaid 实时编辑器</h1>
  <div class="toolbar">
    <div class="templates-dropdown">
      <button class="btn" onclick="toggleTemplates()">📋 模板 ▾</button>
      <div class="templates-menu" id="templatesMenu">
        <div class="item" onclick="loadTemplate('flowchart')">流程图 <span class="tag">flowchart</span></div>
        <div class="item" onclick="loadTemplate('sequence')">时序图 <span class="tag">sequence</span></div>
        <div class="item" onclick="loadTemplate('class')">类图 <span class="tag">class</span></div>
        <div class="item" onclick="loadTemplate('state')">状态图 <span class="tag">state</span></div>
        <div class="item" onclick="loadTemplate('er')">ER 图 <span class="tag">erDiagram</span></div>
        <div class="item" onclick="loadTemplate('gantt')">甘特图 <span class="tag">gantt</span></div>
        <div class="item" onclick="loadTemplate('pie')">饼图 <span class="tag">pie</span></div>
        <div class="item" onclick="loadTemplate('git')">Git 图 <span class="tag">gitGraph</span></div>
        <div class="item" onclick="loadTemplate('mindmap')">思维导图 <span class="tag">mindmap</span></div>
        <div class="item" onclick="loadTemplate('llm-eval')">LLM 评测流程 <span class="tag">flowchart</span></div>
      </div>
    </div>
    <button class="btn" id="btnDark" onclick="toggleBg()">🌙 深色背景</button>
    <button class="btn" onclick="exportSVG()">💾 导出 SVG</button>
    <button class="btn" onclick="exportPNG()">🖼️ 导出 PNG</button>
    <button class="btn" onclick="copySVG()">📋 复制 SVG</button>
  </div>
</div>
<div class="body">
  <div class="editor-panel">
    <div class="panel-header"><span>✏️ Mermaid 语法</span><span id="lineCount">0 行</span></div>
    <textarea id="editor" placeholder="输入 Mermaid 语法...\n\n例如:\nflowchart TD\n    A[开始] --> B{判断}\n    B -->|是| C[执行]\n    B -->|否| D[结束]" oninput="onEdit()" onkeydown="handleTab(event)"></textarea>
  </div>
  <div class="preview-panel">
    <div class="panel-header"><span>👁️ 预览</span><span id="renderTime"></span></div>
    <div class="preview-container" id="preview"></div>
    <div class="error-bar" id="errorBar"></div>
    <div class="status-bar">
      <span><span class="status-dot ok" id="statusDot"></span><span id="statusText">就绪</span></span>
      <span>Mermaid.js v11</span>
    </div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
<script>
mermaid.initialize({startOnLoad:false,theme:'default',securityLevel:'loose',fontFamily:'system-ui'});

const templates={
flowchart:`flowchart TD
    A[🚀 开始] --> B{条件判断}
    B -->|条件1| C[处理 A]
    B -->|条件2| D[处理 B]
    C --> E[合并]
    D --> E
    E --> F[✅ 结束]`,
sequence:`sequenceDiagram
    participant U as 👤 用户
    participant F as 🖥️ 前端
    participant B as ⚙️ 后端
    participant D as 🗄️ 数据库
    U->>F: 发起请求
    F->>B: API 调用
    B->>D: 查询数据
    D-->>B: 返回结果
    B-->>F: JSON 响应
    F-->>U: 渲染页面`,
'class':`classDiagram
    class LLM {
        +String name
        +int parameters
        +float temperature
        +generate(prompt) String
        +embed(text) Vector
    }
    class Evaluator {
        +String benchmark
        +evaluate(model) Score
        +compare(models) Report
    }
    class Dataset {
        +String name
        +int size
        +load() List
        +sample(n) List
    }
    LLM --> Evaluator : 被评测
    Dataset --> Evaluator : 提供数据`,
state:`stateDiagram-v2
    [*] --> 待处理
    待处理 --> 评测中 : 开始评测
    评测中 --> 人工审核 : 自动评测完成
    评测中 --> 失败 : 评测出错
    人工审核 --> 已通过 : 审核通过
    人工审核 --> 待修改 : 需要修改
    待修改 --> 评测中 : 重新评测
    失败 --> 待处理 : 重试
    已通过 --> [*]`,
er:`erDiagram
    MODEL ||--o{ EVALUATION : "被评测"
    EVALUATION }|--|| BENCHMARK : "使用"
    BENCHMARK ||--|{ TASK : "包含"
    EVALUATION ||--|{ RESULT : "产生"
    RESULT }|--|| METRIC : "度量"
    MODEL {
        string name
        int params
        string provider
    }
    BENCHMARK {
        string name
        string category
        int task_count
    }`,
gantt:`gantt
    title 项目排期
    dateFormat YYYY-MM-DD
    section 需求
        需求分析     :a1, 2026-03-01, 5d
        方案设计     :a2, after a1, 3d
    section 开发
        前端开发     :b1, after a2, 10d
        后端开发     :b2, after a2, 12d
        联调测试     :b3, after b2, 5d
    section 上线
        灰度发布     :c1, after b3, 3d
        全量上线     :milestone, after c1, 0d`,
pie:`pie title 模型 API 调用分布
    "GPT-4o" : 35
    "Claude 3.5" : 28
    "Gemini Pro" : 18
    "DeepSeek" : 12
    "其他" : 7`,
git:`gitGraph
    commit id: "init"
    branch feature/eval
    commit id: "add benchmark"
    commit id: "add metrics"
    checkout main
    commit id: "hotfix"
    merge feature/eval
    commit id: "release v1.0"
    branch feature/report
    commit id: "add charts"
    checkout main
    merge feature/report
    commit id: "release v1.1"`,
mindmap:`mindmap
  root((LLM 评测))
    代码能力
      HumanEval
      MBPP
      SWE-bench
      LiveCodeBench
    推理与数学
      GSM8K
      MATH
      AIME
      ARC-AGI
    知识理解
      MMLU
      GPQA
      SimpleQA
    Agent
      WebArena
      GAIA
      Tau-bench`,
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
    style J fill:#3a2a1a,color:#ffcc80`
};

let debounceTimer=null,darkBg=false;

function loadTemplate(key){
  document.getElementById('editor').value=templates[key];
  toggleTemplates();
  onEdit();
}

function toggleTemplates(){
  document.getElementById('templatesMenu').classList.toggle('show');
}
document.addEventListener('click',e=>{
  if(!e.target.closest('.templates-dropdown'))document.getElementById('templatesMenu').classList.remove('show');
});

function handleTab(e){
  if(e.key==='Tab'){
    e.preventDefault();
    const t=e.target,s=t.selectionStart,end=t.selectionEnd;
    t.value=t.value.substring(0,s)+'  '+t.value.substring(end);
    t.selectionStart=t.selectionEnd=s+2;
    onEdit();
  }
}

function onEdit(){
  const code=document.getElementById('editor').value;
  const lines=code.split('\n').length;
  document.getElementById('lineCount').textContent=lines+' 行';
  clearTimeout(debounceTimer);
  debounceTimer=setTimeout(()=>renderDiagram(code),300);
}

async function renderDiagram(code){
  if(!code.trim()){
    document.getElementById('preview').innerHTML='<div style="color:#8b8fa8;text-align:center"><div style="font-size:36px;margin-bottom:8px">🧜‍♀️</div>输入 Mermaid 语法开始绘图</div>';
    document.getElementById('errorBar').style.display='none';
    document.getElementById('statusDot').className='status-dot ok';
    document.getElementById('statusText').textContent='就绪';
    return;
  }
  const start=performance.now();
  try{
    const{svg}=await mermaid.render('mermaid-'+Date.now(),code);
    document.getElementById('preview').innerHTML=svg;
    document.getElementById('errorBar').style.display='none';
    document.getElementById('statusDot').className='status-dot ok';
    const ms=Math.round(performance.now()-start);
    document.getElementById('statusText').textContent='渲染成功';
    document.getElementById('renderTime').textContent=ms+'ms';
  }catch(err){
    document.getElementById('errorBar').textContent='⚠️ '+err.message;
    document.getElementById('errorBar').style.display='block';
    document.getElementById('statusDot').className='status-dot err';
    document.getElementById('statusText').textContent='语法错误';
    document.getElementById('renderTime').textContent='';
  }
}

function toggleBg(){
  darkBg=!darkBg;
  document.getElementById('preview').classList.toggle('dark',darkBg);
  document.getElementById('btnDark').textContent=darkBg?'☀️ 浅色背景':'🌙 深色背景';
}

function getSVG(){return document.getElementById('preview').querySelector('svg')}

function exportSVG(){
  const svg=getSVG();if(!svg)return;
  const blob=new Blob([svg.outerHTML],{type:'image/svg+xml'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download='mermaid-diagram.svg';a.click();
  showToast('SVG 已下载');
}

function exportPNG(){
  const svg=getSVG();if(!svg)return;
  const canvas=document.createElement('canvas');
  const bbox=svg.getBoundingClientRect();
  const scale=2;
  canvas.width=bbox.width*scale;canvas.height=bbox.height*scale;
  const ctx=canvas.getContext('2d');
  ctx.scale(scale,scale);
  const img=new Image();
  const svgData='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg.outerHTML);
  img.onload=()=>{
    ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.drawImage(img,0,0,bbox.width,bbox.height);
    const a=document.createElement('a');a.href=canvas.toDataURL('image/png');
    a.download='mermaid-diagram.png';a.click();
    showToast('PNG 已下载 (2x)');
  };
  img.src=svgData;
}

function copySVG(){
  const svg=getSVG();if(!svg)return;
  navigator.clipboard.writeText(svg.outerHTML).then(()=>showToast('SVG 已复制到剪贴板'));
}

function showToast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2000)}

// Load default template
document.getElementById('editor').value=templates.flowchart;
onEdit();
</script>
</body>
</html>'''

with open('/root/clawd/builds/mermaid-live/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Generated index.html ({len(html)} bytes)")
