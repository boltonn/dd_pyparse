from datetime import datetime
from typing import Literal, Optional

from pydantic import ConfigDict, Field, confloat, field_validator

from dd_pyparse.schemas.base import Base
from dd_pyparse.schemas.enums import (AddressType, DataType, GeoContext,
                                      LocationSourceType)


class Location(Base):
    data_type: Literal["location"] = Field(DataType.location)
    address: Optional[str] = Field(None, description="Address of the location")
    address_type: Optional[AddressType] = Field(None, description="Type of address")
    altitude: Optional[float] = Field(None, example=100.0, description="Altitude of the location")
    bearing: Optional[confloat(ge=0, le=360)] = Field(None, example=100.0, description="Bearing of the location in degrees")
    country: Optional[str] = Field(None, description="Country of the location")
    country_code: Optional[str] = Field(None, description="Country code of the location")
    date_observed: Optional[datetime] = Field(None, description="Date of the location")
    description: Optional[str] = Field(None, description="Description of the location")
    geo_context: Optional[GeoContext] = Field(None, description="Geo context of the location")
    horizontal_accuracy: Optional[float] = Field(
        None, example=100.0, description="Horizontal accuracy of the location dedtermined by the OS"
    )
    latitude: Optional[float] = Field(None, example=100.0, description="Latitude of the location")
    locality: Optional[str] = Field(None, description="City or town of the location")
    longitude: Optional[float] = Field(None, example=100.0, description="Longitude of the location")
    name: Optional[str] = Field(None, description="Name of the location to be used for display purposes")
    postal_code: Optional[str] = Field(None, description="Postal code of the location")
    region: Optional[str] = Field(None, description="Region of the location")
    source: Optional[LocationSourceType] = Field(None, description="Source of the location")
    velocity: Optional[float] = Field(None, example=100.0, description="Velocity of the location")
    vertical_accuracy: Optional[float] = Field(None, example=100.0, description="Vertical accuracy of the location determined by the OS")
    model_config = ConfigDict(use_enum_values=True)

    @field_validator("bearing", mode="before")
    def normalize_bearing(cls, v):
        return v % 360 if v is not None else v
