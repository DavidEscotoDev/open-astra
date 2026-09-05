from openastra.grounder import CenterGrounder


def test_center_grounder():
    g = CenterGrounder()
    assert g.ground(b"png", 1920, 1080, "Search box") == (500, 500)
