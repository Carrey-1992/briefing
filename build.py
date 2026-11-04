#!/usr/bin/env python3
"""成长学习站：读取 data/content.py、data/lectures.py，生成 dist/（index.html、week-01..12.html、assets/）。
与 briefing-site 完全独立；发布时作为 briefing 仓库的 growth/ 子目录。"""
import sys, json, pathlib, shutil, datetime, html
ROOT = pathlib.Path(__file__).resolve().parent; DIST = ROOT / "dist"
sys.path.insert(0, str(ROOT / "data"))
from content import L, PHASES, W
from lectures import LECT
from todos import TODOS
ok = {l.split()[0] for l in (ROOT/"data/linkcheck.txt").read_text().splitlines() if l.endswith(" 200")}
e = lambda s: html.escape(str(s or ""), quote=True)
START = datetime.date(2026, 11, 9)
wstart = lambda n: START + datetime.timedelta(weeks=n-1)
fd = lambda d: f"{d.month}月{d.day}日"
def link(k):
    t, u = L[k]
    return f'<a href="{e(u)}" target="_blank" rel="noopener">{e(t)} ↗</a>' if k in ok else f'{e(t)}（链接未通过检查，暂不放链接）'
def page(title, body, side):
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><link rel="stylesheet" href="assets/style.css">
<style>.lec h3{{margin-top:1.2em}}.lec p,.lec li{{line-height:1.75}}.four{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}}.four .card h4{{margin:0 0 6px}}details.ans{{margin:6px 0 12px}}details.ans summary{{cursor:pointer;opacity:.8}}.todo{{border-left:4px solid #e0a800;padding:8px 12px;margin:12px 0;background:rgba(224,168,0,.08)}}table.t{{border-collapse:collapse;width:100%}}table.t td,table.t th{{border:1px solid rgba(128,128,128,.3);padding:6px 8px;text-align:left;vertical-align:top}}</style>
<script>document.documentElement.dataset.theme=localStorage.getItem('bf_theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light')</script></head>
<body data-root=""><header><div class="bar"><a class="logo" href="index.html">🌱 成长学习站</a>
<div class="search"><input id="q" placeholder="搜索 12 周讲义（标题/主题）…"></div><button class="btn" id="menu">☰ 目录</button><button class="btn" id="theme" title="切换主题">🌓</button></div></header>
<div class="wrap"><aside id="side">{side}</aside><main id="main">{body}</main></div><script src="assets/search-index.js"></script><script src="assets/app.js"></script>
<!-- built {datetime.datetime.now():%Y-%m-%d %H:%M} 北京时间 --></body></html>"""
def directory(cur=None):
    h = '<a class="iss" href="todo.html">☑ 练习待办</a><a class="iss fav-link" href="index.html#fav">★ 我的收藏 <small><span id="favcnt">0</span> 条</small></a><a class="iss" href="index.html#done">✓ 已完成</a>'
    for name, rng, ws, *_ in PHASES:
        op = " open" if (cur in ws or (cur is None)) else ""
        h += f'<details class="drw"{op}><summary class="sidesec">{name}<small>{rng}</small></summary><div class="drwlist">'
        for n in ws:
            w = W[n-1]; on = " on" if cur == n else ""
            h += f'<a class="iss{on}" href="week-{n:02d}.html">第{n}周 · {e(w[1])} <small>{fd(wstart(n))}</small></a>'
        h += '</div></details>'
    return h
def card(n, cid, title, body, url=None):
    pg = f"week-{n:02d}.html#{cid}"; u = url or pg
    return f'<div class="card" id="{cid}" data-id="growth|{cid}" data-title="第{n}周 · {e(title)}" data-url="{e(u)}" data-page="{pg}" data-date="{wstart(n)}" data-kind="week"><h4>{e(title)}</h4>{body}<div class="foot"><span class="acts"><button class="rd" title="标记完成">✓</button><button class="fv" title="收藏">☆</button></span></div></div>'
idx = []
def week(n):
    _, topic, days, lab, out, mats, (os_keys, os_what), qa_outline = W[n-1]
    s = wstart(n); lec = LECT.get(n)
    ph = next(p for p in PHASES if n in p[2])
    b = f'<div class="crumb"><a href="index.html">← 首页</a><span class="tag">{ph[0]}</span></div><h1>第{n}周 · {e(topic)}</h1>'
    b += f'<div class="meta">{fd(s)}（周一）– {fd(s+datetime.timedelta(days=6))}（周日）· 北京时间 · 已完成 <span id="readcnt">0</span> 项</div>'
    if not lec: b += '<div class="todo">📝 本周目前是骨架：讲义将在该周开始前一周补写。</div>'
    b += f'<h3 class="sec">本周目标</h3><p>{e(lec["goal"]) if lec else "完成下列 5 天学习、周末实验和产出「"+e(out)+"」，能不看资料讲清本周主题。"}</p>'
    b += '<div class="secblk" data-sec="主题"><h3 class="sec">本周主题（工作日每天 30–60 分钟）</h3><div class="grid">'
    for i, d in enumerate(days): b += card(n, f"d{i+1}", f"周{'一二三四五'[i]}：{d}", "")
    b += '</div></div>'
    if lec:
        b += '<h3 class="sec">讲义 · 四栏卡片</h3><div class="four lec">' + "".join(f'<div class="card"><h4>{e(h)}</h4>{x}</div>' for h, x in lec["four"]) + '</div>'
    b += '<div class="secblk" data-sec="材料"><h3 class="sec">阅读材料</h3><div class="grid">'
    for k in mats: b += card(n, f"m-{k}", L[k][0], f"<p>{link(k)}</p>", L[k][1] if k in ok else None)
    b += '</div></div>'
    b += f'<h3 class="sec">周末动手实验（半天）</h3><div class="lec">{lec["lab"] if lec else "<p>"+e(lab)+"</p><p class=todo>详细步骤将在该周开始前一周补写。</p>"}</div>'
    b += '<div class="grid">' + card(n, "lab", "周末实验完成", f"<p>产出：{e(out)}</p>") + '</div>'
    b += '<h3 class="sec">回忆题</h3>'
    if lec:
        b += '<ol class="lec">' + "".join(f'<li>{e(q)}<details class="ans"><summary>参考答案</summary><p>{e(a)}</p></details></li>' for q, a in lec["qa"]) + '</ol>'
    else:
        b += '<p>大纲（参考答案随讲义补写）：</p><ol class="lec">' + "".join(f"<li>{e(q)}</li>" for q in qa_outline) + '</ol>'
    r = lambda k: fd(s + datetime.timedelta(days=k))
    b += f'<h3 class="sec">复习安排</h3><table class="t"><tr><th>节点</th><th>日期（北京时间）</th><th>做法</th></tr><tr><td>第 3 天</td><td>{r(2)}</td><td>3 道回忆题，不看资料作答，再对照卡片</td></tr><tr><td>第 1 周</td><td>{r(7)}</td><td>5 道混合题，含一道“这个方案什么时候会出问题”</td></tr><tr><td>第 1 个月</td><td>{r(30)}</td><td>1 道综合题：结合两个主题做方案对比并说取舍</td></tr><tr><td>本周五</td><td>{r(4)}</td><td>本周 5 道回忆题，薄弱点进入下轮复习</td></tr></table>'
    b += '<div class="secblk" data-sec="开源"><h3 class="sec">每周 30 分钟开源讨论</h3><p>看什么：' + e(os_what) + '。做法：挑一个问题先写自己的答案，再对照维护者回复，把差异记进本周卡片。</p><div class="grid">'
    for k in os_keys: b += card(n, f"os-{k}", L[k][0], f"<p>{link(k)}</p>", L[k][1] if k in ok else None)
    b += '</div></div>'
    pv = f'<a class="pv" href="week-{n-1:02d}.html"><small>← 上一周</small>第{n-1}周 · {e(W[n-2][1])}</a>' if n > 1 else '<span class="pv"><small>← 上一周</small>没有了</span>'
    nx = f'<a class="nx" href="week-{n+1:02d}.html"><small>下一周 →</small>第{n+1}周 · {e(W[n][1])}</a>' if n < 12 else '<span class="nx"><small>下一周 →</small>没有了</span>'
    b += f'<div class="pn">{pv}{nx}</div>'
    idx.append({"k": "week", "d": str(s), "t": f"第{n}周 · {topic}", "s": "；".join(days), "p": f"week-{n:02d}.html"})
    return page(f"第{n}周 · {topic} · 成长学习站", b, directory(n))
def home():
    b = '<h1>成长学习站 · 12 周架构师成长计划（第一轮）</h1><div class="meta">AI 研发效能 → 分布式原理 → 存储与高并发 · 每周 6–9 小时 · 第 1 周从 2026 年 11 月 9 日（周一，北京时间）开始</div>'
    b += '<div class="note">ℹ️ 这是第一轮，目标是打通主干不是学完。可观测性和架构方法（DDD、ADR）只在第 11–12 周轻量入门，第二轮再深入。</div>'
    for name, rng, ws, test, outp in PHASES:
        b += f'<h3 class="sec">{name} <span>{rng}</span></h3><div class="grid">'
        for n in ws:
            w = W[n-1]; st = "讲义已写" if n in LECT else "骨架 · 讲义待补"
            b += f'<a class="card icard" href="week-{n:02d}.html"><div class="k">第{n}周 · {fd(wstart(n))} 起 · {st}</div><h4>{e(w[1])}</h4><ul>' + "".join(f"<li>{e(x)}</li>" for x in w[2][:3]) + '</ul></a>'
        b += f'</div><p><b>自测标准：</b>{e(test)}　<b>输出：</b>{e(outp)}</p>'
    b += '''<h3 class="sec">学习方法</h3><div class="four"><div class="card"><h4>四栏卡片</h4><p>每个主题写一张：<b>是什么 / 为什么这样设计 / 什么时候会出问题 / 怎么验证过</b>。最后一栏只在动手做完后填写。</p></div>
<div class="card"><h4>间隔复习</h4><p>第 3 天 3 道回忆题；第 1 周 5 道混合题；第 1 个月 1 道综合对比题；每周五 5 道本周回忆题。先答再对照，薄弱点进下轮。</p></div>
<div class="card"><h4>每周节奏</h4><p>工作日每天 30–60 分钟读资料+回忆题；周末半天动手实验并写卡片；每周另留 30 分钟看开源讨论。AI 当私教：讲原理、出题、评审实现；读、写、做由你完成。</p></div>
<div class="card"><h4>学会的标准</h4><p>三条都过才算：能不看资料讲清楚；能自己实现最小版本；能对比方案并说出取舍。</p></div></div>'''
    b += '<p><a class="card icard" href="todo.html"><b>☑ 练习待办</b> · 回家要动手的练习清单</a></p><h3 class="sec" id="fav">★ 我的收藏</h3><div id="favs"></div><h3 class="sec" id="done">✓ 已完成</h3><div id="dones"></div>'
    b += '<p class="meta">收藏和完成记录保存在本浏览器（localStorage），与新闻简报站互不影响。</p>'
    return page("成长学习站", b, directory())
def todo_page():
    b = '<div class="crumb"><a href="index.html">← 首页</a></div><h1>☑ 练习待办</h1><div class="note">勾选只保存在当前浏览器，不同设备不同步。</div>'
    for t in TODOS:
        b += f'<h3 class="sec">{e(t["title"])}</h3><p><b>目标：</b>{e(t["goal"])}</p>'
        if t.get("week"): b += f'<p>对应：<a href="week-{t["week"]:02d}.html">第{t["week"]}周 · {e(W[t["week"]-1][1])}</a></p>'
        for sid, st, sb in t["steps"]:
            k = f'{t["id"]}|{sid}'
            b += f'<label class="card tdi"><input type="checkbox" data-k="{e(k)}"><div><h4>{e(st)}</h4>{sb}</div></label>'
        if t.get("compose"): b += f'<h4>docker-compose 片段（未在本机运行验证）</h4><pre class="cmp">{e(t["compose"])}</pre>'
        if t.get("refs"): b += '<h4>官方资料</h4><ul>' + "".join(f'<li><a href="{e(u)}" target="_blank" rel="noopener">{e(n)} ↗</a></li>' for n, u in t["refs"]) + '</ul>'
    b += """<style>.tdi{display:flex;gap:12px;align-items:flex-start;margin:10px 0;cursor:pointer}.tdi input{width:24px;height:24px;flex:none;margin-top:2px}.tdi.ck h4{text-decoration:line-through;opacity:.6}.uv{color:#b07d00;font-size:.92em}pre.cmp{overflow-x:auto;padding:12px;font-size:13px;background:rgba(128,128,128,.1);border-radius:8px}code{word-break:break-all}</style>
<script>(function(){var K='gs_todo',s=JSON.parse(localStorage.getItem(K)||'{}');document.querySelectorAll('.tdi input').forEach(function(c){var k=c.dataset.k;c.checked=!!s[k];c.closest('.tdi').classList.toggle('ck',c.checked);c.addEventListener('change',function(){if(c.checked)s[k]=1;else delete s[k];localStorage.setItem(K,JSON.stringify(s));c.closest('.tdi').classList.toggle('ck',c.checked)})})})()</script>"""
    return page("练习待办 · 成长学习站", b, directory())
if DIST.exists(): shutil.rmtree(DIST)
(DIST / "assets").mkdir(parents=True)
for f in ("style.css", "app.js"): shutil.copy(ROOT / "assets_src" / f, DIST / "assets" / f)
for n in range(1, 13): (DIST / f"week-{n:02d}.html").write_text(week(n), "utf-8")
(DIST / "assets" / "search-index.js").write_text("window.SEARCH=" + json.dumps(idx, ensure_ascii=False).replace("</", "<\\/") + ";", "utf-8")
(DIST / "index.html").write_text(home(), "utf-8")
(DIST / "todo.html").write_text(todo_page(), "utf-8")
print("生成", DIST, "12 周 +首页；链接可用", len(ok), "/", len(L))
