from .types import BrandPolicy


BRAND_POLICIES = {
    "Hyundai": BrandPolicy(
        brand="Hyundai",
        approved_model_names=["Creta", "Venue", "Verna", "Alcazar", "Venue N Line"],
        approved_offer_wording=[
            "special finance offers",
            "exchange bonus",
            "festive offers",
        ],
        approved_terminology=[
            "SmartSense safety",
            "BlueLink connectivity",
            "e-CALL (SOS)",
            "Panoramic Sunroof",
        ],
        logo_handling="do_not_generate_text",
        dealership_environment="official Hyundai showroom",
        no_invented_claims=True,
        no_altered_geometry=True,
        tagline="Transforming Mobility",
    ),
    "Maruti Suzuki": BrandPolicy(
        brand="Maruti Suzuki",
        approved_model_names=["Swift", "Baleno", "Fronx", "Grand Vitara", "Jimny"],
        approved_offer_wording=[
            "exclusive discounts",
            "exchange offers",
            "subscription plans",
        ],
        approved_terminology=[
            "S-CNG",
            "NEXA experience",
            "Arena network",
            "Suzuki Connect",
        ],
        logo_handling="do_not_generate_text",
        dealership_environment="official Maruti Suzuki dealership",
        no_invented_claims=True,
        no_altered_geometry=True,
    ),
    "Mahindra": BrandPolicy(
        brand="Mahindra",
        approved_model_names=["XUV 700", "Scorpio-N", "Thar", "XUV 3XO"],
        approved_offer_wording=[
            "festive discounts",
            "exchange bonus",
        ],
        approved_terminology=[
            "AdrenoX technology",
            "big screen display",
            "driver assist",
        ],
        logo_handling="do_not_generate_text",
        dealership_environment="official Mahindra dealership",
        no_invented_claims=True,
        no_altered_geometry=True,
    ),
    "Kia": BrandPolicy(
        brand="Kia",
        approved_model_names=["Seltos", "Sonet", "Carens"],
        approved_offer_wording=[
            "special finance offers",
            "exchange benefits",
        ],
        approved_terminology=[
            "UVO connected car",
            "Level 2 ADAS",
        ],
        logo_handling="do_not_generate_text",
        dealership_environment="official Kia dealership",
        no_invented_claims=True,
        no_altered_geometry=True,
    ),
    "Tata": BrandPolicy(
        brand="Tata",
        approved_model_names=["Nexon", "Punch", "Harrier", "Safari", "Tiago"],
        approved_offer_wording=[
            "exchange bonus",
            "festive offers",
        ],
        approved_terminology=[
            "5-star safety",
            "GNCAP",
            "connected car tech",
        ],
        logo_handling="do_not_generate_text",
        dealership_environment="official Tata Motors dealership",
        no_invented_claims=True,
        no_altered_geometry=True,
        tagline="Connecting Aspirations",
    ),
}

DEFAULT_POLICY = BrandPolicy(
    brand="OEM",
    approved_model_names=[],
    approved_offer_wording=[],
    approved_terminology=[],
    logo_handling="do_not_generate_text",
    dealership_environment="official dealership",
    no_invented_claims=True,
    no_altered_geometry=True,
)


def get_brand_policy(brand: str) -> BrandPolicy:
    """Get brand policy. Returns generic safe policy if brand unknown."""
    return BRAND_POLICIES.get(brand, DEFAULT_POLICY)


def validate_brand_safety(policy: BrandPolicy, model: str, offer_text: str = "", script_text: str = "") -> list:
    """Check that model name, offer wording and script text comply with brand."""
    violations = []
    text = " ".join([model, offer_text, script_text]).lower()

    if policy.approved_model_names and text:
        if model.lower() and model.lower() not in [m.lower() for m in policy.approved_model_names]:
            violations.append(f"Model '{model}' not in approved list: {policy.approved_model_names}")

    if policy.no_invented_claims and any(word in text for word in ["zero down payment", "₹50,000 cashback", "7.99% emi"]):
        violations.append("Invented offer claim detected — remove or verify with source")

    if "logo" in text or " showroom sign " in text:
        violations.append("Do not reference logos/readable text in prompt")

    return violations


def build_brand_constraint_section(policy: BrandPolicy) -> str:
    """Build brand constraint paragraph for prompt metadata."""
    lines = []
    lines.append(f"Brand: {policy.brand} (official dealership setting)")
    if policy.approved_terminology:
        lines.append(f"Approved terminology: {', '.join(policy.approved_terminology)}")
    lines.append("No invented claims, no altered vehicle geometry")
    lines.append("Do not generate readable logos or model-name text")
    return ". ".join(lines)