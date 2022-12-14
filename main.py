import argparse
from typing import Protocol

import pikepdf as pp

from outline import OutlineItem, parse_reader


class Args(Protocol):
    """命令行参数类型"""
    offset: int
    """目录偏移量"""
    outline: str
    """目录文件路径"""
    src: str
    """源文件路径"""
    dest: str
    """结果文件路径"""


parser = argparse.ArgumentParser(description='pdf 目录添加')
parser.add_argument('--offset', '-o',  type=int, default=0,
                    metavar='int', help='目录偏移量')
parser.add_argument('--outline',  type=str, default='data/目录.txt',
                    metavar='path', help='目录文件路径')
parser.add_argument('--src',  type=str, default='data/原文件.pdf',
                    metavar='path', help='原文件路径')
parser.add_argument('--dest',  type=str, default='data/结果.pdf',
                    metavar='path', help='结果文件路径')
args: Args = parser.parse_args()


def _convert(item: OutlineItem) -> pp.OutlineItem:
    oi = pp.OutlineItem(item['name'], item['page']+args.offset-1)
    for sub in item['children']:
        oi.children.append(_convert(sub))
    return oi


with open(args.outline, encoding='utf-8') as f:
    items = parse_reader(f)

with pp.Pdf.open(args.src) as pdf:
    with pdf.open_outline() as outline:
        outline.root.clear()
        for item in items:
            outline.root.append(_convert(item))
    pdf.save(args.dest)
