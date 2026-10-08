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
    """Сбор постов по каждому каналу в отдельный csv"""

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

        for i, channel in enumerate(config.TARGET_CHANNELS, 1):
            print(f"[{i}/{len(config.TARGET_CHANNELS)}] @{channel}")

            try:
                channel_info = await collector.get_channel_info(channel)
                channel_title = channel_info.title if channel_info else channel

                posts = await collector.collect_channel_posts(channel, limit=limit_per_channel)

                if not posts:
                    print("   Посты не собраны")
                    continue

                df = transformer.to_dataframe(posts)

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

                timestamp = datetime.now().strftime("%Y%m%d")
                filename = f"{output_dir}/{channel}_{timestamp}_{limit_per_channel}posts.csv"

                transformer.export_to_csv(posts, filename)
                # повторно сохраняем через pandas, чтобы попали все столбцы
                df.to_csv(filename, index=False, encoding='utf-8')

                print(f"   Постов: {len(df)}, период: {df['post_datetime'].min().date()} - {df['post_datetime'].max().date()}")
                print(f"   Файл: {filename}")

                # карта реакций нужна только для справки
                try:
                    reactions_map = await collector.get_available_reactions(channel, sample_size=20)
                    if reactions_map:
                        custom_reactions = [k for k, v in reactions_map.items() if v['type'] == 'custom']
                        print(f"   Кастомных реакций: {len(custom_reactions)}")
                except Exception:
                    print("   Карту реакций собрать не удалось")

            except Exception as e:
                print(f"   Ошибка: {e}")
                continue


async def main():
    LIMIT_PER_CHANNEL = 5000

    print(f"Лимит постов на канал: {LIMIT_PER_CHANNEL}, каналов: {len(config.TARGET_CHANNELS)}")
    confirm = input("Начать сбор? (y/n): ").strip().lower()

    if confirm == 'y':
        await collect_all_channels_separate(limit_per_channel=LIMIT_PER_CHANNEL)
    else:
        print("Сбор отменен")

if __name__ == "__main__":
    asyncio.run(main())
