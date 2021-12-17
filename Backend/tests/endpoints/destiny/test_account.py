import datetime

import pytest as pytest
from dummyData.insert import mock_request
from httpx import AsyncClient
from orjson import orjson
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession
from static import (
    dummy_activity_name,
    dummy_activity_reference_id,
    dummy_bungie_name,
    dummy_character_id,
    dummy_consumable_id,
    dummy_destiny_id,
    dummy_discord_guild_id,
    dummy_discord_id,
    dummy_gotten_collectible_id,
    dummy_gotten_record_id,
    dummy_metric_id,
    dummy_metric_value,
    dummy_not_gotten_collectible_id,
    dummy_not_gotten_record_id,
)

from Backend.misc.cache import cache
from NetworkingSchemas.basic import BoolModel, NameModel, ValueModel
from NetworkingSchemas.destiny.account import (
    BoolModelRecord,
    DestinyCharactersModel,
    DestinyLowMansModel,
    DestinyStatInputModel,
    DestinyTimeInputModel,
    DestinyTimesModel,
    DestinyTriumphScoreModel,
    SeasonalChallengesModel,
)


@pytest.mark.asyncio
async def test_destiny_name(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/name/")
    assert r.status_code == 200
    data = NameModel.parse_obj(r.json())
    assert data.name == dummy_bungie_name

    r = await client.get(f"/destiny/0/0/account/name")
    assert r.status_code == 409
    assert r.json() == {"error": "DiscordIdNotFound"}


@pytest.mark.asyncio
async def test_has_collectible(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/collectible/{dummy_gotten_collectible_id}"
    )
    assert r.status_code == 200
    data = BoolModel.parse_obj(r.json())
    assert data.bool is True
    assert dummy_gotten_collectible_id in cache.collectibles[dummy_destiny_id]

    r = await client.get(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/collectible/{dummy_not_gotten_collectible_id}"
    )
    assert r.status_code == 200
    data = BoolModel.parse_obj(r.json())
    assert data.bool is False
    assert dummy_not_gotten_collectible_id not in cache.collectibles[dummy_destiny_id]


@pytest.mark.asyncio
async def test_has_triumph(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/triumph/{dummy_gotten_record_id}"
    )
    assert r.status_code == 200
    data = BoolModelRecord.parse_obj(r.json())
    assert data.bool is True
    assert data.objectives == []
    assert dummy_gotten_record_id in cache.triumphs[dummy_destiny_id]

    r = await client.get(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/triumph/{dummy_not_gotten_record_id}"
    )
    assert r.status_code == 200
    data = BoolModelRecord.parse_obj(r.json())
    assert data.bool is False
    assert data.objectives[0].bool is True
    assert data.objectives[1].bool is False
    assert dummy_not_gotten_record_id not in cache.triumphs[dummy_destiny_id]


@pytest.mark.asyncio
async def test_metric(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/metric/{dummy_metric_id}")
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == dummy_metric_value


@pytest.mark.asyncio
async def test_destiny_solos(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/solos")
    assert r.status_code == 200
    data = DestinyLowMansModel.parse_obj(r.json())
    assert data.solos
    assert data.solos[0].activity_name == dummy_activity_name
    assert data.solos[0].activity_ids == [1337]
    assert data.solos[0].count == 1
    assert data.solos[0].flawless_count == 0
    assert data.solos[0].not_flawless_count == 1
    assert data.solos[0].fastest.seconds == 557


@pytest.mark.asyncio
async def test_characters(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/characters")
    assert r.status_code == 200
    data = DestinyCharactersModel.parse_obj(r.json())
    assert data.characters
    assert data.characters[0].character_id == dummy_character_id


@pytest.mark.asyncio
async def test_stat(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    input_model = DestinyStatInputModel(stat_name="kills", stat_category="allPvE")
    r = await client.post(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/stat", json=input_model.dict())
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 1041425

    input_model = DestinyStatInputModel(stat_name="kills", stat_category="allTime")
    r = await client.post(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/stat", json=input_model.dict())
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 1088957


@pytest.mark.asyncio
async def test_stat_characters(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    input_model = DestinyStatInputModel(stat_name="kills", stat_category="allPvE")
    r = await client.post(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/stat/character/{dummy_character_id}",
        json=input_model.dict(),
    )
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 525128

    input_model = DestinyStatInputModel(stat_name="kills", stat_category="allTime")
    r = await client.post(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/stat/character/{dummy_character_id}",
        json=input_model.dict(),
    )
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 540326

    input_model = DestinyStatInputModel(stat_name="kills", stat_category="allTime")
    r = await client.post(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/stat/character/1", json=input_model.dict()
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_time(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    input_model = DestinyTimeInputModel(
        start_time=datetime.datetime(year=2021, month=12, day=1, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(year=2021, month=12, day=31, tzinfo=datetime.timezone.utc),
        modes=[4],
        activity_ids=None,
        character_class=None,
    )
    r = await client.post(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/time", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTimesModel.parse_obj(r.json())
    assert data.entries
    assert len(data.entries) == 1
    assert data.entries[0].time_played == 557
    assert data.entries[0].mode == 4
    assert data.entries[0].activity_ids is None

    input_model = DestinyTimeInputModel(
        start_time=datetime.datetime(year=2021, month=12, day=30, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(year=2021, month=12, day=31, tzinfo=datetime.timezone.utc),
        modes=[4],
        activity_ids=None,
        character_class=None,
    )
    r = await client.post(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/time", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTimesModel.parse_obj(r.json())
    assert data.entries
    assert data.entries[0].time_played == 0

    input_model = DestinyTimeInputModel(
        start_time=datetime.datetime(year=2021, month=12, day=1, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(year=2021, month=12, day=31, tzinfo=datetime.timezone.utc),
        modes=[4],
        activity_ids=None,
        character_class="Hunter",
    )
    r = await client.post(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/time", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTimesModel.parse_obj(r.json())
    assert data.entries
    assert data.entries[0].time_played != 0

    input_model = DestinyTimeInputModel(
        start_time=datetime.datetime(year=2021, month=12, day=1, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(year=2021, month=12, day=31, tzinfo=datetime.timezone.utc),
        modes=[4],
        activity_ids=None,
        character_class="Warlock",
    )
    r = await client.post(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/time", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTimesModel.parse_obj(r.json())
    assert data.entries
    assert data.entries[0].time_played == 0

    input_model = DestinyTimeInputModel(
        start_time=datetime.datetime(year=2021, month=12, day=1, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(year=2021, month=12, day=31, tzinfo=datetime.timezone.utc),
        modes=[4],
        activity_ids=[768123],
        character_class=None,
    )
    r = await client.post(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/time", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTimesModel.parse_obj(r.json())
    assert data.entries
    assert data.entries[1].time_played == 0

    input_model = DestinyTimeInputModel(
        start_time=datetime.datetime(year=2021, month=12, day=1, tzinfo=datetime.timezone.utc),
        end_time=datetime.datetime(year=2021, month=12, day=31, tzinfo=datetime.timezone.utc),
        modes=[14896844],
        activity_ids=[dummy_activity_reference_id],
        character_class=None,
    )
    r = await client.post(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/time", json=orjson.loads(input_model.json())
    )
    assert r.status_code == 200
    data = DestinyTimesModel.parse_obj(r.json())
    assert data.entries
    assert data.entries[1].time_played != 0


@pytest.mark.asyncio
async def test_seasonal_challenges(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/seasonal_challenges")
    assert r.status_code == 200
    data = SeasonalChallengesModel.parse_obj(r.json())
    assert data.topics
    assert data.topics[0].name == "Seasonal"
    assert data.topics[0].seasonal_challenges[0].completion_percentage == 1.0
    assert data.topics[0].seasonal_challenges[0].name == "Master of All"

    assert cache.seasonal_challenges_definition is not None


@pytest.mark.asyncio
async def test_triumphs(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/triumphs")
    assert r.status_code == 200
    data = DestinyTriumphScoreModel.parse_obj(r.json())
    assert data.active_score == 20097
    assert data.legacy_score == 117570
    assert data.lifetime_score == 137667


@pytest.mark.asyncio
async def test_artifact_level(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/artifact")
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 20


@pytest.mark.asyncio
async def test_season_pass_level(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/season_pass")
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 210


@pytest.mark.asyncio
async def test_get_consumable_amount(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(
        f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/consumable/{dummy_consumable_id}"
    )
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 17


@pytest.mark.asyncio
async def test_get_max_power(client: AsyncClient, mocker: MockerFixture):
    mocker.patch("Backend.networking.base.NetworkBase._request", mock_request)

    r = await client.get(f"/destiny/{dummy_discord_guild_id}/{dummy_discord_id}/account/max_power")
    assert r.status_code == 200
    data = ValueModel.parse_obj(r.json())
    assert data.value == 17
