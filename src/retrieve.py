"""条款级混合检索：字符 n-gram 倒排 + BM25 打分。"""
import math
import re
from collections import Counter, defaultdict

SEP = re.compile(r'[\s，。、；：（）()“”"\'·\-—…《》]+')


def tokens(text):
    text = SEP.sub(' ', text or '')
    out = []
    for w in text.split():
        out.extend(w[i:i + 2] for i in range(len(w) - 1))
        if len(w) == 1:
            out.append(w)
    return out


class Index:
    def __init__(self, clauses):
        self.clauses = clauses
        self.docs = [tokens(c.blob()) for c in clauses]
        self.df = defaultdict(int)
        for d in self.docs:
            for t in set(d):
                self.df[t] += 1
        self.avg = sum(len(d) for d in self.docs) / max(1, len(self.docs))
        self.n = max(1, len(self.docs))

    def search(self, q, top_k=5):
        qt = tokens(q)
        scored = []
        for c, d in zip(self.clauses, self.docs):
            tf = Counter(d)
            score = 0.0
            for t in qt:
                if t not in tf:
                    continue
                idf = math.log(1 + (self.n - self.df[t] + 0.5) / (self.df[t] + 0.5))
                denom = tf[t] + 1.5 * (1 - 0.75 + 0.75 * len(d) / self.avg)
                score += idf * tf[t] * 2.5 / denom
            if score > 0:
                scored.append((score, c))
        scored.sort(key=lambda x: -x[0])
        return scored[:top_k]
