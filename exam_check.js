
const TOPIC_ID='{{ topic.id }}';
const TOPIC_NAME='{{ topic.name }}';
const EXAM_IDX={{ exam_idx }};
const EXAM_NAME='{{ exam.name }}';
const UNAME=new URLSearchParams(location.search).get('name')||'anonymous';
const BLOCKS={{ exam.questions|tojson }};
const STORAGE_KEY=`n1_ans_${UNAME}_${TOPIC_ID}_${EXAM_IDX}`;
const TIME_KEY=`n1_time_${UNAME}_${TOPIC_ID}_${EXAM_IDX}`;

// flatten blocks -> items (display cau hoi)
let ITEMS=[];
BLOCKS.forEach((blk,bi)=>{
  if(blk.type==='reading'||blk.type==='listening'){
    blk.questions.forEach((q,qi)=>{
      ITEMS.push({blk,bi,qi,q,firstInBlock:qi===0,multi:q.multi||false,passage:blk.passage,audio:blk.audio,script:blk.script,title:blk.title});
    });
  } else {
    ITEMS.push({blk,bi,qi:0,q:blk,firstInBlock:true,multi:blk.multi||false});
  }
});
const TOTAL=ITEMS.length;
const TIME_LIMIT=TOTAL*30;
let state={answers:{},flagged:{},current:0,timeLeft:TIME_LIMIT,finished:false};

function saveAns(){try{localStorage.setItem(STORAGE_KEY,JSON.stringify({answers:state.answers,flagged:state.flagged,current:state.current}));}catch(e){}}
function loadAns(){try{const s=JSON.parse(localStorage.getItem(STORAGE_KEY));if(s){state.answers=s.answers||{};state.flagged=s.flagged||{};state.current=0;const hasMulti=BLOCKS.some(b=>(b.type?b.questions.some(q=>q.multi):b.multi));if(!hasMulti){for(const k in state.answers){if(Array.isArray(state.answers[k]))delete state.answers[k];}}}catch(e){}}
function saveTime(){try{localStorage.setItem(TIME_KEY,String(state.timeLeft));}catch(e){}}
function loadTime(){try{const t=localStorage.getItem(TIME_KEY);if(t!==null)state.timeLeft=parseInt(t);}catch(e){}}

const $=s=>document.querySelector(s);
const app=$('#app');
const letter=i=>String.fromCharCode(65+i);
function isAns(i){const a=state.answers[i];const it=ITEMS[i];if(it.multi)return Array.isArray(a)&&a.length>0;return a!==undefined&&a>=0;}
function answeredCount(){return ITEMS.filter((_,i)=>isAns(i)).length;}

function renderQuiz(){
  const it=ITEMS[state.current];
  const pct=Math.round(answeredCount()/TOTAL*100);
  const flagged=!!state.flagged[state.current];
  let blockHtml='';
  if(it.firstInBlock && it.passage){
    blockHtml=`<div class="mb-5 p-4 rounded-xl bg-slate-900/50 border border-slate-700 text-sm leading-relaxed text-slate-300 whitespace-pre-line">${it.passage}</div>`;
  }
  if(it.firstInBlock && it.audio){
    blockHtml=`<div class="mb-5 p-4 rounded-xl bg-slate-900/50 border border-slate-700">
      <p class="text-xs text-amber-400 mb-2 flex items-center gap-1.5"><i data-lucide="headphones" class="w-4 h-4"></i> Nghe hiểu: ${it.title}</p>
      <audio controls src="${it.audio}" class="w-full"></audio>
      <details class="mt-2 text-xs text-slate-400"><summary class="cursor-pointer">Xem script</summary><p class="mt-1 whitespace-pre-line">${it.script}</p></details>
    </div>`;
  }
  const cur=it.q;
  app.innerHTML=`
  <header class="grad-header sticky top-0 z-30 border-b border-slate-800 px-4 sm:px-6 py-3">
    <div class="max-w-5xl mx-auto flex items-center justify-between gap-4">
      <div class="min-w-0"><h1 class="font-extrabold text-sm sm:text-base truncate">${TOPIC_NAME} · ${EXAM_NAME}</h1>
      <p class="text-[11px] text-slate-400">Câu ${state.current+1} / ${TOTAL}</p></div>
      <div class="flex items-center gap-3 sm:gap-5">
        <div class="text-right hidden sm:block"><p class="text-[10px] text-slate-400 uppercase tracking-wider">Tiến độ</p><p class="font-bold text-emerald-400">${pct}%</p></div>
        <div class="w-24 sm:w-32 h-1.5 rounded-full bg-slate-700 overflow-hidden"><div class="h-full bg-emerald-400 transition-all duration-500" style="width:${pct}%"></div></div>
        <div id="timerBox" class="flex items-center gap-1.5 font-mono font-bold text-lg"><i data-lucide="timer" class="w-5 h-5"></i><span id="timerText">${fmtTime(state.timeLeft)}</span></div>
      </div>
    </div>
  </header>
  <main class="max-w-5xl mx-auto px-4 sm:px-6 py-6">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
      <section class="lg:col-span-2 space-y-5">
        <div class="rounded-2xl bg-slate-800/50 border border-slate-700 p-6 shadow-sm">
          <div class="flex items-start justify-between gap-3 mb-5">
            <h2 class="text-lg sm:text-xl font-bold leading-snug">${state.current+1}. ${cur.q}${cur.multi?'<span class="ml-2 text-[10px] font-bold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 align-middle">★ Nhiều đáp án</span>':''}</h2>
            <button onclick="toggleFlag()" class="shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold border transition-all duration-300 ${flagged?'bg-amber-400/20 border-amber-400 text-amber-300':'bg-slate-700/50 border-slate-600 text-slate-300 hover:border-amber-400'}"><i data-lucide="flag" class="w-4 h-4"></i> ${flagged?'Đã gắn cờ':'Gắn cờ'}</button>
          </div>
          ${blockHtml}
          <div class="space-y-3" id="optionsBox">
            ${cur.options.map((opt,i)=>{
              const sel=cur.multi?(Array.isArray(state.answers[state.current])&&state.answers[state.current].includes(i)):state.answers[state.current]===i;
              const inpType=cur.multi?'checkbox':'radio';
              return `<label class="opt-card ${sel?'sel':''} flex items-center gap-3 p-4 rounded-xl bg-slate-900/40 border border-slate-700 cursor-pointer" onclick="handleSelect(${i})">
                <input type="${inpType}" ${sel?'checked':''} class="peer" readonly>
                <span class="w-8 h-8 shrink-0 rounded-lg ${sel?'bg-amber-400 text-slate-900':'bg-slate-700 text-slate-300'} flex items-center justify-center font-bold text-sm transition-all duration-300">${letter(i)}</span>
                <span class="text-slate-100 text-sm sm:text-base">${opt}</span>
              </label>`;
            }).join('')}
          </div>
        </div>
        <div class="flex items-center gap-3">
          <button onclick="prev()" class="flex-1 py-3 rounded-xl bg-slate-700/60 hover:bg-slate-700 font-semibold text-sm flex items-center justify-center gap-2 transition-all duration-300 ${state.current===0?'opacity-40 cursor-not-allowed':''}" ${state.current===0?'disabled':''}><i data-lucide="chevron-left" class="w-4 h-4"></i> Câu trước</button>
          ${state.current===TOTAL-1?'<button onclick="requestSubmit()" class="flex-1 py-3 rounded-xl bg-amber-400 hover:bg-amber-300 text-slate-900 font-bold flex items-center justify-center gap-2 transition-all duration-300"><i data-lucide="send" class="w-4 h-4"></i> Nộp bài</button>':'<button onclick="next()" class="flex-1 py-3 rounded-xl bg-slate-700/60 hover:bg-slate-700 font-semibold text-sm flex items-center justify-center gap-2 transition-all duration-300">Câu tiếp theo <i data-lucide="chevron-right" class="w-4 h-4"></i></button>'}
        </div>
      </section>
      <aside class="lg:sticky lg:top-24">
        <div class="rounded-2xl bg-slate-800/50 border border-slate-700 p-5 shadow-sm">
          <h3 class="font-bold text-sm mb-1 flex items-center gap-2"><i data-lucide="layout-grid" class="w-4 h-4 text-amber-400"></i> Ma trận câu hỏi</h3>
          <p class="text-[11px] text-slate-400 mb-4">${answeredCount()}/${TOTAL} đã làm</p>
          <div id="gridBox" class="grid grid-cols-5 gap-2"></div>
          <div class="mt-5 space-y-2 text-[11px] text-slate-400">
            <div class="flex items-center gap-2"><span class="w-4 h-4 rounded bg-slate-600"></span> Chưa làm</div>
            <div class="flex items-center gap-2"><span class="w-4 h-4 rounded bg-sky-500"></span> Đã chọn</div>
            <div class="flex items-center gap-2"><span class="w-4 h-4 rounded bg-amber-400"></span> Đã gắn cờ</div>
          </div>
        </div>
      </aside>
    </div>
  </main>`;
  updateGrid(); lucide.createIcons();
}

function updateGrid(){
  const box=$('#gridBox'); if(!box) return;
  box.innerHTML=ITEMS.map((_,i)=>{
    const ans=isAns(i); const flg=!!state.flagged[i]; const cur=i===state.current;
    let cls='bg-slate-600 text-white';
    if(flg) cls='bg-amber-400 text-slate-900'; else if(ans) cls='bg-sky-500 text-white';
    const ring=cur?'ring-2 ring-amber-400 ring-offset-2 ring-offset-slate-800':'';
    return `<button onclick="goTo(${i})" class="aspect-square rounded-lg font-bold text-sm flex items-center justify-center transition-all duration-300 hover:scale-105 ${cls} ${ring}">${i+1}</button>`;
  }).join('');
}

function handleSelect(idx){
  const it=ITEMS[state.current]; const cur=it.q;
  if(cur.multi){ let arr=state.answers[state.current]||[]; if(arr.includes(idx))arr=arr.filter(x=>x!==idx); else arr.push(idx); state.answers[state.current]=arr; }
  else { state.answers[state.current]=idx; }
  saveAns();
  document.querySelectorAll('#optionsBox .opt-card').forEach((el,i)=>{
    const q=ITEMS[state.current].q; const sel=q.multi?(Array.isArray(state.answers[state.current])&&state.answers[state.current].includes(i)):state.answers[state.current]===i;
    el.classList.toggle('sel',sel);
  });
  updateGrid();
}
function toggleFlag(){ state.flagged[state.current]=!state.flagged[state.current]; saveAns(); renderQuiz(); }
function goTo(i){ state.current=i; saveAns(); renderQuiz(); window.scrollTo({top:0,behavior:'smooth'}); }
function next(){ if(state.current<TOTAL-1){state.current++;saveAns();renderQuiz();window.scrollTo({top:0,behavior:'smooth'});} }
function prev(){ if(state.current>0){state.current--;saveAns();renderQuiz();window.scrollTo({top:0,behavior:'smooth'});} }

let timerInt=null;
function fmtTime(s){const m=String(Math.floor(s/60)).padStart(2,'0');const x=String(s%60).padStart(2,'0');return `${m}:${x}`;}
function startTimer(){
  clearInterval(timerInt);
  timerInt=setInterval(()=>{
    if(state.finished)return clearInterval(timerInt);
    state.timeLeft--;
    const txt=$('#timerText'); const box=$('#timerBox');
    if(txt)txt.textContent=fmtTime(state.timeLeft);
    if(box&&state.timeLeft<=60)box.classList.add('timer-danger');
    if(state.timeLeft%5===0)saveTime();
    if(state.timeLeft<=0){clearInterval(timerInt);requestSubmit(true);}
  },1000);
}

function requestSubmit(auto=false){
  const un=TOTAL-answeredCount();
  $('#confirmText').innerHTML=un>0?`Bạn còn <b class="text-amber-400">${un}</b> câu chưa làm. Xác nhận nộp bài?`:`Bạn đã làm tất cả ${TOTAL} câu. Xác nhận nộp bài?`;
  if(auto)$('#confirmText').innerHTML+='<br><span class="text-rose-400 text-xs">(Tự động nộp do hết giờ)</span>';
  const m=$('#confirmModal'); m.classList.remove('hidden'); m.classList.add('flex');
}
function closeConfirm(){const m=$('#confirmModal');m.classList.add('hidden');m.classList.remove('flex');}
function confirmSubmit(){
  closeConfirm(); clearInterval(timerInt); state.finished=true; localStorage.removeItem(TIME_KEY);
  const ans={}; ITEMS.forEach((_,i)=>{const a=state.answers[i]; const it=ITEMS[i]; ans[i]=it.multi?(Array.isArray(a)?a:[]):(a!==undefined?a:-1);});
  fetch('/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({topic_id:TOPIC_ID,exam_idx:EXAM_IDX,user_name:UNAME,answers:ans})})
  .then(r=>r.json()).then(d=>{window.location=`/result/${TOPIC_ID}/${EXAM_IDX}?name=${encodeURIComponent(UNAME)}`;});
}

loadAns(); loadTime(); startTimer(); renderQuiz();
// Fix mobile: khi quay lai tu bfcache (back/forward tren DT), reload sach de tranh DOM cu
window.addEventListener('pageshow', function(e){ if(e.persisted) location.reload(); });
