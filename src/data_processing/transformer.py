import pandas as pd
import logging
from datetime import datetime

class DataTransformer:
    """Трансформация данных в DataFrame"""
    
    def __init__(self):
        self.logger = logging.getLogger('DataTransformer')

    def to_dataframe(self, posts_data: list) -> pd.DataFrame:
        """Сохранение данных в DataFrame"""
        if not posts_data:
            self.logger.warning("Нет данных для сохранения")
            return pd.DataFrame()
            
        df = pd.DataFrame(posts_data)
        
        # Определяем порядок колонок
        base_columns = [
            'channel_username', 'channel_title', 'channel_subscribers', 'post_id',
            'post_date', 'post_time', 'post_datetime', 'scraped_at',
            'is_scheduled', 'has_poll', 'has_media',
            'text', 'text_length', 'media_type',
            'links_count_entities', 'has_links_entities', 'links_from_entities',
            'views', 'forwards', 'total_reactions',
        ]
        
        # Реакции
        reaction_columns = sorted([col for col in df.columns if col.startswith('reaction_')])
        
        final_columns = base_columns + reaction_columns
        final_columns = [col for col in final_columns if col in df.columns]
        
        # Добавляем оставшиеся колонки
        remaining_columns = [col for col in df.columns if col not in final_columns]
        final_columns.extend(remaining_columns)
        
        df = df[final_columns]
        
        # Конвертируем даты
        datetime_columns = ['post_datetime', 'scraped_at']
        for col in datetime_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
        self.logger.info(f"💾 Данные сохранены в DataFrame: {len(df)} строк, {len(df.columns)} колонок")
        return df

    def export_to_csv(self, posts_data: list, filename: str = None) -> str:
        """Экспорт данных в CSV"""
        if not posts_data:
            self.logger.warning("⚠️ Нет данных для экспорта")
            return None
            
        df = self.to_dataframe(posts_data)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"telegram_data_{timestamp}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8')
        self.logger.info(f"💾 Данные экспортированы в: {filename}")
        return filename