import pandas as pd
import logging
from datetime import datetime

class DataTransformer:
    """Список постов -> DataFrame и csv"""

    def __init__(self):
        self.logger = logging.getLogger('DataTransformer')

    def to_dataframe(self, posts_data: list) -> pd.DataFrame:
        """Собирает DataFrame и упорядочивает колонки"""
        if not posts_data:
            self.logger.warning("Нет данных")
            return pd.DataFrame()

        df = pd.DataFrame(posts_data)

        base_columns = [
            'channel_username', 'channel_title', 'channel_subscribers', 'post_id',
            'post_date', 'post_time', 'post_datetime', 'scraped_at',
            'is_scheduled', 'has_poll', 'has_media',
            'text', 'text_length', 'media_type',
            'links_count_entities', 'has_links_entities', 'links_from_entities',
            'views', 'forwards', 'total_reactions',
        ]

        reaction_columns = sorted([col for col in df.columns if col.startswith('reaction_')])

        final_columns = base_columns + reaction_columns
        final_columns = [col for col in final_columns if col in df.columns]

        remaining_columns = [col for col in df.columns if col not in final_columns]
        final_columns.extend(remaining_columns)

        df = df[final_columns]

        datetime_columns = ['post_datetime', 'scraped_at']
        for col in datetime_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])

        return df

    def export_to_csv(self, posts_data: list, filename: str = None) -> str:
        """Сохраняет посты в csv, возвращает имя файла"""
        if not posts_data:
            self.logger.warning("Нет данных для экспорта")
            return None

        df = self.to_dataframe(posts_data)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"telegram_data_{timestamp}.csv"

        df.to_csv(filename, index=False, encoding='utf-8')
        return filename