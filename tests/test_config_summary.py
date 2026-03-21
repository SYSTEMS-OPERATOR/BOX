import config_summary


def test_project_name():
    assert config_summary.get_project_name() == "SOPHY Embodied Evennia Server"


def test_monday_name():
    assert config_summary.get_monday_name() == "Monday"


def test_style_count():
    assert config_summary.get_style_count() == 23
