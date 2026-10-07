import sys

try:
    import pydantic
    from pydantic import BaseModel, Field, model_validator, ValidationError
    from datetime import datetime
    from enum import Enum
    from typing import Optional

    if int(pydantic.__version__.split(".")[0]) < 2:
        raise ImportError("Pydantic 2.x required")
except ImportError:
    print("Error: Pydantic 2.x is required.", file=sys.stderr)
    print('Install it with: pip install "pydantic>=2"', file=sys.stderr)
    sys.exit(1)


# V.2 Requirements: ContactType Enum
class ContactType(str, Enum):
    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


# AlienContact Model
class AlienContact(BaseModel):
    contact_id: str = Field(..., min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(..., min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(..., ge=0.0, le=10.0)
    duration_minutes: int = Field(..., ge=1, le=1440)
    witness_count: int = Field(..., ge=1, le=100)
    message_received: Optional[str] = Field(default=None, max_length=500)
    is_verified: bool = Field(default=False)

    # Custom Validation Rules
    @model_validator(mode="after")
    def validate_contact_rules(self) -> "AlienContact":
        # Rule 1: Contact ID must start with "AC"
        if not self.contact_id.startswith("AC"):
            raise ValueError("Contact ID must start with 'AC'")

        # Rule 2: Physical contact reports must be verified
        if self.contact_type == ContactType.PHYSICAL and not self.is_verified:
            raise ValueError("Physical contact reports must be verified")

        # Rule 3: Telepathic contact requires at least 3 witnesses
        is_telepathic = self.contact_type == ContactType.TELEPATHIC
        if is_telepathic and self.witness_count < 3:
            msg = "Telepathic contact requires at least 3 witnesses"
            raise ValueError(msg)

        # Rule 4: Strong signals (>7.0) should include received messages
        if self.signal_strength > 7.0 and not self.message_received:
            msg = "Strong signals (>7.0) should include received messages"
            raise ValueError(msg)

        return self


# Demonstration Function
def main() -> None:
    print("Alien Contact Log Validation")
    print("=" * 30)

    # 1. Create a valid contact report instance
    try:
        valid_contact = AlienContact(
            contact_id="AC_2024_001",
            timestamp=datetime.now(),
            location="Area 51, Nevada",
            contact_type=ContactType.RADIO,
            signal_strength=8.5,
            duration_minutes=45,
            witness_count=5,
            message_received="Greetings from Zeta Reticuli",
            is_verified=False,
        )
        print("Valid contact report:")
        print(f"ID: {valid_contact.contact_id}")
        print(f"Type: {valid_contact.contact_type.value}")
        print(f"Location: {valid_contact.location}")
        print(f"Signal: {valid_contact.signal_strength}/10")
        print(f"Duration: {valid_contact.duration_minutes} minutes")
        print(f"Witnesses: {valid_contact.witness_count}")
        print(f"Message: '{valid_contact.message_received}'")
    except ValidationError as e:
        print(f"Unexpected error: {e}")

    print("\n" + "=" * 30 + "\n")

    # 2. Attempt to create an invalid contact report
    # (Telepathic with < 3 witnesses)
    print("Expected validation error:")
    try:
        AlienContact(
            contact_id="AC_TELE_FAIL",
            timestamp=datetime.now(),
            location="Roswell, New Mexico",
            contact_type=ContactType.TELEPATHIC,
            signal_strength=4.0,
            duration_minutes=10,
            witness_count=1,
            # Invalid: Telepathic contacts require >= 3 witnesses
            is_verified=True,
        )
    except ValidationError as e:
        for error in e.errors():
            print(f"ValidationError: {error['msg']}")


if __name__ == "__main__":
    main()
