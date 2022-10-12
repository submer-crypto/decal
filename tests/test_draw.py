from decal import draw, ComputedStyle, BlockBox

def test_draw_block_box():
    box = BlockBox(ComputedStyle(), [])

    # Nothing raised
    draw(box, None)
