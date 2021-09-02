from Backend.core.destiny.manifest import DestinyManifest
from Backend.database.base import get_async_session
from Backend.backgroundEvents import BaseEvent


class UpdateManifest(BaseEvent):
    """Check for Manifest Update hourly"""

    def __init__(self):
        interval_minutes = 60
        super().__init__(scheduler_type="interval", interval_minutes=interval_minutes)

    async def run(self):
        async with get_async_session().begin() as db:
            manifest = DestinyManifest(db=db)

            # update
            await manifest.update()
