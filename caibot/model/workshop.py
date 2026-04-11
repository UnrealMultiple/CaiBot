from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .base import Tag, KVTag, VoteData
from .mod import BaseMod


class PublishedFileDetails(BaseMod):
    """发布的模组详情"""
    result: int
    creator_appid: int
    consumer_appid: int
    consumer_shortcutid: int
    preview_file_size: str
    hcontent_file: str
    hcontent_preview: str
    time_created: int
    visibility: int
    flags: int
    workshop_file: bool
    workshop_accepted: bool
    show_subscribe_all: bool
    num_comments_public: int
    banned: bool
    url: str
    filename: str
    ban_reason: str
    banner: str
    can_be_deleted: bool
    app_name: str
    file_type: int
    can_subscribe: bool
    followers: int
    lifetime_subscriptions: int
    lifetime_favorited: int
    lifetime_followers: int
    lifetime_playtime: str
    lifetime_playtime_sessions: str
    views: int
    num_children: int
    num_reports: int
    tags: List[Tag] = []
    kvtags: List[KVTag] = []
    vote_data: Optional[VoteData] = None
    language: int
    maybe_inappropriate_sex: bool
    maybe_inappropriate_violence: bool
    revision_change_number: str
    revision: int
    ban_text_check_result: int

    @property
    def created_datetime(self) -> datetime:
        """获取创建时间的datetime对象"""
        return datetime.fromtimestamp(self.time_created)

    @property
    def updated_datetime(self) -> datetime:
        """获取更新时间的datetime对象"""
        return datetime.fromtimestamp(self.time_updated)

    @property
    def file_size_mb(self) -> float:
        """获取文件大小（MB）"""
        try:
            return int(self.file_size) / (1024 * 1024)
        except (ValueError, TypeError):
            return 0.0

    @property
    def preview_size_kb(self) -> float:
        """获取预览图大小（KB）"""
        try:
            return int(self.preview_file_size) / 1024
        except (ValueError, TypeError):
            return 0.0

    @property
    def upvote_ratio(self) -> float:
        """获取好评率"""
        total = self.vote_data.votes_up + self.vote_data.votes_down
        if total == 0:
            return 0.0
        return self.vote_data.votes_up / total

    @property
    def kvtags_dict(self) -> dict[str, str]:
        """将 kvtags 列表转为普通字典 {key: value}"""
        return {kv.key: kv.value for kv in self.kvtags}

    @property
    def popularity_score(self) -> float:
        """计算综合人气分数（0-1）"""
        # 基于订阅数、评分和浏览量计算
        sub_score = min(self.subscriptions / 1000000, 1.0)  # 100万订阅为满分
        vote_score = self.vote_data.score
        view_score = min(self.views / 1000000, 1.0)  # 100万浏览为满分

        # 加权计算（可以根据需求调整权重）
        return sub_score * 0.4 + vote_score * 0.4 + view_score * 0.2


class QueryResponse(BaseModel):
    """查询响应"""
    total: int
    publishedfiledetails: List[PublishedFileDetails] = []
    next_cursor: Optional[str] = None


class SteamWorkshopResponse(BaseModel):
    """Steam工作坊完整响应"""
    response: QueryResponse

    @property
    def has_more_results(self) -> bool:
        """是否有更多结果"""
        return bool(self.response.next_cursor) and len(self.response.publishedfiledetails) < self.response.total
