from argparse import ArgumentParser
from typing import List, Protocol

import pikepdf as pp

from outline import OutlineItem, format_writer


class Args(Protocol):
    """命令行参数"""
    offset: int
    """偏移量"""
    src: str
    """原文件路径"""
    outline: str
    """目录文件路径"""


parser = ArgumentParser(description='pdf 目录读取')
parser.add_argument('--offset', '-o',  type=int, default=0,
                    metavar='int', help='目录偏移量')
parser.add_argument('--outline',  type=str, default='data/目录.txt',
                    metavar='path', help='目录文件路径')
parser.add_argument('--src',  type=str, default='data/原文件.pdf',
                    metavar='path', help='原文件路径')
args: Args = parser.parse_args()


def _convert(item: pp.OutlineItem, offset: int) -> OutlineItem:
    name = item.title
    page = _page_of(item) - offset
    children = [_convert(sub, offset) for sub in item.children]
    return OutlineItem(name=name, page=page, children=children)


def _page_of(item: pp.OutlineItem) -> int:
    if isinstance(item.destination, pp.Array):
        page = pp.Page(item.destination[0])
        return page.index
    else:
        print(f"can't parse {item}")
        return 0


items: List[OutlineItem] = []

with pp.Pdf.open(args.src) as pdf:
    with pdf.open_outline() as outlines:
        for item in outlines.root:
            items.append(_convert(item, args.offset))

with open(args.outline, 'w') as w:
    format_writer(w, items)
