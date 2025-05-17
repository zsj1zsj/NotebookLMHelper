from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List


@dataclass
class BilibiliHistoryItem:
    title: str
    redirect_link: str
    short_link: str
    bvid: str
    aid: int
    cid: int
    pubdate: int
    duration: int
    view_at: int
    owner_name: str
    view_count: int
    like_count: int
    favorite_count: int
    coin_count: int
    share_count: int

    @property
    def pubdate_str(self) -> str:
        return datetime.fromtimestamp(self.pubdate).strftime('%Y-%m-%d %H:%M:%S')

    @property
    def view_at_str(self) -> str:
        return datetime.fromtimestamp(self.view_at).strftime('%Y-%m-%d %H:%M:%S')

    def __str__(self):
        return (
            f"Title: {self.title}\n"
            f"Owner: {self.owner_name}\n"
            f"URL: {self.redirect_link}\n"
            f"Short URL: {self.short_link}\n"
            f"BVID: {self.bvid}, AID: {self.aid}, CID: {self.cid}\n"
            f"Published: {self.pubdate_str}\n"
            f"Viewed At: {self.view_at_str}\n"
            f"Duration: {self.duration}s\n"
            f"Views: {self.view_count}, Likes: {self.like_count}, "
            f"Favorites: {self.favorite_count}, Coins: {self.coin_count}, Shares: {self.share_count}\n"
        )

    @classmethod
    def from_json(cls, json_data: Dict) -> 'BilibiliHistoryItem':
        return cls(
            title=json_data.get('title', ''),
            redirect_link=json_data.get('redirect_link', ''),
            short_link=json_data.get('short_link_v2', ''),
            bvid=json_data.get('bvid', ''),
            aid=json_data.get('aid', 0),
            cid=json_data.get('cid', 0),
            pubdate=json_data.get('pubdate', 0),
            duration=json_data.get('duration', 0),
            view_at=json_data.get('view_at', 0),
            owner_name=json_data.get('owner', {}).get('name', ''),
            view_count=json_data.get('stat', {}).get('view', 0),
            like_count=json_data.get('stat', {}).get('like', 0),
            favorite_count=json_data.get('stat', {}).get('favorite', 0),
            coin_count=json_data.get('stat', {}).get('coin', 0),
            share_count=json_data.get('stat', {}).get('share', 0)
        )

    @classmethod
    def from_json_list(cls, json_response: Dict) -> List['BilibiliHistoryItem']:
        return [cls.from_json(item) for item in json_response.get("data", [])]
