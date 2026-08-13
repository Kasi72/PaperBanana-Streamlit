def test_deployment_theme_module_exposes_all_streamlit_fragments():
    from paperbanana_web import studio_theme

    assert "--pb-gold" in studio_theme.APP_CSS
    assert 'aria-label="Figure workflow"' in studio_theme.WORKFLOW_HTML
    assert "Five specialists" in studio_theme.AGENT_PIPELINE_HTML
