from dataclasses import dataclass
from datetime import date

@dataclass
class SimpleGearData:
    gear_type: str
    family_name: str
    datestamp: date
    awak_ap: int=None
    succ_ap: int=None
    dp: int=None
    gs: int=None

@dataclass
class GearData(SimpleGearData):
    user_id: int=None
    scrn_path: str=None
    server_id: int=None

@dataclass
class Result:
    status: bool
    message: str=None
    photos: [str]=None
    gear_data: GearData=None
    obj: object=None