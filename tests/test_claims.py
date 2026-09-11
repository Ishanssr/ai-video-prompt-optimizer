"""Commercial claim validation: offers, superlatives, finance, urgency, safety."""

from engine import (
    check_commercial_claims, ClaimCategory, ScriptLanguage,
    OfferType, create_verified_offer, create_unverified_offer, get_brand_policy,
)


def test_superlative_detected():
    issues = check_commercial_claims("Ye hamari best-selling SUV hai.", None, None, ScriptLanguage.HINDI)
    cats = [i.category for i in issues]
    assert ClaimCategory.SUPERLATIVE in cats
    errs = [i for i in issues if i.is_error]
    assert errs, "superlative must be an error"


def test_sabse_safe_detected():
    issues = check_commercial_claims("Ye sabse safe car hai.", None, None, ScriptLanguage.HINDI)
    assert any(i.category == ClaimCategory.SUPERLATIVE for i in issues)


def test_number_claim_without_verification_blocked():
    issues = check_commercial_claims("₹50,000 cashback mil raha hai.", None, None, ScriptLanguage.HINDI)
    assert any(i.category == ClaimCategory.FINANCE and i.is_error for i in issues)


def test_verified_number_claim_ok():
    offer = create_verified_offer(OfferType.CASHBACK, numeric_value=50000, unit="₹",
                                  validity="31 Dec 2026", source="memo #1")
    issues = check_commercial_claims("₹50,000 cashback mil raha hai.", offer, None, ScriptLanguage.HINDI)
    assert not any(i.category == ClaimCategory.FINANCE and i.is_error for i in issues)


def test_urgency_without_validity_blocked():
    issues = check_commercial_claims("Limited time offer hai, jaldi karein.", None, None, ScriptLanguage.HINDI)
    assert any(i.category == ClaimCategory.URGENCY for i in issues)


def test_urgency_with_validity_ok():
    offer = create_verified_offer(OfferType.FESTIVE_DISCOUNT, validity="31 Dec 2026", source="memo #1")
    issues = check_commercial_claims("Limited time offer hai.", offer, None, ScriptLanguage.HINDI)
    assert not any(i.category == ClaimCategory.URGENCY and i.is_error for i in issues)


def test_safety_claim_warns():
    issues = check_commercial_claims("5-star GNCAP rated car.", None, get_brand_policy("Tata"), ScriptLanguage.HINDI)
    assert any(i.category == ClaimCategory.SAFETY for i in issues)


def test_high_value_warns():
    offer = create_verified_offer(OfferType.CASHBACK, numeric_value=500000, unit="₹",
                                  validity="31 Dec 2026", source="memo #1")
    issues = check_commercial_claims("₹5,00,000 cashback mil raha hai.", offer, None, ScriptLanguage.HINDI)
    assert any(i.category == ClaimCategory.OFFER and i.severity == "warning" for i in issues)


def test_clean_script_no_issues():
    issues = check_commercial_claims(
        "Ismein special finance options available hain. Aaj hi showroom visit kijiye.",
        None, None, ScriptLanguage.HINDI,
    )
    assert issues == []