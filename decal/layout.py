def expand_border(i, direction, attribute, combined):
    if direction is not None and direction[i] is not None:
        return direction[i]

    if attribute is not None:
        return attribute

    return combined[i]

def calculate_width(style, parent):
    if isinstance(style.width, Percentage):
        if style.box_sizing == BoxSizing.CONTENT:
            available_width = parent.dimensions.width
        elif style.box_sizing == BoxSizing.BORDER:
            available_width = (parent.dimensions.width -
                style.border_width_left -
                style.padding_left -
                style.border_width_right -
                style.padding_right)

        return style.width * available_width
    elif style.width is not None:
        return style.width

def calculate_height(style, parent):
    if isinstance(style.height, Percentage):
        if style.box_sizing == BoxSizing.CONTENT:
            available_height = parent.dimensions.height
        elif style.box_sizing == BoxSizing.BORDER:
            available_height = (parent.dimensions.height -
                style.border_width_top -
                style.padding_top -
                style.border_width_bottom -
                style.padding_bottom)

        return style.height * available_height
    elif style.height is not None:
        return style.height

class ScaledBitMap:
    def __init__(self, bitmap, ratio):
        self.bitmap = bitmap
        self.ratio = ratio
        self.width = bitmap.width * ratio
        self.height = bitmap.height * ratio

    def __repr__(self):
        return f'ScaledBitMap({repr(self.bitmap)}, {self.ratio})'

    def __getitem__(self, coordinates):
        x, y = coordinates
        return self.bitmap[x // self.ratio, y // self.ratio]

    def __len__(self):
        return self.width * self.height

    def __iter__(self):
        for x in range(self.width):
            for y in range(self.height):
                # Nearest neighbour
                yield (x, y, self[x, y])

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, ScaledBitMap):
            return False

        return self.bitmap == other.bitmap and self.ratio == other.ratio

    def __hash__(self):
        return hash((self.bitmap, self.ratio))

    def scale(self, ratio):
        return ScaledBitMap(self.bitmap, self.ratio * ratio)

class BitMap:
    # Buffer length must be multiple of width.
    # Each byte in buffer is a column of 8 pixels. LSB at top.
    def __init__(self, buffer, offset=0, length=None, width=None):
        self.buffer = buffer
        self.offset = offset
        self.length = length if length is not None else len(buffer)
        self.width = width if width is not None else self.length
        self.height = (self.length // self.width) * 8

    def __repr__(self):
        return f'BitMap(bytes({len(self.buffer)}), offset={self.offset}, length={self.length}, width={self.width})'

    def __getitem__(self, coordinates):
        x, y = coordinates
        b = self.buffer[self.offset + (y // 8) * self.width + x]
        return (b >> (y % 8)) & 1

    def __len__(self):
        return self.width * self.height

    def __iter__(self):
        for x in range(self.width):
            for y in range(self.height):
                yield (x, y, self[x, y])

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, BitMap):
            return False

        if self.length != other.length or self.width != other.width:
            return False

        for i in range(self.length):
            if self.buffer[self.offset + i] != other.buffer[other.offset + i]:
                return False

        return True

    def __hash__(self):
        return hash((
            self.length,
            self.width,
            self.buffer[self.offset:self.offset + self.length]))

    def scale(self, ratio):
        return ScaledBitMap(self, ratio)

class Color:
    TRANSPARENT = -1
    BLACK = 0
    WHITE = 1

class BorderStyle:
    NONE = 0
    SOLID = 1
    DASHED = 2

class Align:
    START = 0
    CENTER = 1
    END = 2

class BoxSizing:
    CONTENT = 0
    BORDER = 1

class Percentage:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f'{self.value}%'

    def __repr__(self):
        return f'Percentage({self.value})'

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, Percentage):
            return False

        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __mul__(self, other):
        if isinstance(other, Percentage):
            other = other.value

        return (other * self.value) // 100

class ComputedStyle:
    PROPERTIES = (
        'margin_top',
        'margin_right',
        'margin_bottom',
        'margin_left',
        'padding_top',
        'padding_right',
        'padding_bottom',
        'padding_left',
        'border_width_top',
        'border_width_right',
        'border_width_bottom',
        'border_width_left',
        'border_style_top',
        'border_style_right',
        'border_style_bottom',
        'border_style_left',
        'border_color_top',
        'border_color_right',
        'border_color_bottom',
        'border_color_left',
        'x',
        'y',
        'width',
        'height',
        'background_color',
        'foreground_color',
        'font',
        'align',
        'box_sizing')

    @classmethod
    def shorthand(cls,
            margin=0,
            padding=0,
            border=(0, BorderStyle.NONE, 0),
            border_top=None,
            border_right=None,
            border_bottom=None,
            border_left=None,
            border_width=None,
            border_style=None,
            border_color=None,
            **kwargs):

        expand = dict(
            margin_top=margin,
            margin_right=margin,
            margin_bottom=margin,
            margin_left=margin,
            padding_top=padding,
            padding_right=padding,
            padding_bottom=padding,
            padding_left=padding,
            border_width_top=expand_border(0, border_top, border_width, border),
            border_width_right=expand_border(0, border_right, border_width, border),
            border_width_bottom=expand_border(0, border_bottom, border_width, border),
            border_width_left=expand_border(0, border_left, border_width, border),
            border_style_top=expand_border(1, border_top, border_style, border),
            border_style_right=expand_border(1, border_right, border_style, border),
            border_style_bottom=expand_border(1, border_bottom, border_style, border),
            border_style_left=expand_border(1, border_left, border_style, border),
            border_color_top=expand_border(2, border_top, border_color, border),
            border_color_right=expand_border(2, border_right, border_color, border),
            border_color_bottom=expand_border(2, border_bottom, border_color, border),
            border_color_left=expand_border(2, border_left, border_color, border))

        expand.update(kwargs)
        return cls(**expand)

    def __init__(self,
            margin_top=0,
            margin_right=0,
            margin_bottom=0,
            margin_left=0,
            padding_top=0,
            padding_right=0,
            padding_bottom=0,
            padding_left=0,
            border_width_top=0,
            border_width_right=0,
            border_width_bottom=0,
            border_width_left=0,
            border_style_top=BorderStyle.NONE,
            border_style_right=BorderStyle.NONE,
            border_style_bottom=BorderStyle.NONE,
            border_style_left=BorderStyle.NONE,
            border_color_top=Color.TRANSPARENT,
            border_color_right=Color.TRANSPARENT,
            border_color_bottom=Color.TRANSPARENT,
            border_color_left=Color.TRANSPARENT,
            x=None,
            y=None,
            width=None,
            height=None,
            background_color=Color.TRANSPARENT,
            foreground_color=Color.WHITE,
            font=None,
            align=Align.START,
            box_sizing=BoxSizing.CONTENT):

        if border_style_top == BorderStyle.NONE:
            border_width_top = 0

        if border_style_right == BorderStyle.NONE:
            border_width_right = 0

        if border_style_bottom == BorderStyle.NONE:
            border_width_bottom = 0

        if border_style_left == BorderStyle.NONE:
            border_width_left = 0

        self.margin_top = margin_top
        self.margin_right = margin_right
        self.margin_bottom = margin_bottom
        self.margin_left = margin_left
        self.padding_top = padding_top
        self.padding_right = padding_right
        self.padding_bottom = padding_bottom
        self.padding_left = padding_left
        self.border_width_top = border_width_top
        self.border_width_right = border_width_right
        self.border_width_bottom = border_width_bottom
        self.border_width_left = border_width_left
        self.border_style_top = border_style_top
        self.border_style_right = border_style_right
        self.border_style_bottom = border_style_bottom
        self.border_style_left = border_style_left
        self.border_color_top = border_color_top
        self.border_color_right = border_color_right
        self.border_color_bottom = border_color_bottom
        self.border_color_left = border_color_left
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.background_color = background_color
        self.foreground_color = foreground_color
        self.font = font
        self.align = align
        self.box_sizing = box_sizing

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, ComputedStyle):
            return False

        return all(getattr(self, name) == getattr(other, name) for name in ComputedStyle.PROPERTIES)

    def __hash__(self):
        return hash(tuple(getattr(self, name) for name in ComputedStyle.PROPERTIES))

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Position({self.x}, {self.y})'

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, Position):
            return False

        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

class Dimensions:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __repr__(self):
        return f'Dimensions({self.width}, {self.height})'

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, Dimensions):
            return False

        return self.width == other.width and self.height == other.height

    def __hash__(self):
        return hash((self.width, self.height))

class Box:
    def __init__(self, style):
        self.style = style
        self.position = Position(0, 0)
        self.dimensions = Dimensions(0, 0)

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, Box):
            return False

        return (self.position == other.position and
            self.dimensions == other.dimensions and
            self.style == other.style)

    def __hash__(self):
        return hash((self.position, self.dimensions, self.style))

    @property
    def x(self):
        return self.position.x - self.left_offset

    @property
    def y(self):
        return self.position.y - self.top_offset

    @property
    def width(self):
        return (self.style.margin_left +
            self.style.border_width_left +
            self.style.padding_left +
            self.dimensions.width +
            self.style.padding_right +
            self.style.border_width_right +
            self.style.margin_right)

    @property
    def height(self):
        return (self.style.margin_top +
            self.style.border_width_top +
            self.style.padding_top +
            self.dimensions.height +
            self.style.padding_bottom +
            self.style.border_width_bottom +
            self.style.margin_bottom)

    @property
    def left_offset(self):
        return (self.style.margin_left +
            self.style.border_width_left +
            self.style.padding_left)

    @property
    def top_offset(self):
        return (self.style.margin_top +
            self.style.border_width_top +
            self.style.padding_top)

    def translate(self, dx, dy):
        self.position.x += dx
        self.position.y += dy

class Viewport:
    def __init__(self, position, dimensions, children):
        self.position = position
        self.dimensions = dimensions
        self.children = children

    def __repr__(self):
        children = ', '.join(repr(child) for child in self.children)
        return f'Viewport({self.position}, {self.dimensions}, [{children}])'

    def __eq__(self, other):
        if self is other:
            return True

        if not isinstance(other, Viewport):
            return False

        if len(self.children) != len(other.children):
            return False

        return (self.position == other.position and
            self.dimensions == other.dimensions and
            all(self.children[i] == other.children[i] for i in range(len(self.children))))

    def __hash__(self):
        return hash((self.position, self.dimensions, *self.children))

    def layout(self):
        child_height = 0

        for child in self.children:
            # Children layout same as a block box
            if child.style.x is None:
                child.position.x = (self.position.x +
                    child.left_offset)
            else:
                child.position.x = child.style.x

            if child.style.y is None:
                child.position.y = (self.position.y +
                    child_height +
                    child.top_offset)
            else:
                child.position.y = child.style.y

            child.layout(self)

            if child.style.x is None and child.style.y is None:
                child_height += child.height

        if self.dimensions.height is None:
            self.dimensions.height = child_height

class BlockBox(Box):
    def __init__(self, style, children):
        super().__init__(style)
        self.children = children

    def __repr__(self):
        children = ', '.join(repr(child) for child in self.children)
        return f'BlockBox(ComputedStyle(), [{children}])'

    def __eq__(self, other):
        if not super().__eq__(other):
            return False

        if not isinstance(other, BlockBox):
            return False

        if len(self.children) != len(other.children):
            return False

        return all(self.children[i] == other.children[i] for i in range(len(self.children)))

    def __hash__(self):
        return hash((super().__hash__(), *self.children))

    def layout(self, parent):
        if self.style.width is None:
            horizontal = (self.style.margin_left +
                self.style.margin_right +
                self.style.border_width_left +
                self.style.border_width_right +
                self.style.padding_left +
                self.style.padding_right)

            self.dimensions.width = parent.dimensions.width - horizontal
        else:
            self.dimensions.width = calculate_width(self.style, parent)

        self.dimensions.height = calculate_height(self.style, parent)

        child_height = 0

        for child in self.children:
            if child.style.x is None:
                child.position.x = (self.position.x +
                    child.left_offset)
            else:
                child.position.x = child.style.x

            if child.style.y is None:
                child.position.y = (self.position.y +
                    child_height +
                    child.top_offset)
            else:
                child.position.y = child.style.y

            child.layout(self)

            if child.style.x is None and child.style.y is None:
                child_height += child.height

        if self.style.height is None:
            self.dimensions.height = child_height

    def translate(self, dx, dy):
        super().translate(dx, dy)

        for child in self.children:
            child.translate(dx, dy)

class InlineBox(Box):
    def __init__(self, style, children):
        super().__init__(style)
        self.children = children

    def __repr__(self):
        children = ', '.join(repr(child) for child in self.children)
        return f'InlineBox(ComputedStyle(), [{children}])'

    def __eq__(self, other):
        if not super().__eq__(other):
            return False

        if not isinstance(other, InlineBox):
            return False

        if len(self.children) != len(other.children):
            return False

        return all(self.children[i] == other.children[i] for i in range(len(self.children)))

    def __hash__(self):
        return hash((super().__hash__(), *self.children))

    def layout(self, parent):
        self.dimensions.width = calculate_width(self.style, parent)
        self.dimensions.height = calculate_height(self.style, parent)

        child_width = 0
        child_height = 0

        for child in self.children:
            child.position.x = (self.position.x +
                child_width +
                child.left_offset)

            child.position.y = (self.position.y +
                child.top_offset)

            child.layout(self)

            child_width += child.width
            child_height = max(child_height, child.height)

        if self.style.height is None:
            self.dimensions.height = child_height

        if self.style.width is None:
            self.dimensions.width = child_width

        underflow = parent.dimensions.width - self.width

        if underflow > 0 and self.style.align != Align.START:
            dx = 0

            if self.style.align == Align.CENTER:
                dx = underflow // 2
            elif self.style.align == Align.END:
                dx = underflow

            self.translate(dx - self.position.x + parent.position.x, 0)

    def translate(self, dx, dy):
        super().translate(dx, dy)

        for child in self.children:
            child.translate(dx, dy)

class TextBox(Box):
    def __init__(self, style, text):
        super().__init__(style)
        self.text = text

    def __repr__(self):
        return f'TextBox(ComputedStyle(), \'{self.text}\')'

    def __eq__(self, other):
        if not super().__eq__(other):
            return False

        if not isinstance(other, TextBox):
            return False

        return self.text == other.text

    def __hash__(self):
        return hash((super().__hash__(), self.text))

    @property
    def width(self):
        return self.style.font.width(self.text)

    @property
    def height(self):
        return self.style.font.height(self.text)

    @property
    def left_offset(self):
        return 0

    @property
    def top_offset(self):
        return 0

    def layout(self, parent):
        self.dimensions.height = self.height
        self.dimensions.width = self.width

class BitMapBox(Box):
    def __init__(self, style, bitmap):
        super().__init__(style)
        self.bitmap = bitmap

    def __repr__(self):
        return f'BitMapBox(ComputedStyle(), {repr(self.bitmap)})'

    def __eq__(self, other):
        if not super().__eq__(other):
            return False

        if not isinstance(other, BitMapBox):
            return False

        return self.bitmap == other.bitmap

    def __hash__(self):
        return hash((super().__hash__(), self.bitmap))

    @property
    def width(self):
        return self.bitmap.width

    @property
    def height(self):
        return self.bitmap.height

    @property
    def left_offset(self):
        return 0

    @property
    def top_offset(self):
        return 0

    def layout(self, parent):
        self.dimensions.height = self.height
        self.dimensions.width = self.width
