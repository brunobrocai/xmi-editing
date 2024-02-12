import element_editing as ed


def test_is_inside_coords():
    assert ed.is_inside_coords((1, 2), (0, 3)) == [False, False]
    assert ed.is_inside_coords((1, 2), (1, 2)) == [True, True]
    assert ed.is_inside_coords((1, 2), (1, 3)) == [True, False]
    assert ed.is_inside_coords((1, 2), (0, 2)) == [False, True]
    assert ed.is_inside_coords((1, 2), (3, 4)) is False
