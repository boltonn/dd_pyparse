from typing import Any, Optional

from pydantic import BaseModel, Field


class Annotation(BaseModel):
    """Generic annotation object"""

    model_name: Optional[str] = Field(None, description="Name of the model that created the annotation")
    model_version: Optional[str] = Field(None, description="Version of the model that created the annotation")


class Classification(Annotation):
    label: str = Field(..., description="Label of the classification")
    confidence: Optional[float] = Field(None, description="Confidence of the classification")
    display_name: Optional[str] = Field(None, description="Display name of the classification")
    attributes: Optional[dict[str, Any]] = Field(None, description="Attributes of the classification")


class Detection(Classification):
    bbox: list[float] = Field(..., description="Bounding box of the detection")
    landmarks: Optional[list[float]] = Field(None, description="Landmarks of the detection")
