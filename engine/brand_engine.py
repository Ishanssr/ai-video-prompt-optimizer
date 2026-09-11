from .types import BrandPolicy, ModelSpec, VariantSpec


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


# ─── Model / variant / feature database ─────────────────────────────
# Feature claims are only emitted for the model/variant that actually has them.

def _V(name, features, transmission=""):
    return VariantSpec(name=name, features=features, transmission=transmission)


MODEL_FEATURES = {
    "Hyundai": {
        "Creta": ModelSpec(
            model="Creta",
            body_type="SUV",
            variants=[
                _V("E", [], "manual"),
                _V("S", ["traction control"], "manual"),
                _V("S(O)", ["traction control"], "manual"),
                _V("SX", ["sunroof", "BlueLink", "rear camera"], "manual"),
                _V("SX(O)", ["panoramic sunroof", "BlueLink", "e-CALL", "SmartSense", "ventilated seats"], "automatic"),
                _V("SX(O) Turbo", ["panoramic sunroof", "BlueLink", "e-CALL", "SmartSense", "ventilated seats"], "automatic"),
            ],
            shared_features=["All-New Creta", "LED headlamps", "bluetooth"],
            unavailable_features=["ADAS Level 2"],
        ),
        "Venue": ModelSpec(
            model="Venue",
            body_type="SUV",
            variants=[
                _V("E", ["traction control"], "manual"),
                _V("S", ["traction control"], "manual"),
                _V("S(O)", ["received bluelink", "rear camera"], "manual"),
                _V("SX(O)", ["BlueLink", "panoramic sunroof", "SmartSense", "ventilated seats"], "automatic"),
            ],
            shared_features=["LED headlamps"],
            unavailable_features=["ADAS Level 2"],
        ),
        "Verna": ModelSpec(
            model="Verna",
            body_type="sedan",
            variants=[
                _V("S", ["bluetooth"], "manual"),
                _V("SX", ["BlueLink", "rear camera"], "manual"),
                _V("SX(O)", ["BlueLink", "panoramic sunroof", "SmartSense", "ventilated seats"], "automatic"),
            ],
            shared_features=[],
            unavailable_features=["ADAS Level 2"],
        ),
        "Alcazar": ModelSpec(
            model="Alcazar",
            body_type="SUV",
            variants=[
                _V("Prestige", ["sunroof", "BlueLink"], "manual"),
                _V("Platinum", ["panoramic sunroof", "BlueLink", "ventilated seats"], "automatic"),
                _V("Platinum(O)", ["panoramic sunroof", "BlueLink", "e-CALL", "SmartSense"], "automatic"),
            ],
            shared_features=["6-seat option", "LED headlamps"],
            unavailable_features=["ADAS Level 2"],
        ),
    },
    "Tata": {
        "Nexon": ModelSpec(
            model="Nexon",
            body_type="SUV",
            variants=[
                _V("Creative", []),
                _V("Fearless", ["panoramic sunroof", "connected car tech"]),
                _V("Fearless+", ["panoramic sunroof", "connected car tech", "5-star GNCAP safety"]),
            ],
            shared_features=["5-star GNCAP safety"],
            unavailable_features=["ADAS"],
        ),
        "Harrier": ModelSpec(
            model="Harrier",
            body_type="SUV",
            variants=[
                _V("Smart", []),
                _V("Fearless", ["panoramic sunroof"]),
                _V("Fearless+", ["panoramic sunroof", "connected car tech", "ADAS", "5-star GNCAP safety"]),
            ],
            shared_features=["5-star GNCAP safety"],
            unavailable_features=[],
        ),
        "Safari": ModelSpec(
            model="Safari",
            body_type="SUV",
            variants=[
                _V("Smart", []),
                _V("Fearless", ["panoramic sunroof"]),
                _V("Fearless+", ["panoramic sunroof", "connected car tech", "ADAS", "5-star GNCAP safety"]),
            ],
            shared_features=["5-star GNCAP safety"],
            unavailable_features=[],
        ),
    },
}


def get_model_spec(brand: str, model: str) -> ModelSpec:
    """Model-level spec for a brand+model, for feature-applicability checks."""
    db = MODEL_FEATURES.get(brand, {})
    return db.get(model)


def validate_model_feature(brand: str, model: str, feature: str) -> dict:
    """Would 'feature' be a verifiable claim for this model?"""
    spec = get_model_spec(brand, model)
    if spec is None:
        return {
            "verifiable": False,
            "feature": feature,
            "model": model,
            "reason": "model not in feature database — treat claim as unverified",
        }
    return {**spec.feature_applicability(feature), "verifiable": True}


def get_brand_policy(brand: str) -> BrandPolicy:
    """Get brand policy. Returns generic safe policy if brand unknown."""
    return BRAND_POLICIES.get(brand, DEFAULT_POLICY)


def validate_brand_safety(policy: BrandPolicy, model: str, offer_text: str = "", script_text: str = "") -> list:
    """Check that model name, offer wording and script text comply with brand."""
    violations = []
    text = " ".join([model, offer_text, script_text]).lower()

    if policy.approved_model_names and model.lower():
        if model.lower() not in [m.lower() for m in policy.approved_model_names]:
            violations.append(f"Model '{model}' not in approved list: {policy.approved_model_names}")

    if policy.no_invented_claims and any(word in text for word in ["zero down payment", "₹50,000 cashback", "7.99% emi"]):
        violations.append("Invented offer claim detected — remove or verify with source")

    if "logo" in text or " showroom sign " in text:
        violations.append("Do not reference logos/readable text in prompt")

    return violations


def build_brand_constraint_section(policy: BrandPolicy) -> str:
    """Build brand constraint paragraph for prompt metadata."""
    lines = []
    lines.append(f"{policy.brand} (official dealership setting)")
    if policy.approved_terminology:
        lines.append(f"Approved terms: {', '.join(policy.approved_terminology)}")
    lines.append("No invented claims, no altered vehicle geometry")
    lines.append("Do not generate readable logos or model-name text")
    return ". ".join(lines)