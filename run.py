import asyncio
import sys
import os
import pandas as pd
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import config, is_config_valid
from src.data_collection.telegram_client import TelegramClientManager
from src.data_collection.channel_collector import ChannelCollector
from src.data_processing.transformer import DataTransformer

output_dir = "data/channels_data/raw"
os.makedirs(output_dir, exist_ok=True)

async def collect_all_channels_separate(limit_per_channel=500):
    """Сбор данных из всех каналов с сохранением в отдельные файлы"""
    
    if not is_config_valid:
        print("Сначала настройте конфигурацию в .env")
        return
    
    all_stats = []
    
    async with TelegramClientManager(
        api_id=config.API_ID,
        api_hash=config.API_HASH, 
        session_name=config.SESSION_NAME
    ) as client:
        
        collector = ChannelCollector(client, config)
        transformer = DataTransformer()
        
        print("СБОР ДАННЫХ ИЗ ВСЕХ КАНАЛОВ")
        print("=" * 60)
        print(f"Лимит постов на канал: {limit_per_channel}")
        print(f"Всего каналов: {len(config.TARGET_CHANNELS)}")
        print(f"Папка для сохранения: {output_dir}/")
        print("=" * 60)
        
        # Обрабатываем каждый канал
        for i, channel in enumerate(config.TARGET_CHANNELS, 1):
            print(f"\n[{i}/{len(config.TARGET_CHANNELS)}] 📡 Канал: @{channel}")
            print("-" * 50)
            
            try:
                # Получаем информацию о канале
                channel_info = await collector.get_channel_info(channel)
                channel_title = channel_info.title if channel_info else channel
                
                print(f"   Название: {channel_title}")
                if channel_info:
                    print(f"   Подписчики: {channel_info.participants_count:,}")
                
                # Сбор постов
                print(f"   Сбор постов...")
                posts = await collector.collect_channel_posts(channel, limit=limit_per_channel)
                
                if not posts:
                    print(f"   Не удалось собрать посты")
                    continue
                
                # Преобразуем в DataFrame
                df = transformer.to_dataframe(posts)
                
                # Добавляем информацию о канале
                df['channel_username'] = channel
                df['channel_title'] = channel_title
                if channel_info:
                    df['channel_subscribers'] = channel_info.participants_count
                
                # Собираем статистику
                stats = {
                    'channel_username': channel,
                    'channel_title': channel_title,
                    'posts_collected': len(df),
                    'posts_period_start': df['post_datetime'].min(),
                    'posts_period_end': df['post_datetime'].max(),
                    'total_views': int(df['views'].sum()),
                    'avg_views': float(df['views'].mean()),
                    'total_reactions': int(df['total_reactions'].sum()),
                    'scheduled_posts': int(df['is_scheduled'].sum()),
                    'posts_with_media': int(df['has_media'].sum()),
                    'posts_with_polls': int(df['has_poll'].sum()),
                    'reaction_types': len([c for c in df.columns if c.startswith('reaction_')])
                }
                
                all_stats.append(stats)
                
                # Сохраняем в отдельный CSV файл
                timestamp = datetime.now().strftime("%Y%m%d")
                filename = f"{output_dir}/{channel}_{timestamp}_{limit_per_channel}posts.csv"
                
                # Экспорт
                transformer.export_to_csv(posts, filename)
                
                # Дополнительно сохраняем как CSV через pandas (чтобы были все столбцы)
                df.to_csv(filename, index=False, encoding='utf-8')
                
                print(f"   Собрано постов: {len(df)}")
                print(f"   Период: {df['post_datetime'].min().date()} - {df['post_datetime'].max().date()}")
                print(f"   Просмотры: {df['views'].sum():,} (среднее: {df['views'].mean():.0f})")
                print(f"   Реакций всего: {df['total_reactions'].sum():,}")
                print(f"   Файл: {filename}")
                
                # Собираем карту реакций (опционально)
                print(f"   Собираю карту реакций...")
                try:
                    reactions_map = await collector.get_available_reactions(channel, sample_size=20)
                    if reactions_map:
                        custom_reactions = [k for k, v in reactions_map.items() if v['type'] == 'custom']
                        print(f"   Кастомных реакций: {len(custom_reactions)}")
                except:
                    print(f"   Не удалось собрать карту реакций")
                
            except Exception as e:
                print(f"   Ошибка: {str(e)}")
                continue


async def main():
    """Главная функция"""
    
    print("СБОР ДАННЫХ ИЗ ТЕЛЕГРАМ КАНАЛОВ")
    print("=" * 50)
    print("Каждый канал будет сохранен в отдельный файл")
    print("=" * 50)
    
    # Можно изменить лимит здесь
    LIMIT_PER_CHANNEL = 5000  # Укажите нужный лимит
    
    print(f"\nНастройки:")
    print(f"   • Лимит постов на канал: {LIMIT_PER_CHANNEL}")
    print(f"   • Каналов для сбора: {len(config.TARGET_CHANNELS)}")
    
    confirm = input("\nНачать сбор? (y/n): ").strip().lower()
    
    if confirm == 'y':
        await collect_all_channels_separate(limit_per_channel=LIMIT_PER_CHANNEL)
    else:
        print(" Сбор отменен")

if __name__ == "__main__":
    asyncio.run(main())