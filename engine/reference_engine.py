from .types import ReferenceProfile, ReferencePerson, ReferenceVehicle, ReferenceEnvironment, ScaleGraph


def create_reference_profile(
    vehicle_model: str = "",
    vehicle_colour: str = "",
    vehicle_trim: str = "",
    person_hair: str = "",
    person_skin_tone: str = "",
    person_clothing: str = "",
    showroom_type: str = "modern_dealership",
    with_scale_graph: bool = True,
) -> ReferenceProfile:
    person = None
    if any([person_hair, person_skin_tone, person_clothing]):
        person = ReferencePerson(
            hair=person_hair,
            skin_tone=person_skin_tone,
            clothing=person_clothing,
        )

    vehicle = None
    if vehicle_model:
        vehicle = ReferenceVehicle(
            model=vehicle_model,
            colour=vehicle_colour,
            trim=vehicle_trim,
        )

    environment = ReferenceEnvironment(
        location_type=showroom_type,
    ) if showroom_type else None

    return ReferenceProfile(
        person=person,
        vehicle=vehicle,
        environment=environment,
        scale=ScaleGraph() if with_scale_graph else None,
    )


IMMUTABLE_VEHICLE_ATTRS = ("model", "body_type", "generation", "geometry", "colour", "trim", "badging")
MUTABLE_VEHICLE_ATTRS = ("position", "orientation")


def vehicle_identity(profile: ReferenceProfile) -> dict:
    """Immutable identity of the vehicle — must survive generation."""
    if not profile or not profile.vehicle:
        return {}
    v = profile.vehicle
    return {k: val for k, val in v.identity_terms.items() if val}


def assert_vehicle_identity_untouched(profile: ReferenceProfile, scene_colour: str = "", scene_model: str = "") -> list:
    """Cross-check that immutable identity survives into the scene plan."""
    issues = []
    identity = vehicle_identity(profile)
    if identity.get("model") and scene_model and identity["model"].lower() != scene_model.lower():
        issues.append(f"Vehicle model identity broken: {identity['model']} != {scene_model}")
    if identity.get("colour") and scene_colour and identity["colour"].lower() != scene_colour.lower():
        issues.append(f"Vehicle colour identity broken: {identity['colour']} != {scene_colour}")
    return issues


def reference_to_prompt_text(profile: ReferenceProfile) -> str:
    """Convert reference profile to a description for the Veo prompt."""
    return profile.describe_for_prompt()


def reference_to_ingredients_block(profile: ReferenceProfile) -> str:
    """Generate instructions for Veo 3.1 Ingredients-to-Video feature."""
    parts = []
    if profile.vehicle:
        parts.append(
            f"Vehicle reference: {profile.vehicle.colour} {profile.vehicle.model}"
        )
    if profile.person:
        parts.append(
            f"Person reference: {profile.person.hair} hair, "
            f"{profile.person.skin_tone} skin, {profile.person.clothing}"
        )
    if profile.environment:
        parts.append(
            f"Environment reference: {profile.environment.location_type}, "
            f"{profile.environment.lighting} lighting"
        )
    if profile.scale:
        s = profile.scale
        parts.append(
            f"Scale: {s.constraint} (presenter {s.presenter_to_vehicle_m}m, "
            f"{s.lens_focal_mm}mm lens)"
        )
    if not parts:
        return ""
    return "Reference images: " + "; ".join(parts) + "."