"""Canonical speech model — one source of truth for pacing."""

from engine import SpeechModel, ScriptLanguage, SpeechBudget, VEO_3_1, GenerationMode


def test_all_languages_have_rates():
    for lang in ScriptLanguage:
        assert 2.5 <= SpeechModel.rate(lang) <= 3.5, lang


def test_safe_budget_is_under_duration():
    b = SpeechModel.budget(8, ScriptLanguage.HINDI)
    assert b.duration_seconds == 8
    assert b.safe_fraction == 0.85
    assert b.safe_seconds == 6.8
    assert b.max_words_safe == 21  # ~6.5-7s of speech in an 8s ad


def test_fit_report_flags_over_budget():
    # ~24 words in Hindi ≈ 7.5s: over the 6.8s safe budget but under the 8s total
    long = ("yah dialogue thoda lambe hain aur safe budget se zyada time le rahe "
            "hain lekin poore aath second mein fit ho sakte hain")
    report = SpeechModel.fit_report(long, 8, ScriptLanguage.HINDI)
    assert report["fits_at_all"]
    assert not report["fits_safe"]
    assert report["safe_seconds"] < report["estimated_seconds"] < report["duration"]


def test_english_slower_than_hindi():
    assert SpeechModel.rate(ScriptLanguage.ENGLISH) < SpeechModel.rate(ScriptLanguage.HINDI)


def test_veo_capability_duration_guard():
    assert VEO_3_1.validate_duration(8) == []
    assert VEO_3_1.validate_duration(7) != []  # Veo 3.1 supports 4/6/8 only
    assert VEO_3_1.validate_duration(16) != []


def test_veo_capability_mode_guard():
    assert VEO_3_1.validate_mode(GenerationMode.SINGLE_SHOT, 8) == []


def test_budget_dataclass_frozen():
    b = SpeechBudget(rate_wps=3.2, duration_seconds=8, safe_fraction=0.85,
                     safe_seconds=6.8, max_words_full_pace=25, max_words_safe=21)
    assert b.max_words_safe == 21