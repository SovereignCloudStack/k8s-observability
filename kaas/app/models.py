import enum

from .database import Base
from sqlalchemy import TIMESTAMP, Column, String, Integer, Enum
from sqlalchemy.sql import func
from pydantic import BaseModel
from datetime import datetime


class ClusterStatus(enum.Enum):
    provisioning = "provisioning"
    created = "created"
    failed = "failed"


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    status = Column(Enum(ClusterStatus), nullable=False)
    created = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )


class OKSchema(BaseModel):
    status: str = "OK"


class ClusterSchemaCreate(BaseModel):
    name: str = "kaas"


class ClusterSchema(BaseModel):
    id: int
    name: str
    status: ClusterStatus
    created: datetime | None = None

    class Config:
        from_attributes = True
