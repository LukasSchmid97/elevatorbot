import asyncio
import logging
import random
from typing import Optional
from urllib.parse import urlencode

import aiohttp
import aiohttp_client_cache
from orjson import orjson

from Backend.core.errors import CustomException
from Backend.networking.bungieRatelimiting import BungieRateLimiter
from Backend.networking.schemas import InternalWebResponse, WebResponse

# the limiter object which to not get rate-limited by bungie. One obj for ever instance!
bungie_limiter = BungieRateLimiter()


class NetworkBase:
    bungie_request = True

    # get logger
    logger = logging.getLogger("bungieApi")

    # get limiter
    limiter = bungie_limiter

    # how many times to retry a request
    max_web_request_tries = 10

    async def _request(
        self,
        session: aiohttp_client_cache.CachedSession | aiohttp.ClientSession,
        method: str,
        route: str,
        headers: dict = None,
        params: dict = None,
        json: dict = None,
        form_data: dict = None,
    ) -> WebResponse:
        """Make a request to the url with the method and handles the result"""

        assert not (form_data and json), "Only json or form_data can be used"

        allow_redirects = False if self.bungie_request and method == "POST" else True

        # wait for a token from the rate limiter
        if self.bungie_request:
            async with asyncio.Lock():
                await bungie_limiter.wait_for_token()

        # abort after max_web_request_tries tries
        for _ in range(self.max_web_request_tries):
            try:
                async with session.request(
                    method=method,
                    url=route,
                    headers=headers,
                    params=params,
                    json=json,
                    data=form_data,
                    allow_redirects=allow_redirects,
                ) as request:
                    response = await self.__handle_request_data(
                        request=request,
                        params=params,
                        route=route,
                    )

                    # try again
                    if response is None:
                        continue

                    # return response
                    else:
                        return WebResponse.from_dict(response.__dict__)

            except (asyncio.exceptions.TimeoutError, ConnectionResetError):
                self.logger.error("Timeout error for '%s'", f"{route}?{urlencode({} if params is None else params)}")
                await asyncio.sleep(random.randrange(2, 6))
                continue

        # return that it failed
        self.logger.error(
            "Request failed '%s' times, aborting for '%s'",
            self.max_web_request_tries,
            route,
        )
        raise CustomException("UnknownError")

    async def __handle_request_data(
        self,
        request: aiohttp.ClientResponse | aiohttp_client_cache.CachedResponse,
        route: str,
        params: Optional[dict],
    ) -> Optional[InternalWebResponse]:
        """Handle the request results"""

        if not params:
            params = {}
        route_with_params = f"{route}?{urlencode(params)}"

        # catch the content type "application/octet-stream" which is returned for some routes
        if "application/octet-stream" in request.headers["Content-Type"]:
            pass

        # make sure the return is a json, sometimes we get a http file for some reason
        elif "application/json" not in request.headers["Content-Type"]:
            self.logger.error(
                "'%s': Wrong content type '%s' with reason '%s' for '%s'",
                request.status,
                request.headers["Content-Type"],
                request.reason,
                route_with_params,
            )
            if request.status == 200:
                self.logger.error("Wrong content type returned text: '%s'", await request.text())
            await asyncio.sleep(3)
            return

        # get the response as a json
        try:
            response = InternalWebResponse(
                content=await request.json(loads=orjson.loads),
                status=request.status,
            )

            # set the error vars
            response.error = None
            if "ErrorStatus" in response.content:
                response.error = response.content["ErrorStatus"]
            elif "error_description" in response.content:
                response.error = response.content["error_description"]
            response.error_code = response.content["ErrorCode"] if "ErrorCode" in response.content else None
            response.error_message = response.content["Message"] if "Message" in response.content else None

            # set if the response was cached
            try:
                response.from_cache = request.from_cache
            except AttributeError:
                response.from_cache = False

        except aiohttp.ClientPayloadError:
            self.logger.error("'%s': Payload error, retrying for '%s'", request.status, route_with_params)
            return
        except aiohttp.ContentTypeError:
            response = InternalWebResponse(
                status=request.status,
            )

        # if response is ok return it
        if response.status == 200:
            response.success = True

            # remove the leading "Response" from the request (if exists)
            if "Response" in response.content:
                response.content = response.content["Response"]

            return response

        # handling any errors if not ok
        await self.__handle_bungie_errors(
            route=route,
            params=params,
            response=response,
        )

    async def __handle_bungie_errors(self, route: str, params: dict, response: InternalWebResponse):
        """Looks for typical bungie errors and handles / logs them"""

        route_with_params = f"{route}?{urlencode(params)}"

        match (response.status, response.error):
            case (401, _) | (_, "invalid_grant" | "AuthorizationCodeInvalid"):
                # unauthorized
                self.logger.error(
                    "'%s - %s': Unauthorized request for '%s' - '%s'",
                    response.status,
                    response.error,
                    route_with_params,
                    response,
                )
                raise CustomException("BungieUnauthorized")

            case (404, error):
                # not found
                self.logger.error(
                    "'%s - %s': No stats found for '%s' - '%s'",
                    response.status,
                    error,
                    route_with_params,
                    response,
                )
                raise CustomException("BungieBadRequest")

            case (429, error):
                # rate limited
                self.logger.warning(
                    "'%s - %s': Getting rate limited for '%s' - '%s'",
                    response.status,
                    error,
                    route_with_params,
                    response,
                )
                await asyncio.sleep(2)

            case (400, error):
                # generic bad request, such as wrong format
                self.logger.error(
                    "'%s - %s': Generic bad request for '%s' - '%s'",
                    response.status,
                    error,
                    route_with_params,
                    response,
                )
                raise CustomException("BungieDed")

            case (503, error):
                # bungie is ded
                self.logger.error(
                    "'%s - %s': Server is overloaded for '%s' - '%s'",
                    response.status,
                    error,
                    route_with_params,
                    response,
                )
                await asyncio.sleep(10)

            case (status, "PerEndpointRequestThrottleExceeded" | "DestinyDirectBabelClientTimeout"):
                # we we are getting throttled
                self.logger.warning(
                    "'%s - %s': Getting throttled for '%s' - '%s'",
                    status,
                    response.error,
                    route_with_params,
                    response,
                )

                throttle_seconds = response.content["ErrorStatus"]["ThrottleSeconds"]

                await asyncio.sleep(throttle_seconds + random.randrange(1, 3))

            case (status, "GroupMembershipNotFound"):
                # if user doesn't have that item
                self.logger.error(
                    "'%s - %s': User is not in clan '%s' - '%s'",
                    status,
                    response.error,
                    route_with_params,
                    response,
                )
                raise CustomException("BungieGroupMembershipNotFound")

            case (status, "DestinyItemNotFound"):
                # if user doesn't have that item
                self.logger.error(
                    "'%s - %s': User doesn't have that item for '%s' - '%s'",
                    status,
                    response.error,
                    route_with_params,
                    response,
                )
                raise CustomException("BungieDestinyItemNotFound")

            case (status, "DestinyPrivacyRestriction"):
                # private profile
                self.logger.error(
                    "'%s - %s': User has private Profile for '%s' - '%s'",
                    status,
                    response.error,
                    route_with_params,
                    response,
                )
                raise CustomException("BungieDestinyPrivacyRestriction")

            case (status, "DestinyDirectBabelClientTimeout"):
                # timeout
                self.logger.warning(
                    "'%s - %s': Getting timeouts for '%s' - '%s'",
                    status,
                    response.error,
                    route_with_params,
                    response,
                )
                await asyncio.sleep(60)

            case (status, "ClanTargetDisallowsInvites"):
                # user has disallowed clan invites
                self.logger.error(
                    "'%s - %s': User disallows clan invites '%s' - '%s'",
                    status,
                    response.error,
                    route_with_params,
                    response,
                )
                raise CustomException("BungieClanTargetDisallowsInvites")

            case (status, "AuthorizationRecordRevoked"):
                # users tokens are no longer valid
                self.logger.error(
                    "'%s - %s': User refresh token is outdated and they need to re-registration for '%s' - '%s'",
                    status,
                    response,
                    route_with_params,
                    response.error_message,
                )
                raise CustomException("NoToken")

            case (status, error):
                # catch the rest
                self.logger.error(
                    "'%s - %s': Request failed for '%s' - '%s'",
                    status,
                    error,
                    route_with_params,
                    response,
                )
                await asyncio.sleep(2)

        return False
