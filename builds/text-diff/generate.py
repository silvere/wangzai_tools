#!/usr/bin/env python3
"""Generate Text Diff Viewer HTML tool."""

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>文本对比器 | Text Diff</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0f1117;--surface:#1a1d27;--surface2:#242836;--border:#2e3348;--text:#e4e6f0;--text2:#8b8fa8;--accent:#6c7cff;--accent2:#4a57d4;--add-bg:#1a3a2a;--add-text:#4ade80;--del-bg:#3a1a1a;--del-text:#f87171;--eq-text:#8b8fa8}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
.header{padding:20px 24px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}
.header h1{font-size:20px;font-weight:600;display:flex;align-items:center;gap:8px}
.header h1 span{font-size:24px}
.controls{display:flex;gap:8px;flex-wrap:wrap}
.btn{padding:6px 14px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);cursor:pointer;font-size:13px;transition:all .15s}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn.active{background:var(--accent);border-color:var(--accent);color:#fff}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
.btn.primary:hover{background:var(--accent2)}
.main{display:flex;flex-direction:column;height:calc(100vh - 70px)}
.input-area{display:grid;grid-template-columns:1fr 1fr;gap:0;border-bottom:1px solid var(--border);min-height:200px;flex-shrink:0}
.input-panel{display:flex;flex-direction:column;position:relative}
.input-panel:first-child{border-right:1px solid var(--border)}
.input-label{padding:8px 16px;font-size:12px;color:var(--text2);background:var(--surface);border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.input-label .char-count{font-size:11px;opacity:.7}
textarea{flex:1;background:var(--surface);color:var(--text);border:none;padding:12px 16px;font-size:14px;line-height:1.6;resize:none;outline:none;font-family:inherit;min-height:150px}
textarea::placeholder{color:var(--text2);opacity:.5}
.stats-bar{padding:8px 16px;background:var(--surface);border-bottom:1px solid var(--border);display:flex;gap:20px;font-size:13px;color:var(--text2);flex-wrap:wrap;align-items:center}
.stat{display:flex;align-items:center;gap:4px}
.stat .dot{width:8px;height:8px;border-radius:50%;display:inline-block}
.dot.add{background:var(--add-text)}.dot.del{background:var(--del-text)}.dot.eq{background:var(--eq-text)}
.similarity{font-weight:600;color:var(--accent);font-size:14px}
.diff-output{flex:1;overflow:auto;padding:0}
.diff-table{width:100%;border-collapse:collapse;font-size:13px;font-family:'SF Mono',Monaco,'Cascadia Code','Fira Code',monospace}
.diff-table td{padding:2px 12px;vertical-align:top;white-space:pre-wrap;word-break:break-all;line-height:1.7}
.diff-table .ln{color:var(--text2);text-align:right;user-select:none;width:40px;min-width:40px;opacity:.5;font-size:12px;border-right:1px solid var(--border);padding-right:8px}
.diff-table .content{padding-left:12px}
.diff-table tr.add{background:var(--add-bg)}
.diff-table tr.add .content{color:var(--add-text)}
.diff-table tr.del{background:var(--del-bg)}
.diff-table tr.del .content{color:var(--del-text)}
.diff-table tr.eq .content{color:var(--eq-text)}
.diff-table tr.sep td{padding:4px 12px;color:var(--text2);font-size:11px;background:var(--surface2);border-top:1px solid var(--border);border-bottom:1px solid var(--border)}
/* inline char diff highlights */
.char-add{background:#22543d;color:#4ade80;border-radius:2px;padding:0 1px}
.char-del{background:#542222;color:#f87171;border-radius:2px;padding:0 1px;text-decoration:line-through}
/* side by side */
.side-by-side{display:grid;grid-template-columns:1fr 1fr;height:100%}
.side-panel{overflow:auto;border-right:1px solid var(--border)}
.side-panel:last-child{border-right:none}
.side-panel .diff-table{width:100%}
.empty-state{display:flex;align-items:center;justify-content:center;height:100%;color:var(--text2);font-size:15px;flex-direction:column;gap:8px}
.empty-state span{font-size:40px}
.presets{display:flex;gap:6px;flex-wrap:wrap}
.preset-btn{padding:3px 10px;border-radius:4px;border:1px solid var(--border);background:transparent;color:var(--text2);cursor:pointer;font-size:11px;transition:all .15s}
.preset-btn:hover{border-color:var(--accent);color:var(--accent)}
.toast{position:fixed;bottom:20px;right:20px;background:var(--accent);color:#fff;padding:10px 20px;border-radius:8px;font-size:13px;opacity:0;transition:opacity .3s;pointer-events:none;z-index:99}
.toast.show{opacity:1}
@media(max-width:768px){
  .input-area{grid-template-columns:1fr;min-height:auto}
  .input-panel:first-child{border-right:none;border-bottom:1px solid var(--border)}
  textarea{min-height:100px}
  .side-by-side{grid-template-columns:1fr}
  .header{padding:12px 16px}
  .header h1{font-size:16px}
}
</style>
</head>
<body>
<div class="header">
  <h1><span>🔍</span> 文本对比器</h1>
  <div class="controls">
    <div class="presets">
      <button class="preset-btn" onclick="loadPreset('model')">模型输出对比</button>
      <button class="preset-btn" onclick="loadPreset('translate')">翻译对比</button>
      <button class="preset-btn" onclick="loadPreset('code')">代码对比</button>
    </div>
    <button class="btn" id="btnWord" onclick="setMode('word')">词级</button>
    <button class="btn active" id="btnChar" onclick="setMode('char')">字符级</button>
    <button class="btn active" id="btnInline" onclick="setView('inline')">行内</button>
    <button class="btn" id="btnSide" onclick="setView('side')">并排</button>
    <button class="btn" onclick="swapTexts()">⇄ 交换</button>
    <button class="btn" onclick="copyDiff()">📋 复制</button>
    <button class="btn" onclick="clearAll()">清空</button>
  </div>
</div>
<div class="main">
  <div class="input-area">
    <div class="input-panel">
      <div class="input-label"><span>📄 原文 / 参考文本</span><span class="char-count" id="countA">0 字</span></div>
      <textarea id="textA" placeholder="粘贴原文或参考答案..." oninput="onInput()"></textarea>
    </div>
    <div class="input-panel">
      <div class="input-label"><span>📝 对比文本 / 模型输出</span><span class="char-count" id="countB">0 字</span></div>
      <textarea id="textB" placeholder="粘贴对比文本或模型输出..." oninput="onInput()"></textarea>
    </div>
  </div>
  <div class="stats-bar" id="statsBar" style="display:none">
    <span class="similarity" id="simScore"></span>
    <span class="stat"><span class="dot eq"></span> 相同: <b id="statEq">0</b></span>
    <span class="stat"><span class="dot add"></span> 新增: <b id="statAdd">0</b></span>
    <span class="stat"><span class="dot del"></span> 删除: <b id="statDel">0</b></span>
    <span class="stat">总变更: <b id="statTotal">0</b></span>
  </div>
  <div class="diff-output" id="diffOutput">
    <div class="empty-state"><span>📝</span>在上方粘贴两段文本，自动生成对比结果</div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
let mode='char',view='inline',debounceTimer=null;

const presets={
  model:{
    a:'大语言模型（LLM）是基于Transformer架构的深度学习模型，通过在大规模文本语料上进行预训练，学习语言的统计规律和语义表示。其核心能力包括文本生成、理解、推理和翻译等。',
    b:'大语言模型（LLM）是基于Transformer架构的人工智能模型，通过在海量文本数据上进行预训练，学习语言的统计模式和语义表征。其核心能力包括文本生成、语义理解、逻辑推理和机器翻译等。'
  },
  translate:{
    a:'The quick brown fox jumps over the lazy dog. This sentence contains every letter of the English alphabet.',
    b:'The swift brown fox leaps over the lazy dog. This sentence includes every letter of the English alphabet.'
  },
  code:{
    a:'def calculate(data):\n    result = []\n    for item in data:\n        if item > 0:\n            result.append(item * 2)\n    return result',
    b:'def calculate(data):\n    return [item * 2 for item in data if item > 0]'
  }
};

function setMode(m){mode=m;document.getElementById('btnWord').classList.toggle('active',m==='word');document.getElementById('btnChar').classList.toggle('active',m==='char');runDiff()}
function setView(v){view=v;document.getElementById('btnInline').classList.toggle('active',v==='inline');document.getElementById('btnSide').classList.toggle('active',v==='side');runDiff()}
function loadPreset(k){document.getElementById('textA').value=presets[k].a;document.getElementById('textB').value=presets[k].b;onInput()}
function swapTexts(){const a=document.getElementById('textA'),b=document.getElementById('textB');[a.value,b.value]=[b.value,a.value];onInput()}
function clearAll(){document.getElementById('textA').value='';document.getElementById('textB').value='';onInput()}

function onInput(){
  const a=document.getElementById('textA').value,b=document.getElementById('textB').value;
  document.getElementById('countA').textContent=a.length+' 字';
  document.getElementById('countB').textContent=b.length+' 字';
  clearTimeout(debounceTimer);
  debounceTimer=setTimeout(runDiff,200);
}

// Myers diff algorithm (optimized for small inputs)
function myersDiff(a,b){
  const N=a.length,M=b.length,MAX=N+M;
  if(MAX===0)return[];
  if(N===0)return b.map(x=>({type:'add',val:x}));
  if(M===0)return a.map(x=>({type:'del',val:x}));
  const V=new Array(2*(MAX)+1);V[MAX+1]=0;
  const trace=[];
  outer:for(let d=0;d<=MAX;d++){
    const vCopy=V.slice();trace.push(vCopy);
    for(let k=-d;k<=d;k+=2){
      let x;
      if(k===-d||(k!==d&&V[MAX+k-1]<V[MAX+k+1]))x=V[MAX+k+1];
      else x=V[MAX+k-1]+1;
      let y=x-k;
      while(x<N&&y<M&&a[x]===b[y]){x++;y++}
      V[MAX+k]=x;
      if(x>=N&&y>=M)break outer;
    }
  }
  // backtrack
  let x=N,y=M;const ops=[];
  for(let d=trace.length-1;d>0;d--){
    const k=x-y,prev=trace[d-1];
    let pk;
    if(k===-(d)||(k!==(d)&&prev[MAX+k-1]<prev[MAX+k+1]))pk=k+1;
    else pk=k-1;
    const px=prev[MAX+pk],py=px-pk;
    while(x>px&&y>py){x--;y--;ops.push({type:'eq',val:a[x]})}
    if(x>px){x--;ops.push({type:'del',val:a[x]})}
    else if(y>py){y--;ops.push({type:'add',val:b[y]})}
  }
  while(x>0&&y>0){x--;y--;ops.push({type:'eq',val:a[x]})}
  while(x>0){x--;ops.push({type:'del',val:a[x]})}
  while(y>0){y--;ops.push({type:'add',val:b[y]})}
  return ops.reverse();
}

function tokenize(text){
  if(mode==='char')return [...text];
  // word mode: split by whitespace and punctuation, keep delimiters
  return text.match(/[\u4e00-\u9fff]|[a-zA-Z0-9]+|[^\S]|[^\w\s\u4e00-\u9fff]/g)||[];
}

function runDiff(){
  const a=document.getElementById('textA').value,b=document.getElementById('textB').value;
  if(!a&&!b){
    document.getElementById('diffOutput').innerHTML='<div class="empty-state"><span>📝</span>在上方粘贴两段文本，自动生成对比结果</div>';
    document.getElementById('statsBar').style.display='none';
    return;
  }
  const tokA=tokenize(a),tokB=tokenize(b);
  const ops=myersDiff(tokA,tokB);
  let eqC=0,addC=0,delC=0;
  ops.forEach(o=>{if(o.type==='eq')eqC++;else if(o.type==='add')addC++;else delC++});
  const total=eqC+Math.max(addC,delC);
  const sim=total?Math.round(eqC/total*100):100;
  document.getElementById('statsBar').style.display='flex';
  document.getElementById('simScore').textContent='相似度 '+sim+'%';
  document.getElementById('statEq').textContent=eqC;
  document.getElementById('statAdd').textContent=addC;
  document.getElementById('statDel').textContent=delC;
  document.getElementById('statTotal').textContent=addC+delC;

  // group ops into lines
  const lines=groupIntoLines(ops);
  if(view==='inline')renderInline(lines);
  else renderSide(lines);
}

function groupIntoLines(ops){
  const lines=[];let cur=[];
  ops.forEach(o=>{
    if(o.val==='\n'){cur.push(o);lines.push(cur);cur=[]}
    else cur.push(o);
  });
  if(cur.length)lines.push(cur);
  return lines;
}

function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}

function renderInline(lines){
  let html='<table class="diff-table">';
  let lnA=1,lnB=1;
  lines.forEach(line=>{
    const types=new Set(line.map(o=>o.type));
    const hasAdd=types.has('add'),hasDel=types.has('del'),hasEq=types.has('eq');
    if(hasDel&&hasAdd){
      // mixed line - show char-level diff
      let content='';
      line.forEach(o=>{
        if(o.type==='eq')content+=esc(o.val);
        else if(o.type==='add')content+='<span class="char-add">'+esc(o.val)+'</span>';
        else content+='<span class="char-del">'+esc(o.val)+'</span>';
      });
      html+='<tr class="eq"><td class="ln">'+lnA+'</td><td class="ln">'+lnB+'</td><td class="content">'+content+'</td></tr>';
      lnA++;lnB++;
    }else if(hasDel&&!hasAdd){
      let content='';line.forEach(o=>content+=o.type==='del'?'<span class="char-del">'+esc(o.val)+'</span>':esc(o.val));
      html+='<tr class="del"><td class="ln">'+lnA+'</td><td class="ln"></td><td class="content">- '+content+'</td></tr>';
      lnA++;
    }else if(hasAdd&&!hasDel){
      let content='';line.forEach(o=>content+=o.type==='add'?'<span class="char-add">'+esc(o.val)+'</span>':esc(o.val));
      html+='<tr class="add"><td class="ln"></td><td class="ln">'+lnB+'</td><td class="content">+ '+content+'</td></tr>';
      lnB++;
    }else{
      let content='';line.forEach(o=>content+=esc(o.val));
      html+='<tr class="eq"><td class="ln">'+lnA+'</td><td class="ln">'+lnB+'</td><td class="content">  '+content+'</td></tr>';
      lnA++;lnB++;
    }
  });
  html+='</table>';
  document.getElementById('diffOutput').innerHTML=html;
}

function renderSide(lines){
  let leftHtml='<table class="diff-table">',rightHtml='<table class="diff-table">';
  let lnA=1,lnB=1;
  lines.forEach(line=>{
    const types=new Set(line.map(o=>o.type));
    const hasAdd=types.has('add'),hasDel=types.has('del');
    if(hasDel&&hasAdd){
      let lc='',rc='';
      line.forEach(o=>{
        if(o.type==='eq'){lc+=esc(o.val);rc+=esc(o.val)}
        else if(o.type==='del')lc+='<span class="char-del">'+esc(o.val)+'</span>';
        else rc+='<span class="char-add">'+esc(o.val)+'</span>';
      });
      leftHtml+='<tr class="del"><td class="ln">'+lnA+'</td><td class="content">'+lc+'</td></tr>';
      rightHtml+='<tr class="add"><td class="ln">'+lnB+'</td><td class="content">'+rc+'</td></tr>';
      lnA++;lnB++;
    }else if(hasDel){
      let c='';line.forEach(o=>c+=esc(o.val));
      leftHtml+='<tr class="del"><td class="ln">'+lnA+'</td><td class="content">'+c+'</td></tr>';
      rightHtml+='<tr class="eq"><td class="ln"></td><td class="content"></td></tr>';
      lnA++;
    }else if(hasAdd){
      let c='';line.forEach(o=>c+=esc(o.val));
      leftHtml+='<tr class="eq"><td class="ln"></td><td class="content"></td></tr>';
      rightHtml+='<tr class="add"><td class="ln">'+lnB+'</td><td class="content">'+c+'</td></tr>';
      lnB++;
    }else{
      let c='';line.forEach(o=>c+=esc(o.val));
      leftHtml+='<tr class="eq"><td class="ln">'+lnA+'</td><td class="content">'+c+'</td></tr>';
      rightHtml+='<tr class="eq"><td class="ln">'+lnB+'</td><td class="content">'+c+'</td></tr>';
      lnA++;lnB++;
    }
  });
  leftHtml+='</table>';rightHtml+='</table>';
  document.getElementById('diffOutput').innerHTML='<div class="side-by-side"><div class="side-panel">'+leftHtml+'</div><div class="side-panel">'+rightHtml+'</div></div>';
}

function copyDiff(){
  const a=document.getElementById('textA').value,b=document.getElementById('textB').value;
  if(!a&&!b)return;
  const tokA=tokenize(a),tokB=tokenize(b);
  const ops=myersDiff(tokA,tokB);
  let text='';
  ops.forEach(o=>{
    if(o.type==='eq')text+=o.val;
    else if(o.type==='add')text+='[+'+o.val+']';
    else text+='[-'+o.val+']';
  });
  navigator.clipboard.writeText(text).then(()=>showToast('已复制到剪贴板'));
}

function showToast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2000)}

// auto-run on load
onInput();
</script>
</body>
</html>'''

with open('/root/clawd/builds/text-diff/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Generated index.html ({len(html)} bytes)")
