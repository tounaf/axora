import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Paroisse(Base):
    __tablename__ = "paroisse"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)

    zones: Mapped[List["ZoneGeographique"]] = relationship("ZoneGeographique", back_populates="paroisse")
    membres: Mapped[List["Membre"]] = relationship("Membre", back_populates="paroisse")
    associations: Mapped[List["Association"]] = relationship("Association", back_populates="paroisse")


class ZoneGeographique(Base):
    __tablename__ = "zone_geographique"
    __table_args__ = (
        UniqueConstraint("paroisse_id", "nom", name="uq_zone_paroisse_nom"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paroisse_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("paroisse.id"), nullable=False)
    nom: Mapped[str] = mapped_column(String(150), nullable=False)

    paroisse: Mapped["Paroisse"] = relationship("Paroisse", back_populates="zones")
    membres: Mapped[List["Membre"]] = relationship("Membre", back_populates="zone")


class Membre(Base):
    __tablename__ = "membre"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paroisse_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("paroisse.id"), nullable=False)
    zone_geographique_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("zone_geographique.id"), nullable=False)

    nom: Mapped[str] = mapped_column(String(150), nullable=False)
    prenom: Mapped[str] = mapped_column(String(150), nullable=False)
    adresse: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sexe: Mapped[str] = mapped_column(String(30), nullable=False)
    date_naissance: Mapped[date] = mapped_column(Date, nullable=False)
    statut_matrimonial: Mapped[str] = mapped_column(String(30), nullable=False)

    paroisse: Mapped["Paroisse"] = relationship("Paroisse", back_populates="membres")
    zone: Mapped["ZoneGeographique"] = relationship("ZoneGeographique", back_populates="membres")
    adhesions: Mapped[List["AdhesionAssociation"]] = relationship("AdhesionAssociation", back_populates="membre")


class Association(Base):
    __tablename__ = "association"
    __table_args__ = (
        UniqueConstraint("paroisse_id", "code", name="uq_association_paroisse_code"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paroisse_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("paroisse.id"), nullable=False)
    nom: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)

    paroisse: Mapped["Paroisse"] = relationship("Paroisse", back_populates="associations")
    adhesions: Mapped[List["AdhesionAssociation"]] = relationship("AdhesionAssociation", back_populates="association")


class AdhesionAssociation(Base):
    __tablename__ = "adhesion_association"
    __table_args__ = (
        UniqueConstraint("membre_id", "association_id", name="uq_membre_association"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    membre_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("membre.id"), nullable=False)
    association_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("association.id"), nullable=False)
    date_adhesion: Mapped[date] = mapped_column(Date, nullable=False)

    membre: Mapped["Membre"] = relationship("Membre", back_populates="adhesions")
    association: Mapped["Association"] = relationship("Association", back_populates="adhesions")
