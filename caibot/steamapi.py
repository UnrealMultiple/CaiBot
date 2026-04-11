from enum import IntEnum

import httpx

from caibot import config
from caibot.model.workshop import QueryResponse, SteamWorkshopResponse


class QueryType(IntEnum):
    """Steam UGC（用户生成内容）发布文件查询类型枚举"""
    RankedByPublicationDate = 1
    """按发布日期排序（从新到旧）"""

    RankedByTrend = 3
    """按趋势排序（综合考虑近期流行度）"""

    RankedByTotalUniqueSubscriptions = 9
    """按总独立订阅数排序"""

    RankedByLastUpdatedDate = 21
    """按最后更新日期排序"""


class SteamAPI:
    BASEURL: str = "https://api.steampowered.com/"
    KEY: str = config.steam_api_key

    @classmethod
    async def query_mods(cls, search_text: str, cursor: str = "*", *,
                         query_type: QueryType = QueryType.RankedByTotalUniqueSubscriptions) -> QueryResponse:
        params = {"key": cls.KEY,
                  "format": "json",
                  "query_type": query_type,
                  "cursor": cursor,
                  "appid": 1281930,
                  "creator_appid": 1281930,
                  "search_text": search_text,
                  "match_all_tags": False,
                  "language": 6,
                  "numperpage": 30,
                  "return_vote_data": True,
                  "return_tags": True,
                  "return_kv_tags": True,
                  "return_children": True,
                  "return_short_description": True
                  }

        async with httpx.AsyncClient() as client:
            client.base_url = cls.BASEURL
            response = await client.get("/IPublishedFileService/QueryFiles/v1/", params=params,
                                        timeout=30.0)
            response.raise_for_status()
            print(response.text)
            workshop_response = SteamWorkshopResponse.model_validate_json(response.text)
            return workshop_response.response

    @classmethod
    async def query_resource(cls, search_text: str, cursor: str = "*", *,
                         query_type: QueryType = QueryType.RankedByTotalUniqueSubscriptions) -> QueryResponse:
        params = {"key": cls.KEY,
                  "format": "json",
                  "query_type": query_type,
                  "cursor": cursor,
                  "appid": 105600,
                  "creator_appid": 105600,
                  "search_text": search_text,
                  "match_all_tags": False,
                  "language": 6,
                  "numperpage": 30,
                  "return_vote_data": True,
                  "return_tags": True,
                  "return_kv_tags": True,
                  "return_children": True,
                  "return_short_description": True
                  }

        async with httpx.AsyncClient() as client:
            client.base_url = cls.BASEURL
            response = await client.get("/IPublishedFileService/QueryFiles/v1/", params=params,
                                        timeout=30.0)
            response.raise_for_status()
            print(response.text)
            workshop_response = SteamWorkshopResponse.model_validate_json(response.text)
            return workshop_response.response
