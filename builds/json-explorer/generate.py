#!/usr/bin/env python3
"""Generate JSON Explorer HTML tool."""

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JSON 浏览器 | JSON Explorer</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0f1117;--surface:#1a1d27;--surface2:#242836;--border:#2e3348;--text:#e4e6f0;--text2:#8b8fa8;--accent:#6c7cff;--accent2:#4a57d4;--str:#a5d6a7;--num:#ffcc80;--bool:#80deea;--null:#ef9a9a;--key:#90caf9;--bracket:#8b8fa8;--match-bg:#6c7cff33;--match-border:#6c7cff}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column;overflow:hidden}
.header{padding:12px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;flex-shrink:0}
.header h1{font-size:18px;font-weight:600;display:flex;align-items:center;gap:8px}
.header h1 span{font-size:22px}
.toolbar{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.btn{padding:5px 12px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);cursor:pointer;font-size:12px;transition:all .15s;white-space:nowrap}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn.active{background:var(--accent);border-color:var(--accent);color:#fff}
.search-box{padding:5px 10px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:12px;width:180px;outline:none}
.search-box:focus{border-color:var(--accent)}
.search-box::placeholder{color:var(--text2);opacity:.5}
.body{flex:1;display:flex;overflow:hidden}
.input-panel{width:40%;border-right:1px solid var(--border);display:flex;flex-direction:column;flex-shrink:0;position:relative}
.input-panel.collapsed{width:0;min-width:0;overflow:hidden;border-right:none}
.tree-panel{flex:1;display:flex;flex-direction:column;overflow:hidden}
.panel-header{padding:6px 14px;font-size:11px;color:var(--text2);background:var(--surface);border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;flex-shrink:0}
textarea{flex:1;background:var(--surface);color:var(--text);border:none;padding:12px 14px;font-size:13px;line-height:1.6;resize:none;outline:none;font-family:'SF Mono',Monaco,'Cascadia Code','Fira Code',monospace;tab-size:2}
textarea::placeholder{color:var(--text2);opacity:.4}
.tree-container{flex:1;overflow:auto;padding:8px 0;font-family:'SF Mono',Monaco,'Cascadia Code','Fira Code',monospace;font-size:13px;line-height:1.8}
.error-bar{padding:8px 14px;background:#3a1a1a;color:#f87171;font-size:12px;border-bottom:1px solid #5a2a2a;display:none;flex-shrink:0}
.stats-bar{padding:4px 14px;font-size:11px;color:var(--text2);background:var(--surface);border-top:1px solid var(--border);flex-shrink:0;display:flex;gap:16px}
/* tree nodes */
.node{padding-left:20px;position:relative}
.node-line{display:flex;align-items:flex-start;padding:0 14px;cursor:default;border-radius:0}
.node-line:hover{background:var(--surface2)}
.node-line.matched{background:var(--match-bg);box-shadow:inset 2px 0 0 var(--match-border)}
.toggle{width:16px;height:16px;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;color:var(--text2);font-size:10px;flex-shrink:0;margin-right:2px;user-select:none;border-radius:3px;margin-top:3px}
.toggle:hover{background:var(--surface2);color:var(--accent)}
.toggle.leaf{visibility:hidden}
.k{color:var(--key)}.s{color:var(--str)}.n{color:var(--num)}.b{color:var(--bool)}.nl{color:var(--null)}.br{color:var(--bracket)}
.colon{color:var(--text2);margin:0 4px}
.comma{color:var(--text2)}
.count{color:var(--text2);font-size:11px;margin-left:4px;opacity:.6}
.copy-path{opacity:0;margin-left:6px;cursor:pointer;color:var(--text2);font-size:11px;transition:opacity .15s}
.node-line:hover .copy-path{opacity:1}
.copy-path:hover{color:var(--accent)}
.collapsed-preview{color:var(--text2);font-size:12px;opacity:.6}
.path-bar{padding:4px 14px;font-size:11px;color:var(--accent);background:var(--surface);border-top:1px solid var(--border);flex-shrink:0;font-family:'SF Mono',Monaco,monospace;min-height:24px;cursor:pointer}
.path-bar:hover{color:var(--text)}
.toast{position:fixed;bottom:20px;right:20px;background:var(--accent);color:#fff;padding:8px 18px;border-radius:8px;font-size:12px;opacity:0;transition:opacity .3s;pointer-events:none;z-index:99}
.toast.show{opacity:1}
.empty-state{display:flex;align-items:center;justify-content:center;height:100%;color:var(--text2);font-size:14px;flex-direction:column;gap:8px}
.empty-state span{font-size:36px}
.resize-handle{width:4px;cursor:col-resize;background:transparent;position:absolute;right:0;top:0;bottom:0;z-index:10}
.resize-handle:hover{background:var(--accent);opacity:.3}
@media(max-width:768px){
  .input-panel{width:100%;border-right:none;border-bottom:1px solid var(--border);max-height:40vh}
  .body{flex-direction:column}
  .search-box{width:120px}
}
</style>
</head>
<body>
<div class="header">
  <h1><span>🔮</span> JSON 浏览器</h1>
  <div class="toolbar">
    <input class="search-box" id="searchBox" placeholder="搜索键名或值..." oninput="onSearch()">
    <button class="btn" onclick="expandAll()">全部展开</button>
    <button class="btn" onclick="collapseAll()">全部折叠</button>
    <button class="btn" onclick="formatJSON()">格式化</button>
    <button class="btn" onclick="minifyJSON()">压缩</button>
    <button class="btn" onclick="copyAll()">📋 复制</button>
    <button class="btn" onclick="loadSample()">示例</button>
    <button class="btn" onclick="toggleInput()">⇄ 切换面板</button>
  </div>
</div>
<div class="body">
  <div class="input-panel" id="inputPanel">
    <div class="panel-header"><span>📝 粘贴 JSON</span><span id="inputStats"></span></div>
    <textarea id="jsonInput" placeholder='粘贴 JSON 数据...\n\n支持对象、数组、嵌套结构\n自动解析，实时渲染树形视图' oninput="onInputChange()"></textarea>
    <div class="resize-handle" id="resizeHandle"></div>
  </div>
  <div class="tree-panel">
    <div class="error-bar" id="errorBar"></div>
    <div class="panel-header"><span>🌳 树形视图</span><span id="treeStats"></span></div>
    <div class="tree-container" id="treeContainer">
      <div class="empty-state"><span>🔮</span>粘贴 JSON 数据，自动生成可交互的树形视图<br><small style="opacity:.5">支持折叠/展开、搜索、点击复制路径</small></div>
    </div>
    <div class="path-bar" id="pathBar" onclick="copyCurrentPath()" title="点击复制路径">&nbsp;</div>
    <div class="stats-bar" id="statsBar"></div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
let parsedData=null,currentPath='',debounceTimer=null,matchCount=0;

const sample={
  "model":"gpt-4o",
  "choices":[{
    "index":0,
    "message":{"role":"assistant","content":"大语言模型是基于Transformer架构的深度学习模型。"},
    "finish_reason":"stop",
    "logprobs":null
  }],
  "usage":{"prompt_tokens":128,"completion_tokens":64,"total_tokens":192},
  "system_fingerprint":"fp_abc123",
  "created":1708588800,
  "metadata":{"latency_ms":1250,"region":"us-east-1","cached":false,"tags":["eval","benchmark"],"scores":{"bleu":0.72,"rouge_l":0.85,"similarity":0.91}}
};

function loadSample(){document.getElementById('jsonInput').value=JSON.stringify(sample,null,2);onInputChange()}

function onInputChange(){
  clearTimeout(debounceTimer);
  debounceTimer=setTimeout(parseAndRender,150);
}

function parseAndRender(){
  const raw=document.getElementById('jsonInput').value.trim();
  const errBar=document.getElementById('errorBar');
  if(!raw){
    parsedData=null;
    document.getElementById('treeContainer').innerHTML='<div class="empty-state"><span>🔮</span>粘贴 JSON 数据，自动生成可交互的树形视图<br><small style="opacity:.5">支持折叠/展开、搜索、点击复制路径</small></div>';
    errBar.style.display='none';
    document.getElementById('statsBar').innerHTML='';
    document.getElementById('inputStats').textContent='';
    return;
  }
  try{
    parsedData=JSON.parse(raw);
    errBar.style.display='none';
    document.getElementById('inputStats').textContent=raw.length.toLocaleString()+' 字符';
    renderTree();
  }catch(e){
    errBar.textContent='⚠️ JSON 解析错误: '+e.message;
    errBar.style.display='block';
    parsedData=null;
  }
}

function countNodes(v){
  if(v===null||typeof v!=='object')return 1;
  let c=1;
  if(Array.isArray(v))v.forEach(i=>c+=countNodes(i));
  else Object.values(v).forEach(i=>c+=countNodes(i));
  return c;
}

function getDepth(v,d){
  if(v===null||typeof v!=='object')return d;
  let max=d;
  if(Array.isArray(v))v.forEach(i=>{const dd=getDepth(i,d+1);if(dd>max)max=dd});
  else Object.values(v).forEach(i=>{const dd=getDepth(i,d+1);if(dd>max)max=dd});
  return max;
}

function renderTree(){
  if(!parsedData&&parsedData!==0&&parsedData!==false&&parsedData!=='')return;
  const container=document.getElementById('treeContainer');
  const nodes=countNodes(parsedData);
  const depth=getDepth(parsedData,0);
  container.innerHTML=buildNode(parsedData,'$','',true,false);
  document.getElementById('treeStats').textContent=nodes+' 节点 · 深度 '+depth;
  document.getElementById('statsBar').innerHTML='<span>节点: '+nodes+'</span><span>深度: '+depth+'</span><span>类型: '+(Array.isArray(parsedData)?'Array':'Object')+'</span>';
  onSearch();
}

function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}

function buildNode(val,path,key,isLast,showKey){
  const id='n'+Math.random().toString(36).substr(2,8);
  if(val===null)return line(id,path,key,showKey,'<span class="nl">null</span>',isLast,true);
  if(typeof val==='boolean')return line(id,path,key,showKey,'<span class="b">'+val+'</span>',isLast,true);
  if(typeof val==='number')return line(id,path,key,showKey,'<span class="n">'+val+'</span>',isLast,true);
  if(typeof val==='string'){
    const display=val.length>120?esc(val.substring(0,120))+'…':esc(val);
    return line(id,path,key,showKey,'<span class="s">"'+display+'"</span>',isLast,true);
  }
  if(Array.isArray(val)){
    const open='<span class="br">[</span><span class="count">'+val.length+' items</span>';
    const close='<span class="br">]</span>';
    let children='';
    val.forEach((item,i)=>{
      const cp=path+'['+i+']';
      children+=buildNode(item,cp,i,i===val.length-1,true);
    });
    return collapsible(id,path,key,showKey,open,close,children,isLast,val.length===0);
  }
  if(typeof val==='object'){
    const keys=Object.keys(val);
    const open='<span class="br">{</span><span class="count">'+keys.length+' keys</span>';
    const close='<span class="br">}</span>';
    let children='';
    keys.forEach((k,i)=>{
      const cp=path+'.'+k;
      children+=buildNode(val[k],cp,k,i===keys.length-1,true);
    });
    return collapsible(id,path,key,showKey,open,close,children,isLast,keys.length===0);
  }
  return '';
}

function line(id,path,key,showKey,valHtml,isLast,isLeaf){
  const comma=isLast?'':'<span class="comma">,</span>';
  const keyHtml=showKey?'<span class="k">"'+esc(key)+'"</span><span class="colon">:</span> ':'';
  return '<div class="node-line'+(isLeaf?' leaf':'')+'" data-path="'+esc(path)+'" onmouseenter="showPath(this)" onclick="selectNode(this)">'+
    '<span class="toggle leaf">▶</span>'+keyHtml+valHtml+comma+
    '<span class="copy-path" onclick="event.stopPropagation();copyPath(\''+esc(path).replace(/'/g,"\\'")+'\')">📋</span></div>';
}

function collapsible(id,path,key,showKey,openHtml,closeHtml,children,isLast,isEmpty){
  const comma=isLast?'':'<span class="comma">,</span>';
  const keyHtml=showKey?'<span class="k">"'+esc(key)+'"</span><span class="colon">:</span> ':'';
  if(isEmpty){
    const emptyContent=openHtml.includes('[')?'<span class="br">[]</span>':'<span class="br">{}</span>';
    return '<div class="node-line" data-path="'+esc(path)+'" onmouseenter="showPath(this)">'+
      '<span class="toggle leaf">▶</span>'+keyHtml+emptyContent+comma+
      '<span class="copy-path" onclick="event.stopPropagation();copyPath(\''+esc(path).replace(/'/g,"\\'")+'\')">📋</span></div>';
  }
  return '<div class="node-line" data-path="'+esc(path)+'" onmouseenter="showPath(this)" onclick="toggleNode(\''+id+'\',this)">'+
    '<span class="toggle" id="t_'+id+'">▼</span>'+keyHtml+openHtml+
    '<span class="copy-path" onclick="event.stopPropagation();copyPath(\''+esc(path).replace(/'/g,"\\'")+'\')">📋</span></div>'+
    '<div class="node" id="c_'+id+'">'+children+
    '<div class="node-line"><span class="toggle leaf">▶</span>'+closeHtml+comma+'</div></div>';
}

function toggleNode(id,el){
  const c=document.getElementById('c_'+id);
  const t=document.getElementById('t_'+id);
  if(!c)return;
  if(c.style.display==='none'){c.style.display='';t.textContent='▼'}
  else{c.style.display='none';t.textContent='▶'}
}

function expandAll(){document.querySelectorAll('.node').forEach(n=>n.style.display='');document.querySelectorAll('.toggle:not(.leaf)').forEach(t=>t.textContent='▼')}
function collapseAll(){document.querySelectorAll('.node').forEach(n=>n.style.display='none');document.querySelectorAll('.toggle:not(.leaf)').forEach(t=>t.textContent='▶')}

function showPath(el){
  const p=el.dataset.path;
  if(p){currentPath=p;document.getElementById('pathBar').textContent=p||'\u00a0'}
}

function selectNode(el){
  const p=el.dataset.path;
  if(p)copyPath(p);
}

function copyPath(p){
  navigator.clipboard.writeText(p).then(()=>showToast('已复制路径: '+p));
}

function copyCurrentPath(){
  if(currentPath)navigator.clipboard.writeText(currentPath).then(()=>showToast('已复制: '+currentPath));
}

function copyAll(){
  if(!parsedData)return;
  navigator.clipboard.writeText(JSON.stringify(parsedData,null,2)).then(()=>showToast('已复制格式化 JSON'));
}

function formatJSON(){
  if(!parsedData)return;
  document.getElementById('jsonInput').value=JSON.stringify(parsedData,null,2);
}

function minifyJSON(){
  if(!parsedData)return;
  document.getElementById('jsonInput').value=JSON.stringify(parsedData);
}

function toggleInput(){
  document.getElementById('inputPanel').classList.toggle('collapsed');
}

function onSearch(){
  const q=document.getElementById('searchBox').value.trim().toLowerCase();
  matchCount=0;
  document.querySelectorAll('.node-line').forEach(el=>{
    el.classList.remove('matched');
    if(q&&el.textContent.toLowerCase().includes(q)){
      el.classList.add('matched');
      matchCount++;
      // expand parents
      let p=el.parentElement;
      while(p){
        if(p.classList&&p.classList.contains('node')){
          p.style.display='';
          const tid=p.id.replace('c_','t_');
          const t=document.getElementById(tid);
          if(t)t.textContent='▼';
        }
        p=p.parentElement;
      }
    }
  });
  const searchBox=document.getElementById('searchBox');
  if(q)searchBox.style.borderColor=matchCount?'var(--accent)':'#f87171';
  else searchBox.style.borderColor='var(--border)';
}

function showToast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2000)}

// resize handle
const handle=document.getElementById('resizeHandle');
let resizing=false;
handle.addEventListener('mousedown',e=>{resizing=true;e.preventDefault()});
document.addEventListener('mousemove',e=>{
  if(!resizing)return;
  const panel=document.getElementById('inputPanel');
  const w=Math.max(200,Math.min(e.clientX,window.innerWidth-300));
  panel.style.width=w+'px';
});
document.addEventListener('mouseup',()=>resizing=false);

// paste handler - auto parse
document.getElementById('jsonInput').addEventListener('paste',()=>setTimeout(onInputChange,50));
</script>
</body>
</html>'''

with open('/root/clawd/builds/json-explorer/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Generated index.html ({len(html)} bytes)")
