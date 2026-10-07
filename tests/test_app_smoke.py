from streamlit.testing.v1 import AppTest


def test_app_starts_on_default_page():
    app = AppTest.from_file("app.py")
    app.run(timeout=15)

    assert not app.exception
