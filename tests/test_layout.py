from decal import ComputedStyle, Box

def test_default_box():
    box = Box(ComputedStyle())

    assert box.x == 0
    assert box.y == 0
    assert box.width == 0
    assert box.height == 0
    assert box.left_offset == 0
    assert box.top_offset == 0
