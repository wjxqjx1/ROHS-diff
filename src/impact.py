"""影响规则引擎：条款变更 → 物料类别 / 证据缺口 / 动作。"""
RANK = {'高': 3, '中高': 2, '中': 1}
# 引用文件与术语类变更通过实体条款生效，不作为影响触发条款
SKIP_TITLE = ('规范性引用文件', '范围', '术语和定义')


def match(items, rules):
    hits = []
    for r in rules:
        trig = [it for it in items
                if any(k in it.blob() for k in r['match'])]
        core = [it for it in trig if (it.new or it.old).title not in SKIP_TITLE]
        trig = core or trig
        if not trig:
            continue
        hits.append({
            'id': r['id'],
            'name': r['name'],
            'pick': r.get('pick'),
            'material': r['material'],
            'reason': r['reason'],
            'action': r['action'],
            'confidence': r['confidence'],
            'clauses': [t.key for t in trig],
            'samples': trig,
        })
    hits.sort(key=lambda h: (-RANK.get(h['confidence'], 0), h['id']))
    return hits


def pick_details(hits, limit=4):
    """每条规则取一条最有信息量的条款：实质变更优先，其次文本更长者。"""
    prio = {'实质变更': 3, '新增': 2, '删除': 1, '编辑性变更': 0}
    seen, out = set(), []
    for h in hits:
        cands = [it for it in h['samples']
                 if it.kind != '编辑性变更' and it.key not in seen]
        if not cands:
            continue
        pinned = [it for it in cands if it.key == h.get('pick')]
        if pinned:
            it = pinned[0]
        else:
            it = max(cands, key=lambda x: (prio.get(x.kind, 0), len((x.new or x.old).text)))
        seen.add(it.key)
        out.append((h, it))
        if len(out) >= limit:
            break
    return out


def evidence_gap(hits):
    """按置信度反推证据状态，用于报告中的缺口统计。"""
    total = len(hits)
    return {
        'total': total,
        'ready': sum(1 for h in hits if h['confidence'] == '高'),
        'partial': sum(1 for h in hits if h['confidence'] == '中高'),
        'missing': sum(1 for h in hits if h['confidence'] == '中'),
    }
