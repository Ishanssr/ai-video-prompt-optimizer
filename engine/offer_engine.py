from .types import (
    OfferClaim, OfferType, ScriptLanguage,
)


def create_verified_offer(
    offer_type: OfferType,
    value: str = None,
    numeric_value: float = None,
    unit: str = None,
    validity: str = None,
    model: str = None,
    geography: str = None,
    finance_conditions: str = None,
    source: str = None,
) -> OfferClaim:
    """Create a verified offer claim. Only verified claims produce specific numbers."""
    return OfferClaim(
        offer_type=offer_type,
        value=value,
        numeric_value=numeric_value,
        unit=unit,
        validity=validity,
        model=model,
        geography=geography,
        finance_conditions=finance_conditions,
        source=source,
        verified=True,
    )


def create_unverified_offer(
    offer_type: OfferType = OfferType.GENERIC,
    description: str = "",
) -> OfferClaim:
    """Create an unverified offer. Will NOT produce specific numbers."""
    return OfferClaim(
        offer_type=offer_type,
        value=description,
        verified=False,
    )


def offer_to_script_text(claim: OfferClaim, lang: ScriptLanguage = ScriptLanguage.HINDI) -> str:
    """Convert offer claim to safe script text. No hallucinated specifics."""
    if not claim.verified:
        return claim.to_safe_text(lang)

    parts = []
    if claim.numeric_value and claim.unit:
        amt = f"{claim.unit}{claim.numeric_value:,.0f}"
        type_text = {
            OfferType.CASHBACK: f"{amt} cashback mil raha hai",
            OfferType.EXCHANGE_BONUS: f"{amt} exchange bonus mil raha hai",
            OfferType.FREE_ACCESSORY: f"free accessories worth {amt}",
            OfferType.FESTIVE_DISCOUNT: f"{amt} tak ka discount hai",
            OfferType.CORPORATE_DISCOUNT: f"{amt} corporate discount available hai",
        }
        text = type_text.get(claim.offer_type, f"{amt} ka benefit hai")
        parts.append(text)
    elif claim.value:
        parts.append(claim.value)

    if claim.finance_conditions:
        parts.append(f"EMI {claim.finance_conditions} se shuru")

    if claim.validity:
        parts.append(f"ye offer sirf {claim.validity} tak hai")

    return ". ".join(parts) if parts else claim.to_safe_text(lang)


def offer_to_voiceover(claim: OfferClaim, lang: ScriptLanguage = ScriptLanguage.HINDI) -> str:
    """Convert offer to voiceover-friendly line."""
    if not claim.verified:
        return "Special offers available hain. Details ke liye showroom visit kijiye."

    parts = []
    if claim.numeric_value and claim.unit:
        amt = f"{claim.unit}{claim.numeric_value:,.0f}"
        parts.append(f"Abhi {amt} tak ka benefit available hai")
    if claim.validity:
        parts.append(f"ye offer sirf {claim.validity} tak hai valid")

    return ". ".join(parts) if parts else "Special offers available hain."


def safety_check(claim: OfferClaim) -> list:
    """Returns warnings if offer claim is potentially problematic."""
    warnings = []
    if claim.numeric_value and claim.numeric_value > 100000:
        warnings.append("High numeric value detected — verify with source")
    if not claim.source:
        warnings.append("No source specified — claim not verifiable")
    if not claim.validity:
        warnings.append("No validity date — may be misleading")
    if claim.offer_type in (OfferType.ZERO_DOWNPAYMENT, OfferType.FINANCE_RATE) and not claim.finance_conditions:
        warnings.append("Finance offer without conditions — add T&C reference")
    return warnings
