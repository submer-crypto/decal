from .layout import Color, TextDecorationLine, Viewport, TextBox, BitMapBox

def background(box, framebuf):
    x = box.position.x - box.style.padding_left
    y = box.position.y - box.style.padding_top
    width = box.dimensions.width + box.style.padding_left + box.style.padding_right
    height = box.dimensions.height + box.style.padding_top + box.style.padding_bottom

    if width and height and box.style.background_color != Color.TRANSPARENT:
        framebuf.fill_rect(x, y, width, height, box.style.background_color)

def border(box, framebuf):
    horizontal = (box.dimensions.width +
        box.style.border_width_left +
        box.style.padding_left +
        box.style.padding_right +
        box.style.border_width_right)

    vertical = (box.dimensions.height +
        box.style.border_width_top +
        box.style.padding_top +
        box.style.padding_bottom +
        box.style.border_width_bottom)

    # top
    x = box.position.x - box.style.padding_left - box.style.border_width_left
    y = box.position.y - box.style.padding_top - box.style.border_width_top
    width = horizontal
    height = box.style.border_width_top

    if width and height and box.style.border_color_top != Color.TRANSPARENT:
        framebuf.fill_rect(x, y, width, height, box.style.border_color_top)

    # right
    x = box.position.x + box.dimensions.width + box.style.padding_right
    y = box.position.y - box.style.padding_top - box.style.border_width_top
    width = box.style.border_width_right
    height = vertical

    if width and height and box.style.border_color_right != Color.TRANSPARENT:
        framebuf.fill_rect(x, y, width, height, box.style.border_color_right)

    # bottom
    x = box.position.x - box.style.padding_left - box.style.border_width_left
    y = box.position.y + box.dimensions.height + box.style.padding_bottom
    width = horizontal
    height = box.style.border_width_bottom

    if width and height and box.style.border_color_bottom != Color.TRANSPARENT:
        framebuf.fill_rect(x, y, width, height, box.style.border_color_bottom)

    # left
    x = box.position.x - box.style.padding_left - box.style.border_width_left
    y = box.position.y - box.style.padding_top - box.style.border_width_top
    width = box.style.border_width_left
    height = vertical

    if width and height and box.style.border_color_left != Color.TRANSPARENT:
        framebuf.fill_rect(x, y, width, height, box.style.border_color_left)

def text(box, framebuf):
    if box.style.foreground_color != Color.TRANSPARENT:
        framebuf.text(box.text, box.position.x, box.position.y, box.style.foreground_color)

    if (box.style.text_decoration_line != TextDecorationLine.NONE and
            box.style.text_decoration_color != Color.TRANSPARENT and
            box.style.text_decoration_thickness):
        if box.style.text_decoration_line == TextDecorationLine.UNDERLINE:
            y = box.position.y + box.dimensions.height + box.style.text_decoration_offset
        elif box.style.text_decoration_line == TextDecorationLine.OVERLINE:
            y = box.position.y - box.style.text_decoration_thickness - box.style.text_decoration_offset
        elif box.style.text_decoration_line == TextDecorationLine.LINE_THROUGH:
            y = (box.position.y +
                box.style.text_decoration_offset +
                (box.dimensions.height - box.style.text_decoration_thickness) // 2)

        framebuf.fill_rect(
            box.position.x,
            y,
            box.dimensions.width,
            box.style.text_decoration_thickness,
            box.style.text_decoration_color)

def bitmap(box, framebuf):
    for dx, dy, bit in box.bitmap:
        pixel = box.style.foreground_color if bit else box.style.background_color

        if pixel != Color.TRANSPARENT:
            framebuf.pixel(box.position.x + dx, box.position.y + dy, pixel)

def draw(box, framebuf):
    def draw_children(parent):
        for child in parent.children:
            draw(child, framebuf)

    if isinstance(box, Viewport):
        draw_children(box)
    elif isinstance(box, TextBox):
        text(box, framebuf)
    elif isinstance(box, BitMapBox):
        bitmap(box, framebuf)
    else:
        background(box, framebuf)
        border(box, framebuf)
        draw_children(box)
