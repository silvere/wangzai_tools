#!/usr/bin/env python3
"""Generate QR Code Studio HTML tool."""

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>二维码工坊 | QR Studio</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0f1117;--surface:#1a1d27;--surface2:#242836;--border:#2e3348;--text:#e4e6f0;--text2:#8b8fa8;--accent:#6c7cff;--accent2:#4a57d4}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
.header{padding:16px 24px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px}
.header h1{font-size:18px;font-weight:600;display:flex;align-items:center;gap:8px}
.main{max-width:900px;margin:0 auto;padding:20px;display:flex;gap:20px;flex-wrap:wrap}
.panel{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px;flex:1;min-width:300px}
.panel h2{font-size:14px;color:var(--text2);margin-bottom:14px;display:flex;align-items:center;gap:6px}
.form-group{margin-bottom:14px}
.form-group label{display:block;font-size:12px;color:var(--text2);margin-bottom:4px}
textarea,input[type=text],input[type=url],input[type=number],select{width:100%;padding:8px 10px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);font-size:13px;outline:none;font-family:inherit}
textarea{min-height:80px;resize:vertical;line-height:1.5}
textarea:focus,input:focus,select:focus{border-color:var(--accent)}
select{appearance:none;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%238b8fa8' d='M3 5l3 3 3-3'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 10px center;padding-right:28px}
.tabs{display:flex;gap:4px;margin-bottom:14px;flex-wrap:wrap}
.tab{padding:6px 12px;border-radius:6px;border:1px solid var(--border);background:transparent;color:var(--text2);cursor:pointer;font-size:12px;transition:all .15s}
.tab:hover{border-color:var(--accent);color:var(--accent)}
.tab.active{background:var(--accent);border-color:var(--accent);color:#fff}
.color-row{display:flex;gap:10px;align-items:center}
.color-row input[type=color]{width:36px;height:30px;border:1px solid var(--border);border-radius:6px;background:var(--surface2);cursor:pointer;padding:2px}
.color-row input[type=text]{flex:1}
.presets{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}
.preset{width:24px;height:24px;border-radius:50%;cursor:pointer;border:2px solid transparent;transition:all .15s}
.preset:hover,.preset.active{border-color:var(--accent);transform:scale(1.15)}
.slider-row{display:flex;align-items:center;gap:10px}
.slider-row input[type=range]{flex:1;accent-color:var(--accent)}
.slider-row span{font-size:12px;color:var(--text2);min-width:30px;text-align:right}
.preview-area{display:flex;flex-direction:column;align-items:center;gap:14px}
.qr-canvas-wrap{background:#fff;border-radius:12px;padding:20px;display:inline-block}
#qrCanvas{display:block}
.btn-row{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}
.btn{padding:7px 16px;border-radius:6px;border:1px solid var(--border);background:var(--surface2);color:var(--text);cursor:pointer;font-size:12px;transition:all .15s}
.btn:hover{border-color:var(--accent);color:var(--accent)}
.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
.btn.primary:hover{background:var(--accent2)}
.wifi-fields,.vcard-fields,.email-fields{display:none}
.wifi-fields.show,.vcard-fields.show,.email-fields.show{display:block}
.toast{position:fixed;bottom:20px;right:20px;background:var(--accent);color:#fff;padding:8px 18px;border-radius:8px;font-size:12px;opacity:0;transition:opacity .3s;pointer-events:none;z-index:99}
.toast.show{opacity:1}
.info{font-size:11px;color:var(--text2);text-align:center;margin-top:6px}
@media(max-width:700px){.main{flex-direction:column}.panel{min-width:auto}}
</style>
</head>
<body>
<div class="header">
  <h1><span>📱</span> 二维码工坊</h1>
</div>
<div class="main">
  <div class="panel">
    <h2>📝 内容</h2>
    <div class="tabs" id="typeTabs">
      <button class="tab active" onclick="setType('text')">文本</button>
      <button class="tab" onclick="setType('url')">网址</button>
      <button class="tab" onclick="setType('wifi')">WiFi</button>
      <button class="tab" onclick="setType('vcard')">名片</button>
      <button class="tab" onclick="setType('email')">邮件</button>
    </div>

    <div class="form-group" id="textGroup">
      <textarea id="textInput" placeholder="输入文本、网址或任意内容..." oninput="generate()">https://github.com</textarea>
    </div>

    <div class="wifi-fields" id="wifiFields">
      <div class="form-group"><label>WiFi 名称 (SSID)</label><input type="text" id="wifiSSID" placeholder="MyWiFi" oninput="generate()"></div>
      <div class="form-group"><label>密码</label><input type="text" id="wifiPass" placeholder="password123" oninput="generate()"></div>
      <div class="form-group"><label>加密方式</label>
        <select id="wifiEnc" onchange="generate()"><option value="WPA">WPA/WPA2</option><option value="WEP">WEP</option><option value="nopass">无密码</option></select>
      </div>
    </div>

    <div class="vcard-fields" id="vcardFields">
      <div class="form-group"><label>姓名</label><input type="text" id="vcName" placeholder="张三" oninput="generate()"></div>
      <div class="form-group"><label>手机</label><input type="text" id="vcPhone" placeholder="13800138000" oninput="generate()"></div>
      <div class="form-group"><label>邮箱</label><input type="text" id="vcEmail" placeholder="zhangsan@example.com" oninput="generate()"></div>
      <div class="form-group"><label>公司</label><input type="text" id="vcOrg" placeholder="某科技公司" oninput="generate()"></div>
      <div class="form-group"><label>职位</label><input type="text" id="vcTitle" placeholder="高级工程师" oninput="generate()"></div>
    </div>

    <div class="email-fields" id="emailFields">
      <div class="form-group"><label>收件人</label><input type="text" id="emailTo" placeholder="someone@example.com" oninput="generate()"></div>
      <div class="form-group"><label>主题</label><input type="text" id="emailSubj" placeholder="Hello" oninput="generate()"></div>
      <div class="form-group"><label>正文</label><textarea id="emailBody" placeholder="邮件内容..." oninput="generate()" style="min-height:50px"></textarea></div>
    </div>

    <h2 style="margin-top:18px">🎨 样式</h2>
    <div class="form-group">
      <label>配色预设</label>
      <div class="presets" id="colorPresets"></div>
    </div>
    <div class="form-group">
      <label>前景色</label>
      <div class="color-row">
        <input type="color" id="fgColor" value="#000000" oninput="syncColor('fg');generate()">
        <input type="text" id="fgHex" value="#000000" oninput="syncHex('fg');generate()">
      </div>
    </div>
    <div class="form-group">
      <label>背景色</label>
      <div class="color-row">
        <input type="color" id="bgColor" value="#ffffff" oninput="syncColor('bg');generate()">
        <input type="text" id="bgHex" value="#ffffff" oninput="syncHex('bg');generate()">
      </div>
    </div>
    <div class="form-group">
      <label>尺寸</label>
      <div class="slider-row">
        <input type="range" id="sizeSlider" min="120" max="500" value="280" oninput="generate()">
        <span id="sizeVal">280</span>
      </div>
    </div>
    <div class="form-group">
      <label>容错级别</label>
      <select id="ecLevel" onchange="generate()">
        <option value="L">L - 7% (小尺寸)</option>
        <option value="M" selected>M - 15% (推荐)</option>
        <option value="Q">Q - 25% (高容错)</option>
        <option value="H">H - 30% (最高容错)</option>
      </select>
    </div>
  </div>

  <div class="panel">
    <h2>👁️ 预览</h2>
    <div class="preview-area">
      <div class="qr-canvas-wrap" id="qrWrap">
        <canvas id="qrCanvas" width="280" height="280"></canvas>
      </div>
      <div class="info" id="qrInfo"></div>
      <div class="btn-row">
        <button class="btn primary" onclick="downloadPNG()">💾 下载 PNG</button>
        <button class="btn" onclick="downloadSVG()">📐 下载 SVG</button>
        <button class="btn" onclick="copyImage()">📋 复制图片</button>
      </div>
    </div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script src="https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.min.js"></script>
<script>
let currentType='text';
const colorPresets=[
  {fg:'#000000',bg:'#ffffff',name:'经典黑白'},
  {fg:'#1a1a2e',bg:'#e8e8f0',name:'深蓝'},
  {fg:'#2d6a4f',bg:'#d8f3dc',name:'森林绿'},
  {fg:'#6c3483',bg:'#f4ecf7',name:'优雅紫'},
  {fg:'#c0392b',bg:'#fdedec',name:'中国红'},
  {fg:'#1565c0',bg:'#e3f2fd',name:'天空蓝'},
  {fg:'#e65100',bg:'#fff3e0',name:'暖橙'},
  {fg:'#4a148c',bg:'#f3e5f5',name:'薰衣草'},
  {fg:'#004d40',bg:'#e0f2f1',name:'薄荷'},
  {fg:'#bf360c',bg:'#fbe9e7',name:'陶土'},
];

function initPresets(){
  const c=document.getElementById('colorPresets');
  colorPresets.forEach((p,i)=>{
    const d=document.createElement('div');
    d.className='preset'+(i===0?' active':'');
    d.style.background=`linear-gradient(135deg, ${p.fg} 50%, ${p.bg} 50%)`;
    d.title=p.name;
    d.onclick=()=>{
      document.querySelectorAll('.preset').forEach(x=>x.classList.remove('active'));
      d.classList.add('active');
      document.getElementById('fgColor').value=p.fg;
      document.getElementById('fgHex').value=p.fg;
      document.getElementById('bgColor').value=p.bg;
      document.getElementById('bgHex').value=p.bg;
      generate();
    };
    c.appendChild(d);
  });
}

function setType(t){
  currentType=t;
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.querySelector(`.tab[onclick="setType('${t}')"]`).classList.add('active');
  document.getElementById('textGroup').style.display=(t==='text'||t==='url')?'block':'none';
  document.getElementById('wifiFields').className='wifi-fields'+(t==='wifi'?' show':'');
  document.getElementById('vcardFields').className='vcard-fields'+(t==='vcard'?' show':'');
  document.getElementById('emailFields').className='email-fields'+(t==='email'?' show':'');
  if(t==='url')document.getElementById('textInput').placeholder='https://example.com';
  else if(t==='text')document.getElementById('textInput').placeholder='输入文本、网址或任意内容...';
  generate();
}

function getContent(){
  if(currentType==='text'||currentType==='url')return document.getElementById('textInput').value;
  if(currentType==='wifi'){
    const s=document.getElementById('wifiSSID').value;
    const p=document.getElementById('wifiPass').value;
    const e=document.getElementById('wifiEnc').value;
    return `WIFI:T:${e};S:${s};P:${p};;`;
  }
  if(currentType==='vcard'){
    const n=document.getElementById('vcName').value;
    const p=document.getElementById('vcPhone').value;
    const e=document.getElementById('vcEmail').value;
    const o=document.getElementById('vcOrg').value;
    const t=document.getElementById('vcTitle').value;
    return `BEGIN:VCARD\nVERSION:3.0\nFN:${n}\nTEL:${p}\nEMAIL:${e}\nORG:${o}\nTITLE:${t}\nEND:VCARD`;
  }
  if(currentType==='email'){
    const to=document.getElementById('emailTo').value;
    const s=document.getElementById('emailSubj').value;
    const b=document.getElementById('emailBody').value;
    return `mailto:${to}?subject=${encodeURIComponent(s)}&body=${encodeURIComponent(b)}`;
  }
  return '';
}

function syncColor(t){
  const v=document.getElementById(t+'Color').value;
  document.getElementById(t+'Hex').value=v;
}
function syncHex(t){
  let v=document.getElementById(t+'Hex').value;
  if(/^#[0-9a-fA-F]{6}$/.test(v))document.getElementById(t+'Color').value=v;
}

function generate(){
  const content=getContent();
  const size=parseInt(document.getElementById('sizeSlider').value);
  document.getElementById('sizeVal').textContent=size;
  const fg=document.getElementById('fgColor').value;
  const bg=document.getElementById('bgColor').value;
  const ec=document.getElementById('ecLevel').value;
  const canvas=document.getElementById('qrCanvas');
  canvas.width=size;canvas.height=size;
  const ctx=canvas.getContext('2d');

  if(!content){
    ctx.fillStyle=bg;ctx.fillRect(0,0,size,size);
    ctx.fillStyle='#ccc';ctx.font='14px sans-serif';ctx.textAlign='center';
    ctx.fillText('输入内容生成二维码',size/2,size/2);
    return;
  }

  try{
    const ecMap={L:1,M:0,Q:3,H:2};
    const qr=qrcode(0,ecMap[ec]||0);
    qr.addData(content);
    qr.make();
    const count=qr.getModuleCount();
    const cellSize=size/count;
    ctx.fillStyle=bg;ctx.fillRect(0,0,size,size);
    ctx.fillStyle=fg;
    for(let r=0;r<count;r++){
      for(let c=0;c<count;c++){
        if(qr.isDark(r,c)){
          ctx.fillRect(c*cellSize,r*cellSize,cellSize+0.5,cellSize+0.5);
        }
      }
    }
    const bytes=new Blob([content]).size;
    document.getElementById('qrInfo').textContent=`${count}×${count} 模块 · ${bytes} 字节 · 容错 ${ec}`;
    document.getElementById('qrWrap').style.background=bg;
  }catch(e){
    ctx.fillStyle='#fff';ctx.fillRect(0,0,size,size);
    ctx.fillStyle='#f87171';ctx.font='13px sans-serif';ctx.textAlign='center';
    ctx.fillText('内容过长，请减少文本或降低容错级别',size/2,size/2);
    document.getElementById('qrInfo').textContent='⚠️ 生成失败';
  }
}

function downloadPNG(){
  const canvas=document.getElementById('qrCanvas');
  const a=document.createElement('a');
  a.href=canvas.toDataURL('image/png');
  a.download='qrcode.png';a.click();
  showToast('PNG 已下载');
}

function downloadSVG(){
  const content=getContent();if(!content)return;
  const ec=document.getElementById('ecLevel').value;
  const fg=document.getElementById('fgColor').value;
  const bg=document.getElementById('bgColor').value;
  const size=parseInt(document.getElementById('sizeSlider').value);
  try{
    const ecMap={L:1,M:0,Q:3,H:2};
    const qr=qrcode(0,ecMap[ec]||0);
    qr.addData(content);qr.make();
    const count=qr.getModuleCount();
    const cell=size/count;
    let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">`;
    svg+=`<rect width="${size}" height="${size}" fill="${bg}"/>`;
    for(let r=0;r<count;r++){
      for(let c=0;c<count;c++){
        if(qr.isDark(r,c))svg+=`<rect x="${c*cell}" y="${r*cell}" width="${cell}" height="${cell}" fill="${fg}"/>`;
      }
    }
    svg+=`</svg>`;
    const blob=new Blob([svg],{type:'image/svg+xml'});
    const a=document.createElement('a');a.href=URL.createObjectURL(blob);
    a.download='qrcode.svg';a.click();
    showToast('SVG 已下载');
  }catch(e){showToast('生成失败')}
}

function copyImage(){
  const canvas=document.getElementById('qrCanvas');
  canvas.toBlob(blob=>{
    navigator.clipboard.write([new ClipboardItem({'image/png':blob})]).then(()=>showToast('图片已复制到剪贴板'));
  });
}

function showToast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2000)}

initPresets();
generate();
</script>
</body>
</html>'''

with open('/root/clawd/builds/qr-studio/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"Generated index.html ({len(html)} bytes)")
