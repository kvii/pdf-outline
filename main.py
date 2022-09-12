import pikepdf as pp

from parse import OutlineItem, parse_reader

offset = 15
outline_file = '目录.txt'
source_file = '原文件.pdf'
dest_file = '结果.pdf'

with open(outline_file, encoding='utf-8') as f:
    items = parse_reader(f)


def change(item: OutlineItem) -> pp.OutlineItem:
    oi = pp.OutlineItem(item['name'], item['page']+offset-1)
    for sub in item['children']:
        oi.children.append(change(sub))
    return oi


with pp.Pdf.open(source_file) as pdf:
    with pdf.open_outline() as outline:
        outline.root.clear()
        for item in items:
            outline.root.append(change(item))

    pdf.save(dest_file)
