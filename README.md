# decal

A small declarative MicroPython GUI library for display drivers based on the [FrameBuffer](https://docs.micropython.org/en/latest/library/framebuf.html) interface.

The library is inspired by HTML and CSS layout and rendering.

## Usage

There are two elements for layout control, `block` and `inline`. The children of a `block` element are laid out vertically while the children of a `inline` element are laid out horizontally.

Furthermore there are two content elements, `text` and `bitmap`. The `text` element renders text strings while the `bitmap` element renders `BitMap` objects containing monochrome pixel data. The `text` element is assumed by default if a string is encountered, usually there is no need to use it explicitly.

```python
import framebuf
from decal import (
    ComputedStyle,
    Color,
    Align,
    BoxSizing,
    Percentage,
    BitMap,
    Viewport,
    Position,
    Dimensions,
    draw,
    block,
    inline)

# Font structure specifying font width and height.
# Required for calculating position when laying out text.
class font8x8:
    @staticmethod
    def width(text):
        return len(text) * 6

    @staticmethod
    def height(text):
        return 8

# Additional characters not contained in the the default character set.
# The bits in a byte are vertically mapped with bit 0 being nearest the top.
# Similar to definition of framebuf.MONO_VLSB format.
FONT_8_DEGREE = BitMap(bytes([0x00, 0x00, 0x00, 0x06, 0x09, 0x09, 0x06, 0x00]))
FONT_8_LEFT_TRIANGLE = BitMap(bytes([0x00, 0x08, 0x1c, 0x3e, 0x7f, 0x7f, 0x7f, 0x7f]))

# Structure for organizing styling.
class menu_style:
    root = ComputedStyle.shorthand(
        padding_top=2
    )

    item_selected = ComputedStyle.shorthand(
        background_color=Color.WHITE,
        foreground_color=Color.BLACK,
        padding=2,
        width=Percentage(100),
        box_sizing=BoxSizing.BORDER,
        font=font8x8
    )

    item_default = ComputedStyle.shorthand(
        padding=2,
        width=Percentage(100),
        box_sizing=BoxSizing.BORDER,
        font=font8x8
    )

    item_text_selected = ComputedStyle.shorthand(
        foreground_color=Color.BLACK,
        align=Align.END,
        font=font8x8
    )

    item_text_default = ComputedStyle.shorthand(
        align=Align.END,
        font=font8x8
    )

# The actual UI elements to be rendered.
element = block(menu_style.root, [
    inline(menu_style.item_default, [
        'Temperature',
        inline(menu_style.item_text_default, ['25', FONT_8_DEGREE, 'C'])
    ]),
    inline(menu_style.item_selected, [
        'Amperage',
        inline(menu_style.item_text_selected, ['5A'])
    ]),
    inline(menu_style.item_default, ['Settings']),
    inline(menu_style.item_default, ['Firmware']),
    inline(menu_style.item_default, [FONT_8_LEFT_TRIANGLE, ' Back'])
])

# The global viewport used to lay out the individual UI elements.
# The viewport itself is only a container and not rendered to the frame buffer.
viewport = Viewport(Position(0, 0), Dimensions(128, 64), [element])
viewport.layout()

# Built-in MicroPython frame buffer.
frame_buffer = framebuf.FrameBuffer(bytearray(1024), 128, 64, framebuf.MONO_VLSB)

# Call draw to actually draw the UI elements to frame buffer.
draw(viewport, frame_buffer)
```

The above example will draw the following UI on a monochrome 128 x 64 pixel screen.

![UI](/assets/ui.bmp)
