from openastra.executor import click_px, type_text


def test_click_dry_run():
    assert click_px(100, 200, dry_run=True) == (100, 200)


def test_type_dry_run():
    assert type_text("hi", dry_run=True) == "hi"
