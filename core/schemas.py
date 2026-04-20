from ninja import Schema
from typing import Literal, Annotated
from decimal import Decimal
from pydantic import Field


class TruckIn(Schema):
    registration_no: str
    capacity: Decimal
    status: Literal['available', 'in_transit', 'maintenance'] = 'available'


class TruckPatch(Schema):
    registration_no: str | None = None
    capacity: Decimal | None = None
    status: Literal['available', 'in_transit', 'maintenance'] | None = None


class TruckOut(Schema):
    id: int
    registration_no: str
    capacity: Decimal
    status: str


class DriverIn(Schema):
    name: str
    license_no: Annotated[str, Field(pattern=r'^[A-Za-z0-9\s\-]+$')]
    phone_no: Annotated[str, Field(pattern=r'^\+?[0-9\s\-]+$')]


class DriverPatch(Schema):
    name: str | None = None
    license_no: Annotated[str, Field(pattern=r'^[A-Za-z0-9\s\-]+$')] | None = None
    phone_no: Annotated[str, Field(pattern=r'^\+?[0-9\s\-]+$')] | None = None


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
    assigned_truck: TruckOut | None = None
    assigned_driver: DriverOut | None = None


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