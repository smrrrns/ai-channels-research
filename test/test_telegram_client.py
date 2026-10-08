import asyncio
import sys
import os

# корень проекта в sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(project_root)
sys.path.insert(0, project_root)

from config.settings import config, is_config_valid
from src.data_collection.telegram_client import TelegramClientManager
from src.data_collection.channel_collector import ChannelCollector
from src.data_processing.transformer import DataTransformer

async def main():
    """Пробный сбор 100 постов с первого канала"""

    if not is_config_valid:
        print("Сначала настройте конфигурацию в .env")
        return

    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)

    async with TelegramClientManager(
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_name=config.SESSION_NAME
    ) as client:

        collector = ChannelCollector(client, config)
        transformer = DataTransformer()

        test_channel = config.TARGET_CHANNELS[0]

        print(f"Тест на @{test_channel}")

        channel_info = await collector.get_channel_info(test_channel)
        if channel_info:
            print(f"{channel_info.title}, подписчиков: {channel_info.participants_count}")

        posts = await collector.collect_channel_posts(test_channel, limit=100)

        if posts:
            df = transformer.to_dataframe(posts)

            print(f"Постов: {len(df)}, отложенных: {df['is_scheduled'].sum()}, с медиа: {df['has_media'].sum()}")

            filename = os.path.join(data_dir, f"{test_channel}_test_data.csv")
            transformer.export_to_csv(posts, filename)
            print(f"Сохранено: {filename}")

if __name__ == "__main__":
    asyncio.run(main())