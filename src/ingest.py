"""法规文本装载：按「章—条—款」切片并保留层级路径。"""
import io
import re
from dataclasses import dataclass

HEAD = re.compile(r'^(#{1,6})\s*(.+?)\s*$')
NUM = re.compile(r'^((?:\d+\.)*\d+|附录\s*[A-Z])\s*(.*)$')


@dataclass
class Clause:
    number: str
    title: str
    text: str
    level: int
    path: tuple = ()

    @property
    def key(self):
        return self.number

    def blob(self):
        return self.title + '。' + self.text


def load(path):
    items, cur = [], None
    for raw in io.open(path, encoding='utf-8'):
        line = raw.rstrip('\n')
        m = HEAD.match(line)
        if m:
            if cur is not None:
                items.append(cur)
            level = len(m.group(1))
            head = m.group(2).strip()
            nm = NUM.match(head)
            if nm:
                number, title = nm.group(1).replace(' ', ''), nm.group(2).strip()
            else:
                number, title = head, head
            cur = Clause(number=number, title=title or number, text='', level=level)
        elif cur is not None and line.strip():
            cur.text += line.strip() + '\n'
    if cur is not None:
        items.append(cur)

    stack = []
    for c in items:
        while stack and stack[-1][0] >= c.level:
            stack.pop()
        c.path = tuple([s[1] for s in stack] + [c.number])
        stack.append((c.level, c.number))
    return items
