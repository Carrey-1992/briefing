// 共享脚本：主题、已读/收藏(localStorage)、标签筛选、首页搜索与收藏
const LS=k=>JSON.parse(localStorage.getItem(k)||'{}'),SV=(k,v)=>localStorage.setItem(k,JSON.stringify(v));
let read=LS('gs_read'),fav=LS('gs_fav');
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const setT=t=>{document.documentElement.dataset.theme=t;localStorage.setItem('bf_theme',t)};
setT(localStorage.getItem('bf_theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'));
$('#theme').onclick=()=>setT(document.documentElement.dataset.theme==='dark'?'light':'dark');
if($('#menu'))$('#menu').onclick=()=>$('#side').classList.toggle('open');
const ROOT=document.body.dataset.root||'';
function paint(){
 $$('.card[data-id]').forEach(c=>{const id=c.dataset.id;c.classList.toggle('read',!!read[id]);
  const r=c.querySelector('.rd'),f=c.querySelector('.fv');r.classList.toggle('on',!!read[id]);f.classList.toggle('on',!!fav[id]);f.textContent=fav[id]?'★':'☆'});
 const m=$('#readcnt');if(m){const ids=$$('.card[data-id]').map(c=>c.dataset.id);m.textContent=ids.filter(i=>read[i]).length}
 $$('[data-cnt]').forEach(e=>{const ids=e.dataset.cnt.split(' ');/* not used */});
 const fc=$('#favcnt');if(fc)fc.textContent=Object.keys(fav).length}
document.body.addEventListener('click',e=>{
 const c=e.target.closest('.chip');if(c){const t=c.dataset.t;$$('.chip').forEach(x=>x.classList.toggle('on',x===c));
  $$('.secblk').forEach(b=>{let n=0;b.querySelectorAll('.card').forEach(cd=>{const ok=!t||(t[0]==='s'?b.dataset.sec===t.slice(2):(cd.dataset.tags||'').split('|').includes(t.slice(2)));cd.style.display=ok?'':'none';n+=ok});b.style.display=n?'':'none'});return}
 const b=e.target.closest('.rd,.fv');if(!b)return;const cd=b.closest('.card'),id=cd.dataset.id;
 if(b.classList.contains('rd')){read[id]?delete read[id]:read[id]={t:cd.dataset.title,u:cd.dataset.url,p:cd.dataset.page,d:cd.dataset.date,k:cd.dataset.kind};SV('gs_read',read)}
 else{if(fav[id])delete fav[id];else fav[id]={t:cd.dataset.title,u:cd.dataset.url,p:cd.dataset.page,d:cd.dataset.date,k:cd.dataset.kind};SV('gs_fav',fav)}
 paint();if(window.renderFav)renderFav()});
paint();
// 首页：搜索 + 收藏
if(window.SEARCH){const M=$('#main'),home=M.innerHTML;
 const lab=k=>({news:'新闻','java-ai':'工具',hardware:'硬件','mac-ios':'软件',github:'GitHub',discover:'发现',week:'周讲义'})[k]||k;
 const row=x=>`<div class="card"><h4><a href="${x.u?esc(x.u):ROOT+x.p}"${x.u?' target="_blank" rel="noopener"':''}>${esc(x.t)}</a></h4><div class="from"><a href="${ROOT}${x.p}">${lab(x.k)} · ${x.d}${x.s?' · '+esc(x.s):''} →</a></div>${x.g?`<div class="foot">${x.g.split('|').map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div>`:''}</div>`;
 $('#q').oninput=e=>{const q=e.target.value.trim().toLowerCase();if(!q){M.innerHTML=home;window.renderFav();window.renderDone();paint();return}
  const r=SEARCH.filter(x=>(x.t+' '+(x.g||'')+' '+(x.s||'')).toLowerCase().includes(q));
  M.innerHTML=`<h1>搜索「${esc(q)}」</h1><div class="meta">在全部历史中找到 ${r.length} 条（匹配标题/标签/栏目）</div><div class="grid">${r.map(row).join('')}</div>`};
 window.renderFav=()=>{const el=$('#favs');if(!el)return;const l=Object.values(fav).filter(v=>typeof v==='object').sort((a,b)=>b.d.localeCompare(a.d));
  el.innerHTML=l.length?`<div class="grid">${l.map(x=>row({...x,g:''})).join('')}</div>`:'<div class="empty">在期页面点卡片右下角 ☆ 收藏，会出现在这里</div>'};
 window.renderDone=()=>{const el=$('#dones');if(!el)return;const l=Object.values(read).filter(v=>typeof v==='object').sort((a,b)=>a.d.localeCompare(b.d));el.innerHTML=l.length?`<div class="grid">${l.map(x=>row({...x,g:''})).join('')}</div>`:'<div class="empty">在周页面点卡片右下角 ✓ 标记完成，会出现在这里</div>'};
 renderFav();renderDone()}
// 导航 v2：本周、角标、已完成周
(function(){if(!window.NAV)return;const N=window.NAV;
 const d0=new Date(N.start+'T00:00:00+08:00'),now=new Date();
 let cw=Math.floor((now-d0)/(7*864e5))+1;cw=Math.max(1,Math.min(12,cw));
 const t=N.weeks[cw-1][1],href=`week-${String(cw).padStart(2,'0')}.html`;
 const nc=$('#nav-cur');if(nc){nc.href=href;$('#nav-curt').textContent=`第${cw}周`;const m=location.pathname.match(/week-(\d+)/);if(m&&+m[1]===cw)nc.classList.add('on')}
 $$('.wk').forEach(a=>{const n=a.dataset.wk,ids=N.wids[n]||[];a.classList.toggle('now',+n===cw);a.classList.toggle('dn',ids.length>0&&ids.every(i=>read[i]))});
 if($('#cc-t')){$('#cc-k').textContent=now<d0?`本周 · 第1周 ${+N.start.slice(5,7)}月${+N.start.slice(8)}日开始`:`本周 · 第${cw}周`;$('#cc-t').textContent=`第${cw}周 · ${t}`;$('#cc-go').href=href}
 const td=JSON.parse(localStorage.getItem('gs_todo')||'{}'),left=N.todo.filter(k=>!td[k]).length;
 const set=(id,v)=>{const e=document.getElementById(id);if(e){e.textContent=v;e.classList.toggle('hot',id==='bdg-todo'&&v>0)}};
 const upd=()=>{const t2=JSON.parse(localStorage.getItem('gs_todo')||'{}');const l=N.todo.filter(k=>!t2[k]).length;set('bdg-todo',l);set('cc-todo',l);set('bdg-fav',Object.keys(fav).length);set('bdg-done',Object.keys(read).length);
  $$('.wk').forEach(a=>{const ids=N.wids[a.dataset.wk]||[];a.classList.toggle('dn',ids.length>0&&ids.every(i=>read[i]))})};
 upd();document.body.addEventListener('click',()=>setTimeout(upd,0));document.body.addEventListener('change',()=>setTimeout(upd,0));
 const hs=()=>{if(location.pathname.endsWith('/')||location.pathname.endsWith('index.html')){$$('.nbtn[data-nav]').forEach(a=>a.classList.toggle('on',a.dataset.nav===({'#fav':'fav','#done':'done'}[location.hash]||'home')))}};hs();addEventListener('hashchange',hs);
 $$('#side a').forEach(a=>a.addEventListener('click',()=>$('#side').classList.remove('open')));
})();
