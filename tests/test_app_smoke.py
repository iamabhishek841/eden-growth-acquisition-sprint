from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_app_starts_on_default_page():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_path))
    app.run(timeout=15)

    assert not app.exception
