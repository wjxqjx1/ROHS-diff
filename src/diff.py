"""条款对齐与差异分类。"""
import difflib
import re
from dataclasses import dataclass

PUNCT = re.compile(r'[\s，。、；：（）()“”"\'·\-—…《》]')


def norm(s):
    return PUNCT.sub('', s or '')


def sim(a, b):
    a, b = norm(a), norm(b)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


@dataclass
class DiffItem:
    key: str
    title: str
    kind: str
    score: float
    old: object
    new: object
    align: str

    @property
    def chapter(self):
        num = (self.new or self.old).number
        if num.startswith('附录'):
            return num
        return num.split('.')[0]

    def blob(self):
        parts = []
        if self.old is not None:
            parts.append(self.old.blob())
        if self.new is not None:
            parts.append(self.new.blob())
        return '。'.join(parts)


def compare(old, new):
    """按条款号对齐，孤立项按标题相似度兜底；未变化条款不输出。"""
    old = [c for c in old if c.text.strip()]
    new = [c for c in new if c.text.strip()]

    old_by_num = {c.number: c for c in old}
    used = set()
    items = []

    for n in new:
        o = old_by_num.get(n.number)
        align = 'number'
        if o is not None and sim(n.title, o.title) < 0.35:
            # 编号被复用：同一编号在两版指向不同条款，退回标题匹配
            o = None

        if o is None:
            best, best_s = None, 0.0
            for cand in old:
                if cand.number in used:
                    continue
                s = sim(n.title, cand.title)
                if s > best_s:
                    best, best_s = cand, s
            if best is not None and best_s >= 0.60:
                o, align = best, 'title'
            else:
                align = 'none'

        if o is None:
            items.append(DiffItem(n.number, n.title, '新增', 0.0, None, n, 'none'))
            continue

        used.add(o.number)
        s = sim(o.text, n.text)
        if s >= 0.97:
            continue
        kind = '编辑性变更' if s >= 0.80 else '实质变更'
        items.append(DiffItem(n.number, n.title, kind, round(s, 3), o, n, align))

    for o in old:
        if o.number not in used:
            items.append(DiffItem(o.number, o.title, '删除', 0.0, o, None, 'none'))
    return items


def summarize(items):
    stat = {'新增': 0, '删除': 0, '实质变更': 0, '编辑性变更': 0}
    for it in items:
        stat[it.kind] += 1
    return stat


def by_chapter(items):
    rows = {}
    for it in items:
        ch = it.chapter
        r = rows.setdefault(ch, {'chapter': ch, 'count': 0, 'kinds': set(), 'cand': []})
        r['count'] += 1
        r['kinds'].add(it.kind)
        r['cand'].append((len((it.new or it.old).text), it.title))
    out = []
    for ch, r in rows.items():
        r['kinds'] = ' / '.join(sorted(r['kinds']))
        r['titles'] = [t for _, t in sorted(r['cand'], reverse=True)[:3]]
        del r['cand']
        out.append(r)
    out.sort(key=lambda x: (not x['chapter'][0].isdigit(), x['chapter']))
    return out
