"""中国 RoHS 换版条款级差异推演 —— 命令行入口。

用法：
  python main.py build                      # 比对两版条款并生成 HTML + PDF
  python main.py build --no-pdf             # 只生成 HTML
  python main.py query "六价铬怎么判定"       # 条款级检索（带出处）
  python main.py stats                      # 查看语料与差异统计
"""
import argparse
import io
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src import diff, impact, ingest, report, retrieve  # noqa: E402

ROOT = os.path.dirname(os.path.abspath(__file__))


def read_insights(path):
    if not os.path.exists(path):
        return []
    return [ln.strip() for ln in io.open(path, encoding='utf-8') if ln.strip()]


def find_browser():
    for p in (r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
              r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
              r'C:\Program Files\Google\Chrome\Application\chrome.exe'):
        if os.path.exists(p):
            return p
    return None


def to_pdf(html_path, pdf_path):
    exe = find_browser()
    if not exe:
        print('[warn] 未找到 Edge/Chrome，跳过 PDF 导出')
        return False
    url = 'file:///' + html_path.replace('\\', '/')
    subprocess.run([exe, '--headless', '--disable-gpu', '--no-pdf-header-footer',
                    '--print-to-pdf=' + pdf_path, url],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    return os.path.exists(pdf_path)


def load_config(path):
    return json.load(io.open(path, encoding='utf-8'))


def analyse(args):
    cfg = load_config(args.config)
    old = ingest.load(args.old)
    new = ingest.load(args.new)
    items = diff.compare(old, new)
    return {
        'cfg': cfg, 'old': old, 'new': new, 'items': items,
        'stat': diff.summarize(items),
        'chapters': diff.by_chapter(items),
        'hits': impact.match(items, cfg['rules']),
    }


def cmd_build(args):
    a = analyse(args)
    details = impact.pick_details(a['hits'], args.details)
    gap = impact.evidence_gap(a['hits'])
    insights = read_insights(args.insights)
    html = report.render(a['cfg'], a['old'], a['new'], a['items'], a['stat'],
                         a['chapters'], a['hits'], details, gap, insights)
    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    io.open(args.out, 'w', encoding='utf-8').write(html)

    st = a['stat']
    print('切片：旧版 %d 条 / 新版 %d 条' % (len(a['old']), len(a['new'])))
    print('差异：%d 条（新增 %d / 删除 %d / 实质变更 %d / 编辑性变更 %d）'
          % (len(a['items']), st['新增'], st['删除'], st['实质变更'], st['编辑性变更']))
    print('章节：' + '，'.join('%s章 %d 条' % (c['chapter'], c['count']) for c in a['chapters']))
    print('规则命中：%d 组，明细取前 %d 条' % (len(a['hits']), len(details)))
    for h in a['hits']:
        print('  [%s] %-14s %s' % (h['confidence'], h['name'], '、'.join(h['clauses'][:5])))
    print('报告：' + os.path.abspath(args.out))
    if not args.no_pdf:
        pdf = os.path.splitext(args.out)[0] + '.pdf'
        print('PDF ：' + (os.path.abspath(pdf) if to_pdf(args.out, pdf) else '导出失败'))


def cmd_query(args):
    new = ingest.load(args.new)
    idx = retrieve.Index([c for c in new if c.text.strip()])
    hits = idx.search(args.text, args.top)
    if not hits:
        print('信息不足：未命中任何条款，按策略拒答。')
        return
    for score, c in hits:
        print('%.2f  [%s] %s' % (score, c.number, c.title))
        print('      ' + c.text.strip().replace('\n', ' ')[:110] + '...')


def cmd_stats(args):
    a = analyse(args)
    print('旧版条款：%d' % len(a['old']))
    print('新版条款：%d' % len(a['new']))
    print('差异条目：%d' % len(a['items']))
    for k, v in a['stat'].items():
        print('  %-6s %d' % (k, v))
    print('规则库：%d 条' % len(a['cfg']['rules']))


def main():
    p = argparse.ArgumentParser(description='中国 RoHS 换版条款级差异推演')
    sub = p.add_subparsers(dest='cmd')

    def add_common(sp):
        sp.add_argument('--old', default=os.path.join(ROOT, 'data', 'v2011.md'))
        sp.add_argument('--new', default=os.path.join(ROOT, 'data', 'v2025.md'))
        sp.add_argument('--config', default=os.path.join(ROOT, 'config', 'rules.json'))

    b = sub.add_parser('build', help='生成差异报告')
    add_common(b)
    b.add_argument('--out', default=os.path.join(ROOT, 'out', 'rohs-diff-report.html'))
    b.add_argument('--insights', default=os.path.join(ROOT, 'data', 'insights.txt'))
    b.add_argument('--details', type=int, default=4)
    b.add_argument('--no-pdf', action='store_true')
    b.set_defaults(func=cmd_build)

    q = sub.add_parser('query', help='条款级检索')
    q.add_argument('text')
    q.add_argument('--new', default=os.path.join(ROOT, 'data', 'v2025.md'))
    q.add_argument('--top', type=int, default=5)
    q.set_defaults(func=cmd_query)

    s = sub.add_parser('stats', help='查看统计')
    add_common(s)
    s.set_defaults(func=cmd_stats)

    args = p.parse_args()
    if not getattr(args, 'func', None):
        p.print_help()
        return
    args.func(args)


if __name__ == '__main__':
    main()
