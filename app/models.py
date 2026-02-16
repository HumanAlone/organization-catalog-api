from sqlalchemy import (
    DECIMAL,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Building(Base):
    __tablename__ = "building"
    id = Column(Integer, primary_key=True)
    address = Column(String(255), nullable=False)
    latitude = Column(DECIMAL(9, 6), nullable=False)
    longitude = Column(DECIMAL(9, 6), nullable=False)
    organizations = relationship("Organization", back_populates="building")

    __table_args__ = (
        CheckConstraint(
            "latitude >= -90 AND latitude <= 90", name="check_latitude_range"
        ),
        CheckConstraint(
            "longitude >= -180 AND longitude <= 180", name="check_longitude_range"
        ),
        Index("idx_building_coords", "latitude", "longitude"),
    )


class Organization(Base):
    __tablename__ = "organization"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    building_id = Column(
        Integer,
        ForeignKey("building.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    building = relationship("Building", back_populates="organizations")
    phones = relationship("Phone", back_populates="organization")
    businesses = relationship(
        "Business", secondary="organization_business", back_populates="organizations"
    )

    __table_args__ = (Index("idx_organization_name", "name"),)


class Phone(Base):
    __tablename__ = "phone"
    id = Column(Integer, primary_key=True)
    number = Column(String(25), nullable=False)
    organization_id = Column(
        Integer,
        ForeignKey("organization.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization = relationship("Organization", back_populates="phones")

    __table_args__ = (
        UniqueConstraint("number", "organization_id", name="uq_number_organization"),
    )


class Business(Base):
    __tablename__ = "business"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(
        Integer,
        ForeignKey("business.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    organizations = relationship(
        "Organization", secondary="organization_business", back_populates="businesses"
    )

    __table_args__ = (UniqueConstraint("name", "parent_id", name="uq_name_parent"),)


class OrganizationBusiness(Base):
    __tablename__ = "organization_business"
    organization_id = Column(
        Integer, ForeignKey("organization.id", ondelete="CASCADE"), primary_key=True
    )
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = (Index("idx_org_business_business", "business_id"),)
