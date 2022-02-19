from Backend.backgroundEvents.base import BaseEvent
from Backend.core.destiny.manifest import DestinyManifest
from Backend.database.base import get_async_sessionmaker


class ManifestUpdater(BaseEvent):
    """Check for Manifest Update hourly"""

    def __init__(self):
        interval_minutes = 60
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self):
        async with get_async_sessionmaker().begin() as db:
            manifest = DestinyManifest(db=db)

            # update
            await manifest.update()
