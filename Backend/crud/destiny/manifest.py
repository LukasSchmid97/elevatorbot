import dataclasses
from typing import TypeVar

from sqlalchemy import not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.crud import versions
from Backend.crud.base import CRUDBase
from Backend.database.base import Base
from Backend.database.models import DestinyRecordDefinition

ModelType = TypeVar("ModelType", bound=Base)


@dataclasses.dataclass
class Seal:
    reference_id: int
    title_name: str


class CRUDManifest(CRUDBase):
    @staticmethod
    async def get_version(db: AsyncSession):
        """Get the current version"""

        return await versions._get(db=db, name="Manifest")

    @staticmethod
    async def upsert_version(db: AsyncSession, version: str):
        """Upsert the current version"""

        return await versions.upsert(db=db, name="Manifest", version=version)

    async def delete_definition(self, db: AsyncSession, db_model: ModelType):
        """Delete all entries from the specified table"""

        # set table to the correct one
        self.model = db_model

        # delete table
        await self._delete_all(db=db)

    async def insert_definition(self, db: AsyncSession, db_model: ModelType, to_insert: list[ModelType]):
        """Insert the data into the table"""

        # set table to the correct one
        self.model = db_model

        # bulk insert
        await self._insert_multi(db=db, to_create=to_insert)

    async def get_seals(self, db: AsyncSession) -> list[Seal]:
        """Get all current seals"""

        # reference ids which should not _get returned here
        not_available = []

        query = (
            select(DestinyRecordDefinition)
            .filter(DestinyRecordDefinition.has_title)
            .filter(not_(DestinyRecordDefinition.has_title.in_(not_available)))
        )

        result = await self._execute_query(db=db, query=query)
        return [Seal(**row) for row in result.scalars().fetchall()]


destiny_manifest = CRUDManifest(Base)
