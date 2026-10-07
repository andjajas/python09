from pydantic import BaseModel


class SpaceStation(BaseModel):
	station_id: str
	name: str
	crew_size: int
	power_level: float
	oxygen_level: float
	last_maintenance:	# DateTime field
	is_operational: bool = True
	notes: str
