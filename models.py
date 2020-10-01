from dataclasses import dataclass
from datetime import date


@dataclass
class ItemInfo:
    item_id: int
    item_url: str
    item_type: str
    item_desc: str
    elvl: int
    item_icon: str = None
    item_name: str = None
    elvl_info: object = None
    item_sockets: int = 0
    mp_count: int = 0
    mp_price: int = 0
    # item_icon: str = None

@dataclass
class SimpleGearData:
    gear_type: str
    family_name: str
    datestamp: date
    awak_ap: int = None
    succ_ap: int = None
    dp: int = None
    gs: int = None


@dataclass
class GearData(SimpleGearData):
    user_id: int = None
    scrn_path: str = None
    server_id: int = None


@dataclass
class Result:
    status: bool
    message: str = None
    photos: [str] = None
    gear_data: GearData = None
    obj: object = None
    code: int = 0


@dataclass
class ServerInfo:
    server_id: int
    server_owner: int
    requests_name: int = 500
    general_channel_id: int = None
    gear_photo_id: int = None
    gear_talk_id: int = None


@dataclass
class ServerMessages:
    server_id: int
    message: str
