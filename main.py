import io
import re
import sys
from pathlib import Path

from pikepdf import Array, Name, OutlineItem, Page, Pdf, String


#################
# Add bookmarks #
#################
def _get_parent_bookmark(current_indent, history_indent, bookmarks):
    '''The parent of A is the nearest bookmark whose indent is smaller than A's
    '''
    assert len(history_indent) == len(bookmarks)
    if current_indent == 0:
        return None
    for i in range(len(history_indent) - 1, -1, -1):
        # len(history_indent) - 1   ===>   0
        if history_indent[i] < current_indent:
            return bookmarks[i]
    return None


def addBookmark(pdf_path, bookmark_txt_path, page_offset):
    if not Path(pdf_path).exists():
        return "Error: No such file: {}".format(pdf_path)
    if not Path(bookmark_txt_path).exists():
        return "Error: No such file: {}".format(bookmark_txt_path)

    with io.open(bookmark_txt_path, 'r', encoding='utf-8') as f:
        bookmark_lines = f.readlines()

    pdf = Pdf.open(pdf_path)
    maxPages = len(pdf.pages)

    bookmarks, history_indent = [], []
    # decide the level of each bookmark according to the relative indent size in each line
    #   no indent:          level 1
    #     small indent:     level 2
    #       larger indent:  level 3
    #   ...
    with pdf.open_outline() as outline:
        outline.root.clear()
        for line in bookmark_lines:
            line2 = re.split(r'\s+', line.strip())
            if len(line2) == 1:
                continue

            indent_size = len(line) - len(line.lstrip())
            parent = _get_parent_bookmark(
                indent_size, history_indent, bookmarks)
            history_indent.append(indent_size)

            title, page = ' '.join(line2[:-1]), int(line2[-1]) - 1
            if page + page_offset >= maxPages:
                return "Error: page index out of range: %d >= %d" % (page + page_offset, maxPages)

            new_bookmark = OutlineItem(title, page + page_offset)
            if parent is None:
                outline.root.append(new_bookmark)
            else:
                parent.children.append(new_bookmark)
            bookmarks.append(new_bookmark)

    out_path = Path(pdf_path)
    out_path = out_path.with_name(out_path.stem + "-new.pdf")
    pdf.save(out_path)

    return "The bookmarks have been added to %s" % out_path


#####################
# Extract bookmarks #
#####################
def _getDestinationPageNumber(outline, names):
    def find_dest(ref, names):
        resolved = None
        if isinstance(ref, Array):
            resolved = ref[0]
        else:
            for n in range(0, len(names) - 1, 2):
                if names[n] == ref:
                    if names[n+1]._type_name == 'array':
                        named_page = names[n+1][0]
                    elif names[n+1]._type_name == 'dictionary':
                        named_page = names[n+1].D[0]
                    else:
                        raise TypeError("Unknown type: %s" % type(names[n+1]))
                    resolved = named_page
                    break
        if resolved is not None:
            return Page(resolved).index

    if outline.destination is not None:
        if isinstance(outline.destination, Array):
            # 12.3.2.2 Explicit destination
            # [raw_page, /PageLocation.SomeThing, integer parameters for viewport]
            raw_page = outline.destination[0]
            try:
                page = Page(raw_page)
                dest = page.index
            except:
                dest = find_dest(outline.destination, names)
        elif isinstance(outline.destination, String):
            # 12.3.2.2 Named destination, byte string reference to Names
            # dest = f'<Named Destination in document .Root.Names dictionary: {outline.destination}>'
            assert names is not None
            dest = find_dest(outline.destination, names)
        elif isinstance(outline.destination, Name):
            # 12.3.2.2 Named desintation, name object (PDF 1.1)
            # dest = f'<Named Destination in document .Root.Dests dictionary: {outline.destination}>'
            dest = find_dest(outline.destination, names)
        elif isinstance(outline.destination, int):
            # Page number
            dest = outline.destination
        else:
            dest = outline.destination
        return dest
    else:
        return find_dest(outline.action.D, names)


def _parse_outline_tree(outlines, level=0, names=None):
    """Return List[Tuple[level(int), page(int), title(str)]]"""
    ret = []
    if isinstance(outlines, (list, tuple)):
        for heading in outlines:
            # contains sub-headings
            ret.extend(_parse_outline_tree(heading, level=level, names=names))
    else:
        ret.append((level, _getDestinationPageNumber(
            outlines, names) + 1, outlines.title))
        for subheading in outlines.children:
            # contains sub-headings
            ret.extend(_parse_outline_tree(
                subheading, level=level+1, names=names))
    return ret


def extractBookmark(pdf_path, bookmark_txt_path):
    # https://github.com/pikepdf/pikepdf/issues/149#issuecomment-860073511
    def has_nested_key(obj, keys):
        ok = True
        to_check = obj
        for key in keys:
            if key in to_check.keys():
                to_check = to_check[key]
            else:
                ok = False
                break
        return ok

    def get_names(pdf):
        if has_nested_key(pdf.Root, ['/Names', '/Dests']):
            obj = pdf.Root.Names.Dests
            names = []
            ks = obj.keys()
            if '/Names' in ks:
                names.extend(obj.Names)
            elif '/Kids' in ks:
                for k in obj.Kids:
                    names.extend(get_names(k))
            else:
                assert False
            return names
        else:
            return None

    if not Path(pdf_path).exists():
        return "Error: No such file: {}".format(pdf_path)
    if Path(bookmark_txt_path).exists():
        print("Warning: Overwriting {}".format(bookmark_txt_path))

    pdf = Pdf.open(pdf_path)
    names = get_names(pdf)
    with pdf.open_outline() as outline:
        outlines = _parse_outline_tree(outline.root, names=names)
    if len(outlines) == 0:
        return "No bookmark is found in %s" % pdf_path
    # List[Tuple[level(int), page(int), title(str)]]
    max_length = max(len(item[-1]) + 2 * item[0] for item in outlines) + 1
    # print(outlines)
    with open(bookmark_txt_path, 'w') as f:
        for level, page, title in outlines:
            level_space = '  ' * level
            title_page_space = ' ' * (max_length - level * 2 - len(title))
            f.write("{}{}{}{}\n".format(
                level_space, title, title_page_space, page))
    return "The bookmarks have been exported to %s" % bookmark_txt_path


if __name__ == "__main__":
    import sys
    args = sys.argv
    # print(extractBookmark(args[1], args[2]))
    if len(args) != 4:
        print("Usage: %s [pdf] [bookmark_txt] [page_offset]" % args[0])
    else:
        print(addBookmark(args[1], args[2], int(args[3])))
