from .layout import ComputedStyle, BitMap, ScaledBitMap, Box, BlockBox, InlineBox, TextBox, BitMapBox

_DEFAULT_STYLE = ComputedStyle()

def iterate_children(children):
    if children is not None:
        for child in children:
            if child is not None:
                yield child

def normalize_child(style, child):
    if isinstance(child, str):
        return TextBox(style, child)

    if isinstance(child, (BitMap, ScaledBitMap)):
        return BitMapBox(style, child)

    return child

def same_instance(a, b, classinfo):
    return isinstance(a, classinfo) and isinstance(b, classinfo)

def diff_tree(a, b):
    if len(a) != len(b):
        return False

    nodes = [(a[i], b[i], True) for i in range(len(a))]
    updates = []

    while len(nodes) > 0:
        a, b, append = nodes.pop()

        if same_instance(a, b, BlockBox) or same_instance(a, b, InlineBox):
            if len(a.children) == len(b.children):
                if append and (a.dimensions != b.dimensions or a.style != b.style):
                    append = False
                    updates.append((a, b))

                for i, x in enumerate(a.children):
                    y = b.children[i]
                    nodes.append((x, y, append))
            else:
                return False
        elif same_instance(a, b, TextBox):
            if append and (a.text != b.text or a.style != b.style):
                updates.append((a, b))
        elif same_instance(a, b, BitMapBox):
            if append and (a.bitmap != b.bitmap or a.style != b.style):
                updates.append((a, b))
        else:
            return False

    return updates

def element(fn):
    def normalized(style=None, content=None):
        if content is None and not isinstance(style, ComputedStyle):
            content = style
            style = None

        return fn(style or _DEFAULT_STYLE, content)

    return normalized

@element
def block(style, children):
    return BlockBox(style, [normalize_child(style, child) for child in iterate_children(children)])

@element
def inline(style, children):
    return InlineBox(style, [normalize_child(style, child) for child in iterate_children(children)])

@element
def text(style, content):
    return TextBox(style, content)

@element
def bitmap(style, content):
    return BitMapBox(style, content)

class Decal:
    def __init__(self, viewport):
        self.viewport = viewport

    def __call__(self, new_children, diff=True):
        if isinstance(new_children, Box):
            new_children = [new_children]

        old_children = self.viewport.children
        self.viewport.children = new_children
        self.viewport.layout()
        updates = diff_tree(new_children, old_children) if diff else False

        if updates is False:
            yield (self.viewport, None)
        else:
            yield from updates
