#!/usr/bin/env python3
"""Generate Workout Interval Timer HTML"""

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>💪 健身间歇计时器</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;-webkit-tap-highlight-color:transparent}
:root{--bg:#0a0a0f;--surface:#141418;--border:#252530;--text:#e8e8f0;--dim:#666;--work:#ef4444;--rest:#22c55e;--prep:#3b82f6;--done:#a855f7}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;min-height:100vh;display:flex;flex-direction:column;user-select:none;overflow:hidden}
.app{display:flex;flex-direction:column;height:100vh;max-width:500px;margin:0 auto;width:100%}
.top-bar{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid var(--border)}
.top-bar h1{font-size:16px;font-weight:600}
.btn{padding:6px 12px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text);cursor:pointer;font-size:12px;transition:.2s}
.btn:hover{border-color:#58a6ff}

/* Timer Display */
.timer-display{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative;padding:20px}
.phase-label{font-size:18px;font-weight:700;text-transform:uppercase;letter-spacing:4px;margin-bottom:8px}
.phase-work{color:var(--work)}.phase-rest{color:var(--rest)}.phase-prep{color:var(--prep)}.phase-done{color:var(--done)}
.time-display{font-size:120px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1}
.time-display.work{color:var(--work)}.time-display.rest{color:var(--rest)}.time-display.prep{color:var(--prep)}.time-display.done{color:var(--done)}
.round-info{font-size:14px;color:var(--dim);margin-top:12px}
.progress-ring{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%)}
.progress-ring circle{transition:stroke-dashoffset 0.3s linear}

/* Controls */
.controls{display:flex;justify-content:center;gap:16px;padding:16px}
.ctrl-btn{width:64px;height:64px;border-radius:50%;border:2px solid var(--border);background:var(--surface);color:var(--text);cursor:pointer;font-size:24px;display:flex;align-items:center;justify-content:center;transition:.2s}
.ctrl-btn:hover{border-color:#58a6ff}
.ctrl-btn.primary{background:var(--work);border-color:var(--work);color:#fff;width:72px;height:72px;font-size:28px}
.ctrl-btn.primary:hover{opacity:.85}
.ctrl-btn.primary.running{background:var(--rest);border-color:var(--rest)}

/* Setup Panel */
.setup{padding:16px;border-top:1px solid var(--border);overflow-y:auto;max-height:45vh}
.setup.hidden{display:none}
.preset-row{display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap}
.preset{padding:6px 14px;border-radius:20px;border:1px solid var(--border);background:transparent;color:var(--dim);font-size:12px;cursor:pointer;transition:.2s}
.preset:hover,.preset.active{border-color:var(--work);color:var(--text);background:rgba(239,68,68,.1)}
.setting-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.setting-item{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:12px;text-align:center}
.setting-item label{display:block;font-size:11px;color:var(--dim);margin-bottom:6px}
.setting-item .val{display:flex;align-items:center;justify-content:center;gap:8px}
.setting-item .val button{width:28px;height:28px;border-radius:50%;border:1px solid var(--border);background:var(--bg);color:var(--text);cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center}
.setting-item .val button:hover{border-color:var(--work)}
.setting-item .val span{font-size:20px;font-weight:700;min-width:40px;font-variant-numeric:tabular-nums}
.total-time{text-align:center;padding:12px;font-size:13px;color:var(--dim);border-top:1px solid var(--border);margin-top:12px}

/* Toast */
.toast{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%) scale(.8);background:var(--surface);border:2px solid var(--border);border-radius:16px;padding:24px 40px;font-size:48px;font-weight:800;z-index:20;opacity:0;transition:.3s;pointer-events:none;text-align:center}
.toast.show{opacity:1;transform:translate(-50%,-50%) scale(1)}
.toast .sub{font-size:14px;font-weight:400;color:var(--dim);margin-top:8px}

@media(max-width:400px){.time-display{font-size:80px}}
@media(min-height:800px){.time-display{font-size:140px}}
</style>
</head>
<body>
<div class="app">
  <div class="top-bar">
    <h1>💪 健身间歇计时器</h1>
    <button class="btn" onclick="toggleSetup()">⚙️ 设置</button>
  </div>
  <div class="timer-display" id="timerArea">
    <svg class="progress-ring" width="280" height="280">
      <circle cx="140" cy="140" r="130" fill="none" stroke="#252530" stroke-width="6"/>
      <circle id="progressCircle" cx="140" cy="140" r="130" fill="none" stroke="var(--work)" stroke-width="6" stroke-linecap="round" stroke-dasharray="816.8" stroke-dashoffset="0" transform="rotate(-90 140 140)"/>
    </svg>
    <div class="phase-label phase-prep" id="phaseLabel">准备开始</div>
    <div class="time-display prep" id="timeDisplay">00:00</div>
    <div class="round-info" id="roundInfo">点击开始</div>
  </div>
  <div class="controls">
    <button class="ctrl-btn" onclick="resetTimer()">⏹</button>
    <button class="ctrl-btn primary" id="playBtn" onclick="toggleTimer()">▶</button>
    <button class="ctrl-btn" onclick="skipPhase()">⏭</button>
  </div>
  <div class="setup" id="setupPanel">
    <div class="preset-row">
      <button class="preset active" onclick="loadPreset('tabata')">🔥 Tabata</button>
      <button class="preset" onclick="loadPreset('hiit')">⚡ HIIT</button>
      <button class="preset" onclick="loadPreset('emom')">🕐 EMOM</button>
      <button class="preset" onclick="loadPreset('stretch')">🧘 拉伸</button>
      <button class="preset" onclick="loadPreset('custom')">✏️ 自定义</button>
    </div>
    <div class="setting-grid">
      <div class="setting-item">
        <label>运动时间 (秒)</label>
        <div class="val"><button onclick="adj('work',-5)">−</button><span id="workVal">20</span><button onclick="adj('work',5)">+</button></div>
      </div>
      <div class="setting-item">
        <label>休息时间 (秒)</label>
        <div class="val"><button onclick="adj('rest',-5)">−</button><span id="restVal">10</span><button onclick="adj('rest',5)">+</button></div>
      </div>
      <div class="setting-item">
        <label>组数</label>
        <div class="val"><button onclick="adj('rounds',-1)">−</button><span id="roundsVal">8</span><button onclick="adj('rounds',1)">+</button></div>
      </div>
      <div class="setting-item">
        <label>准备时间 (秒)</label>
        <div class="val"><button onclick="adj('prep',-1)">−</button><span id="prepVal">5</span><button onclick="adj('prep',1)">+</button></div>
      </div>
    </div>
    <div class="total-time" id="totalTime">总时长：4:00</div>
  </div>
</div>
<div class="toast" id="toast"></div>

<script>
let cfg={work:20,rest:10,rounds:8,prep:5};
let state={running:false,phase:'idle',timeLeft:0,round:0,interval:null};
let actx=null;

const PRESETS={
  tabata:{work:20,rest:10,rounds:8,prep:5,label:'Tabata'},
  hiit:{work:40,rest:20,rounds:10,prep:10,label:'HIIT'},
  emom:{work:50,rest:10,rounds:10,prep:5,label:'EMOM'},
  stretch:{work:30,rest:10,rounds:6,prep:5,label:'拉伸'},
  custom:{work:30,rest:15,rounds:5,prep:5,label:'自定义'}
};

function loadPreset(name){
  const p=PRESETS[name];
  cfg={...p};
  document.querySelectorAll('.preset').forEach(b=>b.classList.toggle('active',b.textContent.includes(p.label)));
  updateSettings();
  if(state.running)resetTimer();
}

function adj(key,delta){
  const mins={work:5,rest:0,rounds:1,prep:0};
  const maxs={work:300,rest:300,rounds:99,prep:30};
  cfg[key]=Math.max(mins[key],Math.min(maxs[key],cfg[key]+delta));
  updateSettings();
}

function updateSettings(){
  document.getElementById('workVal').textContent=cfg.work;
  document.getElementById('restVal').textContent=cfg.rest;
  document.getElementById('roundsVal').textContent=cfg.rounds;
  document.getElementById('prepVal').textContent=cfg.prep;
  const total=cfg.prep+(cfg.work+cfg.rest)*cfg.rounds;
  const m=Math.floor(total/60),s=total%60;
  document.getElementById('totalTime').textContent='总时长：'+m+':'+(s<10?'0':'')+s;
}

function toggleSetup(){
  const p=document.getElementById('setupPanel');
  p.classList.toggle('hidden');
}

function beep(freq,dur,vol=0.3){
  if(!actx)actx=new(window.AudioContext||window.webkitAudioContext)();
  if(actx.state==='suspended')actx.resume();
  const o=actx.createOscillator();
  const g=actx.createGain();
  o.frequency.value=freq;o.type='sine';
  g.gain.value=vol;
  o.connect(g);g.connect(actx.destination);
  o.start();
  g.gain.exponentialRampToValueAtTime(0.001,actx.currentTime+dur);
  o.stop(actx.currentTime+dur);
}

function shortBeep(){beep(880,0.15)}
function longBeep(){beep(660,0.4,0.4)}
function doneBeep(){beep(523,0.2);setTimeout(()=>beep(659,0.2),200);setTimeout(()=>beep(784,0.3),400)}

function render(){
  const tl=state.timeLeft;
  const m=Math.floor(tl/60),s=tl%60;
  const display=(m<10?'0':'')+m+':'+(s<10?'0':'')+s;
  const td=document.getElementById('timeDisplay');
  const pl=document.getElementById('phaseLabel');
  const ri=document.getElementById('roundInfo');
  const circle=document.getElementById('progressCircle');
  const playBtn=document.getElementById('playBtn');
  td.textContent=display;
  td.className='time-display '+state.phase;
  
  if(state.phase==='work'){
    pl.textContent='运动';pl.className='phase-label phase-work';
    circle.style.stroke='var(--work)';
    const pct=1-tl/cfg.work;
    circle.style.strokeDashoffset=816.8*(1-pct);
    ri.textContent='第 '+state.round+' / '+cfg.rounds+' 组';
  }else if(state.phase==='rest'){
    pl.textContent='休息';pl.className='phase-label phase-rest';
    circle.style.stroke='var(--rest)';
    const pct=1-tl/cfg.rest;
    circle.style.strokeDashoffset=816.8*(1-pct);
    ri.textContent='第 '+state.round+' / '+cfg.rounds+' 组';
  }else if(state.phase==='prep'){
    pl.textContent='准备';pl.className='phase-label phase-prep';
    circle.style.stroke='var(--prep)';
    const pct=1-tl/cfg.prep;
    circle.style.strokeDashoffset=816.8*(1-pct);
    ri.textContent='即将开始';
  }else if(state.phase==='done'){
    pl.textContent='完成！';pl.className='phase-label phase-done';
    circle.style.stroke='var(--done)';circle.style.strokeDashoffset='0';
    const total=cfg.prep+(cfg.work+cfg.rest)*cfg.rounds;
    const m2=Math.floor(total/60),s2=total%60;
    ri.textContent='总用时 '+m2+':'+(s2<10?'0':'')+s2+' · '+cfg.rounds+' 组';
  }else{
    pl.textContent='准备开始';pl.className='phase-label phase-prep';
    circle.style.stroke='#252530';circle.style.strokeDashoffset='0';
    ri.textContent='点击开始';
  }
  playBtn.classList.toggle('running',state.running);
  playBtn.textContent=state.running?'⏸':'▶';
}

function tick(){
  if(state.timeLeft>0){
    state.timeLeft--;
    if(state.timeLeft<=3&&state.timeLeft>0)shortBeep();
    if(state.timeLeft===0)nextPhase();
  }
  render();
}

function nextPhase(){
  if(state.phase==='prep'){
    state.phase='work';state.round=1;state.timeLeft=cfg.work;
    longBeep();showToast('💪 GO!','第 1 组');
  }else if(state.phase==='work'){
    if(state.round>=cfg.rounds){
      state.phase='done';state.timeLeft=0;state.running=false;
      clearInterval(state.interval);state.interval=null;
      doneBeep();showToast('🎉 完成！',cfg.rounds+' 组全部结束');
    }else{
      state.phase='rest';state.timeLeft=cfg.rest;
      longBeep();
    }
  }else if(state.phase==='rest'){
    state.round++;state.phase='work';state.timeLeft=cfg.work;
    longBeep();showToast('💪','第 '+state.round+' 组');
  }
  render();
}

function toggleTimer(){
  if(state.phase==='done')resetTimer();
  if(!state.running){
    if(state.phase==='idle'){
      state.phase='prep';state.timeLeft=cfg.prep;state.round=0;
      document.getElementById('setupPanel').classList.add('hidden');
    }
    state.running=true;
    state.interval=setInterval(tick,1000);
    shortBeep();
  }else{
    state.running=false;
    clearInterval(state.interval);state.interval=null;
  }
  render();
}

function resetTimer(){
  state.running=false;state.phase='idle';state.timeLeft=0;state.round=0;
  if(state.interval){clearInterval(state.interval);state.interval=null}
  render();
}

function skipPhase(){
  if(!state.running||state.phase==='done')return;
  state.timeLeft=0;nextPhase();
}

function showToast(msg,sub){
  const t=document.getElementById('toast');
  t.innerHTML=msg+(sub?'<div class="sub">'+sub+'</div>':'');
  t.classList.add('show');
  setTimeout(()=>t.classList.remove('show'),1500);
}

updateSettings();render();
</script>
</body>
</html>'''

with open('/root/clawd/builds/workout-timer/index.html','w',encoding='utf-8') as f:
    f.write(html)
print(f"OK {len(html)} bytes")
