from decal import Decal, ComputedStyle, Viewport, Position, Dimensions, BlockBox, TextBox, block, inline

class Font8:
    def __eq__(self, other):
        return isinstance(other, Font8)

    def width(self, text):
        return len(text) * 8

    def height(self, text):
        return 8

def layout(box, position, dimensions):
    box.position = position
    box.dimensions = dimensions
    return box

def test_empty_render():
    viewport = Viewport(Position(0, 0), Dimensions(0, 0), [])
    render = Decal(viewport)

    updates = list(render([]))

    assert len(updates) == 0

def test_add_box_render():
    viewport = Viewport(Position(0, 0), Dimensions(0, 0), [])
    render = Decal(viewport)

    updates = list(render(block()))

    assert len(updates) == 1
    assert updates[0] == (Viewport(Position(0, 0), Dimensions(0, 0), [BlockBox(ComputedStyle(), [])]), None)

def test_change_text_render():
    viewport = Viewport(Position(0, 0), Dimensions(0, 64), [
        block([
            inline(ComputedStyle(font=Font8()), ['hello'])
        ])
    ])

    viewport.layout()
    render = Decal(viewport)

    updates = list(render(
        block([
            inline(ComputedStyle(font=Font8()), ['world'])
        ])
    ))

    assert len(updates) == 1
    assert updates[0] == (
        layout(TextBox(ComputedStyle(font=Font8()), 'world'), Position(0, 0), Dimensions(40, 8)),
        layout(TextBox(ComputedStyle(font=Font8()), 'hello'), Position(0, 0), Dimensions(40, 8)))
