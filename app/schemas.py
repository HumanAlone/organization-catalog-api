from pydantic import BaseModel, ConfigDict


class BuildingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    address: str
    latitude: float
    longitude: float


class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None = None


class PhoneResponse(BaseModel):
    number: str

    class Config:
        from_attributes = True


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phones: list[PhoneResponse]
    businesses: list[BusinessResponse]
    building: BuildingResponse
