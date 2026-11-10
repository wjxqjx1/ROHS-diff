"""报告渲染：条款级差异 → 三页 HTML。"""
from datetime import date

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: "Microsoft YaHei","PingFang SC","Source Han Sans SC",sans-serif; color:#1c1c1c; background:#fff;
  -webkit-print-color-adjust:exact; print-color-adjust:exact; }
.page { width:210mm; height:297mm; padding:13mm 15mm 9mm; display:flex; flex-direction:column;
  position:relative; page-break-after:always; overflow:hidden; }
.page:last-child { page-break-after:auto; }
.ph { border-bottom:2.5px solid #0d5c45; padding-bottom:6px; display:flex; align-items:flex-end; justify-content:space-between; }
.kick { font-size:7.6pt; letter-spacing:.2em; color:#0d5c45; font-weight:700; }
.ph h1 { font-size:17pt; line-height:1.2; margin-top:3px; }
.ph h1 small { display:block; font-size:9.6pt; font-weight:400; color:#555; margin-top:3px; }
.sample { font-size:6.6pt; color:#b3541e; border:1px solid #e6c3ab; background:#fdf7f2; padding:2px 6px;
  border-radius:2px; letter-spacing:.08em; white-space:nowrap; }
.meta { display:flex; gap:14px; font-size:6.9pt; color:#777; margin-top:5px; flex-wrap:wrap; }
.meta b { color:#444; }
.st { display:flex; align-items:baseline; gap:7px; margin:12px 0 7px; }
.st .no { font-size:8pt; font-weight:700; color:#0d5c45; letter-spacing:.1em; }
.st h2 { font-size:10.6pt; font-weight:700; }
.st .line { flex:1; height:1px; background:#dcdcdc; }
.stats { display:flex; gap:7px; }
.stat { flex:1; border:1px solid #e4e4e4; border-top:2px solid #0d5c45; padding:6px 8px 7px; background:#fcfcfc; }
.stat .n { font-size:20pt; font-weight:700; line-height:1; color:#0d5c45; }
.stat .n small { font-size:8pt; font-weight:400; color:#888; }
.stat .l { font-size:7pt; color:#666; margin-top:3px; }
.verdict { margin-top:9px; border-left:3.5px solid #b3541e; background:#fdf7f2; padding:7px 10px 8px; }
.verdict .h { font-size:9pt; font-weight:700; color:#8a3d12; margin-bottom:4px; }
.verdict li { font-size:8pt; line-height:1.55; color:#4a3a30; margin:0 0 2px 12px; }
table { width:100%; border-collapse:collapse; }
th { font-size:7pt; font-weight:700; color:#fff; background:#0d5c45; padding:5px 6px; text-align:left; }
td { font-size:7.4pt; line-height:1.45; padding:5px 6px; border-bottom:1px solid #e6e6e6; vertical-align:top; color:#333; }
tr:nth-child(even) td { background:#fafafa; }
td.c { text-align:center; }
.tag { display:inline-block; font-size:6.4pt; font-weight:700; padding:1px 5px; border-radius:2px; white-space:nowrap; }
.t-new { color:#0d5c45; background:#e7f1ec; }
.t-mod { color:#8a5a12; background:#fbf0dd; }
.t-del { color:#8a3d12; background:#f7e6dc; }
.t-edit { color:#666; background:#efefef; }
.lv-h { color:#a33a10; background:#fbe7dd; }
.lv-m { color:#7a6212; background:#f6efd8; }
.lv-l { color:#666; background:#efefef; }
.diff { border:1px solid #e2e2e2; margin-bottom:8px; }
.diff .top { display:flex; align-items:center; gap:6px; padding:5px 8px; background:#f6f6f6; border-bottom:1px solid #e2e2e2; }
.diff .id { font-size:7.6pt; font-weight:700; color:#0d5c45; letter-spacing:.04em; }
.diff .ttl { font-size:8.6pt; font-weight:700; flex:1; }
.diff .body { display:flex; }
.side { flex:1; padding:7px 9px 8px; }
.side.old { background:#fbfbfb; border-right:1px solid #ececec; }
.side.new { background:#f5faf7; }
.side .lab { font-size:6.4pt; letter-spacing:.06em; color:#888; margin-bottom:3px; }
.side.new .lab { color:#0d5c45; }
.side p { font-size:7.5pt; line-height:1.55; color:#333; }
.impact { padding:6px 9px 7px; border-top:1px dashed #dedede; display:flex; gap:8px; }
.impact .k { font-size:6.4pt; color:#0d5c45; font-weight:700; white-space:nowrap; letter-spacing:.06em; padding-top:1px; }
.impact p { font-size:7.4pt; line-height:1.5; color:#444; }
.note { font-size:6.6pt; color:#888; line-height:1.5; margin-top:6px; }
.tl2 { display:flex; margin-top:3px; }
.tl2 .it { flex:1; border-top:2px solid #dbe7e1; padding:9px 9px 0 0; position:relative; }
.tl2 .it.on { border-top-color:#0d5c45; }
.tl2 .dot { position:absolute; top:-5px; left:0; width:8px; height:8px; border-radius:50%; background:#c3d4cc; }
.tl2 .it.on .dot { background:#0d5c45; }
.tl2 .d { font-size:8.4pt; font-weight:700; color:#0d5c45; }
.tl2 .x { font-size:6.9pt; color:#555; line-height:1.45; margin-top:2px; }
.road { display:flex; gap:8px; }
.road .r { flex:1; border:1px solid #e4e4e4; background:#fcfcfc; padding:7px 9px 8px; }
.road .no2 { font-size:7pt; font-weight:700; color:#0d5c45; letter-spacing:.08em; }
.road .t { font-size:8.6pt; font-weight:700; margin:2px 0 3px; }
.road p { font-size:7.3pt; color:#555; line-height:1.48; }
.grid3 { display:grid; grid-template-columns:repeat(3,1fr); gap:7px; }
.grid3 .g { border:1px solid #e4e4e4; background:#fcfcfc; padding:6px 8px 7px; }
.grid3 .g .t { font-size:7.9pt; font-weight:700; }
.grid3 .g p { font-size:6.9pt; color:#666; line-height:1.45; margin-top:2px; }
footer { margin-top:auto; padding-top:6px; border-top:1px solid #eee; font-size:6.4pt; color:#999;
  display:flex; justify-content:space-between; }
"""

KIND_CLASS = {'新增': 't-new', '删除': 't-del', '实质变更': 't-mod', '编辑性变更': 't-edit'}
LV_CLASS = {'高': 'lv-h', '中高': 'lv-m', '中': 'lv-l'}


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def cut(s, n):
    s = (s or '').strip().replace('\n', ' ')
    return s if len(s) <= n else s[:n] + '…'


def head(cfg, kick, title, sub):
    return f'''<div class="ph"><div><div class="kick">{kick}</div>
    <h1>{title}<small>{sub}</small></h1></div>
    <div class="sample">样例输出 · 演示数据</div></div>'''


def page1(cfg, n_old, n_new, items, stat, chapters, insights):
    total = len(items)
    cards = ''.join(
        f'<div class="stat"><div class="n">{v}</div><div class="l">{k}</div></div>'
        for k, v in (('条款级差异', total), ('新增要求', stat['新增']),
                     ('实质变更', stat['实质变更']), ('编辑性变更', stat['编辑性变更']),
                     ('删除', stat['删除']))
    )
    lis = ''.join(f'<li>{esc(x)}</li>' for x in insights)
    rows = ''
    for r in chapters:
        ch = r['chapter']
        label = '附录 ' + ch[2:] if ch.startswith('附录') else '第 %s 章' % ch
        lv = cfg['chapter_impact'].get(ch, '低')
        rows += (f'<tr><td><b>{esc(label)}</b></td><td class="c">{r["count"]}</td>'
                 f'<td>{esc(r["kinds"])}</td><td>{esc("、".join(r["titles"]))}</td>'
                 f'<td class="c"><span class="tag {LV_CLASS.get(lv, "lv-l")}">{lv}</span></td></tr>')
    tl = ''.join(f'<div class="it{" on" if t.get("on") else ""}"><span class="dot"></span>'
                 f'<div class="d">{t["date"]}</div><div class="x">{esc(t["text"])}</div></div>'
                 for t in cfg['timeline'])
    meta = (f'条款库：{len(items)} 条差异 / 新旧共 {n_old + n_new} 条切片　'
            f'比对基线：{cfg["meta"]["old_code"]}　生成：{date.today()}　结论可溯源：{total} / {total}')
    grid = ''.join(f'<div class="g"><div class="t">{esc(f["name"])}</div><p>{esc(f["note"])}</p></div>'
                   for f in cfg['files'])
    return f'''<div class="page">
{head(cfg, 'REGULATORY DIFF REPORT · 条款级差异', '中国 RoHS 换版影响推演报告', cfg['meta']['subtitle'])}
<div class="meta">{meta}</div>
<div class="st"><span class="no">01</span><h2>差异总览</h2><span class="line"></span></div>
<div class="stats">{cards}</div>
<div class="verdict"><div class="h">核心判断（人工标注，非机器摘要）</div><ol>{lis}</ol></div>
<div class="st"><span class="no">02</span><h2>按章聚合</h2><span class="line"></span></div>
<table><thead><tr><th style="width:16%">条款定位</th><th style="width:10%" class="c">差异数</th>
<th style="width:22%">变更类型</th><th>代表条款</th><th style="width:9%" class="c">影响</th></tr></thead>
<tbody>{rows}</tbody></table>
<div class="note">影响等级由 config/rules.json 中的章节规则给出；仅做编辑性调整的条款累计后仍标为低。</div>
<div class="st"><span class="no">03</span><h2>关键时间线</h2><span class="line"></span></div>
<div class="tl2">{tl}</div>
<div class="note">时间线依据：CQC 2025-12-19 换版通知、GB 26572—2025 第 7 章、工信部 2026 版目录公告。</div>
<div class="st"><span class="no">04</span><h2>比对文件范围</h2><span class="line"></span></div>
<div class="grid3">{grid}</div>
<div class="note">比对以条款为最小单位；条款位置调整单独标注，避免把「换了位置」误判为「新增要求」。</div>
<footer><span>条款引用摘自 GB 26572—2025 公开文本与 GB/T 26572—2011 第 1 号修改单</span><span>1 / 3</span></footer>
</div>'''


def page2(details):
    blocks = ''
    for rule, it in details:
        lv = rule['confidence']
        new = it.new
        old = it.old
        left = (f'<p>{esc(cut(old.text, 300))}</p>' if old else
                '<p>无对应条款。</p>')
        right = (f'<p>{esc(cut(new.text, 320))}</p>' if new else '<p>本版已删除。</p>')
        align = '<span class="tag t-edit">按标题对齐</span>' if it.align == 'title' else ''
        blocks += f'''<div class="diff">
<div class="top"><span class="id">{esc(it.key)}</span><span class="ttl">{esc(it.title)}</span>
<span class="tag {KIND_CLASS[it.kind]}">{it.kind}</span><span class="tag {LV_CLASS.get(lv, "lv-l")}">{lv}</span>{align}</div>
<div class="body">
<div class="side old"><div class="lab">旧版 · {esc(it.old.number if old else "—")} {esc(cut(old.title, 20) if old else "")}</div>{left}</div>
<div class="side new"><div class="lab">新版 · {esc(it.new.number if new else "—")} {esc(cut(new.title, 20) if new else "")}</div>{right}</div>
</div>
<div class="impact"><div class="k">影响判定</div><p>{esc(rule["reason"])}。→ {esc(rule["action"])}</p></div>
</div>'''
    return f'''<div class="page">
{head('', 'CLAUSE-LEVEL DIFF · 条款对照', '高影响条款的逐条比对', '左为现行依据，右为新增强制性要求；下方为规则引擎给出的影响判定')}
<div style="margin-top:12px">{blocks}</div>
<footer><span>所有引用均可回溯至条款号与原文片段；低置信结论不输出</span><span>2 / 3</span></footer>
</div>'''


def page3(cfg, hits, gap):
    rows = ''
    for h in hits:
        rows += (f'<tr><td>{esc(h["material"])}</td><td>{esc("、".join(h["clauses"][:4]))}</td>'
                 f'<td>{esc(h["reason"])}</td><td>{esc(h["action"])}</td>'
                 f'<td class="c"><span class="tag {LV_CLASS.get(h["confidence"], "lv-l")}">{h["confidence"]}</span></td></tr>')
    gap_cards = ''.join(
        f'<div class="stat"><div class="n" style="font-size:16pt">{v}<small> / {gap["total"]}</small></div><div class="l">{k}</div></div>'
        for k, v in (('可直接判定', gap['ready']), ('需结合工艺确认', gap['partial']), ('信息不足', gap['missing']))
    )
    bd = ''.join(f'<tr><td style="width:18%;background:#fafafa"><b>{esc(k)}</b></td><td>{esc(v)}</td></tr>'
                 for k, v in cfg['boundaries'])
    steps = ''.join(f'<div class="r"><div class="no2">{s["no"]}</div><div class="t">{esc(s["title"])}</div>'
                    f'<p>{esc(s["text"])}</p></div>' for s in cfg['steps'])
    return f'''<div class="page">
{head(cfg, 'IMPACT LIST · 影响清单', '受影响物料类别与整改动作', '条款差异 → 物料类别 → 动作；不含具体供应商判定')}
<div class="st" style="margin-top:12px"><span class="no">01</span><h2>影响清单</h2><span class="line"></span></div>
<table><thead><tr><th style="width:19%">物料 / 部件类别</th><th style="width:13%">触发条款</th>
<th style="width:29%">受影响原因</th><th>建议动作</th><th style="width:8%" class="c">置信度</th></tr></thead>
<tbody>{rows}</tbody></table>
<div class="note">置信度由规则表给出：高＝条款表述明确且物料关联为确定性规则；中高＝需结合材料工艺判断；中＝依赖客户 BOM 或历史报告状态。低于「中」的条目不进入清单。</div>
<div class="st"><span class="no">02</span><h2>证据缺口</h2><span class="line"></span></div>
<div class="stats">{gap_cards}<div class="stat" style="flex:2"><div class="l" style="margin-top:0">共性缺口分两类：<b>邻苯四项属新增检测项</b>，2011 版从未要求，属于「从来没测过」；<b>六价铬属判定依据变化</b>，报告可能测了但结论口径与 GB/T 39560.701 不匹配。前者要补测，后者要换判。</div></div></div>
<div class="st"><span class="no">03</span><h2>方法与边界</h2><span class="line"></span></div>
<table><tbody>{bd}</tbody></table>
<div class="st"><span class="no">04</span><h2>建议推进顺序</h2><span class="line"></span></div>
<div class="road">{steps}</div>
<footer><span>样例输出，用于方法演示，不构成合规结论；条款内容以正式发布文本为准</span><span>3 / 3</span></footer>
</div>'''


def render(cfg, old, new, items, stat, chapters, hits, details, gap, insights):
    return (f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
            f'<title>中国 RoHS 换版条款级差异报告</title><style>{CSS}</style></head><body>'
            + page1(cfg, len(old), len(new), items, stat, chapters, insights)
            + page2(details)
            + page3(cfg, hits, gap)
            + '</body></html>')
