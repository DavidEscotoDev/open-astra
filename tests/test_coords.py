from openastra.coords import denormalize, clamp1000


def test_denormalize_center():
    assert denormalize(500, 500, 1920, 1080) == (960, 540)


def test_denormalize_clamps():
    assert denormalize(1500, -50, 1000, 1000) == (1000, 0)


def test_clamp1000():
    assert clamp1000(1500) == 1000
    assert clamp1000(-5) == 0
    assert clamp1000(512) == 512
