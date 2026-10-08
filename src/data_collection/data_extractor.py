import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

from src.models.schemas import PollData, LinksData

class DataExtractor:
    """Класс для извлечения и обработки данных из постов"""

    def __init__(self, config=None):
        self.config = config
        self.logger = logging.getLogger('DataExtractor')

    def extract_post_data(self, message, channel_username: str, channel_info: Dict) -> Dict[str, Any]:
        """Собирает словарь с данными одного поста"""
        post_date = message.date
        date_str = post_date.strftime('%Y-%m-%d') if post_date else ''
        time_str = post_date.strftime('%H:%M:%S') if post_date else ''

        text_content = self._clean_text_for_csv(message.text) if message.text else ''
        poll_data = self._extract_poll_data(message)
        full_text = self._combine_text_and_poll(text_content, poll_data)

        post_data = {
            'channel_username': channel_username,
            'channel_title': channel_info.get('title', 'N/A'),
            'channel_subscribers': channel_info.get('participants_count', 0),
            'post_id': message.id,

            'post_date': date_str,
            'post_time': time_str,
            'post_datetime': message.date,
            'scraped_at': datetime.now(),

            'is_scheduled': self._detect_scheduled_post(message),
            'has_poll': poll_data.has_poll,
            'has_media': bool(message.media),

            'text': full_text,
            'text_length': len(full_text),
            'media_type': self._get_media_type(message.media),

            'links_count_entities': 0,
            'has_links_entities': False,
            'links_from_entities': [],

            'views': message.views or 0,
            'forwards': message.forwards or 0,
            'total_reactions': 0,
        }

        links_data = self._extract_links_from_entities(message)
        post_data.update(links_data)

        if message.reactions:
            reactions_data = self._extract_reactions_with_mapping(message.reactions, channel_username)
            post_data.update(reactions_data)
            post_data['total_reactions'] = sum(
                v for k, v in reactions_data.items()
                if k.startswith('reaction_')
            )

        return post_data

    def _clean_text_for_csv(self, text: str) -> str:
        """Очистка текста для CSV"""
        if not text:
            return ""

        cleaned = re.sub(r'\s+', ' ', text.replace('\n', ' ').replace('\r', ' ')).strip()

        if '"' in cleaned:
            cleaned = cleaned.replace('"', '""')

        return cleaned

    def _combine_text_and_poll(self, text: str, poll_data: PollData) -> str:
        """Объединяет текст поста и вопрос опроса"""
        parts = []

        if text:
            parts.append(text)

        if poll_data.has_poll and poll_data.poll_question:
            parts.append(f"[ОПРОС] {poll_data.poll_question}")

        return " | ".join(parts) if parts else ""

    def _extract_poll_data(self, message) -> PollData:
        """Извлечение данных опроса"""
        try:
            poll = None
            question = ""

            if hasattr(message, 'media') and message.media:
                if hasattr(message.media, 'question'):
                    poll = message.media
                    question = poll.question
                elif hasattr(message.media, 'poll') and hasattr(message.media.poll, 'question'):
                    poll = message.media.poll
                    question = message.media.poll.question

            elif hasattr(message, 'poll') and hasattr(message.poll, 'question'):
                poll = message.poll
                question = message.poll.question

            if poll and question:
                question_text = ""
                if hasattr(question, 'text'):
                    question_text = question.text
                elif isinstance(question, str):
                    question_text = question

                cleaned_question = self._clean_text_for_csv(question_text)
                if cleaned_question:
                    self.logger.info(f"Опрос {message.id}: '{cleaned_question}'")
                    return PollData(
                        has_poll=True,
                        poll_question=cleaned_question
                    )

        except Exception as e:
            self.logger.warning(f"Ошибка извлечения опроса {message.id}: {e}")

        return PollData(has_poll=False, poll_question='')

    def _detect_scheduled_post(self, message) -> bool:
        """Определение отложенных постов"""
        if not hasattr(message, 'date'):
            return False

        post_time = message.date
        minute = post_time.minute
        second = post_time.second

        return (minute % 10 == 0 or minute % 10 == 5) and second == 0

    def _extract_reactions_with_mapping(self, reactions, channel_username: str) -> Dict[str, int]:
        """Извлечение реакций с маппингом"""
        reactions_data = {}

        for reaction in reactions.results:
            try:
                reaction_emoji = None

                if hasattr(reaction.reaction, 'emoticon'):
                    reaction_emoji = reaction.reaction.emoticon

                elif hasattr(reaction.reaction, 'document_id'):
                    doc_id = str(reaction.reaction.document_id)

                    if self.config and channel_username in self.config.CUSTOM_REACTIONS_MAP.get('by_channel', {}):
                        channel_map = self.config.CUSTOM_REACTIONS_MAP['by_channel'][channel_username]
                        reaction_emoji = channel_map.get(doc_id, f"custom_{doc_id}")
                    else:
                        reaction_emoji = f"custom_{doc_id}"

                if reaction_emoji:
                    reaction_key = f"reaction_{reaction_emoji}"
                    reactions_data[reaction_key] = reactions_data.get(reaction_key, 0) + reaction.count

            except Exception as e:
                self.logger.warning(f"Ошибка обработки реакции: {e}")
                continue

        return reactions_data

    def _extract_links_from_entities(self, message) -> Dict[str, Any]:
        """Извлечение ссылок через entities"""
        links_data = {
            'links_from_entities': [],
            'links_count_entities': 0,
            'has_links_entities': False
        }

        if not hasattr(message, 'entities') or not message.entities:
            return links_data

        try:
            extracted_links = []

            for entity in message.entities:
                if hasattr(entity, 'url') and entity.url:
                    extracted_links.append(entity.url)

            unique_links = list(set(extracted_links))
            links_data['links_from_entities'] = unique_links
            links_data['links_count_entities'] = len(unique_links)
            links_data['has_links_entities'] = len(unique_links) > 0

        except Exception as e:
            self.logger.warning(f"Ошибка извлечения ссылок: {e}")

        return links_data

    def _get_media_type(self, media) -> Optional[str]:
        """Определение типа медиа"""
        if not media:
            return None

        if isinstance(media, MessageMediaPhoto):
            return 'photo'
        elif isinstance(media, MessageMediaDocument):
            return 'document'
        else:
            return 'other'

    def should_skip_message(self, message) -> bool:
        """Определяем нужно ли пропускать сообщение"""
        if (message.grouped_id and
            not message.text and
            not self._has_poll(message)):
            return True

        if not message.text and not message.media and not self._has_poll(message):
            return True

        return False

    def _has_poll(self, message) -> bool:
        """Проверяем есть ли опрос в сообщении"""
        return (hasattr(message, 'media') and message.media and
                (hasattr(message.media, 'poll') or hasattr(message.media, 'question')))