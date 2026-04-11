from enum import StrEnum

from pydantic import BaseModel



class Child(BaseModel):
    """子模组"""
    publishedfileid: str
    sortorder: int
    file_type: int


class ModVersion(BaseModel):
    version: str
    loader_version: str


class Tag(BaseModel):
    """标签"""
    tag: str
    display_name: str


class KVTag(BaseModel):
    """键值标签"""
    key: str
    value: str


class VoteData(BaseModel):
    """投票数据"""
    score: float
    votes_up: int
    votes_down: int


class ModSide(StrEnum):
    Both = "Both"
    Server = "Server"
    NoSync = "NoSync"
    Client = "Client"
