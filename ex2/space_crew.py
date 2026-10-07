import sys

try:
    import pydantic
    from pydantic import BaseModel, Field, model_validator, ValidationError
    from datetime import datetime
    from enum import Enum
    from typing import List

    if int(pydantic.__version__.split(".")[0]) < 2:
        raise ImportError("Pydantic 2.x required")
except ImportError:
    print("Error: Pydantic 2.x is required.", file=sys.stderr)
    print('Install it with: pip install "pydantic>=2"', file=sys.stderr)
    sys.exit(1)


# VI.2 Requirements: Rank Enum
class Rank(str, Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


# Crew Member Model
class CrewMember(BaseModel):
    member_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=2, max_length=50)
    rank: Rank
    age: int = Field(..., ge=18, le=80)
    specialization: str = Field(..., min_length=3, max_length=30)
    years_experience: int = Field(..., ge=0, le=50)
    is_active: bool = Field(default=True)


# SpaceMission Model
class SpaceMission(BaseModel):
    mission_id: str = Field(..., min_length=5, max_length=15)
    mission_name: str = Field(..., min_length=3, max_length=100)
    destination: str = Field(..., min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(..., ge=1, le=3650)
    crew: List[CrewMember] = Field(..., min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(..., ge=1.0, le=10000.0)

    # Mission Validation Rules
    @model_validator(mode="after")
    def validate_mission_rules(self) -> "SpaceMission":
        # Rule 1: Mission ID must start with 'M'
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")

        # Rule 4: All crew members must be active
        for member in self.crew:
            if not member.is_active:
                raise ValueError(
                    f"Crew member {member.name} is not active. "
                    "All crew members must be active"
                )

        # Rule 2: Must have at least one Commander or Captain
        required_ranks = (Rank.COMMANDER, Rank.CAPTAIN)
        has_required_rank = any(
            m.rank in required_ranks for m in self.crew
        )
        if not has_required_rank:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )

        # Rule 3: Long missions (> 365 days)
        # need 50% experienced crew (5+ years)
        if self.duration_days > 365:
            experienced_count = sum(
                1 for member in self.crew if member.years_experience >= 5
            )
            if experienced_count < (len(self.crew) / 2):
                raise ValueError(
                    "Long missions (> 365 days) need at least 50% "
                    "experienced crew (5+ years). Current: "
                    f"{experienced_count}/{len(self.crew)}"
                )

        return self


# Demonstration Function
def main() -> None:
    print("Space Mission Crew Validation")
    print("=" * 30)

    # 1. Initialize valid crew members
    commander = CrewMember(
        member_id="CMD01",
        name="Sarah Connor",
        rank=Rank.COMMANDER,
        age=45,
        specialization="Mission Command",
        years_experience=15,
        is_active=True,
    )

    lieutenant = CrewMember(
        member_id="LT02",
        name="John Smith",
        rank=Rank.LIEUTENANT,
        age=32,
        specialization="Navigation",
        years_experience=6,
        is_active=True,
    )

    officer = CrewMember(
        member_id="OFF03",
        name="Alice Johnson",
        rank=Rank.OFFICER,
        age=28,
        specialization="Engineering",
        years_experience=3,
        is_active=True,
    )

    # 2. Successfully create a valid long-term mission
    try:
        valid_mission = SpaceMission(
            mission_id="M2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date=datetime(2024, 11, 20, 10, 0),
            duration_days=900,
            crew=[commander, lieutenant, officer],
            budget_millions=2500.0,
        )

        print("Valid mission created:")
        print(f"Mission: {valid_mission.mission_name}")
        print(f"ID: {valid_mission.mission_id}")
        print(f"Destination: {valid_mission.destination}")
        print(f"Duration: {valid_mission.duration_days} days")
        print(f"Budget: ${valid_mission.budget_millions}M")
        print(f"Crew size: {len(valid_mission.crew)}")
        print("Crew members:")
        for m in valid_mission.crew:
            info = f"  {m.name} ({m.rank.value}) {m.specialization}"
            print(info)

    except ValidationError as e:
        print(f"Unexpected validation error: {e}")

    print("\n" + "=" * 30 + "\n")

    # 3. Attempt to create invalid mission (No Commander or Captain present)
    print("Expected validation error:")
    try:
        SpaceMission(
            mission_id="M2024_FAIL",
            mission_name="Unsupervised Cadet Flight",
            destination="The Moon",
            launch_date=datetime(2024, 12, 1, 14, 0),
            duration_days=10,
            crew=[
                lieutenant,
                officer,
            ],  # Invalid: Missing Rank.COMMANDER or Rank.CAPTAIN
            budget_millions=50.0,
        )
    except ValidationError as e:
        for error in e.errors():
            print(f"ValidationError: {error['msg']}")


if __name__ == "__main__":
    main()
