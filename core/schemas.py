from ninja import Schema
from typing import Optional, Literal
from decimal import Decimal


class TruckIn(Schema):
    registration_no: str
    capacity: Decimal
    status: Literal['available', 'in_transit', 'maintenance'] = 'available'


class TruckPatch(Schema):
    registration_no: Optional[str] = None
    capacity: Optional[Decimal] = None
    status: Optional[Literal['available', 'in_transit', 'maintenance']] = None


class TruckOut(Schema):
    id: int
    registration_no: str
    capacity: Decimal
    status: str


class DriverIn(Schema):
    name: str
    license_no: str
    phone_no: str


class DriverPatch(Schema):
    name: Optional[str] = None
    license_no: Optional[str] = None
    phone_no: Optional[str] = None


class DriverOut(Schema):
    id: int
    name: str
    license_no: str
    phone_no: str


class JobIn(Schema):
    pick_up_location: str
    delivery_location: str
    cargo: str


class JobOut(Schema):
    id: int
    pick_up_location: str
    delivery_location: str
    cargo: str
    status: str
    assigned_truck: Optional[TruckOut] = None
    assigned_driver: Optional[DriverOut] = None


class AssignJob(Schema):
    truck_id: int
    driver_id: int


class UpdateStatus(Schema):
    status: Literal['pending', 'in_transit', 'completed', 'cancelled']

class ErrorOut(Schema):
    detail: str

class LoginIn(Schema):
    username: str
    password: str


class TokenOut(Schema):
    access_token: str
    token_type: str = 'bearer'