import base64
from io import BytesIO
import zipfile

from paperbanana_web.models import GenerationRequest
from paperbanana_web.pipeline import build_candidate_inputs
from paperbanana_web.results import candidate_zip, final_image


ONE_PIXEL_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4"
    "//8/AAX+Av4N70a4AAAAAElFTkSuQmCC"
)


def test_build_candidate_inputs_maps_request_and_unique_candidate_ids():
    request = GenerationRequest.for_provider(
        provider="gemini",
        method_content='{"x": [1, 2], "y": [3, 5]}',
        caption="Plot y against x.",
        task_name="plot",
        num_candidates=2,
        aspect_ratio="3:2",
        figure_size="10-13cm",
        max_critic_rounds=4,
    )

    inputs = build_candidate_inputs(request)

    assert [item["candidate_id"] for item in inputs] == [0, 1]
    assert [item["filename"] for item in inputs] == [
        "streamlit_candidate_0",
        "streamlit_candidate_1",
    ]
    assert inputs[0]["content"] == {"x": [1, 2], "y": [3, 5]}
    assert inputs[0]["additional_info"] == {
        "rounded_ratio": "3:2",
        "figure_size": "10-13cm",
        "image_size": "2k",
    }
    assert inputs[0]["max_critic_rounds"] == 4


def test_final_image_decodes_data_url_and_resolves_latest_critic_output():
    result = {
        "task_name": "diagram",
        "target_diagram_desc0_base64_jpg": "not-the-final-image",
        "target_diagram_critic_desc1_base64_jpg": f"data:image/png;base64,{ONE_PIXEL_PNG}",
    }

    image = final_image(result, "demo_planner_critic")

    assert image is not None
    assert image.size == (1, 1)


def test_candidate_zip_contains_valid_images_and_skips_malformed_results():
    results = [
        {
            "task_name": "diagram",
            "target_diagram_desc0_base64_jpg": ONE_PIXEL_PNG,
        },
        {
            "task_name": "diagram",
            "target_diagram_desc0_base64_jpg": "malformed",
        },
    ]

    archive = candidate_zip(results, "demo_planner_critic")

    with zipfile.ZipFile(BytesIO(archive)) as bundle:
        assert bundle.namelist() == ["paperbanana-candidate-01.png"]
        assert bundle.read("paperbanana-candidate-01.png").startswith(
            base64.b64decode(ONE_PIXEL_PNG)[:8]
        )
