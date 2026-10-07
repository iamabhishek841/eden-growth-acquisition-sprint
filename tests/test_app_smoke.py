from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"

PAGES = [
    "Growth command centre",
    "Acquisition channels",
    "Experiment studio",
    "Measurement plan",
    "Conversion & A/B testing",
    "SEO & content",
    "CRM & retention",
    "Partnerships & referrals",
    "30-day sprint",
]


@pytest.mark.parametrize("page", PAGES)
def test_every_workspace_renders_without_exception(page):
    app = AppTest.from_file(str(APP_PATH))
    app.run(timeout=20)

    app.sidebar.radio[0].set_value(page)
    app.run(timeout=20)

    assert not app.exception
