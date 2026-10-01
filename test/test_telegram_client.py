import asyncio
import sys
import os

# Добавляем корень проекта в sys.path
project_root = os.path.dirname(os.path.abspath(__file__)) 
project_root = os.path.dirname(project_root)
sys.path.insert(0, project_root)

from config.settings import config, is_config_valid
from src.data_collection.telegram_client import TelegramClientManager
from src.data_collection.channel_collector import ChannelCollector
from src.data_processing.transformer import DataTransformer

async def main():
    """Тест коллектора с сохранением в test/data/"""
    
    if not is_config_valid:
        print("❌ Сначала настройте конфигурацию в .env")
        return
    
    # Создаем папку test/data если её нет
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    print(f"📁 Папка для сохранения: {data_dir}")
    
    async with TelegramClientManager(
        api_id=config.API_ID,
        api_hash=config.API_HASH, 
        session_name=config.SESSION_NAME
    ) as client:
        
        # Создаем коллектор и трансформер
        collector = ChannelCollector(client, config)
        transformer = DataTransformer()
        
        # Тестируем первый канал
        test_channel = config.TARGET_CHANNELS[0]
        
        print(f"🎯 Тестируем сбор из @{test_channel}")
        print("=" * 50)
        
        # Сначала получаем информацию о канале
        channel_info = await collector.get_channel_info(test_channel)
        if channel_info:
            print(f"📊 Информация о канале:")
            print(f"   Название: {channel_info.title}")
            print(f"   Подписчики: {channel_info.participants_count}")
            print(f"   Описание: {channel_info.description[:100]}...")
        
        # Сбор постов
        posts = await collector.collect_channel_posts(test_channel, limit=100)
        
        if posts:
            df = transformer.to_dataframe(posts)
            
            print(f"\n📊 РЕЗУЛЬТАТЫ СБОРА ПОСТОВ:")
            print(f"   Всего постов: {len(df)}")
            print(f"   Отложенных постов: {df['is_scheduled'].sum()}")
            print(f"   Постов с медиа: {df['has_media'].sum()}")
            print(f"   Постов со ссылками (entities): {df['has_links_entities'].sum()}")
            print(f"   Всего ссылок через entities: {df['links_count_entities'].sum()}")        
            
            # Экспорт в папку test/data/
            filename = os.path.join(data_dir, f"{test_channel}_test_data.csv")
            transformer.export_to_csv(posts, filename)
            print(f"\n💾 Данные сохранены в: {filename}")

if __name__ == "__main__":
    asyncio.run(main())