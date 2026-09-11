"""Script engine: whole-sentence rewriting, never mid-sentence truncation."""

from engine import (
    CampaignObjective, AdConcept, ScriptLanguage, generate_script,
    rewrite_script_to_fit, script_to_colon_format, SpeechModel,
)

SUPERLATIVE_TOKENS = ["best-selling", "best selling", "sabse", "ek number", "perfect", "safest", "most popular"]


def test_default_scripts_have_no_superlatives():
    for objective in list(CampaignObjective):
        for concept in list(AdConcept):
            s = generate_script(objective, concept, ScriptLanguage.HINDI)
            full = " ".join(l.text for l in s.all_lines).lower()
            for tok in SUPERLATIVE_TOKENS:
                assert tok not in full, f"{objective}/{concept} still has '{tok}'"


def test_rewrite_keeps_whole_sentences_only():
    s = generate_script(CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED, ScriptLanguage.HINDI)
    r = rewrite_script_to_fit(s, target_seconds=8)
    original = {l.segment: l for l in s.all_lines}
    for line in r.all_lines:
        if not line.text:
            continue
        ok = line.text == original[line.segment].text or line.text == original[line.segment].condensed
        assert ok, f"{line.segment} was truncated mid-sentence: {line.text!r}"


def test_cta_always_survives_rewrite():
    s = generate_script(CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED, ScriptLanguage.HINDI)
    for seconds in (4, 6, 8):
        r = rewrite_script_to_fit(s, target_seconds=seconds)
        assert r.cta.text, f"CTA lost at {seconds}s"


def test_rewritten_dialogue_fits_safe_budget():
    s = generate_script(CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED, ScriptLanguage.HINDI)
    r = rewrite_script_to_fit(s, target_seconds=8)
    report = SpeechModel.fit_report(r.dialogue_text(8), 8, ScriptLanguage.HINDI)
    assert report["fits_safe"]


def test_short_budget_prefers_priority_and_drops_hook():
    s = generate_script(CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED, ScriptLanguage.HINDI)
    r = rewrite_script_to_fit(s, target_seconds=4)  # tiny budget (13 words)
    assert r.offer.text or r.offer.condensed, "offer is top priority for enquiry"
    assert r.cta.text, "CTA always preserved"
    assert len(r.dialogue_text(4).split()) <= SpeechModel.budget(4, ScriptLanguage.HINDI).max_words_safe


def test_custom_lines_survive_rewrite_when_they_fit():
    s = generate_script(CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED, ScriptLanguage.HINDI,
                        custom_cta="Aaj hi apna test drive book kijiye.")
    r = rewrite_script_to_fit(s, target_seconds=8)
    assert r.cta.text == "Aaj hi apna test drive book kijiye."


def test_colon_format_is_clean():
    s = generate_script(CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED, ScriptLanguage.HINDI)
    colon = script_to_colon_format(s, 8)
    assert ".." not in colon
    assert colon.strip() != ""


def test_spoken_lines_carry_real_timings():
    s = generate_script(CampaignObjective.ENQUIRY, AdConcept.PRESENTER_LED, ScriptLanguage.HINDI)
    spoken = s.spoken_lines(8)
    assert spoken, "expected at least one spoken line"
    assert all("start_seconds" in sl and "duration_seconds" in sl for sl in spoken)
    assert spoken[-1]["end_seconds"] <= 8.5  # timings bounded near the ad window