from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class ChannelInfo:
    username: str
    title: str
    participants_count: int
    description: str
    is_verified: bool

@dataclass
class PollData:
    has_poll: bool
    poll_question: str

@dataclass
class LinksData:
    links_from_entities: List[str]
    links_count_entities: int
    has_links_entities: bool

@dataclass
class PostData:
    # Идентификация и метаданные
    channel_username: str
    channel_title: str
    channel_subscribers: int
    post_id: int
    
    # Дата и время
    post_date: str
    post_time: str
    post_datetime: datetime
    scraped_at: datetime
    
    # Тип и статус поста
    is_scheduled: bool
    has_poll: bool
    has_media: bool
    
    # Контент
    text: str
    text_length: int
    media_type: Optional[str]
    
    # Ссылки
    links_count_entities: int
    has_links_entities: bool
    links_from_entities: List[str]
    
    # Вовлеченность
    views: int
    forwards: int
    total_reactions: int
    
    # Реакции (динамические поля)
    reactions: Dict[str, int]