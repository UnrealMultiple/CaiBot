from datetime import datetime
from typing import Optional, List

from packaging import version
from pydantic import BaseModel

from caibot.model.base import ModVersion, ModSide, Tag, KVTag, Child


class BaseMod(BaseModel):
    publishedfileid: str 
    children: List[Child] = []
    subscriptions: int
    favorited: int
    time_updated: int
    title: str
    short_description: str
    preview_url: str
    file_size: str
    creator: str


class Mod(BaseMod):
    synced: bool
    time_sync: int
    versions: List[ModVersion]
    name: str
    author: str
    modside: ModSide
    homepage: str
    tags: List[str]
    references: List[str]

    @property
    def sync_datetime(self) -> datetime:
        """获取创建时间的datetime对象"""
        return datetime.fromtimestamp(self.time_sync)

    @property
    def latest_loader_version(self) -> str:
        """获取最新的tModLoader版本"""
        print(self.versions)
        self.versions.sort(key=lambda x: version.parse(x.loader_version))
        return self.versions[-1].loader_version

    @property
    def latest_version(self) -> str:
        """获取最新的版本"""
        self.versions.sort(key=lambda x: version.parse(x.loader_version))
        return self.versions[-1].version

    @classmethod
    def from_base(cls, base_mod: BaseMod, tags: List[Tag], kvtags: List[KVTag]):
        kv_dict = {tag.key: tag.value for tag in kvtags}

        versions = [ModVersion(version=i.split(':')[1], loader_version=i.split(':')[0]) for i in
                    kv_dict["versionsummary"].split(";")]

        base_mod_dict = base_mod.model_dump()
        base_mod_dict.pop("tags", None)
        base_mod_dict.pop("kvtags", None)

        return cls(
            **base_mod_dict,
            synced=False,
            time_sync=0,
            versions=versions,
            name=kv_dict["name"],
            author=kv_dict["Author"],
            modside=ModSide(kv_dict["modside"]),
            homepage=kv_dict["homepage"],
            references=[i.publishedfileid for i in (base_mod.children or [])],
            tags=[tag.display_name for tag in tags]
        )
