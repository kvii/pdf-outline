import io
import re
from typing import List, TypedDict


class OutlineItem(TypedDict):
    """目录项目"""
    name: str
    """目录名"""
    page: int
    """页号"""
    children: List["OutlineItem"]
    """子目录"""


class ParseError(Exception):
    """解析异常"""


def parse_str(s: str):
    """将字符串解析为目录格式"""
    return parse_reader(io.StringIO(s))


def parse_reader(r: io.TextIOBase) -> List[OutlineItem]:
    """将字符串解析为目录格式"""
    li = []
    parents = []
    for s in r:
        if s.strip() == "":
            continue
        
        if _reg_comment.match(s):
            continue
        
        depth, name, page = _parse_line(s)
        if depth > len(parents):
            raise ParseError(f'标题缩进数量错误 {name}')

        item = OutlineItem(
            name=name,
            page=page,
            children=[]
        )
        if depth == 0:
            parents = [item]
            li.append(item)
        elif len(parents) == depth:
            parents[depth-1]['children'].append(item)
            parents.append(item)
        else:
            parents[depth-1]['children'].append(item)
            parents = parents[:depth]
            parents.append(item)
    return li


_reg_outline = re.compile(r'^(\t*)([^\s].*)\s+(-?\d+)$')
"""书签正则"""

_reg_comment = re.compile(r'^--')
"""注释正则"""


def _parse_line(s: str):
    """解析一行"""
    m = _reg_outline.match(s)
    if m is None:
        raise ParseError(f'格式错误 {s}')

    depth, name, page = m.groups('')
    return depth.count('\t'), name, int(page)


def format_str(items: List[OutlineItem]) -> str:
    """将目录数据格式化为字符串"""
    with io.StringIO() as w:
        format_writer(w, items)
        return w.getvalue()


def format_writer(w: io.TextIOBase, items: List[OutlineItem]):
    """将目录格式化到流中"""
    def f(item: OutlineItem, indent: str):
        w.write(f"{indent}{item['name']} {item['page']}\n")
        for sub in item['children']:
            f(sub, indent+'\t')

    for item in items:
        f(item, '')
