import dataclasses
import logging
import os
from typing import Optional

import aiohttp
from orjson import orjson

from Backend.networking.base import NetworkBase
from Backend.networking.schemas import WebResponse


@dataclasses.dataclass
class ElevatorApi(NetworkBase):
    logger = logging.getLogger("elevatorApi")

    route = f"""{os.environ.get("ELEVATOR_HOST")}:{os.environ.get("ELEVATOR_PORT")}/"""

    bungie_request: bool = False

    async def post(
        self, route_addition: str, json: Optional[dict] = None, params: Optional[dict] = None
    ) -> WebResponse:
        """Post Request"""

        async with aiohttp.ClientSession(json_serialize=lambda x: orjson.dumps(x).decode()) as session:
            return await self._request(
                session=session,
                method="POST",
                route=self.route + route_addition,
                json=json,
                params=params,
            )

    async def get(self, route_addition: str, params: dict = None) -> WebResponse:
        """Get Request"""

        async with aiohttp.ClientSession() as session:
            return await self._request(
                session=session,
                method="GET",
                route=self.route + route_addition,
                params=params,
            )
