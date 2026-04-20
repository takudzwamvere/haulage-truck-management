from ninja import Schema
from typing import Optional
from decimal import Decimal


class TruckIn(Schema):
    registration_no: str
    capacity: Decimal
    status: str = 'available'


class TruckOut(Schema):
    id: int
    registration_no: str
    capacity: Decimal
    status: str


class DriverIn(Schema):
    name: str
    license_no: str
    phone_no: str


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
    status: str

class ErrorOut(Schema):
    detail: str

class LoginIn(Schema):
    username: str
    password: str


class TokenOut(Schema):
    access_token: str
    token_type: str = 'bearer'