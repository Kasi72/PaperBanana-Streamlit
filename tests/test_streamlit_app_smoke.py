from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).parents[1] / "streamlit_app.py"


def test_streamlit_app_renders_generate_workspace_without_credentials():
    app = AppTest.from_file(APP_PATH).run(timeout=30)

    assert not app.exception
    assert app.title[0].value == "Create a scientific figure"
    assert [area.label for area in app.text_area] == [
        "Method or data",
        "Figure caption",
    ]
    assert "Generate candidates" in [button.label for button in app.button]
    assert "Load example" in [button.label for button in app.button]


def test_load_example_populates_both_authoring_fields():
    app = AppTest.from_file(APP_PATH).run(timeout=30)
    load_example = next(
        button for button in app.button if button.label == "Load example"
    )

    load_example.click().run(timeout=30)

    assert app.text_area[0].value.startswith("## Retrieval-augmented")
    assert "faithfulness feedback loop" in app.text_area[1].value
