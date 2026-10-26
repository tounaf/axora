import datetime
import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from axora.data.models import AdhesionAssociation, Association, Membre, Paroisse, ZoneGeographique
from axora.semantic.service import SemanticModelService

MODEL_MAP = {
    "Paroisse": Paroisse,
    "ZoneGeographique": ZoneGeographique,
    "Membre": Membre,
    "Association": Association,
    "AdhesionAssociation": AdhesionAssociation,
}


class BusinessRuleViolation(Exception):
    """Raised when a data mutation violates a domain business rule."""
    pass


class MutationEngine:
    """Engine responsible for validating business rules and executing create/update mutations."""

    def __init__(self, semantic_service: SemanticModelService) -> None:
        self._semantic_service = semantic_service

    async def create_record(
        self,
        session: AsyncSession,
        entity_name: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        canonical_entity = self._semantic_service.resolve_concept_name(entity_name)
        if not canonical_entity or canonical_entity not in MODEL_MAP:
            raise ValueError(f"Unknown or unsupported entity for creation: '{entity_name}'")

        model_cls = MODEL_MAP[canonical_entity]
        processed_payload = self._convert_types(payload)

        # Business Rule Validations for Member Creation
        if canonical_entity == "Membre":
            await self._validate_membre_rules(session, processed_payload)

        instance = model_cls(**processed_payload)
        session.add(instance)
        await session.flush()

        row_dict = {}
        for col in instance.__table__.columns:
            val = getattr(instance, col.name)
            row_dict[col.name] = str(val) if isinstance(val, (uuid.UUID, datetime.date)) else val

        return row_dict

    async def update_record(
        self,
        session: AsyncSession,
        entity_name: str,
        record_id: str | uuid.UUID,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        canonical_entity = self._semantic_service.resolve_concept_name(entity_name)
        if not canonical_entity or canonical_entity not in MODEL_MAP:
            raise ValueError(f"Unknown or unsupported entity for update: '{entity_name}'")

        model_cls = MODEL_MAP[canonical_entity]
        uid = uuid.UUID(str(record_id)) if isinstance(record_id, str) else record_id

        stmt = select(model_cls).where(model_cls.id == uid)
        result = await session.execute(stmt)
        instance = result.scalar_one_or_none()

        if not instance:
            raise ValueError(f"Record with ID '{record_id}' not found in entity '{canonical_entity}'")

        processed_payload = self._convert_types(payload)

        # Business Rule Validations for Member Update
        if canonical_entity == "Membre":
            merged_payload = {col.name: getattr(instance, col.name) for col in instance.__table__.columns}
            merged_payload.update(processed_payload)
            await self._validate_membre_rules(session, merged_payload)

        for key, value in processed_payload.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await session.flush()

        row_dict = {}
        for col in instance.__table__.columns:
            val = getattr(instance, col.name)
            row_dict[col.name] = str(val) if isinstance(val, (uuid.UUID, datetime.date)) else val

        return row_dict

    def _convert_types(self, payload: dict[str, Any]) -> dict[str, Any]:
        converted = dict(payload)
        # Parse UUID fields if passed as strings
        for key in ("paroisse_id", "zone_geographique_id", "membre_id", "association_id"):
            if key in converted and isinstance(converted[key], str):
                converted[key] = uuid.UUID(converted[key])

        # Parse Date fields if passed as ISO strings
        for key in ("date_naissance", "date_adhesion", "date_demande", "date_debut_passage", "date_fin_passage", "date_effet"):
            if key in converted and isinstance(converted[key], str):
                converted[key] = datetime.date.fromisoformat(converted[key])

        return converted

    async def _validate_membre_rules(self, session: AsyncSession, payload: dict[str, Any]) -> None:
        sexe = payload.get("sexe")
        if sexe and sexe not in ("HOMME", "FEMME"):
            raise BusinessRuleViolation(f"BR-001: Sexe invalide '{sexe}'. Valeurs acceptées: HOMME, FEMME.")

        statut = payload.get("statut_matrimonial")
        if statut and statut not in ("CELIBATAIRE", "MARIE"):
            raise BusinessRuleViolation(f"BR-002: Statut matrimonial invalide '{statut}'. Valeurs: CELIBATAIRE, MARIE.")

        # Ensure Zone belongs to Paroisse
        paroisse_id = payload.get("paroisse_id")
        zone_id = payload.get("zone_geographique_id")

        if paroisse_id and zone_id:
            p_uuid = uuid.UUID(str(paroisse_id)) if isinstance(paroisse_id, str) else paroisse_id
            z_uuid = uuid.UUID(str(zone_id)) if isinstance(zone_id, str) else zone_id

            stmt = select(ZoneGeographique).where(
                ZoneGeographique.id == z_uuid,
                ZoneGeographique.paroisse_id == p_uuid
            )
            res = await session.execute(stmt)
            if not res.scalar_one_or_none():
                raise BusinessRuleViolation(
                    f"BR-001: La zone géographique '{zone_id}' n'appartient pas à la paroisse '{paroisse_id}'."
                )
