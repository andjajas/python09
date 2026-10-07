import sys

try:
    import pydantic
    from pydantic import BaseModel, Field, ValidationError
    from datetime import datetime
    from typing import Any, Optional

    if int(pydantic.__version__.split(".")[0]) < 2:
        raise ImportError("Pydantic 2.x required")
except ImportError:
    print("Error: Pydantic 2.x is required.", file=sys.stderr)
    print('Install it with: pip install "pydantic>=2"', file=sys.stderr)
    sys.exit(1)


# IV.2 Requirements: SpaceStation Model
class SpaceStation(BaseModel):
    station_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=1, max_length=50)
    crew_size: int = Field(..., ge=1, le=20)
    power_level: float = Field(..., ge=0.0, le=100.0)
    oxygen_level: float = Field(..., ge=0.0, le=100.0)
    last_maintenance: datetime
    is_operational: bool = Field(default=True)
    notes: Optional[str] = Field(default=None, max_length=200)


# Demonstration Function
def main() -> None:
    print("Space Stations Data Validation\n")
    print("==============================")
    # print("=" * 30)

    # 1. Create a valid space station instance
    try:
        extra_data: dict[str, Any] = {
                "last_maintenance": "2026-10-07T14:30:00"
            }
        valid_station = SpaceStation(
            station_id="ISS001",
            name="International Space Station",
            crew_size=6,
            power_level=85.5,
            oxygen_level=92.3,
            **extra_data,
            # last_maintenance="2026-10-07T14:30:00",
            # Automatic string to datetime conversion
            is_operational=True,
            notes="Routine checks completed successfully.",
        )
        print("Valid station created:")
        print(f"ID: {valid_station.station_id}")
        print(f"Name: {valid_station.name}")
        print(f"Crew: {valid_station.crew_size} people")
        print(f"Power: {valid_station.power_level}%")
        print(f"Oxygen: {valid_station.oxygen_level}%")
        print(f"Last Maintanance: {valid_station.last_maintenance}")
        if valid_station.is_operational:
            status = "Operational"
        else:
            status = "Non-Operational"
        print(f"Status: {status}")
        print(f"notes: {valid_station.notes}")

    except ValidationError as e:
        print(f"Unexpected error: {e}")

    print("\n==============================\n")
    # print("\n" + "=" * 30 + "\n")

    # 2. Attempt to create an invalid station (crew_size > 20)
    print("Expected validation error:")
    try:
        invalid_station = SpaceStation(
            station_id="Deathstar",
            name="Unfinished Station",
            crew_size=99,  # Invalid: Exceeds maximum allowance of 20
            power_level=99.9,
            oxygen_level=95.0,
            last_maintenance=datetime.now(),
            is_operational=True,
            notes="I am your father, Luke.",
        )
        print("Invalid station created:")
        print(f"ID: {invalid_station.station_id}")
        print(f"Name: {invalid_station.name}")
        print(f"Crew: {invalid_station.crew_size} people")
        print(f"Power: {invalid_station.power_level}%")
        print(f"Oxygen: {invalid_station.oxygen_level}%")
        print(f"Last Maintanance: {invalid_station.last_maintenance}")
        if invalid_station.is_operational:
            status = "Operational"
        else:
            status = "Non-Operational"
        print(f"Status: {status}")
        print(f"notes: {invalid_station.notes}")
    except ValidationError as e:
        for error in e.errors():
            print(f"ValidationError: {error['msg']}")
    print("\n==============================\n")


if __name__ == "__main__":
    main()
