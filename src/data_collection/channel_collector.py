import asyncio
import logging
import pandas as pd
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.errors import FloodWaitError

from src.models.schemas import ChannelInfo
from src.data_collection.data_extractor import DataExtractor

class ChannelCollector:
    """Сборщик данных из Telegram-каналов"""

    def __init__(self, telegram_client: TelegramClient, config=None):
        self.client = telegram_client
        self.config = config
        self.data_extractor = DataExtractor(config)
        self.logger = self._setup_logging()

    def _setup_logging(self):
        logger = logging.getLogger('ChannelCollector')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    async def get_channel_info(self, channel_username: str) -> ChannelInfo:
        try:
            channel = await self.client.get_entity(channel_username)
            full_channel = await self.client(GetFullChannelRequest(channel))

            info = ChannelInfo(
                username=channel_username,
                title=getattr(channel, 'title', 'N/A'),
                participants_count=full_channel.full_chat.participants_count,
                description=getattr(channel, 'about', ''),
                is_verified=getattr(channel, 'verified', False),
            )
            self.logger.info(f"@{channel_username}: {info.participants_count} участников")
            return info

        except Exception as e:
            self.logger.error(f"Не удалось получить информацию о @{channel_username}: {e}")
            return None

    async def collect_channel_posts(self, channel_username: str, limit: int = 100, offset_date=None):
        posts_data = []
        try:
            channel = await self.client.get_entity(channel_username)
            channel_info = await self.get_channel_info(channel_username)

            # extractor ожидает словарь
            channel_info_dict = {
                'title': channel_info.title,
                'participants_count': channel_info.participants_count,
                'description': channel_info.description,
                'is_verified': channel_info.is_verified
            } if channel_info else {}

            collected_count = 0
            async for message in self.client.iter_messages(channel, limit=limit, offset_date=offset_date):
                try:
                    if self.data_extractor.should_skip_message(message):
                        continue

                    post_data = self.data_extractor.extract_post_data(message, channel_username, channel_info_dict)
                    if post_data:
                        posts_data.append(post_data)
                        collected_count += 1

                        if collected_count % 100 == 0:
                            self.logger.info(f"@{channel_username}: {collected_count}/{limit}")

                except Exception as e:
                    self.logger.warning(f"Пост {message.id} пропущен: {e}")
                    continue

            self.logger.info(f"@{channel_username}: собрано {collected_count} постов")
            return posts_data
        except Exception as e:
            self.logger.error(f"Ошибка сбора из @{channel_username}: {e}")
            return []

    async def get_available_reactions(self, channel_username: str, sample_size: int = 50):
        """Реакции, встретившиеся в последних sample_size постах"""
        try:
            channel = await self.client.get_entity(channel_username)
            reactions_map = {}

            async for message in self.client.iter_messages(channel, limit=sample_size):
                if message.reactions:
                    for reaction in message.reactions.results:
                        if hasattr(reaction.reaction, 'emoticon'):
                            emoticon = reaction.reaction.emoticon
                            if emoticon not in reactions_map:
                                reactions_map[emoticon] = {
                                    'type': 'emoji',
                                    'sample_count': reaction.count,
                                    'sample_post': message.id
                                }
                        elif hasattr(reaction.reaction, 'document_id'):
                            doc_id = str(reaction.reaction.document_id)
                            if doc_id not in reactions_map:
                                reactions_map[doc_id] = {
                                    'type': 'custom',
                                    'sample_count': reaction.count,
                                    'sample_post': message.id
                                }

            return reactions_map

        except Exception as e:
            self.logger.error(f"Ошибка сбора реакций: {e}")
            return {}

    async def collect_multiple_channels(self, channels: list, posts_per_channel: int = 100):
        all_posts = []

        for channel in channels:
            posts = await self.collect_channel_posts(channel, limit=posts_per_channel)
            all_posts.extend(posts)

        self.logger.info(f"Всего {len(all_posts)} постов из {len(channels)} каналов")
        return all_posts
