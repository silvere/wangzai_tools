#!/usr/bin/env python3
"""Generate Eval Metrics Calculator HTML"""

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>评测指标计算器</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0f0f0f;--surface:#1a1a1a;--surface2:#242424;--border:#333;--text:#e0e0e0;--text2:#888;--accent:#58a6ff;--green:#3fb950;--yellow:#d29922;--red:#f85149;--purple:#bc8cff}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;min-height:100vh}
.header{padding:20px 24px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.header h1{font-size:20px;font-weight:600}
.toolbar{display:flex;gap:8px;margin-left:auto;flex-wrap:wrap}
.btn{padding:6px 14px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);cursor:pointer;font-size:13px;transition:all .15s}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn.primary{background:var(--accent);color:#000;border-color:var(--accent);font-weight:600}
.btn.primary:hover{opacity:.85}
.main{display:flex;flex-direction:column;padding:20px 24px;gap:20px;max-width:1100px;margin:0 auto}
.input-row{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.input-panel{display:flex;flex-direction:column;gap:6px}
.input-panel label{font-size:12px;color:var(--text2);font-weight:500}
.input-panel textarea{min-height:140px;padding:12px;background:var(--surface);color:var(--text);border:1px solid var(--border);border-radius:8px;resize:vertical;font-family:"SF Mono","Fira Code",monospace;font-size:13px;line-height:1.6;outline:none}
.input-panel textarea:focus{border-color:var(--accent)}
.input-panel textarea::placeholder{color:#555}
.metrics-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}
.metric-card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px;text-align:center;transition:border-color .2s}
.metric-card:hover{border-color:var(--accent)}
.metric-name{font-size:12px;color:var(--text2);margin-bottom:8px;font-weight:500}
.metric-value{font-size:28px;font-weight:700;font-family:"SF Mono",monospace}
.metric-bar{height:4px;background:var(--surface2);border-radius:2px;margin-top:10px;overflow:hidden}
.metric-bar-fill{height:100%;border-radius:2px;transition:width .5s ease}
.metric-detail{font-size:11px;color:var(--text2);margin-top:6px}
.score-high{color:var(--green)}.score-mid{color:var(--yellow)}.score-low{color:var(--red)}
.bar-high{background:var(--green)}.bar-mid{background:var(--yellow)}.bar-low{background:var(--red)}
.section-title{font-size:14px;font-weight:600;color:var(--text);padding-bottom:8px;border-bottom:1px solid var(--border)}
.preset-row{display:flex;gap:8px;flex-wrap:wrap}
.preset{padding:5px 12px;border-radius:16px;border:1px solid var(--border);background:transparent;color:var(--text2);font-size:12px;cursor:pointer;transition:.2s}
.preset:hover{border-color:var(--accent);color:var(--text)}
.batch-area{display:none;flex-direction:column;gap:12px}
.batch-area.show{display:flex}
.batch-table{width:100%;border-collapse:collapse;font-size:13px}
.batch-table th{text-align:left;padding:8px 12px;background:var(--surface);border-bottom:1px solid var(--border);color:var(--text2);font-weight:500;font-size:12px}
.batch-table td{padding:8px 12px;border-bottom:1px solid var(--border);font-family:"SF Mono",monospace;font-size:12px}
.batch-table tr:hover{background:var(--surface)}
.mode-tabs{display:flex;gap:0;border:1px solid var(--border);border-radius:8px;overflow:hidden;width:fit-content}
.mode-tab{padding:6px 16px;background:var(--surface);color:var(--text2);cursor:pointer;font-size:13px;border:none;transition:.2s}
.mode-tab.active{background:var(--accent);color:#000;font-weight:600}
.empty-state{text-align:center;padding:40px;color:var(--text2)}
.empty-state .icon{font-size:48px;opacity:.5;margin-bottom:12px}
.tooltip{position:relative;cursor:help;border-bottom:1px dotted var(--text2)}
.tooltip:hover::after{content:attr(data-tip);position:absolute;bottom:100%;left:50%;transform:translateX(-50%);background:var(--surface2);color:var(--text);padding:6px 10px;border-radius:6px;font-size:11px;white-space:nowrap;z-index:10;border:1px solid var(--border)}
@media(max-width:768px){.input-row{grid-template-columns:1fr}.metrics-grid{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>
<div class="header">
  <h1>📊 评测指标计算器</h1>
  <div class="toolbar">
    <div class="mode-tabs">
      <button class="mode-tab active" onclick="setMode('single')">单条对比</button>
      <button class="mode-tab" onclick="setMode('batch')">批量评测</button>
    </div>
    <button class="btn" onclick="clearAll()">🗑️ 清空</button>
    <button class="btn" onclick="copyResults()">📋 复制结果</button>
    <button class="btn primary" onclick="calculate()">计算 ⏎</button>
  </div>
</div>
<div class="main">
  <div>
    <div class="preset-row">
      <span style="font-size:12px;color:var(--text2);line-height:28px">示例：</span>
      <button class="preset" onclick="loadPreset('translate')">🌐 翻译评测</button>
      <button class="preset" onclick="loadPreset('summary')">📝 摘要评测</button>
      <button class="preset" onclick="loadPreset('qa')">❓ 问答评测</button>
      <button class="preset" onclick="loadPreset('code')">💻 代码生成</button>
    </div>
  </div>
  <div id="singleMode">
    <div class="input-row">
      <div class="input-panel">
        <label>参考文本 (Reference / Ground Truth)</label>
        <textarea id="refText" placeholder="粘贴标准答案 / 参考文本..."></textarea>
      </div>
      <div class="input-panel">
        <label>模型输出 (Candidate / Prediction)</label>
        <textarea id="candText" placeholder="粘贴模型生成的文本..."></textarea>
      </div>
    </div>
  </div>
  <div id="batchMode" class="batch-area">
    <div class="input-panel">
      <label>批量输入（每行一对，用 Tab 或 ||| 分隔 reference 和 candidate）</label>
      <textarea id="batchText" style="min-height:200px" placeholder="参考文本1\t模型输出1&#10;参考文本2\t模型输出2&#10;或&#10;参考文本1|||模型输出1&#10;参考文本2|||模型输出2"></textarea>
    </div>
  </div>
  <div id="results">
    <div class="empty-state">
      <div class="icon">📊</div>
      <p>输入参考文本和模型输出，点击「计算」查看评测指标</p>
    </div>
  </div>
</div>
<script>
// ---- Tokenization ----
function tokenize(text){
  // Chinese: character-level; English: word-level
  const tokens=[];
  const re=/[\u4e00-\u9fff\u3400-\u4dbf]|[a-zA-Z0-9]+|[^\s\u4e00-\u9fff\u3400-\u4dbf]/g;
  let m;
  while((m=re.exec(text))!==null)tokens.push(m[0].toLowerCase());
  return tokens;
}

function ngrams(tokens,n){
  const grams=[];
  for(let i=0;i<=tokens.length-n;i++)grams.push(tokens.slice(i,i+n).join(' '));
  return grams;
}

function countMap(arr){
  const m={};
  arr.forEach(x=>m[x]=(m[x]||0)+1);
  return m;
}

// ---- Metrics ----
function exactMatch(ref,cand){
  return ref.trim()===cand.trim()?1:0;
}

function bleu(ref,cand,maxN=4){
  const refTok=tokenize(ref),candTok=tokenize(cand);
  if(candTok.length===0)return{score:0,precisions:[]};
  const precisions=[];
  let logSum=0,count=0;
  for(let n=1;n<=maxN;n++){
    const cNgrams=ngrams(candTok,n);
    const rNgrams=ngrams(refTok,n);
    if(cNgrams.length===0){precisions.push(0);continue}
    const rCount=countMap(rNgrams);
    const cCount=countMap(cNgrams);
    let clip=0;
    for(const g in cCount)clip+=Math.min(cCount[g],rCount[g]||0);
    const p=clip/cNgrams.length;
    precisions.push(p);
    if(p>0){logSum+=Math.log(p);count++}
  }
  if(count===0)return{score:0,precisions};
  const bp=candTok.length>=refTok.length?1:Math.exp(1-refTok.length/candTok.length);
  const score=bp*Math.exp(logSum/count);
  return{score:Math.min(1,score),precisions};
}

function rouge1(ref,cand){
  const rTok=tokenize(ref),cTok=tokenize(cand);
  if(rTok.length===0||cTok.length===0)return{p:0,r:0,f:0};
  const rSet=countMap(rTok),cSet=countMap(cTok);
  let overlap=0;
  for(const t in cSet)overlap+=Math.min(cSet[t],rSet[t]||0);
  const p=overlap/cTok.length,r=overlap/rTok.length;
  const f=(p+r)>0?2*p*r/(p+r):0;
  return{p,r,f};
}

function rouge2(ref,cand){
  const rBi=ngrams(tokenize(ref),2),cBi=ngrams(tokenize(cand),2);
  if(rBi.length===0||cBi.length===0)return{p:0,r:0,f:0};
  const rSet=countMap(rBi),cSet=countMap(cBi);
  let overlap=0;
  for(const t in cSet)overlap+=Math.min(cSet[t],rSet[t]||0);
  const p=overlap/cBi.length,r=overlap/rBi.length;
  const f=(p+r)>0?2*p*r/(p+r):0;
  return{p,r,f};
}

function lcsLen(a,b){
  const m=a.length,n=b.length;
  const dp=Array.from({length:m+1},()=>new Uint16Array(n+1));
  for(let i=1;i<=m;i++)
    for(let j=1;j<=n;j++)
      dp[i][j]=a[i-1]===b[j-1]?dp[i-1][j-1]+1:Math.max(dp[i-1][j],dp[i][j-1]);
  return dp[m][n];
}

function rougeL(ref,cand){
  const rTok=tokenize(ref),cTok=tokenize(cand);
  if(rTok.length===0||cTok.length===0)return{p:0,r:0,f:0};
  const l=lcsLen(rTok,cTok);
  const p=l/cTok.length,r=l/rTok.length;
  const f=(p+r)>0?2*p*r/(p+r):0;
  return{p,r,f};
}

function editDistance(ref,cand){
  const a=ref,b=cand;
  const m=a.length,n=b.length;
  const dp=Array.from({length:m+1},(_,i)=>{const r=new Uint16Array(n+1);r[0]=i;return r});
  for(let j=1;j<=n;j++)dp[0][j]=j;
  for(let i=1;i<=m;i++)
    for(let j=1;j<=n;j++)
      dp[i][j]=a[i-1]===b[j-1]?dp[i-1][j-1]:1+Math.min(dp[i-1][j],dp[i][j-1],dp[i-1][j-1]);
  return dp[m][n];
}

function charF1(ref,cand){
  const rChars=ref.replace(/\s/g,'').split('');
  const cChars=cand.replace(/\s/g,'').split('');
  if(rChars.length===0||cChars.length===0)return 0;
  const rSet=countMap(rChars),cSet=countMap(cChars);
  let overlap=0;
  for(const c in cSet)overlap+=Math.min(cSet[c],rSet[c]||0);
  const p=overlap/cChars.length,r=overlap/rChars.length;
  return(p+r)>0?2*p*r/(p+r):0;
}

function jaccard(ref,cand){
  const rTok=new Set(tokenize(ref)),cTok=new Set(tokenize(cand));
  if(rTok.size===0&&cTok.size===0)return 1;
  let inter=0;
  for(const t of cTok)if(rTok.has(t))inter++;
  return inter/(rTok.size+cTok.size-inter);
}

// ---- Compute All ----
function computeAll(ref,cand){
  const b=bleu(ref,cand);
  const r1=rouge1(ref,cand);
  const r2=rouge2(ref,cand);
  const rL=rougeL(ref,cand);
  const ed=editDistance(ref,cand);
  const maxLen=Math.max(ref.length,cand.length);
  const edNorm=maxLen>0?1-ed/maxLen:1;
  return {
    exactMatch:exactMatch(ref,cand),
    bleu:b.score,
    bleu1:b.precisions[0]||0,
    bleu2:b.precisions[1]||0,
    bleu4:b.precisions[3]||0,
    rouge1F:r1.f,rouge1P:r1.p,rouge1R:r1.r,
    rouge2F:r2.f,rouge2P:r2.p,rouge2R:r2.r,
    rougeLF:rL.f,rougeLP:rL.p,rougeLR:rL.r,
    editDist:ed,editDistNorm:edNorm,
    charF1:charF1(ref,cand),
    jaccard:jaccard(ref,cand)
  };
}

// ---- Rendering ----
function scoreClass(v){return v>=0.7?'high':v>=0.4?'mid':'low'}

function metricCard(name,value,isPercent=true,tip=''){
  const display=isPercent?(value*100).toFixed(1)+'%':value;
  const sc=isPercent?scoreClass(value):scoreClass(value);
  const barW=isPercent?(value*100).toFixed(1):0;
  return `<div class="metric-card">
    <div class="metric-name">${tip?`<span class="tooltip" data-tip="${tip}">${name}</span>`:name}</div>
    <div class="metric-value score-${sc}">${display}</div>
    ${isPercent?`<div class="metric-bar"><div class="metric-bar-fill bar-${sc}" style="width:${barW}%"></div></div>`:''}
  </div>`;
}

function renderSingle(ref,cand){
  const m=computeAll(ref,cand);
  let html='<div class="section-title">核心指标</div><div class="metrics-grid">';
  html+=metricCard('Exact Match',m.exactMatch,true,'完全匹配：参考文本与模型输出是否完全一致');
  html+=metricCard('BLEU',m.bleu,true,'BLEU 综合分（1-4 gram），衡量生成文本与参考的 n-gram 重叠度');
  html+=metricCard('ROUGE-1 F1',m.rouge1F,true,'Unigram 级别的 F1，衡量词汇覆盖率');
  html+=metricCard('ROUGE-L F1',m.rougeLF,true,'基于最长公共子序列的 F1，衡量语序相似度');
  html+=metricCard('Char F1',m.charF1,true,'字符级 F1，适合中文评测');
  html+=metricCard('Jaccard',m.jaccard,true,'Jaccard 相似系数，词集合交并比');
  html+='</div>';
  html+='<div class="section-title" style="margin-top:20px">详细指标</div><div class="metrics-grid">';
  html+=metricCard('BLEU-1',m.bleu1,true,'Unigram 精确率');
  html+=metricCard('BLEU-2',m.bleu2,true,'Bigram 精确率');
  html+=metricCard('BLEU-4',m.bleu4,true,'4-gram 精确率');
  html+=metricCard('ROUGE-1 P',m.rouge1P,true,'Unigram 精确率');
  html+=metricCard('ROUGE-1 R',m.rouge1R,true,'Unigram 召回率');
  html+=metricCard('ROUGE-2 F1',m.rouge2F,true,'Bigram 级别 F1');
  html+=metricCard('ROUGE-L P',m.rougeLP,true,'LCS 精确率');
  html+=metricCard('ROUGE-L R',m.rougeLR,true,'LCS 召回率');
  html+=metricCard('Edit Dist (norm)',m.editDistNorm,true,'归一化编辑距离（1=完全相同）');
  html+=metricCard('Edit Distance',m.editDist,false,'Levenshtein 编辑距离（字符级）');
  html+='</div>';
  return html;
}

function renderBatch(pairs){
  const allMetrics=pairs.map(([r,c])=>computeAll(r,c));
  const keys=['bleu','rouge1F','rougeLF','charF1','jaccard','editDistNorm'];
  const labels=['BLEU','ROUGE-1','ROUGE-L','Char F1','Jaccard','Edit(norm)'];
  // averages
  const avgs=keys.map(k=>{
    const sum=allMetrics.reduce((s,m)=>s+m[k],0);
    return sum/allMetrics.length;
  });
  let html='<div class="section-title">平均指标（'+pairs.length+' 条）</div><div class="metrics-grid">';
  keys.forEach((k,i)=>{html+=metricCard(labels[i],avgs[i])});
  html+='</div>';
  html+='<div class="section-title" style="margin-top:20px">逐条结果</div>';
  html+='<div style="overflow-x:auto"><table class="batch-table"><thead><tr><th>#</th><th>Reference</th><th>Candidate</th>';
  labels.forEach(l=>{html+=`<th>${l}</th>`});
  html+='</tr></thead><tbody>';
  allMetrics.forEach((m,i)=>{
    const r=pairs[i][0],c=pairs[i][1];
    html+=`<tr><td>${i+1}</td><td title="${esc(r)}">${esc(r.slice(0,30))}${r.length>30?'...':''}</td><td title="${esc(c)}">${esc(c.slice(0,30))}${c.length>30?'...':''}</td>`;
    keys.forEach(k=>{
      const v=m[k];
      html+=`<td class="score-${scoreClass(v)}">${(v*100).toFixed(1)}%</td>`;
    });
    html+='</tr>';
  });
  html+='</tbody></table></div>';
  return html;
}

function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}

// ---- Actions ----
let currentMode='single';
let lastResults=null;

function setMode(mode){
  currentMode=mode;
  document.querySelectorAll('.mode-tab').forEach(t=>t.classList.toggle('active',t.textContent.includes(mode==='single'?'单条':'批量')));
  document.getElementById('singleMode').style.display=mode==='single'?'block':'none';
  document.getElementById('batchMode').classList.toggle('show',mode==='batch');
}

function calculate(){
  const out=document.getElementById('results');
  if(currentMode==='single'){
    const ref=document.getElementById('refText').value.trim();
    const cand=document.getElementById('candText').value.trim();
    if(!ref||!cand){out.innerHTML='<div class="empty-state"><div class="icon">⚠️</div><p>请输入参考文本和模型输出</p></div>';return}
    lastResults=computeAll(ref,cand);
    out.innerHTML=renderSingle(ref,cand);
  }else{
    const raw=document.getElementById('batchText').value.trim();
    if(!raw){out.innerHTML='<div class="empty-state"><div class="icon">⚠️</div><p>请输入批量数据</p></div>';return}
    const pairs=raw.split('\n').filter(l=>l.trim()).map(l=>{
      if(l.includes('|||'))return l.split('|||').map(s=>s.trim());
      if(l.includes('\t'))return l.split('\t').map(s=>s.trim());
      return [l.trim(),''];
    }).filter(p=>p.length>=2&&p[0]&&p[1]);
    if(pairs.length===0){out.innerHTML='<div class="empty-state"><div class="icon">⚠️</div><p>未检测到有效数据对</p></div>';return}
    lastResults=pairs.map(([r,c])=>computeAll(r,c));
    out.innerHTML=renderBatch(pairs);
  }
}

function clearAll(){
  document.getElementById('refText').value='';
  document.getElementById('candText').value='';
  document.getElementById('batchText').value='';
  document.getElementById('results').innerHTML='<div class="empty-state"><div class="icon">📊</div><p>输入参考文本和模型输出，点击「计算」查看评测指标</p></div>';
  lastResults=null;
}

function copyResults(){
  if(!lastResults)return;
  let text='';
  if(currentMode==='single'&&!Array.isArray(lastResults)){
    const m=lastResults;
    text=`Exact Match: ${(m.exactMatch*100).toFixed(1)}%\nBLEU: ${(m.bleu*100).toFixed(1)}%\nBLEU-1: ${(m.bleu1*100).toFixed(1)}%\nBLEU-2: ${(m.bleu2*100).toFixed(1)}%\nBLEU-4: ${(m.bleu4*100).toFixed(1)}%\nROUGE-1 F1: ${(m.rouge1F*100).toFixed(1)}%\nROUGE-2 F1: ${(m.rouge2F*100).toFixed(1)}%\nROUGE-L F1: ${(m.rougeLF*100).toFixed(1)}%\nChar F1: ${(m.charF1*100).toFixed(1)}%\nJaccard: ${(m.jaccard*100).toFixed(1)}%\nEdit Distance: ${m.editDist}\nEdit Dist (norm): ${(m.editDistNorm*100).toFixed(1)}%`;
  }else if(Array.isArray(lastResults)){
    const keys=['bleu','rouge1F','rougeLF','charF1','jaccard','editDistNorm'];
    const labels=['BLEU','ROUGE-1','ROUGE-L','Char F1','Jaccard','Edit(norm)'];
    text='#\t'+labels.join('\t')+'\n';
    lastResults.forEach((m,i)=>{
      text+=(i+1)+'\t'+keys.map(k=>(m[k]*100).toFixed(1)+'%').join('\t')+'\n';
    });
    const avgs=keys.map(k=>(lastResults.reduce((s,m)=>s+m[k],0)/lastResults.length*100).toFixed(1)+'%');
    text+='AVG\t'+avgs.join('\t');
  }
  navigator.clipboard.writeText(text).then(()=>{
    const btn=document.querySelector('.toolbar .btn:nth-child(3)');
    const orig=btn.textContent;btn.textContent='✅ 已复制';
    setTimeout(()=>btn.textContent=orig,1500);
  });
}

const PRESETS={
  translate:{
    ref:'机器学习是人工智能的一个分支，它使计算机系统能够从数据中学习并改进，而无需进行明确的编程。',
    cand:'机器学习是AI的一个子领域，让计算机可以从数据中自动学习和提升，不需要显式编程。'
  },
  summary:{
    ref:'本文提出了一种新的注意力机制，通过多头自注意力实现序列到序列的建模，在机器翻译任务上取得了显著的性能提升，同时大幅减少了训练时间。',
    cand:'论文介绍了多头注意力机制用于序列建模，在翻译任务中表现优异且训练更快。'
  },
  qa:{
    ref:'Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年首次发布。它强调代码可读性，支持多种编程范式，包括面向对象、函数式和过程式编程。',
    cand:'Python 是 Guido van Rossum 创建的高级编程语言，1991 年发布。它注重可读性，支持面向对象和函数式编程。'
  },
  code:{
    ref:'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)',
    cand:'def fibonacci(n):\n    if n < 2:\n        return n\n    a, b = 0, 1\n    for _ in range(n-1):\n        a, b = b, a+b\n    return b'
  }
};

function loadPreset(key){
  setMode('single');
  document.getElementById('refText').value=PRESETS[key].ref;
  document.getElementById('candText').value=PRESETS[key].cand;
  calculate();
}

document.addEventListener('keydown',e=>{
  if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();calculate()}
});
</script>
</body>
</html>'''

with open('/root/clawd/builds/eval-metrics/index.html','w',encoding='utf-8') as f:
    f.write(html)
print(f"OK {len(html)} bytes")
