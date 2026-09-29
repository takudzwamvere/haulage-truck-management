from ninja import Schema
from typing import Literal, Annotated
from datetime import datetime
from decimal import Decimal
from pydantic import Field


class TruckIn(Schema):
    """Payload schema for creating a new haulage truck."""
    registration_no: str
    capacity: Decimal
    status: Literal['available', 'in_transit', 'maintenance'] = 'available'


class TruckPatch(Schema):
    """Payload schema for partially updating an existing truck."""
    registration_no: str | None = None
    capacity: Decimal | None = None
    status: Literal['available', 'in_transit', 'maintenance'] | None = None


class TruckOut(Schema):
    """Response schema representing a haulage truck."""
    id: int
    registration_no: str
    capacity: Decimal
    status: str


class DriverIn(Schema):
    """Payload schema for registering a new driver."""
    name: str
    license_no: Annotated[str, Field(pattern=r'^[A-Za-z0-9\s\-]+$')]
    phone_no: Annotated[str, Field(pattern=r'^\+?[0-9\s\-]+$')]


class DriverPatch(Schema):
    """Payload schema for partially updating driver information."""
    name: str | None = None
    license_no: Annotated[str, Field(pattern=r'^[A-Za-z0-9\s\-]+$')] | None = None
    phone_no: Annotated[str, Field(pattern=r'^\+?[0-9\s\-]+$')] | None = None


class DriverOut(Schema):
    """Response schema representing a driver."""
    id: int
    name: str
    license_no: str
    phone_no: str


class JobIn(Schema):
    """Payload schema for creating a new delivery job."""
    pick_up_location: str
    delivery_location: str
    cargo: str


class JobOut(Schema):
    """Response schema representing a delivery job and its assigned resources."""
    id: int
    pick_up_location: str
    delivery_location: str
    cargo: str
    status: str
    assigned_truck: TruckOut | None = None
    assigned_driver: DriverOut | None = None
    created_at: datetime
    modified_at: datetime


class AssignJob(Schema):
    """Payload schema for assigning a truck and driver to a pending job."""
    truck_id: int
    driver_id: int


class UpdateStatus(Schema):
    """Payload schema for advancing or terminating a job status."""
    status: Literal['pending', 'in_transit', 'completed', 'cancelled']


class ErrorOut(Schema):
    """Standardized error detail response schema."""
    detail: str


class LoginIn(Schema):
    """Payload schema for API token login request."""
    username: str
    password: str


class TokenOut(Schema):
    """Response schema returning a JWT access token."""
    access_token: str
    token_type: str = 'bearer'