"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
from uuid import UUID


# PostgreSQL Models
class CropYieldRecordCreate(BaseModel):
    """Model for creating a new crop yield record"""
    state_name: str = Field(..., description="Name of the state")
    crop_name: str = Field(..., description="Name of the crop")
    season_name: str = Field(..., description="Name of the season")
    crop_year: int = Field(..., ge=1990, le=2030, description="Year of the crop (1990-2030)")
    area: float = Field(..., ge=0, description="Area in hectares")
    production: float = Field(..., ge=0, description="Production in metric tons")
    annual_rainfall: float = Field(..., ge=0, description="Annual rainfall in mm")
    fertilizer: float = Field(..., ge=0, description="Fertilizer usage in kg")
    pesticide: float = Field(..., ge=0, description="Pesticide usage in kg")
    yield_value: float = Field(..., ge=0, description="Yield (Production/Area)", alias="yield")

    class Config:
        populate_by_name = True

    @model_validator(mode='after')
    def validate_yield(self):
        """Validate yield approximately equals production/area"""
        if self.area and self.area > 0:
            calculated_yield = self.production / self.area
            if abs(self.yield_value - calculated_yield) / calculated_yield > 0.05:
                pass
        return self


class CropYieldRecordUpdate(BaseModel):
    """Model for updating a crop yield record"""
    state_name: Optional[str] = None
    crop_name: Optional[str] = None
    season_name: Optional[str] = None
    crop_year: Optional[int] = Field(None, ge=1990, le=2030)
    area: Optional[float] = Field(None, ge=0)
    production: Optional[float] = Field(None, ge=0)
    annual_rainfall: Optional[float] = Field(None, ge=0)
    fertilizer: Optional[float] = Field(None, ge=0)
    pesticide: Optional[float] = Field(None, ge=0)
    yield_value: Optional[float] = Field(None, ge=0, alias="yield")

    class Config:
        populate_by_name = True
        extra = "ignore"  

class CropYieldRecordResponse(BaseModel):
    """Response model for crop yield record"""
    record_id: UUID
    state_name: str
    crop_name: str
    season_name: str
    crop_year: int
    area: float
    production: float
    annual_rainfall: float
    fertilizer: float
    pesticide: float
    yield_value: float
    created_at: datetime

    class Config:
        from_attributes = True


# MongoDB Models
class MongoCropYieldRecordCreate(BaseModel):
    """Model for creating a MongoDB crop yield record"""
    state_name: str = Field(..., description="Name of the state")
    crop_name: str = Field(..., description="Name of the crop")
    season_name: str = Field(..., description="Name of the season")
    year: int = Field(..., ge=1990, le=2030, description="Year of the crop")
    area: Optional[float] = Field(None, ge=0, description="Area in hectares")
    production: Optional[float] = Field(None, ge=0, description="Production in metric tons")
    annual_rainfall: Optional[float] = Field(None, ge=0, description="Annual rainfall in mm")
    fertilizer: Optional[float] = Field(None, ge=0, description="Fertilizer usage in kg")
    pesticide: Optional[float] = Field(None, ge=0, description="Pesticide usage in kg")
    yield_value: Optional[float] = Field(None, ge=0, description="Yield", alias="yield")

    class Config:
        populate_by_name = True


class MongoCropYieldRecordUpdate(BaseModel):
    """Model for updating a MongoDB crop yield record"""
    state_name: Optional[str] = None
    crop_name: Optional[str] = None
    season_name: Optional[str] = None
    year: Optional[int] = Field(None, ge=1990, le=2030)
    area: Optional[float] = Field(None, ge=0)
    production: Optional[float] = Field(None, ge=0)
    annual_rainfall: Optional[float] = Field(None, ge=0)
    fertilizer: Optional[float] = Field(None, ge=0)
    pesticide: Optional[float] = Field(None, ge=0)
    yield_value: Optional[float] = Field(None, ge=0, alias="yield")

    class Config:
        populate_by_name = True


class MongoCropYieldRecordResponse(BaseModel):
    """Response model for MongoDB crop yield record"""
    id: str
    state_id: str
    crop_id: str
    season_id: str
    year: int
    area: Optional[float]
    production: Optional[float]
    annual_rainfall: Optional[float]
    fertilizer: Optional[float]
    pesticide: Optional[float]
    yield_value: Optional[float]

    class Config:
        from_attributes = True
