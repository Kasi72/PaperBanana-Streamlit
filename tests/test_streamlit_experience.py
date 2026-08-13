from paperbanana_web.experience import build_readiness, can_generate


def test_readiness_identifies_every_missing_generation_input():
    checks = build_readiness(
        provider="openrouter",
        api_key="",
        method_content="",
        caption="",
        task_name="diagram",
        aspect_ratio="16:9",
        num_candidates=4,
    )

    assert [check.label for check in checks] == [
        "Provider connection",
        "Method or data",
        "Figure caption",
        "Configuration",
    ]
    assert [check.ready for check in checks] == [False, False, False, True]
    assert checks[0].detail == "Add a session-only OpenRouter key"
    assert checks[1].detail == "Describe the science to visualize"
    assert checks[2].detail == "State the figure's communication goal"
    assert not can_generate(checks)


def test_readiness_summarizes_complete_inputs_without_exposing_the_key():
    secret = "sk-or-v1-abcdefghijklmnopqrstuvwxyz"
    checks = build_readiness(
        provider="openrouter",
        api_key=secret,
        method_content="A graph neural network passes messages across molecular bonds.",
        caption="Overview of the message-passing architecture and prediction head.",
        task_name="diagram",
        aspect_ratio="3:2",
        num_candidates=3,
    )

    assert all(check.ready for check in checks)
    assert checks[0].detail == "OpenRouter key ready for this session"
    assert checks[1].detail == "9 words supplied"
    assert checks[2].detail == "8 words supplied"
    assert checks[3].detail == "Diagram · 3:2 · 3 candidates"
    assert secret not in " ".join(check.detail for check in checks)
    assert can_generate(checks)


def test_readiness_treats_short_credentials_as_not_ready():
    checks = build_readiness(
        provider="gemini",
        api_key="too-short",
        method_content="Method",
        caption="Caption",
        task_name="plot",
        aspect_ratio="16:9",
        num_candidates=1,
    )

    assert checks[0].ready is False
    assert checks[0].detail == "Add a session-only Gemini key"
    assert not can_generate(checks)
