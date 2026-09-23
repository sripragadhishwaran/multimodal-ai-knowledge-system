from retrieval.section_policy import SectionPolicyEngine


def test_content_section_has_neutral_priority():
    engine = SectionPolicyEngine()

    priority = engine.get_priority(
        query="What topics are explained?",
        section_type="content",
    )

    assert priority == 1.0


def test_references_are_lower_priority_for_normal_query():
    engine = SectionPolicyEngine()

    priority = engine.get_priority(
        query="What topics are explained in the PDF?",
        section_type="references",
    )

    assert priority == 0.85


def test_reference_query_restores_neutral_priority():
    engine = SectionPolicyEngine()

    priority = engine.get_priority(
        query="What references are cited in the PDF?",
        section_type="references",
    )

    assert priority == 1.0


def test_unknown_section_is_neutral():
    engine = SectionPolicyEngine()

    priority = engine.get_priority(
        query="What topics are explained?",
        section_type="unknown_section",
    )

    assert priority == 1.0


def test_missing_section_is_neutral():
    engine = SectionPolicyEngine()

    priority = engine.get_priority(
        query="What topics are explained?",
        section_type=None,
    )

    assert priority == 1.0
